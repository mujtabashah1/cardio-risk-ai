"""Local HTTP integration and backend regression evidence. No training/data writes."""
import hashlib,io,json,logging,sys,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.run_model_qa import LOW,HIGH
EXPECTED='4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1'
def main():
    suite=unittest.TestSuite()
    for directory in ['api','inference','models','artifacts','frontend']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'/directory)))
    suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_pipeline.py'))
    stream=io.StringIO()
    # Suppress operational request noise; preserve unittest evidence in local log.
    original=logging.basicConfig
    logging.basicConfig=lambda **kwargs:None
    logging.getLogger().setLevel(logging.CRITICAL)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    logging.basicConfig=original
    (ROOT/'reports/model_qa/react_backend_tests.log').write_text(stream.getvalue(),encoding='utf-8')
    backend={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped)}
    assert result.wasSuccessful(),backend
    rows=[]
    with httpx.Client(base_url='http://127.0.0.1:5173/api',timeout=20) as client:
        for endpoint in ['/health','/ready','/model-info']:
            r=client.get(endpoint);assert r.status_code==200
            rows.append({'test':endpoint,'status':'PASS','response':r.json()})
        for name,p in [('low',LOW),('high',HIGH),('all_unknown',dict.fromkeys(LOW))]:
            r=client.post('/predict',json={'profile':p,'threshold_profile':'research_balanced'});assert r.status_code==200
            direct=httpx.post('http://127.0.0.1:8000/predict',json={'profile':p,'threshold_profile':'research_balanced'},timeout=20)
            assert r.json()==direct.json()
            rows.append({'test':name,'status':'PASS','request':p,'response':r.json(),'proxy_matches_direct':True})
        switched=[]
        for policy in ['research_balanced','high_sensitivity_80','high_sensitivity_90']:
            r=client.post('/predict',json={'profile':{**LOW,'stroke_history':1},'threshold_profile':policy});assert r.status_code==200
            data=r.json();assert data['classification']==('elevated_model_association' if data['profile_score']>=data['threshold'] else 'lower_model_association')
            switched.append(data)
            rows.append({'test':'threshold '+policy,'status':'PASS','response':data})
        assert len({r['profile_score'] for r in switched})==1
        assert len({r['threshold'] for r in switched})==3
        assert len({r['classification'] for r in switched})==2
        r=client.post('/predict',json={'profile':{**LOW,'bmi':100}});assert r.status_code==422 and 'error' in r.json()
        rows.append({'test':'invalid BMI','status':'PASS','http_status':r.status_code})
    digest=hashlib.sha256((ROOT/'models/heart_disease_pipeline.joblib').read_bytes()).hexdigest();assert digest==EXPECTED
    report={'backend':backend,'integration_tests':len(rows),'integration_passed':len(rows),'checks':rows,'model_sha256_before':EXPECTED,'model_sha256_after':digest}
    (ROOT/'reports/model_qa/react_integration_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'backend':backend,'integration_tests':len(rows),'model_sha256':digest},indent=2))
if __name__=='__main__':main()
