# Responsabilità del Pilot Apache Flink

## Sintesi

- Il Team Infrastruttura abilita piattaforma, runtime e prerequisiti.
- Il Team di Sviluppo gestisce come codice le risorse applicative tramite Terraform, Liquibase e pipeline.
- Ogni deviazione dal confine deve essere concordata esplicitamente prima dell'esecuzione.

## Dettagli

### Team Infrastruttura

È responsabile di namespace, RBAC, NetworkPolicy, predisposizione del runtime Flink e Operator, prerequisiti CDC SQL Server, flussi di rete e autenticazione, integrazione Splunk, smoke test infrastrutturali e supporto al troubleshooting. Valuta inoltre la ResourceQuota senza assumere come vincolante il sizing proposto.

### Team di Sviluppo

Gestisce via Terraform la definizione di Debezium/Kafka Connect e lo storage di stato Flink; tramite Liquibase crea e versiona schema, tabelle, indici e constraint su Aurora PostgreSQL. Gestisce inoltre job e immagini Flink, configurazioni applicative, snapshot/CDC/retry/error handling/naming, reconciliation e relativo scheduler.

### Attività senza effort infrastrutturale manuale

Non sono richiesti provisioning manuali Infra per storage Flink, connector, topic MSK, schema e tabelle target, grant Aurora, reconciliation o relativo scheduling. L'Infra interviene solo in presenza di vincoli di piattaforma, rete, sicurezza o policy.

## Collegamenti

- [[infrastruttura-pilot-flink|Infrastruttura del Pilot Apache Flink]]
- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]
- [[reconciliation-output-pilot|Reconciliation degli output del Pilot]]

## Contraddizioni o dubbi

- Il confine è esplicito, ma non è riportata una matrice RACI nominativa né sono identificati approvatori e owner delle singole attività.
- Non è indicato chi formalizza l'accettazione dei gate del Pilot.

## Fonti

- `raw/Flink_Pilot_Infrastruttura.docx`, sezioni 1-17 e tabelle di responsabilità; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
