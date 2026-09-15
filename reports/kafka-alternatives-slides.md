# Alternative a Kafka gestito per il Pilot Flink

> Script slide per PowerPoint. Ogni sezione `## Slide N` corrisponde a una slide.
> Formato bullet: `- ` per elenco puntato. `Titolo:` e `Sottotitolo:` opzionali.
> `Diagramma:` descrive il flusso architetturale della slide, da rendere come schema grafico (box + frecce), non solo testo.
> Fonte di contesto: [[architettura-pilot-flink|Architettura]], [[infrastruttura-pilot-flink|Infrastruttura]], [[osservabilita-pilot-flink|Osservabilità]].

---

## Slide 1
Titolo: Alternative a Kafka per il Pilot Legacy Data Bridge
Sottotitolo: Ridurre il costo del broker mantenendo scalabilità e semplicità operativa

- Il Pilot Apache Flink gira su Kubernetes e riceve eventi di change data capture che restano sulla coda solo per pochi istanti, giusto il tempo di essere consumati da Flink
- L'obiettivo di questa analisi è trovare un'alternativa che resti economica, scali con il volume di eventi e sia facile da gestire per il Team Infrastruttura, senza richiedere competenze specialistiche aggiuntive
- Oggi il flusso passa da AWS MSK, la versione Kafka completamente gestita da AWS, che si sta però rivelando troppo costosa rispetto al valore reale che offre per questo caso d'uso
- Qualsiasi alternativa dovrà comunque restare compatibile con Debezium/Kafka Connect e con i connettori Flink già in uso, e continuare a integrarsi con Splunk per il monitoraggio

---

## Slide 2
Titolo: Criteri di valutazione
Sottotitolo: Come confrontiamo le opzioni

- Il costo non è solo il prezzo del broker: bisogna considerare anche compute, storage, traffico di rete in uscita e il tempo che il team dedica a gestirlo
- La scalabilità conta perché il volume di eventi CDC può crescere, e la soluzione deve poter scalare orizzontalmente senza dover ripensare l'architettura
- La semplicità operativa è cruciale per un team infrastrutturale che non vuole diventare esperto di un nuovo sistema distribuito: contano operator Kubernetes maturi, upgrade prevedibili e osservabilità pronta all'uso
- La compatibilità con il protocollo Kafka, con Debezium e con i connettori Flink determina quanto lavoro di migrazione sarà davvero necessario
- L'affidabilità riguarda la durabilità dei dati, la replica e la semantica di consegna, che deve restare almeno at-least-once
- Infine conta il footprint: quante risorse cluster servono in aggiunta al JobManager e ai due TaskManager già previsti per il Pilot

---

## Slide 3
Titolo: Opzione A — AWS MSK (baseline attuale)
Sottotitolo: Kafka managed su AWS
Diagramma: SQL Server -> Debezium/Kafka Connect -> [AWS MSK] -> Flink (EKS) -> Aurora PostgreSQL

- AWS MSK è la versione Kafka completamente gestita da Amazon: il provider si occupa di patching, alta disponibilità e integrazione con IAM e PrivateLink, così il team infrastrutturale non deve preoccuparsi della gestione dei broker
- Il vantaggio principale è che richiede pochissimo sforzo operativo, perché tutta la manutenzione è delegata ad AWS e si integra naturalmente con il resto dell'ecosistema
- Il rovescio della medaglia è il costo: si pagano i nodi broker (tipicamente `kafka.m5.large` in tripla replica), lo storage EBS e il traffico cross-AZ, e la fattura cresce anche quando il volume reale di messaggi è modesto
- Per un flusso come il nostro, dove i messaggi CDC vivono sulla coda solo per pochi secondi, questo costo fisso appare sproporzionato rispetto al valore che se ne ricava
- Resta comunque un'opzione sensata se in futuro servissero SLA molto stringenti e il team infrastrutturale restasse piccolo, ma per il Pilot attuale non è la scelta più efficiente

---

## Slide 4
Titolo: Opzione B — Strimzi (Kafka self-managed su EKS)
Sottotitolo: Stesso Kafka, gestito con operator Kubernetes
Diagramma: SQL Server -> Debezium/Kafka Connect -> [Kafka su Strimzi Operator, pod EKS] -> Flink (EKS) -> Aurora PostgreSQL

- Strimzi porta Kafka così com'è, ma lo fa girare direttamente sul cluster EKS che già usiamo, gestito tramite un operator Kubernetes invece che tramite un servizio cloud a pagamento
- Il punto di forza è che tutto resta identico dal punto di vista del protocollo: Debezium e i connettori Flink continuano a funzionare senza modifiche, e non si pagano licenze aggiuntive
- La gestione diventa dichiarativa attraverso le custom resource `Kafka`, `KafkaTopic` e `KafkaUser`, e gli upgrade dei broker avvengono in modo rolling, senza downtime
- Lo storage viaggia su EBS o gp3 e può essere dimensionato in base alla retention breve richiesta dal nostro caso d'uso, tenendo i volumi contenuti
- La parte impegnativa è che il team infrastrutturale si assume la responsabilità di gestire i broker, il consenso KRaft (o ZooKeeper) e il tuning della JVM, un lavoro che prima faceva AWS
- Sul fronte economico si paga solo il compute EKS e lo storage, con una stima di risparmio tra il 50 e il 70 percento rispetto a MSK per carichi di questa dimensione, a fronte di uno sforzo di setup medio che poi si riduce grazie all'operator

---

## Slide 5
Titolo: Opzione C — Redpanda (Kafka-compatible, senza JVM)
Sottotitolo: Broker C++ single-binary, protocollo Kafka nativo
Diagramma: SQL Server -> Debezium/Kafka Connect -> [Redpanda Operator, pod EKS] -> Flink (EKS) -> Aurora PostgreSQL

- Redpanda riscrive il broker Kafka in C++, eliminando la JVM e ZooKeeper, ma mantiene piena compatibilità con l'API Kafka, così Debezium e i connettori Flink continuano a funzionare senza modifiche
- Il vantaggio principale è il footprint: bastano circa un terzo delle risorse rispetto a un broker Kafka tradizionale, con latenze più basse e molto meno tuning da fare
- Essendo compatibile con Debezium, Kafka Connect e i connettori Flink, la migrazione da MSK o da Strimzi risulterebbe quasi trasparente
- La Community Edition è open source, sotto licenza BSL, e per i volumi previsti nel Pilot è più che sufficiente
- Il compromesso è un ecosistema più piccolo rispetto a Kafka, con alcune funzionalità enterprise come il tiered storage o l'RBAC avanzato riservate alla versione a pagamento
- Anche qui si paga solo compute e storage, e la maggiore densità dei broker permette di usare meno nodi EKS, con uno sforzo di gestione basso grazie a un operator semplice e a una documentazione lineare

---

## Slide 6
Titolo: Opzione D — NATS JetStream
Sottotitolo: Messaging leggero cloud-native, non Kafka
Diagramma: SQL Server -> Debezium Server -> [NATS JetStream, pod EKS] -> Flink (EKS) -> Aurora PostgreSQL

- NATS JetStream abbandona del tutto il protocollo Kafka a favore di un sistema pub/sub nativo cloud, distribuito come singolo binario Go e gestito tramite operator o Helm chart
- Il punto di forza più evidente è il footprint minimo, con nodi che richiedono meno di 100 MB di RAM, uno scaling orizzontale semplice e una replica basata su RAFT già integrata
- La retention configurabile per tempo o dimensione è perfetta per messaggi che, come i nostri, vivono sulla coda solo per pochi istanti, e l'operatività quotidiana resta estremamente semplice grazie all'osservabilità Prometheus nativa
- Il vero costo di questa opzione è che non parla il protocollo Kafka: bisognerebbe sostituire il sink di Debezium e la sorgente Flink con connettori nuovi
- L'ecosistema CDC intorno a NATS è ancora meno maturo, e spesso richiede un connettore custom o Debezium Server
- Economicamente è la soluzione più leggera della lista, ma l'effort di migrazione iniziale è alto, anche se poi la gestione a regime diventa molto semplice

---

## Slide 7
Titolo: Opzione E — RabbitMQ Cluster Operator (opzionale)
Sottotitolo: Message broker maturo, protocollo AMQP
Diagramma: SQL Server -> Debezium/Kafka Connect -> [RabbitMQ Cluster Operator, pod EKS] -> Flink (EKS) -> Aurora PostgreSQL

- RabbitMQ resta un broker maturo basato su AMQP, distribuibile su EKS tramite il Cluster Operator ufficiale, con il plugin Streams che introduce code append-only più vicine alla semantica Kafka
- È una scelta solida per messaggi transitori come i nostri, e la gestione tramite custom resource resta semplice; il plugin Streams in particolare offre una retention breve simile a quella di un topic Kafka
- Il limite principale è che, non essendo compatibile con il protocollo Kafka, richiederebbe comunque un refactoring di Debezium e dei connettori Flink
- Su volumi molto alti il throughput resta inferiore a quello di Kafka o Redpanda
- Il costo è basso e il footprint contenuto, ma va messo in conto uno sforzo medio per riscrivere i connettori durante la migrazione

---

## Slide 8
Titolo: Opzione F — Connessione diretta, nessuna coda in mezzo
Sottotitolo: Flink CDC Connector con Debezium embedded, senza broker
Diagramma: SQL Server (transaction log) -> Flink CDC Connector (Debezium embedded, dentro il job Flink su EKS) -> Aurora PostgreSQL

- L'idea più radicale è eliminare del tutto la coda: il Flink CDC Connector integra un motore Debezium direttamente all'interno del job Flink e legge il transaction log di SQL Server senza passare da nessun broker intermedio
- Il vantaggio più evidente è il costo, che diventa il più basso possibile perché non c'è alcuna infrastruttura di messaggistica da gestire o da pagare; l'architettura si riduce all'essenziale, con meno componenti da monitorare, meno hop di rete e una latenza end-to-end più bassa, senza duplicare lo storage degli eventi, il che è coerente con la vita brevissima dei messaggi CDC
- Il prezzo da pagare è che sorgente e job Flink restano completamente accoppiati: se Flink rallenta o va riavviato, la pressione ricade direttamente sul transaction log di SQL Server, senza alcun cuscinetto intermedio
- Non esiste inoltre un vero fan-out, quindi un solo consumer può leggere lo stream e non è possibile fare replay indipendente o servire più consumatori dallo stesso flusso
- La capacità di lettura scala solo insieme al parallelismo del job Flink e ai limiti di connessione della sorgente, e la visibilità sul lag della coda scompare del tutto: va ricavata indirettamente dalle metriche di checkpoint di Flink
- Va anche considerato che la fase di snapshot iniziale può generare un carico significativo sul database sorgente
- Questa opzione ha senso soprattutto per flussi non critici e a basso volume, dove il risparmio di costo giustifica il rischio di un accoppiamento così stretto

---

## Slide 9
Titolo: Opzione G — Amazon Kinesis Data Streams
Sottotitolo: Streaming AWS-native, alternativa gestita ma non Kafka
Diagramma: SQL Server -> Debezium (Kinesis sink) -> [Kinesis Data Streams] -> Flink (EKS) -> Aurora PostgreSQL

- Amazon Kinesis Data Streams e completamente gestito da AWS: nessun cluster da patchare, si paga solo per shard-hour e dati trasferiti
- Il connettore Kinesis di Flink e maturo e nativo, e la retention (fino a 365 giorni) puo essere impostata bassa per adattarsi a messaggi CDC di vita breve
- Puo costare meno di MSK a bassi volumi, perche non richiede broker dedicati ma solo shard proporzionati al throughput
- Non parla il protocollo Kafka: Debezium non scrive nativamente su Kinesis, serve un sink dedicato (Kafka Connect Kinesis o produttore custom)
- La capacita scala a shard: resharding e limiti di velocita richiedono pianificazione, e il fan-out avanzato per piu consumer ha un costo aggiuntivo
- Resta comunque un servizio AWS a consumo: utile se si vuole restare nell'ecosistema AWS, meno se l'obiettivo e uscire dai costi variabili cloud

---

## Slide 10
Titolo: Matrice di confronto
Sottotitolo: Sintesi qualitativa

- Guardando le sette opzioni fianco a fianco: MSK resta la baseline più costosa ma richiede pochissimo sforzo operativo, grazie alla piena compatibilità Kafka e al disaccoppiamento tra sorgente e sink
- Strimzi su EKS offre lo stesso protocollo Kafka a un costo medio-basso, con uno sforzo di gestione medio ma sempre con disaccoppiamento garantito
- Redpanda va oltre, con un costo basso e uno sforzo ancora più contenuto, mantenendo la compatibilità con l'API Kafka e il disaccoppiamento tra le due parti del flusso
- NATS JetStream porta il costo al minimo storico, ma abbandonando Kafka richiede uno sforzo di migrazione alto, pur conservando il disaccoppiamento
- RabbitMQ Operator si colloca in una via di mezzo, con costo basso ma sforzo medio, anche qui senza compatibilità Kafka ma con disaccoppiamento preservato
- Kinesis Data Streams offre un modello a consumo interamente gestito da AWS, con costo basso-medio e sforzo medio, ma senza compatibilità Kafka e con un sink dedicato da mantenere
- La connessione diretta, l'Opzione F, azzera il costo della coda ma lo fa rinunciando del tutto al disaccoppiamento tra sorgente e sink, e richiede il più alto sforzo di migrazione
- Nel complesso, il miglior compromesso tra valore e rischio per il Pilot resta Strimzi o Redpanda; la connessione diretta va considerata solo quando il rischio di accoppiamento è davvero accettabile

---

## Slide 11
Titolo: Raccomandazione
Sottotitolo: Percorso a due passi (più opzione radicale)

- Il percorso più sensato è procedere in due passi: prima un quick win, poi un'evoluzione più mirata
- Il primo passo è migrare da MSK a Strimzi su EKS, perché il protocollo resta lo stesso e non serve toccare Debezium o Flink: la riduzione dei costi arriva quasi subito, e lo sforzo del team infrastrutturale si concentra tutto nella fase di setup iniziale
- Il secondo passo, più a medio termine, è valutare Redpanda per densificare ulteriormente i broker: il client Kafka resta lo stesso, servono meno risorse e gli upgrade non sono più disruptivi
- NATS e RabbitMQ restano opzioni valide solo se in futuro decidessimo di uscire completamente dall'ecosistema Kafka, un cambiamento più radicale da valutare a parte
- Kinesis Data Streams e un'alternativa da considerare se si vuole restare nell'ecosistema AWS senza gestire cluster, accettando un modello a consumo e la necessita di un sink dedicato per Debezium
- La connessione diretta, l'Opzione F, va tenuta in considerazione solo per flussi non critici e a basso volume, dove il costo pari a zero della coda vale il rischio di un accoppiamento diretto con la sorgente
- Come prossimo passo concreto, proponiamo un PoC con Strimzi nel namespace del Pilot, un benchmark di throughput e latenza, e una stima puntuale dei costi EKS

---

## Slide 12
Titolo: Dubbi aperti e verifiche necessarie
Sottotitolo: Da confermare prima della decisione

- Prima di prendere una decisione definitiva restano alcuni punti da chiarire
- Serve capire i volumi reali di eventi CDC al secondo e la dimensione media dei messaggi, perché è da questi numeri che dipende il dimensionamento di qualunque soluzione
- Vanno definiti la retention richiesta e gli SLO di disponibilità attesi dal broker, così come i vincoli di sicurezza e compliance che si applicano a un broker gestito internamente, patching e audit inclusi
- È da verificare la compatibilità tra la versione di Debezium/Kafka Connect in uso e Redpanda, e va stimato il costo reale su EKS, considerando se i nodi saranno dedicati o condivisi, oltre allo storage EBS necessario
- Bisogna anche capire come si integrerà il nuovo broker con l'[[osservabilita-pilot-flink|osservabilità Splunk]] già in uso
- Per l'opzione a connessione diretta, infine, va valutata la reale tolleranza al rischio di un accoppiamento stretto tra sorgente e job, e la capacità del transaction log di SQL Server di assorbire eventuali rallentamenti
