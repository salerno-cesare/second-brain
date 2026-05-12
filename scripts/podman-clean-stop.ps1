param(
  [string]$MachineName = 'podman-machine-default',
  [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = 'Continue'

function Invoke-TimedExe {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [string[]]$ArgumentList = @(),
    [int]$TimeoutSeconds = 30
  )

  $safeName = $FilePath -replace '[^a-zA-Z0-9_.-]', '_'
  $id = [guid]::NewGuid().ToString('N')
  $out = Join-Path $env:TEMP "podman-stop-$safeName-$id.out"
  $err = Join-Path $env:TEMP "podman-stop-$safeName-$id.err"

  Write-Host "> $FilePath $($ArgumentList -join ' ')"
  try {
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
      Write-Warning "TIMEOUT after ${TimeoutSeconds}s"
      try { $process.Kill($true) } catch { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
      return $false
    }

    if (Test-Path $out) { Get-Content $out -ErrorAction SilentlyContinue }
    if (Test-Path $err) { Get-Content $err -ErrorAction SilentlyContinue }
    return ($process.ExitCode -eq 0)
  } finally {
    Remove-Item $out, $err -Force -ErrorAction SilentlyContinue
  }
}

Write-Host "== Clean Podman / WSL stop =="
Write-Host "Closing Podman Desktop..."
Get-Process 'Podman Desktop' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Invoke-TimedExe 'podman.exe' @('machine', 'stop', $MachineName) $TimeoutSeconds | Out-Null
Invoke-TimedExe 'wsl.exe' @('--shutdown') 20 | Out-Null

# These marker files can survive an interrupted start/stop and make Podman believe
# an SSH proxy or machine lock is still active.
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$markers = @(
  "$env:USERPROFILE\.local\share\containers\podman\machine\wsl\$MachineName\win-sshproxy.tid",
  "$env:USERPROFILE\.config\containers\podman\machine\wsl\$MachineName.lock"
)

foreach ($marker in $markers) {
  if (Test-Path -LiteralPath $marker) {
    Rename-Item -LiteralPath $marker -NewName "$(Split-Path -Leaf $marker).stale-$stamp" -ErrorAction Continue
    Write-Host "Renamed stale marker: $marker"
  }
}

Write-Host "Done."
