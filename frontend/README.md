# CardioRisk React research application

React 19, TypeScript, Vite, Tailwind CSS 4 with shared CSS design tokens, Zod contract validation, React Router and Lucide icons. Node 22.12+ is supported; this milestone was verified with Node 22.23.3 and React 19.3.0. Dependencies are locked in package-lock.json.

Start the frozen-model Python API from the project root:

```powershell
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Then in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints **http://127.0.0.1:5173/**. Port 5173 is strict so an existing listener produces an actionable error instead of silently switching URLs. All requests use the central client. The default `/api` proxy forwards to loopback port 8000 without changing backend CORS. `.env.example` documents `VITE_API_BASE_URL`. A direct URL such as `http://127.0.0.1:8000` requires explicit `CORS_ORIGINS='["http://127.0.0.1:5173"]'` on the backend. Do not commit actual .env files.

Pages: Home, Assessment (four-step wizard), Results, About the Model, Research / QA. Assessment uses research_balanced only. QA provides all five existing policies, synthetic presets, editable inputs, duplicate-and-compare, technical JSON, and manual JSON download. Profiles and QA records are kept in memory and cleared on refresh; there is no patient database or automatic upload.

All 14 fields retain the API categories. Unknown is explicit null, never zero. BMI is human-readable 12–99.99. Invalid values are blocked rather than converted to missing. Responses are validated, timeouts are bounded to 15 seconds, stale assessment results cannot redirect a user who has left the page, and API failures display friendly errors. Classification comes from the API; it is never recomputed from rounded scores.

```powershell
npm test
npm run build
```

Vitest + Testing Library tests use mocked HTTP. From the project root, with both local servers running:

```powershell
python scripts/verify_react_milestone.py
python scripts/run_model_qa.py
```

The first command runs all existing Python regressions plus live Vite-proxy/API checks. The second generates synthetic behavior, boundary and missing-input reports without training. See reports/model_qa/react_completion_report.md and frontend_responsive_qa.md for browser evidence.

The former standalone QA page remains in `legacy/` and is served by a freshly started FastAPI process at `/testing/`. Root app.js/style.css are retained for the earlier standalone JavaScript tests. React is run through Vite; FastAPI does not serve uncompiled TSX. No production deployment is configured.
