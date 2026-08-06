# Framework analitico per la crescita delle startup

## Sintesi

- Il framework integra spiegazione con PLS-SEM, analisi configurazionale con fsQCA, previsione con XGBoost e prescrizione con ottimizzazione.
- L'esito studiato è la crescita del fatturato, misurata da `Q4_2`.
- L'ambito empirico confermato è l'insieme delle startup del dataset, non un campione composto interamente da startup turistiche.

## Dettagli

### Sequenza metodologica proposta

1. PLS-SEM valida i costrutti e stima le relazioni strutturali medie.
2. fsQCA cerca configurazioni alternative associate ad alta crescita.
3. XGBoost stima la probabilità individuale di alta crescita e rileva non linearità e interazioni.
4. Il modello di Operations Research usa la previsione come funzione obiettivo e le configurazioni fsQCA come scenari o vincoli di ammissibilità.

### Contributo atteso

Il framework estende il revenue management dalla gestione operativa di prezzi e capacità all'allocazione strategica di risorse per innovazione e tecnologia. Le quattro tecniche hanno ruoli complementari e non intercambiabili.

### Stato

Le fonti descrivono un impianto metodologico e una bozza di articolo. Non riportano risultati convalidati di PLS-SEM, fsQCA, XGBoost o ottimizzazione.

## Collegamenti

- [[dataset-za9016-startup|Dataset ZA9016 per l'analisi delle startup]]
- [[costrutti-crescita-startup|Costrutti per la crescita delle startup]]
- [[pls-sem-crescita-startup|PLS-SEM per la crescita delle startup]]
- [[fsqca-crescita-startup|fsQCA per la crescita delle startup]]
- [[xgboost-crescita-startup|XGBoost per la crescita delle startup]]
- [[ottimizzazione-crescita-startup|Ottimizzazione della crescita delle startup]]

## Contraddizioni o dubbi

- La bozza dell'articolo dichiara 311 startup turistiche; il dataset e la chat confermano invece 311 startup totali, di cui 21 con `d1b = 14`. L'ambito settoriale del paper deve essere corretto o giustificato.
- La bozza cita CB-SEM nel background metodologico e PLS-SEM nel framework. La tecnica SEM definitiva deve essere formalizzata.
- Budget, capacità e leve decisionali sono citati, ma non sono ancora operazionalizzati nel dataset.

## Fonti

- `.codex_sources/source-revenue-growth-in-tourism-startup-b7c2e2ec01.txt` (origine: `raw/Revenue_Growth_in_Tourism_Startup.pdf`).
- `.codex_sources/source-chat-martina-xgboost-pls-sem-f07ec89b70.txt` (origine: `raw/chat_martina_xgboost_pls_sem.pdf`).
- `.codex_sources/source-conceptual-model-data-carlo-1-f2ecf19d79.txt` (origine: `raw/Conceptual Model_Data_Carlo (1).pptx`).

