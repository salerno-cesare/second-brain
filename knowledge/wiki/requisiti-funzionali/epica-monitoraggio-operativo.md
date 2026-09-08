# Monitoraggio operativo

## Metadati Requisiti

- Tipo requisito: Epica
- Epica: Monitoraggio operativo
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]

## Sintesi

Il Pilot deve rendere consultabili in Splunk log, metriche e segnali operativi e generare alert sulle anomalie minime indicate dalle fonti.

## User story

- [[raccogliere-log-metriche-splunk|Raccogliere log e metriche in Splunk]].
- [[generare-alert-operativi|Generare alert operativi]].

## Regole funzionali

- Splunk è lo stack da utilizzare.
- Non è previsto un nuovo stack Prometheus/Grafana/Loki salvo decisione separata.

## Dubbi aperti

- Dashboard, soglie, destinatari, escalation e retention specifica non sono definiti.

## Fonti

- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
