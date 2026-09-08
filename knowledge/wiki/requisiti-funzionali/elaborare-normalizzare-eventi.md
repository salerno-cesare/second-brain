# Elaborare e normalizzare gli eventi con Flink

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Elaborazione e persistenza del flusso
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[legacy-data-bridge|Legacy Data Bridge]]

## Descrizione

Il job Flink consuma gli eventi del Pilot da AWS MSK e applica trasformazione, arricchimento e normalizzazione dei tracciati.

## User story

Come Legacy Data Bridge, voglio elaborare e normalizzare gli eventi acquisiti dai sistemi legacy, così da esporre dati in una forma moderna e integrabile.

## Criteri di accettazione

- Dati gli eventi disponibili sui topic del Pilot, quando il job Flink è operativo, allora li consuma tramite il consumer group dedicato.
- Il flusso implementa trasformazione e normalizzazione previste per il flusso del Normalizzatore selezionato.
- Record in/out, throughput, latenza, backpressure ed errori risultano misurabili.

## Regole funzionali

- Il progetto deve prevedere configurazioni replicabili e librerie condivisibili per mapping e serializzazione.
- Il Pilot copre un solo flusso del Normalizzatore.

## Dipendenze

- [[epica-elaborazione-persistenza|Elaborazione e persistenza del flusso]].
- [[acquisire-variazioni-sql-server|Acquisire le variazioni da SQL Server]].

## Dubbi aperti

- Flusso selezionato, mapping, serializzazione, arricchimenti e regole di normalizzazione non sono documentati.

## Fonti

- [[legacy-data-bridge|Legacy Data Bridge]].
- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
