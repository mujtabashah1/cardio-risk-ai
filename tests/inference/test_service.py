import json,subprocess,sys,unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from pydantic import ValidationError
from api.config import Settings
from src.inference.constants import ROOT,FEATURES,PROFILE_NAMES,DEFAULT_THRESHOLD
from src.inference.model_loader import load_artifacts,clear_cache
from src.inference.service import InferenceService
from src.inference.threshold_policy import apply_threshold

class InferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings=Settings();cls.service=InferenceService(cls.settings)
        cls.golden=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text())
        cls.profile=cls.golden[0]['input']
    def test_golden_single_and_batch(self):
        result=self.service.predict_batch([r['input'] for r in self.golden])
        for fixture,batch in zip(self.golden,result):
            single=self.service.predict(fixture['input'])
            self.assertAlmostEqual(single['profile_score'],fixture['expected_profile_score'],places=12)
            self.assertEqual(single,batch);self.assertEqual(single['classification'],fixture['expected_classification']);self.assertEqual(single['model_version'],'1.0.0')
    def test_load_once_under_concurrent_initialization(self):
        import joblib
        clear_cache()
        with patch('src.inference.model_loader.joblib.load',wraps=joblib.load) as load:
            with ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(load_artifacts,[self.settings]*8))
            self.assertEqual(load.call_count,1);self.assertTrue(all(v is values[0] for v in values))
            self.assertIs(load_artifacts(replace(self.settings,max_batch_size=2)),values[0])
            self.assertEqual(load.call_count,1)
    def test_all_threshold_profiles_preserve_probability(self):
        expected=self.service.predict(self.profile)['profile_score']
        thresholds=[]
        for name in PROFILE_NAMES:
            r=self.service.predict(self.profile,name)
            self.assertEqual(r['profile_score'],expected);thresholds.append(r['threshold'])
            self.assertEqual(r['classification'],apply_threshold(expected,r['threshold']))
        self.assertEqual(len(set(thresholds)),5)
        self.assertEqual(self.service.predict(self.profile)['threshold'],DEFAULT_THRESHOLD)
    def test_threshold_boundary_full_precision(self):
        self.assertEqual(apply_threshold(DEFAULT_THRESHOLD,DEFAULT_THRESHOLD),'elevated_model_association')
        self.assertEqual(apply_threshold(np.nextafter(DEFAULT_THRESHOLD,0),DEFAULT_THRESHOLD),'lower_model_association')
    def test_feature_order_and_exact_dataframe_columns(self):
        reverse=dict(reversed(list(self.profile.items())))
        self.assertEqual(self.service.predict(reverse),self.service.predict(self.profile))
        original=self.service.artifacts.pipeline.predict_proba
        with patch.object(self.service.artifacts.pipeline,'predict_proba',wraps=original) as call:
            self.service.predict(reverse)
            self.assertEqual(list(call.call_args.args[0].columns),list(FEATURES))
    def test_missing_supported(self):
        for profile in [dict.fromkeys(FEATURES),{'sex':1},{**self.profile,'high_cholesterol':None,'bmi':None,'smoking_status':None}]:
            p=self.service.predict(profile)['profile_score'];self.assertTrue(0<=p<=1)
    def test_invalid_values_never_become_missing(self):
        for field,value in [('bmi','28.5'),('bmi',True),('bmi',float('inf')),('bmi',float('nan')),('bmi',2500),('sex',1.0),('smoking_status',999),('diabetes',{}),('age_group',[1])]:
            with self.subTest(field=field,value=value),self.assertRaises(ValidationError):self.service.predict({**self.profile,field:value})
    def test_transactional_batch_no_prediction_for_invalid_row(self):
        with patch.object(self.service.artifacts.pipeline,'predict_proba') as call:
            with self.assertRaises(ValidationError):self.service.predict_batch([self.profile,{'sex':999}])
            call.assert_not_called()
    def test_unknown_features_and_leakage(self):
        for field in ['education','income_group','heart_disease','_MICHD','CVDINFR4','CVDCRHD4','AGE_GROUP']:
            with self.subTest(field=field),self.assertRaises(ValidationError):self.service.predict({**self.profile,field:1})
    def test_bad_structure_and_policy(self):
        for records in [[],None,{},[self.profile]*1001]:
            with self.assertRaises(ValueError):self.service.predict_batch(records)
        for name in [0.5,'unknown',None]:
            with self.assertRaises(ValueError):self.service.predict(self.profile,name)
    def test_concurrent_predictions(self):
        expected=self.service.predict(self.profile)
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(self.service.predict,[self.profile]*20))
        self.assertTrue(all(r==expected for r in results))
    def test_fresh_process_serialization(self):
        code="import json; from api.config import Settings; from src.inference.service import InferenceService; from src.inference.constants import ROOT; rows=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text()); s=InferenceService(Settings()); print(json.dumps({'single':[s.predict(r['input'])['profile_score'] for r in rows],'batch':[r['profile_score'] for r in s.predict_batch([r['input'] for r in rows])]}))"
        p=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True,check=True)
        result=json.loads(p.stdout)
        for key in ['single','batch']:np.testing.assert_allclose(result[key],[r['expected_profile_score'] for r in self.golden],rtol=0,atol=1e-12)

if __name__=='__main__':unittest.main()
