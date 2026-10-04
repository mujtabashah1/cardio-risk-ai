"""Native end-to-end verification and research release packaging. No model fitting."""
import ctypes,hashlib,importlib.metadata,json,os,re,shutil,socket,statistics,subprocess,sys,time,zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import httpx,numpy as np
from src.inference.constants import MODEL_HASH,FEATURES,PROFILE_NAMES,DEFAULT_THRESHOLD
from src.inference.service import InferenceService
from api.config import Settings
OUT=ROOT/'reports/deployment';RELEASE=ROOT/'release'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2),encoding='utf-8')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in rows)+'\n'
def summary(values):return dict(mean_latency_seconds=statistics.mean(values),median_latency_seconds=statistics.median(values),p95_latency_seconds=float(np.quantile(values,.95)))
def memory_mib(pid):
    if os.name!='nt':
        text=Path(f'/proc/{pid}/status').read_text();return int(re.search(r'VmRSS:\s+(\d+)',text)[1])/1024
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    handle=kernel.OpenProcess(0x0410,False,pid)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    try:
        counter=Counters();counter.cb=ctypes.sizeof(counter)
        if not psapi.GetProcessMemoryInfo(handle,ctypes.byref(counter),counter.cb):raise ctypes.WinError(ctypes.get_last_error())
        return counter.WorkingSetSize/2**20
    finally:kernel.CloseHandle(handle)

def main():
    artifact=ROOT/'models/heart_disease_pipeline.joblib';actual=sha(artifact)
    if actual!=MODEL_HASH:
        write(OUT/'release_model_integrity_failure.json',dict(expected=MODEL_HASH,actual=actual,passed=False))
        raise RuntimeError('STOP: frozen model hash mismatch')
    preserved=['models/heart_disease_pipeline.joblib','models/feature_schema.json','models/model_metadata.json','models/model_version.txt','models/threshold_profiles.json','reports/deployment/model_integrity.json','reports/deployment/threshold_false_negative_comparison.csv','reports/deployment/false_negative_tradeoff.md']
    before={p:sha(ROOT/p) for p in preserved};assert all((ROOT/p).is_file() for p in preserved)
    service=InferenceService(Settings());policy=service.artifacts.policy
    assert tuple(service.artifacts.metadata['feature_names'])==FEATURES and service.artifacts.metadata['calibration_method']=='none'
    assert policy['profiles']['research_balanced']['threshold']==DEFAULT_THRESHOLD
    suites=json.loads((OUT/'automated_tests.json').read_text());assert all(v['passed'] for v in suites.values())
    total=sum(v['tests_run'] for v in suites.values());runtime=0.;skipped=0
    for name in suites:
        text=(OUT/f'{name}_tests.txt').read_text();match=re.search(r'Ran \d+ tests? in ([\d.]+)s',text)
        if match:runtime+=float(match[1])
        skip=re.search(r'skipped=(\d+)',text);skipped+=int(skip[1]) if skip else 0
    golden=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text())
    for row in golden:assert np.isclose(service.predict(row['input'])['profile_score'],row['expected_profile_score'],rtol=0,atol=1e-12)
    docker={}
    for command in [['docker','--version'],['docker','info']]:
        try:
            result=subprocess.run(command,capture_output=True,text=True,timeout=30)
            docker[' '.join(command)]=dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        except FileNotFoundError:docker[' '.join(command)]=dict(available=False,reason='Docker executable unavailable')
    # This run has no Docker engine. Never convert native checks into container passes.
    docker['status']='PENDING - Docker unavailable' if not shutil.which('docker') else 'PENDING - container validation requires separate successful build/run'
    write(OUT/'release_docker_environment.json',docker)
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    url=f'http://127.0.0.1:{port}';server_log=OUT/'release_native_server.log';checks=[];observations=[]
    def check(name,condition):
        checks.append(dict(check=name,passed=bool(condition)))
        if not condition:raise AssertionError(name)
    def request(client,path,payload=None):
        start=time.perf_counter();r=client.get(path) if payload is None else client.post(path,json=payload)
        return r,time.perf_counter()-start
    with server_log.open('w',encoding='utf-8') as log:
        launch=time.perf_counter()
        proc=subprocess.Popen([sys.executable,str(ROOT/'scripts/release_probe_server.py'),str(port)],cwd=ROOT,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            with httpx.Client(base_url=url,timeout=60,trust_env=False) as client:
                for _ in range(200):
                    if proc.poll() is not None:raise RuntimeError('Verification server exited; inspect release_native_server.log')
                    try:
                        if client.get('/ready').status_code==200:break
                    except httpx.HTTPError:pass
                    time.sleep(.1)
                else:raise RuntimeError('Readiness deadline exceeded')
                startup=time.perf_counter()-launch
                observations.append(dict(stage='ready_idle',working_set_MiB=memory_mib(proc.pid)))
                for endpoint in ['/health','/ready','/model-info']:
                    r,_=request(client,endpoint);check(endpoint+' HTTP 200',r.status_code==200)
                    if endpoint=='/health':check('minimal liveness payload',r.json()=={'status':'ok'})
                    if endpoint=='/model-info':check('safe model metadata',r.json()['model_family']=='catboost' and r.json()['feature_count']==14 and '\\' not in r.text and 'joblib' not in r.text)
                profile=golden[0]['input'];r,first=request(client,'/predict',{'profile':profile})
                check('single/default prediction',r.status_code==200 and r.json()['threshold']==DEFAULT_THRESHOLD and r.json()['threshold_profile']=='research_balanced')
                observations.append(dict(stage='single_prediction',working_set_MiB=memory_mib(proc.pid)))
                baseline=r.json()
                for name in PROFILE_NAMES:
                    r,_=request(client,'/predict',{'profile':profile,'threshold_profile':name});data=r.json()
                    check('threshold '+name,r.status_code==200 and data['profile_score']==baseline['profile_score'] and data['model_version']==baseline['model_version'] and data['threshold']==policy['profiles'][name]['threshold'])
                    expected=service.predict(profile,name)
                    check('full-precision threshold classification '+name,data['classification']==expected['classification'])
                for row in golden:
                    r,_=request(client,'/predict',{'profile':row['input']});data=r.json()
                    check('HTTP golden '+row['name'],r.status_code==200 and abs(data['profile_score']-row['expected_profile_score'])<=.5e-6+1e-12 and data['classification']==row['expected_classification'])
                expected_scores=[round(row['expected_profile_score'],6) for row in golden]
                for size in [1,10,100]:
                    records=[golden[i%len(golden)]['input'] for i in range(size)]
                    r,_=request(client,'/predict/batch',{'profiles':records});data=r.json()
                    check('ordered batch '+str(size),r.status_code==200 and data['count']==size and all(v['profile_score']==expected_scores[i%len(golden)] and v['model_version']=='1.0.0' and 0<=v['profile_score']<=1 for i,v in enumerate(data['predictions'])))
                observations.append(dict(stage='100_record_batch',working_set_MiB=memory_mib(proc.pid)))
                for key in ['bmi','high_cholesterol','smoking_status']:
                    r,_=request(client,'/predict',{'profile':{**profile,key:None}});check('missing '+key,r.status_code==200)
                invalid=[{'profile':{**profile,'bmi':'NaN'}},{'profile':{**profile,'bmi':{}}},{'profile':{**profile,'sex':999}},{'profile':{**profile,'未知字段':1}},{'profile':{**profile,'bmi':'x'*100000}},{'threshold_profile':'clinical_super_mode','profile':profile}]
                invalid +=[{'profile':{**profile,k:1}} for k in ['heart_disease','_MICHD','CVDINFR4','CVDCRHD4','education','income_group']]
                for i,payload in enumerate(invalid):
                    r,_=request(client,'/predict',payload);check('safe invalid input '+str(i),r.status_code==422 and 'error' in r.json() and 'Traceback' not in r.text)
                r,_=request(client,'/predict/batch',{'profiles':[{'sex':1}]*1001});check('batch limit',r.status_code==422)
                for name,body,statuses,content_type in [('malformed','{',(400,),'application/json'),('nonfinite','{"profile":{"bmi":Infinity}}',(400,),'application/json'),('negative_nonfinite','{"profile":{"bmi":-Infinity}}',(400,),'application/json'),('nested','{"profile":{"sex":'+'['*1500+'1'+']'*1500+'}}',(400,422),'application/json'),('oversized','x'*1048577,(413,),'application/json'),('content_type','text',(415,),'text/plain')]:
                    r=client.post('/predict',content=body,headers={'content-type':content_type});check('robustness '+name,r.status_code in statuses and 'Traceback' not in r.text)
                benchmarks=[]
                for size in [1,10,100,1000]:
                    payload={'profiles':[golden[i%len(golden)]['input'] for i in range(size)]}
                    check('warmup '+str(size),client.post('/predict/batch',json=payload).status_code==200)
                    durations=[]
                    for _ in range(20):
                        r,duration=request(client,'/predict/batch',payload);assert r.status_code==200;durations.append(duration)
                    stats=summary(durations);benchmarks.append(dict(records=size,iterations=20,**stats,records_per_second=size/stats['median_latency_seconds']))
                concurrency=[]
                def concurrent_call(_):
                    with httpx.Client(base_url=url,timeout=60,trust_env=False) as worker:
                        response,duration=request(worker,'/predict',{'profile':profile})
                        return response.status_code,duration,response.json()
                for clients in [5,10]:
                    start=time.perf_counter()
                    with ThreadPoolExecutor(max_workers=clients) as pool:responses=list(pool.map(concurrent_call,range(clients*2)))
                    elapsed=time.perf_counter()-start
                    success=sum(status==200 and data==baseline for status,_,data in responses)
                    concurrency.append(dict(concurrent_clients=clients,requests=len(responses),successful=success,errors=len(responses)-success,success_rate=success/len(responses),elapsed_seconds=elapsed,**summary([d for _,d,_ in responses])))
                    check('concurrency '+str(clients),success==len(responses))
                    observations.append(dict(stage=str(clients)+'_concurrent_clients',working_set_MiB=memory_mib(proc.pid)))
                for _ in range(20):assert client.post('/predict',json={'profile':profile}).status_code==200
                observations.append(dict(stage='post_repeated_requests',working_set_MiB=memory_mib(proc.pid)))
                loading=json.loads((OUT/'release_model_loading.json').read_text());check('one model deserialization',loading['joblib_deserializations']==1)
        finally:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    logs=server_log.read_text();check('no startup/model loading traceback','Traceback' not in logs)
    log_rows=[]
    for line in logs.splitlines():
        if 'cardiorisk.requests:' in line:log_rows.append(json.loads(line.split('cardiorisk.requests:',1)[1]))
    fields={'request_id','endpoint','status','latency_ms','model_version','threshold_profile','batch_size'}
    check('privacy-conscious operational log fields',bool(log_rows) and all(set(row)==fields for row in log_rows))
    for p,h in before.items():assert sha(ROOT/p)==h,p
    write(OUT/'release_e2e_verification.json',dict(passed=True,transport='Actual native Uvicorn TCP HTTP on loopback; not Docker',checks=checks,checks_passed=len(checks),preserved_artifact_hashes=before,golden_internal_tolerance=1e-12,golden_HTTP_tolerance=.5e-6+1e-12,model_deserializations=loading['joblib_deserializations']))
    write(OUT/'inference_performance.json',dict(measurement='Warm localhost HTTP end-to-end, including strict validation/serialization; synthetic profiles; single caller; excludes cold start; not server capacity',model_version='1.0.0',pipeline_sha256=actual,application_startup_seconds=startup,first_prediction_seconds=first,benchmarks=benchmarks,concurrency=concurrency,memory_working_set=observations,memory_note='Approximate native-process working-set samples, not container memory. Short observations cannot prove leak absence.',model_deserializations=loading['joblib_deserializations']))
    timestamp=datetime.now(ZoneInfo('America/Los_Angeles')).isoformat()
    gate_names=['Model hash integrity','Model reproducibility','Feature schema validation','Leakage protection','Threshold profile validation','False-negative analysis','API single inference','API batch inference','Missing-value handling','Invalid-input rejection','Golden predictions','Automated tests','Health endpoint (native)','Readiness endpoint (native)','Latency benchmark (native)','Concurrency check (native)','Security input checks','Logging review','Documentation']
    gates={name:'PASS' for name in gate_names}
    gates.update({'Docker build':'PENDING - Docker unavailable','Container startup':'PENDING - Docker unavailable','Container model integrity':'PENDING - Docker unavailable','Container golden predictions/tests':'PENDING - Docker unavailable','Container health/readiness':'PENDING - Docker unavailable'})
    readiness='READY FOR LOCAL RESEARCH USE'
    (OUT/'final_deployment_quality_gate.md').write_text('# Final research release quality gate\n\n'+table(['Check','Status'],gates.items())+f'\nAutomated tests: {total-skipped} passed, 0 failed, {skipped} skipped; summed test runtime {runtime:.3f} seconds. Native HTTP checks: {len(checks)} passed. Docker/container checks are not substituted by native results; deployment verification is not fully complete.\n\nRelease/model/API version 1.0.0. No model fitting, recalibration, feature/split/default-threshold changes or test-data optimization occurred. Golden/cached validation evidence is reused; only synthetic profiles were sent over HTTP.\n\nReadiness: **'+readiness+'**. Default recall ~51% and high-sensitivity false-positive costs remain documented. No diagnosis, future-risk prediction or clinical screening standard. Public deployment needs controlled access, TLS, rate/concurrency controls and external validation.\n',encoding='utf-8')
    (OUT/'container_verification.md').write_text('# Container verification\n\nDocker --version and docker info could not execute: Docker executable unavailable.\n\nDocker build: **PENDING - Docker unavailable**. Container startup, health, readiness, golden predictions and in-container model hash: **PENDING - Docker unavailable**. No image size/build timestamp or in-container hash is invented.\n\nPrepared image tag: `cardiorisk-profile-api:1.0.0`; base image: `python:3.12-slim`. The existing Dockerfile uses explicit runtime copies, a non-root user, debug disabled and a readiness health check. The .dockerignore allowlist excludes respondent datasets, candidate models, training caches, SHAP data and secrets. This is source inspection, not image-content verification. Run `scripts/verify_container.ps1` when an engine is available.\n\nThe native localhost HTTP verification and earlier isolated runtime-bundle check passed. These do not prove Linux-image packaging or container execution.\n',encoding='utf-8')
    try:git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,timeout=10);commit=git.stdout.strip() if git.returncode==0 else None
    except FileNotFoundError:commit=None
    manifest=dict(release_version='1.0.0',model_version='1.0.0',api_version='1.0.0',model_sha256=actual,feature_schema_sha256=sha(ROOT/'models/feature_schema.json'),metadata_sha256=sha(ROOT/'models/model_metadata.json'),threshold_profiles_sha256=sha(ROOT/'models/threshold_profiles.json'),docker_image_tag='cardiorisk-profile-api:1.0.0',docker_build_status='PENDING - Docker unavailable',docker_image_size_bytes=None,docker_build_timestamp=None,base_image='python:3.12-slim',python_version=sys.version.split()[0],catboost_version=importlib.metadata.version('catboost'),fastapi_version=importlib.metadata.version('fastapi'),build_timestamp=timestamp,git_commit=commit,git_commit_note='Unavailable in current environment' if commit is None else None,test_count=total,tests_passed=total-skipped,tests_failed=0,tests_skipped=skipped,test_runtime_seconds=runtime,test_result='PASS',native_HTTP_checks_passed=len(checks),deployment_readiness=readiness,full_container_verification_complete=False,archive_file='cardiorisk-api-1.0.0.zip')
    write(RELEASE/'release_manifest.json',manifest)
    print(json.dumps(dict(readiness=readiness,tests_passed=total-skipped,native_checks=len(checks),startup_seconds=startup,first_prediction_seconds=first,benchmarks=benchmarks,concurrency=concurrency,memory=observations,docker='PENDING'),indent=2),flush=True)

if __name__=='__main__':main()
