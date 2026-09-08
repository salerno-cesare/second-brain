# Strategia "migrare misurando"

## Sintesi

- Il nuovo flusso affianca il Normalizzatore legacy senza sostituirlo immediatamente.
- Input e output sono isolati per permettere confronti controllati.
- La decisione di estendere la migrazione dipende da misure di performance, qualità dati e operabilità.

## Dettagli

### Separazione dell'input

Il Pilot usa un connector Debezium duplicato e indipendente da quello esistente. Il nuovo flusso legge la stessa sorgente tramite CDC, ma opera su una pipeline separata.

### Separazione dell'output

Il job Flink scrive in uno schema target distinto sul database Aurora PostgreSQL esistente. La separazione evita contaminazioni dell'output legacy e abilita il confronto diretto.

### Misurazione

Il confronto copre:

- performance: latenza, throughput, tasso di errore e risorse;
- allineamento dati: corrispondenza di record, chiavi e campi critici tra output legacy e target.

Le misure alimentano i gate del [[pilot-apache-flink|Pilot]] e la decisione sull'eventuale fase Scale.

## Collegamenti

- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]
- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]
- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Contraddizioni o dubbi

- Non sono definite le soglie che rendono accettabili differenze di performance o mismatch dati.
- Non sono elencati i campi critici né le tolleranze per valori non deterministici.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 5 e 8; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
