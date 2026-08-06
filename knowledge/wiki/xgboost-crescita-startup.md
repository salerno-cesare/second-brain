# XGBoost per la crescita delle startup

## Sintesi

Il modello principale proposto è una classificazione binaria che stima la probabilità di alta crescita, definita come `Q4_2 = 4`. La scala originaria resta disponibile per verifiche multiclasse o ordinali.

## Dettagli

### Target e campione

`HighGrowth = 1` se `Q4_2 = 4`, altrimenti `0`, escludendo o trattando esplicitamente i codici non validi. Nel dataset sono disponibili 301 startup con `Q4_2` da 1 a 4, di cui 81 nella classe alta crescita.

### Pipeline proposta

- validazione iniziale di codici, mancanti, distribuzioni e compositi;
- regressione logistica come baseline sugli stessi predittori;
- cross-validation stratificata;
- imputazione, selezione, bilanciamento e tuning eseguiti dentro i fold;
- tuning di profondità, numero di alberi, learning rate, campionamento e regolarizzazione;
- metriche ROC-AUC, precision, recall, F1, matrice di confusione, PR-AUC se necessario e calibrazione;
- interpretazione con importanza delle feature e SHAP.

### Robustezza

Confrontare la classificazione binaria con modelli multiclasse e ordinali, valutando la stabilità dei driver e delle conclusioni.

## Collegamenti

- [[dataset-za9016-startup|Dataset ZA9016 per l'analisi delle startup]]
- [[costrutti-crescita-startup|Costrutti per la crescita delle startup]]
- [[ottimizzazione-crescita-startup|Ottimizzazione della crescita delle startup]]

## Contraddizioni o dubbi

- Non sono ancora disponibili split, risultati di validazione, iperparametri selezionati o prestazioni.
- Con 21 startup turistiche non è supportato un XGBoost affidabile limitato a quel sottogruppo; l'eventuale analisi settoriale resta esplorativa.
- Il trattamento definitivo dei 10 codici `998` in `Q4_2` deve essere documentato.

## Fonti

- `.codex_sources/source-chat-martina-xgboost-pls-sem-f07ec89b70.txt`.
- `.codex_sources/source-za9016-v1-0-0-final-638abfdbcd.txt`.
- `.codex_sources/source-revenue-growth-in-tourism-startup-b7c2e2ec01.txt`.

