param([switch]$Live)
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$python = @((Join-Path $project '.venv\Scripts\python.exe'), 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe') |
    Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'A configured Python environment is required.' }
$arguments = @((Join-Path $project 'scripts\test_google_connection.py'))
if ($Live) { $arguments += '--live' }
& $python @arguments
exit $LASTEXITCODE
