# Checklist Pilot MSP — Asgard Suite v2.6.0

> Da usare insieme a `PILOT_BETA_AGREEMENT.md` (30 giorni, as-is) e `docs/ADOPTION_GUIDE.md`.
> Ogni voce ha un criterio di accettazione: si spunta solo a evidenza vista, mai a sensazione.

---

## 0. Pre-pilot (prima di firmare)

- [ ] MSP identificato: 1 tenant di test, max 5 host, nessun sistema di produzione al giorno 1
- [ ] Referente tecnico nominato da entrambe le parti (nome + canale diretto)
- [ ] `PILOT_BETA_AGREEMENT.md` firmato — attenzione ad Art. 3 (esonero responsabilità) e Art. 4 (titolarità degli asset scansionati)
- [ ] Perimetro scritto: IP/host/domini inclusi ESPLICITAMENTE; tutto il resto è fuori perimetro
- [ ] Heimdall in **dry-run** per i primi 7 giorni (`dry_run: true` — default): nessun blocco firewall automatico finché il tuning non è validato
- [ ] Canale feedback concordato (Art. 5.1): bug e suggerimenti dove finiscono, entro quando rispondi

## 1. Installazione (giorno 1, insieme al referente)

- [ ] `git clone --recursive` + `./install.sh` (o `.\install.ps1`) senza errori
- [ ] Dashboard raggiungibile su `http://localhost:8080/dashboard`, wizard di setup completato
- [ ] Account admin + 1 analyst + 1 viewer creati; login/logout verificati per tutti i ruoli
- [ ] Servizi rispondenti: Heimdall `:18000`, Gjallarhorn `:8090`, Forseti `:8091`, Bifrost `:8092`
- [ ] `/health` = 200, `/metrics` espone le 4 metriche Grafana (regression test dedicato esiste)

## 2. Prime due settimane (osservazione, niente automazioni aggressive)

- [ ] Heimdall: almeno 1 brute-force simulato rilevato (`python main.py simulate`), alert visibile in dashboard
- [ ] Bifrost: 1 `discover` del perimetro concordato, report rivisto col referente (falsi positivi annotati)
- [ ] Fenrir: feed CISA KEV aggiornato (`update`), 1 lookup IOC di prova
- [ ] Mjolnir: 1 `triage --simulate`, report Markdown/HTML aperto e capito
- [ ] Yggdrasil: 1 audit AD (o simulato se senza AD), voce MFA/admin riviste
- [ ] Forseti: questionario compilato (GDPR/NIS2; DORA/ISO a 8 controlli = base di lavoro, NON assessment completo)
- [ ] Gjallarhorn: almeno 1 canale reale configurato (Telegram o webhook) + 1 alert ricevuto davvero
- [ ] Zero blocchi firewall automatici non spiegati (dry-run attivo: verificare i log, non i firewall)

## 3. Settimane 3-4 (automazione controllata)

- [ ] Dry-run valutato coi log: soglie Heimdall tarate sul rumore reale del tenant
- [ ] Solo DOPO la taratura: valutare blocco automatico su 1 host non critico, con TTL breve e rollback documentato
- [ ] 1 playbook Sleipnir eseguito end-to-end (es. brute-force → scan → triage → notifica), stato finale `CONTAINED` verificato
- [ ] Backup Ragnarok creato E verificato (`/api/v1/backup` + verify), restore testato in ambiente separato se possibile
- [ ] TLS valutato: self-signed accettato per il pilot o cert aziendali caricati (`ASGARD_TLS_CERTFILE/KEYFILE`)

## 4. Criteri di successo (go / no-go a fine pilot)

- [ ] L'MSP sa installare da zero senza il tuo aiuto (test con una VM pulita, cronometrato)
- [ ] Almeno 3 bug o attriti documentati dal referente (un pilot senza feedback è un pilot fallito)
- [ ] Report Forseti allegabile a un cliente dell'MSP senza imbarazzo (gap onesti, niente "conformità certificata")
- [ ] Decisione scritta: stop / estensione / contratto (Art. 1.2)

## 5. Limiti da dichiarare al giorno 1 (non negoziabili)

- Nessun isolamento automatico dell'host, nessun honeypot/FIM — contenimento manuale (vedi `OPERATIONAL_RUNBOOK.md`)
- Niente HA/clustering, niente ARM64, TLS self-signed di default
- RAG e telemetria sono locali (pro) ma richiedono risorse (4GB RAM minimo, meglio 8)
- Asgard non sostituisce antivirus/backup/firewall esistenti (Art. 2.2 dell'accordo)
