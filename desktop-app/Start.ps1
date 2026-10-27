param([string]$Runtime)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$executable = Join-Path $PSScriptRoot 'release\win-unpacked\Wayfinder.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw 'Build the app with npm run package from desktop-app first.' }
$previousProject = $env:WAYFINDER_PROJECT_ROOT
$previousRuntime = $env:WAYFINDER_DESKTOP_RUNTIME
try {
    $env:WAYFINDER_PROJECT_ROOT = $projectRoot
    if ($Runtime) { $env:WAYFINDER_DESKTOP_RUNTIME = [System.IO.Path]::GetFullPath($Runtime) }
    # This is the user-invoked interactive application, not a background helper.
    Start-Process -FilePath $executable -WorkingDirectory $projectRoot -WindowStyle Normal
} finally {
    $env:WAYFINDER_PROJECT_ROOT = $previousProject
    $env:WAYFINDER_DESKTOP_RUNTIME = $previousRuntime
}
