# Asgard Suite — Guided Installer (Windows PowerShell)
# Usage:
#   .\install.ps1            → interactive, builds and starts everything
#   .\install.ps1 -Monitoring → also start the optional monitoring stack (Prometheus/Alertmanager/Loki/Grafana)
#   .\install.ps1 -DryRun    → show what would be done, no changes
#   .\install.ps1 -Status    → show running services
#   .\install.ps1 -Stop      → stop all services
# Requirements: Docker Desktop for Windows

param(
    [switch]$DryRun,
    [switch]$Status,
    [switch]$Stop,
    [switch]$Monitoring
)

$ComposeFile = "docker-compose.yml"
$MonitoringComposeFile = "monitoring\docker-compose.monitoring.yml"
$ProjectName = "asgard"

function Run-Command {
    param([scriptblock]$ScriptBlock)
    if ($DryRun) {
        Write-Host "  [dry-run] $($ScriptBlock.ToString().Trim())" -ForegroundColor Cyan
    } else {
        & $ScriptBlock
    }
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor White
Write-Host "  ASGARD SUITE — Guided Installer (Windows)" -ForegroundColor White
Write-Host "==============================================" -ForegroundColor White
Write-Host ""

if ($Status) {
    Write-Host "Running services:"
    docker compose -p $ProjectName ps
    exit 0
}

if ($Stop) {
    Write-Host "Stopping all services..."
    Run-Command { docker compose -p $ProjectName down }
    Write-Host "Stopped."
    exit 0
}

# --- Docker availability check ---
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
}

# Check compose
$composeCheck = docker compose version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Compose plugin not found." -ForegroundColor Red
    Write-Host "Enable it in Docker Desktop -> Settings -> General -> 'Use Docker Compose V2'"
    exit 1
}

Write-Host "[1/5] Docker OK" -ForegroundColor Green

# --- Submodule check ---
# The 9 module directories are git submodules; a plain "git clone" (without
# --recursive) leaves them as empty folders, which breaks the Docker build
# with a confusing "no such file" error. Detect and self-heal instead of
# letting that happen.
if (-not (Test-Path "Heimdall\main.py")) {
    Write-Host "[i] Module submodules look empty -- fetching them now..." -ForegroundColor Yellow
    if (Test-Path ".git") {
        git submodule update --init --recursive
    } else {
        Write-Host "ERROR: Heimdall\main.py not found and this isn't a git checkout," -ForegroundColor Red
        Write-Host "so submodules can't be fetched automatically. Re-clone with:"
        Write-Host "  git clone --recursive https://github.com/Fioru12/Asgard.git"
        exit 1
    }
}

# --- Build image ---
Write-Host "[2/5] Building asgard-suite image (this may take a few minutes)..."
Run-Command { docker compose -f $ComposeFile -p $ProjectName build --no-cache }

# --- Launch services ---
Write-Host "[3/5] Starting all services..."
Run-Command { docker compose -f $ComposeFile -p $ProjectName up -d gjallarhorn heimdall bifrost forseti mjolnir yggdrasil fenrir sleipnir ragnarok }

# --- Wait for Ragnarök health ---
Write-Host "[4/5] Waiting for Ragnarök to be healthy..."
$healthy = $false
for ($i = 1; $i -le 30; $i++) {
    $psOutput = docker compose -p $ProjectName ps ragnarok 2>&1
    if ($psOutput -match "healthy") {
        Write-Host "  Ragnarok is healthy" -ForegroundColor Green
        $healthy = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    Write-Host "  WARNING: Ragnarok did not become healthy within 60 seconds." -ForegroundColor Yellow
    Write-Host "  Check logs with: docker compose -p asgard logs -f ragnarok"
}

# --- Optional monitoring stack ---
if ($Monitoring) {
    Write-Host ""
    Write-Host "[5/5] Starting monitoring stack (Prometheus/Alertmanager/Loki/Grafana)..."
    Run-Command { docker compose -f $ComposeFile -f $MonitoringComposeFile -p $ProjectName up -d prometheus alertmanager loki grafana }
}

# --- Show status + admin setup URL ---
Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Asgard Suite is running!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Dashboard:     http://localhost:8080/dashboard"
Write-Host "  Ragnarök API:  http://localhost:8080"
Write-Host "  Heimdall:      http://localhost:18000"
Write-Host "  Gjallarhorn:   http://localhost:8090"
Write-Host "  Forseti:       http://localhost:8091"
Write-Host "  Bifrost:       http://localhost:8092"
Write-Host ""
Write-Host "First-time setup:" -ForegroundColor Yellow
Write-Host "  1. Open the Dashboard in your browser"
Write-Host "  2. The 'Initial Setup' wizard will appear"
Write-Host "  3. Create your admin account (password shown in console)"
Write-Host ""
Write-Host "  Or check the admin password directly:" -ForegroundColor Yellow
Write-Host '    docker logs asgard-ragnarok 2>&1 | Select-String "default admin" -Context 0,4'
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  .\install.ps1 -Status    -> check running services"
Write-Host "  .\install.ps1 -Stop      -> stop all services"
Write-Host "  .\install.ps1 -Monitoring -> start the full suite + monitoring stack (Prometheus :9090, Grafana :3000, Loki :3100)"
Write-Host "  docker compose -p asgard logs -f  -> follow logs"
Write-Host ""
