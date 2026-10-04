import json,unittest
from pathlib import Path
from fastapi.testclient import TestClient
from api.main import create_app
from scripts.run_model_qa import LOW,HIGH
from src.inference.validation import DOMAINS
class WebsiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.client=TestClient(create_app());cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def test_page(self):
        r=self.client.get('/testing/');self.assertEqual(r.status_code,200);self.assertIn('Model Profile Score',r.text)
    def test_assets(self):
        for file in ['app.js','style.css']:self.assertEqual(self.client.get('/testing/'+file).status_code,200)
    def test_all_14_fields(self):self.assertEqual(len(LOW),14);self.assertEqual(self.client.post('/predict',json={'profile':LOW}).status_code,200)
    def test_dropdown_domains(self):
        for key,values in DOMAINS.items():
            for value in values:self.assertEqual(self.client.post('/predict',json={'profile':{**LOW,key:value}}).status_code,200)
    def test_missing(self):self.assertEqual(self.client.post('/predict',json={'profile':dict.fromkeys(LOW)}).status_code,200)
    def test_bmi_not_scaled(self):self.assertEqual(self.client.post('/predict',json={'profile':{**LOW,'bmi':28.5}}).status_code,200);self.assertEqual(self.client.post('/predict',json={'profile':{**LOW,'bmi':2850}}).status_code,422)
    def test_presets(self):
        for p in [LOW,HIGH]:self.assertIn('profile_score',self.client.post('/predict',json={'profile':p}).json())
    def test_error(self):self.assertIn('error',self.client.post('/predict',json={'profile':{'bmi':100}}).json())
    def test_threshold_switch(self):
        rows=[self.client.post('/predict',json={'profile':HIGH,'threshold_profile':t}).json() for t in ['research_balanced','high_sensitivity_80','high_sensitivity_90','youden','conventional_050']];self.assertEqual(len({r['profile_score'] for r in rows}),1);self.assertEqual(len({r['threshold'] for r in rows}),5)
