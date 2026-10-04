from fastapi import APIRouter,Depends
from api.dependencies import inference_service
router=APIRouter()
@router.get('/health',tags=['health'])
def health():return {'status':'ok'}
@router.get('/ready',tags=['health'])
def ready(service=Depends(inference_service)):return {'status':'ready','model_version':'1.0.0'}
