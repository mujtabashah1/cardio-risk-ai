# Container verification

Checked: 2026-10-04T02:40:24.855621-07:00

`docker --version` and `docker info`: command not found. Docker version is unavailable; engine reachability cannot be established. `wsl --status` and `wsl --version`: Windows Subsystem for Linux is not installed. The standard Docker Desktop executable path is absent. WSL2 backend and Linux-container mode cannot be verified.

| Container check | Result |
| --- | --- |
| Image build | PENDING - Docker unavailable |
| Image size / build duration / warnings | PENDING - Docker unavailable |
| Image runtime contents / secrets | PENDING - Docker unavailable |
| Container startup / first prediction | PENDING - Docker unavailable |
| In-container model SHA-256 | PENDING - Docker unavailable |
| GET /health | PENDING - Docker unavailable |
| GET /ready | PENDING - Docker unavailable |
| GET /model-info | PENDING - Docker unavailable |
| Existing golden predictions | PENDING - Docker unavailable |
| All five threshold profiles | PENDING - Docker unavailable |
| Single / batch 10, 100, 1000 / ordering | PENDING - Docker unavailable |
| Invalid-input rejection | PENDING - Docker unavailable |
| Warm latency: 1, 100, 1000 records | PENDING - Docker unavailable |
| Memory: idle / prediction / 1000 records | PENDING - Docker unavailable |
| Concurrency: 5 and 10 clients / deterministic output / no reload | PENDING - Docker unavailable |
| Non-root runtime user | PENDING - Docker unavailable |
| Debug disabled / CORS / logging | PENDING - Docker unavailable |

Image tag: `cardiorisk-profile-api:1.0.0`. Expected base: `python:3.12-slim`. No build was attempted; actual build timestamp, duration and image size are null. No container latency or memory measurements exist for this check. Prior native measurements remain native evidence only.

The existing Dockerfile, .dockerignore and verification script were preserved. Their runtime allowlist and non-root configuration are source evidence only, not proof of image contents or runtime behavior. `scripts/verify_container.ps1` was not invoked because the task explicitly requires a responding engine before continuing. No execution-policy block was encountered.

Follow [Windows Docker setup](../../docs/docker_setup_windows.md), including the restart requirement and process-scoped script command if needed. Complete the full container checks after the engine becomes available; the existing script covers only the build and smoke tests.

Host model, schema, metadata and threshold hashes were verified against the unchanged release manifest. No model training, feature/threshold/calibration changes or API changes occurred.

Readiness: **READY FOR LOCAL RESEARCH USE**. Container verification remains incomplete.
