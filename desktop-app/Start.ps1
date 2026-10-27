param([string]$Runtime, [string]$Python)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$executable = Join-Path $PSScriptRoot 'release\win-unpacked\Wayfinder.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw 'Build the app with npm run package from desktop-app first.' }
$previousProject = $env:WAYFINDER_PROJECT_ROOT
$previousRuntime = $env:WAYFINDER_DESKTOP_RUNTIME
$previousPython = $env:WAYFINDER_PYTHON
try {
    $env:WAYFINDER_PROJECT_ROOT = $projectRoot
    if ($Runtime) { $env:WAYFINDER_DESKTOP_RUNTIME = [System.IO.Path]::GetFullPath($Runtime) }
    if ($Python) {
        if (-not [System.IO.Path]::IsPathRooted($Python) -or -not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Select an existing absolute Python executable. Nothing is installed automatically.' }
        $env:WAYFINDER_PYTHON = $Python
    }
    # This is the user-invoked interactive application, not a background helper.
    Start-Process -FilePath $executable -WorkingDirectory $projectRoot -WindowStyle Normal
} finally {
    $env:WAYFINDER_PROJECT_ROOT = $previousProject
    $env:WAYFINDER_DESKTOP_RUNTIME = $previousRuntime
    $env:WAYFINDER_PYTHON = $previousPython
}
