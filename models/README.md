# Exported BRFSS CHD/MI profile classifier

Install the pinned requirements and retain the src package alongside the models directory. Use `from src.models.inference import predict_heart_disease_profile`. Supply named cleaned feature values as a dictionary or list of dictionaries, using feature_schema.json. Missing optional inputs become missing and use fitted preprocessing. Unknown feature names, target and leakage fields, numeric strings/booleans, and invalid BMI are rejected. Unseen numeric categorical codes become missing with a warning.

The helper caches the complete pipeline, calls predict_proba, and applies model_metadata.json classification_threshold. Output is a prevalent reported CHD/MI profile score, never future risk or clinical diagnosis. The artifact is the exact independently tested frozen pipeline; no post-test production refit was made.
