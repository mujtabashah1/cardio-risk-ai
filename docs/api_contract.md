# API contract — research release 1.0.0

This is the stable contract for future clients. Model and API version: **1.0.0**. The model classifies profiles associated with **existing self-reported CHD/MI in BRFSS 2021**. It is not a diagnosis, future-risk prediction or clinical screening standard.

## Endpoints

| Method | Endpoint | Request | Response |
| --- | --- | --- | --- |
| GET | /health | None | 200: {"status":"ok"} |
| GET | /ready | None | 200: status ready and model_version; otherwise 503 |
| GET | /model-info | None | Safe model family/version, features, profiles, intended use and limitations |
| POST | /predict | Required profile; optional threshold_profile | Prediction result |
| POST | /predict/batch | Required profiles list; optional threshold_profile | Ordered predictions list plus count |

Liveness alone does not establish model readiness. Startup must verify all supporting hashes and golden vectors before serving. A model/hash mismatch aborts startup. Model-info never returns filesystem paths, secrets, raw rows or classifier objects.

## Profile fields

Fields use the unchanged data dictionary and cleaned encoding. No aliases or automatic raw-CDC recoding are supported. All 14 predictors permit omission/null. The profile object itself is required and must be nonempty; one known field with null is sufficient to express unknown information.

| Field | Type | Allowed values | Omitted/null handling |
| --- | --- | --- | --- |
| age_group | strict integer category | 1: 18-24; 2: 25-29; 3: 30-34; 4: 35-39; 5: 40-44; 6: 45-49; 7: 50-54; 8: 55-59; 9: 60-64; 10: 65-69; 11: 70-74; 12: 75-79; 13: 80 or older | Explicit __MISSING__ token |
| sex | strict integer category | 1: Male; 2: Female | Explicit __MISSING__ token |
| bmi | number | Numeric BMI 12.00–99.99 (human-readable; never /100) | Saved training median BMI |
| general_health | strict integer category | 1: Excellent; 2: Very good; 3: Good; 4: Fair; 5: Poor | Explicit __MISSING__ token |
| physical_activity | strict integer category | 0: No activity; 1: Activity | Explicit __MISSING__ token |
| smoking_status | strict integer category | 1: Current every day, at least 100 lifetime cigarettes; 2: Current some days, at least 100 lifetime cigarettes; 3: Former, at least 100 lifetime cigarettes; 4: Fewer than 100 lifetime cigarettes | Explicit __MISSING__ token |
| diabetes | strict integer category | 1: Yes; 2: Only during pregnancy; 3: No; 4: Prediabetes/borderline | Explicit __MISSING__ token |
| stroke_history | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |
| kidney_disease | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |
| asthma | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |
| difficulty_walking | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |
| high_cholesterol | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |
| high_blood_pressure | strict integer category | 0: No, includes pregnancy-only and borderline; 1: Yes | Explicit __MISSING__ token |
| alcohol_use | strict integer category | 0: No; 1: Yes | Explicit __MISSING__ token |

Numbers encoded as strings, booleans, category floats, unsupported category codes, non-finite numbers, nested values and unknown fields are rejected rather than mapped to missing. Education and income are excluded; heart_disease, _MICHD, CVDINFR4 and CVDCRHD4 are rejected. Smoking retains the CDC lifetime 100-cigarette distinction; diabetes retains all four categories.

## Request examples (synthetic)

```json
{"profile":{"sex":1,"bmi":28.5},"threshold_profile":"research_balanced"}
```

```json
{"profiles":[{"sex":1},{"sex":2,"bmi":null}],"threshold_profile":"high_sensitivity_80"}
```

Batch limit defaults to 1,000 (configurable downward). Body limit defaults to 1 MiB and applies to streamed bodies too. Batches validate transactionally: any invalid row rejects the whole batch with an indexed location; there are no partial predictions. Output order equals input order.

## Response

`profile_score` is a number in [0,1]; `classification` is lower_model_association or elevated_model_association; `threshold` is the exact stored research threshold; `threshold_profile` is a supported name; `model_version` is 1.0.0; `model_name` is BRFSS CHD/MI Profile Score; `model_context` supplies the non-diagnostic interpretation. Batch response wraps results as `predictions` and `count`. All successful responses are HTTP 200.

Scores are computed with full precision. Classification uses `score >= threshold`. Only JSON score display is rounded to six decimals; do not recompute classification from that rounded score. Golden tolerance is 1e-12 internally and 0.5e-6 + 1e-12 over HTTP.

## Named threshold policies

| Profile | Exact threshold | Meaning |
| --- | --- | --- |
| research_balanced | 0.20943938491134126 | Maximum validation F1 |
| high_sensitivity_80 | 0.08757439013898735 | Approximately 80% validation recall |
| high_sensitivity_90 | 0.045767086681139546 | Approximately 90% validation recall |
| youden | 0.08256882571678677 | Maximum validation Youden J |
| conventional_050 | 0.5 | Conventional classifier reference |

Omitting threshold_profile selects research_balanced. Arbitrary numeric thresholds and unknown names are rejected. The same input produces identical profile_score and model_version across all profiles; only classification, threshold and threshold_profile can change. These validation-derived operating points are not clinical cutoffs. Default validation recall is 51.27% (2,582 missed positives). The ~80% profile avoids 1,522 misses but adds 10,273 false positives; ~90% avoids 2,052 misses but adds 18,423 false positives. Independent-test default recall is 51.55%, precision 31.68%.

## Errors

All errors have `{"error":{"code":"...","message":"...","details":[...]}}`. Validation details contain sanitized location/type/message, never submitted health values or Python exception context. Status codes: 400 malformed/duplicate/non-finite JSON, 413 oversized body, 415 unsupported media type, 422 invalid schema/category/profile/batch limit, 500 safe internal/inference failure, 503 not ready, 404/405 unsupported route/method. Deep valid JSON is rejected by parser or schema, never accepted as a profile. No silent profile fallback. Responses include generated X-Request-ID.

## Operations and compatibility

CORS is configurable with an explicit origin list and defaults to no origins. Debug is false. The model is cached once per process; calls share a prediction lock. Operational logs contain request_id, normalized endpoint, status, latency, model_version, threshold_profile and batch_size, without health payloads/scores. No public SHAP, clinical advice, subgroup thresholds or future-risk endpoint exists. See OpenAPI at /openapi.json and docs at /docs. Changes to category meanings, required structural fields or response semantics require a reviewed contract version.

This release is **READY FOR LOCAL RESEARCH USE**. Docker/container execution remains PENDING because Docker is unavailable. Controlled deployment requires successful container verification, appropriate client authorization, TLS, rate/concurrency controls and deployment-specific review. External clinical validation is separate.
