import json,unittest,warnings
import joblib
import numpy as np
import pandas as pd
from src.models.config import ROOT
from src.models.inference import predict_heart_disease_profile,load_artifacts

class InferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline,cls.metadata,cls.schema=load_artifacts()
        example={'age_group':8,'sex':1,'bmi':28.5,'general_health':3,'physical_activity':1,'smoking_status':3,'diabetes':3,'stroke_history':0,'kidney_disease':0,'asthma':0,'difficulty_walking':0,'high_cholesterol':1,'high_blood_pressure':1,'alcohol_use':0,'education':3,'income_group':5}
        cls.record={f:example[f] for f in cls.metadata['feature_names']}
    def test_artifacts(self):
        self.assertEqual(self.metadata['model_version'],'1.0.0')
        self.assertEqual(self.metadata['feature_names'],[f['name'] for f in self.schema['features']])
        self.assertNotIn('heart_disease',self.metadata['feature_names'])
    def test_valid_and_batch(self):
        r=predict_heart_disease_profile(self.record)
        self.assertGreaterEqual(r['probability'],0);self.assertLessEqual(r['probability'],1)
        self.assertEqual(r['classification'],int(r['probability']>=r['threshold']))
        b=predict_heart_disease_profile([self.record,self.record])
        self.assertEqual(len(b),2);self.assertAlmostEqual(b[0]['probability'],r['probability'])
    def test_missing_allowed(self):
        for f in ['bmi','high_cholesterol','income_group','smoking_status']:
            if f in self.record:
                r=predict_heart_disease_profile({**self.record,f:None})
                self.assertTrue(np.isfinite(r['probability']))
        self.assertTrue(np.isfinite(predict_heart_disease_profile({'sex':1})['probability']))
    def test_unknown_category(self):
        r=predict_heart_disease_profile({**self.record,'smoking_status':999})
        self.assertTrue(np.isfinite(r['probability']));self.assertTrue(r['warnings'])
    def test_feature_order(self):
        reverse=dict(reversed(list(self.record.items())))
        self.assertAlmostEqual(predict_heart_disease_profile(reverse)['probability'],predict_heart_disease_profile(self.record)['probability'])
        one=self.pipeline.predict_proba(pd.DataFrame([self.record]))
        two=self.pipeline.predict_proba(pd.DataFrame([reverse]))
        np.testing.assert_allclose(one,two,rtol=0,atol=0)
    def test_serialized_predictions(self):
        reloaded=joblib.load(ROOT/'models/heart_disease_pipeline.joblib')
        frame=pd.DataFrame([self.record])
        np.testing.assert_allclose(reloaded.predict_proba(frame),self.pipeline.predict_proba(frame),rtol=0,atol=0)
    def test_bad_names_and_leakage(self):
        for f in ['made_up','heart_disease','_MICHD','CVDINFR4','CVDCRHD4']:
            with self.subTest(feature=f),self.assertRaises(ValueError):predict_heart_disease_profile({**self.record,f:1})
    def test_bad_types(self):
        for value in ['28.5',{},[],True,float('inf')]:
            with self.subTest(value=value),self.assertRaises((ValueError,TypeError)):predict_heart_disease_profile({**self.record,'bmi':value})
        with self.assertRaises(TypeError):predict_heart_disease_profile({**self.record,'sex':'Male'})
        with self.assertRaises(TypeError):predict_heart_disease_profile({**self.record,'age_group':3.5})
        with self.assertRaises(ValueError):predict_heart_disease_profile({**self.record,'bmi':.285})
    def test_bad_structure(self):
        for value in [None,[],{},'text',[None]]:
            with self.subTest(value=value),self.assertRaises(TypeError):predict_heart_disease_profile(value)

if __name__=='__main__':unittest.main()
