"""One independent evaluation of the frozen pipeline; no training or tuning."""
import json,time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score,average_precision_score
from .config import ROOT,TARGET,SEED
from .metrics import metrics
from .preflight import sha
from .model_selection import subgroup_rows
from .train_models import now,write_json

OUT=ROOT/'reports/modeling'

def evaluate():
    result_path=OUT/'final_test_metrics.json'
    if result_path.exists():
        print('Independent test evaluation already recorded; returning existing results without another prediction call.',flush=True)
        return json.loads(result_path.read_text())
    freeze=json.loads((OUT/'frozen_model_specification.json').read_text())
    assert sha(ROOT/'models/heart_disease_pipeline.joblib')==freeze['pipeline_sha256']
    assert sha(ROOT/'models/feature_schema.json')==freeze['schema_sha256']
    for path,value in freeze['code_hashes'].items():assert sha(ROOT/path)==value,f'Frozen source changed: {path}'
    metadata=json.loads((ROOT/'models/model_metadata.json').read_text())
    assert metadata['feature_names']==freeze['model_specification']['feature_names']
    assert metadata['classification_threshold']==freeze['model_specification']['classification_threshold']
    preflight=json.loads((OUT/'data_preflight.json').read_text())
    assert sha(ROOT/'data/processed/test.csv')==preflight['input_hashes'][str((ROOT/'data/processed/test.csv').relative_to(ROOT))]
    with (OUT/'test_evaluation_started.json').open('x') as f:
        json.dump(dict(timestamp=now(),pipeline_sha256=freeze['pipeline_sha256'],purpose='Exactly one frozen-model test prediction; all choices already saved'),f,indent=2)
    start=time.perf_counter()
    test=pd.read_csv(ROOT/'data/processed/test.csv');features=metadata['feature_names'];threshold=metadata['classification_threshold']
    pipeline=joblib.load(ROOT/'models/heart_disease_pipeline.joblib')
    p=pipeline.predict_proba(test[features])[:,1] # Sole model prediction call on test data.
    y=test[TARGET].to_numpy();result=metrics(y,p,threshold)
    result.update(evaluation_timestamp=now(),evaluation_runtime_seconds=time.perf_counter()-start,pipeline_sha256=freeze['pipeline_sha256'],model_version=metadata['model_version'],test_used_for_selection=False,model_refit_after_test=False)
    np.savez_compressed(OUT/'frozen_test_predictions.npz',probability=p,target=y)
    write_json(result_path,result)
    metadata['test_metrics']=result;write_json(ROOT/'models/model_metadata.json',metadata)
    subgroup=pd.read_csv(OUT/'subgroup_metrics.csv')
    pd.concat([subgroup,pd.DataFrame(subgroup_rows(test,p,threshold,'test'))],ignore_index=True).to_csv(OUT/'subgroup_metrics.csv',index=False)
    fig,ax=plt.subplots(figsize=(7,6));matrix=np.array([[result['TN'],result['FP']],[result['FN'],result['TP']]])
    image=ax.imshow(matrix,cmap='Blues')
    for i in range(2):
        for j in range(2):ax.text(j,i,f'{matrix[i,j]:,}',ha='center',va='center',color='white' if matrix[i,j]>matrix.max()/2 else 'black',fontsize=16)
    ax.set_xticks([0,1],['Negative','Positive']);ax.set_yticks([0,1],['Negative','Positive']);ax.set(xlabel='Predicted reported CHD/MI class',ylabel='Observed reported CHD/MI class',title=f'Independent test confusion matrix; threshold {threshold:.4f}')
    fig.colorbar(image,ax=ax,fraction=.046,pad=.04);fig.tight_layout();fig.savefig(OUT/'confusion_matrix.png',dpi=170);plt.close(fig)
    # Fixed-prediction grouped bootstrap: no repeat fitting, prediction or optimization.
    groups=pd.read_csv(ROOT/'data/processed/split_membership.csv').query("split == 'test'").equality_group.to_numpy()
    _,inverse=np.unique(groups,return_inverse=True);n=int(inverse.max()+1);rng=np.random.default_rng(SEED)
    measures={k:[] for k in ['roc_auc','pr_auc','recall','specificity','f1']}
    label=p>=threshold
    for _ in range(150):
        weights=np.bincount(rng.integers(0,n,n),minlength=n)[inverse]
        tp=float(weights[(y==1)&label].sum());tn=float(weights[(y==0)&~label].sum());fp=float(weights[(y==0)&label].sum());fn=float(weights[(y==1)&~label].sum())
        measures['roc_auc'].append(roc_auc_score(y,p,sample_weight=weights));measures['pr_auc'].append(average_precision_score(y,p,sample_weight=weights))
        measures['recall'].append(tp/(tp+fn));measures['specificity'].append(tn/(tn+fp));measures['f1'].append(2*tp/(2*tp+fp+fn))
    intervals={k:dict(estimate=result[k],CI95_low=float(np.quantile(v,.025)),CI95_high=float(np.quantile(v,.975))) for k,v in measures.items()}
    write_json(OUT/'test_confidence_intervals.json',dict(method='150 labeled-record-group bootstrap replicates of frozen test predictions',seed=SEED,metrics=intervals))
    for path,value in preflight['input_hashes'].items():assert sha(ROOT/path)==value,f'Processed input changed: {path}'
    write_json(OUT/'final_integrity_check.json',dict(passed=True,all_processed_inputs_and_CDC_mappings_unchanged=True,frozen_pipeline_unchanged=sha(ROOT/'models/heart_disease_pipeline.joblib')==freeze['pipeline_sha256'],test_evaluation_calls=1,no_post_test_tuning=True))
    print(json.dumps(result,indent=2),flush=True)
    return result

if __name__=='__main__':evaluate()
