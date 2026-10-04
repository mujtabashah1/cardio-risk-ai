"""Stage 1/2 training and calibration. Test predictors never loaded here."""
import json,time,logging,traceback,copy
from datetime import datetime
from zoneinfo import ZoneInfo
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import train_test_split,StratifiedGroupKFold,RandomizedSearchCV
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from threadpoolctl import threadpool_limits
from .config import ROOT,FEATURE_SETS,SEED,THREADS,TARGET,FORBIDDEN
from .preflight import verify,sha
from .preprocessing import make_pipeline
from .estimators import candidates,family,search_space
from .metrics import metrics
from .hardware import detect,configure,GPUMonitor

OUT=ROOT/'reports/modeling'
CACHE=ROOT/'models/candidates'

def now():return datetime.now(ZoneInfo('America/Los_Angeles')).isoformat()
def write_json(path,obj):path.write_text(json.dumps(obj,indent=2,default=str))

def training_partition(train):
    membership=pd.read_csv(ROOT/'data/processed/split_membership.csv')
    groups=membership.loc[membership.split=='train','equality_group'].to_numpy()
    meta=pd.DataFrame({'group':groups,'target':train[TARGET]}).drop_duplicates('group')
    fit_groups,cal_groups=train_test_split(meta.group,test_size=.2,stratify=meta.target,random_state=SEED)
    fit=np.flatnonzero(np.isin(groups,fit_groups));cal=np.flatnonzero(np.isin(groups,cal_groups))
    assert not set(groups[fit])&set(groups[cal])
    membership_training=pd.DataFrame({'source_row_id':membership.loc[membership.split=='train','source_row_id'].to_numpy(),'equality_group':groups,'training_role':np.where(np.isin(groups,cal_groups),'calibration_only','model_fit')})
    membership_training.to_csv(OUT/'training_partition.csv',index=False)
    return fit,cal,groups

def run():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(OUT/'training.log',mode='a',encoding='utf-8')])
    if (ROOT/'models/model_freeze.json').exists():raise RuntimeError('Model already frozen. Preserve the completed run; no retuning after test access.')
    if (OUT/'data_preflight.json').exists():
        preflight=json.loads((OUT/'data_preflight.json').read_text())
        assert preflight['passed']
        for p,h in preflight['input_hashes'].items():assert sha(ROOT/p)==h,f'Input changed: {p}'
    else:preflight=verify()
    train=pd.read_csv(ROOT/'data/processed/train.csv');validation=pd.read_csv(ROOT/'data/processed/validation.csv')
    fit_idx,cal_idx,groups=training_partition(train)
    fit=train.iloc[fit_idx];cal=train.iloc[cal_idx]
    ratio=float(fit[TARGET].eq(0).sum()/fit[TARGET].eq(1).sum())
    hardware=json.loads((OUT/'hardware_environment.json').read_text()) if (OUT/'hardware_environment.json').exists() else detect()
    write_json(OUT/'training_design.json',dict(seed=SEED,threads=THREADS,model_fit_rows=len(fit),calibration_only_rows=len(cal),fit_positive=int(fit[TARGET].sum()),calibration_positive=int(cal[TARGET].sum()),training_only_scale_pos_weight=ratio,calibration_source='Reserved random, class-stratified labeled-record groups within original train.csv; not validation or test',tuning='Top two distinct model families: CatBoost 18 configurations and XGBoost 20 configurations with 3-fold StratifiedGroupKFold; logistic comparator 5 C values with 5 grouped folds. Uses 60000 stratified model-fit rows, independently fitted preprocessing within each fold, and full model-fit partition refits.',test_locked=True))
    records=json.loads((OUT/'experiment_records.json').read_text()) if (OUT/'experiment_records.json').exists() else []

    def checkpoint():
        write_json(OUT/'experiment_records.json',records)
        pd.DataFrame([{**r,'hyperparameters':json.dumps(r.get('hyperparameters',{}),default=str),'validation_metrics':json.dumps(r.get('validation_metrics',{}))} for r in records]).to_csv(OUT/'experiment_log.csv',index=False)
        successful=[r for r in records if r['status']=='success']
        comparison=[]
        for r in successful:
            comparison.append(dict(experiment_id=r['experiment_id'],model_name=r['model_name'],model_family=r['model_family'],feature_set=r['feature_set'],class_balance_method=r['class_weighting'],imputation_strategy=r['imputation'],encoding_strategy=r['preprocessing'],calibration=r['calibration'],runtime_seconds=r['runtime_seconds'],**{'validation_'+k:v for k,v in r['validation_metrics'].items()}))
        pd.DataFrame(comparison).to_csv(OUT/'model_comparison.csv',index=False)

    def experiment(name,set_name,estimator,scaled=False,native=False,weight='none',missing='most_frequent',ordinal=False,stage='baseline',prefit=None,calibration='none',requested='auto'):
        identifier=f'{stage}__{name}__{set_name}__{missing}__{"ordinal" if ordinal else "default"}__{calibration}'+('__cpu' if requested=='cpu' else '')
        old=next((r for r in records if r['experiment_id']==identifier),None)
        if old:return old
        features=FEATURE_SETS[set_name]
        assert not FORBIDDEN.intersection(features)
        configured,device=configure(clone(estimator),family(name),hardware,requested)
        base=make_pipeline(features,configured,scaled=scaled,missing=missing,ordinal=ordinal,native=native,dense=not scaled) if prefit is None else prefit
        record=dict(experiment_id=identifier,timestamp=now(),model_name=name,model_family=family(name),feature_set=set_name,number_of_features=len(features),preprocessing='native categorical strings' if native else 'nominal one-hot; ordinals '+('explicit numeric comparison' if ordinal else 'one-hot'),imputation='BMI training median; categorical '+('explicit Missing' if native or missing=='explicit_missing' else 'training most frequent'),class_weighting=weight,hyperparameters=base.get_params(deep=False) if prefit is not None else estimator.get_params(),threshold=.5,calibration=calibration,random_seed=SEED,stage=stage)
        support=hardware['GPU_support'].get(family(name),{})
        record.update(device_requested=requested,device_used=device,gpu_name=hardware['GPU_model'],cuda_available=hardware['CUDA_available'],fallback_occurred=(requested=='auto' and family(name) in hardware['GPU_support'] and not support.get('supported',False)),fallback_reason=support.get('error') if requested=='auto' and not support.get('supported',False) else None,CV_folds=0,categorical_strategy=record['preprocessing'],imputation_strategy=record['imputation'])
        start=time.perf_counter();logging.info('START %s (%s)',identifier,device)
        try:
            with threadpool_limits(limits=THREADS):
                if prefit is None:
                    prep_start=time.perf_counter()
                    guarded=base.named_steps['guard'].fit_transform(fit[features],fit[TARGET])
                    matrix=base.named_steps['preprocess'].fit_transform(guarded,fit[TARGET])
                    record['preprocessing_fit_seconds']=time.perf_counter()-prep_start
                    model_start=time.perf_counter()
                    try:
                        if device=='GPU':
                            with GPUMonitor() as monitor:base.named_steps['classifier'].fit(matrix,fit[TARGET])
                            record['peak_GPU_total_used_MiB']=monitor.peak
                        else:base.named_steps['classifier'].fit(matrix,fit[TARGET])
                    except Exception as gpu_error:
                        if device!='GPU':raise
                        logging.exception('GPU fit failed; retrying same estimator on CPU')
                        cpu,_=configure(clone(configured),family(name),hardware,'cpu')
                        base.set_params(classifier=cpu);base.named_steps['classifier'].fit(matrix,fit[TARGET])
                        record.update(device_used='CPU',fallback_occurred=True,fallback_reason=repr(gpu_error))
                    record['model_fit_seconds']=time.perf_counter()-model_start
                    if family(name)=='xgboost':base.named_steps['classifier'].set_params(device='cpu')
                elif calibration!='none':
                    calibration_start=time.perf_counter()
                    base=CalibratedClassifierCV(FrozenEstimator(prefit),method=calibration,n_jobs=1)
                    base.fit(cal[features],cal[TARGET])
                    record.update(calibration_fit_seconds=time.perf_counter()-calibration_start,calibration_device='CPU')
                p=base.predict_proba(validation[features])[:,1]
            record.update(status='success',validation_metrics=metrics(validation[TARGET],p),model_path=str((CACHE/f'{identifier}.joblib').relative_to(ROOT)),runtime_seconds=time.perf_counter()-start)
            joblib.dump(base,ROOT/record['model_path'],compress=3)
            np.savez_compressed(CACHE/f'{identifier}_validation.npz',probability=p)
            logging.info('DONE %s: AP %.5f ROC %.5f Brier %.5f in %.1fs',identifier,record['validation_metrics']['pr_auc'],record['validation_metrics']['roc_auc'],record['validation_metrics']['brier'],record['runtime_seconds'])
        except Exception as e:
            record.update(status='failed',error=repr(e),traceback=traceback.format_exc(),runtime_seconds=time.perf_counter()-start)
            logging.exception('FAILED %s',identifier)
        records.append(record);checkpoint();return record

    for set_name in FEATURE_SETS:
        for name,est,scaled,native,weight in candidates(ratio):
            gpu_family=family(name) in ['xgboost','catboost']
            experiment(name,set_name,est,scaled,native,weight,stage='gpu_baseline' if gpu_family else 'baseline')
    for name,est,scaled,native,weight in candidates(ratio):
        if name in ['xgboost_none','catboost_native']:
            for requested in ['cpu','auto']:experiment(name,'full_features',est,scaled,native,weight,stage='benchmark',requested=requested)
    baseline=[r for r in records if r['status']=='success' and r['stage'] in ['baseline','gpu_baseline'] and r['model_family']!='dummy' and r['feature_set'] in FEATURE_SETS]
    if not baseline:raise RuntimeError('All real baselines failed')
    ranked=sorted(baseline,key=lambda r:r['validation_metrics']['pr_auc'],reverse=True)
    strongest=[]
    for r in ranked:
        if r['model_family'] not in [x['model_family'] for x in strongest]:strongest.append(r)
        if len(strongest)==2:break
    if not any(r['model_family']=='logistic' for r in strongest):strongest.append(max([r for r in baseline if r['model_family']=='logistic'],key=lambda r:r['validation_metrics']['pr_auc']))
    sample_idx,_=train_test_split(np.arange(len(fit)),train_size=min(60000,len(fit)-1),stratify=fit[TARGET],random_state=SEED)
    sample=fit.iloc[sample_idx];sample_groups=groups[fit_idx][sample_idx]
    for r in strongest:
        tuned_path=CACHE/f'tuned_template__{r["model_family"]}.joblib'
        if tuned_path.exists():template=joblib.load(tuned_path)
        else:
            base=joblib.load(ROOT/r['model_path'])
            features=FEATURE_SETS[r['feature_set']]
            tune_base=clone(base)
            configured,_=configure(tune_base.named_steps['classifier'],r['model_family'],hardware)
            tune_base.set_params(classifier=configured)
            folds=5 if r['model_family']=='logistic' else 3
            trials=5 if r['model_family']=='logistic' else 18 if r['model_family']=='catboost' else 20
            cv=StratifiedGroupKFold(n_splits=folds,shuffle=True,random_state=SEED)
            search=RandomizedSearchCV(tune_base,search_space(r['model_name']),n_iter=trials,scoring='average_precision',cv=cv,n_jobs=1,refit=False,random_state=SEED,error_score='raise',verbose=1)
            logging.info('TUNING %s using training-only grouped CV',r['model_family'])
            start=time.perf_counter()
            try:
                with threadpool_limits(limits=THREADS):search.fit(sample[features],sample[TARGET],groups=sample_groups)
                pd.DataFrame(search.cv_results_).to_csv(OUT/f'tuning_{r["model_family"]}.csv',index=False)
                template=clone(tune_base).set_params(**search.best_params_)
                joblib.dump(template,tuned_path)
                write_json(OUT/f'tuning_{r["model_family"]}.json',dict(best_parameters=search.best_params_,training_cv_average_precision=search.best_score_,runtime_seconds=time.perf_counter()-start,rows=len(sample),folds=folds,configurations=trials,device_requested='auto',CV='StratifiedGroupKFold on fixed training model-fit portion only; sample and grouped folds seed 42',reason='3 folds for boosted search limits sequential GPU runtime and memory; inexpensive logistic uses 5. Bounded CatBoost space contains 18 combinations; other boosted search uses 20.'))
            except Exception as e:
                logging.exception('Tuning failed; retain baseline')
                records.append(dict(experiment_id='tuning_failed_'+r['model_family'],timestamp=now(),model_name=r['model_name'],model_family=r['model_family'],feature_set=r['feature_set'],stage='tuning',status='failed',error=repr(e),hyperparameters={},validation_metrics={},runtime_seconds=time.perf_counter()-start));checkpoint();continue
        for set_name in FEATURE_SETS:
            experiment(r['model_name']+'_tuned',set_name,template.named_steps['classifier'],scaled=r['model_family']=='logistic',native='native categorical' in r['preprocessing'],weight=r['class_weighting'],stage='tuned')
    contenders=[r for r in records if r['status']=='success' and r['model_family']!='dummy' and r['calibration']=='none' and r['feature_set'] in FEATURE_SETS]
    best=max(contenders,key=lambda r:r['validation_metrics']['pr_auc'])
    fitted=joblib.load(ROOT/best['model_path']);estimator=fitted.named_steps['classifier']
    if hasattr(estimator,'weighted'):
        from catboost import CatBoostClassifier
        estimator=CatBoostClassifier(iterations=estimator.iterations,depth=estimator.depth,learning_rate=estimator.learning_rate,auto_class_weights='Balanced' if estimator.weighted else None,random_seed=SEED,thread_count=THREADS,verbose=False,allow_writing_files=False)
    for missing,ordinal in [('explicit_missing',False),('most_frequent',True)]:
        experiment(best['model_name']+'_representation',best['feature_set'],estimator,scaled=best['model_family']=='logistic',native=False,weight=best['class_weighting'],missing=missing,ordinal=ordinal,stage='representation')
    contenders=[r for r in records if r['status']=='success' and r['model_family']!='dummy' and r['calibration']=='none' and r['feature_set'] in FEATURE_SETS]
    # Calibrate the strongest candidate of each feature configuration.
    for set_name in FEATURE_SETS:
        r=max([x for x in contenders if x['feature_set']==set_name],key=lambda x:x['validation_metrics']['pr_auc'])
        fitted=joblib.load(ROOT/r['model_path'])
        for method in ['sigmoid','isotonic']:
            experiment(r['model_name'],set_name,fitted.named_steps['classifier'],weight=r['class_weighting'],native='native' in r['preprocessing'],missing='explicit_missing' if 'explicit' in r['imputation'] else 'most_frequent',stage='calibrated',prefit=fitted,calibration=method)
    checkpoint()
    for p,h in preflight['input_hashes'].items():assert sha(ROOT/p)==h,f'Input altered during modeling: {p}'
    write_json(OUT/'training_complete.json',dict(timestamp=now(),experiments=len(records),successful=sum(r['status']=='success' for r in records),failed=sum(r['status']=='failed' for r in records),inputs_unchanged=True,test_predictions_accessed=False))
    logging.info('Training/validation stage complete. Test remains locked.')

if __name__=='__main__':run()
