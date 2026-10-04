"""Review staged paths/content without printing credentials or respondent values."""
import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KEYWORDS=re.compile(r'password|token|API_KEY|SECRET|Authorization|Bearer|PRIVATE_KEY',re.I)
PATTERNS=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'AIza[0-9A-Za-z_-]{30,}'),re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----')]
ASSIGNMENT=re.compile(r'''(?:password|token|api_key|secret|authorization|private_key)["']?\s*[:=]\s*["']([^"'\r\n]{8,})["']''',re.I)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--git',default='git')
    parser.add_argument('--report',type=Path,default=ROOT/'reports/model_qa/git_privacy_review.json')
    args=parser.parse_args()
    def git(*command):return subprocess.check_output([args.git,'-C',str(ROOT),*command])
    entries=[f for f in git('ls-files','--stage','-z').split(b'\0') if f]
    files=[entry.split(b'\t',1)[1].decode('utf-8') for entry in entries]
    object_ids=[entry.split(b'\t',1)[0].split()[1] for entry in entries]
    # Read staged objects in one process rather than spawning Git per file.
    batch=subprocess.check_output([args.git,'-C',str(ROOT),'cat-file','--batch'],input=b''.join(oid+b'\n' for oid in object_ids))
    contents=[];offset=0
    for _ in entries:
        end=batch.index(b'\n',offset)
        size=int(batch[offset:end].split()[-1]);offset=end+1
        contents.append(batch[offset:offset+size]);offset+=size+1
    if not files:raise RuntimeError('Stage the reviewed milestone files before running this check.')
    blocked=[];credential_locations=[];keyword_files=[]
    for relative,content in zip(files,contents):
        name=Path(relative).name
        prohibited=(relative.startswith('data/') and relative!='data/processed/data_dictionary.csv') or relative.startswith('models/candidates/') or relative.endswith(('.XPT','.xpt','.npz','.parquet','.pem','.key','.pfx','.p12')) or name=='.env' or (name.startswith('.env.') and name!='.env.example') or 'node_modules/' in relative or name in ['training_partition.csv','split_membership.csv','clean_row_ids.csv','bmi_review_records.csv','invalid_bmi_records.csv','manual_profile_tests.csv','manual_model_qa.csv']
        if prohibited:blocked.append(relative)
        if len(content)>50*1024*1024:blocked.append(relative+' (exceeds reviewed size policy)')
        if Path(relative).suffix.lower() in ['.png','.pdf','.joblib']:continue
        text=content.decode('utf-8',errors='replace')
        if KEYWORDS.search(text):keyword_files.append(relative)
        for index,line in enumerate(text.splitlines(),1):
            matches=list(ASSIGNMENT.finditer(line))
            assignments=[m.group(1) for m in matches if not any(p in m.group(1).upper() for p in ['EXAMPLE','PLACEHOLDER','YOUR_','REPLACE_'])]
            if any(pattern.search(line) for pattern in PATTERNS) or assignments:credential_locations.append({'file':relative,'line':index})
        if relative.endswith('.csv'):
            header=next(csv.reader(text.splitlines()),[])
            if any(column in ['source_row_id','equality_group','training_role'] for column in header):blocked.append(relative+' (respondent membership header)')
    required=['src/data/clean_data.py','src/data/mappings.py','src/models/train_models.py','src/models/train_all.py','src/models/evaluate.py','frontend/app.js','api/main.py','models/heart_disease_pipeline.joblib']
    missing=[name for name in required if name not in files]
    report={'staged_files':len(files),'respondent_data_paths_found':blocked,'potential_credentials':credential_locations,'keyword_reference_files':keyword_files,'required_sources_missing':missing,'passed':not(blocked or credential_locations or missing),'scope':'Staged Git blobs; keyword references are reviewed separately; no credential values printed.'}
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='keyword_reference_files'},indent=2))
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
