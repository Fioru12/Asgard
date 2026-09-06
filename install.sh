# Asgard Suite — Guided Installer (Windows / Linux / macOS)
# Usage:
#   install.sh            → interactive, builds and starts everything
#   install.sh --dry-run  → show what would be done, no changes
#   install.sh --status   → show running services
#   install.sh --stop     → stop all services
# Requirements: Docker Desktop (or Docker Engine + Compose plugin)

set -euo pipefail

DRY_RUN=false
STATUS_ONLY=false
STOP_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=true ;;
    --status)   STATUS_ONLY=true ;;
    --stop)     STOP_ONLY=true ;;
    -h|--help)  head -12 "$0" | grep -E '^#' | sed 's/^#\s*//'; exit 0 ;;
  esac
done

COMPOSE_FILE="docker-compose.yml"
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
echo "  docker compose -p asgard logs -f  → follow logs"
echo ""
