# Architettura del Pilot Apache Flink

## Sintesi

- Flusso di riferimento: Microsoft SQL Server → Debezium/Kafka Connect → AWS MSK → Apache Flink su Kubernetes → Amazon Aurora PostgreSQL.
- Riusa sorgente, cluster MSK, cluster Kubernetes e database target esistenti; introduce Apache Flink ex novo.
- Mantiene separati connector, consumer group e schema target del Pilot rispetto al legacy.

## Dettagli

### Flusso dati

Debezium/Kafka Connect acquisisce snapshot e variazioni CDC dal Microsoft SQL Server e produce eventi sui topic del Pilot in AWS MSK. Il job Apache Flink consuma tramite un consumer group dedicato, elabora i dati e scrive via JDBC/upsert nello schema target di Aurora PostgreSQL.

### Componenti riutilizzati

- cluster Kubernetes;
- database sorgente Microsoft SQL Server;
- cluster Kafka AWS MSK;
- database target Amazon Aurora PostgreSQL;
- piattaforma Splunk per monitoring e logging.

### Componenti nuovi o dedicati

- runtime Apache Flink e Flink Kubernetes Operator;
- namespace Kubernetes del Pilot;
- connector Debezium/Kafka Connect dedicato;
- job Flink;
- topic e consumer group del Pilot;
- storage persistente esterno per checkpoint e savepoint, creato via Terraform;
- schema e strutture target, versionati e creati via Liquibase.

### Continuità e isolamento

Checkpoint e savepoint devono essere accessibili al runtime con identità definite via IaC. Il Pilot non usa filesystem effimeri dei Pod per lo stato. Il flusso nuovo resta isolato dal legacy secondo la [[strategia-migrare-misurando|strategia "migrare misurando"]].

## Collegamenti

- [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]]
- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]]
- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]
- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Contraddizioni o dubbi

- L'offerta indica che l'identificazione di una tecnologia alternativa a Kafka è in ambito al Pilot; il documento infrastrutturale successivo assume invece il riuso di AWS MSK. Occorre confermare se la valutazione resta aperta o se AWS MSK è la decisione corrente.
- Versioni di Apache Flink e Flink Kubernetes Operator, endpoint, regole di rete e metodo di autenticazione MSK sono da confermare.
- Non sono documentati naming dei topic, mapping dei dati, schema logico target e semantica dell'upsert.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 4-7; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `raw/Flink_Pilot_Infrastruttura.docx`, sezioni 1, 4-14 e 17; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
