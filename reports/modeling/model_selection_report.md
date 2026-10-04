# Model selection report

Selected experiment: gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none.

Family: catboost; feature set: no_socioeconomic; 14 inputs; calibration: none; threshold: 0.20943938.

Hyperparameters are saved exactly in model_metadata.json. Selection considered average precision first, Brier calibration, uncertainty in feature-set AP gains, removal of socioeconomic fields, threshold precision/recall/specificity, missingness checks, subgroup stability and CPU-compatible inference. It was not based on accuracy or ROC-AUC alone.

The strongest baseline families were tuned; dummy/forest and materially weaker comparisons were not heavily searched. Logistic remains a required interpretable regularization comparator. Detailed comparison rows include every successful variant and failures remain in experiment_log.csv.

| model | feature_set | device | calibration | PR_AUC | ROC_AUC | Brier | training_time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| catboost_native | no_socioeconomic | GPU | none | 0.33936 | 0.84196 | 0.06299 | 21.74378 |
| catboost_native | no_socioeconomic | GPU | sigmoid | 0.33936 | 0.84196 | 0.06474 | 9.35902 |
| catboost_native_balanced | full_features | GPU | none | 0.33883 | 0.84253 | 0.17500 | 25.32048 |
| catboost_native_balanced | full_features | GPU | sigmoid | 0.33883 | 0.84253 | 0.06347 | 10.09410 |
| catboost_native | full_features | CPU | none | 0.33880 | 0.84200 | 0.06300 | 69.02816 |
| catboost_native | full_features | CPU | none | 0.33880 | 0.84200 | 0.06300 | 74.66244 |
| catboost_native | full_features | GPU | none | 0.33850 | 0.84213 | 0.06300 | 24.95647 |
| catboost_native | full_features | GPU | none | 0.33847 | 0.84218 | 0.06300 | 24.37239 |
| catboost_native_balanced | no_socioeconomic | GPU | none | 0.33817 | 0.84240 | 0.17478 | 22.62585 |
| catboost_native_tuned | full_features | GPU | none | 0.33780 | 0.84143 | 0.06303 | 25.57088 |
| catboost_native_tuned | no_socioeconomic | GPU | none | 0.33767 | 0.84130 | 0.06305 | 23.41450 |
| catboost_native_representation | no_socioeconomic | GPU | none | 0.33760 | 0.84173 | 0.06305 | 19.01876 |

Feature comparisons and matched differences:

| model | feature_set | PR_AUC | ROC_AUC | Brier |
| --- | --- | --- | --- | --- |
| catboost_native | full_features | 0.33847 | 0.84218 | 0.06300 |
| catboost_native | core_features | 0.28263 | 0.81867 | 0.06570 |
| catboost_native | no_socioeconomic | 0.33936 | 0.84196 | 0.06299 |
| catboost_native | no_temporal_proxies | 0.28668 | 0.82167 | 0.06548 |


{
  "full_features": {
    "PR_AUC_difference_vs_full": 0.0,
    "ROC_AUC_difference_vs_full": 0.0
  },
  "core_features": {
    "PR_AUC_difference_vs_full": -0.055841205604559074,
    "ROC_AUC_difference_vs_full": -0.02350975926503618
  },
  "no_socioeconomic": {
    "PR_AUC_difference_vs_full": 0.0008917993324978335,
    "ROC_AUC_difference_vs_full": -0.00022145361298375743
  },
  "no_temporal_proxies": {
    "PR_AUC_difference_vs_full": -0.05178774890535648,
    "ROC_AUC_difference_vs_full": -0.020505917982272526
  }
}

Exploratory group-bootstrap decisions:

{
  "leading_AP_experiment": "gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none",
  "selected_experiment": "gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none",
  "best_by_feature_set": {
    "full_features": "calibrated__catboost_native_balanced__full_features__explicit_missing__default__isotonic",
    "core_features": "tuned__catboost_native_tuned__core_features__most_frequent__default__none",
    "no_socioeconomic": "gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none",
    "no_temporal_proxies": "tuned__catboost_native_tuned__no_temporal_proxies__most_frequent__default__none"
  },
  "leader_minus_core": {
    "AP_difference": 0.05553678952253088,
    "CI95_low": 0.049109164849630425,
    "CI95_high": 0.06395605298190139,
    "bootstrap_iterations": 150,
    "method": "Paired labeled-record-group bootstrap of validation predictions; exploratory, not clinical significance"
  },
  "chosen_before_socio_policy_minus_no_socio": {
    "AP_difference": 0.0,
    "CI95_low": 0.0,
    "CI95_high": 0.0,
    "bootstrap_iterations": 150,
    "method": "Paired labeled-record-group bootstrap of validation predictions; exploratory, not clinical significance"
  },
  "rule": "Favor portable core if its AP difference is not resolved by exploratory paired group-bootstrap CI; otherwise avoid socioeconomic variables when their AP gain is unresolved. Calibration minimizes validation Brier among raw/sigmoid/isotonic versions of each AP-leading raw model. Final threshold maximizes validation F1, with recall/specificity/precision tradeoffs reported. This is a research operating point, not a clinical cutoff.",
  "threshold_choices": {
    "default_0.50": 0.5,
    "maximum_validation_F1": 0.20943938491134126,
    "maximum_Youden_J": 0.08256882571678677,
    "approximately_80pct_recall": 0.08757439013898735,
    "approximately_90pct_recall": 0.045767086681139546
  }
}

No arbitrary AP margin defines portability tradeoffs. Paired validation prediction intervals quantify the actual observed difference; these intervals do not certify clinical equivalence or correct repeated-selection bias. Temporal-proxy removal is not automatically preferred when it produces a clearly resolved AP reduction for this prevalent-label objective; the selected model remains unsuitable for causal/future-risk claims.

Threshold maximizes validation F1 as a reproducible research operating point. Youden J, 0.50 and approximately 80%/90% recall alternatives document false-positive tradeoffs. No clinical cost ratio was supplied, so this threshold is not a clinical screening recommendation.

Missingness robustness:

| scenario | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | ece | TP | TN | FP | FN | threshold | rows | positive_count | positive_prevalence | note | mean_absolute_probability_change | classification_flip_percentage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_inputs_present | 0.85739 | 0.70492 | 0.31401 | 0.51978 | 0.89007 | 0.39150 | 0.83352 | 0.33866 | 0.06821 | 0.23464 | 0.00604 | 2221.00000 | 39286.00000 | 4852.00000 | 2052.00000 | 0.20944 | 48411.00000 | 4273.00000 | 0.08827 | nan | not applicable | not applicable |
| at_least_one_missing | 0.90526 | 0.70815 | 0.32041 | 0.48343 | 0.93287 | 0.38539 | 0.86218 | 0.34422 | 0.04783 | 0.17252 | 0.00479 | 496.00000 | 14620.00000 | 1052.00000 | 530.00000 | 0.20944 | 16698.00000 | 1026.00000 | 0.06144 | nan | not applicable | not applicable |
| mask_income_group | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | Not used by selected model; omission has no effect | not applicable | not applicable |
| mask_high_cholesterol | 0.88733 | 0.66675 | 0.33862 | 0.40328 | 0.93021 | 0.36813 | 0.83563 | 0.32769 | 0.06375 | 0.22258 | 0.01097 | 2137.00000 | 55636.00000 | 4174.00000 | 3162.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.01776 | 3.94723 |
| mask_bmi | 0.87693 | 0.69540 | 0.32571 | 0.47858 | 0.91222 | 0.38762 | 0.84181 | 0.33977 | 0.06289 | 0.21851 | 0.00208 | 2536.00000 | 54560.00000 | 5250.00000 | 2763.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.00609 | 1.45448 |
| mask_smoking_status | 0.86810 | 0.70453 | 0.31065 | 0.50915 | 0.89990 | 0.38587 | 0.83918 | 0.33263 | 0.06343 | 0.22025 | 0.00661 | 2698.00000 | 53823.00000 | 5987.00000 | 2601.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.01157 | 2.42056 |


Inference of 100 validation rows took 0.035414200014201924 seconds in the observed environment. No post-test refit: the exported artifact is exactly the independently evaluated frozen pipeline, preserving its calibration and threshold.

| dataset | rows | positive_count | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | TP | TN | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| validation | 65109.00000 | 5299.00000 | 0.86966 | 0.70701 | 0.31516 | 0.51274 | 0.90129 | 0.39037 | 0.84196 | 0.33936 | 0.06299 | 0.21871 | 2717.00000 | 53906.00000 | 5904.00000 | 2582.00000 |
| independent test | 65108.00000 | 5298.00000 | 0.87012 | 0.70851 | 0.31682 | 0.51548 | 0.90154 | 0.39244 | 0.84676 | 0.34479 | 0.06254 | 0.21649 | 2731.00000 | 53921.00000 | 5889.00000 | 2567.00000 |


Limitations:

- Cross-sectional, self-reported existing CHD/MI; no prospective 10-year endpoint, diagnosis validation, or temporal causality.
- BRFSS 2021 U.S. and territory respondents; generalization outside comparable populations is unknown.
- Unweighted respondent classification, not survey-weighted population prevalence estimation.
- Class imbalance, screening-dependent cholesterol status, missing values, and possible subgroup differences.
- Income nonresponse and U.S.-dollar groups reduce portability; socioeconomic and temporal-proxy fields need explicit interpretation.
- The fixed grouped split has predictor-missingness shifts (notably BMI); it was preserved unchanged.
- Repeated validation-based comparisons can overfit selection; external validation is required before clinical use.
- GPU numerical training is not guaranteed bitwise deterministic despite seed 42.
- Software-ready profile classification does not establish clinical validity.