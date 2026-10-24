$ErrorActionPreference = 'Stop'
$project = 'D:\Opencode_\AI assistant'
$distro = 'Ubuntu-24.04'
$settingsPath = Join-Path $env:APPDATA 'Docker\settings-store.json'
if (-not (Test-Path -LiteralPath $settingsPath)) { throw 'Expected Docker Desktop settings file is missing.' }
$settings = Get-Content -LiteralPath $settingsPath -Raw | ConvertFrom-Json
$localDir = Join-Path $project '.local'
New-Item -ItemType Directory -Force -Path $localDir | Out-Null
$running = @(docker ps --format '{{.Names}}')
if ($LASTEXITCODE -ne 0) { throw 'Docker is not reachable; no settings changed.' }
Copy-Item -LiteralPath $settingsPath -Destination (Join-Path $localDir ('docker-settings-before-' + (Get-Date -Format yyyyMMddHHmmss) + '.json'))
$distros = @()
if ($null -ne $settings.PSObject.Properties['integratedWslDistros']) { $distros = @($settings.integratedWslDistros) }
$distros = @($distros + $distro | Where-Object { $_ } | Select-Object -Unique)
$settings | Add-Member -MemberType NoteProperty -Name integratedWslDistros -Value ([string[]]$distros) -Force
$settings | Add-Member -MemberType NoteProperty -Name wslEngineEnabled -Value $true -Force
# Preserve the default-distro integration setting, including its implicit default.
wsl -d $distro -u assistant -- sh -c 'mkdir -p "$HOME/.docker"'
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the project Docker configuration.' }
wsl --terminate $distro
if ($LASTEXITCODE -ne 0) { throw 'Could not stop the project distro before integration.' }
[IO.File]::WriteAllText($settingsPath, ($settings | ConvertTo-Json -Depth 100) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
Write-Output 'Added Ubuntu-24.04 integration, preserving existing distro settings. Restarting Docker Desktop.'
docker desktop restart
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop restart failed; the original settings backup is in .local.' }
$deadline = (Get-Date).AddMinutes(2)
do {
    docker info --format '{{.ServerVersion}}' 2>$null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 3
} while ((Get-Date) -lt $deadline)
if ($LASTEXITCODE -ne 0) { throw 'Docker engine did not become ready within two minutes.' }
foreach ($name in $running) {
    $isRunning = docker inspect --format '{{.State.Running}}' $name
    if ($LASTEXITCODE -ne 0) { throw ('Existing container is missing: ' + $name) }
    if ($isRunning -ne 'true') {
        docker start $name
        if ($LASTEXITCODE -ne 0) { throw ('Could not restore running container: ' + $name) }
    }
}
wsl -d $distro -u assistant -- docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop integration is still unavailable inside Ubuntu-24.04.' }
docker ps --format '{{.Names}} {{.Status}}'
Write-Output 'Project Docker integration is ready; previously running containers were preserved.'
