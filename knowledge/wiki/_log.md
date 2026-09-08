# Log operativo
## 2026-09-07T15:26:18+02:00 - configurazione lingua

- Pagine create:
  - [[_config|Configurazione Wiki]]
- Pagine aggiornate:
  - [[_log|Log operativo]]
- Lingua wiki bloccata: Italian (`it`).
- Dubbi aperti:
  - Nessuno.

## 2026-09-08T12:26:47+02:00 - compilazione fonti Pilot Apache Flink

- Modalità: `compile`.
- Fonti considerate:
  - `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt` (origine: `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`).
  - `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt` (origine: `raw/Flink_Pilot_Infrastruttura.docx`).
- Pagine create:
  - [[legacy-data-bridge|Legacy Data Bridge]].
  - [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]].
  - [[strategia-migrare-misurando|Strategia "migrare misurando"]].
  - [[architettura-pilot-flink|Architettura del Pilot Apache Flink]].
  - [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]].
  - [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]].
  - [[reconciliation-output-pilot|Reconciliation degli output del Pilot]].
  - [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]].
- Pagine aggiornate:
  - [[_index|Indice Wiki]].
  - [[_log|Log operativo]].
  - Vista [[requisiti-funzionali/_index|Requisiti funzionali]] e relativo log.
- Pagine unite o divise: nessuna; la wiki non conteneva ancora pagine di dominio.
- Dubbi aperti:
  - Da chiarire se la valutazione di una tecnologia alternativa a Kafka sia ancora nel perimetro, dato che le istruzioni infrastrutturali assumono il riuso di AWS MSK.
  - Da formalizzare criteri, soglie e periodo di osservazione per i gate tecnico, dati e operativo.
  - Da confermare versione Flink/Operator, sizing effettivo, tabelle CDC, autenticazione MSK, endpoint/NetworkPolicy e meccanismo di integrazione Splunk.
  - Non è identificato nelle fonti il flusso specifico del Normalizzatore scelto per il Pilot.

