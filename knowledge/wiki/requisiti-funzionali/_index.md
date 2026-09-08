# Indice Requisiti Funzionali

Questa wiki parallela indicizza solo requisiti software funzionali, ordinati per progetto, epiche e user story.

## Progetto: Legacy Data Bridge MVP 1 - Pilot Apache Flink

### [[epica-acquisizione-cdc|Acquisizione CDC dedicata]]

- [[acquisire-variazioni-sql-server|Acquisire le variazioni da SQL Server]].

### [[epica-elaborazione-persistenza|Elaborazione e persistenza del flusso]]

- [[elaborare-normalizzare-eventi|Elaborare e normalizzare gli eventi con Flink]].
- [[scrivere-output-schema-target|Scrivere l'output nello schema target]].
- [[gestire-errori-duplicati|Gestire errori, idempotenza e duplicati]].

### [[epica-reconciliation|Reconciliation degli output]]

- [[confrontare-output-legacy-target|Confrontare output legacy e target]].
- [[pianificare-reconciliation|Pianificare l'esecuzione della reconciliation]].

### [[epica-monitoraggio-operativo|Monitoraggio operativo]]

- [[raccogliere-log-metriche-splunk|Raccogliere log e metriche in Splunk]].
- [[generare-alert-operativi|Generare alert operativi]].
