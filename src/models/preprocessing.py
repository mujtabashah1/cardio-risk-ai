import warnings
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from src.data.mappings import VARIABLES
from .config import FORBIDDEN

DOMAINS={s['name']:sorted({v for v in s['mapping'].values() if v is not None}) for k,s in VARIABLES.items() if k!='_BMI5'}

class FeatureGuard(TransformerMixin,BaseEstimator):
    def __init__(self,features):self.features=features
    def fit(self,X,y=None):
        self.transform(X);self.feature_names_in_=np.array(self.features,dtype=object);self.n_features_in_=len(self.features);return self
    def transform(self,X):
        if not isinstance(X,pd.DataFrame):raise TypeError('Named DataFrame inputs required')
        if X.columns.duplicated().any():raise ValueError('Duplicate feature names')
        if FORBIDDEN.intersection(X):raise ValueError('Target/leakage fields cannot be inputs')
        if set(X)!=set(self.features):raise ValueError(f'Expected exactly: {self.features}')
        result=X.loc[:,self.features].copy()
        for name in self.features:
            values=result[name];nonmissing=values.dropna()
            if not nonmissing.map(lambda v:isinstance(v,(int,float,np.integer,np.floating)) and not isinstance(v,(bool,np.bool_))).all():raise TypeError(f'{name} requires numeric values or null')
            values=values.astype(float)
            if np.isinf(values).any():raise ValueError(f'{name}: infinite values rejected')
            if name=='bmi':
                if not values.dropna().between(12,99.99).all():raise ValueError('BMI must be human-readable, 12.00-99.99, or null')
            else:
                if not values.dropna().eq(values.dropna().round()).all():raise TypeError(f'{name}: category must be an integer')
                unseen=values.notna() & ~values.isin(DOMAINS[name])
                if unseen.any():warnings.warn(f'{name}: unsupported cleaned category treated as missing',UserWarning);values=values.mask(unseen)
            result[name]=values
        return result
    def get_feature_names_out(self,input_features=None):return np.array(self.features,dtype=object)

class NativeCategories(TransformerMixin,BaseEstimator):
    def fit(self,X,y=None):
        self.feature_names_in_=np.array(X.columns,dtype=object);self.bmi_median_=float(X.bmi.median()) if 'bmi' in X else None;return self
    def transform(self,X):
        result=X.copy()
        for name in result:
            if name=='bmi':result[name]=result[name].fillna(self.bmi_median_).astype(float)
            else:result[name]=result[name].map(lambda v:'__MISSING__' if pd.isna(v) else str(int(v))).astype(object)
        return result
    def get_feature_names_out(self,input_features=None):return self.feature_names_in_

def preprocessor(features,scaled=False,missing='most_frequent',ordinal=False,dense=True):
    numeric=[f for f in features if f=='bmi'];categorical=[f for f in features if f!='bmi']
    num_steps=[('impute',SimpleImputer(strategy='median',keep_empty_features=True))]
    if scaled:num_steps.append(('scale',StandardScaler()))
    cat_imputer=SimpleImputer(strategy='most_frequent' if missing=='most_frequent' else 'constant',fill_value=-1,keep_empty_features=True)
    ordinals=[f for f in categorical if f in ['age_group','general_health','education','income_group']] if ordinal else []
    nominal=[f for f in categorical if f not in ordinals];transformers=[]
    if numeric:transformers.append(('bmi',Pipeline(num_steps),numeric))
    if nominal:transformers.append(('categories',Pipeline([('impute',cat_imputer),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=not dense,dtype=np.float32))]),nominal))
    if ordinals:transformers.append(('ordinal_comparison',Pipeline([('impute',SimpleImputer(strategy='most_frequent',keep_empty_features=True))]),ordinals))
    return ColumnTransformer(transformers,sparse_threshold=0 if dense else 1,verbose_feature_names_out=True)

def make_pipeline(features,estimator,scaled=False,missing='most_frequent',ordinal=False,native=False,dense=True):
    assert not FORBIDDEN.intersection(features)
    return Pipeline([('guard',FeatureGuard(features)),('preprocess',NativeCategories() if native else preprocessor(features,scaled,missing,ordinal,dense)),('classifier',estimator)])
