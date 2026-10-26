param([string]$Runtime,[string]$Python,[switch]$Demo,[switch]$Check)
$ErrorActionPreference='Stop'
$appRoot=Join-Path $PSScriptRoot 'desktop-app'
if($Check){
    [pscustomobject]@{executable_present=(Test-Path -LiteralPath (Join-Path $appRoot 'release/win-unpacked/Wayfinder.exe'));project=$PSScriptRoot;interface='GitHub Wayfinder Electron UI';native_driver_enabled=$false;requires='Existing Python, FalkorDB, cached embeddings; managed Hermes for tasks'}|Format-List
    exit 0
}
if($Demo){& (Join-Path $appRoot 'scripts/Start-Demo.ps1') -Python $Python;exit $LASTEXITCODE}
$options=@{}
if($Runtime){$options.Runtime=$Runtime}
if($Python){$options.Python=$Python}
& (Join-Path $appRoot 'Start.ps1') @options
