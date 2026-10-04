# Research threshold policies

All values and metrics come from the existing selected-model validation rows in `reports/modeling/threshold_analysis.csv`, parsed with round-trip float precision. No thresholds were derived from test data.

| Profile | Threshold | Precision | Recall | Specificity | F1 | TP | TN | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| research_balanced | 0.20943938491134126 | 0.315161 | 0.512738 | 0.901287 | 0.390374 | 2717 | 53906 | 5904 | 2582 |
| high_sensitivity_80 | 0.08757439013898735 | 0.207631 | 0.799962 | 0.729527 | 0.329691 | 4239 | 43633 | 16177 | 1060 |
| high_sensitivity_90 | 0.045767086681139546 | 0.163906 | 0.899981 | 0.593262 | 0.277308 | 4769 | 35483 | 24327 | 530 |
| youden | 0.08256882571678677 | 0.203102 | 0.812984 | 0.717388 | 0.325009 | 4308 | 42907 | 16903 | 991 |
| conventional_050 | 0.5 | 0.571606 | 0.086620 | 0.994248 | 0.150442 | 459 | 59466 | 344 | 4840 |

The default `research_balanced` threshold maximized validation F1. `youden` maximized sensitivity + specificity − 1. The ~80%/~90% profiles target validation recall, without any claim of medically optimal performance. `conventional_050` is a reference only. Lower thresholds recover more positives and increase false positives; higher thresholds reduce false positives and miss more positives.

These are research operating policies, not clinical cutoffs. The raw CatBoost score is identical for all named policies. Thresholding uses full internal precision and `score >= threshold`; JSON scores are rounded to six decimals only after classification. Clients must use the returned classification rather than reconstructing it from the displayed score. Numeric caller-defined thresholds and subgroup-specific thresholds are not accepted.

Independent-test default recall was 51.55% (2,567 of 5,298 positives missed), precision 31.68% (5,889 of 8,620 elevated classifications were target-negative). ROC-AUC 0.84676; average precision 0.34479; positive prevalence 8.137%. These results do not establish diagnostic validity. Alternative-profile metrics above are validation metrics; no new test comparisons were made.
