from fastapi import APIRouter,Depends,HTTPException
from api.dependencies import inference_service
from api.schemas import PredictionRequest,PredictionResponse,BatchRequest,BatchResponse
router=APIRouter()
@router.post('/predict',response_model=PredictionResponse,tags=['prediction'])
def predict(body:PredictionRequest,service=Depends(inference_service)):
    return service.predict(body.profile.model_dump(),body.threshold_profile)
@router.post('/predict/batch',response_model=BatchResponse,tags=['prediction'])
def batch(body:BatchRequest,service=Depends(inference_service)):
    if len(body.profiles)>service.settings.max_batch_size:raise HTTPException(422,detail='BATCH_LIMIT')
    result=service.predict_batch([p.model_dump() for p in body.profiles],body.threshold_profile)
    return {'predictions':result,'count':len(result)}
