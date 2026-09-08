# Elaborazione e persistenza del flusso

## Metadati Requisiti

- Tipo requisito: Epica
- Epica: Elaborazione e persistenza del flusso
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[legacy-data-bridge|Legacy Data Bridge]]

## Sintesi

Il job Flink deve consumare gli eventi del Pilot, trasformare e normalizzare i dati e persisterli nello schema target separato.

## User story

- [[elaborare-normalizzare-eventi|Elaborare e normalizzare gli eventi con Flink]].
- [[scrivere-output-schema-target|Scrivere l'output nello schema target]].
- [[gestire-errori-duplicati|Gestire errori, idempotenza e duplicati]].

## Regole funzionali

- La configurazione deve essere replicabile.
- Struttura di progetto e librerie comuni devono poter essere riutilizzate.

## Dubbi aperti

- Mapping, serializzazione, regole di arricchimento, schema target e semantica dell'upsert non sono documentati.

## Fonti

- [[legacy-data-bridge|Legacy Data Bridge]].
- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
