# BRFSS CHD/MI Profile Score API

This model classifies BRFSS-like health profiles associated with existing self-reported CHD/MI. It is not a medical diagnosis and does not estimate future cardiovascular-event risk.

## Start locally

From the project directory with Python 3.12:

```powershell
python -m pip install -r requirements-api-test.txt
python -m api
```

The default binding is `127.0.0.1:8000`. `python -m api` reads API_HOST/API_PORT, disables access logging and trusts no forwarded proxy headers. For an equivalent explicit start: `python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers`. No debug/reload mode is used.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Minimal process liveness |
| GET | /ready | 503 until verified model is loaded |
| GET | /model-info | Safe model interpretation/features/profiles |
| POST | /predict | One named profile |
| POST | /predict/batch | Transactional ordered batch |

OpenAPI: `/openapi.json`; interactive documentation: `/docs`. Exported specification: `reports/deployment/openapi.json`.

## Synthetic request and actual fixture response

```json
{
  "profile": {
    "age_group": 8,
    "sex": 1,
    "bmi": 28.5,
    "general_health": 3,
    "physical_activity": 1,
    "smoking_status": 3,
    "diabetes": 3,
    "stroke_history": 0,
    "kidney_disease": 0,
    "asthma": 0,
    "difficulty_walking": 0,
    "high_cholesterol": 1,
    "high_blood_pressure": 1,
    "alcohol_use": 0
  },
  "threshold_profile": "research_balanced"
}
```

```json
{
  "profile_score": 0.183223,
  "classification": "lower_model_association",
  "threshold": 0.20943938491134126,
  "threshold_profile": "research_balanced",
  "model_version": "1.0.0",
  "model_name": "BRFSS CHD/MI Profile Score",
  "model_context": "This model classifies BRFSS-like health profiles associated with existing self-reported CHD/MI. It is not a medical diagnosis and does not estimate future cardiovascular-event risk."
}
```

Batch form: `{"profiles":[{"sex":1},{"sex":2,"bmi":null}],"threshold_profile":"research_balanced"}`. Returned `predictions` preserve input order with a `count`. All rows validate before any prediction; one invalid row rejects the entire batch with indexed details. See [model_inputs.md](model_inputs.md) for dictionary-derived meanings and [thresholds.md](thresholds.md) for policies.

Unknown/extra fields, socioeconomic fields and every target/leakage name are rejected. No aliases are accepted. Missing structural objects, empty objects, malformed types and invalid categories are rejected. Optional predictor omission/null is supported. No numeric strings, boolean category codes, non-finite floats, category floats or numeric caller-provided thresholds. Duplicate JSON keys are rejected before schema parsing.

## Responses and errors

Successful response fields: profile_score, classification, threshold, threshold_profile, model_version, model_name and model_context. Classifications are `lower_model_association` or `elevated_model_association`. Raw score remains full precision internally; JSON display has six decimals.

Errors use `{"error":{"code":"INVALID_INPUT","message":"Input validation failed.","details":[...]}}`, with submitted values, unknown-field names and exception context stripped. Statuses: 400 malformed/duplicate JSON, 413 body size exceeded, 415 wrong media type, 422 schema/category/batch-policy failure, 500 safe inference/internal failure, 503 not ready, 404/405 routing errors. Model/hash/metadata/schema/threshold/golden mismatch aborts startup rather than serving a substitute model.

## Configuration and operations

Environment variables: API_HOST, API_PORT, LOG_LEVEL, CORS_ORIGINS (JSON array of exact HTTP(S) origins), MAX_BATCH_SIZE (1–1000; default 1000), MAX_BODY_BYTES (default 1 MiB), MODEL_PATH, METADATA_PATH, SCHEMA_PATH, THRESHOLD_PROFILES_PATH and EXPECTED_MODEL_HASH. Hash must equal the pinned 1.0.0 artifact. Paths must refer to identical approved content. `.env.example` is a template; variables are exported by the shell/container, not automatically loaded from a dotenv file.

Empty CORS list is the default; wildcard origins are rejected. Prediction calls share one cached model per worker and a lock; different workers each load their own verified model. Increase worker count only after measuring memory and throughput. Health payloads, returned scores and identifiers are never logged by the application. Operational logs contain only generated request_id, normalized endpoint, status, latency, model_version, named threshold_profile and batch_size. Reverse-proxy logs must also avoid request bodies and sensitive query strings.

Rate limiting and authentication are boundary responsibilities: place behind a TLS reverse proxy with explicit client authorization and per-client/per-IP rate and concurrent-request limits (for example a modest research limit of 5 requests/second with a small burst, adjusted by load testing). Do not expose this unauthenticated research service directly to the public Internet. In-memory per-worker limiting would not enforce a reliable multi-worker quota, so no extra limiter dependency was added. Apply a proxy body limit matching the application limit; preserve readiness checks.

## Container

```powershell
docker build -t cardiorisk-profile-api:1.0.0 .
docker run --rm -p 127.0.0.1:8000:8000 cardiorisk-profile-api:1.0.0
./scripts/verify_container.ps1
```

The Dockerfile runs as a non-root user, has a readiness health check, and explicitly copies only inference code, approved model artifacts, dictionary, integrity manifest and synthetic smoke fixtures. No respondent datasets, candidates, training reports or secrets are included. XGBoost/LightGBM are necessary imports of the unchanged pickled wrapper module, not additional models served; SHAP, Optuna, PyArrow and PDF tooling are excluded. CatBoost declares plotting/graphviz Python dependencies even though this API does not expose explanations. A Docker engine is absent here, so build and container health have not been verified. These quality gates are pending, not passed.

## Tests and limitations

```powershell
python scripts/check_deployment.py
```

This runs API/inference/golden/fresh-process/concurrency and existing tests, then benchmarks synthetic records and checks unchanged artifacts. It does not rerun test-data predictions. `scripts/audit_deployment.py` is the separate explicit reproduction audit and should only be run when that audit is intended.

Independent-test recall ~51.5%, precision ~31.7%, ROC-AUC ~0.8468, average precision ~0.3448, prevalence ~8.14%. Many target-positive records are missed and many elevated classifications are target-negative. See subgroup deployment notes; do not claim uniform age/sex performance. No public per-profile SHAP, diagnosis, future-risk calculation, clinical cutoff, mobile interface or clinical validation.

Implementation references: [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/), [FastAPI lifecycle tests](https://fastapi.tiangolo.com/advanced/testing-events/), [Pydantic strict validation](https://docs.pydantic.dev/latest/concepts/strict_mode/).
