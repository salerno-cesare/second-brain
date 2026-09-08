# Pianificare l'esecuzione della reconciliation

## Metadati Requisiti

- Tipo requisito: User story
- Epica: Reconciliation degli output
- Priorità: Non indicata
- Stato: Parziale
- Fase: MVP 1 (Pilot)
- Fonte wiki: [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Descrizione

La reconciliation deve essere eseguita dallo scheduler previsto dal Team di Sviluppo.

## User story

Come Team di Sviluppo, voglio pianificare l'esecuzione della reconciliation, così da produrre con regolarità i KPI di allineamento tra legacy e target.

## Criteri di accettazione

- L'esecuzione può essere avviata dallo scheduler autorizzato del Team di Sviluppo.
- Non è necessario predisporre un Job o CronJob Kubernetes a carico del Team Infrastruttura.
- L'esecuzione usa gli accessi già disponibili e produce output e KPI di confronto.

## Regole funzionali

- Logica e scheduling sono responsabilità del Team di Sviluppo.
- L'Infra interviene solo se connettività o policy bloccano lo scheduler autorizzato.

## Dipendenze

- [[epica-reconciliation|Reconciliation degli output]].
- [[confrontare-output-legacy-target|Confrontare output legacy e target]].

## Dubbi aperti

- Scheduler, frequenza, finestre temporali e modalità di recupero dopo un'esecuzione fallita non sono documentati.

## Fonti

- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]].
- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]].
- `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
