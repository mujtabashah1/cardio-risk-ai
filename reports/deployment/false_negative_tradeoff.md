# False-negative threshold tradeoff

## Overview

The existing CatBoost model 1.0.0 is frozen and unchanged. No retraining, tuning, recalibration or new threshold selection occurred. This report reuses its cached validation probabilities (65,109 rows; 5,299 positives; 59,810 negatives) and the previously selected validation thresholds. Test data was not used for threshold optimization, and no test inference was run in this task.

| Profile | Threshold | Recall | False negative rate | FN | TP | Precision | Specificity | FP | F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| research_balanced | 0.20943938491134126 | 51.27% | 48.73% | 2582 | 2717 | 31.52% | 90.13% | 5904 | 0.39037 |
| youden | 0.08256882571678677 | 81.30% | 18.70% | 991 | 4308 | 20.31% | 71.74% | 16903 | 0.32501 |
| high_sensitivity_80 | 0.08757439013898735 | 80.00% | 20.00% | 1060 | 4239 | 20.76% | 72.95% | 16177 | 0.32969 |
| high_sensitivity_90 | 0.045767086681139546 | 90.00% | 10.00% | 530 | 4769 | 16.39% | 59.33% | 24327 | 0.27731 |
| conventional_050 | 0.5 | 8.66% | 91.34% | 4840 | 459 | 57.16% | 99.42% | 344 | 0.15044 |

## Current default

`research_balanced` retains threshold 0.20943938491134126. TP 2,717, FN 2,582, recall 51.27%, false-negative rate 48.73%, FP 5,904, precision 31.52%, specificity 90.13%, F1 0.39037. **2,582 of 5,299 validation positives are missed**. Historical independent-test recall was 51.55% (2,567 missed positives), so roughly half of positive reported CHD/MI records were missed by the default binary operating point.

## Approximately 80% recall

Threshold 0.08757439013898735; TP 4,239, FN 1,060, recall 80.00%, false-negative rate 20.00%, precision 20.76%, specificity 72.95%, FP 16,177, F1 0.32969.

Compared with the default, this captures **1,522 additional positives**, avoids **1,522 false negatives**, and produces **10,273 additional false positives**. Precision changes by -10.75 percentage points, specificity by -17.18 points, and F1 by -0.06068. Remaining missed positives: 1,060.

## Approximately 90% recall

Threshold 0.045767086681139546; TP 4,769, FN 530, recall 90.00%, false-negative rate 10.00%, precision 16.39%, specificity 59.33%, FP 24,327, F1 0.27731.

Compared with the default, this captures **2,052 additional positives**, avoids **2,052 false negatives**, and produces **18,423 additional false positives**. Precision changes by -15.13 percentage points, specificity by -30.80 points, and F1 by -0.11307. Remaining missed positives: 530.

## Youden threshold

Youden J = sensitivity + specificity - 1. This previously selected validation criterion balances two statistical rates, not medical consequences. Its threshold and all counts/rates are in the comparison table and CSV. It is not a medical cutoff.

## 0.50 threshold

This is a conventional reference only. It misses 4,840 of 5,299 validation positives (recall 8.66%), despite reducing false positives to 344. A conventional probability threshold is not automatically appropriate.

## Recommendation

Retain research_balanced as the API default. The ~80% and ~90% profiles support explicitly requested sensitivity-oriented research objectives, recovering positives at substantial false-positive and precision costs. No clinical threshold is selected or recommended. External clinical validation and a defined cost/benefit framework are required before choosing a clinical screening operating point. The model describes existing self-reported CHD/MI associations, not a diagnosis or future risk.

## Verification

For all five rows: TP + FN = 5,299; TN + FP = 59,810; all four counts total 65,109. Metrics were recomputed from cached validation scores and cross-checked against the unchanged threshold analysis. False-negative rate = FN/5,299; false-positive rate = FP/59,810. Probability stays identical between profiles; only threshold-based classification changes.
