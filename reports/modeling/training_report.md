# Training report

Purpose: classify profiles associated with EXISTING reported CHD/MI in CDC BRFSS 2021. No future-risk endpoint or clinical diagnosis is modeled.

Verified dimensions: cleaned 434,058 x 17; train 303,841 x 17; validation 65,109 x 17; test 65,108 x 17. Class counts match the required fixed split. Test features were used initially only for requested schema/count/membership integrity checks; test predictions were made once after freeze. No datasets or CDC mappings changed.

Hardware: 11th Gen Intel(R) Core(TM) i7-11850H @ 2.50GHz; 16 logical CPUs; RAM 15.73 GiB; GPU NVIDIA T1200 Laptop GPU, 4096 MiB; driver 610.60. Driver CUDA compatibility 13.3; this is not an independently detected runtime. XGBoost compiled CUDA details and toolkit detection are in hardware_environment.json.

GPU fit probes succeeded for XGBoost and CatBoost. Installed LightGBM lacks a GPU learner; its exact error was saved and CPU fallback was used without rebuilding libraries. GPU fits were sequential, 4 CPU threads, depth/bins/VRAM conservative.

Original training rows were partitioned by randomized, target-stratified exact labeled-record groups: 242,904 model-fit rows and 60,937 calibration-only rows. No group crosses those roles. Base estimators and preprocessing use only model-fit rows; sigmoid/isotonic calibration uses only the reserved training rows. No refit on validation or test was performed.

BMI: training median; scaled for logistic only. Categorical primary: training most frequent + one-hot, including ordinal fields. Alternatives: explicit Missing category, native categorical CatBoost, and separately labeled ordinal numeric comparison. Diabetes remains four categories; smoking remains nominal and preserves the 100-cigarette threshold. Categorical missingness under modal imputation is a statistical assumption, not a recorded No diagnosis; the explicit missing experiment is reported separately.

Families: Dummy (most frequent/prior), logistic (unweighted/balanced), random forest (unweighted/balanced), HistGradientBoosting, XGBoost (unweighted/training ratio), LightGBM (unweighted/balanced), and CatBoost (native, one-hot, native balanced). No resampling, SMOTE, or neural network. XGBoost weighting 11.282767 uses only model-fit training frequencies.

Feature configurations: full_features (16), core_features (11), no_socioeconomic (14), no_temporal_proxies (13). Earlier mobile_core experiments are retained as the historical name for the identical 11-feature core; not a fifth distinct feature configuration.

Tuning results: {
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

Leading two boosted families were screened by validation AP; train-only RandomizedSearchCV then used a fixed 60,000-row stratified model-fit sample and grouped folds. All preprocessing is refit within each fold. Three folds bound GPU runtime; logistic regularization uses five folds. Selected settings refit the full model-fit partition. This is a bounded search, not proof of global optimum.

| model | feature_set | device | PR_AUC | ROC_AUC | F1 | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| catboost_native | no_socioeconomic | GPU | 0.33936 | 0.84196 | 0.24406 | 0.06474 |
| catboost_native_balanced | full_features | GPU | 0.33883 | 0.84253 | 0.32320 | 0.17500 |
| catboost_native_tuned | no_temporal_proxies | GPU | 0.28771 | 0.82141 | 0.17852 | 0.06713 |
| catboost_native_tuned | core_features | GPU | 0.28382 | 0.81869 | 0.16795 | 0.06735 |

Completed fits: 103; recorded failed fits: 0. Sum of measured fit/calibration experiment runtimes plus completed tuning: 1794.5s, excluding interrupted work and analysis overhead. Separate preprocessing/model/calibration times are recorded where measured; historical CPU runs have only total time, not invented timing breakdowns.

| model | CPU_model_fit_seconds | GPU_model_fit_seconds | model_fit_speedup | CPU_total_seconds | GPU_total_seconds |
| --- | --- | --- | --- | --- | --- |
| catboost_native | 62.36420 | 18.07922 | 3.44950 | 69.02816 | 24.95647 |
| xgboost_none | 3.17803 | 1.45516 | 2.18397 | 7.63591 | 5.85645 |

Failure record:

No recorded fit failures.

CPU screening was checkpoint-resumed after launcher inspection and after the GPU-first request arrived. A training-only search was restarted to correct the native-category flag before tuned refits. Completed experiment rows were preserved; incomplete attempts have no fabricated metrics. Events are recorded in interrupted_runs.json.

The original fixed split has unequal missingness patterns: BMI missingness is approximately 12.13% train, 6.99% validation and 6.94% test. Group-based split allocation is not equivalent to unrestricted IID row splitting; this limitation is preserved and disclosed.


Implementation references: [sklearn calibration and disjoint fit/calibration](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html), [XGBoost GPU configuration](https://xgboost.readthedocs.io/en/stable/gpu/), [CatBoost Tree SHAP](https://catboost.ai/docs/en/concepts/python-reference_catboostclassifier_get_feature_importance), [LightGBM Windows GPU builds](https://lightgbm.readthedocs.io/en/stable/Installation-Guide.html).
