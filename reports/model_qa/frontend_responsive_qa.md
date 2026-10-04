# React responsive and browser QA — 2026-10-04

Chrome, real Vite frontend and local frozen CatBoost API. Only synthetic inputs. Measurements are saved in react_responsive_measurements.json.

| Width | Layout | Navigation | Forms / native selects | Review / results | QA comparison | Horizontal overflow |
| --- | --- | --- | --- | --- | --- | --- |
| 375px | Single column | Hamburger opened and navigation used | Controls inside viewport | PASS | PASS | None |
| 768px | Compact tablet | Hamburger available | Controls inside viewport | PASS | PASS | None |
| 1024px | Laptop layout | Top navigation | Controls inside viewport | PASS | PASS | None |
| 1440px | Desktop layout | Top navigation | Controls inside viewport | PASS | PASS | None |

Home, assessment, review, results and expanded QA form/result/comparison were measured at every width. Native smoking and diabetes select labels preserve CDC meanings. Review shows grouped answers with edit buttons. No custom modal was introduced. Long JSON is intentionally scrollable within its own technical panel. Temporary viewport overrides were reset.

Chrome manual flow: home → assessment → all four steps → real low response → QA high/null profiles → threshold switching → duplicate low profile and change only stroke history. Display formatting matched returned scores. Reloading Results produced a safe empty state; browser Back returned to a working assessment. A separate temporary local Vite instance pointed to an unused API port: status showed API unavailable and Analyze showed a friendly error with Try again. That test server was stopped.

Edge was not exposed by the connected browser inventory, so no Edge pass is claimed. The temporary HMR interruption during source formatting was recovered with reload; completed flows ran successfully afterward.

Screenshots: docs/screenshots/react_home.png, react_assessment.png, react_review.png, react_results.png, react_qa.png, react_mobile.png, react_model.png and react_api_outage.png. All contain synthetic data only.
