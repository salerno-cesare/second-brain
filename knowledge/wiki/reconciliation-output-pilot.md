# Reconciliation degli output del Pilot

## Sintesi

- Confronta output legacy e output del nuovo flusso nello schema target.
- Misura corrispondenza di record, chiavi e campi critici e rende visibili i mismatch.
- È sviluppata e schedulata dal Team di Sviluppo, senza CronJob Kubernetes predisposto dall'Infra.

## Dettagli

### Funzione

La prima versione della reconciliation verifica l'allineamento tra lo schema legacy e lo schema target isolato. Il confronto deve produrre KPI di match/mismatch e supportare tolleranze concordate per eventuali campi non deterministici.

### Esecuzione

L'esecuzione è affidata allo scheduler previsto dal Team di Sviluppo. Il Team di Sviluppo gestisce logica, accessi già disponibili, output e KPI; il Team Infrastruttura interviene soltanto se connettività o policy impediscono allo scheduler autorizzato di operare.

### Uso nel Pilot

I risultati contribuiscono al gate dati della [[strategia-migrare-misurando|strategia "migrare misurando"]] e alla valutazione di fattibilità del [[pilot-apache-flink|Pilot Apache Flink]].

## Collegamenti

- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]
- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]]
- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]

## Contraddizioni o dubbi

- Non sono definiti record, chiavi e campi critici da confrontare.
- Non sono definite soglia di match, tolleranze, frequenza di esecuzione, formato dell'output o comportamento in caso di mismatch.
- Lo scheduler applicativo previsto non è identificato.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 5, 7 e 8; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `raw/Flink_Pilot_Infrastruttura.docx`, sezione 10 e tabelle relative alla reconciliation; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
