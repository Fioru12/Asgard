## Backup & restore

Every persistent store (auth DB, audit trail, RAG vector index, conversation memory, security score history) can be backed up to a single zip archive containing a `manifest.json` with the sha256 of each entry. Restores are refused unless the archive verifies against the manifest — a corrupted backup can never silently overwrite live data. Archives are saved to `backend/backups/`. After a restore, restart the backend so live connections pick up the restored data.

## Getting started

New to Asgard? Follow the [30-day adoption guide](docs/ADOPTION_GUIDE.md) — a gradual path from "just installed" to "operational in production" without skipping steps.

# Ragnarök

### **The Asgard Suite — AI-Powered SOC Orchestrator**

![Tauri](https://img.shields.io/badge/Tauri-24C8DB?style=for-the-badge&logo=tauri&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-ChromaDB%20%2B%20FastEmbed-8B5CF6?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

> **Ragnarök** is the crown jewel of the Asgard Suite. It is an AI-powered desktop SOC Orchestrator built with **Tauri** (Rust + web frontend) and a **Python FastAPI** backend. It unifies all 5 Asgard security tools (Heimdall, Mjolnir, Bifrost, Yggdrasil, Fenrir) into a single command center where analysts can chat with an AI assistant to monitor, orchestrate, and control defensive security operations in real-time.

## Screenshots

> Need to capture these? See the [screenshot capture guide](docs/screenshots/README.md).

| # | Screenshot | What to capture |
|---|-----------|-----------------|
| 1 | **Command center** | Overview tab with module health dots green and telemetry chart alive |
| 2 | **AI assistant** | Chat exchange with an action proposal and the confirmation prompt visible |
| 3 | **RAG dashboard** | `/dashboard` with KPIs, security score and timeline populated |
| 4 | **RBAC** | Sidebar account block logged in as admin (badge visible) |

<p align="center">
  <img src="docs/screenshots/overview.png" width="45%" alt="Command center" />
  <img src="docs/screenshots/ai-assistant.png" width="45%" alt="AI assistant" />
</p>
<p align="center">
  <img src="docs/screenshots/rag-dashboard.png" width="45%" alt="RAG dashboard" />
  <img src="docs/screenshots/rbac-account.png" width="45%" alt="RBAC account" />
</p>

---

## Architecture

```
                 +-----------------------------------+
                 |      Ragnarök Desktop App         |
                 |  (Tauri Shell + Tailwind UI)      |
                 +-----------------+-----------------+
                                   |
                                   v (HTTP / WebSockets)
                 +-----------------------------------+
                 |     Python FastAPI Orchestrator   |
                 |     (AI Intent Parser & Router)   |
                 +-----------------+-----------------+
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
         v                         v                         v
   +--------------+         +--------------+         +--------------+
   |   HEIMDALL   |         |   MJOLNIR    |         |   BIFROST    |
   |    (HIDS)    |         |   (Triage)   |         |  (Scanner)   |
   +--------------+         +--------------+         +--------------+
         |                         |
         v                         v
   +--------------+         +--------------+
   |  YGGDRASIL   |         |    FENRIR    |
   |  (AD Audit)  |         |  (Threat Intel) |
   +--------------+         +--------------+
```

---

## Quick Start (Running the Orchestrator)

```bash
# 1. Clone repository
cd C:\Progetti\Asgard\Ragnarök

# 2. Install Python backend dependencies
cd backend
pip install -r requirements.txt  # (fastapi, uvicorn, pydantic)
cd ..

# 3. Start the backend (in a terminal)
cd backend
python server.py

# 4. Open the dashboard in your browser
#    → http://localhost:8000/dashboard
```

---

## Configuration

All configuration is done via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `RAGNAROK_API_KEY` | auto-generated | API key for legacy endpoints (still works alongside Bearer tokens) |
| `RAGNAROK_AUTH_SECRET` | auto-generated (32 bytes) | Secret for auth DB encryption — **set in production** |
| `RAGNAROK_AUTH_DB_PATH` | `ragnarok_auth.db` | Path to the auth SQLite database |
| `RAGNAROK_AUDIT_DB_PATH` | `ragnarok_audit.db` | Path to the audit SQLite database |
| `RAGNAROK_CHROMA_DIR` | `./chroma_db` | ChromaDB vector store directory |
| `RAGNAROK_CONVERSATION_DB_PATH` | `ragnarok_conversation.db` | Conversation memory database |
| `RAGNAROK_OUTPUT_DIR` | `./output` | Output directory for reports |
| `RAGNAROK_MODEL` | `gpt-4o-mini` | LLM model (requires `OPENAI_API_KEY`) |
| `RAGNAROK_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model for RAG |
| `RAGNAROK_RAG_DEVICE` | `cpu` | Device for embeddings (`cpu` or `cuda`) |
| `RAGNAROK_AUTO_INDEX_MINUTES` | `60` | Auto-index interval in minutes (0=disabled) |
| `RAGNAROK_ANOMALY_WATCH_MINUTES` | `60` | Anomaly watcher interval (0=disabled) |
| `RAGNAROK_REPORT_SEND_MINUTES` | `0` | Report send interval (0=disabled) |
| `RAGNAROK_REPORT_SEND_CRON` | — | Report send cron time `HH:MM` (daily at fixed time) |
| `RAGNAROK_SESSION_TTL` | `28800` (8h) | Session lifetime in seconds |
| `RAGNAROK_LOGIN_MAX_ATTEMPTS` | `5` | Failed login attempts before account lockout |
| `RAGNAROK_LOCKOUT_SECONDS` | `300` (5m) | Lockout duration after too many failures |
| `RAGNAROK_RATE_LIMIT_MAX` | `300` | Max requests per window per IP |
| `RAGNAROK_RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |
| `ASGARD_TLS` | `false` | Enable HTTPS (`true` for self-signed cert) |
| `ASGARD_TLS_CERTFILE` | — | Path to TLS certificate (optional, enables HTTPS) |
| `ASGARD_TLS_KEYFILE` | — | Path to TLS private key (optional, enables HTTPS) |
