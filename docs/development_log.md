# Development log

## Established earlier milestones

- Dataset cleaning, exact mappings, dictionary and grouped stratified splits completed before this website phase. Dates are not reconstructed here.
- CatBoost training/evaluation and model selection completed. The frozen model specification records **2026-10-03** for the v1.0.0 freeze.
- FastAPI inference, integrity checks, threshold policies, native tests and native release verification were present before this phase. Container verification remains pending.

## 2026-10-04 — Local interactive model QA website

- Completed and verified the existing lightweight HTML/CSS/JavaScript website, served alongside FastAPI at /testing/ with exactly 14 cleaned inputs.
- Preserved frozen model, feature list, thresholds, calibration and prediction response contract. Added baseline duplication, named invalid-input QA and protection against stale asynchronous responses.
- Verified 22 JavaScript tests, 9 Python frontend contract tests and 60 backend/model/artifact/pipeline tests.
- Ran 55 synthetic model cases, 4 missing-input cases and 56 boundary checks. No fitting or respondent-data predictions were performed.
- Verified Chrome submissions for both synthetic presets: 0.002504 and 0.831258. Raw JSON, threshold switching, missing BMI, error rendering, local recording/CSV download and responsive layout were checked.
- Prepared training reproduction documentation, privacy exclusions and version-control review. GitHub status is recorded separately in docs/version_control.md; no final release tag is created for this development milestone.
- Committed the verified local milestone on main. A fresh local clone passed 68 Python tests with one explicitly skipped local-data audit; model/supporting hashes and golden/API checks passed without respondent datasets. The original workspace passed all 69 Python tests, including that audit.
