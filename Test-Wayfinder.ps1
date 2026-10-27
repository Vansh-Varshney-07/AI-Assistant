param([ValidateSet('Regression','Frontend','Build','NeuralLive','NodeBridge','Packaged','Rendered')][string]$Mode='Regression',[string]$Python)
$ErrorActionPreference='Stop'
$appRoot=Join-Path $PSScriptRoot 'desktop-app'
if(-not $Python){$Python=@($env:WAYFINDER_PYTHON,(Join-Path $PSScriptRoot '.venv/Scripts/python.exe'),'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe')|Where-Object{$_ -and(Test-Path -LiteralPath $_)}|Select-Object -First 1}
$oldPython=$env:WAYFINDER_PYTHON;$oldPlaywright=$env:WAYFINDER_PLAYWRIGHT_MODULE;$oldChrome=$env:WAYFINDER_CHROME
try{
    if($Python){$env:WAYFINDER_PYTHON=$Python}
    $bundled=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json'
    if(-not $env:WAYFINDER_PLAYWRIGHT_MODULE -and(Test-Path -LiteralPath $bundled)){$env:WAYFINDER_PLAYWRIGHT_MODULE=$bundled}
    if(-not $env:WAYFINDER_CHROME){$env:WAYFINDER_CHROME=Join-Path $env:ProgramFiles 'Google/Chrome/Application/chrome.exe'}
    if($Mode -in @('Frontend','Build','Rendered')){
        Push-Location $appRoot
        try{
            if($Mode -eq 'Frontend'){npm run check;if($LASTEXITCODE -ne 0){exit $LASTEXITCODE};npm test -- --reporter=json --outputFile=test-results/ui.json}
            elseif($Mode -eq 'Build'){npm run package}
            else{node scripts/verify-renderer.mjs}
            $result=$LASTEXITCODE
        }finally{Pop-Location}
    }else{
        $options=@{}
        if($Mode -eq 'NeuralLive'){$options.Neural=$true;$options.Live=$true}
        if($Mode -eq 'NodeBridge'){$options.NodeBridge=$true}
        if($Mode -eq 'Packaged'){$options.Packaged=$true}
        & (Join-Path $appRoot 'scripts/Test-Backend.ps1') @options
        $result=$LASTEXITCODE
    }
}finally{$env:WAYFINDER_PYTHON=$oldPython;$env:WAYFINDER_PLAYWRIGHT_MODULE=$oldPlaywright;$env:WAYFINDER_CHROME=$oldChrome}
exit $result
