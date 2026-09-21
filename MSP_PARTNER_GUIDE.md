# 🤝 ASGARD CYBER SUITE — GUIDA COMMERCIALE & OPERATIVA PER MSP E SYSTEM INTEGRATOR

> **Come erogare servizi SOC Sovrani, Audit NIS2/GDPR e Difesa Attiva ai vostri clienti con margini elevati.**

---

## 1. Perché Asgard è la Piattaforma Ideale per i Partner MSP

Gli MSP e System Integrator tradizionali affrontano tre grandi sfide:
1. **Costi proibitivi dei SIEM Enterprise** (Microsoft Sentinel, Splunk, CrowdStrike richiedono decine di migliaia di euro e team dedicati 24/7).
2. **Resistenza al Cloud / Compliance GDPR** (molti clienti industriali, bancari, legali o sanitari non vogliono trasferire i log sui cloud USA).
3. **Mancanza di personale specializzato** (difficoltà a reperire analisti SOC Tier 1/2).

### La Risposta di Asgard (v2.5 Enterprise & MSP Tier):
* **100% On-Premises & Sovrano**: Nessun dato esce dall'infrastruttura del cliente.
* **Architettura Multi-Tenant & OIDC Single Sign-On (v2.5)**: Gestisci N clienti da un unico pannello isolato con autenticazione federata Azure AD / Entra ID.
* **Enrollment Centralizzato degli Agent**: Distribuisci gli agent Heimdall sugli host con token monouso ed auto-sync delle regole via API.
* **Osservabilità Prometheus & Grafana**: Monitora lo stato di salute di tutti i sensori e tenant in tempo reale.
* **Intelligenza Artificiale Locale (Ragnarök)**: Sostituisce l'analista Tier 1 generando i playbook di remediation già pronti.
* **Pronto per NIS2 (D.Lgs. 138/2024)**: Permette agli MSP di vendere contratti di adeguamento continuo e compliance audit a valore aggiunto.

---

## 2. Modelli di Erogazione del Servizio (Come monetizzare con i Clienti)

### Modello A: SOC Co-Gestito (Co-Managed SOC)
* **Target**: PMI strutturate con 1-2 tecnici IT interni.
* **Come funziona**: L'MSP installa Asgard sul server del cliente. Gli allarmi di livello 1 e le notifiche arrivano direttamente all'IT aziendale con i playbook di Ragnarök. Se l'allarme è critico (P1), scala automaticamente all'helpdesk dell'MSP.
* **Prezzo consigliato al cliente finale**: € 350 - € 650 / mese.

### Modello B: Managed Security & Compliance (Full MSP)
* **Target**: PMI senza personale IT interno.
* **Come funziona**: L'MSP gestisce Asgard al 100%. L'MSP invia ogni mese il report di conformità NIS2/GDPR generato da Forseti e garantisce la risposta agli incidenti.
* **Prezzo consigliato al cliente finale**: € 600 - € 1.500 / mese per azienda.

### Modello C: One-Off Audit & Assessment (Grimaldello Commerciale)
* **Target**: Nuovi prospect o clienti che non hanno ancora contratti di sicurezza.
* **Come funziona**: L'MSP esegue un assessment iniziale con `Forseti` e `Yggdrasil`, consegnando un report executive con vulnerabilità, configurazioni errate e calcolo del rischio sanzione NIS2.
* **Prezzo consigliato**: € 800 - € 2.500 una tantum (spesso convertito in contratto annuale).

---

## 3. Matrice Comparativa: Asgard vs Alternative di Mercato

> **Nota per chi presenta questa tabella**: ogni riga è stata verificata contro il codice sorgente reale al 20/09/2026. Una funzionalità presente in una versione precedente di questo documento (deception/honeypot nativo) è stata rimossa perché non esiste nella suite — se un prospect tecnico la chiede, la risposta onesta è "sul roadmap, non ancora disponibile", mai "sì, ce l'abbiamo". Il rilevamento "YARA" era in una versione precedente codice presente ma mai collegato al flusso di triage reale, ed era inoltre un set di firme regex interne solo ispirate allo stile YARA, non il motore vero. Entrambi i problemi sono stati risolti: Mjolnir ora usa `yara-python` (i binding ufficiali al motore YARA/libyara reale), compila regole `.yar` reali da `Mjolnir/rules/` (14 regole totali: 3 in `default.yar` + 11 in `extended.yar`, che coprono webshell PHP/ASPX/JSP, tool di credential dumping, LOLBin download-and-execute, persistenza via registro/scheduled task, beacon Cobalt Strike, marker ransomware, macro Office malevole, dump di LSASS, movimento laterale via PsExec, DNS tunneling) ed è cablato nel flusso di triage. Nota sulla provenienza: sono regole scritte internamente da IOC/TTP pubblicamente noti, non copiate da ruleset di terzi — i due ruleset pubblici più citati (Yara-Rules/rules: GPLv2; Neo23x0/signature-base: licenza DRL 1.1 che vieta l'uso commerciale senza pagare) sono stati **deliberatamente esclusi** perché incompatibili con un prodotto venduto commercialmente. Va presentato come "motore YARA reale, copertura di partenza propria", non come un ruleset commerciale completo.

| Caratteristica | Antivirus Tradizionale / EDR Base | SIEM Cloud Enterprise (es. Sentinel) | Asgard Cyber Suite |
| :--- | :--- | :--- | :--- |
| **Rilevamento Malware Noto (hash + firme)** | ✅ Sì | ✅ Sì | ✅ Sì (Mjolnir: verifica hash via VirusTotal + scansione a firme YARA reali su eseguibili sospetti) |
| **Active Deception (Honeypot / Honeytoken)** | ❌ No | ❌ Modulo aggiuntivo costoso | ❌ **Non presente oggi** (valutabile come sviluppo futuro) |
| **Autovalutazione Guidata NIS2 & GDPR/DORA/ISO27001** | ❌ No | ❌ Richiede consulenza esterna | ✅ **Guidata via questionario (Forseti)** — risposta umana richiesta, lo scoring è automatico |
| **Privacy Dati & Zero Cloud Leakage** | ⚠️ Dipende dal fornitore | ❌ Log inviati su cloud estero | ✅ **100% On-Premise Sovrano** |
| **Generazione Playbook Guidata da AI** | ❌ No | ⚠️ Solo prompt generici cloud | ✅ **RAG Locale Specialistico** |
| **Costo di Avviamento** | Basso | Molto Alto (€ 15k+ / anno) | **Accessibile & Scalabile** |

**Nota sulla profondità dei framework di compliance**: Forseti copre oggi GDPR (13 controlli) e NIS2 (12 controlli) in modo sostanziale; DORA e ISO 27001 sono presenti con 8 controlli ciascuno — una base di lavoro seria (backup, continuità, logging, accessi privilegiati), ma non un assessment completo. Non presentarli a un cliente regolamentato (banche, assicurazioni) come "conformità DORA verificata".

---

## 4. Script di Vendita & FAQ per i Commerciali del Partner

### Domanda del Cliente: *"Ho già l'antivirus e il firewall, perché dovrei pagare anche Asgard?"*
> **Risposta consigliata**:  
> *"L'antivirus e il firewall proteggono solo le porte esterne e i virus noti. Se un attaccante ottiene una password o entra tramite una mail di phishing, l'antivirus non si accorge di nulla. Asgard posiziona trappole invisibili nella rete interna, monitora costantemente che le vostre configurazioni rispettino la legge NIS2 e, in caso di attacco, vi dice esattamente cosa fare per bloccarlo in pochi secondi."*

### Domanda del Cliente: *"I miei dati o i log aziendali vengono inviati a server terzi?"*
> **Risposta consigliata**:  
> *"Assolutamente no. Asgard è una tecnologia 100% Sovrana. Tutto il software, i database e persino il motore di intelligenza artificiale girano sul vostro server locale. Nessuna informazione riservata lascia mai la vostra azienda."*

---

## 5. Checklist di Onboarding per Nuovi Clienti (In 30 Minuti)

> Ogni comando qui sotto è stato eseguito e verificato dal vivo il 29/09/2026 — non solo scritto a scopo illustrativo.

1. **Deploy Appliance/Server**:
   ```bash
   bash setup-express.sh
   # oppure su Windows (richiede il file salvato con BOM UTF-8, già corretto):
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```
2. **Configurazione Notifiche & SMTP**:
   Impostare i parametri in `.env` per ricevere gli alert su Teams / Email / Slack del NOC.
3. **Lancio Primo Audit di Conformità**:
   ```bash
   cd Forseti
   python main.py init --output assessment.yaml   # genera il questionario da compilare
   # ... compilare le risposte in assessment.yaml ...
   python main.py assess --input assessment.yaml --output report.md
   ```
4. **Primo Triage Forense di Verifica**:
   ```bash
   cd Mjolnir
   python main.py triage --simulate   # esegue uno snapshot host + scan IOC di prova
   ```
   (Non esiste oggi una funzionalità di "deception/honeypot" nella suite — se un cliente la richiede esplicitamente, comunicalo come roadmap futura, non come disponibile.)
