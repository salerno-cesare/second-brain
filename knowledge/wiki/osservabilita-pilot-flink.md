# Osservabilità del Pilot Apache Flink

## Sintesi

- Splunk è lo stack aziendale obbligatorio per monitoring e logging del Pilot.
- Centralizza log, metriche tecniche, KPI e segnali necessari al troubleshooting.
- Il Pilot non introduce Prometheus, Grafana o Loki salvo decisione separata.

## Dettagli

### Log e metriche

Splunk deve acquisire stdout/stderr dei Pod Flink e dei componenti runtime. I controlli minimi coprono:

- Flink: stato job, restart, record in/out, throughput, latenza, backpressure, checkpoint, CPU, RAM e JVM;
- Debezium/Kafka Connect: stato connector/task, source lag, errori, avanzamento snapshot e record emessi;
- AWS MSK: consumer lag, throughput ed errori producer/consumer;
- SQL Server: stato CDC, transaction log/CDC jobs, connessioni ed errori rilevanti;
- Aurora PostgreSQL: connessioni ed errori applicativi disponibili;
- Kubernetes: restart, OOMKilled, CPU/memoria e scheduling failure.

### Alert

Gli alert minimi riguardano job Flink non operativo o in restart loop, checkpoint falliti, consumer lag elevato, connector CDC in errore e anomalie Kubernetes.

### Governo dei dati operativi

Retention e controllo accessi seguono le policy Splunk esistenti. Il meccanismo tecnico di raccolta deve riusare l'integrazione standard già adottata nel cluster.

## Collegamenti

- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]]
- [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]]
- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Contraddizioni o dubbi

- Non sono definite soglie di alert, dashboard, destinatari, escalation o retention specifica.
- Il collector/forwarder o altro meccanismo standard di integrazione Splunk non è identificato.
- I KPI minimi dell'offerta non sono formalizzati oltre alle metriche elencate nelle istruzioni infrastrutturali.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 7 e 8; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `raw/Flink_Pilot_Infrastruttura.docx`, sezioni 1, 4, 11, 15-17 e tabelle KPI; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
