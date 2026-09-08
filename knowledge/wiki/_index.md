# Indice Wiki

Knowledge base del progetto Legacy Data Bridge MVP 1, compilata dalle fonti di offerta e dalle istruzioni operative infrastrutturali.

## Progetto e obiettivi

- [[legacy-data-bridge|Legacy Data Bridge]] — applicazione di integrazione per dati legacy in modalità batch e near-real time.
- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]] — perimetro, deliverable, pianificazione e criteri di successo del pilot.
- [[strategia-migrare-misurando|Strategia "migrare misurando"]] — affiancamento controllato del nuovo flusso al Normalizzatore legacy.

## Architettura e piattaforma

- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]] — flusso SQL Server, Debezium/Kafka Connect, AWS MSK, Flink e Aurora PostgreSQL.
- [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]] — predisposizione Kubernetes, runtime Flink, connettività, sicurezza e handover.

## Esercizio, qualità e responsabilità

- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]] — confine operativo tra Team Infrastruttura e Team di Sviluppo.
- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]] — confronto tra output legacy e schema target.
- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]] — log, metriche e alert in Splunk.

## Viste derivate

- [[requisiti-funzionali/_index|Requisiti funzionali]] — indice progetto, epiche e user story tracciabili alle fonti.
