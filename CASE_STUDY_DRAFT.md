# Bozza post LinkedIn/case study — Asgard

*Modifica liberamente tono e lunghezza. Ho lasciato due versioni: una breve per LinkedIn, una più lunga per un articolo/blog post.*

---

## Versione breve (LinkedIn)

Negli ultimi mesi ho costruito Asgard: una suite di 7 strumenti di sicurezza difensiva open source — HIDS, scanner di rete, triage forense, audit Active Directory, threat intelligence, motore SOAR, orchestratore desktop.

Poi ho fatto una cosa che consiglio a chiunque abbia un portfolio tecnico: **ho smesso di scrivere e ho iniziato a verificare.**

Ho fatto leggere ogni singola riga di codice — non i README, il codice — a una revisione tecnica indipendente. Il risultato non è stato piacevole da leggere:

→ Un modulo dichiarava di aver bloccato un IP malevolo anche quando il comando firewall falliva.
→ Un audit tool per Active Directory non aveva nemmeno una libreria LDAP: era puro scoring su dati finti.
→ Un motore SOAR eseguiva azioni reali, ma su un IP hardcoded, mai su quello dell'incidente vero.
→ Nessuna delle mie API aveva autenticazione.

Il pattern comune: il README prometteva sempre più di quanto il codice facesse davvero.

Ho passato la sessione successiva a chiudere quella distanza, modulo per modulo. Poi ho aggiunto due tasselli che mancavano — un compliance checker GDPR/NIS2 per PMI (Forseti) e un hub di notifiche centralizzato (Gjallarhorn) — con lo stesso criterio: se non è testato, non esiste.

Oggi: 9 moduli, oltre 300 test automatici, CI verde su ogni repository.

La lezione più utile non è tecnica. È che un progetto "quasi finito" e uno "finito" si distinguono da una sola domanda: *l'ho verificato davvero, o mi sono fidato di come suonava?*

🔗 [github.com/Fioru12/Asgard](https://github.com/Fioru12/Asgard)

#cybersecurity #blueteam #python #opensource

---

## Versione lunga (articolo/blog)

### Il progetto che sembrava finito

Asgard è nato come una serie di strumenti di sicurezza difensiva — sette moduli, ciascuno con un nome della mitologia norrena e un compito preciso: Heimdall monitora i log e blocca gli attacchi brute-force, Bifrost scansiona la rete, Mjolnir fa triage forense su un host compromesso, Yggdrasil controlla la postura di sicurezza di Active Directory, Fenrir aggrega threat intelligence pubblica, Sleipnir orchestra tutto tramite playbook, e Ragnarök doveva essere il "gioiello della corona": un'app desktop con un assistente AI che comanda l'intera suite.

Su carta, un portfolio completo. Ogni modulo aveva un README curato, badge CI, licenza MIT, test unitari. Sembrava pronto.

### La domanda che ho smesso di evitare

A un certo punto mi sono chiesto: *quanto di quello che il README dice è vero al 100%?*

Non l'avevo mai verificato riga per riga. Avevo scritto i README mentre costruivo, con l'intenzione di implementare tutto — ma tra l'intenzione e il codice finito, in sette progetti paralleli, si accumulano crepe che nessuno controlla mai davvero, perché i test coprono il caso felice e il README suona bene.

Ho deciso di fare quello che avrei chiesto a un collega di fare sul mio codice: una revisione tecnica completa, modulo per modulo, leggendo ogni file sorgente — non fidandomi della documentazione.

### Quello che ho trovato

Non è stato un esercizio confortante.

**Heimdall**, il sistema di rilevamento intrusioni, aveva un bug che a posteriori mi ha fatto sudare freddo: se il comando per bloccare un IP falliva per qualunque motivo (permessi, firewall non installato, timeout), il codice catturava l'eccezione e impostava comunque `success = True`. Il sistema notificava "IP bloccato con successo" — mentre l'attaccante aveva ancora accesso completo. Un falso senso di sicurezza attiva, il tipo di bug che in un vero incidente costa caro.

**Yggdrasil**, l'audit tool per Active Directory, non aveva *nessuna* libreria LDAP nel progetto. Zero righe di codice che si connettessero davvero a un domain controller. Era un motore di scoring che girava su un dizionario Python hardcoded — e il flag `--simulate` che avrebbe dovuto permettere un audit reale aveva un bug di `argparse` che lo teneva bloccato su `True` comunque, anche passando l'opzione per disattivarlo.

**Sleipnir**, il motore di orchestrazione, eseguiva davvero i comandi verso gli altri moduli — non erano stub — ma ignorava i parametri reali dell'incidente. Uno scan di rete lanciato da un playbook puntava sempre a `127.0.0.1`, mai all'IP effettivo dell'attaccante che aveva scatenato l'allarme.

**Fenrir** prometteva aggregazione da più feed di threat intelligence; nel codice ne esisteva uno solo, e per giunta troncava il catalogo scaricato alle prime 20 voci — scartando il 98% dei dati reali a ogni aggiornamento.

**Nessuna** delle API esposte dai moduli aveva autenticazione. Lo scanner di rete di Bifrost, in particolare, era di fatto un servizio di port-scanning pubblico per chiunque lo raggiungesse.

### Il pattern, non i singoli bug

Il dettaglio interessante non è la lista dei bug — è che seguivano tutti lo stesso schema: **la distanza tra ciò che il progetto dichiara di fare e ciò che il codice fa davvero.** Non bug di battitura, ma funzionalità core assenti o rotte, mascherate da un'interfaccia (CLI, README, badge) che comunicava competenza e completezza.

È un pattern facile da produrre in buona fede, quando si lavora da soli su più progetti in parallelo: si scrive l'interfaccia e la documentazione con l'intenzione ferma di implementare tutto, il codice iniziale copre il caso più semplice, i test verificano quel caso, e la scadenza (o la noia, o il prossimo progetto che chiama) arriva prima che si torni a chiudere i casi limite. Il risultato è un progetto che *sembra* finito a chiunque legga solo il README — inclusi, spesso, gli autori stessi qualche mese dopo.

### La correzione

Ho affrontato ogni bug non come un fix isolato, ma chiedendomi: *cosa serve perché questo modulo faccia davvero quello che dichiara?*

- Heimdall: il fallimento del blocco ora è un fallimento vero, con una notifica critica separata, più un meccanismo di TTL/sblocco per non trasformare un falso positivo in un self-DoS permanente.
- Yggdrasil: ha ora una vera integrazione LDAP/LDAPS (libreria `ldap3`), testata offline con un server LDAP mock — nessun Active Directory reale necessario per validarla, ma nessuna finzione quando ce n'è uno vero.
- Sleipnir: i parametri dell'evento reale vengono ora risolti e validati prima di essere passati alle azioni.
- Fenrir: il troncamento è sparito, e ho aggiunto un secondo feed (OTX) invece di lasciarlo solo citato nel nome del progetto.
- Ogni API ora richiede autenticazione, con una chiave generata automaticamente se non configurata esplicitamente — mai un endpoint aperto per dimenticanza.

Poi ho aggiunto quello che mancava per davvero, non per completezza estetica: **Forseti**, un compliance checker GDPR/NIS2 pensato per PMI (25 controlli reali, non simbolici), e **Gjallarhorn**, un hub di notifiche centralizzato che elimina la duplicazione di logica che avevo sparso in tre moduli diversi.

### Il numero che conta

Oggi la suite conta 9 moduli, oltre 300 test automatici, pipeline CI verdi su ogni singolo repository — verificate, non dichiarate.

Ma il vero risultato di questo esercizio non è il numero di test. È aver reso ripetibile una domanda che prima non mi ponevo abbastanza spesso: *questo funziona davvero, o suona solo bene?*

È una domanda scomoda da farsi sul proprio lavoro. Ma è l'unica che separa un portfolio che regge a un colloquio tecnico da uno che regge solo a uno sguardo veloce.

🔗 Il codice, tutti i moduli, tutte le CI: [github.com/Fioru12/Asgard](https://github.com/Fioru12/Asgard)
