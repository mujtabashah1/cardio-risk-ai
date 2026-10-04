"""Start with python -m api; lifespan verifies all artifacts before readiness."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from fastapi.exceptions import RequestValidationError
from api.config import Settings
from api.errors import error_response
from api.middleware.request_guard import RequestGuard
from api.routes import health,model_info,predict
from src.inference.service import InferenceService,InferenceError
from src.inference.model_loader import ModelInitializationError
from src.inference.constants import FEATURES
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path

def create_app(settings=None,service_factory=InferenceService):
    settings=settings or Settings()
    @asynccontextmanager
    async def lifespan(app):
        logging.basicConfig(level=settings.logging_level)
        try:app.state.service=service_factory(settings)
        except ModelInitializationError:
            logging.getLogger('cardiorisk.startup').critical('Frozen model verification failed; startup aborted.')
            raise ModelInitializationError('Model verification failed; startup aborted.') from None
        yield
        app.state.service=None
    app=FastAPI(title='BRFSS CHD/MI Profile Score API',version='1.0.0',description='Research classification of existing reported CHD/MI profiles; no diagnosis or future-risk endpoint.',lifespan=lifespan,debug=False)
    app.state.settings=settings;app.state.service=None
    app.add_middleware(RequestGuard,max_body_bytes=settings.max_body_bytes)
    if settings.cors_origins:app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_methods=['GET','POST'],allow_headers=['Content-Type'],expose_headers=['X-Request-ID'],allow_credentials=False)
    @app.exception_handler(RequestValidationError)
    async def invalid(request,exc):
        # Exclude submitted values, exception context, and arbitrary unknown field names.
        permitted={'body','profile','profiles','threshold_profile',*FEATURES}
        details=[{'location':[p if isinstance(p,int) or p in permitted else 'unknown_field' for p in e['loc']],'type':e['type'],'message':'Value does not match the request schema.'} for e in exc.errors()]
        return error_response(422,'INVALID_INPUT','Input validation failed.',details)
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request,exc):
        if exc.status_code==503:return error_response(503,'MODEL_NOT_READY','Model is not ready.')
        if exc.status_code==422:return error_response(422,'INVALID_INPUT','Batch exceeds configured limit.',[{'location':['body','profiles'],'type':'batch_limit','message':'Reduce batch size.'}])
        return error_response(exc.status_code,'HTTP_ERROR','Request could not be processed.')
    @app.exception_handler(InferenceError)
    async def inference_error(request,exc):return error_response(500,'INFERENCE_ERROR','Model inference failed.')
    for router in [health.router,model_info.router,predict.router]:app.include_router(router)
    frontend=Path(__file__).resolve().parents[1]/'frontend'
    if frontend.is_dir():app.mount('/testing',StaticFiles(directory=frontend,html=True),name='testing')
    return app
app=create_app()
