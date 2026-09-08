# Gestire errori, idempotenza e duplicati

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Elaborazione e persistenza del flusso
- Priorità: Non indicata
- Stato: Da verificare
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]]

## Descrizione

Il flusso pilota deve includere gestione errori standard e meccanismi di idempotenza/deduplicazione.

## User story

Come Legacy Data Bridge, voglio gestire errori e record duplicati in modo idempotente, così da mantenere affidabile l'output del flusso pilota.

## Criteri di accettazione

- La gestione errori è presente nel flusso implementato.
- L'elaborazione include un meccanismo di idempotenza o deduplicazione.
- Gli errori del job sono disponibili al monitoraggio del Pilot.

## Regole funzionali

- Il comportamento deve essere parte del template standard riutilizzabile.
- Le regole concrete non possono essere determinate dalle fonti disponibili.

## Dipendenze

- [[epica-elaborazione-persistenza|Elaborazione e persistenza del flusso]].
- [[raccogliere-log-metriche-splunk|Raccogliere log e metriche in Splunk]].

## Dubbi aperti

- Non sono definiti chiave di deduplicazione, finestra temporale, semantica exactly-once/at-least-once, retry, dead-letter handling o riprocessamento.

## Fonti

- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
