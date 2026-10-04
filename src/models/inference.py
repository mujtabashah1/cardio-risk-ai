"""Software inference for existing reported CHD/MI profiles, not future risk."""
import json,warnings
from functools import lru_cache
import joblib
import numpy as np
import pandas as pd
from .config import ROOT,FORBIDDEN

@lru_cache(maxsize=1)
def load_artifacts():
    pipeline=joblib.load(ROOT/'models/heart_disease_pipeline.joblib')
    metadata=json.loads((ROOT/'models/model_metadata.json').read_text())
    schema=json.loads((ROOT/'models/feature_schema.json').read_text())
    assert metadata['feature_names']==[r['name'] for r in schema['features']]
    return pipeline,metadata,schema

def predict_heart_disease_profile(input_data):
    pipeline,metadata,schema=load_artifacts()
    single=isinstance(input_data,dict)
    records=[input_data] if single else input_data
    if not isinstance(records,list) or not records or not all(isinstance(r,dict) and r for r in records):raise TypeError('Provide a nonempty record dictionary or list of record dictionaries')
    features=metadata['feature_names']
    for record in records:
        if FORBIDDEN.intersection(record):raise ValueError('Target and direct leakage fields cannot be inputs')
        extra=set(record)-set(features)
        if extra:raise ValueError(f'Unsupported feature names: {sorted(extra)}')
    frame=pd.DataFrame([{f:r.get(f,np.nan) for f in features} for r in records],columns=features)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',UserWarning)
        probability=pipeline.predict_proba(frame)[:,1]
    threshold=metadata['classification_threshold']
    if not np.isfinite(probability).all() or not ((probability>=0)&(probability<=1)).all():raise RuntimeError('Invalid probability returned by model')
    result=[dict(probability=float(p),classification=int(p>=threshold),threshold=threshold,model_version=metadata['model_version'],warnings=sorted(set(str(w.message) for w in caught))) for p in probability]
    return result[0] if single else result
