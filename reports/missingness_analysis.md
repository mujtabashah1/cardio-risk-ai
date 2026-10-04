# Candidate missingness before row removal

| variable | valid_count | missing_count | missing_percentage | dont_know_count | refused_count | not_asked_or_missing_count | combined_unknown_refused_missing_count | other_invalid_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _AGEG5YR | 429086 | 9607 | 2.18991413129455 | 0 | 0 | 0 | 9607 | 0 |
| SEXVAR | 438693 | 0 | 0.0 | 0 | 0 | 0 | 0 | 0 |
| _BMI5 | 391841 | 46852 | 10.679905993485193 | 0 | 0 | 46852 | 0 | 0 |
| GENHLTH | 437532 | 1161 | 0.26464976646538696 | 788 | 369 | 4 | 0 | 0 |
| _TOTINDA | 437765 | 928 | 0.21153745329877613 | 0 | 0 | 0 | 928 | 0 |
| _SMOKER3 | 413723 | 24970 | 5.691907552662112 | 0 | 0 | 0 | 24970 | 0 |
| DIABETE4 | 437708 | 985 | 0.22453059428803285 | 613 | 369 | 3 | 0 | 0 |
| CVDSTRK3 | 437264 | 1429 | 0.32574032409908527 | 1130 | 297 | 2 | 0 | 0 |
| CHCKDNY2 | 436880 | 1813 | 0.4132730633951306 | 1488 | 322 | 3 | 0 | 0 |
| ASTHMA3 | 436947 | 1746 | 0.398000423986706 | 1441 | 303 | 2 | 0 | 0 |
| DIFFWALK | 418863 | 19830 | 4.520245365209839 | 1190 | 631 | 18009 | 0 | 0 |
| TOLDHI3 | 374713 | 63980 | 14.584230885835881 | 2689 | 455 | 60836 | 0 | 0 |
| _RFHYPE6 | 436781 | 1912 | 0.43584009774489224 | 0 | 0 | 0 | 1912 | 0 |
| DRNKANY5 | 408104 | 30589 | 6.972757714392524 | 3738 | 0 | 0 | 26851 | 0 |
| _EDUCAG | 436215 | 2478 | 0.5648597082697924 | 0 | 0 | 0 | 2478 | 0 |
| _INCOMG1 | 344280 | 94413 | 21.52142842488939 | 0 | 0 | 0 | 94413 | 0 |

Not-asked counts cannot be separated from ordinary missing using BLANK alone. The table therefore reports not_asked_or_missing, not a guessed count. Some calculated categories combine unknown/refused/missing; separate counts are not identifiable from that variable and are represented in the combined column. Other-invalid counts exclude documented nonresponses.

Policy: remove missing target only; retain all missing predictors as nullable values. No complete-case deletion, imputation, scaling, frequency encoding, or resampling. Later fit imputation and any missing indicators on training only, or use a model with native missing-value support. Missingness is not necessarily random (particularly cholesterol testing, BMI, income).


Sources: [CDC 2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf); [CDC calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf); [CDC dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html). Local PDFs and extracted text are in docs/.
