# 🤝 ASGARD CYBER SUITE — GUIDA COMMERCIALE & OPERATIVA PER MSP E SYSTEM INTEGRATOR

> **Come erogare servizi SOC Sovrani, Audit NIS2/GDPR e Difesa Attiva ai vostri clienti con margini elevati.**

---

## 1. Perché Asgard è la Piattaforma Ideale per i Partner MSP

Gli MSP e System Integrator tradizionali affrontano tre grandi sfide:
1. **Costi proibitivi dei SIEM Enterprise** (Microsoft Sentinel, Splunk, CrowdStrike richiedono decine di migliaia di euro e team dedicati 24/7).
2. **Resistenza al Cloud / Compliance GDPR** (molti clienti industriali, bancari, legali o sanitari non vogliono trasferire i log sui cloud USA).
3. **Mancanza di personale specializzato** (difficoltà a reperire analisti SOC Tier 1/2).

### La Risposta di Asgard:
* **100% On-Premises & Sovrano**: Nessun dato esce dall'infrastruttura del cliente.
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

| Caratteristica | Antivirus Tradizionale / EDR Base | SIEM Cloud Enterprise (es. Sentinel) | Asgard Cyber Suite |
| :--- | :--- | :--- | :--- |
| **Rilevamento Malware Noto** | ✅ Sì | ✅ Sì | ✅ Sì (Mjolnir + YARA) |
| **Active Deception (Honeypot / Honeytoken)** | ❌ No | ❌ Modulo aggiuntivo costoso | ✅ **Nativo (Mjolnir/Sleipnir)** |
| **Audit Continuo NIS2 & GDPR** | ❌ No | ❌ Richiede consulenza esterna | ✅ **Automatico (Forseti)** |
| **Privacy Dati & Zero Cloud Leakage** | ⚠️ Dipende dal fornitore | ❌ Log inviati su cloud estero | ✅ **100% On-Premise Sovrano** |
| **Generazione Playbook Guidata da AI** | ❌ No | ⚠️ Solo prompt generici cloud | ✅ **RAG Locale Specialistico** |
| **Costo di Avviamento** | Basso | Molto Alto (€ 15k+ / anno) | **Accessibile & Scalabile** |

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

1. **Deploy Appliance/Server**:
   ```bash
   bash setup-express.sh
   # oppure su Windows:
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```
2. **Configurazione Notifiche & SMTP**:
   Impostare i parametri in `.env` per ricevere gli alert su Teams / Email / Slack del NOC.
3. **Lancio Primo Audit Baseline**:
   ```bash
   python Forseti/main.py assess
   ```
4. **Attivazione Guardiani & Trappole Deception**:
   ```bash
   python Mjolnir/main.py deploy-traps
   ```
