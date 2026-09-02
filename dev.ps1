$ErrorActionPreference = "Stop"

$ROOT = $PSScriptRoot

$MINIAPP_DIR = Join-Path $ROOT "front\miniapp"

$API_PORT = 8001
$MINIAPP_PORT = 8000

Write-Host ""
Write-Host "========================================"
Write-Host " Starting Sale Agent Bot Development"
Write-Host "========================================"
Write-Host ""

# --------------------------------------------------
# 1. Start Mini App server
# --------------------------------------------------

Write-Host "[1/4] Starting Mini App on port $MINIAPP_PORT..."

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$MINIAPP_DIR'; python -m http.server $MINIAPP_PORT"
)

Start-Sleep -Seconds 2


# --------------------------------------------------
# 2. Start FastAPI
# --------------------------------------------------

Write-Host "[2/4] Starting FastAPI on port $API_PORT..."

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$ROOT'; .\.venv\Scripts\python.exe -m uvicorn back.src.interfaces.http.app:app --host 127.0.0.1 --port $API_PORT --reload"
)

Start-Sleep -Seconds 3


function Start-CloudflareTunnel {
    param (
        [int]$Port,
        [string]$LogFile,
        [string]$ErrorLogFile,
        [int]$MaxAttempts = 3,
        [int]$StartupTimeoutSeconds = 60
    )

    Remove-Item $LogFile, $ErrorLogFile -Force -ErrorAction SilentlyContinue

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        $tunnel = Start-Process cloudflared `
            -ArgumentList "tunnel --protocol http2 --no-autoupdate --url http://localhost:$Port" `
            -PassThru `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError $ErrorLogFile

        for ($second = 0; $second -lt $StartupTimeoutSeconds; $second++) {
            $output = @(
                Get-Content $LogFile, $ErrorLogFile -Raw -ErrorAction SilentlyContinue
            ) -join "`n"

            if ($output -match "https://[a-zA-Z0-9\-]+\.trycloudflare\.com") {
                return $tunnel
            }

            if ($tunnel.HasExited) {
                break
            }

            Start-Sleep -Seconds 1
        }

        if (-not $tunnel.HasExited) {
            Stop-Process -Id $tunnel.Id -Force
        }

        if ($attempt -lt $MaxAttempts) {
            Write-Host "Cloudflare tunnel retry $attempt/$MaxAttempts after waiting ${StartupTimeoutSeconds}s..." -ForegroundColor Yellow
        }
    }

    return $null
}


# --------------------------------------------------
# 3. Start Mini App Cloudflare Tunnel
# --------------------------------------------------

Write-Host "[3/4] Starting Mini App Cloudflare Tunnel..."

$miniTunnel = Start-CloudflareTunnel `
    -Port $MINIAPP_PORT `
    -LogFile "$ROOT\miniapp-tunnel.log" `
    -ErrorLogFile "$ROOT\miniapp-tunnel-error.log"

Start-Sleep -Seconds 6


# --------------------------------------------------
# 4. Start FastAPI Cloudflare Tunnel
# --------------------------------------------------

Write-Host "[4/4] Starting FastAPI Cloudflare Tunnel..."

$apiTunnel = Start-CloudflareTunnel `
    -Port $API_PORT `
    -LogFile "$ROOT\api-tunnel.log" `
    -ErrorLogFile "$ROOT\api-tunnel-error.log"

Start-Sleep -Seconds 6


# --------------------------------------------------
# Read Cloudflare URLs
# --------------------------------------------------
# --------------------------------------------------
# Wait for Cloudflare URLs
# --------------------------------------------------

Write-Host ""
Write-Host "Waiting for Cloudflare tunnels..."

function Get-TunnelUrl {
    param (
        [string]$LogFile,
        [string]$ErrorLogFile,
        [int]$TimeoutSeconds = 30
    )

    $start = Get-Date

    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSeconds) {

        if ((Test-Path $LogFile) -or (Test-Path $ErrorLogFile)) {

            $content = @(
                Get-Content $LogFile, $ErrorLogFile -Raw -ErrorAction SilentlyContinue
            ) -join "`n"

            if ($content) {

                $match = [regex]::Match(
                    $content,
                    "https://[a-zA-Z0-9\-]+\.trycloudflare\.com"
                )

                if ($match.Success) {
                    return $match.Value
                }
            }
        }

        Start-Sleep -Seconds 1
    }

    return $null
}


$miniUrl = Get-TunnelUrl `
    -LogFile "$ROOT\miniapp-tunnel.log" `
    -ErrorLogFile "$ROOT\miniapp-tunnel-error.log"

$apiUrl = Get-TunnelUrl `
    -LogFile "$ROOT\api-tunnel.log" `
    -ErrorLogFile "$ROOT\api-tunnel-error.log"


if (-not $miniUrl) {

    Write-Host ""
    Write-Host "ERROR: Mini App Cloudflare URL was not found." -ForegroundColor Red
    Write-Host ""

    if (Test-Path "$ROOT\miniapp-tunnel.log") {
        Write-Host "Mini App tunnel log:"
        Get-Content "$ROOT\miniapp-tunnel.log"
    }

    exit 1
}


if (-not $apiUrl) {

    Write-Host ""
    Write-Host "ERROR: FastAPI Cloudflare URL was not found." -ForegroundColor Red
    Write-Host ""

    if (Test-Path "$ROOT\api-tunnel.log") {
        Write-Host "FastAPI tunnel log:"
        Get-Content "$ROOT\api-tunnel.log"
    }

    exit 1
}


Write-Host ""
Write-Host "Mini App Tunnel:"
Write-Host $miniUrl -ForegroundColor Green

Write-Host ""

Write-Host "FastAPI Tunnel:"
Write-Host $apiUrl -ForegroundColor Green
# --------------------------------------------------
# Generate config.js
# --------------------------------------------------

$configPath = Join-Path $MINIAPP_DIR "config.js"

$configContent = @"
window.APP_CONFIG = {
    API_BASE_URL: "$apiUrl"
};
"@

Set-Content `
    -Path $configPath `
    -Value $configContent `
    -Encoding UTF8

$envPath = Join-Path $ROOT ".env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    if ($envContent -match "(?m)^\s*MINI_APP_URL\s*=") {
        $envContent = [regex]::Replace(
            $envContent,
            "(?m)^\s*MINI_APP_URL\s*=.*$",
            "MINI_APP_URL=$miniUrl"
        )
    } else {
        $envContent = $envContent.TrimEnd() + "`r`nMINI_APP_URL=$miniUrl`r`n"
    }
    Set-Content -Path $envPath -Value $envContent -Encoding UTF8
}


# --------------------------------------------------
# Show result
# --------------------------------------------------

Write-Host ""
Write-Host "========================================"
Write-Host " Development environment is running"
Write-Host "========================================"
Write-Host ""

Write-Host "Mini App:"
Write-Host $miniUrl

Write-Host ""

Write-Host "FastAPI:"
Write-Host $apiUrl

Write-Host ""

Write-Host "FastAPI Docs:"
Write-Host "$apiUrl/docs"

Write-Host ""

Write-Host "Config:"
Write-Host $configPath

Write-Host ""
Write-Host "========================================"
Write-Host ""