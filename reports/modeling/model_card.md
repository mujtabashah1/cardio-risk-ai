# Model card

## Model overview

BRFSS CHD/MI Profile Classifier 1.0.0. Research profile classifier using catboost.

## Intended use

Research/educational classification of comparable BRFSS-like adult health profiles associated with existing reported CHD/MI.

## Non-intended use

Clinical diagnosis, treatment decisions, causal risk attribution, future cardiovascular-event or 10-year/30-year risk prediction. No external clinical validation has been performed.

## Dataset

CDC BRFSS 2021; 434,058 supervised respondents from 438,693 raw rows; fixed 70/15/15 grouped and target-stratified splits. Unweighted respondent-level modeling; survey weights/design are not population-level estimates.

## Target

Existing self-reported coronary heart disease or myocardial infarction; not prospective future risk or clinical diagnosis.

## Input features

age_group, sex, bmi, general_health, physical_activity, smoking_status, diabetes, stroke_history, kidney_disease, asthma, difficulty_walking, high_cholesterol, high_blood_pressure, alcohol_use

## Data preprocessing

NativeCategories()

## Missing-value handling

BMI training median; categorical explicit Missing. Missing predictors retained. All learned transformations fit in training only. Unknown cleaned categorical values are mapped to missing with a warning; invalid types, unknown names and leakage fields are rejected.

## Class imbalance

none. Positive class approximately 8.14%; AP dummy baseline approximately 0.0814. No oversampling/undersampling or SMOTE.

## Models evaluated

catboost, dummy, hist_gradient_boosting, lightgbm, logistic, random_forest, xgboost

## Final model

gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none

## Hyperparameter tuning

{
  "tuning_catboost": {
    "best_parameters": {
      "classifier__learning_rate": 0.04,
      "classifier__iterations": 260,
      "classifier__depth": 4
    },
    "training_cv_average_precision": 0.34470101265415404,
    "runtime_seconds": 427.41806359999464,
    "rows": 60000,
    "folds": 3,
    "configurations": 18,
    "device_requested": "auto",
    "CV": "StratifiedGroupKFold on fixed training model-fit portion only; sample and grouped folds seed 42",
    "reason": "3 folds for boosted search limits sequential GPU runtime and memory; inexpensive logistic uses 5. Bounded CatBoost space contains 18 combinations; other boosted search uses 20."
  },
  "tuning_logistic": {
    "best_parameters": {
      "classifier__C": 0.1
    },
    "training_cv_average_precision": 0.3446827313635254,
    "runtime_seconds": 122.58952159999171,
    "rows": 60000,
    "folds": 5,
    "configurations": 5,
    "device_requested": "auto",
    "CV": "StratifiedGroupKFold on fixed training model-fit portion only; sample and grouped folds seed 42",
    "reason": "3 folds for boosted search limits sequential GPU runtime and memory; inexpensive logistic uses 5. Bounded CatBoost space contains 18 combinations; other boosted search uses 20."
  },
  "tuning_xgboost": {
    "best_parameters": {
      "classifier__min_child_weight": 1,
      "classifier__max_depth": 3,
      "classifier__learning_rate": 0.08
    },
    "training_cv_average_precision": 0.344336273620786,
    "runtime_seconds": 89.06311200000346,
    "rows": 60000,
    "folds": 3,
    "configurations": 20,
    "device_requested": "auto",
    "CV": "StratifiedGroupKFold on fixed training model-fit portion only; sample and grouped folds seed 42",
    "reason": "3 folds for boosted search limits sequential GPU runtime and memory; inexpensive logistic uses 5. Bounded CatBoost space contains 18 combinations; other boosted search uses 20."
  }
}

## Probability calibration

none; reserved training-only groups, selected by validation Brier.

## Classification threshold

0.20943938491134126; validation maximum F1; research operating point, not a clinical cutoff.

## Validation metrics

| dataset | rows | positive_count | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | TP | TN | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| validation | 65109.00000 | 5299.00000 | 0.86966 | 0.70701 | 0.31516 | 0.51274 | 0.90129 | 0.39037 | 0.84196 | 0.33936 | 0.06299 | 0.21871 | 2717.00000 | 53906.00000 | 5904.00000 | 2582.00000 |


## Test metrics

| dataset | rows | positive_count | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | TP | TN | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| independent test | 65108.00000 | 5298.00000 | 0.87012 | 0.70851 | 0.31682 | 0.51548 | 0.90154 | 0.39244 | 0.84676 | 0.34479 | 0.06254 | 0.21649 | 2731.00000 | 53921.00000 | 5889.00000 | 2567.00000 |
Exactly one frozen model probability vector; no post-test tuning or refit. Bootstrap confidence intervals resample cached predictions only.

## Subgroup metrics

| subgroup_feature | subgroup_value | rows | positive_count | precision | recall | specificity | f1 | roc_auc | pr_auc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sex | 1 | 30786.00000 | 3035.00000 | 0.32627 | 0.59868 | 0.86480 | 0.42236 | 0.84378 | 0.37922 |
| sex | 2 | 34323.00000 | 2264.00000 | 0.29489 | 0.39753 | 0.93287 | 0.33860 | 0.83253 | 0.28037 |
| age_group | 2 | 3060.00000 | 32.00000 | 0.41667 | 0.15625 | 0.99769 | 0.22727 | 0.77090 | 0.19644 |
| age_group | 3 | 3769.00000 | 43.00000 | 0.30435 | 0.16279 | 0.99571 | 0.21212 | 0.76185 | 0.16366 |
| age_group | 4 | 4068.00000 | 52.00000 | 0.17857 | 0.09615 | 0.99427 | 0.12500 | 0.79214 | 0.11832 |
| age_group | 5 | 4251.00000 | 99.00000 | 0.33871 | 0.21212 | 0.99013 | 0.26087 | 0.85499 | 0.23550 |
| age_group | 6 | 4121.00000 | 156.00000 | 0.38202 | 0.21795 | 0.98613 | 0.27755 | 0.82235 | 0.22757 |
| age_group | 7 | 5114.00000 | 250.00000 | 0.27490 | 0.27600 | 0.96258 | 0.27545 | 0.80488 | 0.22734 |
| age_group | 8 | 5756.00000 | 377.00000 | 0.27344 | 0.37135 | 0.93084 | 0.31496 | 0.80929 | 0.25320 |
| age_group | 9 | 6635.00000 | 596.00000 | 0.30355 | 0.44463 | 0.89932 | 0.36079 | 0.79053 | 0.32313 |
| age_group | 10 | 6906.00000 | 796.00000 | 0.29589 | 0.46985 | 0.85434 | 0.36311 | 0.76701 | 0.32116 |
| age_group | 11 | 6664.00000 | 951.00000 | 0.32820 | 0.58254 | 0.80151 | 0.41986 | 0.76218 | 0.36015 |
| age_group | 12 | 4611.00000 | 792.00000 | 0.33246 | 0.63889 | 0.73396 | 0.43734 | 0.74644 | 0.40761 |
| age_group | 13 | 5194.00000 | 1059.00000 | 0.32090 | 0.67422 | 0.63458 | 0.43484 | 0.71175 | 0.38912 |
| age_group | missing | 1233.00000 | 77.00000 | 0.30303 | 0.25974 | 0.96021 | 0.27972 | 0.78508 | 0.22381 |
Small subgroup metrics flagged unstable (n<200 or positives<30). Descriptive flags are not statistical guarantees or fairness certification; age and sex differences can reflect prevalence, self-report and selection.

## Explainability

Permutation AP decreases on 2,000 stratified validation profiles, three repeats. SHAP explains contributions to the underlying uncalibrated model output, not causal disease mechanisms or the calibration transform. Built-in tree importance and regularized logistic coefficients are additional descriptive views.

## Known limitations

- Cross-sectional, self-reported existing CHD/MI; no prospective 10-year endpoint, diagnosis validation, or temporal causality.
- BRFSS 2021 U.S. and territory respondents; generalization outside comparable populations is unknown.
- Unweighted respondent classification, not survey-weighted population prevalence estimation.
- Class imbalance, screening-dependent cholesterol status, missing values, and possible subgroup differences.
- Income nonresponse and U.S.-dollar groups reduce portability; socioeconomic and temporal-proxy fields need explicit interpretation.
- The fixed grouped split has predictor-missingness shifts (notably BMI); it was preserved unchanged.
- Repeated validation-based comparisons can overfit selection; external validation is required before clinical use.
- GPU numerical training is not guaranteed bitwise deterministic despite seed 42.
- Software-ready profile classification does not establish clinical validity.

## Ethical/portability considerations

No formal fairness certification. Screening-dependent cholesterol and structural socioeconomic factors may encode unequal access. Income groups are U.S.-specific; external validation and a separate prospective endpoint are required before clinical use.