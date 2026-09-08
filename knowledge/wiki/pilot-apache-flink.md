# Legacy Data Bridge MVP 1 - Pilot Apache Flink

## Sintesi

- Migra in modo controllato un flusso del Normalizzatore verso Legacy Data Bridge.
- Verifica la fattibilità tecnica e operativa e produce un primo template standard riutilizzabile.
- Prevede un nuovo connector Debezium, un job Flink e uno schema target separato.

## Dettagli

### Perimetro

Il Pilot implementa un flusso Flink con gestione errori standard, idempotenza/deduplicazione e configurazioni replicabili. Include struttura di progetto e librerie condivisibili, per esempio moduli comuni di mapping e serializzazione.

Sul fronte dati include un connector Debezium indipendente dal legacy, uno schema target con relative strutture di output, monitoring con KPI minimi e una prima versione della [[reconciliation-output-pilot|reconciliation]].

### Pianificazione e costo

L'offerta stima una durata di circa 12 settimane. Nell'ipotesi di avvio nella settimana del 24 agosto 2026, indica il completamento entro il 13 novembre 2026; la pianificazione di dettaglio deve essere formalizzata nelle prime due settimane. Il valore economico indicato è 29.320,00 euro più IVA.

### Criteri di successo

I criteri devono essere definiti congiuntamente nella prima settimana. Le categorie proposte sono:

- gate tecnico: stabilità per un periodo definito e performance almeno comparabile al legacy, oppure delta spiegato e mitigato;
- gate dati: allineamento degli output entro una soglia concordata e metriche dei mismatch;
- gate operativo: runbook minimo per deploy, monitoraggio, incident investigation e riprocessamento, con procedure di arresto e riavvio senza impatto sul legacy.

### Evoluzione

La fase Scale potrà estendere l'approccio a tutti i flussi del Normalizzatore solo dopo conferma di fattibilità e valore. È esclusa dal Pilot e richiede un'offerta separata.

## Collegamenti

- [[legacy-data-bridge|Legacy Data Bridge]]
- [[strategia-migrare-misurando|Strategia "migrare misurando"]]
- [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]]
- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]

## Contraddizioni o dubbi

- Soglie quantitative, tolleranze e durata del periodo di stabilità non sono ancora definite.
- La pianificazione puntuale e il flusso del Normalizzatore da migrare non sono documentati.
- Non è documentato l'esito dell'ipotesi di avvio nella settimana del 24 agosto 2026.

## Fonti

- `raw/2026-OFF-54531_02 - Mediaset System Integration Standard - Pilot on Flink.pptx`, slide 5-9; testo estratto in `.codex_sources/source-2026-off-54531-02-mediaset-system-integration-standard-pilot-on-flink-d076b7b1d4.txt`.
- `raw/Flink_Pilot_Infrastruttura.docx`, versione 1.1 dell'8 settembre 2026; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
