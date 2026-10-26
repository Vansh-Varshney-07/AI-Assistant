param([switch]$Prepare, [switch]$Check)
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$python = @((Join-Path $project '.venv\Scripts\python.exe'), 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe') |
    Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'A configured Python environment is required.' }
if ($Prepare) {
    & $python -m pip --isolated install --target (Join-Path $project '.local\google-oauth') --no-compile --only-binary=:all: --index-url 'https://pypi.org/simple' -r (Join-Path $project 'requirements\google-connect.txt')
    if ($LASTEXITCODE -ne 0) { throw 'The local OAuth helper could not be prepared.' }
    $Check = $true
}
$arguments = @((Join-Path $project 'scripts\auth_google.py'))
if ($Check) { $arguments += '--check' }
& $python @arguments
exit $LASTEXITCODE
