# Asgard Suite — Release Notes

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
