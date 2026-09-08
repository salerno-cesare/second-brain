# Acquisizione CDC dedicata

## Metadati Requisiti

- Tipo requisito: Epica
- Epica: Acquisizione CDC dedicata
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Sintesi

Il Pilot deve acquisire in modo indipendente snapshot e variazioni CDC dal Microsoft SQL Server, mantenendo separata la pipeline legacy.

## User story

- [[acquisire-variazioni-sql-server|Acquisire le variazioni da SQL Server]].

## Regole funzionali

- Il connector è dedicato al Pilot.
- Gli eventi acquisiti sono prodotti sui topic del Pilot in AWS MSK.

## Dubbi aperti

- Tabelle CDC, modalità di snapshot, retry, naming dei topic e comportamento sugli errori non sono definiti.

## Fonti

- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]].
- [[strategia-migrare-misurando|Strategia "migrare misurando"]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
