param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$WikiArguments
)

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& "$PSScriptRoot\ensure-venv.ps1"

$projectRoot = (Get-Location).Path
$env:WIKI_SOURCE_DIR = Join-Path $projectRoot "knowledge"
$env:WIKI_RAW_DIR = Join-Path $projectRoot "knowledge\raw"
$env:WIKI_OUTPUT_DIR = Join-Path $projectRoot "knowledge\wiki"
$env:CODEX_COMMAND = if (Get-Command codex.cmd -ErrorAction SilentlyContinue) { "codex.cmd" } else { "codex" }
$env:CODEX_SHELL = "powershell"
$env:PYTHONPATH = $projectRoot
$env:PYTHONUNBUFFERED = "1"

& ".\.venv\Scripts\python.exe" -m app.cli @WikiArguments
exit $LASTEXITCODE
