# Feature selection before exclusions

All 16 requested candidates are present and documented. Retained deterministically for a baseline prevalence-classification dataset; no target-association selection was performed. No candidate is permanently excluded. Missingness alone does not justify complete-case deletion. All other raw columns are outside this approved scope, not demonstrated irrelevant.

| variable | available | missing_percent | decision | mobile | reason |
| --- | --- | --- | --- | --- | --- |
| _AGEG5YR | True | 2.19 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| SEXVAR | True | 0.0 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| _BMI5 | True | 10.68 | Retain provisionally | requires measurement | Retain: documented, available questionnaire input. |
| GENHLTH | True | 0.265 | Retain provisionally | easy user input | Retain provisionally: may reflect consequences of existing CHD/MI; unsuitable for causal or future-risk interpretation. |
| _TOTINDA | True | 0.212 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| _SMOKER3 | True | 5.692 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| DIABETE4 | True | 0.225 | Retain provisionally | requires known medical history | Retain: documented, available questionnaire input. |
| CVDSTRK3 | True | 0.326 | Retain provisionally | requires known medical history | Retain provisionally: distinct diagnosis from CHD/MI; shared vascular disease and temporal ordering are unresolved. |
| CHCKDNY2 | True | 0.413 | Retain provisionally | requires known medical history | Retain: documented, available questionnaire input. |
| ASTHMA3 | True | 0.398 | Retain provisionally | requires known medical history | Retain: documented, available questionnaire input. |
| DIFFWALK | True | 4.52 | Retain provisionally | easy user input | Retain provisionally: may reflect consequences of existing cardiovascular disease. |
| TOLDHI3 | True | 14.584 | Retain provisionally | requires known medical history | Retain provisionally: prior testing needed; not a numeric laboratory result. Screening-dependent missingness. |
| _RFHYPE6 | True | 0.436 | Retain provisionally | requires known medical history | Retain: documented, available questionnaire input. |
| DRNKANY5 | True | 6.973 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| _EDUCAG | True | 0.565 | Retain provisionally | easy user input | Retain: documented, available questionnaire input. |
| _INCOMG1 | True | 21.521 | Retain provisionally | easy user input | Retain provisionally despite high missingness: optional socioeconomic input; fairness and geographic/price portability require review. |

General health, walking difficulty and stroke history have unresolved temporal relationships. Income has nonresponse, sensitivity and fairness concerns. High cholesterol is conditional on screening and must not treat lack of testing as No. Education and income may encode structural inequities; later compare training-only feature alternatives. SEXVAR is the survey respondent-sex field, not gender identity; applicability outside those categories requires design review.


Sources: [CDC 2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf); [CDC calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf); [CDC dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html). Local PDFs and extracted text are in docs/.
