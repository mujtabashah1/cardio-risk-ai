# Manual browser verification

Verified in Chrome on 2026-10-04 (America/Los_Angeles), against the actual native API at http://127.0.0.1:8000. Website: http://127.0.0.1:8000/testing/.

| Check | Observed result |
| --- | --- |
| All 14 controls | Rendered, with documented categories and Unknown choices |
| Young synthetic profile | Score 0.002504; displayed 0.3%; lower model association |
| Older synthetic profile | Score 0.831258; displayed 83.1%; elevated model association |
| Frontend/API consistency | Display and formatted raw JSON agree for both profiles |
| Threshold switching | Older-profile score stayed 0.831258 when threshold changed from 0.20943938491134126 to 0.045767086681139546 |
| Missing BMI | Blank field submitted; successful score 0.002513 |
| Invalid BMI QA | Readable error names Body Mass Index (BMI); raw INVALID_INPUT response has sanitized schema details |
| Manual recording | Two actual results recorded in browser; PASS refers to UI/API agreement only |
| CSV export | Downloaded manual_model_qa.csv, 552 bytes, two records; copied to manual_profile_tests.csv |
| Desktop | Two-column form/result layout; desktop screenshot saved |
| Mobile | At requested 390x844 viewport, document client and content widths were both 375 CSS pixels; all 14 fields present, no horizontal overflow; screenshot saved and override reset |

The download-event observer timed out, but the completed CSV was independently found and inspected in Downloads. No export success is inferred from the observer alone.

JavaScript tests separately exercise all five policies, classification changes, baseline duplication/comparison, local recording/clearing, network errors and stale-response rejection. Python contract tests exercise all categorical domains and API endpoints. Behavioral observations remain REVIEW until qualitatively assessed; these checks are not clinical validation.
