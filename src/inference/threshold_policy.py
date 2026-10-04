import math
from .constants import PROFILE_NAMES,DEFAULT_PROFILE,DEFAULT_THRESHOLD

def verify_profiles(policy,metadata):
    if policy['model_version']!='1.0.0' or policy['default_profile']!=DEFAULT_PROFILE:raise ValueError('Invalid threshold policy version/default')
    if set(policy['profiles'])!=set(PROFILE_NAMES):raise ValueError('Unexpected threshold profiles')
    for profile in policy['profiles'].values():
        value=profile['threshold']
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1:raise ValueError('Invalid threshold')
    if policy['profiles'][DEFAULT_PROFILE]['threshold']!=DEFAULT_THRESHOLD or metadata['classification_threshold']!=DEFAULT_THRESHOLD:raise ValueError('Frozen threshold mismatch')

def apply_threshold(score,threshold):return 'elevated_model_association' if score>=threshold else 'lower_model_association'
