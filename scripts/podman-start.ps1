param(
  [string]$MachineName = 'podman-machine-default'
)

$ErrorActionPreference = 'Continue'

Write-Host "== Start Podman machine =="
podman machine start $MachineName
podman machine list
podman info
