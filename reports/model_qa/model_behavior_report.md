# Frozen model behavior QA

Synthetic research tests only; no clinical rules or causal conclusions. Model v1.0.0 remains unchanged.

```json
{
  "synthetic_tests": 55,
  "score_min": 0.00211,
  "score_max": 0.831258,
  "low_score": 0.002504,
  "high_score": 0.831258,
  "high_scored_higher": true,
  "unexpected_errors": 0,
  "missing_passed": 4,
  "boundary_passed": 56,
  "boundary_count": 56,
  "threshold_score_unchanged": true,
  "classification_distribution": {
    "lower_model_association": 53,
    "elevated_model_association": 2
  }
}
```

All four missing-value cases are sent as explicit nulls. Categorical minima/maxima and out-of-domain values plus BMI endpoints and out-of-range values are exercised through POST /predict. PASS in boundary tests means the HTTP contract matched expectations. All valid behavioral observations remain REVIEW pending human assessment.

Largest observed one-field response changes:

- stroke_history=1: absolute difference 0.078095
- age_group=13: absolute difference 0.031904
- general_health=5: absolute difference 0.023961
- age_group=12: absolute difference 0.017491
- age_group=11: absolute difference 0.011167

No unsupported clinical directional expectations were asserted. See CSV files for every input and actual response.
