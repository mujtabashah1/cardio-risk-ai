# Cleaning report

| metric | value |
| --- | --- |
| original_rows | 438693.0 |
| original_columns | 303.0 |
| cleaned_rows | 434058.0 |
| cleaned_columns | 17.0 |
| rows_removed | 4635.0 |
| percentage_retained | 98.9434524827157 |
| final_predictor_count | 16.0 |
| positive_count | 35323.0 |
| negative_count | 398735.0 |
| positive_percentage | 8.137852545051583 |
| original_feature_count | 302.0 |
| candidate_feature_count | 16.0 |

Target: reported existing CHD or MI from _MICHD; 1 -> 1, 2 -> 0. This is not a future-risk label.

Candidates: _AGEG5YR, SEXVAR, _BMI5, GENHLTH, _TOTINDA, _SMOKER3, DIABETE4, CVDSTRK3, CHCKDNY2, ASTHMA3, DIFFWALK, TOLDHI3, _RFHYPE6, DRNKANY5, _EDUCAG, _INCOMG1

Final predictors: age_group, sex, bmi, general_health, physical_activity, smoking_status, diabetes, stroke_history, kidney_disease, asthma, difficulty_walking, high_cholesterol, high_blood_pressure, alcohol_use, education, income_group.

Exclusions: every raw column outside the selected 16 predictors and target. Direct leakage exclusions: _MICHD as input, CVDINFR4, CVDCRHD4. No requested candidate permanently removed; all are provisional.

CDC mappings and code-level nonresponse rules are recorded in data_dictionary.csv and src/data/mappings.py. Diabetes retains four meaningful categories. Smoking retains the 100-cigarette lifetime threshold; category 4 is not literally zero lifetime cigarettes. Hypertension No includes pregnancy-only/borderline. No global 7/9/77/99 recoding.

Row removal ledger: raw 438693; missing/unusable target removed 4635; predictor-missing rows removed 0; duplicates removed 0; final 434058. Equal projected records retained as distinct people; no source row was duplicated.

BMI: CDC codebook confirms two implied decimal places; calculated-variable SAS code explicitly multiplies BMI by 100 for release. Divide by 100. CDC construction bounds are 12.00 to 99.99; undocumented integer/range values become missing and are separately listed. Invalid count: 0.

| statistic | bmi |
| --- | --- |
| count | 391841.0 |
| mean | 28.552264949303417 |
| std | 6.551949766699135 |
| min | 12.0 |
| 1% | 17.85 |
| 5% | 20.18 |
| 25% | 24.14 |
| 50% | 27.44 |
| 75% | 31.74 |
| 95% | 40.69 |
| 99% | 49.6 |
| max | 99.33 |

Descriptive review flags below 15 or above 60: 1118; retained, not claimed to be impossible. Flags are an audit heuristic, not a clinical cutoff. Valid extremes are never automatically removed.

Missing predictors retained; imputation/encoding/scaling/balancing and learned feature selection must be fit on training only.

Split: seed 42; randomized identical-record groups allocated within each target class to 70/15/15 row quotas. Largest groups assigned first; ties shuffled. Small group-size rounding differences are possible. Pairwise source-row and exact labeled-record intersections verified empty; union and row counts reconcile. Membership is in split_membership.csv, never a predictor.

| dataset | target | count | percentage | dataset_rows |
| --- | --- | --- | --- | --- |
| full_cleaned | 0 | 398735 | 91.862147 | 434058 |
| full_cleaned | 1 | 35323 | 8.137853 | 434058 |
| train | 0 | 279115 | 91.862191 | 303841 |
| train | 1 | 24726 | 8.137809 | 303841 |
| validation | 0 | 59810 | 91.86134 | 65109 |
| validation | 1 | 5299 | 8.13866 | 65109 |
| test | 0 | 59810 | 91.862751 | 65108 |
| test | 1 | 5298 | 8.137249 | 65108 |

Validation: {"passed": true, "source_ids_unique": true, "projected_duplicates": 22401, "rows": 434058, "saved_csv_parquet_and_split_roundtrips_verified": true, "split_source_intersections_empty": true, "split_exact_labeled_record_intersections_empty": true, "split_union_complete": true, "target_derivation_verified": true}.

Reproducibility: raw/ZIP SHA-256 recorded and checked before/after build; output SHA-256 manifest generated. Two builds must match deterministically.

Unresolved concerns: USEMRJN3 is unselected and lacks a definition in the downloaded codebook (see all_variable_leakage_audit.csv); cross-sectional timing, self-reported diagnoses, sampling/design weights, reporting-area coverage, representation, income fairness/nonresponse and cholesterol-screening missingness. This dataset is ready for a reproducible baseline training pipeline that handles missing values, not for clinically validated future-risk deployment. No model has been trained.


Sources: [CDC 2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf); [CDC calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf); [CDC dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html). Local PDFs and extracted text are in docs/.
