<div align="center">

# ASGARD

### Blue Team Security Suite — 9 modules, one principle: if it isn't tested, it doesn't exist.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/Test-300%2B%20passing-2ea44f?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

[🇮🇹 Versione italiana](README.md)

</div>

---

## What is Asgard

Asgard is a suite of defensive security (blue team) tools designed for small businesses and independent analysts who cannot afford a commercial SOC platform, yet still need to detect, investigate, orchestrate and — increasingly often — demonstrate regulatory compliance.

Every module does **one thing** and does it well: no monoliths, no forced dependency on a cloud provider, no feature described in a README that doesn't actually exist in the code. That last point is not a throwaway sentence: the entire suite went through a full technical audit (every source file read, not just the documentation) which fixed real security bugs — including two cases where the software claimed a success that had never actually happened. The guiding criterion since then has been a single one: **it really works, or it isn't in the suite.**

---

## Architecture

```mermaid
flowchart TB
    subgraph Detection
        Heimdall["🛡️ Heimdall<br/>HIDS · brute-force detection"]
        Bifrost["🌈 Bifrost<br/>Network scanner"]
        Yggdrasil["🌳 Yggdrasil<br/>Active Directory audit"]
    end

    subgraph Response and Intelligence
        Mjolnir["🔨 Mjolnir<br/>Forensic triage"]
        Fenrir["🐺 Fenrir<br/>Threat intel aggregator"]
        Sleipnir["🐴 Sleipnir<br/>SOAR playbook engine"]
    end

    subgraph Governance
        Forseti["⚖️ Forseti<br/>GDPR/NIS2 compliance"]
        Gjallarhorn["📯 Gjallarhorn<br/>Alerting hub"]
    end

    Ragnarok["⚡ Ragnarök<br/>Desktop orchestrator + AI"]

    Heimdall -- alert --> Sleipnir
    Sleipnir -- triage --> Mjolnir
    Sleipnir -- IOC lookup --> Fenrir
    Sleipnir -- scan --> Bifrost
    Sleipnir -- audit --> Yggdrasil
    Heimdall -. notifications .-> Gjallarhorn
    Sleipnir -. notifications .-> Gjallarhorn
    Yggdrasil -. evidence .-> Forseti
    Bifrost -. evidence .-> Forseti
    Heimdall -. evidence .-> Forseti
    Ragnarok --> Heimdall & Mjolnir & Bifrost & Yggdrasil & Fenrir & Sleipnir
```

Three functional groups:

- **Detection** — the sensors: Heimdall watches the logs, Bifrost watches the network, Yggdrasil watches Active Directory.
- **Response and Intelligence** — what happens after an alert: Mjolnir performs forensic triage on the host, Fenrir enriches with public threat intel, Sleipnir orchestrates everything through YAML playbooks.
- **Governance** — the part usually missing from purely technical security portfolios: Forseti translates security posture into a GDPR/NIS2 compliance score, Gjallarhorn centralizes notifications instead of letting every module reimplement them.

---

## The modules

| Module | What it does | Stack | Tests |
|---|---|---|---|
| [**Heimdall**](Heimdall) | Lightweight HIDS: detects brute-force in SSH/Windows logs, blocks IPs at the firewall level with a configurable TTL, notifies via Telegram/Gjallarhorn | Python, FastAPI, SQLite | 33 ✅ |
| [**Mjolnir**](Mjolnir) | Automated forensic triage on a compromised host: process/network snapshots, hash lookups on VirusTotal (with caching and rate-limiting), Markdown/HTML reports | Python, psutil | 20 ✅ |
| [**Bifrost**](Bifrost) | Multi-threaded network scanner with banner grabbing, GeoIP/WHOIS enrichment, encrypted reports (PBKDF2 + Fernet) | Python, FastAPI | 42 ✅ |
| [**Yggdrasil**](Yggdrasil) | Active Directory security audit over real LDAP/LDAPS (read-only bind) or a simulated mode for demos | Python, ldap3 | 22 ✅ |
| [**Fenrir**](Fenrir) | Public threat intelligence aggregator: CISA KEV always on, optional OTX, indexed in a local SQLite database | Python | 36 ✅ |
| [**Sleipnir**](Sleipnir) | SOAR engine: runs YAML playbooks that orchestrate the other modules, with persistent state and an incident audit trail | Python, PyYAML | 24 ✅ |
| [**Forseti**](Forseti) | GDPR/NIS2 compliance checker for SMBs: 25 real controls, scoring, report with gaps and concrete remediations | Python | 29 ✅ |
| [**Gjallarhorn**](Gjallarhorn) | Centralized alerting hub (Telegram/webhook/SMTP/Teams/Jira/ServiceNow) with dedup and throttling, used by Heimdall and Sleipnir | Python, FastAPI | 50 ✅ |
| [**Ragnarök**](Ragnarok) | Desktop orchestrator (Tauri + FastAPI) with an AI assistant, multi-user RBAC, security hardening, and mandatory human confirmation before every action | Tauri, Rust, Python | 128 ✅ |

Every module is independent: clone it, install it, use it on its own. Sleipnir and Ragnarök are where the suite stops being "a collection of scripts" and becomes a system.

---

## Quick start for any module

```bash
git clone https://github.com/Fioru12/<Module>.git
cd <Module>
pip install -r requirements.txt
pytest -v          # verify everything works in your environment
python main.py --help
```

Every module has its own `README.md` with a specific Quick Start, a `.env.example` for configuration, and a "Why I built it" section explaining the real problem it answers — this isn't a one-day effort, it's the story of how the suite evolved one module at a time.

---

## Project principles

- **Zero aspirational features.** If a module's README describes something, that something has a test proving it. Where a module supports a demo/simulated mode (e.g. Yggdrasil without a real Active Directory available), it is stated explicitly — never passed off as real data.
- **Fail loudly, not silently.** A security action that fails (a firewall block, an LDAP query, a notification) says so clearly — it never fakes a success.
- **Authentication by default on every exposed API**: a key is generated automatically if not configured explicitly; there is never an open endpoint by oversight.
- **A human stays in the loop** for every action with real consequences (IP blocking, playbook execution, AI-proposed actions in Ragnarök).

---

<div align="center">

**Built by [Fioru12](https://github.com/Fioru12)**

</div>
