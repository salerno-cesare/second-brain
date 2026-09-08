# Confrontare output legacy e target

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Reconciliation degli output
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Descrizione

La reconciliation confronta record, chiavi e campi critici tra output legacy e schema target e produce KPI di match/mismatch.

## User story

Come responsabile della validazione del Pilot, voglio confrontare output legacy e target, così da misurare l'allineamento dei dati e identificare i mismatch.

## Criteri di accettazione

- Dati output legacy e target disponibili, quando si esegue la reconciliation, allora vengono confrontati record e chiavi previsti.
- Il risultato espone KPI di match e mismatch.
- I mismatch sono evidenziati tramite metriche consultabili.

## Regole funzionali

- Il confronto può applicare tolleranze concordate ai campi non deterministici.
- La soglia di accettazione deve essere concordata prima della valutazione del gate dati.

## Dipendenze

- [[epica-reconciliation|Reconciliation degli output]].
- [[scrivere-output-schema-target|Scrivere l'output nello schema target]].

## Dubbi aperti

- Attore approvatore, chiavi, campi, tolleranze, soglia di match, formato e destinazione dei risultati non sono definiti.

## Fonti

- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
