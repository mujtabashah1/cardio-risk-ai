"""Fail-closed, cached loading of the approved pickle and its supporting files."""
import hashlib,io,json,threading
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
import joblib,numpy as np,pandas as pd
from .constants import ROOT,MODEL_HASH,INTEGRITY_HASH,FEATURES
from .threshold_policy import verify_profiles,apply_threshold

class ModelInitializationError(RuntimeError):pass

@dataclass
class Artifacts:
    pipeline:object
    metadata:dict
    schema:dict
    policy:dict
    lock:object
    integrity_passed:bool=True

def sha(data):return hashlib.sha256(data).hexdigest()
_load_lock=threading.Lock()

@dataclass(frozen=True)
class ModelKey:
    model_path:Path
    metadata_path:Path
    schema_path:Path
    threshold_path:Path
    expected_model_hash:str

@lru_cache(maxsize=4)
def _load(settings):
    try:
        integrity_bytes=(ROOT/'reports/deployment/model_integrity.json').read_bytes()
        if sha(integrity_bytes)!=INTEGRITY_HASH:raise ValueError('Integrity manifest mismatch')
        manifest=json.loads(integrity_bytes)
        overrides={'models/heart_disease_pipeline.joblib':settings.model_path,'models/model_metadata.json':settings.metadata_path,'models/feature_schema.json':settings.schema_path,'models/threshold_profiles.json':settings.threshold_path}
        buffers={}
        for relative,expected in manifest['files_sha256'].items():
            data=overrides.get(relative,ROOT/relative).read_bytes()
            if sha(data)!=expected:raise ValueError('Supporting artifact mismatch')
            buffers[relative]=data
        data=buffers['models/heart_disease_pipeline.joblib']
        if sha(data)!=MODEL_HASH or sha(data)!=settings.expected_model_hash:raise ValueError('Frozen pipeline mismatch')
        metadata=json.loads(buffers['models/model_metadata.json']);schema=json.loads(buffers['models/feature_schema.json']);policy=json.loads(buffers['models/threshold_profiles.json'])
        if metadata['model_version']!='1.0.0' or tuple(metadata['feature_names'])!=FEATURES or tuple(f['name'] for f in schema['features'])!=FEATURES or metadata['calibration_method']!='none':raise ValueError('Model specification mismatch')
        if buffers['models/model_version.txt'].decode().strip()!='1.0.0':raise ValueError('Version mismatch')
        verify_profiles(policy,metadata)
        from .validation import DOMAINS
        for feature in schema['features']:
            if feature['name']!='bmi' and list(DOMAINS[feature['name']])!=feature['allowed_categories']:raise ValueError('Dictionary domain mismatch')
        pipeline=joblib.load(io.BytesIO(data))
        if tuple(pipeline.named_steps['guard'].features)!=FEATURES or list(pipeline.named_steps['classifier'].classes_)!=[0,1]:raise ValueError('Classifier specification mismatch')
        golden=json.loads(buffers['tests/fixtures/golden_predictions.json'])
        frame=pd.DataFrame([{f:r['input'].get(f,np.nan) for f in FEATURES} for r in golden],columns=FEATURES,dtype=float)
        scores=pipeline.predict_proba(frame)[:,1]
        for row,score in zip(golden,scores):
            if not np.isclose(score,row['expected_profile_score'],rtol=0,atol=row['absolute_tolerance']) or apply_threshold(score,metadata['classification_threshold'])!=row['expected_classification']:raise ValueError('Golden smoke test mismatch')
        return Artifacts(pipeline,metadata,schema,policy,threading.RLock())
    except Exception as exc:
        raise ModelInitializationError('Frozen model startup verification failed; service cannot start.') from exc

def load_artifacts(settings):
    # Serialize cache misses too: concurrent first requests cannot load duplicate models.
    key=ModelKey(settings.model_path,settings.metadata_path,settings.schema_path,settings.threshold_path,settings.expected_model_hash)
    with _load_lock:return _load(key)

def clear_cache():
    with _load_lock:_load.cache_clear()
