# Asgard Suite — Release Notes

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
