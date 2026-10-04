# Calibration report

Calibrators were fit on reserved training-only exact-record groups disjoint from base-model fit and preprocessing. FrozenEstimator prevents refitting the base model. Validation compares raw, sigmoid and isotonic; no test calibration.

| feature_set | method | selected | brier | log_loss | ece | pr_auc | roc_auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_features | none | False | 0.17500 | 0.51156 | 0.27288 | 0.33883 | 0.84253 |
| full_features | sigmoid | False | 0.06347 | 0.22017 | 0.01170 | 0.33883 | 0.84253 |
| full_features | isotonic | True | 0.06312 | 0.22075 | 0.00732 | 0.32736 | 0.84218 |
| core_features | none | True | 0.06564 | 0.22925 | 0.00473 | 0.28382 | 0.81869 |
| core_features | sigmoid | False | 0.06735 | 0.23827 | 0.01373 | 0.28382 | 0.81869 |
| core_features | isotonic | False | 0.06573 | 0.23039 | 0.00631 | 0.27344 | 0.81838 |
| no_socioeconomic | none | True | 0.06299 | 0.21871 | 0.00545 | 0.33936 | 0.84196 |
| no_socioeconomic | sigmoid | False | 0.06474 | 0.22889 | 0.01645 | 0.33936 | 0.84196 |
| no_socioeconomic | isotonic | False | 0.06313 | 0.22060 | 0.00734 | 0.32635 | 0.84156 |
| no_temporal_proxies | none | True | 0.06542 | 0.22819 | 0.00497 | 0.28771 | 0.82141 |
| no_temporal_proxies | sigmoid | False | 0.06713 | 0.23744 | 0.01424 | 0.28771 | 0.82141 |
| no_temporal_proxies | isotonic | False | 0.06556 | 0.23043 | 0.00630 | 0.27788 | 0.82098 |


Chosen method: none. The choice minimizes observed validation Brier among corresponding model versions; small differences are not asserted to be clinically meaningful. Quantile-bin curves show average predicted score against observed CHD/MI frequency. ECE uses 10 equal-width probability bins, weighted by observed bin size and absolute frequency-score gaps; this binning-dependent statistic is secondary. The model score concerns existing reported CHD/MI, never future-event probability.


Implementation references: [sklearn calibration and disjoint fit/calibration](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html), [XGBoost GPU configuration](https://xgboost.readthedocs.io/en/stable/gpu/), [CatBoost Tree SHAP](https://catboost.ai/docs/en/concepts/python-reference_catboostclassifier_get_feature_importance), [LightGBM Windows GPU builds](https://lightgbm.readthedocs.io/en/stable/Installation-Guide.html).
