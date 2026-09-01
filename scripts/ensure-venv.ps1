$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$projectRoot = (Get-Location).Path
$venvPath = ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirementsFile = "requirements.txt"
$stampFile = Join-Path $venvPath ".requirements.sha256"

$toolsDir = Join-Path $projectRoot "tools"
$uvDir = Join-Path $toolsDir "uv"
$uvExe = Join-Path $uvDir "uv.exe"
$uvPythonDir = Join-Path $toolsDir "python"
$uvCacheDir = Join-Path $projectRoot ".uv-cache"
$pythonVersion = "3.12"

$env:UV_LINK_MODE = "copy"
$env:UV_PYTHON_INSTALL_DIR = $uvPythonDir
$env:UV_CACHE_DIR = $uvCacheDir
$env:UV_NO_MODIFY_PATH = "1"
$env:UV_TOOL_DIR = Join-Path $toolsDir "uv-tools"
$env:UV_TOOL_BIN_DIR = Join-Path $toolsDir "uv-tools\bin"

New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
New-Item -ItemType Directory -Force -Path $uvDir | Out-Null
New-Item -ItemType Directory -Force -Path $uvPythonDir | Out-Null
New-Item -ItemType Directory -Force -Path $uvCacheDir | Out-Null

function Get-FileHashHex {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Get-UvAssetName {
    $arch = $env:PROCESSOR_ARCHITECTURE
    switch ($arch) {
        "AMD64" { return "uv-x86_64-pc-windows-msvc.zip" }
        "ARM64" { return "uv-aarch64-pc-windows-msvc.zip" }
        "x86"   { return "uv-i686-pc-windows-msvc.zip" }
        default { return "uv-x86_64-pc-windows-msvc.zip" }
    }
}

function Install-UvPortable {
    if (Test-Path -LiteralPath $uvExe) { return }

    $asset = Get-UvAssetName
    $url = "https://github.com/astral-sh/uv/releases/latest/download/$asset"
    $tmpZip = Join-Path $env:TEMP ("uv-" + [guid]::NewGuid().ToString("N") + ".zip")
    $tmpExtract = Join-Path $env:TEMP ("uv-" + [guid]::NewGuid().ToString("N"))

    Write-Host "[ensure-venv] Download uv portable da $url ..."
    $prevProgress = $ProgressPreference
    $ProgressPreference = "SilentlyContinue"
    try {
        Invoke-WebRequest -Uri $url -OutFile $tmpZip -UseBasicParsing
        Expand-Archive -LiteralPath $tmpZip -DestinationPath $tmpExtract -Force

        $found = Get-ChildItem -LiteralPath $tmpExtract -Recurse -Filter "uv.exe" | Select-Object -First 1
        if (-not $found) { throw "uv.exe non trovato nell'archivio scaricato." }
        Copy-Item -LiteralPath $found.FullName -Destination $uvExe -Force

        $foundUvx = Get-ChildItem -LiteralPath $tmpExtract -Recurse -Filter "uvx.exe" | Select-Object -First 1
        if ($foundUvx) {
            Copy-Item -LiteralPath $foundUvx.FullName -Destination (Join-Path $uvDir "uvx.exe") -Force
        }
    } catch {
        throw "Download/estrazione uv fallita: $($_.Exception.Message)"
    } finally {
        $ProgressPreference = $prevProgress
        Remove-Item -LiteralPath $tmpZip -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $tmpExtract -Recurse -Force -ErrorAction SilentlyContinue
    }

    if (-not (Test-Path -LiteralPath $uvExe)) {
        throw "uv non installato correttamente in $uvExe"
    }
    Write-Host "[ensure-venv] uv portable installato in $uvExe"
}

Install-UvPortable

function Test-Executable {
    param([string]$Exe, [string[]]$ExeArgs)
    if (-not (Test-Path -LiteralPath $Exe)) { return $false }
    try {
        & $Exe @ExeArgs *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

if (-not (Test-Executable -Exe $uvExe -ExeArgs @("--version"))) {
    Write-Host "[ensure-venv] uv.exe non funzionante, ridownload..."
    Remove-Item -LiteralPath $uvExe -Force -ErrorAction SilentlyContinue
    Install-UvPortable
    if (-not (Test-Executable -Exe $uvExe -ExeArgs @("--version"))) {
        throw "uv.exe non eseguibile dopo il ridownload."
    }
}

if ((Test-Path -LiteralPath $venvPython) -and -not (Test-Executable -Exe $venvPython -ExeArgs @("--version"))) {
    Write-Host "[ensure-venv] Venv corrotto o Python di riferimento mancante. Rigenero .venv..."
    Remove-Item -LiteralPath $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $stampFile -Force -ErrorAction SilentlyContinue
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "[ensure-venv] Creazione ambiente virtuale portable in $venvPath (Python $pythonVersion)..."
    if (Test-Path -LiteralPath $venvPath) {
        Remove-Item -LiteralPath $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    & $uvExe venv --python $pythonVersion $venvPath
    if ($LASTEXITCODE -ne 0) { throw "uv venv fallito (exit $LASTEXITCODE)." }
}

if (-not (Test-Executable -Exe $venvPython -ExeArgs @("--version"))) {
    throw "Ambiente virtuale non valido: $venvPython non eseguibile."
}

$sentinelModule = "fastapi"
$sentinelOk = $false
try {
    & $venvPython -c "import $sentinelModule" *> $null
    $sentinelOk = ($LASTEXITCODE -eq 0)
} catch { $sentinelOk = $false }

$currentHash = Get-FileHashHex -Path $requirementsFile
$storedHash = if (Test-Path -LiteralPath $stampFile) { (Get-Content -LiteralPath $stampFile -Raw).Trim() } else { $null }

if ($sentinelOk -and $currentHash -and $currentHash -eq $storedHash) {
    Write-Host "[ensure-venv] Dipendenze gia' aggiornate (hash coincidente). Skip install."
    return
}

if (-not $sentinelOk) {
    Write-Host "[ensure-venv] Dipendenze mancanti nel venv, reinstallo..."
}

Write-Host "[ensure-venv] Installazione dipendenze da $requirementsFile..."
& $uvExe pip install -r $requirementsFile --python $venvPython
if ($LASTEXITCODE -ne 0) { throw "uv pip install fallito (exit $LASTEXITCODE)." }

if ($currentHash) {
    Set-Content -LiteralPath $stampFile -Value $currentHash -NoNewline
}

Write-Host "[ensure-venv] Ambiente portable pronto."
