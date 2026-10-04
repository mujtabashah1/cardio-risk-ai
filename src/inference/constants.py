from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL_HASH='4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1'
INTEGRITY_HASH='e8737e226173ab6fcceceedd4fb8c0e3f506a11d9dd440180ede2995a1efc62f'
FEATURES=('age_group','sex','bmi','general_health','physical_activity','smoking_status','diabetes','stroke_history','kidney_disease','asthma','difficulty_walking','high_cholesterol','high_blood_pressure','alcohol_use')
PROFILE_NAMES=('research_balanced','high_sensitivity_80','high_sensitivity_90','youden','conventional_050')
DEFAULT_PROFILE='research_balanced'
DEFAULT_THRESHOLD=0.20943938491134126
MODEL_CONTEXT='This model classifies BRFSS-like health profiles associated with existing self-reported CHD/MI. It is not a medical diagnosis and does not estimate future cardiovascular-event risk.'
