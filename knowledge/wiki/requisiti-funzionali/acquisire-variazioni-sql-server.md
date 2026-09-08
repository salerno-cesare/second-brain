# Acquisire le variazioni da SQL Server

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Acquisizione CDC dedicata
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Descrizione

Un connector Debezium/Kafka Connect dedicato acquisisce snapshot e variazioni CDC dal SQL Server sorgente e produce gli eventi sui topic del Pilot.

## User story

Come componente di acquisizione del Pilot, voglio acquisire le variazioni dal Microsoft SQL Server e pubblicarle su AWS MSK, così da alimentare il nuovo flusso indipendentemente dal legacy.

## Criteri di accettazione

- Dato il CDC attivo sulle tabelle incluse nel Pilot, quando si verifica una variazione, allora il connector dedicato può acquisirla e produrla sui topic del Pilot.
- Il flusso di acquisizione del Pilot non usa il connector del flusso legacy.
- Stato, lag, errori e avanzamento dello snapshot del connector sono disponibili al monitoraggio.

## Regole funzionali

- Il connector usa i prerequisiti CDC di SQL Server; non usa publication, replication slot o WAL PostgreSQL.
- Configurazione di snapshot, CDC, retry, error handling e naming è gestita dal Team di Sviluppo via IaC.

## Dipendenze

- [[epica-acquisizione-cdc|Acquisizione CDC dedicata]].
- SQL Server con CDC, Debezium/Kafka Connect e AWS MSK.

## Dubbi aperti

- Tabelle, modalità snapshot, retry, naming dei topic e trattamento puntuale degli errori non sono documentati.

## Fonti

- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]].
- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]].
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
