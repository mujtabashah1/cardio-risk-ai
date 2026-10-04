"""Single and transactional batch inference for named research operating points."""
import numpy as np,pandas as pd
from .constants import FEATURES,DEFAULT_PROFILE,MODEL_CONTEXT
from .model_loader import load_artifacts
from .validation import validate_profile
from .threshold_policy import apply_threshold

class InferenceError(RuntimeError):pass

class InferenceService:
    def __init__(self,settings):self.settings=settings;self.artifacts=load_artifacts(settings)
    @property
    def ready(self):return self.artifacts is not None and self.artifacts.integrity_passed
    def predict(self,profile,threshold_profile=DEFAULT_PROFILE):return self.predict_batch([profile],threshold_profile)[0]
    def predict_batch(self,profiles,threshold_profile=DEFAULT_PROFILE):
        if not isinstance(profiles,list) or not 1<=len(profiles)<=self.settings.max_batch_size:raise ValueError('Invalid batch size')
        if not isinstance(threshold_profile,str) or threshold_profile not in self.artifacts.policy['profiles']:raise ValueError('Unsupported threshold profile')
        # Validate every record before any prediction. Malformed values never become missing.
        validated=[validate_profile(p) for p in profiles]
        frame=pd.DataFrame(validated,columns=FEATURES,dtype=float)
        try:
            with self.artifacts.lock:scores=self.artifacts.pipeline.predict_proba(frame)[:,1]
            if len(scores)!=len(profiles) or not np.isfinite(scores).all() or not ((scores>=0)&(scores<=1)).all():raise ValueError('Invalid model output')
        except Exception as exc:raise InferenceError('Model inference failed.') from exc
        threshold=self.artifacts.policy['profiles'][threshold_profile]['threshold']
        return [dict(profile_score=float(score),classification=apply_threshold(score,threshold),threshold=threshold,threshold_profile=threshold_profile,model_version=self.artifacts.metadata['model_version'],model_name='BRFSS CHD/MI Profile Score',model_context=MODEL_CONTEXT) for score in scores]
