"""Rebuild with: python -m src.data.build_dataset [--root PATH]."""
import argparse
import hashlib
import json
import logging
from pathlib import Path
import pandas as pd
from .inspect_data import inspect_data
from .clean_data import clean_data
from .validate_data import validate_data,validate_saved_frame
from .split_data import split_data
from .reports import reports

def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): digest.update(block)
    return digest.hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=parser.parse_args()
    root=args.root.resolve();processed=root/'data/processed';out=root/'reports'
    processed.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(out/'build.log',mode='w',encoding='utf-8')])
    raw_path=root/'data/raw/LLCP2021.XPT';before=sha256(raw_path)
    archive=root.parent/'LLCP2021XPT.zip';zip_before=sha256(archive) if archive.exists() else None
    logging.info('Loading raw BRFSS XPT without a full-data copy')
    raw=pd.read_sas(raw_path,format='xport',encoding='utf-8')
    logging.info('Rows loaded: %s; columns loaded: %s',*raw.shape)
    logging.info('Profiling complete raw dataset before cleaning')
    summary=inspect_data(raw,out/'data_profile')
    # Verify CDC target construction across the complete dataset.
    derived=pd.Series(float('nan'),index=raw.index)
    derived.loc[raw.CVDINFR4.eq(2)&raw.CVDCRHD4.eq(2)]=2
    derived.loc[raw.CVDINFR4.eq(1)|raw.CVDCRHD4.eq(1)]=1
    assert derived.equals(raw['_MICHD']), 'Target derivation mismatch'
    logging.info('CDC target derivation verified against every raw row')
    clean,missing=clean_data(raw)
    validation=validate_data(clean,raw)
    logging.info('Cleaned dataset validation passed; creating stratified splits')
    clean.to_csv(processed/'heart_disease_clean.csv',index=False)
    clean.to_parquet(processed/'heart_disease_clean.parquet',index=False)
    splits=split_data(clean,processed)
    csv=pd.read_csv(processed/'heart_disease_clean.csv',float_precision='round_trip')
    parquet=pd.read_parquet(processed/'heart_disease_clean.parquet')
    validate_saved_frame(csv,clean.reset_index(drop=True))
    pd.testing.assert_frame_equal(parquet,clean.reset_index(drop=True))
    for name,frame in splits.items():
        saved=pd.read_csv(processed/f'{name}.csv',float_precision='round_trip')
        validate_saved_frame(saved,frame.reset_index(drop=True))
    validation['saved_csv_parquet_and_split_roundtrips_verified']=True
    validation.update(split_source_intersections_empty=True,split_exact_labeled_record_intersections_empty=True,split_union_complete=True,target_derivation_verified=True)
    final=reports(root,raw,clean,missing,summary,validation,splits,{'raw':before})
    assert sha256(raw_path)==before,'Raw XPT changed'
    if zip_before: assert sha256(archive)==zip_before,'Raw ZIP changed'
    pd.DataFrame({'source_row_id':clean.index}).to_csv(processed/'clean_row_ids.csv',index=False)
    hashes={str(p.relative_to(root)):sha256(p) for folder in [processed,out,root/'docs',root/'src'] for p in sorted(folder.rglob('*')) if p.is_file() and p.suffix not in ['.pyc','.log'] and p.name not in ['artifact_manifest.json','reproducibility_report.json','generated_files.txt']}
    manifest=dict(raw_xpt_sha256=before,raw_zip_sha256=zip_before,outputs=hashes)
    (out/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2))
    paths=[str(p.relative_to(root)) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in str(p)]
    (out/'generated_files.txt').write_text('\n'.join(paths)+'\n')
    logging.info('Build complete: %s',json.dumps(final))

if __name__=='__main__': main()
