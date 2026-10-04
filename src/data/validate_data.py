"""Fail-fast validation; keep source-row provenance outside predictor files."""
import numpy as np
import pandas as pd
from .mappings import VARIABLES,FEATURE_NAMES,LEAKAGE

def validate_saved_frame(saved,expected):
    assert list(saved)==list(expected)
    # CSV uses np.nan while nullable pandas arrays use pd.NA.
    np.testing.assert_allclose(saved.to_numpy(dtype=float,na_value=np.nan),expected.to_numpy(dtype=float,na_value=np.nan),equal_nan=True,rtol=0,atol=0)

def validate_data(clean,raw):
    assert list(clean)==FEATURE_NAMES+['heart_disease']
    assert not LEAKAGE.intersection(clean.columns)
    assert clean.heart_disease.notna().all() and clean.heart_disease.isin([0,1]).all()
    expected=raw.index[raw['_MICHD'].isin([1,2])]
    assert clean.index.equals(expected) and clean.index.is_unique
    assert len(clean)+int(raw['_MICHD'].isna().sum())==len(raw)
    assert np.array_equal(clean.heart_disease.to_numpy(dtype=int),(raw.loc[expected,'_MICHD']==1).to_numpy(dtype=int))
    for original,spec in VARIABLES.items():
        s=clean[spec['name']]
        if original=='_BMI5':
            source=raw.loc[expected,original]
            wanted=(source/100).where(source.between(1200,9999)&source.eq(source.round()))
            np.testing.assert_allclose(s.to_numpy(dtype=float,na_value=np.nan),wanted.to_numpy(),equal_nan=True,rtol=0,atol=0)
        else:
            assert s.dropna().isin([x for x in spec['mapping'].values() if x is not None]).all()
            wanted=raw.loc[expected,original].map(spec['mapping'])
            np.testing.assert_allclose(s.to_numpy(dtype=float,na_value=np.nan),wanted.to_numpy(dtype=float),equal_nan=True,rtol=0,atol=0)
    # Projection can create equal feature rows; they remain distinct source records.
    return dict(passed=True,source_ids_unique=True,projected_duplicates=int(clean.duplicated().sum()),rows=len(clean))
