# Final research release quality gate

| Check | Status |
| --- | --- |
| Model hash integrity | PASS |
| Model reproducibility | PASS |
| Feature schema validation | PASS |
| Leakage protection | PASS |
| Threshold profile validation | PASS |
| False-negative analysis | PASS |
| API single inference | PASS |
| API batch inference | PASS |
| Missing-value handling | PASS |
| Invalid-input rejection | PASS |
| Golden predictions | PASS |
| Automated tests | PASS |
| Health endpoint (native) | PASS |
| Readiness endpoint (native) | PASS |
| Latency benchmark (native) | PASS |
| Concurrency check (native) | PASS |
| Security input checks | PASS |
| Logging review | PASS |
| Documentation | PASS |
| Docker build | PENDING - Docker unavailable |
| Container startup | PENDING - Docker unavailable |
| Container model integrity | PENDING - Docker unavailable |
| Container golden predictions/tests | PENDING - Docker unavailable |
| Container health/readiness | PENDING - Docker unavailable |

Automated tests: 60 passed, 0 failed, 0 skipped; summed test runtime 5.879 seconds. Native HTTP checks: 54 passed. Docker/container checks are not substituted by native results; deployment verification is not fully complete.

Release/model/API version 1.0.0. No model fitting, recalibration, feature/split/default-threshold changes or test-data optimization occurred. Golden/cached validation evidence is reused; only synthetic profiles were sent over HTTP.

Readiness: **READY FOR LOCAL RESEARCH USE**. Default recall ~51% and high-sensitivity false-positive costs remain documented. No diagnosis, future-risk prediction or clinical screening standard. Public deployment needs controlled access, TLS, rate/concurrency controls and external validation.

## Latest Docker environment check

Checked 2026-10-04T02:40:24.855621-07:00. Docker CLI is unavailable and WSL reports not installed. All five container gates remain PENDING. Earlier native PASS results are retained; no native tests were rerun for this Docker-only task. `container_verification_complete` and `full_container_verification_complete` are false. See [container report](container_verification.md) and [Windows setup](../../docs/docker_setup_windows.md).
