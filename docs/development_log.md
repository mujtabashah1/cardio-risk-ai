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

## 2026-10-04 — GitHub version control

- Verified GitHub CLI authentication as mujtabashah1 after user-approved device authorization. Credentials are stored in the Windows keyring; no credential values are versioned.
- Created the private mujtabashah1/cardio-risk-ai repository after explicit approval; verified that it had no prior branches/history before the initial main push.
- Rechecked the staged privacy scan: no prohibited respondent-data paths, potential credentials or missing required source files were detected. Existing local commit history is preserved; no release tag or force push is part of this milestone.

## 2026-10-04 — modern React research application

Modern React research website completed and connected to frozen CatBoost v1.0.0 API.

Implemented React/TypeScript/Vite/Tailwind frontend with Home, four-step Assessment, Results, About the Model and Research / QA. The central typed API client validates responses and handles timeout/network/HTTP failures. All 14 inputs preserve CDC encodings, direct BMI and explicit null. Browser-only memory, synthetic presets, named-policy QA, one-field comparison, JSON export, accessible mobile navigation and responsive design are included.

Validation: 37 mocked React tests, 69 Python regressions, 10 live proxy/API checks, 55 synthetic profiles, 56 boundary checks. Chrome desktop and 375/768/1024/1440px measurements passed without page overflow. Real low/high/all-null outputs and threshold consistency are recorded. Controlled API-outage testing recovered gracefully; Edge was unavailable to the browser connector. Frozen model SHA-256 is unchanged. Screenshots use synthetic profiles only.

The existing repository was made public at the user's explicit request before this milestone. Respondent datasets, manual health exports, credentials, node_modules and builds remain excluded. No new model tag, training or deployment.
