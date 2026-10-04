"""Explicit frozen-artifact reproduction audit; never training or selection."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib,numpy as np,pandas as pd
from src.models.metrics import metrics
EXPECTED_HASH='4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1'
FEATURES=['age_group','sex','bmi','general_health','physical_activity','smoking_status','diabetes','stroke_history','kidney_disease','asthma','difficulty_walking','high_cholesterol','high_blood_pressure','alcohol_use']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def main():
    out=ROOT/'reports/deployment';out.mkdir(parents=True,exist_ok=True)
    try:
        model_path=ROOT/'models/heart_disease_pipeline.joblib'
        assert digest(model_path)==EXPECTED_HASH,'Pipeline hash mismatch'
        freeze=json.loads((ROOT/'models/model_freeze.json').read_text())
        metadata=json.loads((ROOT/'models/model_metadata.json').read_text())
        schema=json.loads((ROOT/'models/feature_schema.json').read_text())
        assert metadata['feature_names']==FEATURES==[f['name'] for f in schema['features']]
        assert metadata['model_version']=='1.0.0' and metadata['feature_set']=='no_socioeconomic'
        assert metadata['selected_experiment']=='gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none'
        assert metadata['calibration_method']=='none' and metadata['classification_threshold']==0.20943938491134126
        assert digest(model_path)==freeze['pipeline_sha256']
        assert digest(ROOT/'models/feature_schema.json')==freeze['schema_sha256']
        for p,h in freeze['code_hashes'].items():assert digest(ROOT/p)==h,f'Frozen source altered: {p}'
        preflight=json.loads((ROOT/'reports/modeling/data_preflight.json').read_text())
        for p,h in preflight['input_hashes'].items():assert digest(ROOT/p)==h,f'Prepared input altered: {p}'
        model=joblib.load(model_path)
        assert list(model.named_steps)==['guard','preprocess','classifier']
        assert model.named_steps['guard'].features==FEATURES
        test=pd.read_csv(ROOT/'data/processed/test.csv')
        probability=model.predict_proba(test[FEATURES])[:,1]
        reference=np.load(ROOT/'reports/modeling/frozen_test_predictions.npz')
        np.testing.assert_allclose(probability,reference['probability'],rtol=1e-12,atol=1e-12)
        result=metrics(test.heart_disease,probability,metadata['classification_threshold'])
        saved=json.loads((ROOT/'reports/modeling/final_test_metrics.json').read_text())
        for k,v in result.items():assert np.isclose(v,saved[k],rtol=1e-12,atol=1e-12),k
        thresholds=pd.read_csv(ROOT/'reports/modeling/threshold_analysis.csv',float_precision='round_trip')
        rows=thresholds[(thresholds.model=='catboost_native')&(thresholds.feature_set=='no_socioeconomic')&(thresholds.calibration=='none')]
        names={'research_balanced':'maximum_validation_F1','high_sensitivity_80':'approximately_80pct_recall','high_sensitivity_90':'approximately_90pct_recall','youden':'maximum_Youden_J','conventional_050':'default_0.50'}
        profiles={}
        for name,selection in names.items():
            row=rows[rows.selection==selection];assert len(row)==1,selection
            row=row.iloc[0]
            profiles[name]={'threshold':float(row.threshold),'purpose':selection,'validation_metrics':{k:float(row[k]) if k not in ['TP','TN','FP','FN'] else int(row[k]) for k in ['precision','recall','specificity','F1','TP','TN','FP','FN']}}
        assert profiles['research_balanced']['threshold']==metadata['classification_threshold']
        write(ROOT/'models/threshold_profiles.json',{'model_version':'1.0.0','default_profile':'research_balanced','policy_type':'Named research operating points, not clinical cutoffs','source':'reports/modeling/threshold_analysis.csv','profiles':profiles})
        normal=dict(age_group=8,sex=1,bmi=28.5,general_health=3,physical_activity=1,smoking_status=3,diabetes=3,stroke_history=0,kidney_disease=0,asthma=0,difficulty_walking=0,high_cholesterol=1,high_blood_pressure=1,alcohol_use=0)
        examples=[('synthetic_complete',normal),('synthetic_elevated',{**normal,'age_group':12,'general_health':5,'stroke_history':1,'diabetes':1,'difficulty_walking':1}),('synthetic_partial',{'sex':2,'bmi':None}),('synthetic_missing',dict.fromkeys(FEATURES))]
        fixtures=[]
        for name,profile in examples:
            frame=pd.DataFrame([{f:profile.get(f,np.nan) for f in FEATURES}],columns=FEATURES)
            p=float(model.predict_proba(frame)[0,1])
            fixtures.append(dict(name=name,input=profile,expected_profile_score=p,expected_classification='elevated_model_association' if p>=metadata['classification_threshold'] else 'lower_model_association',model_version='1.0.0',absolute_tolerance=1e-12))
        write(ROOT/'tests/fixtures/golden_predictions.json',fixtures)
        runtime=['src/models/config.py','src/models/estimators.py','src/models/preprocessing.py','src/data/mappings.py']
        files=['models/heart_disease_pipeline.joblib','models/feature_schema.json','models/model_metadata.json','models/model_version.txt','models/threshold_profiles.json','data/processed/data_dictionary.csv','tests/fixtures/golden_predictions.json']+runtime
        write(out/'model_integrity.json',dict(passed=True,model_version='1.0.0',pipeline_sha256=EXPECTED_HASH,recorded_hash_matches=True,feature_names=FEATURES,frozen_metrics_reproduced=True,max_probability_absolute_difference=float(np.max(np.abs(probability-reference['probability']))),metrics=result,reproduction_note='One explicitly requested post-training reproduction audit against cached official test probabilities; not a new selection/evaluation and no historical reports overwritten.',files_sha256={p:digest(ROOT/p) for p in files},input_hashes=preflight['input_hashes']))
        (out/'pipeline_audit.md').write_text(f'# Frozen pipeline audit\n\nSHA-256: `{EXPECTED_HASH}`. Model version 1.0.0 and all frozen sources match. Official test probabilities and metrics reproduce within 1e-12. One explicitly requested reproduction prediction was made without changing historical reports or making model decisions.\n\nFeatureGuard reorders the 14 named numeric/null inputs. The historical guard maps unsupported categorical codes to missing with warnings; the serving boundary instead rejects invalid codes. BMI is human-readable, restricted to the saved 12–99.99 policy, and never divided by 100.\n\nNativeCategories fills BMI with model-fit training median **{model.named_steps['preprocess'].bmi_median_}**. Category codes become integer strings; nulls become `__MISSING__`. No statistic is newly fitted. Native CatBoost has 220 iterations, depth 6 and learning rate 0.08, without class weights. `predict_proba` column 1 corresponds to target class 1. No calibrator is added. Profiles compare the same full-precision score using `>=`.\n\nExpected order: '+', '.join(FEATURES)+'\n',encoding='utf-8')
        # Keep the richer post-training artifacts and serving integrity pin synchronized.
        from scripts.complete_post_training_artifacts import complete
        complete()
        print(json.dumps({'passed':True,'hash':EXPECTED_HASH,'reproduction_max_difference':float(np.max(np.abs(probability-reference['probability']))),'profiles':profiles},indent=2))
    except Exception as exc:
        (out/'model_reproducibility_failure.md').write_text('# STOP: frozen artifact reproduction failed\n\n'+str(exc),encoding='utf-8')
        raise
if __name__=='__main__':main()
