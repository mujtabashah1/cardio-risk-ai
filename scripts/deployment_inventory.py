"""Record serving-source fingerprints without changing the historical model freeze."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[]
for directory in ['api','src/inference','tests/api','tests/inference','tests/artifacts','tests/fixtures','reports/deployment','release']:
    files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='deployment_artifact_manifest.json')
files.extend(ROOT/p for p in ['Dockerfile','.dockerignore','.env.example','requirements-api.txt','requirements-api-test.txt','README.md','docs/api.md','docs/model_inputs.md','docs/thresholds.md','scripts/audit_deployment.py','scripts/check_deployment.py','scripts/check_runtime_bundle.py','scripts/profile_inference.py','scripts/verify_container.ps1','scripts/deployment_inventory.py'])
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}
manifest['scripts/complete_post_training_artifacts.py']=hashlib.sha256((ROOT/'scripts/complete_post_training_artifacts.py').read_bytes()).hexdigest()
for relative in ['scripts/verify_release.py','scripts/package_release.py','scripts/verify_release_archive.py','scripts/release_probe_server.py','docs/api_contract.md','docs/model_v2_backlog.md']:
    manifest[relative]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
(ROOT/'reports/deployment/deployment_artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Recorded deployment artifacts:',len(manifest))
