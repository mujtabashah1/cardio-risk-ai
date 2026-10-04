"""Validation-only analysis and export. This module never reads test.csv."""
import json,time,logging
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve,roc_curve,average_precision_score
from sklearn.calibration import CalibratedClassifierCV,calibration_curve
from sklearn.frozen import FrozenEstimator
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .config import ROOT,FEATURE_SETS,TARGET,SEED,THREADS
from .metrics import metrics
from .preflight import sha,environment
from .train_models import now,write_json

OUT=ROOT/'reports/modeling'
LIMITATIONS=['Cross-sectional, self-reported existing CHD/MI; no prospective 10-year endpoint, diagnosis validation, or temporal causality.','BRFSS 2021 U.S. and territory respondents; generalization outside comparable populations is unknown.','Unweighted respondent classification, not survey-weighted population prevalence estimation.','Class imbalance, screening-dependent cholesterol status, missing values, and possible subgroup differences.','Income nonresponse and U.S.-dollar groups reduce portability; socioeconomic and temporal-proxy fields need explicit interpretation.','The fixed grouped split has predictor-missingness shifts (notably BMI); it was preserved unchanged.','Repeated validation-based comparisons can overfit selection; external validation is required before clinical use.','GPU numerical training is not guaranteed bitwise deterministic despite seed 42.','Software-ready profile classification does not establish clinical validity.']

def prediction(record):
    return np.load(ROOT/'models/candidates'/f'{record["experiment_id"]}_validation.npz')['probability']

def unwrap(model):
    if isinstance(model,CalibratedClassifierCV):model=model.estimator
    if isinstance(model,FrozenEstimator):model=model.estimator
    return model

def threshold_choices(y,p):
    precision,recall,thresholds=precision_recall_curve(y,p)
    f1=2*precision[:-1]*recall[:-1]/np.maximum(precision[:-1]+recall[:-1],1e-15)
    fpr,tpr,roc_threshold=roc_curve(y,p)
    usable=np.isfinite(roc_threshold)&(roc_threshold>=0)&(roc_threshold<=1)
    j_idx=np.flatnonzero(usable)[np.argmax((tpr-fpr)[usable])]
    return {'default_0.50':.5,'maximum_validation_F1':float(thresholds[np.argmax(f1)]),'maximum_Youden_J':float(roc_threshold[j_idx]),'approximately_80pct_recall':float(np.quantile(p[np.asarray(y)==1],.2)),'approximately_90pct_recall':float(np.quantile(p[np.asarray(y)==1],.1))}

def paired_AP_interval(y,a,b,groups,iterations=150):
    _,inverse=np.unique(groups,return_inverse=True);n=int(inverse.max()+1)
    rng=np.random.default_rng(SEED);differences=[]
    for _ in range(iterations):
        multiplicity=np.bincount(rng.integers(0,n,n),minlength=n)
        weight=multiplicity[inverse]
        differences.append(average_precision_score(y,a,sample_weight=weight)-average_precision_score(y,b,sample_weight=weight))
    return dict(AP_difference=float(average_precision_score(y,a)-average_precision_score(y,b)),CI95_low=float(np.quantile(differences,.025)),CI95_high=float(np.quantile(differences,.975)),bootstrap_iterations=iterations,method='Paired labeled-record-group bootstrap of validation predictions; exploratory, not clinical significance')

def subgroup_rows(frame,p,threshold,dataset='validation'):
    rows=[]
    for feature in ['sex','age_group']:
        for value,indices in frame.groupby(feature,dropna=False).groups.items():
            positions=frame.index.get_indexer(indices);y=frame.iloc[positions][TARGET]
            rows.append(dict(dataset=dataset,subgroup_feature=feature,subgroup_value='missing' if pd.isna(value) else int(value),unstable=len(y)<200 or int(y.sum())<30,stability_rule='Descriptive flag: n<200 or positives<30',**metrics(y,p[positions],threshold)))
    return rows

def compare_tables(records):
    rows=[]
    for r in records:
        if r.get('status')!='success':continue
        m=r['validation_metrics'];row=dict(experiment_id=r['experiment_id'],model=r['model_name'],model_family=r['model_family'],feature_set=r['feature_set'],feature_count=r['number_of_features'],device=r.get('device_used','CPU'),imputation=r['imputation'],categorical_encoding=r['preprocessing'],class_weighting=r['class_weighting'],hyperparameters_summary=json.dumps(r['hyperparameters'],default=str),calibration=r['calibration'],accuracy=m['accuracy'],balanced_accuracy=m['balanced_accuracy'],precision=m['precision'],recall=m['recall'],specificity=m['specificity'],F1=m['f1'],ROC_AUC=m['roc_auc'],PR_AUC=m['pr_auc'],Brier=m['brier'],log_loss=m['log_loss'],TP=m['TP'],TN=m['TN'],FP=m['FP'],FN=m['FN'],training_time=r['runtime_seconds'])
        rows.append(row)
    comparison=pd.DataFrame(rows)
    comparison.to_csv(OUT/'model_comparison.csv',index=False)
    baseline_ids={r['experiment_id'] for r in records if r.get('stage') in ['baseline','gpu_baseline']}
    comparison[comparison.experiment_id.isin(baseline_ids)].to_csv(OUT/'baseline_model_comparison.csv',index=False)
    ablations=comparison[comparison.feature_set.isin(FEATURE_SETS)].copy()
    ablations['PR_AUC_difference_vs_matched_full']=np.nan
    ablations['ROC_AUC_difference_vs_matched_full']=np.nan
    for _,sub in ablations.groupby(['model','calibration','device','imputation','categorical_encoding']):
        full=sub[sub.feature_set=='full_features']
        if len(full):
            reference=full.iloc[0]
            ablations.loc[sub.index,'PR_AUC_difference_vs_matched_full']=sub.PR_AUC-reference.PR_AUC
            ablations.loc[sub.index,'ROC_AUC_difference_vs_matched_full']=sub.ROC_AUC-reference.ROC_AUC
    ablations.to_csv(OUT/'feature_set_comparison.csv',index=False)
    benchmark=comparison[comparison.experiment_id.str.startswith('benchmark__')].copy()
    details={r['experiment_id']:r for r in records}
    benchmark['model_fit_seconds']=benchmark.experiment_id.map(lambda i:details[i].get('model_fit_seconds'))
    benchmark['preprocessing_fit_seconds']=benchmark.experiment_id.map(lambda i:details[i].get('preprocessing_fit_seconds'))
    benchmark['peak_GPU_total_used_MiB']=benchmark.experiment_id.map(lambda i:details[i].get('peak_GPU_total_used_MiB'))
    benchmark['memory_measurement_note']='One-second nvidia-smi total-device samples; includes other processes, not an exact allocator peak'
    benchmark.to_csv(OUT/'gpu_cpu_benchmark.csv',index=False)
    # Retain every earlier experiment and its values, augmenting only missing device metadata.
    log=pd.DataFrame(records)
    for col,default in [('device_used','CPU'),('device_requested','cpu'),('fallback_occurred',False),('CV_folds',0)]:
        if col not in log:log[col]=default
        else:log[col]=log[col].fillna(default)
    for key,alias in [('f1','F1'),('roc_auc','ROC_AUC'),('pr_auc','PR_AUC'),('brier','Brier')]:log['validation_'+alias]=log.validation_metrics.map(lambda m:m.get(key) if isinstance(m,dict) else None)
    for key in ['accuracy','balanced_accuracy','precision','recall','specificity','log_loss']:log['validation_'+key]=log.validation_metrics.map(lambda m:m.get(key) if isinstance(m,dict) else None)
    log['training_runtime_seconds']=log.runtime_seconds
    for col,source in [('categorical_strategy','preprocessing'),('imputation_strategy','imputation')]:
        if col not in log:log[col]=log[source]
        else:log[col]=log[col].fillna(log[source])
    hardware=json.loads((OUT/'hardware_environment.json').read_text())
    for col,value in [('gpu_name',hardware['GPU_model']),('cuda_available',hardware['CUDA_available'])]:
        if col not in log:log[col]=value
        else:log[col]=log[col].fillna(value)
    log['calibration_device']=np.where(log.calibration!='none','CPU','not applicable')
    for model_family in ['catboost','xgboost','logistic']:
        tuning_path=OUT/f'tuning_{model_family}.json'
        if tuning_path.exists():
            tuning=json.loads(tuning_path.read_text())
            log.loc[(log.model_family==model_family)&(log.stage=='tuned'),'CV_folds']=tuning['folds']
    for key in ['hyperparameters','validation_metrics']:
        log[key]=log[key].map(lambda v:json.dumps(v,default=str))
    log.to_csv(OUT/'experiment_log.csv',index=False)
    return comparison

def explain(record,model,validation):
    features=FEATURE_SETS[record['feature_set']]
    indices,_=train_test_split(np.arange(len(validation)),train_size=2000,stratify=validation[TARGET],random_state=SEED)
    sample=validation.iloc[indices];X=sample[features];y=sample[TARGET]
    with threadpool_limits(limits=THREADS):
        permutation=permutation_importance(model,X,y,scoring='average_precision',n_repeats=3,n_jobs=1,random_state=SEED)
    importance=pd.DataFrame({'feature':features,'permutation_AP_decrease':permutation.importances_mean,'permutation_std':permutation.importances_std}).sort_values('permutation_AP_decrease',ascending=False)
    importance.to_csv(OUT/'feature_importance.csv',index=False)
    base=unwrap(model);classifier=base.named_steps['classifier'];transformed=base[:-1].transform(X)
    try:
        if hasattr(classifier,'model_') or classifier.__class__.__module__.startswith('catboost'):
            from catboost import Pool
            actual=classifier.model_ if hasattr(classifier,'model_') else classifier
            cats=[c for c in transformed if c!='bmi'] if isinstance(transformed,pd.DataFrame) else []
            pool=Pool(transformed,cat_features=cats or None)
            values=actual.get_feature_importance(pool,type='ShapValues',thread_count=THREADS)[:,:-1]
            builtin=actual.get_feature_importance()
        else:
            import shap
            actual=classifier
            values=shap.TreeExplainer(classifier).shap_values(transformed)
            if isinstance(values,list):values=values[1]
            if values.ndim==3:values=values[:,:,1]
            builtin=getattr(classifier,'feature_importances_',None)
        if isinstance(transformed,pd.DataFrame):names=list(transformed.columns)
        else:names=list(base.named_steps['preprocess'].get_feature_names_out())
        aggregated=np.zeros((len(X),len(features)));built=np.zeros(len(features))
        for j,name in enumerate(names):
            matched=[i for i,f in enumerate(features) if name==f or name==f'bmi__{f}' or name==f'ordinal_comparison__{f}' or name.startswith(f'categories__{f}_')]
            if not matched:raise ValueError(f'Cannot map transformed feature {name}')
            aggregated[:,matched[0]]+=values[:,j]
            if builtin is not None:built[matched[0]]+=builtin[j]
        shap_table=pd.DataFrame({'feature':features,'mean_absolute_SHAP':np.abs(aggregated).mean(axis=0)}).sort_values('mean_absolute_SHAP',ascending=False)
        shap_table.to_csv(OUT/'shap_importance.csv',index=False)
        np.savez_compressed(OUT/'shap_values_validation_sample.npz',SHAP=aggregated,features=np.array(features),validation_row_indices=indices)
        if builtin is not None:pd.DataFrame({'feature':features,'built_in_importance':built}).sort_values('built_in_importance',ascending=False).to_csv(OUT/'built_in_feature_importance.csv',index=False)
        order=np.argsort(np.abs(aggregated).mean(axis=0));rng=np.random.default_rng(SEED)
        fig,ax=plt.subplots(figsize=(10,7))
        for position,j in enumerate(order):ax.scatter(aggregated[:,j],position+rng.uniform(-.3,.3,len(X)),s=4,alpha=.25,color='#285f9b',rasterized=True)
        ax.set_yticks(range(len(features)),[features[j] for j in order]);ax.axvline(0,color='gray',lw=1)
        ax.set_xlabel('SHAP contribution to uncalibrated model output (not causal)');ax.set_title('2,000 stratified validation profiles: feature contributions')
        fig.tight_layout();fig.savefig(OUT/'shap_summary.png',dpi=170);plt.close(fig)
        write_json(OUT/'explainability_method.json',dict(permutation_rows=2000,repeats=3,permutation_score='average_precision',SHAP_rows=2000,SHAP_model='Underlying uncalibrated classifier; does not explain the calibration map',SHAP_method='Native CatBoost Tree SHAP' if actual.__class__.__module__.startswith('catboost') else 'shap.TreeExplainer',one_hot_aggregation='Sum signed contributions of each original feature before calculating mean absolute contribution',seed=SEED))
    except Exception as e:
        write_json(OUT/'shap_failure.json',dict(error=repr(e),note='No SHAP plot or values fabricated; permutation importance remains valid.'))
        logging.exception('SHAP computation failed')
    return importance

def select_and_export():
    if (ROOT/'models/model_freeze.json').exists():raise RuntimeError('Already frozen; selection cannot be repeated after test access.')
    assert (OUT/'training_complete.json').exists()
    records=json.loads((OUT/'experiment_records.json').read_text());comparison=compare_tables(records)
    success=[r for r in records if r.get('status')=='success' and r.get('model_family')!='dummy' and r['feature_set'] in FEATURE_SETS]
    validation=pd.read_csv(ROOT/'data/processed/validation.csv');y=validation[TARGET].to_numpy()
    groups=pd.read_csv(ROOT/'data/processed/split_membership.csv').query("split == 'validation'").equality_group.to_numpy()
    best={};calibration_choices=[]
    for set_name in FEATURE_SETS:
        raw=max([r for r in success if r['feature_set']==set_name and r['calibration']=='none'],key=lambda r:r['validation_metrics']['pr_auc'])
        versions=[raw]+[r for r in success if r['feature_set']==set_name and r['model_name']==raw['model_name'] and r['calibration']!='none']
        selected=min(versions,key=lambda r:r['validation_metrics']['brier'])
        best[set_name]=selected
        calibration_choices.extend(dict(feature_set=set_name,experiment_id=r['experiment_id'],method=r['calibration'],selected=r['experiment_id']==selected['experiment_id'],**r['validation_metrics']) for r in versions)
    pd.DataFrame(calibration_choices).to_csv(OUT/'calibration_comparison.csv',index=False)
    leader=max(best.values(),key=lambda r:r['validation_metrics']['pr_auc']);core=best['core_features'];no_soc=best['no_socioeconomic']
    difference_core=paired_AP_interval(y,prediction(leader),prediction(core),groups)
    selected=core if difference_core['CI95_low']<=0 else leader
    difference_socio=paired_AP_interval(y,prediction(selected),prediction(no_soc),groups)
    if selected['feature_set']=='full_features' and difference_socio['CI95_low']<=0:selected=no_soc
    chosen=joblib.load(ROOT/selected['model_path']);features=FEATURE_SETS[selected['feature_set']];p=prediction(selected)
    choices=threshold_choices(y,p);threshold=choices['maximum_validation_F1']
    threshold_rows=[]
    for set_name,record in best.items():
        probabilities=prediction(record);special=threshold_choices(y,probabilities)
        for value in np.arange(.01,1.,.01):threshold_rows.append(dict(model=record['model_name'],feature_set=set_name,calibration=record['calibration'],selection='grid',**metrics(y,probabilities,float(value))))
        for reason,value in special.items():threshold_rows.append(dict(model=record['model_name'],feature_set=set_name,calibration=record['calibration'],selection=reason,**metrics(y,probabilities,value)))
    pd.DataFrame(threshold_rows).rename(columns={'f1':'F1'}).to_csv(OUT/'threshold_analysis.csv',index=False)
    selected_metrics=metrics(y,p,threshold)
    write_json(OUT/'final_validation_metrics.json',selected_metrics)
    write_json(OUT/'selection_decisions.json',dict(leading_AP_experiment=leader['experiment_id'],selected_experiment=selected['experiment_id'],best_by_feature_set={k:v['experiment_id'] for k,v in best.items()},leader_minus_core=difference_core,chosen_before_socio_policy_minus_no_socio=difference_socio,rule='Favor portable core if its AP difference is not resolved by exploratory paired group-bootstrap CI; otherwise avoid socioeconomic variables when their AP gain is unresolved. Calibration minimizes validation Brier among raw/sigmoid/isotonic versions of each AP-leading raw model. Final threshold maximizes validation F1, with recall/specificity/precision tradeoffs reported. This is a research operating point, not a clinical cutoff.',threshold_choices=choices))
    # Validation-only missingness robustness for the exported candidate.
    sensitivity=[];missing=validation[features].isna().any(axis=1).to_numpy()
    for label,mask in [('all_inputs_present',~missing),('at_least_one_missing',missing)]:
        sensitivity.append(dict(scenario=label,**metrics(y[mask],p[mask],threshold)))
    for field in ['income_group','high_cholesterol','bmi','smoking_status']:
        if field not in features:
            sensitivity.append(dict(scenario='mask_'+field,note='Not used by selected model; omission has no effect'));continue
        modified=validation[features].copy();modified[field]=np.nan
        changed=chosen.predict_proba(modified)[:,1]
        sensitivity.append(dict(scenario='mask_'+field,mean_absolute_probability_change=float(np.mean(np.abs(changed-p))),classification_flip_percentage=float(np.mean((changed>=threshold)!=(p>=threshold))*100),**metrics(y,changed,threshold)))
    pd.DataFrame(sensitivity).to_csv(OUT/'missingness_sensitivity.csv',index=False)
    pd.DataFrame(subgroup_rows(validation,p,threshold)).to_csv(OUT/'subgroup_metrics.csv',index=False)
    # Independent age/sex slices are descriptive, not fairness certification.
    importance=explain(selected,chosen,validation)
    # Coefficient associations for the unweighted full logistic baseline.
    logistic=next(r for r in success if r['model_name']=='logistic_none' and r['feature_set']=='full_features')
    linear=joblib.load(ROOT/logistic['model_path'])
    dictionary=pd.read_csv(ROOT/'data/processed/data_dictionary.csv',keep_default_na=False).set_index('clean_variable')
    coefficient_rows=[]
    for name,value in zip(linear.named_steps['preprocess'].get_feature_names_out(),linear.named_steps['classifier'].coef_[0]):
        feature=next((f for f in features+list(dictionary.index) if name==f'bmi__{f}' or name.startswith(f'categories__{f}_')),None)
        category=name.split(feature+'_',1)[1] if feature and feature!='bmi' else None
        label='per training BMI standard deviation' if feature=='bmi' else ''
        if category:
            mapping=json.loads(dictionary.loc[feature,'clean_mapping']);labels=json.loads(dictionary.loc[feature,'original_labels'])
            label=' / '.join(labels[k] for k,v in mapping.items() if isinstance(v,(int,float)) and float(v)==float(category))
        coefficient_rows.append(dict(transformed_feature=name,feature=feature,category_label=label,coefficient=float(value),notes='Regularized full one-hot associations, not causal effects or unadjusted odds ratios; all levels retained.'))
    pd.DataFrame(coefficient_rows).to_csv(OUT/'logistic_coefficients.csv',index=False)
    # Plot underlying validation curves; test curve is added only after freeze.
    fig,ax=plt.subplots(figsize=(7,6));roc_rows=[]
    for set_name,r in best.items():
        fpr,tpr,t=roc_curve(y,prediction(r));ax.plot(fpr,tpr,label=f'{set_name} (AUC {r["validation_metrics"]["roc_auc"]:.3f})')
        roc_rows.extend(dict(feature_set=set_name,FPR=a,TPR=b,threshold=c) for a,b,c in zip(fpr,tpr,t))
    ax.plot([0,1],[0,1],'k--',lw=1);ax.set(xlabel='False positive rate',ylabel='True positive rate',title='Validation ROC curves');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'roc_curve.png',dpi=170);plt.close(fig)
    pd.DataFrame(roc_rows).to_csv(OUT/'roc_curve_values.csv',index=False)
    fig,ax=plt.subplots(figsize=(7,6));pr_rows=[]
    for set_name,r in best.items():
        precision,recall,t=precision_recall_curve(y,prediction(r));ax.plot(recall,precision,label=f'{set_name} (AP {r["validation_metrics"]["pr_auc"]:.3f})')
        pr_rows.extend(dict(feature_set=set_name,precision=a,recall=b) for a,b in zip(precision,recall))
    ax.axhline(y.mean(),linestyle='--',color='gray',label=f'Prevalence {y.mean():.3f}');ax.set(xlabel='Recall',ylabel='Precision',title='Validation precision-recall curves',ylim=(0,1));ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'precision_recall_curve.png',dpi=170);plt.close(fig)
    pd.DataFrame(pr_rows).to_csv(OUT/'precision_recall_curve_values.csv',index=False)
    fig,ax=plt.subplots(figsize=(7,6));cal_rows=[]
    for row in calibration_choices:
        if row['feature_set']!=selected['feature_set']:continue
        r=next(r for r in records if r['experiment_id']==row['experiment_id']);fraction,mean=calibration_curve(y,prediction(r),n_bins=10,strategy='quantile')
        ax.plot(mean,fraction,'o-',label=f'{r["calibration"]}; Brier {row["brier"]:.5f}')
        cal_rows.extend(dict(method=r['calibration'],mean_probability=a,observed_fraction=b) for a,b in zip(mean,fraction))
    ax.plot([0,1],[0,1],'k--');ax.set(xlabel='Mean model score',ylabel='Observed reported CHD/MI fraction',title='Validation calibration (quantile bins)');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'calibration_curve.png',dpi=170);plt.close(fig)
    pd.DataFrame(cal_rows).to_csv(OUT/'calibration_curve_values.csv',index=False)
    schema=[]
    for feature in features:
        row=dictionary.loc[feature];mapping=json.loads(row.clean_mapping)
        domain=sorted({v for v in mapping.values() if isinstance(v,(int,float))}) if feature!='bmi' else None
        schema.append(dict(name=feature,feature_type=row.feature_type,required=False,missing_allowed=True,allowed_categories=domain,numeric_constraints={'minimum':12,'maximum':99.99,'units':'kg/m^2; human-readable, not multiplied by 100'} if feature=='bmi' else {'integer_only':True},description=row.description,source_variable=row.original_variable,ordinal_or_nominal=row.ordinal_or_nominal,unsupported_category_handling='Numeric unseen categorical codes become missing with a warning; not silently treated as valid CDC categories.'))
    write_json(ROOT/'models/feature_schema.json',dict(version='1.0.0',input_format='Nonempty dictionary or list of nonempty dictionaries using clean feature names; optional omitted fields become missing.',features=schema))
    joblib.dump(chosen,ROOT/'models/heart_disease_pipeline.joblib',compress=3)
    # Ensure exported artifact preserves the selected candidate's probabilities.
    reloaded=joblib.load(ROOT/'models/heart_disease_pipeline.joblib')
    np.testing.assert_allclose(reloaded.predict_proba(validation[features].iloc[:32]),chosen.predict_proba(validation[features].iloc[:32]),rtol=0,atol=0)
    start=time.perf_counter();reloaded.predict_proba(validation[features].iloc[:100]);inference_seconds=time.perf_counter()-start
    design=json.loads((OUT/'training_design.json').read_text())
    base=unwrap(chosen)
    underlying=base.named_steps['classifier']
    fit_device=selected.get('device_used','CPU')
    if hasattr(underlying,'device'):fit_device=underlying.device
    elif underlying.__class__.__module__.startswith('catboost'):fit_device=underlying.get_param('task_type') or 'CPU'
    actual_encoding=selected['preprocessing']
    processor=base.named_steps['preprocess']
    if hasattr(processor,'named_transformers_') and 'ordinal_comparison' in processor.named_transformers_:actual_encoding='Nominal one-hot; explicitly tested ordinal numeric representation'
    metadata=dict(model_name='BRFSS CHD/MI Profile Classifier',model_family=selected['model_family'],model_version='1.0.0',training_dataset='CDC BRFSS 2021; fixed original train.csv, partitioned into disjoint grouped model-fit and calibration-only subsets',target_definition='Existing self-reported coronary heart disease or myocardial infarction; not prospective future risk or clinical diagnosis.',feature_set=selected['feature_set'],feature_names=features,preprocessing=str(base.named_steps['preprocess']),imputation=selected['imputation'],encoding=selected['preprocessing'],hyperparameters=base.named_steps['classifier'].get_params(),class_balance_method=selected['class_weighting'],calibration_method=selected['calibration'],classification_threshold=threshold,threshold_rationale='Maximum validation F1; alternatives for 80%/90% recall, Youden J, and 0.50 reported explicitly.',device_used=selected.get('device_used','CPU'),inference_device='CPU-compatible inference; XGBoost exported prediction device CPU',training_runtime=selected['runtime_seconds'],validation_metrics=selected_metrics,test_metrics=None,random_seed=SEED,training_date=now(),software_versions=environment(),known_limitations=LIMITATIONS,model_fit_rows=design['model_fit_rows'],calibration_only_rows=design['calibration_only_rows'],selected_experiment=selected['experiment_id'],refit_on_train_plus_validation=False,inference_100_rows_seconds=inference_seconds)
    metadata.update(device_used=fit_device,calibration_device='CPU',encoding=actual_encoding)
    write_json(ROOT/'models/model_metadata.json',metadata);(ROOT/'models/model_version.txt').write_text('1.0.0\n')
    freeze=dict(timestamp=now(),test_predictions_accessed=False,model_specification=metadata,pipeline_sha256=sha(ROOT/'models/heart_disease_pipeline.joblib'),schema_sha256=sha(ROOT/'models/feature_schema.json'),code_hashes={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/models').glob('*.py')},selection_details=json.loads((OUT/'selection_decisions.json').read_text()))
    write_json(ROOT/'models/model_freeze.json',freeze);write_json(OUT/'frozen_model_specification.json',freeze)
    print(json.dumps(dict(selected_experiment=selected['experiment_id'],feature_set=selected['feature_set'],calibration=selected['calibration'],threshold=threshold,validation_metrics=selected_metrics,test_still_locked=True),indent=2),flush=True)

if __name__=='__main__':select_and_export()
