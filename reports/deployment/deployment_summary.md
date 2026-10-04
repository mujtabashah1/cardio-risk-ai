# Deployment completion status

Frozen model/hash, exact 14-feature schema, all five named threshold profiles, singleton loading, golden/fresh-process output, single/batch validation, concurrency, privacy/error/body/CORS behavior, OpenAPI and documentation passed.

60 tests passed; 0 failed. Native backend is ready for local research-client integration.

| Records | Median seconds | p95 seconds | Records/second (single caller) |
| --- | --- | --- | --- |
| 1 | 0.059982 | 0.075693 | 16.7 |
| 10 | 0.066061 | 0.081010 | 151.4 |
| 100 | 0.076251 | 0.092484 | 1311.5 |
| 1000 | 0.144390 | 0.171849 | 6925.7 |

Docker build and local container health are pending because no Docker engine is installed. The full container quality gate is not complete. No model, threshold default, prepared dataset, mapping or historical metrics was changed. See docs/api.md and model_inputs.md for integration.
