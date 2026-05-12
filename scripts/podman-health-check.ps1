param(
  [int]$TimeoutSeconds = 15
)

$ErrorActionPreference = 'Continue'

function Invoke-TimedExe {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [string[]]$ArgumentList = @(),
    [int]$TimeoutSeconds = 15
  )

  $safeName = $FilePath -replace '[^a-zA-Z0-9_.-]', '_'
  $id = [guid]::NewGuid().ToString('N')
  $out = Join-Path $env:TEMP "podman-health-$safeName-$id.out"
  $err = Join-Path $env:TEMP "podman-health-$safeName-$id.err"

  Write-Host "> $FilePath $($ArgumentList -join ' ')"
  try {
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
      Write-Warning "TIMEOUT after ${TimeoutSeconds}s"
      try { $process.Kill($true) } catch { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
      return $false
    }

    Write-Host "ExitCode: $($process.ExitCode)"
    if (Test-Path $out) { Get-Content $out -ErrorAction SilentlyContinue }
    if (Test-Path $err) { Get-Content $err -ErrorAction SilentlyContinue }
    return ($process.ExitCode -eq 0)
  } finally {
    Remove-Item $out, $err -Force -ErrorAction SilentlyContinue
  }
}

Write-Host "== Podman / WSL health check =="
Write-Host "User: $(whoami)"

$ok = $true
$ok = (Invoke-TimedExe 'wsl.exe' @('--status') $TimeoutSeconds) -and $ok
$ok = (Invoke-TimedExe 'wsl.exe' @('-l', '-v') $TimeoutSeconds) -and $ok
$ok = (Invoke-TimedExe 'podman.exe' @('machine', 'list') $TimeoutSeconds) -and $ok
$ok = (Invoke-TimedExe 'podman.exe' @('info') ($TimeoutSeconds * 2)) -and $ok

Write-Host "`nRelevant processes:"
Get-Process | Where-Object { $_.ProcessName -match 'Podman Desktop|podman|wsl|vmmem|win-sshproxy|wslhost|wslrelay' } |
  Select-Object ProcessName, Id, CPU, StartTime |
  Sort-Object ProcessName, Id |
  Format-Table -AutoSize

if ($ok) {
  Write-Host "`nStatus: OK"
  exit 0
}

Write-Warning "Status: not healthy. If WSL commands timed out, run scripts\podman-wsl-admin-repair.ps1 from an elevated PowerShell, then run scripts\podman-start.ps1."
exit 1
