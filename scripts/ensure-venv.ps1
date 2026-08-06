$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

$env:UV_LINK_MODE = "copy"

$uv = Get-Command uv -ErrorAction SilentlyContinue

if ($uv) {
    if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
        uv venv .venv
    }
    uv pip install -r requirements.txt --python ".venv\Scripts\python.exe"
}
else {
    Write-Host "uv non trovato: uso python -m venv + pip come fallback." -ForegroundColor Yellow

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and ($python.Source -notmatch "WindowsApps")) {
        $pythonExe = $python.Source
        $pythonArgs = @()
    }
    else {
        $py = Get-Command py -ErrorAction SilentlyContinue
        if (-not $py) {
            throw "Nessun interprete Python trovato (ne' 'python' ne' 'py'). Installa Python 3 oppure uv (https://github.com/astral-sh/uv)."
        }
        $pythonExe = $py.Source
        $pythonArgs = @("-3")
    }

    if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
        & $pythonExe @pythonArgs -m venv .venv
    }

    $venvPython = ".venv\Scripts\python.exe"
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
}
