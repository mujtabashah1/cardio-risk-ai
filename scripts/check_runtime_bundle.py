"""Verify the Dockerfile's Python/application file subset in a fresh native process.

This is a packaging smoke check, not a substitute for a Linux Docker build.
"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
integrity=json.loads((ROOT/'reports/deployment/model_integrity.json').read_text())
files=set(integrity['files_sha256'])|{'src/__init__.py','src/models/__init__.py','src/data/__init__.py','reports/deployment/model_integrity.json'}
files.update(str(p.relative_to(ROOT)) for directory in ['api','src/inference'] for p in (ROOT/directory).rglob('*.py'))
with tempfile.TemporaryDirectory(prefix='runtime-bundle-') as name:
    bundle=Path(name)
    for relative in files:
        target=bundle/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/relative,target)
    code="import sys,json; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from src.inference.constants import ROOT; assert ROOT==Path(sys.argv[1]); from api.config import Settings; from src.inference.service import InferenceService; s=InferenceService(Settings()); assert s.predict({'sex':1})['model_version']=='1.0.0'; assert len(s.predict_batch([{'sex':1},{'sex':2}]))==2; print(json.dumps({'passed':True,'minimal_application_bundle':True,'single_and_batch':True,'shap_imported':'shap' in sys.modules,'training_runner_imported':'src.models.train_models' in sys.modules}))"
    result=subprocess.run([sys.executable,'-c',code,str(bundle)],cwd=bundle,capture_output=True,text=True,check=True)
    data=json.loads(result.stdout);data['note']='Fresh native process using Docker application/source subset; installed native packages. Linux image build and container health remain pending.'
    (ROOT/'reports/deployment/runtime_bundle_check.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))
