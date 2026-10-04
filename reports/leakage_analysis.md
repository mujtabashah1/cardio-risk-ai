# Target leakage audit

| Variable | Reason for exclusion | Relationship with target |
| --- | --- | --- |
| _MICHD | Label cannot be a predictor | Exact target |
| CVDINFR4 | Explicit prior heart attack/MI diagnosis | Direct CDC source |
| CVDCRHD4 | Explicit angina/CHD diagnosis | Direct CDC source |

CDC logic: either source equals 1 -> _MICHD=1; both equal 2 -> _MICHD=2; otherwise missing. A Yes takes precedence over an unknown in the other source. The pipeline verifies this derivation against every raw row.

All available codebook variable definitions were searched for coronary, myocardial, heart attack, angina, heart disease and cardiovascular. Matched variables are in leakage_keyword_audit.csv; every requested predictor was separately reviewed. CRGVPRB3 mentions heart disease for the person cared for, not the respondent; it is outside the selected feature scope and is not a direct source of the respondent target. No other documented explicit respondent CHD/MI diagnosis was found. Documentation gap: raw USEMRJN3 has no entry in the downloaded codebook. It is outside the candidate scope, remains excluded, and has not been interpreted. An official 2021 USEMRJN3 definition would be required before considering it. All selected variables have confirmed definitions. Therefore this audit cannot claim interpretation of every unselected raw field. The dependency matrix lists only the two direct sources for _MICHD.

General health, disability, stroke and lifestyle could follow a diagnosis. They are potential temporal proxies, not documented encodings of the target. This cross-sectional dataset cannot establish when they occurred. It is prepared for classification of reported prevalent CHD/MI; a claim of prospective risk would require a different outcome and temporal data. Statistical correlation is not proof of leakage. Identifiers, sampling weights, geography, and every unapproved raw field are absent from predictors.

Identical complete cleaned records are assigned to one split; source-row IDs also have disjoint membership. Different people can share identical predictors with different labels; that does not duplicate the same labeled record.


Sources: [CDC 2021 codebook](https://www.cdc.gov/brfss/annual_data/2021/pdf/codebook21_llcp-v2-508.pdf); [CDC calculated variables](https://www.cdc.gov/brfss/annual_data/2021/pdf/2021-calculated-variables-version4-508.pdf); [CDC dependency matrix](https://www.cdc.gov/brfss/annual_data/2021/summary_matrix_21.html). Local PDFs and extracted text are in docs/.
