# Local model testing application

This native Windows research interface calls the existing frozen-model API. Plain HTML, CSS and JavaScript are served by FastAPI at **http://127.0.0.1:8000/testing/**. API requests use the same origin, so there is no second server, CORS relaxation, Node build, Docker or hosting requirement.

From `cardio-risk-ai/`, with Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-api-test.txt
.\.venv\Scripts\python.exe scripts/start_local_testing.py
```

For this workspace, use the existing runtime instead:

```powershell
Set-Location 'C:\heart disease project\cardio-risk-ai'
& '..\.runtime\python\python.exe' scripts/start_local_testing.py
```

Open the website URL. Ctrl+C stops the server. The default API address is http://127.0.0.1:8000; keep API_HOST on loopback. A server already using port 8000 must be stopped before starting another instance. `python -m api` also starts both API and frontend.

## Form and interpretation

Exactly 14 cleaned predictors appear. Unknown selections and blank BMI become explicit nulls. BMI is human-readable, range 12–99.99, without division by 100. Age uses the 13 documented adult categories; smoking retains the fewer-than-100-lifetime-cigarettes meaning, and diabetes retains all four categories. Model scores and classifications come only from POST /predict. The page does not calculate medical risk or infer a diagnosis.

## Manual QA workflow

1. Expand Model QA Controls and load a synthetic preset. Analyze it and compare the raw response with the displayed score/classification/version.
2. Switch named research policies. The score stays the same; classification follows the selected stored threshold. No custom numerical thresholds are accepted.
3. Load BMI missing, Smoking missing, High cholesterol missing or Multiple values missing to exercise the saved missing-value behavior.
4. Capture an analyzed baseline. Duplicate it into the form, select the comparison field, change that field only and compare. Differences describe model responses and do not establish causality.
5. Use Test invalid BMI response to send the synthetic invalid value 100 and inspect the readable, sanitized API error. Normal form validation still enforces the accepted range.
6. Enter Test ID, profile name, expected qualitative behavior, PASS/REVIEW/FAIL and notes. Record the actual result, then download manual_model_qa.csv. The browser keeps only QA records locally, not an external copy of profile inputs. Clear local QA records when finished.

Editing while a request is pending discards the stale response. Recording an unsuccessful or stale prediction is blocked. CSV export escapes spreadsheet-formula prefixes in user-entered notes.

## Automated verification

```powershell
python -m unittest discover -s tests/api
python -m unittest discover -s tests/inference
python -m unittest discover -s tests/models
python -m unittest discover -s tests/artifacts
python -m unittest discover -s tests/frontend
python -m unittest discover -s tests
python scripts/run_model_qa.py
```

With the local API running, JavaScript event/mapping/integration tests use Node.js (only needed for these tests):

```powershell
node tests/frontend/test_app.cjs
```

These tests compare all frontend dropdown codes against the live API schema and exercise form submission, raw responses, presets, missing values, policy switching, comparison, recording and asynchronous errors. They use a DOM adapter; actual Chrome verification is documented separately in reports/model_qa/manual_browser_verification.md.

Synthetic behavior observations are saved under reports/model_qa/. REVIEW means a qualitative observation needs human assessment, not a failed HTTP contract. The QA script never reads respondent datasets, fits, tunes, recalibrates or replaces the frozen model. Preserve manually entered records: the script creates its empty template only if it does not already exist.
