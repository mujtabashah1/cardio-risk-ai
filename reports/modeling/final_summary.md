# Final modeling summary

| dataset | rows | positive_count | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | TP | TN | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| validation | 65109.00000 | 5299.00000 | 0.86966 | 0.70701 | 0.31516 | 0.51274 | 0.90129 | 0.39037 | 0.84196 | 0.33936 | 0.06299 | 0.21871 | 2717.00000 | 53906.00000 | 5904.00000 | 2582.00000 |
| independent test | 65108.00000 | 5298.00000 | 0.87012 | 0.70851 | 0.31682 | 0.51548 | 0.90154 | 0.39244 | 0.84676 | 0.34479 | 0.06254 | 0.21649 | 2731.00000 | 53921.00000 | 5889.00000 | 2567.00000 |


Selected: gpu_baseline__catboost_native__no_socioeconomic__most_frequent__default__none

Feature set: no_socioeconomic; calibration none; threshold 0.20943938491134126.

| model | CPU_model_fit_seconds | GPU_model_fit_seconds | model_fit_speedup | CPU_total_seconds | GPU_total_seconds |
| --- | --- | --- | --- | --- | --- |
| catboost_native | 62.36420 | 18.07922 | 3.44950 | 69.02816 | 24.95647 |
| xgboost_none | 3.17803 | 1.45516 | 2.18397 | 7.63591 | 5.85645 |


Matched feature effects:

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

Top permutation contributions:

| feature | permutation_AP_decrease | permutation_std |
| --- | --- | --- |
| age_group | 0.07724 | 0.00586 |
| general_health | 0.07684 | 0.01101 |
| stroke_history | 0.04832 | 0.00792 |
| sex | 0.04131 | 0.00273 |
| high_cholesterol | 0.02439 | 0.00929 |
| high_blood_pressure | 0.02342 | 0.00431 |
| smoking_status | 0.01808 | 0.00392 |
| diabetes | 0.00998 | 0.00291 |


Missingness:

| scenario | accuracy | balanced_accuracy | precision | recall | specificity | f1 | roc_auc | pr_auc | brier | log_loss | ece | TP | TN | FP | FN | threshold | rows | positive_count | positive_prevalence | note | mean_absolute_probability_change | classification_flip_percentage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_inputs_present | 0.85739 | 0.70492 | 0.31401 | 0.51978 | 0.89007 | 0.39150 | 0.83352 | 0.33866 | 0.06821 | 0.23464 | 0.00604 | 2221.00000 | 39286.00000 | 4852.00000 | 2052.00000 | 0.20944 | 48411.00000 | 4273.00000 | 0.08827 | nan | not applicable | not applicable |
| at_least_one_missing | 0.90526 | 0.70815 | 0.32041 | 0.48343 | 0.93287 | 0.38539 | 0.86218 | 0.34422 | 0.04783 | 0.17252 | 0.00479 | 496.00000 | 14620.00000 | 1052.00000 | 530.00000 | 0.20944 | 16698.00000 | 1026.00000 | 0.06144 | nan | not applicable | not applicable |
| mask_income_group | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | not applicable | Not used by selected model; omission has no effect | not applicable | not applicable |
| mask_high_cholesterol | 0.88733 | 0.66675 | 0.33862 | 0.40328 | 0.93021 | 0.36813 | 0.83563 | 0.32769 | 0.06375 | 0.22258 | 0.01097 | 2137.00000 | 55636.00000 | 4174.00000 | 3162.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.01776 | 3.94723 |
| mask_bmi | 0.87693 | 0.69540 | 0.32571 | 0.47858 | 0.91222 | 0.38762 | 0.84181 | 0.33977 | 0.06289 | 0.21851 | 0.00208 | 2536.00000 | 54560.00000 | 5250.00000 | 2763.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.00609 | 1.45448 |
| mask_smoking_status | 0.86810 | 0.70453 | 0.31065 | 0.50915 | 0.89990 | 0.38587 | 0.83918 | 0.33263 | 0.06343 | 0.22025 | 0.00661 | 2698.00000 | 53823.00000 | 5987.00000 | 2601.00000 | 0.20944 | 65109.00000 | 5299.00000 | 0.08139 | nan | 0.01157 | 2.42056 |


See model_card.md for subgroup details and complete limitations. Software-ready export is not clinically validated future-risk prediction. All 52 requested summary fields are represented in final_summary.json and the detailed reports.
