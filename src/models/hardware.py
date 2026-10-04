"""Small sequential GPU capability tests; no BRFSS/test data used."""
import ctypes,json,os,platform,re,subprocess,time,warnings,threading
from pathlib import Path
import numpy as np
from .config import ROOT,THREADS,SEED

def command(args):
    try:
        r=subprocess.run(args,capture_output=True,text=True,timeout=20,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        return r.stdout.strip() if r.returncode==0 else r.stderr.strip()
    except Exception as e:return repr(e)

class GPUMonitor:
    def __enter__(self):
        self.peak=None;self.stop=threading.Event()
        def poll():
            while not self.stop.is_set():
                s=command(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'])
                try:self.peak=max(self.peak or 0,int(s.splitlines()[0]))
                except (ValueError,IndexError):pass
                self.stop.wait(1)
        self.thread=threading.Thread(target=poll,daemon=True);self.thread.start();return self
    def __exit__(self,*args):self.stop.set();self.thread.join(timeout=2)

def detect():
    from xgboost import XGBClassifier,build_info
    from catboost import CatBoostClassifier
    from lightgbm import LGBMClassifier
    report={'CPU_model':platform.processor(),'logical_CPU_count':os.cpu_count(),'Python':platform.python_version()}
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:report['CPU_model']=winreg.QueryValueEx(key,'ProcessorNameString')[0]
    except Exception as e:report['CPU_detection_note']=repr(e)
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('page_total',ctypes.c_ulonglong),('page_available',ctypes.c_ulonglong),('virtual_total',ctypes.c_ulonglong),('virtual_available',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
    memory=Memory();memory.length=ctypes.sizeof(memory)
    if os.name=='nt' and ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        report.update(RAM_total_bytes=memory.total,RAM_free_bytes=memory.available)
    gpu=command(['nvidia-smi','--query-gpu=name,memory.total,memory.free,driver_version','--format=csv,noheader,nounits'])
    parts=[x.strip() for x in gpu.split(',')]
    report.update(nvidia_smi_query=gpu,GPU_model=parts[0] if len(parts)==4 else None,VRAM_total_MiB=int(parts[1]) if len(parts)==4 else None,VRAM_free_MiB=int(parts[2]) if len(parts)==4 else None,NVIDIA_driver=parts[3] if len(parts)==4 else None)
    full=command(['nvidia-smi']);report['nvidia_smi']=full
    match=re.search(r'CUDA(?: UMD)? Version:\s*([\d.]+)',full)
    report['driver_CUDA_compatibility_version']=match.group(1) if match else None
    report['CUDA_toolkit_nvcc']=command(['nvcc','--version'])
    report['XGBoost_build_info']=build_info()
    report['CUDA_runtime_version_note']='Driver compatibility is not the installed CUDA runtime version; XGBoost compiled CUDA details are recorded separately. No standalone runtime/toolkit version is assumed.'
    rng=np.random.default_rng(SEED);X=rng.normal(size=(512,4));y=(X[:,0]>1).astype(int)
    tests={'xgboost':XGBClassifier(n_estimators=3,max_depth=2,tree_method='hist',device='cuda',n_jobs=THREADS,random_state=SEED),'catboost':CatBoostClassifier(iterations=3,depth=2,task_type='GPU',devices='0',gpu_ram_part=.6,random_seed=SEED,verbose=False,allow_writing_files=False,thread_count=THREADS),'lightgbm':LGBMClassifier(n_estimators=3,num_leaves=4,max_bin=63,device_type='gpu',gpu_platform_id=0,gpu_device_id=0,n_jobs=THREADS,verbosity=-1,random_state=SEED)}
    report['GPU_support']={}
    for name,est in tests.items():
        start=time.perf_counter()
        try:
            with warnings.catch_warnings(record=True) as caught:
                est.fit(X,y)
            actual='gpu'
            if name=='xgboost':
                actual=json.loads(est.get_booster().save_config())['learner']['generic_param']['device']
                if not actual.startswith('cuda'):raise RuntimeError('XGBoost silently selected CPU: '+str([str(w.message) for w in caught]))
            report['GPU_support'][name]={'supported':True,'actual_device':actual,'probe_seconds':time.perf_counter()-start,'warnings':[str(w.message) for w in caught]}
        except Exception as e:
            report['GPU_support'][name]={'supported':False,'error':repr(e),'probe_seconds':time.perf_counter()-start}
    report['CUDA_available']=report['GPU_support']['xgboost']['supported'] or report['GPU_support']['catboost']['supported']
    path=ROOT/'reports/modeling/hardware_environment.json';path.write_text(json.dumps(report,indent=2,default=str))
    print(json.dumps(report,indent=2,default=str),flush=True)
    return report

def configure(estimator,model_family,hardware,requested='auto'):
    supported=hardware['GPU_support'].get(model_family,{}).get('supported',False)
    gpu=requested!='cpu' and supported
    if model_family=='xgboost':estimator.set_params(device='cuda' if gpu else 'cpu',max_bin=128)
    elif model_family=='lightgbm':estimator.set_params(device_type='gpu' if gpu else 'cpu',max_bin=63,gpu_platform_id=0,gpu_device_id=0)
    elif model_family=='catboost':
        if hasattr(estimator,'device'):estimator.set_params(device='GPU' if gpu else 'CPU')
        else:estimator.set_params(task_type='GPU' if gpu else 'CPU',devices='0' if gpu else None,gpu_ram_part=.6)
    return estimator,'GPU' if gpu else 'CPU'

if __name__=='__main__':detect()
