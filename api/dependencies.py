from fastapi import Request,HTTPException
def inference_service(request:Request):
    service=getattr(request.app.state,'service',None)
    if service is None or not service.ready:raise HTTPException(503,detail='MODEL_NOT_READY')
    return service
