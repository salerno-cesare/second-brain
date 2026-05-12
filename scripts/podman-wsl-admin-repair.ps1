param(
  [string]$TargetUserProfile = 'C:\Users\ESALERC1Y',
  [string]$MachineName = 'podman-machine-default'
)

$ErrorActionPreference = 'Continue'

function Test-IsAdmin {
  $current = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($current)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Stop-ServiceHard {
  param([string]$Name, [int]$TimeoutSeconds = 20)

  Write-Host "Stopping service $Name..."
  $service = Get-Service $Name -ErrorAction SilentlyContinue
  if (-not $service) {
    Write-Warning "Service not found: $Name"
    return
  }

  Stop-Service $Name -Force -ErrorAction Continue
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    Start-Sleep -Seconds 1
    $service = Get-Service $Name -ErrorAction SilentlyContinue
    if ($service.Status -eq 'Stopped') {
      Write-Host "$Name stopped"
      return
    }
  } while ((Get-Date) -lt $deadline)

  $cim = Get-CimInstance Win32_Service -Filter "Name='$Name'" -ErrorAction SilentlyContinue
  if ($cim -and $cim.ProcessId -and $cim.ProcessId -ne 0) {
    Write-Warning "$Name did not stop; killing PID $($cim.ProcessId)"
    Stop-Process -Id $cim.ProcessId -Force -ErrorAction Continue
    Start-Sleep -Seconds 3
  }
}

Write-Host "== Admin WSL service repair =="
Write-Host "User: $([Security.Principal.WindowsIdentity]::GetCurrent().Name)"
Write-Host "IsAdmin: $(Test-IsAdmin)"

if (-not (Test-IsAdmin)) {
  Write-Error "Run this script from PowerShell as Administrator."
  exit 1
}

Get-Process 'Podman Desktop', 'podman', 'wsl', 'gvproxy', 'qemu-system-x86_64', 'ssh' -ErrorAction SilentlyContinue |
  Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

wsl --shutdown

Stop-ServiceHard 'WSLService' 20
Stop-ServiceHard 'vmcompute' 20
Stop-ServiceHard 'HNS' 20

Write-Host "Starting services..."
Start-Service vmcompute -ErrorAction Continue
Start-Service HNS -ErrorAction Continue
Start-Service WSLService -ErrorAction Continue
Start-Sleep -Seconds 5
Get-Service WSLService, vmcompute, HNS -ErrorAction SilentlyContinue | Format-Table -AutoSize

Write-Host "Updating WSL if an update is available..."
wsl --update

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$markers = @(
  "$TargetUserProfile\.local\share\containers\podman\machine\wsl\$MachineName\win-sshproxy.tid",
  "$TargetUserProfile\.config\containers\podman\machine\wsl\$MachineName.lock"
)

foreach ($marker in $markers) {
  if (Test-Path -LiteralPath $marker) {
    Rename-Item -LiteralPath $marker -NewName "$(Split-Path -Leaf $marker).stale-$stamp" -ErrorAction Continue
    Write-Host "Renamed stale marker: $marker"
  }
}

Write-Host "Repair completed. Now run scripts\podman-start.ps1 from the normal user session."
