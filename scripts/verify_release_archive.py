"""Test the actual ZIP runtime in a fresh native process; no Docker claim."""
import hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'release/cardiorisk-api-1.0.0.zip'
with tempfile.TemporaryDirectory(prefix='research-release-') as directory:
    bundle=Path(directory)
    with zipfile.ZipFile(archive) as package:
        for member in package.namelist():
            target=(bundle/member).resolve()
            assert target.is_relative_to(bundle.resolve()),member
        package.extractall(bundle)
    manifest=json.loads((bundle/'release/release_manifest.json').read_text())
    for relative,expected in manifest['packaged_files_sha256'].items():assert hashlib.sha256((bundle/relative).read_bytes()).hexdigest()==expected,relative
    code="import sys,json,numpy as np; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from src.inference.constants import ROOT; assert ROOT==Path(sys.argv[1]); from api.config import Settings; from src.inference.service import InferenceService; from api.main import create_app; from fastapi.testclient import TestClient; rows=json.loads((ROOT/'tests/fixtures/golden_predictions.json').read_text()); s=InferenceService(Settings()); results=s.predict_batch([r['input'] for r in rows]); assert all(abs(v['profile_score']-r['expected_profile_score'])<=1e-12 for v,r in zip(results,rows)); client=TestClient(create_app()); client.__enter__(); assert client.get('/health').status_code==200 and client.get('/ready').status_code==200; response=client.post('/predict/batch',json={'profiles':[r['input'] for r in rows]}); assert response.status_code==200; assert all(abs(v['profile_score']-r['expected_profile_score'])<=.5e-6+1e-12 for v,r in zip(response.json()['predictions'],rows)); client.__exit__(None,None,None); print(json.dumps({'passed':True,'archive_member_hashes_verified':True,'direct_golden_passed':True,'packaged_API_golden_passed':True,'no_training_datasets_in_archive':not (ROOT/'data/processed/train.csv').exists(),'note':'Fresh native process with installed dependencies; not a Linux image/container test'}))"
    result=subprocess.run([sys.executable,'-c',code,str(bundle)],cwd=bundle,capture_output=True,text=True,check=True)
    data=json.loads(result.stdout);data['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
    (ROOT/'reports/deployment/release_archive_verification.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))
