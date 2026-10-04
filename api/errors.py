from starlette.responses import JSONResponse
def error_response(status,code,message,details=None):
    return JSONResponse(status_code=status,content={'error':{'code':code,'message':message,'details':details or []}})
