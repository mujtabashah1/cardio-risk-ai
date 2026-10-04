"""Private native verification server; instrumentation is never exposed via HTTP."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import joblib,uvicorn
counter=ROOT/'reports/deployment/release_model_loading.json'
original=joblib.load;loads=0
def tracked_load(*args,**kwargs):
    global loads
    start=time.perf_counter();result=original(*args,**kwargs);loads+=1
    counter.write_text(json.dumps({'joblib_deserializations':loads,'last_deserialization_seconds':time.perf_counter()-start}),encoding='utf-8')
    return result
joblib.load=tracked_load
from api.main import create_app
from api.config import Settings
from dataclasses import replace
settings=replace(Settings(),port=int(sys.argv[1]))
uvicorn.run(create_app(settings),host='127.0.0.1',port=settings.port,access_log=False,proxy_headers=False,log_level='warning')
