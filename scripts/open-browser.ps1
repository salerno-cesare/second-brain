param(
    [string]$Url = "http://127.0.0.1:8000",
    [int]$TimeoutSeconds = 45,
    [int]$PollMilliseconds = 500
)

$ErrorActionPreference = "Stop"

$chromeCandidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

$chrome = $chromeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $chrome) {
    $chromeCommand = Get-Command chrome.exe -ErrorAction SilentlyContinue
    if ($chromeCommand) {
        $chrome = $chromeCommand.Source
    }
}

if (-not $chrome) {
    throw "Chrome non trovato. Installa Google Chrome o aggiungi chrome.exe al PATH."
}

$launcher = {
    param(
        [string]$TargetUrl,
        [string]$ChromePath,
        [int]$WaitSeconds,
        [int]$SleepMilliseconds
    )

    $ErrorActionPreference = "SilentlyContinue"
    $deadline = (Get-Date).AddSeconds($WaitSeconds)

    do {
        $response = Invoke-WebRequest -Uri $TargetUrl -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            break
        }

        Start-Sleep -Milliseconds $SleepMilliseconds
    } while ((Get-Date) -lt $deadline)

    Start-Process -FilePath $ChromePath -ArgumentList $TargetUrl
}

$escapedUrl = $Url.Replace("'", "''")
$escapedChrome = $chrome.Replace("'", "''")
$command = @"
& {
$launcher
} -TargetUrl '$escapedUrl' -ChromePath '$escapedChrome' -WaitSeconds $TimeoutSeconds -SleepMilliseconds $PollMilliseconds
"@

$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))

Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-EncodedCommand",
    $encodedCommand
) -WindowStyle Hidden
