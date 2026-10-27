param([switch]$IncludeUi, [switch]$Platform, [switch]$PlatformLive)
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$python = @((Join-Path $project '.venv\Scripts\python.exe'), 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe') |
    Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'A configured project Python environment is required.' }
$testId = [Guid]::NewGuid().ToString('N')
$container = 'wayfinder-desktop-tests-' + $testId
$testTemp = Join-Path $env:TEMP ('wayfinder-desktop-tests-' + $testId)
$report = Join-Path $project '.local\verification'
$priorHost = $env:FALKORDB_HOST
$priorPort = $env:FALKORDB_PORT
$priorPlatformLive = $env:WAYFINDER_PLATFORM_LIVE
$testExit = 1
Push-Location $project
try {
    New-Item -ItemType Directory -Force -Path $report | Out-Null
    docker image inspect falkordb/falkordb:v4.20.7 --format '{{.Id}}' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Install the pinned database image before running these tests.' }
    docker run -d --name $container -p '127.0.0.1::6379' --tmpfs /data -e 'REDIS_ARGS=--appendonly no --save ""' -e 'BROWSER=0' falkordb/falkordb:v4.20.7 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Disposable database could not start.' }
    $port = docker port $container 6379/tcp
    if ($port -notmatch '^127\.0\.0\.1:(\d+)$') { throw 'Unexpected test database binding.' }
    $env:FALKORDB_HOST = '127.0.0.1'
    $env:FALKORDB_PORT = $Matches[1]
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ((docker exec $container redis-cli ping 2>$null) -eq 'PONG') { $ready = $true; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'Disposable database is not ready.' }
    $testFiles = @('tests/test_desktop_workers.py', 'tests/test_cua_fixture.py', 'tests/test_wayfinder_app.py')
    $reportName = 'desktop-workers.xml'
    if ($Platform) {
        $testFiles += 'tests/test_platform_integration.py'
        $testFiles += 'tests/test_platform_git.py'
        $testFiles += 'tests/test_platform_memory.py'
        $testFiles += 'tests/test_platform_sources.py'
        $testFiles += 'tests/test_google_setup.py'
        $reportName = 'platform.xml'
    }
    if ($PlatformLive) {
        $env:WAYFINDER_PLATFORM_LIVE = '1'
        $reportName = 'platform-live.xml'
    } else {
        $env:WAYFINDER_PLATFORM_LIVE = '0'
    }
    $selection = @('-k', 'not desktop_worker_controls_and_space_switch')
    if ($IncludeUi) {
        $testFiles += 'tests/test_wayfinder_desktop.py'
        $selection = @()
    }
    if ($PlatformLive) {
        $selection = @('-k', 'live_installed_hermes_read_workflow')
    }
    & $python -m pytest @testFiles @selection -q --tb=short -p no:cacheprovider --basetemp $testTemp --junitxml (Join-Path $report $reportName)
    $testExit = $LASTEXITCODE
} finally {
    # Only this run's uniquely named disposable container; no persistent data volume.
    docker rm -f -v $container 2>$null | Out-Null
    $env:FALKORDB_HOST = $priorHost
    $env:FALKORDB_PORT = $priorPort
    $env:WAYFINDER_PLATFORM_LIVE = $priorPlatformLive
    Pop-Location
}
exit $testExit
