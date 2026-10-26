param([switch]$Live)
# Reuse the existing isolated database runner. Native/UI tests stay excluded.
& (Join-Path $PSScriptRoot 'Test-DesktopWorkers.ps1') -Platform -PlatformLive:$Live
exit $LASTEXITCODE
