"""Deterministic mappings verified against the CDC 2021 codebook."""
CODEBOOK = 'https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf'
CALCULATED = 'https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf'

def spec(name, labels, mapping, question, kind='nominal', usability='easy user input', reason='Retain: documented, available questionnaire input.', unknown=(), refused=(), combined=()):
    return dict(name=name, labels=labels, mapping=mapping, question=question, kind=kind, usability=usability, reason=reason, unknown=unknown, refused=refused, combined=combined)

YES_NO = {1: 1, 2: 0, 7: None, 9: None}
VARIABLES = {
 '_AGEG5YR': spec('age_group', dict(enumerate(['18-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80 or older'],1)) | {14:'Unknown/refused/missing'}, {**{i:i for i in range(1,14)},14:None}, 'What is your age? Adults 18 or older only.', 'ordinal', combined=(14,)),
 'SEXVAR': spec('sex',{1:'Male',2:'Female'}, {1:1,2:2}, 'What sex was recorded for you under the BRFSS respondent-sex question?'),
 '_BMI5': spec('bmi',{'1-9999':'BMI with two implied decimal places'}, {}, 'Enter your measured height and weight to calculate BMI.', 'continuous', 'requires measurement'),
 'GENHLTH': spec('general_health',{1:'Excellent',2:'Very good',3:'Good',4:'Fair',5:'Poor',7:'Unknown',9:'Refused'}, {**{i:i for i in range(1,6)},7:None,9:None}, 'In general, would you say your health is:', 'ordinal', reason='Retain provisionally: may reflect consequences of existing CHD/MI; unsuitable for causal or future-risk interpretation.',unknown=(7,),refused=(9,)),
 '_TOTINDA': spec('physical_activity',{1:'Activity',2:'No activity',9:'Unknown/refused/missing'}, {1:1,2:0,9:None}, 'During the past 30 days, did you do physical activity or exercise other than your regular job?', combined=(9,)),
 '_SMOKER3': spec('smoking_status',{1:'Current every day, at least 100 lifetime cigarettes',2:'Current some days, at least 100 lifetime cigarettes',3:'Former, at least 100 lifetime cigarettes',4:'Fewer than 100 lifetime cigarettes',9:'Unknown/refused/missing'}, {1:1,2:2,3:3,4:4,9:None}, 'Have you smoked at least 100 cigarettes in your entire life? If yes, do you now smoke every day, some days, or not at all?',combined=(9,)),
 'DIABETE4': spec('diabetes',{1:'Yes',2:'Only during pregnancy',3:'No',4:'Prediabetes/borderline',7:'Unknown',9:'Refused'}, {1:1,2:2,3:3,4:4,7:None,9:None}, 'Have you ever been told you had diabetes? If yes, was it only during pregnancy? Include a separate prediabetes/borderline option.',usability='requires known medical history',unknown=(7,),refused=(9,)),
 'CVDSTRK3': spec('stroke_history',{1:'Yes',2:'No',7:'Unknown',9:'Refused'},YES_NO,'Have you ever been told you had a stroke?',usability='requires known medical history',reason='Retain provisionally: distinct diagnosis from CHD/MI; shared vascular disease and temporal ordering are unresolved.',unknown=(7,),refused=(9,)),
 'CHCKDNY2': spec('kidney_disease',{1:'Yes',2:'No',7:'Unknown',9:'Refused'},YES_NO,'Not including kidney stones, bladder infection or incontinence, were you ever told you had kidney disease?',usability='requires known medical history',unknown=(7,),refused=(9,)),
 'ASTHMA3': spec('asthma',{1:'Yes',2:'No',7:'Unknown',9:'Refused'},YES_NO,'Have you ever been told you had asthma?',usability='requires known medical history',unknown=(7,),refused=(9,)),
 'DIFFWALK': spec('difficulty_walking',{1:'Yes',2:'No',7:'Unknown',9:'Refused'},YES_NO,'Do you have serious difficulty walking or climbing stairs?',reason='Retain provisionally: may reflect consequences of existing cardiovascular disease.',unknown=(7,),refused=(9,)),
 'TOLDHI3': spec('high_cholesterol',{1:'Yes',2:'No',7:'Unknown',9:'Refused'},YES_NO,'Have you ever been told by a doctor, nurse, or other health professional that your cholesterol is high?',usability='requires known medical history',reason='Retain provisionally: prior testing needed; not a numeric laboratory result. Screening-dependent missingness.',unknown=(7,),refused=(9,)),
 '_RFHYPE6': spec('high_blood_pressure',{1:'No, includes pregnancy-only and borderline',2:'Yes',9:'Unknown/refused/missing'},{1:0,2:1,9:None},'Have you been told by a health professional that you have high blood pressure? Separate pregnancy-only and borderline answers map to 0.',usability='requires known medical history',combined=(9,)),
 'DRNKANY5': spec('alcohol_use',{1:'Yes',2:'No',7:'Unknown',9:'Refused/missing'},{1:1,2:0,7:None,9:None},'During the past 30 days, did you have at least one drink of any alcoholic beverage?',unknown=(7,),combined=(9,)),
 '_EDUCAG': spec('education',{1:'Did not graduate high school',2:'Graduated high school',3:'Attended college/technical school',4:'Graduated college/technical school',9:'Unknown/missing'},{1:1,2:2,3:3,4:4,9:None},'What is the highest level of education you completed?', 'ordinal',combined=(9,)),
 '_INCOMG1': spec('income_group',{1:'Household annual income below $15,000',2:'$15,000 to below $25,000',3:'$25,000 to below $35,000',4:'$35,000 to below $50,000',5:'$50,000 to below $100,000',6:'$100,000 to below $200,000',7:'$200,000 or more',9:'Unknown/refused/missing'},{**{i:i for i in range(1,8)},9:None},'What is your annual household income from all sources in US dollars?', 'ordinal',reason='Retain provisionally despite high missingness: optional socioeconomic input; fairness and geographic/price portability require review.',combined=(9,)),
}
VARIABLE_MAPPINGS = {k:v['mapping'] for k,v in VARIABLES.items()}
TARGET_MAPPING = {1:1,2:0}
LEAKAGE = {'_MICHD','CVDINFR4','CVDCRHD4'}
FEATURE_NAMES = [v['name'] for v in VARIABLES.values()]
