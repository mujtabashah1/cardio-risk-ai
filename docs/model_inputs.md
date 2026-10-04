# Model inputs

Derived from the unchanged authoritative `data/processed/data_dictionary.csv` and checked against the frozen schema. Exactly 14 features; no education, income, target or leakage fields. Cleaned codes only: do not send raw CDC response codes, labels, or strings. Category codes are categories, not continuous numbers.

| Field | Meaning | Type | Allowed values | Missing behavior | BRFSS source |
| --- | --- | --- | --- | --- | --- |
| age_group | What is your age? Adults 18 or older only. | strict integer category | 1: 18-24; 2: 25-29; 3: 30-34; 4: 35-39; 5: 40-44; 6: 45-49; 7: 50-54; 8: 55-59; 9: 60-64; 10: 65-69; 11: 70-74; 12: 75-79; 13: 80 or older | Omitted/null -> explicit __MISSING__ categorical token | _AGEG5YR |
| sex | What sex was recorded for you under the BRFSS respondent-sex question? | strict integer category | 1: Male; 2: Female | Omitted/null -> explicit __MISSING__ categorical token | SEXVAR |
| bmi | Enter your measured height and weight to calculate BMI. | number | Human-readable numeric BMI 12.00–99.99; no /100 conversion | Omitted/null -> saved training median BMI | _BMI5 |
| general_health | In general, would you say your health is: | strict integer category | 1: Excellent; 2: Very good; 3: Good; 4: Fair; 5: Poor | Omitted/null -> explicit __MISSING__ categorical token | GENHLTH |
| physical_activity | During the past 30 days, did you do physical activity or exercise other than your regular job? | strict integer category | 0: No activity; 1: Activity | Omitted/null -> explicit __MISSING__ categorical token | _TOTINDA |
| smoking_status | Have you smoked at least 100 cigarettes in your entire life? If yes, do you now smoke every day, some days, or not at all? | strict integer category | 1: Current every day, at least 100 lifetime cigarettes; 2: Current some days, at least 100 lifetime cigarettes; 3: Former, at least 100 lifetime cigarettes; 4: Fewer than 100 lifetime cigarettes | Omitted/null -> explicit __MISSING__ categorical token | _SMOKER3 |
| diabetes | Have you ever been told you had diabetes? If yes, was it only during pregnancy? Include a separate prediabetes/borderline option. | strict integer category | 1: Yes; 2: Only during pregnancy; 3: No; 4: Prediabetes/borderline | Omitted/null -> explicit __MISSING__ categorical token | DIABETE4 |
| stroke_history | Have you ever been told you had a stroke? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | CVDSTRK3 |
| kidney_disease | Not including kidney stones, bladder infection or incontinence, were you ever told you had kidney disease? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | CHCKDNY2 |
| asthma | Have you ever been told you had asthma? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | ASTHMA3 |
| difficulty_walking | Do you have serious difficulty walking or climbing stairs? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | DIFFWALK |
| high_cholesterol | Have you ever been told by a doctor, nurse, or other health professional that your cholesterol is high? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | TOLDHI3 |
| high_blood_pressure | Have you been told by a health professional that you have high blood pressure? Separate pregnancy-only and borderline answers map to 0. | strict integer category | 0: No, includes pregnancy-only and borderline; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | _RFHYPE6 |
| alcohol_use | During the past 30 days, did you have at least one drink of any alcoholic beverage? | strict integer category | 0: No; 1: Yes | Omitted/null -> explicit __MISSING__ categorical token | DRNKANY5 |

All predictors are optional, but the structural `profile` object must be present and nonempty; at least one known field is required, which may be null. Omitted values and explicit null are unknown, not No. Null can represent source nonresponse only after cleaning semantics have been applied. Invalid categories and malformed values are rejected, never imputed.

Smoking categories preserve the CDC 100-cigarette threshold. Diabetes preserves pregnancy-only and borderline/prediabetes separately. Hypertension uses the CDC calculated indicator; pregnancy-only/borderline categories follow its released definition. Cholesterol unknown is not automatically No. BMI bounds are the confirmed cleaning/model policy, not newly invented clinical cutoffs.
