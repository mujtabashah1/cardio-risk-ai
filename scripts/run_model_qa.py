"""Synthetic QA via the existing API. Never reads respondent data or trains."""
import csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api.main import create_app
from src.inference.validation import DOMAINS
ROOT=Path(__file__).resolve().parents[1]
LOW=dict(age_group=1,sex=2,bmi=22,general_health=1,physical_activity=1,smoking_status=4,diabetes=3,stroke_history=0,kidney_disease=0,asthma=0,difficulty_walking=0,high_cholesterol=0,high_blood_pressure=0,alcohol_use=0)
HIGH=dict(age_group=11,sex=1,bmi=34,general_health=5,physical_activity=0,smoking_status=1,diabetes=1,stroke_history=1,kidney_disease=1,asthma=1,difficulty_walking=1,high_cholesterol=1,high_blood_pressure=1,alcohol_use=0)
def write(name,rows,columns):
    with (ROOT/'reports/model_qa'/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
def run():
    output=ROOT/'reports/model_qa';output.mkdir(exist_ok=True)
    cases=[('Young healthy profile',LOW),('Older high-association profile',HIGH)]
    for k,values in {**DOMAINS,'bmi':(12,22,28.5,34,99.99)}.items():
        cases.extend((f'{k}={v}',{**LOW,k:v}) for v in values)
    missing=[('BMI missing',{**LOW,'bmi':None}),('Smoking missing',{**LOW,'smoking_status':None}),('High cholesterol missing',{**LOW,'high_cholesterol':None}),('Multiple values missing',dict.fromkeys(LOW))]
    cases+=missing
    rows=[];boundaries=[];switches=[]
    with TestClient(create_app()) as client:
        for i,(name,p) in enumerate(cases,1):
            r=client.post('/predict',json={'profile':p});data=r.json()
            rows.append(dict(test_id=f'SYN-{i:03}',profile_name=name,profile_json=json.dumps(p),http_status=r.status_code,actual_score=data.get('profile_score',''),actual_classification=data.get('classification',''),threshold_profile=data.get('threshold_profile',''),status='REVIEW' if r.status_code==200 else 'FAIL',notes='Synthetic behavior observation; qualitative review pending.'))
        for k,values in {**DOMAINS,'bmi':(12,99.99)}.items():
            for v in (min(values),max(values)):
                r=client.post('/predict',json={'profile':{**LOW,k:v}})
                boundaries.append(dict(feature=k,value=v,expected_http_status=200,actual_http_status=r.status_code,status='PASS' if r.status_code==200 else 'FAIL'))
            for v in ((11.99,100) if k=='bmi' else (min(values)-1,max(values)+1)):
                r=client.post('/predict',json={'profile':{**LOW,k:v}})
                boundaries.append(dict(feature=k,value=v,expected_http_status=422,actual_http_status=r.status_code,status='PASS' if r.status_code==422 and 'error' in r.json() else 'FAIL'))
        for t in ['research_balanced','high_sensitivity_80','high_sensitivity_90','youden','conventional_050']:
            r=client.post('/predict',json={'profile':HIGH,'threshold_profile':t});switches.append(r.json())
    columns=list(rows[0]);write('synthetic_profile_results.csv',rows,columns)
    write('missing_input_tests.csv',rows[-len(missing):],columns)
    write('boundary_tests.csv',boundaries,list(boundaries[0]))
    if not (output/'manual_profile_tests.csv').exists():
        write('manual_profile_tests.csv',[],['test_id','profile_name','expected_qualitative_behavior','actual_score','actual_classification','threshold_profile','status','notes'])
    sensitivity=[dict(feature=name.split('=')[0],modified_value=name.split('=')[1],original_score=rows[0]['actual_score'],modified_score=r['actual_score'],absolute_score_difference=abs(r['actual_score']-rows[0]['actual_score']),status='REVIEW') for (name,p),r in zip(cases[2:-4],rows[2:-4]) if isinstance(r['actual_score'],(float,int))]
    write('feature_sensitivity_tests.csv',sensitivity,list(sensitivity[0]))
    scores=[r['actual_score'] for r in rows if isinstance(r['actual_score'],(float,int))]
    summary=dict(synthetic_tests=len(rows),score_min=min(scores),score_max=max(scores),low_score=rows[0]['actual_score'],high_score=rows[1]['actual_score'],high_scored_higher=rows[1]['actual_score']>rows[0]['actual_score'],unexpected_errors=sum(r['http_status']!=200 for r in rows),missing_passed=sum(r['http_status']==200 for r in rows[-4:]),boundary_passed=sum(r['status']=='PASS' for r in boundaries),boundary_count=len(boundaries),threshold_score_unchanged=len({r['profile_score'] for r in switches})==1,classification_distribution={k:sum(r['actual_classification']==k for r in rows) for k in ['lower_model_association','elevated_model_association']})
    (output/'qa_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'threshold_switching.json').write_text(json.dumps(switches,indent=2)+'\n')
    notable=sorted(sensitivity,key=lambda r:r['absolute_score_difference'],reverse=True)[:5]
    (output/'model_behavior_report.md').write_text('# Frozen model behavior QA\n\nSynthetic research tests only; no clinical rules or causal conclusions. Model v1.0.0 remains unchanged.\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n\nAll four missing-value cases are sent as explicit nulls. Categorical minima/maxima and out-of-domain values plus BMI endpoints and out-of-range values are exercised through POST /predict. PASS in boundary tests means the HTTP contract matched expectations. All valid behavioral observations remain REVIEW pending human assessment.\n\nLargest observed one-field response changes:\n\n'+ '\n'.join(f"- {r['feature']}={r['modified_value']}: absolute difference {r['absolute_score_difference']:.6f}" for r in notable)+'\n\nNo unsupported clinical directional expectations were asserted. See CSV files for every input and actual response.\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if summary['unexpected_errors'] or summary['missing_passed']!=4 or summary['boundary_passed']!=summary['boundary_count'] or not summary['threshold_score_unchanged']:
        raise RuntimeError('Synthetic API contract QA failed; inspect reports/model_qa results.')
if __name__=='__main__':run()
