# Scrivere l'output nello schema target

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Elaborazione e persistenza del flusso
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Descrizione

Il job Flink scrive via JDBC/upsert nel database Aurora PostgreSQL esistente, usando uno schema target separato dal legacy.

## User story

Come Legacy Data Bridge, voglio persistere l'output elaborato in uno schema target separato, così da evitare contaminazioni del legacy e rendere confrontabili i risultati.

## Criteri di accettazione

- Dato un record elaborato dal job Flink, quando viene persistito, allora è scritto nelle strutture dello schema target.
- Nessun output del Pilot è scritto nello schema legacy.
- Lo schema e le strutture target sono versionati e creati tramite Liquibase.

## Regole funzionali

- Il target è il database Amazon Aurora PostgreSQL esistente.
- Il Team di Sviluppo usa permessi già disponibili; le fonti non richiedono nuove grant.

## Dipendenze

- [[epica-elaborazione-persistenza|Elaborazione e persistenza del flusso]].
- [[elaborare-normalizzare-eventi|Elaborare e normalizzare gli eventi con Flink]].
- [[confrontare-output-legacy-target|Confrontare output legacy e target]].

## Dubbi aperti

- Schema logico, tabelle, indici, constraint e semantica dell'upsert non sono documentati.

## Fonti

- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]].
- [[strategia-migrare-misurando|Strategia "migrare misurando"]].
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
