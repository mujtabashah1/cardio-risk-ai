from pathlib import Path
from src.data.mappings import FEATURE_NAMES
ROOT=Path(__file__).resolve().parents[2]
SEED=42
THREADS=4
TARGET='heart_disease'
FORBIDDEN={'heart_disease','_MICHD','CVDINFR4','CVDCRHD4'}
FEATURE_SETS={'full_features':FEATURE_NAMES,'core_features':['age_group','sex','bmi','physical_activity','smoking_status','diabetes','kidney_disease','asthma','high_cholesterol','high_blood_pressure','alcohol_use'],'no_socioeconomic':[f for f in FEATURE_NAMES if f not in ['education','income_group']],'no_temporal_proxies':[f for f in FEATURE_NAMES if f not in ['general_health','stroke_history','difficulty_walking']]}
EXPECTED={'heart_disease_clean':(434058,398735,35323),'train':(303841,279115,24726),'validation':(65109,59810,5299),'test':(65108,59810,5298)}
