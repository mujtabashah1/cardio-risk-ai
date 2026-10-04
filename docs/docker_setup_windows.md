# Windows Docker setup

Checked 2026-10-04: `docker --version` and `docker info` fail because the Docker command is unavailable. Both `wsl --status` and `wsl --version` report that WSL is not installed. The standard `C:\Program Files\Docker\Docker\Docker Desktop.exe` path is absent. No container verification has run.

1. Open PowerShell **as Administrator** and run:

   ```powershell
   wsl --install
   ```

   Restart Windows when installation finishes. This enables the required Windows features and installs Ubuntu; complete its first-launch user setup if prompted. See [Microsoft WSL installation instructions](https://learn.microsoft.com/en-us/windows/wsl/install).

2. After restarting, run:

   ```powershell
   wsl --update
   wsl --set-default-version 2
   wsl --status
   wsl --version
   wsl --list --verbose
   ```

   If Ubuntu is listed as version 1, run `wsl --set-version Ubuntu 2`. If installation reports a virtualization prerequisite, follow the Microsoft troubleshooting link from the installation page before proceeding.

3. Install Docker Desktop using the [official Windows installer and requirements](https://docs.docker.com/desktop/setup/install/windows-install/), choosing the installer matching the host architecture. Launch Docker Desktop. In Settings > General, enable **Use the WSL 2 based engine**. Use Linux containers; if its tray menu offers **Switch to Linux containers**, select it. See [Docker's WSL backend instructions](https://docs.docker.com/desktop/features/wsl/).

4. Open a new project PowerShell terminal and verify:

   ```powershell
   docker --version
   docker info
   docker info --format '{{.OSType}}'
   ```

   The engine must respond successfully and the last command must print `linux`. Confirm the WSL engine setting in Docker Desktop as well. If Docker is still not found, restart the IDE after installation so its terminal receives the updated PATH.

5. Only after those checks succeed, run the existing verification script from the project directory:

   ```powershell
   Set-Location 'C:\heart disease project\cardio-risk-ai'
   .\scripts\verify_container.ps1
   ```

   If execution policy alone blocks this trusted local script, a process-scoped invocation is:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_container.ps1
   ```

   This does not persistently change execution policy or override organization policy. The existing script builds `cardiorisk-profile-api:1.0.0`, checks readiness, health and a synthetic prediction, then removes its own container. It is a smoke test: image-content inspection, in-container hash, unchanged golden fixtures, all five policies, full invalid-input checks, benchmarks, memory, concurrency and runtime security checks must also pass before upgrading readiness.

No system installation or restart was performed by this verification task. The existing Dockerfile, ignore rules and verification script are unchanged.
