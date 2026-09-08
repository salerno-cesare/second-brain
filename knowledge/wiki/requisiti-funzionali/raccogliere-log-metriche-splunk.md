# Raccogliere log e metriche in Splunk

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Monitoraggio operativo
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]

## Descrizione

Splunk deve rendere consultabili log stdout/stderr, metriche Flink e segnali operativi dei componenti del Pilot.

## User story

Come operatore del Pilot, voglio consultare in Splunk log e metriche del flusso, così da monitorarne lo stato e investigare gli incidenti.

## Criteri di accettazione

- I log stdout/stderr dei Pod Flink e dei componenti runtime sono acquisiti in Splunk.
- Sono consultabili almeno stato e restart del job, record in/out, throughput, latenza, backpressure e checkpoint.
- Sono disponibili i segnali previsti per connector, MSK, SQL Server, Aurora PostgreSQL e Kubernetes.

## Regole funzionali

- Si usa l'integrazione Splunk aziendale esistente.
- Retention e access control seguono le policy Splunk esistenti.

## Dipendenze

- [[epica-monitoraggio-operativo|Monitoraggio operativo]].
- [[generare-alert-operativi|Generare alert operativi]].

## Dubbi aperti

- Dashboard, meccanismo di raccolta, retention e autorizzazioni specifiche non sono documentati.

## Fonti

- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]].
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
