# Model v2 research backlog

Documentation only: none of these changes is implemented in frozen version 1.0.0.

| Topic | Proposed evidence / question |
| --- | --- |
| External validation | Evaluate independent populations with prespecified metrics and missingness policies. |
| Prospective outcomes | Acquire a longitudinal outcome dataset before making any future-risk claim. |
| Survey weighting | Assess population-oriented estimates using appropriate BRFSS sampling weights/design. |
| Subgroups | Prespecify age/sex and other adequately sampled subgroup analyses, uncertainty and fairness objectives. |
| Clinical measurements | Study meaningful measurements only where deployment collection and outcome validity are established. |
| Threshold cost analysis | Define research/clinical costs, benefits and acceptable error burdens before considering a clinical operating point. |
| Cross-year BRFSS | Validate fixed definitions and preprocessing on later surveys without optimizing the current test set. |
| Temporal validation | Use a genuinely held-out time period with prespecified evaluation. |
| Missingness shifts | Investigate train/validation differences, screening-dependent cholesterol and real-world input availability. |
| Calibration | Study transportability using independent, appropriately reserved calibration data in a new model version. |

Retain v1.0.0 unchanged. Docker verification, TLS, authorization and rate limiting are deployment tasks, not excuses to tune the model against its test set.
