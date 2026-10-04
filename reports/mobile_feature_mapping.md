# Mobile questionnaire mapping

No UI is built. All unknown or skipped responses remain missing; the later inference pipeline must match training handling. These questions classify a survey label and do not establish future cardiovascular-event probability.

## age_group (_AGEG5YR)

Classification: easy user input.

Question: What is your age? Adults 18 or older only.

CDC options: {"1": "18-24", "2": "25-29", "3": "30-34", "4": "35-39", "5": "40-44", "6": "45-49", "7": "50-54", "8": "55-59", "9": "60-64", "10": "65-69", "11": "70-74", "12": "75-79", "13": "80 or older", "14": "Unknown/refused/missing"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12, "13": 13, "14": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## sex (SEXVAR)

Classification: easy user input.

Question: What sex was recorded for you under the BRFSS respondent-sex question?

CDC options: {"1": "Male", "2": "Female"}

Internal mapping: {"1": 1, "2": 2}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## bmi (_BMI5)

Classification: requires measurement.

Question: Enter your measured height and weight to calculate BMI.

CDC options: {"1-9999": "BMI with two implied decimal places"}

Internal mapping: Divide integer _BMI5 by 100; outside documented 12.00-99.99 range becomes missing.

Validation: BMI = kg / metres squared; 12.00 through 99.99 accepted. Values outside this range must be reviewed, never clamped.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## general_health (GENHLTH)

Classification: easy user input.

Question: In general, would you say your health is:

CDC options: {"1": "Excellent", "2": "Very good", "3": "Good", "4": "Fair", "5": "Poor", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## physical_activity (_TOTINDA)

Classification: easy user input.

Question: During the past 30 days, did you do physical activity or exercise other than your regular job?

CDC options: {"1": "Activity", "2": "No activity", "9": "Unknown/refused/missing"}

Internal mapping: {"1": 1, "2": 0, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## smoking_status (_SMOKER3)

Classification: easy user input.

Question: Have you smoked at least 100 cigarettes in your entire life? If yes, do you now smoke every day, some days, or not at all?

CDC options: {"1": "Current every day, at least 100 lifetime cigarettes", "2": "Current some days, at least 100 lifetime cigarettes", "3": "Former, at least 100 lifetime cigarettes", "4": "Fewer than 100 lifetime cigarettes", "9": "Unknown/refused/missing"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## diabetes (DIABETE4)

Classification: requires known medical history.

Question: Have you ever been told you had diabetes? If yes, was it only during pregnancy? Include a separate prediabetes/borderline option.

CDC options: {"1": "Yes", "2": "Only during pregnancy", "3": "No", "4": "Prediabetes/borderline", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## stroke_history (CVDSTRK3)

Classification: requires known medical history.

Question: Have you ever been told you had a stroke?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## kidney_disease (CHCKDNY2)

Classification: requires known medical history.

Question: Not including kidney stones, bladder infection or incontinence, were you ever told you had kidney disease?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## asthma (ASTHMA3)

Classification: requires known medical history.

Question: Have you ever been told you had asthma?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## difficulty_walking (DIFFWALK)

Classification: easy user input.

Question: Do you have serious difficulty walking or climbing stairs?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## high_cholesterol (TOLDHI3)

Classification: requires known medical history.

Question: Have you ever been told by a doctor, nurse, or other health professional that your cholesterol is high?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## high_blood_pressure (_RFHYPE6)

Classification: requires known medical history.

Question: Have you been told by a health professional that you have high blood pressure? Separate pregnancy-only and borderline answers map to 0.

CDC options: {"1": "No, includes pregnancy-only and borderline", "2": "Yes", "9": "Unknown/refused/missing"}

Internal mapping: {"1": 0, "2": 1, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: prior professional diagnosis needed; no new laboratory numeric result is requested.

## alcohol_use (DRNKANY5)

Classification: easy user input.

Question: During the past 30 days, did you have at least one drink of any alcoholic beverage?

CDC options: {"1": "Yes", "2": "No", "7": "Unknown", "9": "Refused/missing"}

Internal mapping: {"1": 1, "2": 0, "7": null, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## education (_EDUCAG)

Classification: easy user input.

Question: What is the highest level of education you completed?

CDC options: {"1": "Did not graduate high school", "2": "Graduated high school", "3": "Attended college/technical school", "4": "Graduated college/technical school", "9": "Unknown/missing"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.

## income_group (_INCOMG1)

Classification: easy user input.

Question: What is your annual household income from all sources in US dollars?

CDC options: {"1": "Household annual income below $15,000", "2": "$15,000 to below $25,000", "3": "$25,000 to below $35,000", "4": "$35,000 to below $50,000", "5": "$50,000 to below $100,000", "6": "$100,000 to below $200,000", "7": "$200,000 or more", "9": "Unknown/refused/missing"}

Internal mapping: {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "9": null}

Validation: Only listed options allowed; unknown/refused/skipped answers become missing. The questionnaire must preserve wording and category boundaries.

Medical/lab knowledge: no diagnosis or laboratory result required; BMI requires measurement.


Sources: [CDC 2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf); [CDC calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf); [CDC dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html). Local PDFs and extracted text are in docs/.
