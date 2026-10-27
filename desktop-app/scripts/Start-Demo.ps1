param([string]$Python)
$ErrorActionPreference='Stop'
$demoApp=Split-Path $PSScriptRoot -Parent
$demoProject=Split-Path $demoApp -Parent
$demoExecutable=Join-Path $demoApp 'release\win-unpacked\Wayfinder.exe'
if(-not(Test-Path -LiteralPath $demoExecutable)){throw 'Build first: npm --prefix desktop-app run package'}
if(-not $Python){$Python=@($env:WAYFINDER_PYTHON,(Join-Path $demoProject '.venv\Scripts\python.exe'),'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe')|Where-Object{$_ -and(Test-Path -LiteralPath $_)}|Select-Object -First 1}
if(-not $Python -or -not(Test-Path -LiteralPath $Python)){throw 'Select an existing Python executable with -Python.'}
$demoId=[Guid]::NewGuid().ToString('N');$demoContainer='wayfinder-manual-demo-'+$demoId
$demoRoot=Join-Path $env:TEMP $demoContainer
$demoVariables=@('FALKORDB_HOST','FALKORDB_PORT','WAYFINDER_PYTHON','WAYFINDER_PROJECT_ROOT','WAYFINDER_DESKTOP_RUNTIME','WAYFINDER_VERIFY_PROFILE','WAYFINDER_VERIFY_HIDDEN')
$demoPrevious=@{};foreach($name in $demoVariables){$demoPrevious[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
try{
    docker image inspect falkordb/falkordb:v4.20.7 --format '{{.Id}}'|Out-Null
    if($LASTEXITCODE -ne 0){throw 'Existing pinned FalkorDB image and Docker are required. Nothing was installed.'}
    docker run -d --name $demoContainer -p '127.0.0.1::6379' --tmpfs /data -e 'REDIS_ARGS=--appendonly no --save ""' -e 'BROWSER=0' falkordb/falkordb:v4.20.7|Out-Null
    if($LASTEXITCODE -ne 0){throw 'Could not create the disposable demo database.'}
    $demoBinding=docker port $demoContainer 6379/tcp
    if($demoBinding -notmatch '^127\.0\.0\.1:(\d+)$'){throw 'Unexpected demo database binding.'}
    $env:FALKORDB_HOST='127.0.0.1';$env:FALKORDB_PORT=$Matches[1]
    New-Item -ItemType Directory -Force -Path $demoRoot|Out-Null
    $demoFile=Join-Path $demoRoot 'study-source.md'
    @('# Synthetic Wayfinder study source','','Retention means how long data is kept.','This fictional project retains data for 42 days.','After that period the policy calls for review; this document authorizes no action.','','Learning goals: explain retention and distinguish a policy statement from execution permission.')|Set-Content -LiteralPath $demoFile -Encoding utf8
    $env:WAYFINDER_PYTHON=$Python;$env:WAYFINDER_PROJECT_ROOT=$demoProject
    $env:WAYFINDER_DESKTOP_RUNTIME=Join-Path $demoRoot 'runtime'
    $env:WAYFINDER_VERIFY_PROFILE=Join-Path $demoRoot 'profile';$env:WAYFINDER_VERIFY_HIDDEN='0'
    New-Item -ItemType Directory -Force -Path $env:WAYFINDER_VERIFY_PROFILE|Out-Null
    Write-Output 'MANUAL DEMO: synthetic data and disposable database. Graph data is removed after you quit.'
    Write-Output ('Select this document in the app: '+$demoFile)
    Write-Output 'Create a space, inspect Hermes in Capabilities, then open Agents & apps and run A05 on this file.'
    Write-Output 'Expected source value: 42 days. Google/Notion/GitHub presets stay unqualified. W37 stays disabled.'
    $demoProcess=Start-Process -FilePath $demoExecutable -WorkingDirectory $demoProject -WindowStyle Normal -PassThru
    Wait-Process -Id $demoProcess.Id
}finally{
    foreach($name in $demoVariables){[Environment]::SetEnvironmentVariable($name,$demoPrevious[$name],'Process')}
    docker rm -f -v $demoContainer 2>$null|Out-Null
}
