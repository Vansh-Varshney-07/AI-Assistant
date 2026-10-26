param([string]$ReportDirectory = (Join-Path $PSScriptRoot '.local\verification'))
$ErrorActionPreference = 'Stop'
$candidates = @((Join-Path $PSScriptRoot '.venv\Scripts\python.exe'), 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe')
$python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'Install requirements.txt into .venv first.' }
$testId = [Guid]::NewGuid().ToString('N').Substring(0,12)
$container = 'wayfinder-tests-' + $testId
$priorPort = $env:FALKORDB_PORT
$priorHost = $env:FALKORDB_HOST
$reportPath = [System.IO.Path]::GetFullPath($ReportDirectory)
$exitCode = 1
Push-Location $PSScriptRoot
try {
    Write-Output 'Quit Wayfinder before this run so its global hotkey is available to the native UI test.'
    New-Item -ItemType Directory -Force -Path $reportPath | Out-Null
    docker image inspect falkordb/falkordb:v4.20.7 --format '{{.Id}}'
    if ($LASTEXITCODE -ne 0) { throw 'The pinned FalkorDB image must already be installed.' }
    docker run -d --name $container -p '127.0.0.1::6379' --tmpfs /data -e 'REDIS_ARGS=--appendonly no --save ""' -e 'BROWSER=0' falkordb/falkordb:v4.20.7
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the disposable test database.' }
    $portText = docker port $container 6379/tcp
    if ($portText -notmatch '^127\.0\.0\.1:(\d+)$') { throw 'Unexpected database binding.' }
    $env:FALKORDB_PORT = $Matches[1]
    $env:FALKORDB_HOST = '127.0.0.1'
    $ready = $false
    for ($attempt=0; $attempt -lt 20; $attempt++) {
        if ((docker exec $container redis-cli ping 2>$null) -eq 'PONG') { $ready = $true; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'Disposable database did not become ready.' }
    $baseTemp = Join-Path $PSScriptRoot ('.local\pytest-' + $testId)
    & $python -m pytest -q --tb=short --basetemp $baseTemp --junitxml (Join-Path $reportPath 'regression.xml')
    $exitCode = $LASTEXITCODE
} finally {
    # Only this invocation's unique disposable container; never a live volume.
    docker rm -f -v $container 2>$null | Out-Null
    $env:FALKORDB_PORT = $priorPort
    $env:FALKORDB_HOST = $priorHost
    Pop-Location
}
exit $exitCode
