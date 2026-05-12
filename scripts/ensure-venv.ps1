$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$env:UV_LINK_MODE = "copy"

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    uv venv .venv
}

uv pip install -r requirements.txt --python ".venv\Scripts\python.exe"
