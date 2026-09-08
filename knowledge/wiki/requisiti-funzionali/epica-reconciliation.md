# Reconciliation degli output

## Metadati Requisiti

- Tipo requisito: Epica
- Epica: Reconciliation degli output
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Sintesi

La soluzione deve confrontare output legacy e target, calcolare KPI di allineamento e rendere visibili i mismatch.

## User story

- [[confrontare-output-legacy-target|Confrontare output legacy e target]].
- [[pianificare-reconciliation|Pianificare l'esecuzione della reconciliation]].

## Regole funzionali

- L'esecuzione usa lo scheduler del Team di Sviluppo, non un CronJob Kubernetes predisposto dall'Infra.
- Logica, output e KPI sono gestiti dal Team di Sviluppo.

## Dubbi aperti

- Chiavi, campi critici, tolleranze, soglie, frequenza e gestione dei mismatch non sono definiti.

## Fonti

- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]].
- `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
