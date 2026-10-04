from sklearn.base import BaseEstimator,ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from .config import THREADS,SEED

class NativeCatBoost(ClassifierMixin,BaseEstimator):
    def __init__(self,iterations=220,depth=6,learning_rate=.08,weighted=False,device='CPU'):
        self.iterations=iterations;self.depth=depth;self.learning_rate=learning_rate;self.weighted=weighted;self.device=device
    def fit(self,X,y):
        self.model_=CatBoostClassifier(iterations=self.iterations,depth=self.depth,learning_rate=self.learning_rate,auto_class_weights='Balanced' if self.weighted else None,random_seed=SEED,thread_count=THREADS,verbose=False,allow_writing_files=False,task_type=self.device,devices='0' if self.device=='GPU' else None,gpu_ram_part=.6)
        self.model_.fit(X,y,cat_features=[c for c in X if c!='bmi'])
        self.classes_=self.model_.classes_;self.n_features_in_=X.shape[1];self.feature_names_in_=X.columns.to_numpy();return self
    def predict_proba(self,X):return self.model_.predict_proba(X)
    def predict(self,X):return self.model_.predict(X).ravel().astype(int)

def candidates(ratio):
    return [
      ('dummy_most_frequent',DummyClassifier(strategy='most_frequent'),False,False,'none'),
      ('dummy_prior',DummyClassifier(strategy='prior'),False,False,'none'),
      ('logistic_none',LogisticRegression(C=1,max_iter=600,solver='lbfgs',random_state=SEED),True,False,'none'),
      ('logistic_balanced',LogisticRegression(C=1,max_iter=600,solver='lbfgs',class_weight='balanced',random_state=SEED),True,False,'balanced'),
      ('random_forest_none',RandomForestClassifier(n_estimators=80,max_depth=12,min_samples_leaf=20,max_samples=.7,n_jobs=THREADS,random_state=SEED),False,False,'none'),
      ('random_forest_balanced',RandomForestClassifier(n_estimators=80,max_depth=12,min_samples_leaf=20,max_samples=.7,class_weight='balanced',n_jobs=THREADS,random_state=SEED),False,False,'balanced'),
      ('hist_gradient_boosting',HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=15,learning_rate=.08,l2_regularization=2,early_stopping=False,random_state=SEED),False,False,'none'),
      ('hist_gradient_boosting_balanced',HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=15,learning_rate=.08,l2_regularization=2,class_weight='balanced',early_stopping=False,random_state=SEED),False,False,'balanced'),
      ('xgboost_none',XGBClassifier(n_estimators=220,max_depth=4,learning_rate=.08,subsample=.85,colsample_bytree=.85,tree_method='hist',n_jobs=THREADS,random_state=SEED,eval_metric='logloss'),False,False,'none'),
      ('xgboost_weighted',XGBClassifier(n_estimators=220,max_depth=4,learning_rate=.08,subsample=.85,colsample_bytree=.85,tree_method='hist',scale_pos_weight=ratio,n_jobs=THREADS,random_state=SEED,eval_metric='logloss'),False,False,'training negatives/positives'),
      ('lightgbm_none',LGBMClassifier(n_estimators=220,num_leaves=15,learning_rate=.08,min_child_samples=60,verbosity=-1,n_jobs=THREADS,random_state=SEED,deterministic=True,force_col_wise=True),False,False,'none'),
      ('lightgbm_balanced',LGBMClassifier(n_estimators=220,num_leaves=15,learning_rate=.08,min_child_samples=60,class_weight='balanced',verbosity=-1,n_jobs=THREADS,random_state=SEED,deterministic=True,force_col_wise=True),False,False,'balanced'),
      ('catboost_native',NativeCatBoost(),False,True,'none'),
      ('catboost_native_balanced',NativeCatBoost(weighted=True),False,True,'balanced'),
      ('catboost_onehot',CatBoostClassifier(iterations=220,depth=6,learning_rate=.08,random_seed=SEED,thread_count=THREADS,verbose=False,allow_writing_files=False),False,False,'none'),
    ]

def family(name):
    for name_prefix in ['dummy','logistic','random_forest','hist_gradient_boosting','xgboost','lightgbm','catboost']:
        if name.startswith(name_prefix):return name_prefix
    return name

def search_space(name):
    if name.startswith('logistic'):return {'classifier__C':[.03,.1,1,3,10]}
    if name.startswith('random_forest'):return {'classifier__max_depth':[8,12,18],'classifier__min_samples_leaf':[10,30,60],'classifier__max_features':[.5,1.]}
    if name.startswith('hist'):return {'classifier__max_leaf_nodes':[7,15,31],'classifier__learning_rate':[.04,.08,.12],'classifier__l2_regularization':[1,5,10]}
    if name.startswith('xgboost'):return {'classifier__max_depth':[3,4,6],'classifier__min_child_weight':[1,10,30],'classifier__learning_rate':[.04,.08,.12]}
    if name.startswith('lightgbm'):return {'classifier__num_leaves':[7,15,31],'classifier__min_child_samples':[30,80,160],'classifier__learning_rate':[.04,.08,.12]}
    return {'classifier__depth':[4,6,8],'classifier__learning_rate':[.04,.08,.12],'classifier__iterations':[180,260]}
