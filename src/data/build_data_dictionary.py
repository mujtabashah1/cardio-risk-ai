"""Recover documentation only; never clean raw data, split data, or train a model."""
import hashlib
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from pypdf import PdfReader

from .mappings import VARIABLES, VARIABLE_MAPPINGS, TARGET_MAPPING, FEATURE_NAMES, CODEBOOK, CALCULATED

COLUMNS = ['original_variable','clean_variable','role','description','original_codes',
           'original_labels','clean_mapping','missing_value_rule','data_type','feature_type',
           'ordinal_or_nominal','used_in_model','used_in_mobile_app','mobile_input_type',
           'user_facing_question','allowed_user_answers','internal_encoding','validation_rules',
           'reason_for_inclusion','source_document','notes','reason_for_inclusion_or_exclusion']

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def encoded(value):
    return json.dumps(value,ensure_ascii=False)

def source_entries(root):
    pages=[p.extract_text() for p in PdfReader(root/'docs/codebook21.pdf').pages]
    text='\n'.join(pages)
    calculated='\n'.join(p.extract_text() for p in PdfReader(root/'docs/calculated_variables_2021.pdf').pages)
    assert '(_BMI5*100)' in calculated.replace(' ','')
    assert 'Has 2 implied decimal' in text
    assert 'CVDINFR4=1 OR CVDCRHD4=1' in calculated
    assert 'CVDINFR4=2 AND CVDCRHD4=2' in calculated
    result={}
    for original in [*VARIABLES,'_MICHD']:
        pattern=r'SAS Variable Name:\s*'+re.escape(original)+r'\b'
        match=re.search(pattern,text)
        if not match: raise ValueError(f'Official definition missing: {original}')
        block=text[match.end():].split('\nLabel:',1)[0]
        codes=set(re.findall(r'(?m)^\s*(\d+)\s',block))
        if original!='_BMI5':
            mapping=TARGET_MAPPING if original=='_MICHD' else VARIABLE_MAPPINGS[original]
            assert set(map(str,mapping)).issubset(codes),f'CDC codes not confirmed for {original}'
        page=next(i+1 for i,p in enumerate(pages) if re.search(pattern,p))
        result[original]=(block,f'{CODEBOOK}#page={page}; {CALCULATED}')
    return result

def build_dictionary(root):
    entries=source_entries(root)
    logic=(root/'src/data/clean_data.py').read_text(encoding='utf-8')
    assert 's.between(1200,9999) & s.eq(s.round())' in logic
    assert '(s/100).where(valid)' in logic
    assert "s.map(spec['mapping'])" in logic
    selection=(root/'reports/feature_selection_report.md').read_text(encoding='utf-8')
    rows=[]
    for original,spec in VARIABLES.items():
        assert f'| {original} |' in selection
        block,source=entries[original]
        labels={str(k):v for k,v in spec['labels'].items()}
        # Expand terse labels using this variable's official nonresponse definitions.
        for k in spec['unknown']: labels[str(k)]="Don't know/Not sure"
        for k in spec['refused']: labels[str(k)]='Refused'
        combined={'_AGEG5YR':"Don't know/Refused/Missing",'_TOTINDA':"Don't know/Refused/Missing",
                  '_SMOKER3':"Don't know/Refused/Missing",'_RFHYPE6':"Don't know/Not sure/Refused/Missing",
                  'DRNKANY5':'Refused/Missing','_EDUCAG':"Don't know/Not sure/Missing",
                  '_INCOMG1':"Don't know/Not sure/Missing (source INCOME3: 77 unknown, 99 refused, or missing)"}
        for k in spec['combined']: labels[str(k)]=combined[original]
        blank_label=("Don't know/Refused/Missing" if original=='_BMI5' else 'Not asked or Missing') if 'BLANK' in block else 'SAS missing input; no separate BLANK category listed in this CDC table'
        labels['BLANK']=blank_label
        notes='No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.'
        if original=='_BMI5':
            mapping={'integer 1200..9999':'original value / 100','BLANK':None,'outside 1200..9999 or noninteger':None}
            answers='Measured height and weight, or directly supplied BMI; unknown/skipped -> missing'
            internal='BMI = weight_kg / height_metres**2; released _BMI5 / 100. Store human-readable BMI, not the scaled CDC integer.'
            rules='Pipeline accepts integer released _BMI5 in [1200,9999], yielding BMI in [12.00,99.99]; other values become missing. Do not clamp or add outlier-removal rules. Height/weight inputs must be positive, finite and unit-labelled; accept BMI to two decimal places.'
            notes+=' CDC construction code limits BMI to 12.00-99.99; release code multiplies by 100. Existing review flags were descriptive only, not removals.'
            input_type='requires measurement; numeric BMI or calculated from height/weight'
        else:
            assert spec['mapping']==VARIABLE_MAPPINGS[original]
            mapping={str(k):v for k,v in VARIABLE_MAPPINGS[original].items()}|{'BLANK':None}
            answers=[labels[str(k)] for k,v in spec['mapping'].items() if v is not None]+["Don't know",'Prefer not to answer','Skipped/not provided']
            internal=encoded(mapping)+'; mobile nonresponse -> null (not a learned or imputed category)'
            approved=sorted({v for v in spec['mapping'].values() if v is not None})
            rules=f'Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: {approved}, plus missing. No global 7/9/77/88/99 recoding.'
            input_type=spec['usability']+'; single choice'
            if original=='_AGEG5YR': rules+=' If age is entered numerically, require an adult age and apply the documented bins; 80 or older maps to 13.'
            if original=='_SMOKER3': notes+=' Category 4 is CDC Never smoked: fewer than 100 lifetime cigarettes, not necessarily zero. For >=100 lifetime cigarettes, current every-day/some-day/not-at-all maps to 1/2/3.'
            if original=='DIABETE4': notes+=' Preserve 1 Yes, 2 pregnancy-only, 3 No, and 4 prediabetes/borderline separately; do not binarize.'
            if original=='_RFHYPE6': notes+=' Source BPHIGH6=1 -> 1; BPHIGH6=2 (pregnancy-only), 3 (No), or 4 (borderline/prehypertensive) -> 0. Unknown/refused/missing -> missing.'
            if original=='TOLDHI3': notes+=' Requires known professional diagnosis after testing; not tested/unknown must never become No.'
        missing='Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.'
        if original=='_BMI5': missing='SAS missing/blank and released values outside [1200,9999] or noninteger -> missing; no new outlier removal.'
        rows.append(dict(original_variable=original,clean_variable=spec['name'],role='predictor',description=spec['question'],original_codes=encoded(list(labels)),original_labels=encoded(labels),clean_mapping=encoded(mapping),missing_value_rule=missing,data_type='Float64 (nullable continuous)' if original=='_BMI5' else 'Int8 (nullable categorical)',feature_type='continuous numeric' if original=='_BMI5' else 'categorical',ordinal_or_nominal=spec['kind'],used_in_model=True,used_in_mobile_app=True,mobile_input_type=input_type,user_facing_question=spec['question'],allowed_user_answers=encoded(answers) if isinstance(answers,list) else answers,internal_encoding=internal,validation_rules=rules,reason_for_inclusion=spec['reason'],reason_for_inclusion_or_exclusion=spec['reason'],source_document=source,notes=notes))
        if original=='SEXVAR':
            rows[-1]['user_facing_question']='What is your sex? Select Male or Female using the BRFSS respondent-sex categories.'
        if original=='_RFHYPE6':
            rows[-1]['user_facing_question']='Have you ever been told by a doctor, nurse, or other health professional that you have high blood pressure? Was this only during pregnancy, or were you told you had borderline high blood pressure or prehypertension?'
            mobile_answers={'Yes':1,'Yes, only during pregnancy':0,'No':0,'Borderline high blood pressure or prehypertension':0,"Don't know":None,'Prefer not to answer':None,'Skipped/not provided':None}
            rows[-1]['allowed_user_answers']=encoded(list(mobile_answers))
            rows[-1]['internal_encoding']=encoded({'CDC released-code mapping':mapping,'mobile-answer mapping':mobile_answers})
    target_mapping={str(k):v for k,v in TARGET_MAPPING.items()}|{'BLANK':'EXCLUDE ROW'}
    rows.append(dict(original_variable='_MICHD',clean_variable='heart_disease',role='target',description='PREVALENT / EXISTING reported coronary heart disease or myocardial infarction; not a prospective 10-year cardiovascular-risk label or future disease probability.',original_codes=encoded(['1','2','BLANK']),original_labels=encoded({'1':'Reported having MI or CHD','2':'Did not report having MI or CHD','BLANK':'Not asked or Missing; target unavailable'}),clean_mapping=encoded(target_mapping),missing_value_rule='Missing/unusable target is excluded from supervised rows. Unexpected nonmissing _MICHD codes cause the existing pipeline to fail, rather than guess or silently recode.',data_type='Int8 (non-null binary label)',feature_type='binary target',ordinal_or_nominal='binary nominal',used_in_model=True,used_in_mobile_app=False,mobile_input_type='not a questionnaire/model input',user_facing_question='Not applicable: supervised target, never an input.',allowed_user_answers='Not applicable',internal_encoding=encoded(target_mapping),validation_rules='heart_disease must contain only 0 or 1 and never be missing. _MICHD, CVDINFR4 and CVDCRHD4 must never become predictors.',reason_for_inclusion='Supervised label only; excluded from predictors.',reason_for_inclusion_or_exclusion='Supervised label only; excluded from predictors.',source_document=entries['_MICHD'][1],notes='CDC derives _MICHD=1 if CVDINFR4=1 OR CVDCRHD4=1; =2 if both equal 2; otherwise missing. Positive diagnosis takes precedence over unknown in the other source. used_in_model=True denotes target use only, never predictor use. No model has been trained.'))
    result=pd.DataFrame(rows,columns=COLUMNS)
    result.loc[result.role=='target','internal_encoding']='_MICHD = 1 -> heart_disease = 1 (reported CHD/MI); _MICHD = 2 -> heart_disease = 0 (did not report CHD/MI); missing/unusable target -> excluded from supervised dataset. Unexpected nonmissing codes fail cleaning.'
    assert len(result)==17 and result.clean_variable.tolist()==FEATURE_NAMES+['heart_disease']
    return result

def verify_saved_datasets(root,dictionary):
    processed=root/'data/processed';expected=dictionary.clean_variable.tolist()
    checked={}
    for name in ['heart_disease_clean','train','validation','test']:
        count=0
        for frame in pd.read_csv(processed/f'{name}.csv',chunksize=50000,float_precision='round_trip'):
            assert list(frame)==expected,f'Schema mismatch in {name}'
            assert frame.heart_disease.notna().all() and frame.heart_disease.isin([0,1]).all()
            for original,s in VARIABLES.items():
                values=frame[s['name']].dropna()
                if original=='_BMI5':
                    assert values.between(12,99.99).all()
                    np.testing.assert_allclose(values*100,np.round(values*100),rtol=0,atol=1e-10)
                else: assert values.isin([v for v in s['mapping'].values() if v is not None]).all()
            count+=len(frame)
        checked[name]=count
    assert checked['heart_disease_clean']==sum(checked[k] for k in ['train','validation','test'])
    return checked

def write_dictionary(root):
    dictionary=build_dictionary(root)
    checked=verify_saved_datasets(root,dictionary)
    destination=root/'data/processed/data_dictionary.csv'
    csv_bytes=dictionary.to_csv(index=False).encode('utf-8')
    if not destination.exists() or destination.read_bytes()!=csv_bytes:
        destination.write_bytes(csv_bytes)
    # Roundtrip validation ensures literal mappings and fields survive CSV serialization.
    restored=pd.read_csv(destination,keep_default_na=False)
    assert restored.clean_variable.tolist()==dictionary.clean_variable.tolist()
    for original,s in VARIABLES.items():
        row=restored[restored.original_variable==original].iloc[0]
        if original!='_BMI5':
            mapping=json.loads(row.clean_mapping);mapping.pop('BLANK')
            assert {int(k):v for k,v in mapping.items()}==VARIABLE_MAPPINGS[original]
    target=json.loads(restored[restored.role=='target'].iloc[0].clean_mapping)
    assert {int(k):v for k,v in target.items() if k!='BLANK'}==TARGET_MAPPING
    md=['# BRFSS 2021 data dictionary','', '17 variables: 16 predictors and one target. This documents the existing completed pipeline; no datasets were cleaned, split, or trained during dictionary recovery.', '', 'The target represents PREVALENT / EXISTING reported CHD or MI. It is NOT prospective 10-year cardiovascular risk or future disease probability.', '', '## Leakage exclusions','', '`_MICHD` as an input, `CVDINFR4`, and `CVDCRHD4` must NEVER be predictors. The two diagnosis variables directly construct `_MICHD`. They are described here, not added as dictionary rows or model inputs.', '', 'Recreate documentation only: `python -m src.data.build_data_dictionary`.', '']
    for row in dictionary.to_dict('records'):
        md.extend([f'## {row["clean_variable"]} ({row["original_variable"]})',''])
        labels=json.loads(row['original_labels']);mapping=json.loads(row['clean_mapping'])
        md.extend(['| Original code | CDC meaning / missing-input description | Cleaned representation |','| --- | --- | --- |'])
        for code,label in labels.items():
            value=mapping.get(code,'Divide by 100 only for integer values 1200..9999; otherwise missing')
            md.append(f'| {code} | {label} | {"missing (null)" if value is None else value} |')
        md.append('')
        for key in COLUMNS:
            if key not in ['original_variable','clean_variable','original_codes','original_labels','clean_mapping']:
                md.extend([f'**{key.replace("_"," ")}**: {row[key]}',''])
    md.extend(['## Saved dataset checks','',*['- '+k+': '+str(v)+' rows; all 17 columns and allowed values verified.' for k,v in checked.items()],'', 'BLANK descriptions for variables without a separate codebook BLANK category describe existing pipeline missing-input handling; they do not invent a new CDC response code. Mobile skipped/refused options similarly become null, not additional model categories.'])
    markdown_path=root/'docs/data_dictionary.md'
    markdown='\n'.join(md)+'\n'
    if not markdown_path.exists() or markdown_path.read_text(encoding='utf-8')!=markdown:
        markdown_path.write_text(markdown,encoding='utf-8')
    return checked

def main():
    root=Path(__file__).resolve().parents[2]
    # Use the historical build's validation and hashes to verify the unchanged artifacts
    # without reloading or recleaning the 1 GB raw dataset.
    manifest=json.loads((root/'reports/artifact_manifest.json').read_text())
    files=[root/'data/processed'/f'{name}.csv' for name in ['heart_disease_clean','train','validation','test']]
    files += [root/'data/processed/heart_disease_clean.parquet',root/'src/data/mappings.py',root/'src/data/clean_data.py',root/'docs/codebook21.pdf',root/'docs/calculated_variables_2021.pdf']
    before={str(p.relative_to(root)):digest(p) for p in files}
    for name,value in before.items(): assert manifest['outputs'][name]==value,f'Previously validated artifact changed: {name}'
    previous_validation=json.loads((root/'reports/validation_report.json').read_text())
    assert previous_validation['passed'] and previous_validation['target_derivation_verified']
    assert previous_validation['saved_csv_parquet_and_split_roundtrips_verified']
    destination=root/'data/processed/data_dictionary.csv'
    previous=pd.read_csv(destination) if destination.exists() else None
    defects=[]
    if previous is not None:
        if len(previous)!=17: defects.append(f'Expected 17 rows; existing file has {len(previous)}')
        defects.extend('Missing column: '+c for c in COLUMNS if c not in previous)
        if defects:
            backup=root/'reports/data_dictionary_previous.csv'
            if not backup.exists(): shutil.copyfile(destination,backup)
    checked=write_dictionary(root)
    assert all(digest(root/name)==value for name,value in before.items()),'Input artifact modified'
    report=dict(passed=True,documented_variables=17,predictors=16,targets=1,all_cleaned_columns_documented=True,mappings_match_cleaning_pipeline=True,unverified_mappings=[],existing_dictionary_path=str(destination),existing_dictionary_defects=defects,dataset_rows_checked=checked,validated_original_artifact_hashes=before,raw_dataset_read=False,cleaning_rerun=False,model_trained=False,notes='Historical full-build manifest is retained; its prior dictionary hash describes the earlier file. This recovery has its own output hashes.')
    report['output_hashes']={str(p.relative_to(root)):digest(p) for p in [destination,root/'docs/data_dictionary.md']}
    (root/'reports/data_dictionary_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['passed','documented_variables','mappings_match_cleaning_pipeline','unverified_mappings','dataset_rows_checked']},indent=2))

if __name__=='__main__':main()
