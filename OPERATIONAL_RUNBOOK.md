# 🛡️ ASGARD CYBER SUITE — MANUALE OPERATIVO & RUNBOOK INCIDENT RESPONSE (SOP)

> **Documento Tecnico Operativo per Amministratori di Sistema, IT Manager e Fornitori MSP.**  
> *Versione Piattaforma: 2.5.1 — Classificazione: Uso Interno / Partner*

---

## 1. Architettura di Monitoraggio & Flusso degli Eventi

Asgard opera attraverso una gerarchia di **Guardiani Autonomi** coordinati dal motore centrale:

```
                  +-----------------------------------+
                  |      EVENTO DI SICUREZZA / MINACCIA|
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
       [HEIMDALL]              [MJOLNIR]            [FORSETI / YGGDRASIL]
   Rilevamento Intrusione      Triage Forense        Anomalia Config / NIS2
            |                       |                       |
            +-----------------------+-----------------------+
                                    |
                                    v
                     +-----------------------------+
                     |    GJALLARHORN (Alerting)   |
                     | Invia Mail, Webhook, Syslog |
                     +--------------+--------------+
                                    |
                                    v
                     +-----------------------------+
                     |  RAGNARÖK RAG (AI Sovrana)  |
                     | Genera Playbook di Bonifica |
                     +--------------+--------------+
                                    |
                                    v
                     +-----------------------------+
                     | AZIONE IT MANAGER / MSP SOC |
                     | Esecuzione comandi guidati  |
                     +-----------------------------+
```

---

## 2. Matrice di Severità & Tempi di Risposta (SLA Consigliati)

| Severità | Descrizione Evento | Azione Automatica Asgard | SLA Risposta IT/MSP |
| :--- | :--- | :--- | :--- |
| **CRITICAL (P1)** | Brute-force SSH/RDP con soglia superata (Heimdall), hash di processo confermato malevolo su VirusTotal (Mjolnir). | Blocco IP temporaneo su firewall locale (TTL configurabile), notifica immediata. | **< 15 Minuti** |
| **HIGH (P2)** | Porta critica esposta non censita (Bifrost), admin M365/AD senza MFA (Yggdrasil). | Segnalazione nel report e nell'alert Gjallarhorn. | **< 1 Ora** |
| **MEDIUM (P3)** | Utente privo di MFA, mancata rotazione credenziali, configurazione debole (da assessment Forseti). | Segnalazione nel report di autovalutazione. | **< 24 Ore** |
| **LOW / INFO (P4)** | Scansione periodica completata con esito regolare, aggiornamento feed IOC (Fenrir). | Archiviazione nel database locale. | **Nessuna azione richiesta** |

> Nota: le "azioni automatiche" sopra sono quelle che i moduli eseguono davvero oggi (blocco IP di Heimdall, verifica hash di Mjolnir). Non esistono nella suite funzionalità di honeypot/honeytoken, file integrity monitoring (FIM) o isolamento automatico dell'host — se ti servono, vanno implementate a parte.

---

## 3. Procedure di Risoluzione per Categoria di Allarme (Playbooks)

### Scenario A: Processo Sospetto Confermato Malevolo (Mjolnir)
* **Sintomo**: Allarme `[CRITICAL] VT: <processo> (N detections)` nel report di triage o via Gjallarhorn.
* **Cosa significa**: Mjolnir ha eseguito un triage dell'host (snapshot processi/rete + scan IOC + verifica hash VirusTotal) e un eseguibile in esecuzione è stato confermato malevolo da più motori antivirus.
* **Procedura Operativa per l'IT**:
  1. Aprire il report generato in `Mjolnir/output/` (Markdown e HTML).
  2. Identificare processo, PID e percorso eseguibile riportati.
  3. Isolare manualmente l'host dalla rete (Asgard non lo fa automaticamente oggi) e terminare il processo.
  4. Rilanciare il triage per conferma, con verifica VirusTotal attiva:
     ```bash
     cd Mjolnir
     python main.py triage --vt
     ```
  5. Conservare il report come prova per l'eventuale notifica di incidente NIS2.

---

### Scenario B: Attacco Brute-Force Rilevato (Heimdall)
* **Sintomo**: Allarme `[HIGH]`/`[CRITICAL]` da Heimdall su tentativi di login falliti ripetuti (SSH/RDP), con notifica su Telegram o Gjallarhorn se configurati.
* **Cosa significa**: Un attaccante esterno o interno sta tentando di indovinare le credenziali di accesso. Se la severità è HIGH/CRITICAL e l'IP è valido, Heimdall tenta già il blocco automatico sul firewall locale (a meno che sia in modalità dry-run).
* **Procedura Operativa per l'IT**:
  1. Verificare nel log/report se il blocco automatico è andato a buon fine (un fallimento genera ora un alert critico dedicato, non un falso "successo").
  2. Cercare l'IP nel catalogo di threat intelligence di Fenrir:
     ```bash
     cd Fenrir
     python main.py search "<IP_ATTACCANTE>"
     ```
  3. Se l'IP è interno, verificare se la macchina appartiene a un dipendente con credenziali scadute o compromesse e forzarne il reset.
  4. Se il blocco automatico era in dry-run, valutare l'attivazione reale in `Heimdall/config.yaml` (`responder.dry_run: false`) dopo aver validato le regole.

---

### Scenario C: Gap di Conformità Rilevato (Forseti)
* **Sintomo**: Un assessment Forseti (compilato manualmente, non è un audit automatico continuo) riporta uno score combinato basso e gap di severità alta.
* **Cosa significa**: Le risposte al questionario indicano configurazioni deboli o processi mancanti rispetto ai controlli GDPR/NIS2/DORA/ISO27001 mappati da Forseti.
* **Procedura Operativa per l'IT**:
  1. Aprire il report Markdown generato dall'assessment.
  2. Consultare la tabella dei **gap** ordinati per severità, con la colonna "Come rimediare".
  3. Applicare i rimedi indicati (organizzativi o tecnici — Forseti non li esegue automaticamente).
  4. Ricompilare il questionario e rilanciare l'assessment per verificare il nuovo punteggio:
     ```bash
     cd Forseti
     python main.py assess --input assessment.yaml --output report.md
     ```
     (oppure `python main.py serve` per compilarlo da browser invece che a mano)

---

## 4. Manutenzione Ordinaria & Healthcheck della Suite

Per verificare che tutti i demoni e moduli di Asgard siano operativi sul server:

1. **Controllo Stato Globale**:
   Con Ragnarök in esecuzione (`python backend/server.py` o `npm run tauri dev`), lo stato di tutti i moduli è disponibile su:
   ```
   GET http://127.0.0.1:8080/api/v1/status
   ```
2. **Aggiornamento Intelligence Minacce**:
   ```bash
   cd Fenrir
   python main.py update
   ```
3. **Backup Database Locale SQLite**:
   Ogni modulo tiene il proprio database SQLite nella propria cartella (es. `Heimdall/heimdall.db`, `Fenrir/fenrir.db`, `Ragnarok/backend/ragnarok_auth.db`) — non esiste una cartella `data/` condivisa. Includere l'intera directory root di Asgard nei backup di sistema schedulati copre tutti i database. Ragnarök ha inoltre una funzione di backup/restore integrata (vedi sezione "Backup & restore" nel README di Ragnarok).
