import hashlib,json,platform,importlib.metadata
import pandas as pd
import numpy as np
from .config import ROOT,EXPECTED,TARGET,FORBIDDEN,FEATURE_SETS
from src.data.mappings import VARIABLES,FEATURE_NAMES,VARIABLE_MAPPINGS

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def environment():
    versions={}
    for name in ['pandas','numpy','scikit-learn','xgboost','lightgbm','catboost','shap','joblib','matplotlib','scipy','pyarrow','threadpoolctl','optuna']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]='not installed'
    result=dict(Python=platform.python_version(),platform=platform.platform(),libraries=versions)
    hardware_path=ROOT/'reports/modeling/hardware_environment.json'
    if hardware_path.exists():result['hardware']=json.loads(hardware_path.read_text())
    return result

def verify():
    out=ROOT/'reports/modeling';out.mkdir(parents=True,exist_ok=True)
    discrepancies=[];report={};d=pd.read_csv(ROOT/'data/processed/data_dictionary.csv',keep_default_na=False)
    expected_columns=FEATURE_NAMES+[TARGET]
    if len(d)!=17 or d.clean_variable.tolist()!=expected_columns:discrepancies.append('Dictionary schema differs')
    for original,s in VARIABLES.items():
        row=d[d.original_variable==original]
        if len(row)!=1 or row.iloc[0].clean_variable!=s['name']:discrepancies.append(f'Dictionary/source mismatch: {original}');continue
        if original!='_BMI5':
            m=json.loads(row.iloc[0].clean_mapping);m.pop('BLANK',None)
            if {int(k):v for k,v in m.items()}!=VARIABLE_MAPPINGS[original]:discrepancies.append(f'Mapping mismatch: {original}')
        elif row.iloc[0].feature_type!='continuous numeric':discrepancies.append('BMI not continuous')
    for name,(rows,negative,positive) in EXPECTED.items():
        df=pd.read_csv(ROOT/f'data/processed/{name}.csv',float_precision='round_trip')
        counts=df[TARGET].value_counts().to_dict() if TARGET in df else {}
        if df.shape!=(rows,17) or counts!={0:negative,1:positive}:discrepancies.append(f'{name}: shape {df.shape}, counts {counts}; expected {(rows,17)}, {negative}/{positive}')
        if list(df)!=expected_columns:discrepancies.append(f'{name}: unexpected schema')
        if TARGET not in df or df[TARGET].isna().any():discrepancies.append(f'{name}: target missing')
        for original,s in VARIABLES.items():
            if s['name'] not in df:continue
            v=df[s['name']].dropna()
            if original=='_BMI5':
                if not v.between(12,99.99).all():discrepancies.append(f'{name}: BMI range/scale mismatch')
            elif not v.isin([x for x in s['mapping'].values() if x is not None]).all():discrepancies.append(f'{name}: invalid {s["name"]}')
        report[name]={'shape':list(df.shape),'negative':counts.get(0),'positive':counts.get(1),'positive_prevalence':float(df[TARGET].mean()),'dtypes':{c:str(t) for c,t in df.dtypes.items()},'missing_percent':(df.isna().mean()*100).to_dict()}
        if name=='heart_disease_clean':
            parquet=pd.read_parquet(ROOT/'data/processed/heart_disease_clean.parquet')
            if list(parquet)!=list(df) or not np.allclose(df.to_numpy(dtype=float),parquet.to_numpy(dtype=float,na_value=np.nan),rtol=0,atol=0,equal_nan=True):discrepancies.append('CSV/Parquet mismatch')
    membership=pd.read_csv(ROOT/'data/processed/split_membership.csv')
    if membership.source_row_id.duplicated().any():discrepancies.append('Source rows overlap splits')
    if (membership.groupby('equality_group').split.nunique()>1).any():discrepancies.append('Labeled duplicates overlap splits')
    ids=pd.read_csv(ROOT/'data/processed/clean_row_ids.csv').source_row_id
    if set(ids)!=set(membership.source_row_id):discrepancies.append('Split membership does not reconcile')
    master=pd.read_csv(ROOT/'data/processed/heart_disease_clean.csv',float_precision='round_trip');master.index=ids
    for name in ['train','validation','test']:
        split=pd.read_csv(ROOT/f'data/processed/{name}.csv',float_precision='round_trip')
        wanted=master.loc[membership.loc[membership.split==name,'source_row_id']]
        if not np.allclose(split.to_numpy(dtype=float),wanted.to_numpy(dtype=float),equal_nan=True,rtol=0,atol=0):discrepancies.append(f'{name}: rows differ from fixed membership')
    for name,features in FEATURE_SETS.items():
        if FORBIDDEN.intersection(features):discrepancies.append(f'{name}: leakage field')
    raw_summary=pd.read_csv(ROOT/'reports/data_profile/dataset_summary.csv').iloc[0]
    if int(raw_summary.rows)!=438693:discrepancies.append('Raw profile rows differ')
    paths=list((ROOT/'data/processed').glob('*'))+[ROOT/'src/data/mappings.py',ROOT/'src/data/clean_data.py']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
    report.update(passed=not discrepancies,discrepancies=discrepancies,predictors=FEATURE_NAMES,target=TARGET,no_leakage_fields=True,dictionary_consistent=not discrepancies,raw_profile_rows=int(raw_summary.rows),input_hashes=hashes,test_use='Required schema/count/integrity checks only; no test predictions or selection')
    (out/'data_preflight.json').write_text(json.dumps(report,indent=2))
    (out/'environment.json').write_text(json.dumps(environment(),indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='input_hashes'},indent=2),flush=True)
    if discrepancies:
        (out/'data_discrepancy_report.md').write_text('# STOP: data discrepancies\n\n'+'\n'.join('- '+x for x in discrepancies))
        raise RuntimeError('Processed data validation failed; no training performed.')
    return report

if __name__=='__main__':verify()
