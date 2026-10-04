$ErrorActionPreference = 'Stop'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker is required for the pending container quality gates.' }
docker build --tag cardiorisk-profile-api:1.0.0 .
if ($LASTEXITCODE -ne 0) { throw 'Docker build failed.' }
$containerId = docker run --detach --publish 127.0.0.1:18000:8000 cardiorisk-profile-api:1.0.0
if ($LASTEXITCODE -ne 0) { throw 'Container start failed.' }
try {
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:18000/ready' -TimeoutSec 2; if ($response.status -eq 'ready') { $ready = $true; break } } catch { }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'Container readiness failed.' }
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:18000/health'
    $prediction = Invoke-RestMethod -Uri 'http://127.0.0.1:18000/predict' -Method Post -ContentType 'application/json' -Body '{"profile":{"sex":1}}'
    if ($health.status -ne 'ok' -or $prediction.model_version -ne '1.0.0') { throw 'Container smoke test failed.' }
    Write-Output 'Docker build, container readiness, health, and synthetic prediction checks passed.'
} finally {
    docker stop $containerId | Out-Null
    docker rm $containerId | Out-Null
}
