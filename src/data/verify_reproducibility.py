"""Rebuild and compare every deterministic artifact to the previous build."""
import json
import subprocess
import sys
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[2]
    manifest=root/'reports/artifact_manifest.json'
    before=json.loads(manifest.read_text())
    subprocess.run([sys.executable,'-m','src.data.build_dataset','--root',str(root)],check=True,cwd=root)
    after=json.loads(manifest.read_text())
    assert before['raw_xpt_sha256']==after['raw_xpt_sha256']
    assert before['raw_zip_sha256']==after['raw_zip_sha256']
    changed=sorted(k for k in set(before['outputs'])|set(after['outputs']) if before['outputs'].get(k)!=after['outputs'].get(k))
    report=dict(passed=not changed,artifacts_compared=len(after['outputs']),changed_artifacts=changed,raw_xpt_unchanged=True,raw_zip_unchanged=True,method='Fresh full rebuild; SHA-256 comparison of deterministic output and source artifacts. Logs and file inventories are excluded.')
    (root/'reports/reproducibility_report.json').write_text(json.dumps(report,indent=2))
    paths=[str(p.relative_to(root)) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in str(p)]
    (root/'reports/generated_files.txt').write_text('\n'.join(paths)+'\n')
    assert not changed, f'Artifacts changed across rebuild: {changed}'
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
