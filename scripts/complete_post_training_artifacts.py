"""Complete research threshold artifacts using cached validation scores only."""
import hashlib,json,re,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd
from src.models.metrics import metrics
from src.inference.constants import MODEL_HASH,FEATURES,DEFAULT_THRESHOLD
from api.config import Settings

OUT=ROOT/'reports/deployment'
REQUIRED=['models/threshold_profiles.json','reports/deployment/model_integrity.json','reports/deployment/threshold_false_negative_comparison.csv','reports/deployment/false_negative_tradeoff.md']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,indent=2),encoding='utf-8')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in rows)+'\n'

def complete():
    OUT.mkdir(parents=True,exist_ok=True)
    settings=Settings();actual=digest(settings.model_path)
    integrity_path=OUT/'model_integrity.json'
    report=json.loads(integrity_path.read_text()) if integrity_path.exists() else {}
    metadata=json.loads(settings.metadata_path.read_text())
    report.update(model_version=metadata['model_version'],model_path=str(settings.model_path.relative_to(ROOT)),expected_sha256=MODEL_HASH,actual_sha256=actual,current_sha256=actual,hash_match=actual==MODEL_HASH,model_family=metadata['model_family'],feature_set=metadata['feature_set'],feature_count=len(metadata['feature_names']),calibration=metadata['calibration_method'],default_threshold=metadata['classification_threshold'],integrity_verified=actual==MODEL_HASH,verification_timestamp=datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(),feature_schema_path=str(settings.schema_path.relative_to(ROOT)),metadata_path=str(settings.metadata_path.relative_to(ROOT)),model_version_file_path='models/model_version.txt',api_model_loader='src/inference/model_loader.py')
    if actual!=MODEL_HASH:
        report.update(passed=False,recorded_hash_matches=False,integrity_verified=False)
        write_json(integrity_path,report)
        raise RuntimeError('STOP: canonical API model hash differs from historical frozen hash. Model untouched.')
    assert metadata['model_version']=='1.0.0' and metadata['model_family']=='catboost'
    assert metadata['selected_experiment']=='gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none'
    assert metadata['feature_set']=='no_socioeconomic' and tuple(metadata['feature_names'])==FEATURES
    assert metadata['calibration_method']=='none' and metadata['classification_threshold']==DEFAULT_THRESHOLD
    schema=json.loads(settings.schema_path.read_text());assert tuple(f['name'] for f in schema['features'])==FEATURES
    freeze=json.loads((ROOT/'models/model_freeze.json').read_text())
    assert actual==freeze['pipeline_sha256'] and digest(settings.schema_path)==freeze['schema_sha256']
    for p,h in freeze['code_hashes'].items():assert digest(ROOT/p)==h,p
    preflight=json.loads((ROOT/'reports/modeling/data_preflight.json').read_text())
    for p,h in preflight['input_hashes'].items():assert digest(ROOT/p)==h,p
    validation=pd.read_csv(ROOT/'data/processed/validation.csv')
    cache=ROOT/'models/candidates'/f"{metadata['selected_experiment']}_validation.npz"
    scores=np.load(cache)['probability'];y=validation.heart_disease.to_numpy()
    try:
        assert len(scores)==len(y)==65109 and int(y.sum())==5299 and int((y==0).sum())==59810
        assert np.isfinite(scores).all() and ((scores>=0)&(scores<=1)).all()
        baseline=metrics(y,scores,DEFAULT_THRESHOLD)
        expected=json.loads((ROOT/'reports/modeling/final_validation_metrics.json').read_text())
        for k,v in expected.items():assert np.isclose(baseline[k],v,rtol=1e-12,atol=1e-12),k
        assert [baseline[k] for k in ['TP','TN','FP','FN']]==[2717,53906,5904,2582]
    except Exception as exc:
        (OUT/'threshold_reproducibility_failure.md').write_text('# STOP: validation score reproduction failed\n\n'+str(exc),encoding='utf-8')
        raise
    analysis_path=ROOT/'reports/modeling/threshold_analysis.csv'
    analysis=pd.read_csv(analysis_path,float_precision='round_trip')
    source=analysis[(analysis.model=='catboost_native')&(analysis.feature_set=='no_socioeconomic')&(analysis.calibration=='none')]
    spec={
      'research_balanced':('maximum_validation_F1','Maximum validation F1','Default research operating point'),
      'youden':('maximum_Youden_J','Maximum validation Youden J','Research sensitivity/specificity tradeoff'),
      'high_sensitivity_80':('approximately_80pct_recall','Approximately 80% validation recall','Research high-sensitivity operating point'),
      'high_sensitivity_90':('approximately_90pct_recall','Approximately 90% validation recall','Research very-high-sensitivity operating point'),
      'conventional_050':('default_0.50','Conventional classifier reference','Reference only')}
    policy=json.loads(settings.threshold_path.read_text()) if settings.threshold_path.exists() else {'model_version':'1.0.0','default_profile':'research_balanced','profiles':{}}
    profiles={};rows=[]
    for name,(selection,basis,intended) in spec.items():
        matched=source[source.selection==selection];assert len(matched)==1,name
        selected=matched.iloc[0];threshold=float(selected.threshold)
        assert 0<=threshold<=1
        if name=='research_balanced':assert threshold==DEFAULT_THRESHOLD
        m=metrics(y,scores,threshold)
        assert m['TP']+m['FN']==5299 and m['TN']+m['FP']==59810 and sum(m[k] for k in ['TP','TN','FP','FN'])==65109
        for k in ['TP','TN','FP','FN','precision','recall','specificity','accuracy','balanced_accuracy']:
            assert np.isclose(m[k],selected[k],rtol=1e-12,atol=1e-12),(name,k)
        assert np.isclose(m['f1'],selected.F1,rtol=1e-12,atol=1e-12)
        profiles[name]=dict(threshold=threshold,purpose=selection,selection_basis=basis,intended_use=intended,clinical_cutoff=False,validation_metrics={**{k:m[k] for k in ['precision','recall','specificity','TP','TN','FP','FN']},'F1':m['f1']})
        row=dict(profile_name=name,threshold=threshold,**{k:m[k] for k in ['TP','TN','FP','FN']},positive_count=5299,negative_count=59810,recall=m['recall'],false_negative_rate=m['FN']/5299,precision=m['precision'],specificity=m['specificity'],false_positive_rate=m['FP']/59810,F1=m['f1'],accuracy=m['accuracy'],balanced_accuracy=m['balanced_accuracy'],positive_predictions=m['TP']+m['FP'],negative_predictions=m['TN']+m['FN'],additional_true_positives_vs_research_balanced=m['TP']-baseline['TP'],reduction_in_false_negatives_vs_research_balanced=baseline['FN']-m['FN'],additional_false_positives_vs_research_balanced=m['FP']-baseline['FP'],delta_precision_vs_research_balanced=m['precision']-baseline['precision'],delta_recall_vs_research_balanced=m['recall']-baseline['recall'],delta_specificity_vs_research_balanced=m['specificity']-baseline['specificity'],delta_F1_vs_research_balanced=m['f1']-baseline['f1'])
        rows.append(row)
    policy.update(model_version='1.0.0',default_profile='research_balanced',policy_type='Named research operating points, not clinical cutoffs',source='reports/modeling/threshold_analysis.csv',profiles=profiles)
    write_json(settings.threshold_path,policy)
    pd.DataFrame(rows).to_csv(OUT/'threshold_false_negative_comparison.csv',index=False)
    readable=table(['Profile','Threshold','Recall','False negative rate','FN','TP','Precision','Specificity','FP','F1'],[[r['profile_name'],repr(r['threshold']),f"{r['recall']:.2%}",f"{r['false_negative_rate']:.2%}",r['FN'],r['TP'],f"{r['precision']:.2%}",f"{r['specificity']:.2%}",r['FP'],f"{r['F1']:.5f}"] for r in rows])
    text='# False-negative threshold tradeoff\n\n## Overview\n\nThe existing CatBoost model 1.0.0 is frozen and unchanged. No retraining, tuning, recalibration or new threshold selection occurred. This report reuses its cached validation probabilities (65,109 rows; 5,299 positives; 59,810 negatives) and the previously selected validation thresholds. Test data was not used for threshold optimization, and no test inference was run in this task.\n\n'+readable+'\n## Current default\n\n'+f"`research_balanced` retains threshold {DEFAULT_THRESHOLD}. TP {baseline['TP']:,}, FN {baseline['FN']:,}, recall {baseline['recall']:.2%}, false-negative rate {baseline['FN']/5299:.2%}, FP {baseline['FP']:,}, precision {baseline['precision']:.2%}, specificity {baseline['specificity']:.2%}, F1 {baseline['f1']:.5f}. **2,582 of 5,299 validation positives are missed**. Historical independent-test recall was 51.55% (2,567 missed positives), so roughly half of positive reported CHD/MI records were missed by the default binary operating point.\n"
    for name,title in [('high_sensitivity_80','Approximately 80% recall'),('high_sensitivity_90','Approximately 90% recall')]:
        r=next(r for r in rows if r['profile_name']==name)
        text+=f"\n## {title}\n\nThreshold {r['threshold']}; TP {r['TP']:,}, FN {r['FN']:,}, recall {r['recall']:.2%}, false-negative rate {r['false_negative_rate']:.2%}, precision {r['precision']:.2%}, specificity {r['specificity']:.2%}, FP {r['FP']:,}, F1 {r['F1']:.5f}.\n\nCompared with the default, this captures **{r['additional_true_positives_vs_research_balanced']:,} additional positives**, avoids **{r['reduction_in_false_negatives_vs_research_balanced']:,} false negatives**, and produces **{r['additional_false_positives_vs_research_balanced']:,} additional false positives**. Precision changes by {r['delta_precision_vs_research_balanced']*100:+.2f} percentage points, specificity by {r['delta_specificity_vs_research_balanced']*100:+.2f} points, and F1 by {r['delta_F1_vs_research_balanced']:+.5f}. Remaining missed positives: {r['FN']:,}.\n"
    text+='\n## Youden threshold\n\nYouden J = sensitivity + specificity - 1. This previously selected validation criterion balances two statistical rates, not medical consequences. Its threshold and all counts/rates are in the comparison table and CSV. It is not a medical cutoff.\n\n## 0.50 threshold\n\nThis is a conventional reference only. It misses 4,840 of 5,299 validation positives (recall 8.66%), despite reducing false positives to 344. A conventional probability threshold is not automatically appropriate.\n\n## Recommendation\n\nRetain research_balanced as the API default. The ~80% and ~90% profiles support explicitly requested sensitivity-oriented research objectives, recovering positives at substantial false-positive and precision costs. No clinical threshold is selected or recommended. External clinical validation and a defined cost/benefit framework are required before choosing a clinical screening operating point. The model describes existing self-reported CHD/MI associations, not a diagnosis or future risk.\n\n## Verification\n\nFor all five rows: TP + FN = 5,299; TN + FP = 59,810; all four counts total 65,109. Metrics were recomputed from cached validation scores and cross-checked against the unchanged threshold analysis. False-negative rate = FN/5,299; false-positive rate = FP/59,810. Probability stays identical between profiles; only threshold-based classification changes.\n'
    (OUT/'false_negative_tradeoff.md').write_text(text,encoding='utf-8')
    report.update(passed=True,recorded_hash_matches=True,integrity_verified=True,validation_predictions_reproduced=True,validation_metrics=baseline,validation_probability_source=str(cache.relative_to(ROOT)),validation_probability_sha256=digest(cache),threshold_analysis_sha256=digest(analysis_path),post_training_artifact_note='Validation-cache-only artifact completion; no new test inference, threshold optimization, or model changes.')
    if 'files_sha256' not in report:
        required_runtime=['models/heart_disease_pipeline.joblib','models/feature_schema.json','models/model_metadata.json','models/model_version.txt','models/threshold_profiles.json','data/processed/data_dictionary.csv','tests/fixtures/golden_predictions.json','src/models/config.py','src/models/estimators.py','src/models/preprocessing.py','src/data/mappings.py']
        report['files_sha256']={p:digest(ROOT/p) for p in required_runtime}
    else:report['files_sha256']['models/threshold_profiles.json']=digest(settings.threshold_path)
    report['input_hashes']=preflight['input_hashes']
    write_json(integrity_path,report)
    constants=ROOT/'src/inference/constants.py'
    updated=re.sub(r"INTEGRITY_HASH='[0-9a-f]+'",f"INTEGRITY_HASH='{digest(integrity_path)}'",constants.read_text())
    constants.write_text(updated,encoding='utf-8')
    for relative in REQUIRED:
        assert (ROOT/relative).is_file() and (ROOT/relative).stat().st_size
        print('[PASS]',relative,flush=True)
    print('Cached validation metrics reproduced; canonical model unchanged.',flush=True)
if __name__=='__main__':complete()
