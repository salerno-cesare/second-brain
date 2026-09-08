# Log operativo Requisiti Funzionali

Questo log traccia le modifiche alla wiki parallela dei requisiti funzionali.

## 2026-09-08T12:26:47+02:00 - compilazione requisiti Pilot Apache Flink

- Modalità: `compile`.
- Progetto indicizzato: Legacy Data Bridge MVP 1 - Pilot Apache Flink.
- Epiche create: acquisizione CDC dedicata; elaborazione e persistenza; reconciliation; monitoraggio operativo.
- User story create: 8.
- Pagine aggiornate: [[_index|Indice Requisiti Funzionali]] e [[_log|Log operativo Requisiti Funzionali]].
- Dubbi aperti:
  - Non sono definite le tabelle CDC, le regole di mapping/normalizzazione, la semantica di upsert o deduplicazione e il comportamento puntuale sugli errori.
  - Non sono definite chiavi/campi di confronto, tolleranze, soglie o frequenza della reconciliation.
  - Non sono definite soglie, destinatari ed escalation degli alert.
