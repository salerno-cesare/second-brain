$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

& "$PSScriptRoot\ensure-venv.ps1"
& "$PSScriptRoot\open-browser.ps1"

$env:WIKI_SOURCE_DIR = Join-Path (Get-Location) "knowledge"
$env:WIKI_RAW_DIR = Join-Path (Get-Location) "knowledge\raw"
$env:WIKI_OUTPUT_DIR = Join-Path (Get-Location) "knowledge\wiki"
$codexCommand = if (Get-Command codex.cmd -ErrorAction SilentlyContinue) { "codex.cmd" } else { "codex" }
$env:CODEX_COMMAND = $codexCommand
$env:CODEX_SHELL = "powershell"
$env:APP_HOST = "127.0.0.1"
$env:APP_PORT = "8000"
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONUNBUFFERED = "1"
$env:WATCHFILES_FORCE_POLLING = "true"

.\.venv\Scripts\python.exe -m uvicorn app.main:app `
    --reload `
    --reload-dir app `
    --reload-include "*.py" `
    --reload-include "*.html" `
    --reload-include "*.css" `
    --reload-include "*.js" `
    --host 127.0.0.1 `
    --port 8000
