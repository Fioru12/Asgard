# Asgard Suite — Guided Installer (Windows / Linux / macOS)
# Usage:
#   install.sh            → interactive, builds and starts everything
#   install.sh --monitoring → also start the optional monitoring stack (Prometheus/Alertmanager/Loki/Grafana)
#   install.sh --dry-run  → show what would be done, no changes
#   install.sh --status   → show running services
#   install.sh --stop     → stop all services
# Requirements: Docker Desktop (or Docker Engine + Compose plugin)

set -euo pipefail

DRY_RUN=false
STATUS_ONLY=false
STOP_ONLY=false
MONITORING=false

for arg in "$@"; do
  case "$arg" in
    --dry-run)     DRY_RUN=true ;;
    --status)      STATUS_ONLY=true ;;
    --stop)        STOP_ONLY=true ;;
    --monitoring)  MONITORING=true ;;
    -h|--help)  head -14 "$0" | grep -E '^#' | sed 's/^#\s*//'; exit 0 ;;
  esac
done

COMPOSE_FILE="docker-compose.yml"
MONITORING_COMPOSE_FILE="monitoring/docker-compose.monitoring.yml"
PROJECT_NAME="asgard"

run() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

echo ""
echo "=============================================="
echo "  ASGARD SUITE — Guided Installer"
echo "=============================================="
echo ""

if [ "$STATUS_ONLY" = true ]; then
  echo "Running services:"
  docker compose -p "$PROJECT_NAME" ps
  exit 0
fi

if [ "$STOP_ONLY" = true ]; then
  echo "Stopping all services..."
  run docker compose -p "$PROJECT_NAME" down
  echo "Stopped."
  exit 0
fi

# --- Docker availability check ---
if ! command -v docker &>/dev/null; then
  echo "ERROR: Docker is not installed or not in PATH."
  echo "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  exit 1
fi

if ! docker compose version &>/dev/null && ! docker compose &>/dev/null; then
  echo "ERROR: Docker Compose plugin not found."
  echo "Enable it in Docker Desktop → Settings → General → 'Use Docker Compose V2'"
  exit 1
fi

echo "[1/5] Docker OK"

# --- Submodule check ---
# The 9 module directories are git submodules; a plain `git clone` (without
# --recursive) leaves them as empty folders, which breaks the Docker build
# with a confusing "no such file" error. Detect and self-heal instead of
# letting that happen.
if [ ! -f "Heimdall/main.py" ]; then
  echo "[i] Module submodules look empty — fetching them now..."
  if [ -d .git ]; then
    git submodule update --init --recursive
  else
    echo "ERROR: Heimdall/main.py not found and this isn't a git checkout,"
    echo "so submodules can't be fetched automatically. Re-clone with:"
    echo "  git clone --recursive https://github.com/Fioru12/Asgard.git"
    exit 1
  fi
fi

# --- Build image ---
echo "[2/5] Building asgard-suite image (this may take a few minutes)..."
run docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache

# --- Launch services ---
echo "[3/5] Starting all services..."
run docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d gjallarhorn heimdall bifrost forseti mjolnir yggdrasil fenrir sleipnir ragnarok

# --- Wait for Ragnarök health ---
echo "[4/5] Waiting for Ragnarök to be healthy..."
for i in $(seq 1 30); do
  if docker compose -p "$PROJECT_NAME" ps ragnarok 2>/dev/null | grep -q "healthy"; then
    echo "  ✓ Ragnarök is healthy"
    break
  fi
  sleep 2
done

# --- Optional monitoring stack ---
if [ "$MONITORING" = true ]; then
  echo ""
  echo "[5/5] Starting monitoring stack (Prometheus/Alertmanager/Loki/Grafana)..."
  run docker compose -f "$COMPOSE_FILE" -f "$MONITORING_COMPOSE_FILE" -p "$PROJECT_NAME" up -d prometheus alertmanager loki grafana
fi

# --- Show status + admin setup URL ---
echo ""
echo "=============================================="
echo "  ✓ Asgard Suite is running!"
echo "=============================================="
echo ""
echo "  Dashboard:     http://localhost:8080/dashboard"
echo "  Ragnarök API:  http://localhost:8080"
echo "  Heimdall:      http://localhost:18000"
echo "  Gjallarhorn:   http://localhost:8090"
echo "  Forseti:       http://localhost:8091"
echo "  Bifrost:       http://localhost:8092"
echo ""
echo "First-time setup:"
echo "  1. Open the Dashboard in your browser"
echo "  2. The 'Initial Setup' wizard will appear"
echo "  3. Create your admin account (password shown in console)"
echo ""
echo "  Or check the admin password directly:"
echo "    docker logs asgard-ragnarok 2>&1 | grep -A 4 'default admin'"
echo ""
echo "Useful commands:"
echo "  install.sh --status    → check running services"
echo "  install.sh --stop      → stop all services"
echo "  install.sh --monitoring → start the full suite + monitoring stack (Prometheus :9090, Grafana :3000, Loki :3100)"
echo "  docker compose -p asgard logs -f  → follow logs"
echo ""
