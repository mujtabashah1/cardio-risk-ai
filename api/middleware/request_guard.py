import json,logging,time,uuid
from api.errors import error_response
from src.inference.constants import PROFILE_NAMES

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate JSON keys')
        result[key]=value
    return result
def reject_constant(value):raise ValueError('Non-finite JSON numbers')

class RequestGuard:
    def __init__(self,app,max_body_bytes):self.app=app;self.max_body_bytes=max_body_bytes
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        started=time.perf_counter();request_id=str(uuid.uuid4());status=500;profile=None;batch_size=None;response_started=False
        async def tracked_send(message):
            nonlocal status,response_started
            if message['type']=='http.response.start':
                response_started=True;status=message['status']
                message={**message,'headers':[ *message.get('headers',[]),(b'x-request-id',request_id.encode())]}
            await send(message)
        async def reject(status,code,message):return await error_response(status,code,message)(scope,receive,tracked_send)
        try:
            lengths=[v for k,v in scope.get('headers',[]) if k.lower()==b'content-length']
            if len(lengths)>1:return await reject(400,'INVALID_REQUEST','Conflicting content length.')
            if lengths:
                try:declared=int(lengths[0]);assert declared>=0
                except (ValueError,AssertionError):return await reject(400,'INVALID_REQUEST','Invalid content length.')
                if declared>self.max_body_bytes:return await reject(413,'REQUEST_TOO_LARGE','Request body exceeds configured limit.')
            body=bytearray()
            while True:
                message=await receive()
                if message['type']=='http.disconnect':return
                body.extend(message.get('body',b''))
                if len(body)>self.max_body_bytes:return await reject(413,'REQUEST_TOO_LARGE','Request body exceeds configured limit.')
                if not message.get('more_body',False):break
            if scope['method']=='POST' and scope['path'] in ['/predict','/predict/batch']:
                content_type=dict(scope.get('headers',[])).get(b'content-type',b'').decode('latin1').split(';')[0].lower()
                if content_type!='application/json' and not content_type.endswith('+json'):return await reject(415,'UNSUPPORTED_MEDIA_TYPE','Send application/json.')
                try:payload=json.loads(body,object_pairs_hook=unique_object,parse_constant=reject_constant)
                except (ValueError,UnicodeError,RecursionError):return await reject(400,'INVALID_JSON','Malformed JSON, duplicate keys, or non-finite JSON numbers.')
                if isinstance(payload,dict):
                    selected=payload.get('threshold_profile','research_balanced')
                    profile=selected if isinstance(selected,str) and selected in PROFILE_NAMES else 'invalid'
                    batch_size=len(payload['profiles']) if isinstance(payload.get('profiles'),list) else 1 if 'profile' in payload else None
            delivered=False
            async def replay():
                nonlocal delivered
                if not delivered:delivered=True;return {'type':'http.request','body':bytes(body),'more_body':False}
                return await receive()
            await self.app(scope,replay,tracked_send)
        except Exception:
            if response_started:raise
            await reject(500,'INTERNAL_ERROR','The request could not be completed.')
        finally:
            route=scope.get('route');endpoint=getattr(route,'path',None)
            if endpoint is None:endpoint=scope['path'] if scope['path'] in ['/health','/ready','/model-info','/predict','/predict/batch','/docs','/openapi.json'] else 'unmatched'
            logging.getLogger('cardiorisk.requests').info(json.dumps(dict(request_id=request_id,endpoint=endpoint,status=status,latency_ms=round((time.perf_counter()-started)*1000,3),model_version='1.0.0',threshold_profile=profile,batch_size=batch_size)))
