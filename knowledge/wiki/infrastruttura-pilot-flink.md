# Infrastruttura del Pilot Apache Flink

## Sintesi

- Predispone un ambiente Kubernetes isolato e introduce da zero il runtime Flink.
- Abilita connettività, sicurezza, integrazione Splunk e prerequisiti CDC senza duplicare il provisioning applicativo gestito come codice.
- Conclude con smoke test end-to-end e handover operativo.

## Dettagli

### Sequenza raccomandata

1. Confermare namespace, connettività, DNS/TLS, registry, secret management e integrazione Splunk.
2. Configurare namespace, ServiceAccount/RBAC e NetworkPolicy.
3. Valutare una ResourceQuota rispetto alla capacità reale del cluster.
4. Selezionare e installare versioni compatibili di Apache Flink e Flink Kubernetes Operator.
5. Predisporre i prerequisiti CDC sul SQL Server sorgente.
6. Verificare i flussi Debezium/Kafka Connect verso SQL Server e AWS MSK.
7. Verificare i flussi Flink verso MSK, Aurora PostgreSQL, storage di stato e Splunk.
8. Integrare log e metriche con Splunk, eseguire smoke test e handover.

### Kubernetes e sizing

Il Team di Sviluppo deve poter operare solo nel namespace autorizzato, senza privilegi cluster-admin. La baseline suggerita, da validare, prevede un JobManager con una replica da 2 vCPU e 4 GB RAM e due TaskManager da 4 vCPU e 8 GB RAM ciascuno. La ResourceQuota complessiva indicativa è 14-16 vCPU e 28-36 GB RAM, ma non costituisce un vincolo.

### Sicurezza e connettività

Si applicano least privilege, autenticazione MSK esistente e gestione aziendale di secret e certificati. Le NetworkPolicy devono consentire solo i flussi necessari verso SQL Server, MSK, Aurora, storage, Splunk e registry. Il documento non impone porte specifiche.

### Verifiche e handover

Gli esiti attesi includono disponibilità dell'Operator e delle CRD, salute dei Pod, connettività end-to-end, accessibilità dello storage di stato e consultabilità in Splunk di log, metriche e alert essenziali.

## Collegamenti

- [[architettura-pilot-flink|Architettura del Pilot Apache Flink]]
- [[responsabilita-pilot-flink|Responsabilità del Pilot Apache Flink]]
- [[osservabilita-pilot-flink|Osservabilità del Pilot Apache Flink]]

## Contraddizioni o dubbi

- La baseline di sizing deve essere validata su eventi al secondo, dimensione degli eventi e parallelismo.
- Sono da confermare versioni Flink/Operator, tabelle CDC, endpoint, autenticazione MSK e integrazione Splunk.
- Non è specificato il periodo di stabilità richiesto prima dell'handover.

## Fonti

- `raw/Flink_Pilot_Infrastruttura.docx`, versione 1.1 dell'8 settembre 2026, sezioni 1-17; testo estratto in `.codex_sources/source-flink-pilot-infrastruttura-28d3b7a043.txt`.
