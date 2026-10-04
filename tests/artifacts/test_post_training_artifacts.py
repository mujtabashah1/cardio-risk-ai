import hashlib,json,unittest
import numpy as np,pandas as pd
from pydantic import ValidationError
from api.config import Settings
from src.inference.constants import ROOT,MODEL_HASH,INTEGRITY_HASH,PROFILE_NAMES,DEFAULT_PROFILE,DEFAULT_THRESHOLD
from src.inference.service import InferenceService
from src.inference.threshold_policy import apply_threshold

class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=json.loads((ROOT/'models/threshold_profiles.json').read_text())
        cls.integrity=json.loads((ROOT/'reports/deployment/model_integrity.json').read_text())
        cls.comparison=pd.read_csv(ROOT/'reports/deployment/threshold_false_negative_comparison.csv',float_precision='round_trip').set_index('profile_name')
        cls.service=InferenceService(Settings())
    def test_all_four_required_files_physically_exist(self):
        for p in ['models/threshold_profiles.json','reports/deployment/model_integrity.json','reports/deployment/threshold_false_negative_comparison.csv','reports/deployment/false_negative_tradeoff.md']:
            self.assertTrue((ROOT/p).is_file());self.assertGreater((ROOT/p).stat().st_size,0)
    def test_profile_schema_and_default(self):
        self.assertEqual(self.policy['default_profile'],DEFAULT_PROFILE)
        self.assertEqual(set(self.policy['profiles']),set(PROFILE_NAMES))
        for p in self.policy['profiles'].values():
            self.assertIsInstance(p['threshold'],float);self.assertTrue(np.isfinite(p['threshold']));self.assertTrue(0<=p['threshold']<=1)
            self.assertIs(p['clinical_cutoff'],False);self.assertTrue(p['selection_basis']);self.assertTrue(p['intended_use'])
        self.assertEqual(self.policy['profiles'][DEFAULT_PROFILE]['threshold'],DEFAULT_THRESHOLD)
    def test_thresholds_match_unchanged_analysis(self):
        analysis=pd.read_csv(ROOT/'reports/modeling/threshold_analysis.csv',float_precision='round_trip')
        source=analysis[(analysis.model=='catboost_native')&(analysis.feature_set=='no_socioeconomic')&(analysis.calibration=='none')]
        for name,p in self.policy['profiles'].items():
            selected=source[source.selection==p['purpose']];self.assertEqual(len(selected),1)
            self.assertEqual(p['threshold'],float(selected.iloc[0].threshold));self.assertEqual(self.comparison.loc[name].threshold,p['threshold'])
    def test_cached_validation_reproduction(self):
        cache=ROOT/self.integrity['validation_probability_source']
        validation=ROOT/'data/processed/validation.csv'
        if not cache.exists() or not validation.exists():
            self.skipTest('Optional local audit requires excluded respondent validation data and prediction cache; not distributed on GitHub.')
        scores=np.load(cache)['probability']
        y=pd.read_csv(ROOT/'data/processed/validation.csv',usecols=['heart_disease']).heart_disease.to_numpy()
        self.assertEqual(len(scores),65109)
        for name,p in self.policy['profiles'].items():
            positive=scores>=p['threshold'];row=self.comparison.loc[name]
            for field,value in [('TP',np.sum((y==1)&positive)),('TN',np.sum((y==0)&~positive)),('FP',np.sum((y==0)&positive)),('FN',np.sum((y==1)&~positive))]:self.assertEqual(row[field],value)
        self.assertTrue(self.integrity['validation_predictions_reproduced'])
    def test_comparison_formulas_counts_and_deltas(self):
        baseline=self.comparison.loc[DEFAULT_PROFILE]
        for _,r in self.comparison.iterrows():
            self.assertEqual(r.TP+r.FN,5299);self.assertEqual(r.TN+r.FP,59810);self.assertEqual(r.TP+r.TN+r.FP+r.FN,65109)
            self.assertEqual(r.positive_count,5299);self.assertEqual(r.negative_count,59810)
            values={'recall':r.TP/5299,'false_negative_rate':r.FN/5299,'precision':r.TP/(r.TP+r.FP),'specificity':r.TN/59810,'false_positive_rate':r.FP/59810,'F1':2*r.TP/(2*r.TP+r.FP+r.FN),'accuracy':(r.TP+r.TN)/65109,'balanced_accuracy':(r.TP/5299+r.TN/59810)/2}
            for name,v in values.items():self.assertAlmostEqual(r[name],v,places=12)
            self.assertEqual(r.positive_predictions,r.TP+r.FP);self.assertEqual(r.negative_predictions,r.TN+r.FN)
            self.assertEqual(r.additional_true_positives_vs_research_balanced,r.TP-baseline.TP)
            self.assertEqual(r.reduction_in_false_negatives_vs_research_balanced,baseline.FN-r.FN)
            self.assertEqual(r.additional_false_positives_vs_research_balanced,r.FP-baseline.FP)
            for metric in ['precision','recall','specificity','F1']:self.assertAlmostEqual(r['delta_'+metric+'_vs_research_balanced'],r[metric]-baseline[metric],places=12)
    def test_integrity_required_fields_and_model_hash(self):
        r=self.integrity;actual=hashlib.sha256((ROOT/r['model_path']).read_bytes()).hexdigest()
        self.assertEqual(actual,MODEL_HASH);self.assertEqual(r['actual_sha256'],actual);self.assertEqual(r['expected_sha256'],MODEL_HASH)
        self.assertTrue(r['hash_match']);self.assertTrue(r['integrity_verified']);self.assertEqual(r['model_version'],'1.0.0')
        self.assertEqual(r['feature_count'],14);self.assertEqual(r['calibration'],'none');self.assertEqual(r['default_threshold'],DEFAULT_THRESHOLD)
        for field in ['verification_timestamp','feature_schema_path','metadata_path','model_version_file_path','api_model_loader']:self.assertTrue(r[field])
    def test_api_integrity_pin_and_supporting_hashes(self):
        self.assertEqual(hashlib.sha256((ROOT/'reports/deployment/model_integrity.json').read_bytes()).hexdigest(),INTEGRITY_HASH)
        for relative,expected in self.integrity['files_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),expected)
    def test_same_score_only_threshold_fields_change(self):
        expected=self.service.predict({'sex':1,'bmi':28.5})
        for name in PROFILE_NAMES:
            result=self.service.predict({'sex':1,'bmi':28.5},name)
            for key in expected:
                if key not in ['classification','threshold','threshold_profile']:self.assertEqual(result[key],expected[key])
            self.assertEqual(result['classification'],apply_threshold(result['profile_score'],result['threshold']))
    def test_leakage_fields_still_rejected(self):
        for field in ['heart_disease','_MICHD','CVDINFR4','CVDCRHD4']:
            with self.assertRaises(ValidationError):self.service.predict({'sex':1,field:1})
    def test_recovered_positives_and_false_positive_burden(self):
        for name,additional,extra_fp,fn in [('high_sensitivity_80',1522,10273,1060),('high_sensitivity_90',2052,18423,530)]:
            r=self.comparison.loc[name];self.assertEqual(r.additional_true_positives_vs_research_balanced,additional);self.assertEqual(r.additional_false_positives_vs_research_balanced,extra_fp);self.assertEqual(r.FN,fn)

if __name__=='__main__':unittest.main()
