# 🛡️ ASGARD CYBER SUITE — MANUALE OPERATIVO & RUNBOOK INCIDENT RESPONSE (SOP)

> **Documento Tecnico Operativo per Amministratori di Sistema, IT Manager e Fornitori MSP.**  
> *Versione Piattaforma: 2.4.0 — Classificazione: Uso Interno / Partner*

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
    [FENRIR / HEIMDALL]     [MJOLNIR / SLEIPNIR]   [FORSETI / YGGDRASIL]
   Rilevamento Intrusione     Trappola Attivata      Anomalia Config / NIS2
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
| **CRITICAL (P1)** | Rilevamento Ransomware, esca Mjolnir violata, brute force attivo con esito positivo. | Isolamento host / blocco IP temporaneo su firewall locale. | **< 15 Minuti** |
| **HIGH (P2)** | Modifica anomala file di sistema (Heimdall FIM), porta critica aperta non censita. | Generazione snapshot forense e alert prioritario. | **< 1 Ora** |
| **MEDIUM (P3)** | Utente privo di MFA (Yggdrasil), mancata rotazione credenziali, configurazione debole. | Notifica nel report settimanale di conformità. | **< 24 Ore** |
| **LOW / INFO (P4)** | Scansione periodica completata con esito regolare, aggiornamento feed IOC. | Archiviazione log nei registri locali cifrati. | **Nessuna azione richiesta** |

---

## 3. Procedure di Risoluzione per Categoria di Allarme (Playbooks)

### Scenario A: Esca Mjolnir / Honeypot Violata
* **Sintomo**: Ricezione allarme da Gjallarhorn: `[CRITICAL] Honeytoken accessed on host SERVER-APP01`.
* **Cosa significa**: Un utente malintenzionato o un malware sta scansionando le cartelle di rete e ha aperto un file civetta appositamente posizionato da Mjolnir.
* **Procedura Operativa per l'IT**:
  1. Aprire la dashboard di Ragnarök o il report Mjolnir allegato all'email.
  2. Identificare l'indirizzo IP interno sorgente e l'account utente che ha effettuato l'accesso.
  3. Eseguire il comando di isolamento host consigliato dal Playbook:
     ```powershell
     # Esempio isolamento rapido host Windows via PowerShell
     Disable-NetAdapter -Name "Ethernet0" -Confirm:$false
     ```
  4. Lanciare il triage forense automatico:
     ```bash
     python Mjolnir/main.py triage --target <IP_INFETTO>
     ```
  5. Verificare i file aperti e i processi attivi prima di riammettere la macchina in rete.

---

### Scenario B: Attacco Brute Force Rilevato da Fenrir
* **Sintomo**: Allarme `[HIGH] Multiple failed authentication attempts on Port 22/3389`.
* **Cosa significa**: Un attaccante esterno o interno sta tentando di indovinare le credenziali di accesso.
* **Procedura Operativa per l'IT**:
  1. Verificare che Fenrir abbia applicato la regola di blocco automatico nell'`Active Response`.
  2. Verificare l'IP nel database IOC di Fenrir:
     ```bash
     python Fenrir/main.py check --ip <IP_ATTACCANTE>
     ```
  3. Se l'IP è interno, verificare se la macchina appartiene a un dipendente con credenziali scadute o compromesse.
  4. Forzare il reset della password dell'account target.

---

### Scenario C: Rilievo Non-Conformità NIS2 / GDPR da Forseti
* **Sintomo**: Report di audit settimanale con punteggio di conformità inferiore all'80%.
* **Cosa significa**: Sono presenti configurazioni deboli (es. backup non immutabili, logging disattivato).
* **Procedura Operativa per l'IT**:
  1. Aprire il report PDF/HTML generato in `Forseti/reports/`.
  2. Consultare la sezione **"Priorità di Rimedio"**.
  3. Eseguire lo script di hardening automatico o applicare le GPO/policy indicate nella scheda tecnica.
  4. Rilanciare l'audit per verificare l'aumento del punteggio:
     ```bash
     python Forseti/main.py assess
     ```

---

## 4. Manutenzione Ordinaria & Healthcheck della Suite

Per verificare che tutti i demoni e moduli di Asgard siano operativi sul server:

1. **Controllo Stato Globale**:
   ```bash
   python Ragnarok/backend/server.py --health
   ```
2. **Aggiornamento Intelligence Minacce**:
   ```bash
   python Fenrir/main.py update-feeds
   ```
3. **Backup Database Locale SQLite**:
   I database locali si trovano nella cartella `data/` di ciascun modulo. È sufficiente includere la directory root di Asgard nei backup di sistema schedulati.
