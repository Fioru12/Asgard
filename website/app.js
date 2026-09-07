// Asgard Cyber Suite - Apple-grade Interactive Controller v2.4

document.addEventListener('DOMContentLoaded', () => {
  initSegmentedCalculator();
  initBillingSwitcher();
  initDualViewSimulation();
  initFleetTelemetry();
});

// ---------------------------------------------------------------------------
// 1. Apple-style Segmented Controls Compliance Calculator
// ---------------------------------------------------------------------------
function initSegmentedCalculator() {
  const segmentedGroups = document.querySelectorAll('.segmented-control');
  const scoreVal = document.getElementById('calc-score-val');
  const scoreCircle = document.getElementById('calc-score-circle');
  const scoreStatus = document.getElementById('calc-score-status');
  const fineAmount = document.getElementById('calc-fine-amount');

  if (!scoreVal || !scoreCircle) return;

  const currentChoices = {
    size: 'pmi',
    mfa: 'partial',
    adaudit: 'never',
    irplan: 'no'
  };

  segmentedGroups.forEach(group => {
    const groupName = group.getAttribute('data-group');
    const buttons = group.querySelectorAll('.seg-btn');

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentChoices[groupName] = btn.getAttribute('data-val');
        recalculateScore();
      });
    });
  });

  function recalculateScore() {
    let score = 100;

    // MFA impact
    if (currentChoices.mfa === 'none') score -= 35;
    else if (currentChoices.mfa === 'partial') score -= 15;

    // AD & M365 audit impact
    if (currentChoices.adaudit === 'never') score -= 25;
    else if (currentChoices.adaudit === 'old') score -= 12;

    // Incident Response plan impact
    if (currentChoices.irplan === 'no') score -= 25;
    else if (currentChoices.irplan === 'untested') score -= 10;

    score = Math.max(10, Math.min(100, score));
    scoreVal.textContent = score;

    // Dynamic Visual Feedback
    if (score >= 80) {
      scoreCircle.style.borderColor = 'var(--emerald)';
      scoreCircle.style.boxShadow = '0 0 35px rgba(16, 185, 129, 0.4)';
      scoreStatus.textContent = 'CONFORME (BASSO RISCHIO SANZIONI)';
      scoreStatus.style.color = 'var(--emerald)';
      fineAmount.textContent = "0 € (Rischio Minimo Sanzionatorio)";
      fineAmount.style.color = "var(--emerald)";
    } else if (score >= 50) {
      scoreCircle.style.borderColor = 'var(--amber)';
      scoreCircle.style.boxShadow = '0 0 35px rgba(245, 158, 11, 0.4)';
      scoreStatus.textContent = 'RISCHIO MEDIO (INADEMPIENZA PARZIALE)';
      scoreStatus.style.color = 'var(--amber)';
      updateFine();
    } else {
      scoreCircle.style.borderColor = 'var(--rose)';
      scoreCircle.style.boxShadow = '0 0 35px rgba(244, 63, 94, 0.4)';
      scoreStatus.textContent = 'RISCHIO CRITICO (NON CONFORME NIS2/GDPR)';
      scoreStatus.style.color = 'var(--rose)';
      updateFine();
    }

    function updateFine() {
      fineAmount.style.color = "var(--rose)";
      if (currentChoices.size === 'micro') {
        fineAmount.textContent = "Fino a 500.000 €";
      } else if (currentChoices.size === 'pmi') {
        fineAmount.textContent = "Fino a 7.000.000 € (o 1.4% fatturato)";
      } else {
        fineAmount.textContent = "Fino a 10.000.000 € (o 2.0% fatturato)";
      }
    }
  }

  recalculateScore();
}

// ---------------------------------------------------------------------------
// 2. Billing Toggle Switcher (Annual -20% vs Monthly)
// ---------------------------------------------------------------------------
function initBillingSwitcher() {
  const btnMonthly = document.getElementById('bill-monthly');
  const btnAnnual = document.getElementById('bill-annual');
  const priceBusiness = document.getElementById('price-business');
  const periodBusiness = document.getElementById('period-business');
  const priceMsp = document.getElementById('price-msp');
  const periodMsp = document.getElementById('period-msp');

  if (!btnMonthly || !btnAnnual) return;

  btnMonthly.addEventListener('click', () => {
    btnMonthly.classList.add('active');
    btnAnnual.classList.remove('active');

    priceBusiness.innerHTML = '249 € <span id="period-business">/ mese</span>';
    priceMsp.innerHTML = '699 € <span id="period-msp">/ mese</span>';
  });

  btnAnnual.addEventListener('click', () => {
    btnAnnual.classList.add('active');
    btnMonthly.classList.remove('active');

    priceBusiness.innerHTML = '199 € <span id="period-business">/ mese (annuale)</span>';
    priceMsp.innerHTML = '559 € <span id="period-msp">/ mese (annuale)</span>';
  });
}

// ---------------------------------------------------------------------------
// 3. Synchronized Dual-View Simulation Engine
// ---------------------------------------------------------------------------
function initDualViewSimulation() {
  const runBtn = document.getElementById('btn-run-simulation');
  const terminal = document.getElementById('terminal-logs');
  const statusText = document.getElementById('sim-status-text');

  // Inspector Elements
  const statePill = document.getElementById('inc-state-pill');
  const idTag = document.getElementById('inc-id-tag');
  const titleDisplay = document.getElementById('inc-title-display');
  const descDisplay = document.getElementById('inc-desc-display');
  const srcIp = document.getElementById('inc-src-ip');
  const targetHost = document.getElementById('inc-target-host');
  const ctiScore = document.getElementById('inc-cti-score');
  const actionStatus = document.getElementById('inc-action-status');
  const mitreTag = document.getElementById('inc-mitre-tag');

  if (!runBtn || !terminal) return;

  const simulationTimeline = [
    {
      time: 400,
      log: "[*] Aggancio alla pipeline di telemetria Asgard in corso...",
      logClass: "log-cyan",
      inspector: {
        state: "STANDBY",
        stateClass: "b-ok",
        id: "INC-IDLE",
        title: "Infrastruttura Protetta",
        desc: "Tutti gli agenti Windows riportano heartbeat nominali.",
        src: "127.0.0.1",
        target: "DC-PRIMARY-01",
        cti: "0 / 100",
        action: "In Ascolto",
        mitre: "T1078 - Valid Accounts (Audited)"
      }
    },
    {
      time: 1300,
      log: "[HEIMDALL] Rilevato evento Windows Security 4625 da IP 203.0.113.42 (Tentativi RDP falliti ripetuti)",
      logClass: "log-amber",
      inspector: {
        state: "SUSPICIOUS",
        stateClass: "b-high",
        id: "INC-2026-9041",
        title: "Accessi Falliti Ripetuti",
        desc: "5 tentativi errati di login in 10 secondi per utente 'Administrator'.",
        src: "203.0.113.42",
        target: "DC-PRIMARY-01",
        cti: "Query in corso...",
        action: "Campionamento log",
        mitre: "T1110.001 - Password Guessing"
      }
    },
    {
      time: 2400,
      log: "[HEIMDALL] Soglia di attacco superata (>5 tentativi/60s) -> Generato allarme critico di intrusione!",
      logClass: "log-rose",
      inspector: {
        state: "ATTACK ACTIVE",
        stateClass: "b-crit",
        id: "INC-2026-9041",
        title: "Brute-Force in Corso",
        desc: "Rilevata attività di attacco a dizionario su porta 3389.",
        src: "203.0.113.42",
        target: "DC-PRIMARY-01",
        cti: "Query Fenrir CTI...",
        action: "Escalation automatica",
        mitre: "T1110.001 - Password Guessing"
      }
    },
    {
      time: 3500,
      log: "[SLEIPNIR] Attivazione playbook condizionale 'contain_bruteforce_host.yaml' (AST Engine)",
      logClass: "log-cyan",
      inspector: {
        state: "SOAR DISPATCHED",
        stateClass: "b-high",
        id: "INC-2026-9041",
        title: "Esecuzione Playbook di Contenimento",
        desc: "Sleipnir coordina Fenrir, Bifrost, Mjolnir e Heimdall.",
        src: "203.0.113.42",
        target: "DC-PRIMARY-01",
        cti: "Analisi reputazione...",
        action: "Playbook #04 Attivo",
        mitre: "T1110 - Brute Force"
      }
    },
    {
      time: 4600,
      log: "[FENRIR] Feed CTI: IP 203.0.113.42 confermato Botnet C2 in archivio KEV (Score: 94/100 MALICIOUS)",
      logClass: "log-rose",
      inspector: {
        state: "CONFIRMED C2",
        stateClass: "b-crit",
        id: "INC-2026-9041",
        title: "Attore Malevolo Confermato",
        desc: "L'indirizzo sorgente appartiene a un cluster di scansione globale.",
        src: "203.0.113.42",
        target: "DC-PRIMARY-01",
        cti: "94 / 100 (MALICIOUS C2)",
        action: "Approvazione Blocco Firewall",
        mitre: "T1110.001 - Password Guessing"
      }
    },
    {
      time: 5700,
      log: "[MJOLNIR] Triage rapido completato in 48s: 0 webshell YARA, dump memoria archiviato per forensics",
      logClass: "log-emerald",
      inspector: {
        state: "HOST VERIFIED",
        stateClass: "b-ok",
        id: "INC-2026-9041",
        title: "Nessuna Compromissione Locale",
        desc: "Memoria volatile pulita, nessun payload o chiave di persistenza rilevata.",
        src: "203.0.113.42",
        target: "DC-PRIMARY-01",
        cti: "94 / 100",
        action: "Triage OK",
        mitre: "T1059 - Command & Scripting"
      }
    },
    {
      time: 6800,
      log: "[HEIMDALL] Difesa Attiva: IP 203.0.113.42 bloccato istantaneamente dalle regole firewall [SAFE/DRY-RUN]",
      logClass: "log-emerald",
      inspector: {
        state: "CONTAINED",
        stateClass: "b-ok",
        id: "INC-2026-9041",
        title: "Attaccante Isolato",
        desc: "Regola firewall applicata sull'host. Comunicazioni interrotte.",
        src: "203.0.113.42 (BLOCKED)",
        target: "DC-PRIMARY-01 (SECURE)",
        cti: "94 / 100",
        action: "FIREWALL DROP APPLIED",
        mitre: "T1110 - Neutralized"
      }
    },
    {
      time: 7900,
      log: "[GJALLARHORN] Alert inviato al canale Microsoft Teams / Telegram dell'IT Manager. Report PDF archiviato.",
      logClass: "log-cyan",
      inspector: {
        state: "RESOLVED",
        stateClass: "b-ok",
        id: "INC-2026-9041",
        title: "Incidente Concluso con Successo",
        desc: "Notifiche inviate e dossier forense salvato per conformità NIS2.",
        src: "203.0.113.42 (ISOLATED)",
        target: "DC-PRIMARY-01 (SECURE)",
        cti: "94 / 100",
        action: "INCIDENT RESOLVED",
        mitre: "T1110 - Neutralized"
      }
    }
  ];

  let isRunning = false;

  runBtn.addEventListener('click', () => {
    if (isRunning) return;
    isRunning = true;
    runBtn.disabled = true;
    runBtn.textContent = "Simulazione in Corso...";
    statusText.textContent = "Stato: Esecuzione Playbook...";
    terminal.innerHTML = "";

    simulationTimeline.forEach(evt => {
      setTimeout(() => {
        // Append log line
        const div = document.createElement('div');
        div.className = `log-entry ${evt.logClass}`;
        div.textContent = evt.log;
        terminal.appendChild(div);
        terminal.scrollTop = terminal.scrollHeight;

        // Synchronize Inspector
        statePill.textContent = evt.inspector.state;
        statePill.className = `badge-tag ${evt.inspector.stateClass}`;
        idTag.textContent = `ID: ${evt.inspector.id}`;
        titleDisplay.textContent = evt.inspector.title;
        descDisplay.textContent = evt.inspector.desc;
        srcIp.textContent = evt.inspector.src;
        targetHost.textContent = evt.inspector.target;
        ctiScore.textContent = evt.inspector.cti;
        actionStatus.textContent = evt.inspector.action;
        mitreTag.textContent = evt.inspector.mitre;
      }, evt.time);
    });

    const finishTime = simulationTimeline[simulationTimeline.length - 1].time + 1000;
    setTimeout(() => {
      isRunning = false;
      runBtn.disabled = false;
      runBtn.textContent = "Riavvia Simulazione SOC";
      statusText.textContent = "Stato: Incidente Risolto";
    }, finishTime);
  });
}

// ---------------------------------------------------------------------------
// 4. Subtle Fleet Telemetry Variation
// ---------------------------------------------------------------------------
function initFleetTelemetry() {
  const epStat = document.getElementById('stat-endpoints');
  if (!epStat) return;

  let count = 48;
  setInterval(() => {
    const delta = Math.random() > 0.65 ? (Math.random() > 0.5 ? 1 : -1) : 0;
    count = Math.max(46, Math.min(52, count + delta));
    epStat.textContent = count;
  }, 4500);
}

// ---------------------------------------------------------------------------
// 5. Pilot Modal Request Trigger
// ---------------------------------------------------------------------------
function openPilotModal(planName) {
  const message = `Richiesta Programma Pilota 30 Giorni per "${planName}"\n\n` +
    `Cosa include la tua prova gratuita:\n` +
    `• Tutti i 9 moduli attivi e configurati\n` +
    `• Agente Windows PowerShell con deploy GPO senza dipendenze\n` +
    `• Audit di sicurezza Active Directory e Microsoft 365 Entra ID\n` +
    `• Generazione report esecutivo PDF a norma NIS2 e DORA\n` +
    `• Accordo contrattuale a responsabilità zero (PILOT_BETA_AGREEMENT.md)\n\n` +
    `Un nostro technical account specialist ti assisterà nell'attivazione: enterprise@asgard-sec.eu`;
  alert(message);
}
window.openPilotModal = openPilotModal;
