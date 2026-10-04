import logging
import numpy as np
import pandas as pd
from .mappings import VARIABLES,TARGET_MAPPING

def clean_data(raw):
    logging.info('Cleaning target; removing only unusable target records')
    if not raw['_MICHD'].dropna().isin(TARGET_MAPPING).all(): raise ValueError('Unexpected target codes')
    keep=raw['_MICHD'].isin(TARGET_MAPPING)
    clean=pd.DataFrame(index=raw.index[keep])
    missing=[]
    for original,spec in VARIABLES.items():
        s=raw[original]
        if original=='_BMI5':
            valid=s.between(1200,9999) & s.eq(s.round())
            converted=(s/100).where(valid)
            logging.info('BMI scale /100; undocumented range/noninteger values: %s', int((s.notna() & ~valid).sum()))
        else:
            unexpected=s.notna() & ~s.isin(spec['mapping'])
            if unexpected.any(): raise ValueError(f'Undocumented {original} codes: {s[unexpected].unique()}')
            converted=s.map(spec['mapping'])
        clean[spec['name']]=converted.loc[keep].astype('Float64' if original=='_BMI5' else 'Int8')
        blank=int(s.isna().sum())
        unknown=int(s.isin(spec['unknown']).sum())
        refused=int(s.isin(spec['refused']).sum())
        combined=int(s.isin(spec['combined']).sum())
        invalid=int((s.notna() & converted.isna() & ~s.isin((*spec['unknown'],*spec['refused'],*spec['combined']))).sum())
        missing.append(dict(variable=original,valid_count=int(converted.notna().sum()),missing_count=int(converted.isna().sum()),missing_percentage=float(converted.isna().mean()*100),dont_know_count=unknown,refused_count=refused,not_asked_or_missing_count=blank,combined_unknown_refused_missing_count=combined,other_invalid_count=invalid))
        logging.info('%s: %s missing/invalid predictors retained as missing',original,int(converted.isna().sum()))
    clean['heart_disease']=raw.loc[keep,'_MICHD'].map(TARGET_MAPPING).astype('Int8')
    logging.info('Rows removed for unavailable target: %s; final rows: %s',int((~keep).sum()),len(clean))
    return clean,pd.DataFrame(missing)
