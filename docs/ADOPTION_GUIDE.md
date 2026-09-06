# Primi 30 giorni con Asgard

> Guida pratica per PMI e team di sicurezza che adottano Asgard per la prima volta.

---

## 📋 Prima di iniziare

- Server Linux/Windows (4GB RAM, 2 CPU)
- Docker (opzionale, consigliato)
- Rete LAN con sistemi da monitorare
- 30 min/giorno per 30 giorni

---

## 🗓️ Settimana 1: Installazione

### Giorno 1-2: Avvia Ragnarök

```bash
git clone https://github.com/Fioru12/Asgard.git
cd Asgard/Ragnarök/backend
pip install -r requirements.txt
python server.py
```

Annota la password admin stampata in console.

### Giorno 3: Rivendica l'admin

Vai su `http://localhost:8000/dashboard` → banner "Configurazione iniziale" → inserisci console password + nuovo username + nuova password (min 8 caratteri).

### Giorno 4-5: Crea il team

| Utente | Ruolo | Permessi |
|--------|-------|----------|
| Tu | `admin` | Tutto |
| Senior | `analyst` | Query, export, notifiche (no execute) |
| Junior | `viewer` | Solo lettura |

```bash
curl -X POST http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"username":"collega","password":"Pass123!","role":"analyst"}'
```

### Giorno 6-7: Verifica

- [ ] Login admin/analyst/viewer → OK
- [ ] Viewer non vede "Re-indicizza" → OK
- [ ] Audit log visibile → OK

---

## 🗓️ Settimana 2: Moduli

### Giorno 8-10: Heimdall (HIDS)

```bash
cd ../../Heimdall && pip install -r requirements.txt
python main.py --test-alert
```
Verifica: dashboard → timeline → alert.

### Giorno 11-12: Bifrost (scanner)

```bash
cd ../Bifrost && pip install -r requirements.txt
python main.py --target 192.168.1.0/24 --scan-type banner
```

### Giorno 13-14: Fenrir (threat intel)

```bash
cd ../Fenrir && pip install -r requirements.txt
python main.py --update  # CISA KEV
```

---

## 🗓️ Settimana 3: Automazione

### Giorno 15-17: Notifiche

Configura `.env`:
```bash
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Giorno 18-19: Report automatico

```bash
RAG_REPORT_SEND_CRON=08:00
```

### Giorno 20-21: Playbook Sleipnir

```bash
cd ../Sleipnir
```

Crea `playbooks/ssh-response.yaml`:
```yaml
name: "SSH Brute Force Response"
trigger: "heimdall.alert"
steps:
  - action: "bifrost.scan"
    params: {target: "{{ alert.source_ip }}", scan_type: "fast"}
  - action: "mjolnir.triage"
    params: {host: "{{ alert.affected_host }}"}
  - action: "gjallarhorn.notify"
    params: {message: "Bruteforce da {{ alert.source_ip }}"}
```

---

## 🗓️ Settimana 4: Produzione

### Giorno 22-24: TLS

```bash
# Self-signed (test)
ASGARD_TLS=true python server.py

# Produzione
ASGARD_TLS=true ASGARD_TLS_CERTFILE=/etc/ssl/certs/ragnarok.pem ASGARD_TLS_KEYFILE=/etc/ssl/private/ragnarok.key python server.py
```

### Giorno 25-26: Backup

```bash
curl -X POST http://localhost:8000/api/v1/backup \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"path":"/backup/asgard/nightly.zip"}'
```

### Giorno 27-28: Compliance

```bash
cd ../Forseti
python main.py --report  # GDPR/NIS2
```

### Giorno 29-30: Handover

- [ ] Esporta audit log
- [ ] Backup finale
- [ ] Scrivi documento interno
- [ ] Crea "backup admin"

---

## 🎯 Checkpost operativo

- [ ] 2 moduli connessi → alert visibili
- [ ] Notifiche su almeno un canale
- [ ] Report giornaliero automatico
- [ ] Almeno un playbook
- [ ] Backup verificato
- [ ] TLS attivo
- [ ] Team usa Asgard ogni giorno

---

## 🆘 Problemi comuni

| Problema | Soluzione |
|----------|-----------|
| Password admin non funziona | Cancella `ragnarok_auth.db` e riparti (solo se non hai dati) |
| Teams non riceve alert | Verifica webhook URL con curl |
| Report non parte | Formato: `08:00` (non `8:00`) |
| Backup fallisce | Spazio su disco? Path scrivibile? |

---

<div align="center">

**Asgard è vivo.** Più lo usi, più vale.

⭐ su GitHub se ti è utile.

</div>
