param([switch]$Live, [switch]$Neural, [switch]$NodeBridge, [switch]$ClientOnly)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path $PSScriptRoot -Parent
$projectRoot = Split-Path $appRoot -Parent
$python = @((Join-Path $projectRoot '.venv\Scripts\python.exe'), (Join-Path (Split-Path $projectRoot -Parent) 'reserchpaper\.venv\Scripts\python.exe')) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'Existing configured Python environment required.' }
$testIdentity = [Guid]::NewGuid().ToString('N')
$containerName = 'wayfinder-electron-tests-' + $testIdentity
$testRoot = Join-Path $env:TEMP $containerName
$reports = Join-Path $appRoot 'test-results'
New-Item -ItemType Directory -Force -Path $reports | Out-Null
$previousHost = $env:FALKORDB_HOST
$previousPort = $env:FALKORDB_PORT
$previousLive = $env:WAYFINDER_PLATFORM_LIVE
$testExit = 1
Push-Location $projectRoot
try {
    docker image inspect falkordb/falkordb:v4.20.7 --format '{{.Id}}' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Pinned existing test image unavailable; no image pull performed.' }
    docker run -d --name $containerName -p '127.0.0.1::6379' --tmpfs /data -e 'REDIS_ARGS=--appendonly no --save ""' -e 'BROWSER=0' falkordb/falkordb:v4.20.7 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated test database.' }
    $binding = docker port $containerName 6379/tcp
    if ($binding -notmatch '^127\.0\.0\.1:(\d+)$') { throw 'Unexpected database port binding.' }
    $env:FALKORDB_HOST = '127.0.0.1'
    $env:FALKORDB_PORT = $Matches[1]
    $env:WAYFINDER_PLATFORM_LIVE = '0'
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ((docker exec $containerName redis-cli ping 2>$null) -eq 'PONG') { $ready = $true; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'Isolated database not ready.' }
    $files = @('desktop-app/backend/test_host.py', 'tests/test_wayfinder_app.py', 'tests/test_desktop_workers.py', 'tests/test_platform_integration.py', 'tests/test_platform_git.py', 'tests/test_platform_memory.py', 'tests/test_platform_sources.py', 'tests/test_google_setup.py')
    $selection = @('-k', 'not desktop_worker_controls_and_space_switch')
    $reportName = 'backend.xml'
    if ($ClientOnly) { $files = @('desktop-app/backend/test_host.py'); $reportName = 'client-adapter.xml' }
    if ($Live) { $env:WAYFINDER_PLATFORM_LIVE = '1'; $selection = @('-k', 'live_installed_hermes_read_workflow'); $reportName = 'live-hermes.xml' }
    if ($NodeBridge) {
        New-Item -ItemType Directory -Force -Path $testRoot | Out-Null
        node (Join-Path $appRoot 'scripts\verify-node-bridge.mjs') (Join-Path $testRoot 'node-runtime') (Join-Path $reports 'node-bridge.json')
    } elseif ($Neural) {
        New-Item -ItemType Directory -Force -Path $testRoot | Out-Null
        $liveArgs = @()
        if ($Live) { $liveArgs = @('--live') }
        & $python -B (Join-Path $appRoot 'backend\verify_transport.py') --runtime (Join-Path $testRoot 'runtime') --report (Join-Path $reports 'actual-transport.json') @liveArgs
    } else {
        & $python -B -m pytest @files @selection -q --tb=short -p no:cacheprovider --basetemp $testRoot --junitxml (Join-Path $reports $reportName)
    }
    $testExit = $LASTEXITCODE
} finally {
    docker rm -f -v $containerName 2>$null | Out-Null
    $env:FALKORDB_HOST = $previousHost
    $env:FALKORDB_PORT = $previousPort
    $env:WAYFINDER_PLATFORM_LIVE = $previousLive
    Pop-Location
}
exit $testExit
