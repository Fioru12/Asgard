#!/bin/bash
# =============================================================================
# Asgard Express Setup — Installazione guidata per PMI in 5 minuti
# https://github.com/asgard-security
# =============================================================================
# Questo script:
#   1) Raccoglie le informazioni minime per proteggere la tua PMI
#   2) Genera automaticamente il file .env e avvia lo stack Docker
#   3) Non salva mai le credenziali in chiaro nel repository
#
# Uso: ./setup-express.sh
# =============================================================================

set -euo pipefail

# Colori per output leggibile
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}🛡️  ASGARD EXPRESS — Setup Rapido per PMI${NC}"
echo "============================================="
echo ""
echo "Questo setup ti permette di proteggere la tua azienda in meno di 10 minuti."
echo "Non verranno mai salvate credenziali sensibili nel repository.".
echo ""

# ---------------------------------------------------------------------------
# 1. Raccogliamo informazioni minime
# ---------------------------------------------------------------------------
echo -e "${YELLOW}Step 1/3: Informazioni di base${NC}"
echo ""

# Percorso log di sistema
read -rp "📁 Qual è il percorso dei log di sistema? [/var/log]: " INPUT
HEIMDALL_WATCH_PATHS="${INPUT:-/var/log}"

# Porta SSH pubblica
read -rp "🔌 Qual è la porta SSH pubblica? [22]: " INPUT
HEIMDALL_SSH_PORT="${INPUT:-22}"

# Email aziendale per notifiche
read -rp "📧 Inserisci l'email aziendale per le notifiche (lascia vuoto se non necessario): " INPUT
GJALLARHORN_CONTACT_EMAIL="${INPUT:-admin@${HEIMDALL_SSH_PORT:-22}.com}"
# Se è stato lasciato vuoto, usiamo un valore placeholder
if [ -z "$GJALLARHORN_CONTACT_EMAIL" ]; then
  GJALLARHORN_CONTACT_EMAIL="admin@azienda.local"
fi

# Dominio aziendale
read -rp "🌐 Inserisci il dominio aziendale (es. azienda.local) [localhost]: " INPUT
ASGARD_DOMAIN="${INPUT:-localhost}"

# Chiave API opzionale
echo ""
echo -e "${BLUE}🔐 Generazione della chiave API segreta...${NC}"
RAGNAROK_API_KEY=$(openssl rand -hex 32)
echo -e "${GREEN}✅ Chiave API generata (non verrà mostrata di nuovo)${NC}"

echo ""
echo -e "${YELLOW}Step 2/3: Generazione configurazione...${NC}"

# ---------------------------------------------------------------------------
# 2. Scriviamo il .env seguro
# ---------------------------------------------------------------------------
cat > .env <<EOF
# ========================================
# ASGARD EXPRESS — Configurazione PMI
# Generata il $(date)
# ========================================

# Chiavi API (segreto — non committare mai!)
RAGNAROK_API_KEY=${RAGNAROK_API_KEY}

# Heimdall (HIDS)
HEIMDALL_WATCH_PATHS=${HEIMDALL_WATCH_PATHS}
HEIMDALL_SSH_PORT=${HEIMDALL_SSH_PORT}

# Gjallarhorn (notifiche)
GJALLARHORN_CONTACT_EMAIL=${GJALLARHORN_CONTACT_EMAIL}

# Ragnarok (orchestrazione)
ASGARD_DOMAIN=${ASGARD_DOMAIN}

# RAG Engine
ASGARD_RAG_DB_PATH=/tmp/asgard-rag-db
RAG_AUTO_INDEX_MINUTES=15
RAG_ANOMALY_WATCH_MINUTES=5
EOF

echo -e "${GREEN}✅ File .env generato${NC}"

# Aggiungiamo una riga al .gitignore se esiste
if [ -f .gitignore ]; then
  if ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    echo "*.log" >> .gitignore
  fi
fi

echo ""
echo -e "${YELLOW}Step 3/3: Avvio dello stack Docker...${NC}"
echo ""

# ---------------------------------------------------------------------------
# 3. Avviamo lo stack
# ---------------------------------------------------------------------------
if command -v docker-compose &>/dev/null; then
    compose_cmd="docker-compose"
elif docker compose version &>/dev/null; then
    compose_cmd="docker compose"
else
    echo -e "${RED}❌ Docker non è installato o Docker Compose non è disponibile${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Avvio container...${NC}"
sleep 1

# Usa il file specifico per l'express
if [ -f docker-compose-express.yml ]; then
    ${compose_cmd} -f docker-compose-express.yml up -d
else
    ${compose_cmd} up -d
fi

# ---------------------------------------------------------------------------
# 4. Output finale
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}🎉 Setup completato con successo!${NC}"
echo "============================================="
echo ""
echo -e "📊 Accesso alla dashboard: ${BLUE}http://localhost:8080/dashboard${NC}"
echo -e "🛡️  Monitoraggio HIDS attivo su porta: ${BLUE}:${HEIMDALL_SSH_PORT}${NC}"
echo -e "📧 Notifiche configurate per: ${GREEN}${GJALLARHORN_CONTACT_EMAIL}${NC}"
echo -e "📈 Analisi intelligente (RAG) pronta"
echo ""
echo -e "📝 Prossimi passi:"
echo   "1. Apri il browser su http://localhost:8080/dashboard"
echo   "2. Usa la chiave API mostrata sopra per accedere alle API"
echo   "3. Guarda la card 'Security Score' nella dashboard per verificare che tutto funzioni"
echo ""
echo -e "${YELLOW}ℹ️  Per fermare: docker compose down${NC}"
echo ""
