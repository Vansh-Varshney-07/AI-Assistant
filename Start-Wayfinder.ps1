param([string]$Runtime = (Join-Path $PSScriptRoot '.local\wayfinder'))
$ErrorActionPreference = 'Stop'
$candidates = @((Join-Path $PSScriptRoot '.venv\Scripts\pythonw.exe'), 'D:\Opencode_\reserchpaper\.venv\Scripts\pythonw.exe')
$python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw 'Create a Python environment with requirements.txt first. See docs/wayfinder-phase-0-2/README.md.' }
Start-Process -FilePath $python -ArgumentList @('"' + (Join-Path $PSScriptRoot 'wayfinder_app.py') + '"', '--runtime', '"' + $Runtime + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
