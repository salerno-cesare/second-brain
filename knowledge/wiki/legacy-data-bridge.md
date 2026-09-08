# Legacy Data Bridge

## Sintesi

- Applicazione dedicata all'integrazione dei dati dei sistemi legacy in modalità batch e near-real time.
- Evoluzione del precedente Normalizzatore basata su Apache Flink.
- Consente di esporre dati legacy in forma moderna e a eventi senza interventi invasivi sulle sorgenti.

## Dettagli

### Scopo

Legacy Data Bridge acquisisce dati dai sistemi legacy, trasforma, arricchisce e normalizza i tracciati. L'obiettivo dichiarato è rendere integrabili le applicazioni esistenti mediante una pipeline più strutturata e scalabile.

### Modalità di elaborazione

La soluzione deve supportare sia carichi batch sia flussi near-real time. Apache Flink è il motore previsto per unificare i due modelli di elaborazione.

### Percorso di adozione

Il primo incremento è il [[pilot-apache-flink|Pilot Apache Flink]], che migra un solo flusso del Normalizzatore e produce un template standard riutilizzabile. L'estensione a tutti i flussi, denominata fase Scale, è subordinata all'esito del Pilot e non è inclusa nel suo perimetro economico.

## Collegamenti

- [[pilot-apache-flink|Legacy Data Bridge MVP 1 - Pilot Apache Flink]]
- [[strategia-migrare-misurando|Strategia "migrare misurando"]]
- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Contraddizioni o dubbi

- Non è documentato quali applicazioni legacy, oltre al flusso pilota del Normalizzatore, rientreranno in un'eventuale fase Scale.
- Non è identificato il flusso del Normalizzatore selezionato per il Pilot.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 2, 5-9; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
