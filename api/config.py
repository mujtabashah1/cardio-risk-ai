import os,json,re
from dataclasses import dataclass,field
from pathlib import Path
from src.inference.constants import ROOT,MODEL_HASH

def env_path(name,relative):return Path(os.getenv(name,str(ROOT/relative))).resolve()
@dataclass(frozen=True)
class Settings:
    host:str=field(default_factory=lambda:os.getenv('API_HOST','127.0.0.1'))
    port:int=field(default_factory=lambda:int(os.getenv('API_PORT','8000')))
    cors_origins:tuple[str,...]=field(default_factory=lambda:tuple(json.loads(os.getenv('CORS_ORIGINS','[]'))))
    logging_level:str=field(default_factory=lambda:os.getenv('LOG_LEVEL','INFO').upper())
    max_batch_size:int=field(default_factory=lambda:int(os.getenv('MAX_BATCH_SIZE','1000')))
    max_body_bytes:int=field(default_factory=lambda:int(os.getenv('MAX_BODY_BYTES','1048576')))
    model_path:Path=field(default_factory=lambda:env_path('MODEL_PATH','models/heart_disease_pipeline.joblib'))
    metadata_path:Path=field(default_factory=lambda:env_path('METADATA_PATH','models/model_metadata.json'))
    schema_path:Path=field(default_factory=lambda:env_path('SCHEMA_PATH','models/feature_schema.json'))
    threshold_path:Path=field(default_factory=lambda:env_path('THRESHOLD_PROFILES_PATH','models/threshold_profiles.json'))
    expected_model_hash:str=field(default_factory=lambda:os.getenv('EXPECTED_MODEL_HASH',MODEL_HASH).lower())
    def __post_init__(self):
        if not 1<=self.port<=65535 or not 1<=self.max_batch_size<=1000 or self.max_body_bytes<256:raise ValueError('Invalid API capacity configuration')
        if self.logging_level not in ['DEBUG','INFO','WARNING','ERROR','CRITICAL']:raise ValueError('Invalid logging level')
        if not isinstance(self.cors_origins,tuple) or any(not isinstance(x,str) or x=='*' or not re.match(r'^https?://[^/]+$',x) for x in self.cors_origins):raise ValueError('CORS requires explicit HTTP(S) origins')
        if self.expected_model_hash!=MODEL_HASH:raise ValueError('Expected hash must match frozen model version 1.0.0')
