# Frozen pipeline audit

SHA-256: `4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1`. Model version 1.0.0 and all frozen sources match. Official test probabilities and metrics reproduce within 1e-12. One explicitly requested reproduction prediction was made without changing historical reports or making model decisions.

FeatureGuard reorders the 14 named numeric/null inputs. The historical guard maps unsupported categorical codes to missing with warnings; the serving boundary instead rejects invalid codes. BMI is human-readable, restricted to the saved 12–99.99 policy, and never divided by 100.

NativeCategories fills BMI with model-fit training median **27.41**. Category codes become integer strings; nulls become `__MISSING__`. No statistic is newly fitted. Native CatBoost has 220 iterations, depth 6 and learning rate 0.08, without class weights. `predict_proba` column 1 corresponds to target class 1. No calibrator is added. Profiles compare the same full-precision score using `>=`.

Expected order: age_group, sex, bmi, general_health, physical_activity, smoking_status, diabetes, stroke_history, kidney_disease, asthma, difficulty_walking, high_cholesterol, high_blood_pressure, alcohol_use
