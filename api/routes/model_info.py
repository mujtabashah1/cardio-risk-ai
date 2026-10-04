from fastapi import APIRouter,Depends
from api.dependencies import inference_service
from src.inference.constants import MODEL_CONTEXT,DEFAULT_PROFILE,FEATURES
router=APIRouter()
@router.get('/model-info',tags=['model'])
def model_info(service=Depends(inference_service)):
    return dict(model_name='BRFSS CHD/MI Profile Score',model_family='catboost',model_version='1.0.0',feature_count=len(FEATURES),feature_names=list(FEATURES),target_description='Existing self-reported CHD/MI status',default_threshold_profile=DEFAULT_PROFILE,supported_threshold_profiles=list(service.artifacts.policy['profiles']),intended_use='Research profile classification',model_context=MODEL_CONTEXT,limitations_summary=['Independent-test recall 51.55% and precision 31.68% at the default threshold.','Subgroup performance varies; no subgroup-specific thresholds.','Cross-sectional self-report and fixed-split missingness shifts; external validation required.'])
