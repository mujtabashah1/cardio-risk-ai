# Modern React research application — completion evidence

Date: 2026-10-04 (America/Los_Angeles). Local application and model QA milestone; frozen model v1.0.0.

| Requested item | Verified result |
| --- | --- |
| Frontend stack | React, TypeScript, Vite, Tailwind CSS 4, shared CSS tokens, Zod, React Router, Lucide, Vitest/Testing Library |
| React version | 19.3.0 (installed lockfile) |
| Node version | 22.23.3; portable official download verified against published SHA-256 |
| Frontend URL | http://127.0.0.1:5173/ |
| Backend URL | http://127.0.0.1:8000 |
| Pages | Home, Assessment, Results, About the Model, Research / QA |
| Components | App layout/navigation/footer, ErrorBoundary, Disclaimer, ErrorCard, FieldInput, ProfileSummary, ScoreCard, TechnicalDetails; page-local progress, metrics, status, presets, comparison and feedback |
| 14 inputs | Exact API fields, domains and cleaned category encodings; no socioeconomic or UI-only fields sent |
| Missing/null | Explicit Unknown → null; invalid strings/categories/NaN/Infinity/range violations blocked; BMI not scaled |
| Python regressions | 69 passed, 0 failed, 0 skipped; includes API/inference/models/artifacts/legacy website/pipeline tests |
| React frontend tests | 37 passed; mocked HTTP. Retained standalone JavaScript suite: 22 passed |
| Live integration | 10 passed through real Vite proxy/API; 5 recorded Chrome request/response observations plus one-feature comparison |
| Low profile | API score 0.002504; Chrome 0.3%; lower model association |
| High profile | API score 0.831258; Chrome 83.1%; elevated model association |
| All-null profile | API score 0.221609; Chrome 22.2%; elevated under research_balanced. Missing-data model limitation / requires review |
| Threshold consistency | Identical score across research_balanced/high_sensitivity_80/high_sensitivity_90; exact distinct stored thresholds. Stroke-only modified low profile classification changes under high_sensitivity_90 |
| Responsive QA | Home/assessment/review/results/expanded QA at 375, 768, 1024, 1440px; no horizontal overflow or out-of-viewport form controls |
| Model SHA before | 4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1 |
| Model SHA after | 4e313ef2810df2d4eb73c496db169cd963303da56abb9f1fa2e97522c21108f1 |
| Commit SHA | Reported in final handoff and Git history; this report is included in that commit |
| Push status | Final handoff reports remote verification after normal main push; no force push or model release tag |
| Repository | https://github.com/mujtabashah1/cardio-risk-ai (public at explicit user request) |
| Raw datasets | Excluded, including processed respondent splits/IDs/caches/candidates. Only data dictionary is publishable under data/ |
| Secrets | No actual credentials found in staged-blob review; .env files ignored, .env.example contains only local configuration |
| Screenshots | Eight synthetic-only PNGs in docs/screenshots: home, assessment, review, results, QA, mobile, model, API outage |
| Remaining issues | Edge not available to the connected browser inventory; no Edge pass claimed. External clinical validation remains outside this milestone. No known blocking local application failure |

Evidence: react_frontend_tests.json, react_integration_tests.json, react_browser_integration.json, react_responsive_measurements.json, frontend_responsive_qa.md, qa_summary.json, threshold_switching.json and model_behavior_report.md. Local manual_profile_tests.csv was extended with synthetic Chrome formatting observations and remains ignored because later manual notes might contain personal information.

The 55-profile synthetic behavior suite and 56 boundary checks passed. Findings are observations rather than clinical assertions. A stroke-history-only comparison produced a 7.8095 percentage-point response difference; this does not establish causation. All-null elevated output is documented as a missing-data limitation, not automatically a model defect.

Assessment state and QA records are memory-only; refresh clears them and Results gives a safe empty state. Browser Back works. A controlled local API outage showed API unavailable, a readable error card and Try again without a white screen. Normal assessment uses research_balanced; other policies appear only in Research / QA. Requests have a 15-second timeout; responses are schema-validated. The frontend displays server classification and never recomputes it from rounded scores.

No training, tuning, calibration, threshold/mapping/split changes, Docker, deployment, mobile implementation or new model release tag occurred. The earlier standalone testing page remains available on freshly started FastAPI at /testing/.
