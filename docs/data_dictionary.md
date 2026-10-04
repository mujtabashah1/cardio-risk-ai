# BRFSS 2021 data dictionary

17 variables: 16 predictors and one target. This documents the existing completed pipeline; no datasets were cleaned, split, or trained during dictionary recovery.

The target represents PREVALENT / EXISTING reported CHD or MI. It is NOT prospective 10-year cardiovascular risk or future disease probability.

## Leakage exclusions

`_MICHD` as an input, `CVDINFR4`, and `CVDCRHD4` must NEVER be predictors. The two diagnosis variables directly construct `_MICHD`. They are described here, not added as dictionary rows or model inputs.

Recreate documentation only: `python -m src.data.build_data_dictionary`.

## age_group (_AGEG5YR)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | 18-24 | 1 |
| 2 | 25-29 | 2 |
| 3 | 30-34 | 3 |
| 4 | 35-39 | 4 |
| 5 | 40-44 | 5 |
| 6 | 45-49 | 6 |
| 7 | 50-54 | 7 |
| 8 | 55-59 | 8 |
| 9 | 60-64 | 9 |
| 10 | 65-69 | 10 |
| 11 | 70-74 | 11 |
| 12 | 75-79 | 12 |
| 13 | 80 or older | 13 |
| 14 | Don't know/Refused/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: What is your age? Adults 18 or older only.

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: ordinal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: What is your age? Adults 18 or older only.

**allowed user answers**: ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80 or older", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12, "13": 13, "14": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], plus missing. No global 7/9/77/88/99 recoding. If age is entered numerically, require an adult age and apply the documented bins; 80 or older maps to 13.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=145; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## sex (SEXVAR)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Male | 1 |
| 2 | Female | 2 |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: What sex was recorded for you under the BRFSS respondent-sex question?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: What is your sex? Select Male or Female using the BRFSS respondent-sex categories.

**allowed user answers**: ["Male", "Female", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=19; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## bmi (_BMI5)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1-9999 | BMI with two implied decimal places | Divide by 100 only for integer values 1200..9999; otherwise missing |
| BLANK | Don't know/Refused/Missing | missing (null) |

**role**: predictor

**description**: Enter your measured height and weight to calculate BMI.

**missing value rule**: SAS missing/blank and released values outside [1200,9999] or noninteger -> missing; no new outlier removal.

**data type**: Float64 (nullable continuous)

**feature type**: continuous numeric

**ordinal or nominal**: continuous

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires measurement; numeric BMI or calculated from height/weight

**user facing question**: Enter your measured height and weight to calculate BMI.

**allowed user answers**: Measured height and weight, or directly supplied BMI; unknown/skipped -> missing

**internal encoding**: BMI = weight_kg / height_metres**2; released _BMI5 / 100. Store human-readable BMI, not the scaled CDC integer.

**validation rules**: Pipeline accepts integer released _BMI5 in [1200,9999], yielding BMI in [12.00,99.99]; other values become missing. Do not clamp or add outlier-removal rules. Height/weight inputs must be positive, finite and unit-labelled; accept BMI to two decimal places.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=149; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness. CDC construction code limits BMI to 12.00-99.99; release code multiplies by 100. Existing review flags were descriptive only, not removals.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## general_health (GENHLTH)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Excellent | 1 |
| 2 | Very good | 2 |
| 3 | Good | 3 |
| 4 | Fair | 4 |
| 5 | Poor | 5 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: In general, would you say your health is:

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: ordinal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: In general, would you say your health is:

**allowed user answers**: ["Excellent", "Very good", "Good", "Fair", "Poor", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4, 5], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain provisionally: may reflect consequences of existing CHD/MI; unsuitable for causal or future-risk interpretation.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=19; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain provisionally: may reflect consequences of existing CHD/MI; unsuitable for causal or future-risk interpretation.

## physical_activity (_TOTINDA)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Activity | 1 |
| 2 | No activity | 0 |
| 9 | Don't know/Refused/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: During the past 30 days, did you do physical activity or exercise other than your regular job?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: During the past 30 days, did you do physical activity or exercise other than your regular job?

**allowed user answers**: ["Activity", "No activity", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=134; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## smoking_status (_SMOKER3)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Current every day, at least 100 lifetime cigarettes | 1 |
| 2 | Current some days, at least 100 lifetime cigarettes | 2 |
| 3 | Former, at least 100 lifetime cigarettes | 3 |
| 4 | Fewer than 100 lifetime cigarettes | 4 |
| 9 | Don't know/Refused/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: Have you smoked at least 100 cigarettes in your entire life? If yes, do you now smoke every day, some days, or not at all?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: Have you smoked at least 100 cigarettes in your entire life? If yes, do you now smoke every day, some days, or not at all?

**allowed user answers**: ["Current every day, at least 100 lifetime cigarettes", "Current some days, at least 100 lifetime cigarettes", "Former, at least 100 lifetime cigarettes", "Fewer than 100 lifetime cigarettes", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=153; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness. Category 4 is CDC Never smoked: fewer than 100 lifetime cigarettes, not necessarily zero. For >=100 lifetime cigarettes, current every-day/some-day/not-at-all maps to 1/2/3.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## diabetes (DIABETE4)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | Only during pregnancy | 2 |
| 3 | No | 3 |
| 4 | Prediabetes/borderline | 4 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Have you ever been told you had diabetes? If yes, was it only during pregnancy? Include a separate prediabetes/borderline option.

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Have you ever been told you had diabetes? If yes, was it only during pregnancy? Include a separate prediabetes/borderline option.

**allowed user answers**: ["Yes", "Only during pregnancy", "No", "Prediabetes/borderline", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=32; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness. Preserve 1 Yes, 2 pregnancy-only, 3 No, and 4 prediabetes/borderline separately; do not binarize.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## stroke_history (CVDSTRK3)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Have you ever been told you had a stroke?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Have you ever been told you had a stroke?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain provisionally: distinct diagnosis from CHD/MI; shared vascular disease and temporal ordering are unresolved.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=28; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain provisionally: distinct diagnosis from CHD/MI; shared vascular disease and temporal ordering are unresolved.

## kidney_disease (CHCKDNY2)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Not including kidney stones, bladder infection or incontinence, were you ever told you had kidney disease?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Not including kidney stones, bladder infection or incontinence, were you ever told you had kidney disease?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=32; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## asthma (ASTHMA3)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Have you ever been told you had asthma?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Have you ever been told you had asthma?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=29; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## difficulty_walking (DIFFWALK)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Do you have serious difficulty walking or climbing stairs?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: Do you have serious difficulty walking or climbing stairs?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain provisionally: may reflect consequences of existing cardiovascular disease.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=45; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain provisionally: may reflect consequences of existing cardiovascular disease.

## high_cholesterol (TOLDHI3)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused | missing (null) |
| BLANK | Not asked or Missing | missing (null) |

**role**: predictor

**description**: Have you ever been told by a doctor, nurse, or other health professional that your cholesterol is high?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Have you ever been told by a doctor, nurse, or other health professional that your cholesterol is high?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain provisionally: prior testing needed; not a numeric laboratory result. Screening-dependent missingness.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=26; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness. Requires known professional diagnosis after testing; not tested/unknown must never become No.

**reason for inclusion or exclusion**: Retain provisionally: prior testing needed; not a numeric laboratory result. Screening-dependent missingness.

## high_blood_pressure (_RFHYPE6)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | No, includes pregnancy-only and borderline | 0 |
| 2 | Yes | 1 |
| 9 | Don't know/Not sure/Refused/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: Have you been told by a health professional that you have high blood pressure? Separate pregnancy-only and borderline answers map to 0.

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: requires known medical history; single choice

**user facing question**: Have you ever been told by a doctor, nurse, or other health professional that you have high blood pressure? Was this only during pregnancy, or were you told you had borderline high blood pressure or prehypertension?

**allowed user answers**: ["Yes", "Yes, only during pregnancy", "No", "Borderline high blood pressure or prehypertension", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"CDC released-code mapping": {"1": 0, "2": 1, "9": null, "BLANK": null}, "mobile-answer mapping": {"Yes": 1, "Yes, only during pregnancy": 0, "No": 0, "Borderline high blood pressure or prehypertension": 0, "Don't know": null, "Prefer not to answer": null, "Skipped/not provided": null}}

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=134; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness. Source BPHIGH6=1 -> 1; BPHIGH6=2 (pregnancy-only), 3 (No), or 4 (borderline/prehypertensive) -> 0. Unknown/refused/missing -> missing.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## alcohol_use (DRNKANY5)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Yes | 1 |
| 2 | No | 0 |
| 7 | Don't know/Not sure | missing (null) |
| 9 | Refused/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: During the past 30 days, did you have at least one drink of any alcoholic beverage?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: nominal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: During the past 30 days, did you have at least one drink of any alcoholic beverage?

**allowed user answers**: ["Yes", "No", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 0, "7": null, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [0, 1], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=154; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## education (_EDUCAG)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Did not graduate high school | 1 |
| 2 | Graduated high school | 2 |
| 3 | Attended college/technical school | 3 |
| 4 | Graduated college/technical school | 4 |
| 9 | Don't know/Not sure/Missing | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: What is the highest level of education you completed?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: ordinal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: What is the highest level of education you completed?

**allowed user answers**: ["Did not graduate high school", "Graduated high school", "Attended college/technical school", "Graduated college/technical school", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain: documented, available questionnaire input.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=151; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain: documented, available questionnaire input.

## income_group (_INCOMG1)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Household annual income below $15,000 | 1 |
| 2 | $15,000 to below $25,000 | 2 |
| 3 | $25,000 to below $35,000 | 3 |
| 4 | $35,000 to below $50,000 | 4 |
| 5 | $50,000 to below $100,000 | 5 |
| 6 | $100,000 to below $200,000 | 6 |
| 7 | $200,000 or more | 7 |
| 9 | Don't know/Not sure/Missing (source INCOME3: 77 unknown, 99 refused, or missing) | missing (null) |
| BLANK | SAS missing input; no separate BLANK category listed in this CDC table | missing (null) |

**role**: predictor

**description**: What is your annual household income from all sources in US dollars?

**missing value rule**: Documented nonresponse codes and SAS missing/blank -> missing; rows retained when target usable. Unexpected categorical codes fail; no full-data imputation.

**data type**: Int8 (nullable categorical)

**feature type**: categorical

**ordinal or nominal**: ordinal

**used in model**: True

**used in mobile app**: True

**mobile input type**: easy user input; single choice

**user facing question**: What is your annual household income from all sources in US dollars?

**allowed user answers**: ["Household annual income below $15,000", "$15,000 to below $25,000", "$25,000 to below $35,000", "$35,000 to below $50,000", "$50,000 to below $100,000", "$100,000 to below $200,000", "$200,000 or more", "Don't know", "Prefer not to answer", "Skipped/not provided"]

**internal encoding**: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "9": null, "BLANK": null}; mobile nonresponse -> null (not a learned or imputed category)

**validation rules**: Only documented original codes are accepted; unexpected nonmissing codes fail cleaning. Clean domain: [1, 2, 3, 4, 5, 6, 7], plus missing. No global 7/9/77/88/99 recoding.

**reason for inclusion**: Retain provisionally despite high missingness: optional socioeconomic input; fairness and geographic/price portability require review.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=152; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: No imputation was performed. Blank and combined nonresponse categories cannot distinguish individual reasons for missingness.

**reason for inclusion or exclusion**: Retain provisionally despite high missingness: optional socioeconomic input; fairness and geographic/price portability require review.

## heart_disease (_MICHD)

| Original code | CDC meaning / missing-input description | Cleaned representation |
| --- | --- | --- |
| 1 | Reported having MI or CHD | 1 |
| 2 | Did not report having MI or CHD | 0 |
| BLANK | Not asked or Missing; target unavailable | EXCLUDE ROW |

**role**: target

**description**: PREVALENT / EXISTING reported coronary heart disease or myocardial infarction; not a prospective 10-year cardiovascular-risk label or future disease probability.

**missing value rule**: Missing/unusable target is excluded from supervised rows. Unexpected nonmissing _MICHD codes cause the existing pipeline to fail, rather than guess or silently recode.

**data type**: Int8 (non-null binary label)

**feature type**: binary target

**ordinal or nominal**: binary nominal

**used in model**: True

**used in mobile app**: False

**mobile input type**: not a questionnaire/model input

**user facing question**: Not applicable: supervised target, never an input.

**allowed user answers**: Not applicable

**internal encoding**: _MICHD = 1 -> heart_disease = 1 (reported CHD/MI); _MICHD = 2 -> heart_disease = 0 (did not report CHD/MI); missing/unusable target -> excluded from supervised dataset. Unexpected nonmissing codes fail cleaning.

**validation rules**: heart_disease must contain only 0 or 1 and never be missing. _MICHD, CVDINFR4 and CVDCRHD4 must never become predictors.

**reason for inclusion**: Supervised label only; excluded from predictors.

**source document**: https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf#page=136; https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf

**notes**: CDC derives _MICHD=1 if CVDINFR4=1 OR CVDCRHD4=1; =2 if both equal 2; otherwise missing. Positive diagnosis takes precedence over unknown in the other source. used_in_model=True denotes target use only, never predictor use. No model has been trained.

**reason for inclusion or exclusion**: Supervised label only; excluded from predictors.

## Saved dataset checks

- heart_disease_clean: 434058 rows; all 17 columns and allowed values verified.
- train: 303841 rows; all 17 columns and allowed values verified.
- validation: 65109 rows; all 17 columns and allowed values verified.
- test: 65108 rows; all 17 columns and allowed values verified.

BLANK descriptions for variables without a separate codebook BLANK category describe existing pipeline missing-input handling; they do not invent a new CDC response code. Mobile skipped/refused options similarly become null, not additional model categories.
