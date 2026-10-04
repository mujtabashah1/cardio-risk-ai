import json,logging,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.config import Settings
from api.main import create_app
from src.inference.constants import ROOT,FEATURES,PROFILE_NAMES
from src.inference.model_loader import ModelInitializationError,clear_cache
from src.inference.service import InferenceError

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.golden=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text());cls.profile=cls.golden[0]['input']
        cls.app=create_app(Settings());cls.client=TestClient(cls.app);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def invalid(self,payload,status=422,path='/predict'):
        response=self.client.post(path,json=payload);self.assertEqual(response.status_code,status,response.text)
        self.assertIn('error',response.json());self.assertNotIn('Traceback',response.text)
        return response
    def test_health(self):self.assertEqual(self.client.get('/health').json(),{'status':'ok'})
    def test_ready(self):self.assertEqual(self.client.get('/ready').json(),{'status':'ready','model_version':'1.0.0'})
    def test_model_info_safe(self):
        r=self.client.get('/model-info');self.assertEqual(r.status_code,200)
        data=r.json();self.assertEqual(data['feature_count'],14);self.assertEqual(data['feature_names'],list(FEATURES))
        self.assertEqual(data['model_family'],'catboost')
        for token in ['joblib','C:\\','/app/','hyperparameters','disease_probability']:self.assertNotIn(token,r.text)
    def test_valid_single_golden(self):
        for fixture in self.golden:
            r=self.client.post('/predict',json={'profile':fixture['input']});self.assertEqual(r.status_code,200,r.text)
            self.assertAlmostEqual(r.json()['profile_score'],fixture['expected_profile_score'],places=6)
            self.assertEqual(r.json()['classification'],fixture['expected_classification']);self.assertIn('x-request-id',r.headers)
    def test_batch_matches_independent_rows(self):
        r=self.client.post('/predict/batch',json={'profiles':[f['input'] for f in self.golden]});self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['count'],len(self.golden))
        for row,fixture in zip(r.json()['predictions'],self.golden):self.assertAlmostEqual(row['profile_score'],fixture['expected_profile_score'],places=6)
    def test_optional_missing(self):
        for p in [{'sex':1},dict.fromkeys(FEATURES),{**self.profile,'bmi':None,'high_cholesterol':None}]:self.assertEqual(self.client.post('/predict',json={'profile':p}).status_code,200)
    def test_required_structural_fields(self):
        for p in [{},{'profile':{}},{'profile':None},{'threshold_profile':'research_balanced'}]:self.invalid(p)
        for p in [{},{'profiles':[]}]:self.invalid(p,path='/predict/batch')
    def test_invalid_bmi_types_and_range(self):
        for value in ['28.5',{},[],True,-1,2500]:self.invalid({'profile':{**self.profile,'bmi':value}})
    def test_unknown_categories_strict_types(self):
        for feature in FEATURES:
            if feature!='bmi':self.invalid({'profile':{**self.profile,feature:999}})
        for value in ['1',True,1.0]:self.invalid({'profile':{**self.profile,'sex':value}})
    def test_extra_socioeconomic_and_each_leakage_field(self):
        for field in ['extra','education','income_group','heart_disease','_MICHD','CVDINFR4','CVDCRHD4']:
            with self.subTest(field=field):self.invalid({'profile':{**self.profile,field:1}})
        self.invalid({'profile':self.profile,'threshold':0.5})
    def test_invalid_threshold_profile(self):
        for name in ['unknown',0.2,None]:self.invalid({'profile':self.profile,'threshold_profile':name})
    def test_all_profiles_same_score(self):
        results=[self.client.post('/predict',json={'profile':self.profile,'threshold_profile':name}).json() for name in PROFILE_NAMES]
        self.assertEqual(len({r['profile_score'] for r in results}),1);self.assertEqual(len({r['threshold'] for r in results}),5)
    def test_malformed_duplicate_and_nonfinite_json(self):
        for value in ['{','{"profile":{"sex":1,"sex":2}}','{"profile":{"bmi":NaN}}','{"profile":{"bmi":Infinity}}','{"profile":{"sex":1},"threshold_profile":"youden","threshold_profile":"research_balanced"}']:
            r=self.client.post('/predict',content=value,headers={'content-type':'application/json'});self.assertEqual(r.status_code,400,r.text)
    def test_oversized_batch(self):self.invalid({'profiles':[{'sex':1}]*1001},path='/predict/batch')
    def test_transactional_indexed_batch_error(self):
        r=self.invalid({'profiles':[self.profile,{'sex':999},self.profile]},path='/predict/batch')
        self.assertIn(1,r.json()['error']['details'][0]['location'])
    def test_body_and_configured_batch_limits(self):
        app=create_app(replace(Settings(),max_body_bytes=1024,max_batch_size=2))
        with TestClient(app) as client:
            self.assertEqual(client.post('/predict',content=b'x'*1025,headers={'content-type':'application/json'}).status_code,413)
            self.assertEqual(client.post('/predict/batch',json={'profiles':[{'sex':1}]*3}).status_code,422)
            # Chunked streaming body with no content-length is bounded too.
            self.assertEqual(client.post('/predict',content=iter([b'x'*700,b'x'*700]),headers={'content-type':'application/json'}).status_code,413)
    def test_unsupported_media(self):self.assertEqual(self.client.post('/predict',content='text').status_code,415)
    def test_model_unavailable_without_startup(self):
        with TestClient(create_app()) as client:
            client.app.state.service=None
            self.assertEqual(client.get('/health').status_code,200);self.assertEqual(client.get('/ready').status_code,503)
            self.assertEqual(client.post('/predict',json={'profile':self.profile}).status_code,503)
    def test_model_missing_and_integrity_failure_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.joblib'
            for present in [False,True]:
                if present:path.write_bytes(b'invalid artifact')
                app=create_app(replace(Settings(),model_path=path))
                with self.assertRaises(ModelInitializationError):
                    with TestClient(app):pass
    def test_safe_inference_and_unexpected_errors(self):
        for error in [InferenceError('secret /path'),RuntimeError('secret /path')]:
            with patch.object(self.app.state.service,'predict',side_effect=error):
                r=self.client.post('/predict',json={'profile':self.profile});self.assertEqual(r.status_code,500);self.assertNotIn('secret',r.text);self.assertNotIn('/path',r.text)
    def test_privacy_conscious_logs_and_errors(self):
        with self.assertLogs('cardiorisk.requests',level='INFO') as capture:self.client.post('/predict',json={'profile':self.profile})
        message=json.loads(capture.records[-1].message)
        self.assertEqual(set(message),{'request_id','endpoint','status','latency_ms','model_version','threshold_profile','batch_size'})
        self.assertNotIn('bmi',capture.output[0]);self.assertNotIn('profile_score',capture.output[0])
        r=self.invalid({'profile':{'bmi':'sensitive-user-value'}});self.assertNotIn('sensitive-user-value',r.text)
    def test_cors_configuration(self):
        r=self.client.get('/health',headers={'origin':'https://example.com'});self.assertNotIn('access-control-allow-origin',r.headers)
        with TestClient(create_app(replace(Settings(),cors_origins=('https://example.com',)))) as client:
            self.assertEqual(client.get('/health',headers={'origin':'https://example.com'}).headers['access-control-allow-origin'],'https://example.com')
            self.assertNotIn('access-control-allow-origin',client.get('/health',headers={'origin':'https://evil.example'}).headers)
    def test_openapi_exact_schema(self):
        schema=self.client.get('/openapi.json').json()['components']['schemas']['HealthProfile']
        self.assertEqual(set(schema['properties']),set(FEATURES));self.assertFalse(schema['additionalProperties'])
    def test_concurrent_api_requests(self):
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:self.client.post('/predict',json={'profile':self.profile}).json(),range(12)))
        self.assertTrue(all(r==results[0] for r in results))
    def test_release_security_edge_cases(self):
        for payload in [{'profile':{'bmi':'NaN'}},{'profile':{'bmi':'x'*100000}},{'profile':{'未知字段':1}},{'profile':{'sex':{'nested':1}}},{'profiles':{'sex':1}}]:
            path='/predict/batch' if 'profiles' in payload else '/predict'
            r=self.invalid(payload,path=path);self.assertNotIn('未知字段',r.text)
        nested='{"profile":{"sex":'+'['*1500+'1'+']'*1500+'}}'
        for content,allowed_statuses in [(nested.encode(),(400,422)),(b'\xff',(400,))]:
            r=self.client.post('/predict',content=content,headers={'content-type':'application/json'})
            self.assertIn(r.status_code,allowed_statuses);self.assertIn('error',r.json());self.assertNotIn('Traceback',r.text)

if __name__=='__main__':unittest.main()
