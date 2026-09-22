# Asgard Suite — Release Notes

## v2.7.1 — Runtime Validation & Bugfix Pass

> 2026-09-22 — La suite è stata spinta fino al punto in cui ogni claim era provato a
> runtime, non solo a test: `docker compose up` reale, playbook SOAR completo,
> monitoring stack attivo, webhook Alertmanager→Gjallarhorn funzionante. Tutto ciò che
> non reggeva è stato corretto. **679 test, tutti verdi.**

### Fix a runtime confermati

- **Crash-loop servizi on-demand** (`docker-compose.yml`): fenrir/mjolnir/yggdrasil/
  sleipnir ereditavano il CMD `python server.py` dell'immagine → morte immediata.
  Ora `command: ["tail", "-f", "/dev/null"]` (idle; il playbook li lancia via subprocess).
- **Monitoring stack** (`monitoring/docker-compose.monitoring.yml`): `name: asgard`
  uniforme (prima `asgard-monitoring` → container orfani in conflitto al merge dei due
  compose) e path volumi relativi alla root del progetto (`./monitoring/*`,
  `./docker/grafana/*`; prima `../monitoring/*` risolveva a `C:\Progetti\monitoring`).
- **Webhook Alertmanager** (`Gjallarhorn`): nuovo endpoint `/api/v1/notify/alertmanager`
  (payload standard `status/labels/alerts`, severità mappata, 400 su corpus vuoto) —
  prima `alertmanager.yml` puntava a `/notify` (404). `alertmanager.yml` ora invia
  `X-API-Key: asgard-gjallarhorn-key` via `http_config.http_headers` e
  `prom/alertmanager` è passato a **v0.28.0** (il campo `headers` non esiste in v0.27 →
  crash-loop all'avvio; verificato end-to-end: alert critical via API AM → webhook
  Gjallarhorn 200, «forwarded»=1). Test Gjallarhorn: 69→**73**.
- **Hang runner** (`Ragnarok/conftest.py`): isolato `ASGARD_RAG_DB_PATH` su temp dir —
  `server.py` istanzia chromadb all'import sul DB condiviso `.asgard-suite-repo/rag_db`;
  con server dev/container attivi il lock SQLite bloccava run_suite_tests.py in modo
  intermittente su "Ragnarok UI". Ora `run_suite_tests.py` completa in ~134s senza hang.
- **CI no-secrets**: gate `scripts/rotate_keys.py --check-files --allow-dev-placeholders`
  (exit 1 se un `.env` reale o un default debole non-DEV finisce nei compose) + rivalutazione
  dei 4 ignore chromadb con pip-audit aggiornato (2026-09-22): versioni ferme a 1.5.9,
  ignore ancora necessari fino alla patch / 2026-12-31.

### Runtime smoke (docker compose up, 2026-09-22)

- 9/9 container up, 6/6 moduli healthy via `GET /api/v1/status`.
- Auth: bootstrap admin → login → token → RAG chat (suggerimento playbook, zero auto-action).
- `execute bifrost`: scan live `127.0.0.1` (25 porte, 8080 rilevata). Backup+verify+retention OK (14).
- Playbook SOAR `brute_force` end-to-end: Fenrir (1717 IOC CISA KEV) → Heimdall (2 alert)
  → Mjolnir IR → Bifrost scan → Yggdrasil audit → `CONTAINED`.
- Monitoring: Prometheus scrape ragnarok/gjallarhorn, 4 alert rules, Loki API ok, Grafana 200.
- Webhook Alertmanager reale → Gjallarhorn: 200, notified/forwarded ok.

### Verification

```bash
python run_suite_tests.py   # 10/10 entries, 679 tests, 0 failures
```

| Modulo | v2.6.0 | v2.7.1 |
|---|---|---:|
| Heimdall | 38 | 42 |
| Bifrost | 46 | 51 |
| Fenrir | 48 | 53 |
| Sleipnir | 32 | 38 |
| Forseti | 44 | 48 |
| Gjallarhorn | 63 | 73 |
| Ragnarok (backend+UI) | 264 | 271 |
| Mjolnir / Yggdrasil | invariati | invariati |
| **Totale** | **638** | **679** |

**License: MIT — free to use, modify, and distribute. No warranty.**

---

## v2.7.0 — P0/P1/P2 Implementation Pass

> 2026-09-22 — Chiusura dei gap documentati: persistenza RAG, backup con retention,
> rotation secrets, supply-chain CI (P0); FIM, SOAR resiliente, MISP, evidence
> automatiche (P1); escalation on-call, CVE+NVD, Helm, monitoring (P2).

### P0 — Produzione minima

- **RAG persistente**: `ASGARD_RAG_DB_PATH` da `/tmp` a `/state` con named volumes
  (`asgard-rag-state`, `asgard-backups`) in `docker-compose.yml` e `-express`;
  `/state` creato in `Dockerfile` con owner `1000` (era il motivo del `/tmp`).
- **Backup con retention**: `Ragnarok/backend/backup.py` con `prune_old_backups()`
  (`BACKUP_KEEP_COUNT=14`, `BACKUP_RETENTION_DAYS=30`, mai fatale) + `scripts/suite_backup.py`
  (zip centrale verificato di tutti i `*.db` dei moduli).
- **Secrets**: `scripts/rotate_keys.py` (`--write .env` con chmod 600, `--check` che
  fallisce sui default `asgard-*-key`); compose + `.env.example` documentati.
- **Supply-chain CI**: job `supply-chain` (`pip-audit` su tutti i 10 requirements,
  Trivy fs HIGH/CRITICAL, SBOM CycloneDX); lint `pyflakes` esteso a `Gjallarhorn/core`.

### P1 — Detection, SOAR, Intel, Compliance

- **Heimdall FIM lite** (`core/fim.py`, `fim-baseline`/`fim-scan`, tabella `fim_events`):
  baseline sha256, eventi NEW/MODIFIED/DELETED. Nota: lo Sigma-lite esisteva già
  (`core/detector.py` + `rules/*.yaml`) — non è stato duplicato.
- **Sleipnir resiliente**: `retries` + `retry_delay` + `timeout` per-step,
  `continue_on_failure`, gruppi `parallel:` (ThreadPoolExecutor, max 4).
  Gli errori di validazione IP non vengono mai ritentati.
- **Fenrir MISP**: `fetch_misp_attributes()` (REST search, `MISP_URL`/`MISP_API_KEY`,
  401/403 espliciti) + `aggregate_feeds(..., misp_url, misp_api_key)` isolato per-feed.
- **Forseti evidence**: `core/evidence.py` (conteggi readonly da Heimdall/Fenrir/
  Gjallarhorn, mai crash), allegata a `assess()` + sezione report + `serve`.

### P2 — Escalation, Vuln, Deploy, Monitoring

- **Gjallarhorn on-call**: canali `PagerDuty` (Events API v2) e `Opsgenie` (Alert API,
  supporto `.eu`), stesso contratto `never-raise` degli altri 6 canali.
- **Bifrost CVE**: firme 6 → 12 (Heartbleed, SambaCry, ProFTPD, IIS 6.0, PHP dev…),
  CVSS live da NVD API v2 (`fetch_nvd_cvss`, cache, best-effort), `--enrich` con
  tabella vulnerabilità, nuovo flag `--nvd`.
- **Helm** (`helm/asgard/`): 5 Deployment+Service con gli stessi command/workingDir
  del compose, PVC `asgard-rag-state`/`asgard-backups`, `PrometheusRule`.
- **Monitoring** (`monitoring/`): `prometheus.yml`, `asgard-alerts.yml` (solo metriche
  reali: `asgard_last_backup_hours_ago`, `gjallarhorn_alerts_total`), `alertmanager.yml`
  verso il webhook Gjallarhorn, Loki+Promtail, `docker-compose.monitoring.yml`.

### Verification

```bash
python run_suite_tests.py   # 10/10 entries, 675 tests, 0 failures (+37 vs v2.6.0)
```

| Modulo | v2.6.0 | v2.7.0 |
|---|---|---:|
| Heimdall | 38 | 42 |
| Bifrost | 46 | 51 |
| Fenrir | 48 | 53 |
| Sleipnir | 32 | 38 |
| Forseti | 44 | 48 |
| Gjallarhorn | 63 | 69 |
| Ragnarok (backend+UI) | 264 | 271 |
| Mjolnir / Yggdrasil | invariati | invariati |
| **Totale** | **638** | **675** |

**License: MIT — free to use, modify, and distribute. No warranty.**

---

## v2.6.0 — Coverage & Structure Pass

> 2026-09-22 — Full-suite verification extended to every test that exists (638 across 10 runner entries, including the 136 Ragnarok UI tests the runner never executed), Ragnarok's `server.py` split from 1790 to 1101 lines across 9 routers with zero behavior change, and the honesty bar applied to docs, packager and Docker context. Every item below was verified by running it.

### Expanded (real coverage, wider than described before)

- **Test suite 502 → 638**: `run_suite_tests.py` gains the `Ragnarok/tests` entry (136 Desktop & API tests previously run only via CI) plus `--setup` (one-command local deps install mirroring CI/Dockerfile), a pre-flight warning for missing `msal`/`yara-python`, and honest failed/error counts on red runs.
- **Forseti 31 → 41 controls**: DORA and ISO 27001 grow from 3 to 8 controls each (backup, continuity, logging, privileged access…); docs updated everywhere, starter-level warning for regulated clients kept.
- **MITRE matrix 6 → 18 techniques across 9 tactics**: both endpoints (`/api/v1/mitre/matrix`, `/api/v1/dashboard/mitre-matrix`) were serving *different* hardcoded copies — now a single source of truth (`core/mitre.py`), each technique mapped only to capabilities a module really has (`active` vs `monitored`).
- **Ragnarok `server.py` 1790 → 1101 lines**: 9 routers (`rag`, `ops`, `pages`, `setup`, `info`, `intel`, `gdpr`, `auth`, `tenants_agents`) extracted verbatim with lazy server imports; 264/264 Ragnarok tests pass, all paths unchanged.

### Fixed (found by actually running things)

- **Ragnarok UI tests failed from the suite root**: `test_health_endpoint_returns_200` gave 503 outside `Ragnarok/` — two cwd-relative paths plus import-order DB binding (test users leaked into the real dev DB: 194 users found, cleaned to 1 with backup). Isolation centralized in `conftest.py`; green from any cwd.
- **`/metrics` backup metric never emitted in production**: cwd-relative `backend/backups` path doesn't exist under Docker WORKDIR — now absolute.
- **Release packager shipped real secrets**: the v2.5.0 zip contained `Ragnarok/backend/asgard_setup.env` with live API keys; `.env` files are now excluded (templates kept), version bumped, old leaky archive deleted.
- **Docker images baked in secrets and GBs of build dirs**: `.dockerignore` was never even committed (ignored by mistake) — now tracked and hardened (`*.env`, `*.db`, `node_modules/`, `src-tauri/target/`…); pattern-audited, full build not run.
- **7 wrong commands in ADOPTION_GUIDE** (plain clone, `Ragnarök` dir typo, `:8000` ports, nonexistent `--test-alert`/`--scan-type`/`--report` flags, useless backup body) — every replacement verified against real `--help`/endpoint signatures.
- **9 orphan per-module Dockerfiles**: wrong ports and CLI flags no module accepts, referenced by nothing — deleted (−157 lines).
- **46 pyflakes findings → 0** suite-wide (unused imports, brace-free f-strings, one dead variable), enforced by a new CI lint job plus shell syntax checks.

### Verification

```bash
git clone --recursive https://github.com/Fioru12/Asgard.git
python run_suite_tests.py --setup   # one-command local deps (new)
python run_suite_tests.py           # 10/10 entries, 638 tests, 0 failures
```

**License: MIT — free to use, modify, and distribute. No warranty.**

---

## v2.5.1 — Verification & Honesty Pass

> 2026-09-15 — Every "Enterprise/MSP" claim in v2.5.0 was checked against the running code, not just re-read from the docs. Three real bugs were found and fixed; two features turned out thinner than described and have been re-labeled instead of silently left overstated.

### Fixed (were broken, now genuinely work — each verified live, not just by reading the diff)

- **OIDC SSO was only half-built**: `/api/v1/auth/oidc/login` generated a login URL, but there was no callback to exchange the authorization code, verify the id_token's signature against the IdP's JWKS, or issue a session. Implemented the full flow (`exchange_oidc_code`, `find_or_create_oidc_user`, `GET /api/v1/auth/oidc/callback`) using standard OIDC discovery and PyJWT signature verification — never hand-rolled crypto. New SSO users auto-provision at the least-privileged role (`viewer`). 15 new tests, all mocked (no real IdP calls), covering both the happy path and forged/expired/wrong-audience tokens being rejected.
- **The Grafana dashboard would have shown "No data" on 3 of its 4 panels**: `server.py` defined `/metrics` twice; FastAPI silently used only the first definition, so the metrics the dashboard actually queries (`asgard_registered_users_total`, `asgard_registered_agents_total`, `asgard_active_tenants_total`) were never emitted by a running server. Merged into one endpoint, verified live that all four dashboard metrics are now present, added a regression test (none existed before).
- **`install.ps1` failed to parse at all on Windows PowerShell 5.1**: the file was saved as UTF-8 without a BOM; non-ASCII characters (e.g. "ö" in "Ragnarök") get misread under the system ANSI codepage, corrupting string tokenization for the rest of the file. Re-saved with a UTF-8 BOM; the script now parses cleanly.

### Also fixed: dead code wired in for real

- **Mjolnir's `YaraPatternScanner` (`core/yara_scanner.py`) existed but was never called from anywhere** — a regex-based signature scanner (3 built-in rules: generic webshell, ransomware note, encoded PowerShell one-liner) sitting completely unused. Wired it into `run_triage()`: it now scans the executable of any process already flagged suspicious by the IOC scanner, and surfaces matches in both the console summary and the generated report. New integration test covers it end to end. Also fixed an existing key-name typo (`detail` vs `details`) that silently dropped the VirusTotal detection count from every report. Note: this is not the actual YARA engine — no `.yar` rule file support, not compatible with the public YARA rule ecosystem — `MSP_PARTNER_GUIDE.md` has been updated to describe it accurately.

### Corrected in documentation (features don't exist at all)

- **"Active Deception (Honeypot/Honeytoken)" does not exist anywhere in the codebase.** Removed from `MSP_PARTNER_GUIDE.md`'s comparison table; the onboarding checklist's `python Mjolnir/main.py deploy-traps` step (a command that does not exist — Mjolnir has exactly one subcommand, `triage`) was replaced with a real, verified command.
- **DORA and ISO 27001 support in Forseti is real but shallow**: 3 controls each, versus 13 (GDPR) and 12 (NIS2). Loads and scores correctly, but should not be presented to a client as a complete DORA/ISO27001 assessment.
- **Yggdrasil's "M365/Entra ID audit" does not connect to a live tenant.** `core/entra_audit.py` analyzes a JSON file the operator must already have (or fall back to simulated data) — there is no exporter anywhere in the suite that pulls this from a real Microsoft Graph API. Useful as an offline analyzer; not a plug-and-play cloud connector.
- **The MITRE ATT&CK matrix is a curated reference (18 techniques across 9 tactics), not comprehensive coverage tracking** — see the v2.5.0 entry above, updated to match.

All fixes verified by actually running them (live OIDC token exchange with mocked IdP responses, live `/metrics` HTTP calls, live PowerShell parser checks, live `Forseti init`/`assess` and `Mjolnir triage --simulate` runs) — not inferred from reading the source.

---

## v2.5.0 — Enterprise & MSP Tier Release

> 2026-09-07 — Multi-Tenancy, OIDC SSO, Agent Remote Management & Observability.

---

### What's New in v2.5.0

- **Multi-Tenant Architecture**: Multi-organization isolation (`tenants` DB schema, `X-Tenant-ID` scoping, `/api/v1/tenants` REST APIs).
- **Enterprise SSO (OIDC)**: Azure AD / Entra ID, Okta, and Keycloak authentication via standard OIDC discovery, authorization-code exchange and JWKS signature verification (`/api/v1/auth/oidc/login` + `/api/v1/auth/oidc/callback`). Completed and verified in v2.5.1 — see below.
- **Agent Remote Management & Enrollment**: One-time enrollment token generation (`/api/v1/agents/tokens`) and automated heartbeat registration for Heimdall agents (`heimdall_agent.py --enroll-token`).
- **Prometheus Metrics Exporters**: Native `/metrics` endpoints in Ragnarök and Gjallarhorn.
- **Grafana Dashboard Template**: Ready-to-use JSON dashboard template (`docker/grafana/asgard-overview-dashboard.json`).
- **MITRE ATT&CK Reference Matrix**: initial technique-to-module mapping endpoint (`/api/v1/dashboard/mitre-matrix`), covering 6 techniques across 4 tactics today. This is a curated starting reference, not a comprehensive or dynamically-verified coverage map — see the v2.5.1 audit notes below.
- **End-to-End Attack Simulation Pipeline**: Automated incident lifecycle verification runner (`run_e2e_attack_simulation.py`).
- **Unified Test Verification**: All 376 tests across 9 modules passed (`python run_suite_tests.py`).

---

## v1.0.0 — First Stable Release

> 2026-09-05 — The suite is honest, tested, and deployable.

---

### What this release includes

A complete, on-premise, AI-augmented SOC platform for small businesses — 9 independent modules unified by a single desktop orchestrator.

#### Core modules (all HTTP APIs with auto-generated keys, all tested)
| Module | Purpose | Tests |
|--------|---------|-------|
| Heimdall | HIDS: brute-force detection, firewall blocking | 33 |
| Mjolnir | Forensic triage: process/network snapshots, VirusTotal lookups | 20 |
| Bifrost | Network scanner: banner grabbing, GeoIP/WHOIS, encrypted reports | 42 |
| Yggdrasil | Active Directory audit (real LDAP/LDAPS or demo mode) | 22 |
| Fenrir | Threat intelligence aggregator (CISA KEV + OTX) | 36 |
| Sleipnir | SOAR engine: YAML playbooks orchestrating the other modules | 24 |
| Forseti | GDPR/NIS2 compliance checker: 25 real controls, scoring, remediation | 29 |
| Gjallarhorn | Centralized alerting hub (6 channels: Telegram, webhook, SMTP, Teams, Jira, ServiceNow) | 50 |
| Ragnarök | Desktop orchestrator: AI assistant, dashboard, multi-user RBAC | 128 |

**Total: 377 tests, 0 failures.**

#### New in this release (vs. pre-audit state)

- **Multi-user RBAC**: 3 roles (admin, analyst, viewer), session-based auth, audit trail
- **Security hardening**: brute-force lockout, rate limiting, security headers, TLS, encrypted auth database
- **Backup/restore**: verifiable (sha256), tamper-refusing, one endpoint
- **Docker deployment**: all 9 modules in one `docker compose up -d`
- **Guided installers**: `install.sh` (bash) + `install.ps1` (PowerShell)
- **Bilingual documentation**: English + Italian
- **Bug fixes found by test-driven development**: several real bugs fixed (fake-success claims, broken restore, unencrypted usernames)

---

### What this release does NOT include (honest gaps)

- Screenshots / demo video in README
- Certified compliance (SOC2, ISO2701) — requires legal audit, not code
- Enterprise HA / clustering
- Mobile app
- Built-in LLM (optional Ollama/OpenAI integration only)

---

### Quick start

```bash
# Docker (recommended)
git clone https://github.com/Fioru12/Asgard.git
cd Asgard
./install.sh            # Linux / macOS / Git Bash
.\install.ps1           # Windows PowerShell
# Open http://localhost:8080/dashboard
```

---

### Architecture

See `README.md` (Italian) or `README_EN.md` (English) for the full architecture diagram and module descriptions.

### Known issues

- The e2e semantic search test is deterministic (fixed rank-variance) but requires ChromaDB embedding to work
- TLS self-signed certs trigger browser warnings (expected)
- No installer for ARM64 (Apple Silicon) yet — manual Docker setup works

### Roadmap (tentative, by impact)

1. Screenshots / demo video
2. ARM64 support
3. Optional managed cloud version (if demand exists)

---

### Verification

To verify this release:
```bash
cd Asgard
pytest tests/ -v          # Ragnarök: 128 tests
pytest backend/tests/     # RAG backend: 93 tests
# Other modules: run pytest in each module directory
```

**License: MIT — free to use, modify, and distribute. No warranty.**

---

*Built by [Fioru12](https://github.com/Fioru12) — because security tools should prove what they claim.*
