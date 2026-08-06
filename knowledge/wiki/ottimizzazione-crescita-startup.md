# Ottimizzazione della crescita delle startup

## Sintesi

Il livello prescrittivo deve massimizzare la probabilità di alta crescita prevista da XGBoost, rispettando configurazioni fsQCA e vincoli di budget, capacità e profilo aziendale.

## Dettagli

### Formulazione concettuale

La forma proposta è `max f_XGB(x)` con `x` appartenente all'insieme ammissibile derivato da fsQCA e dai vincoli operativi. Le variabili modificabili rappresentano pratiche di innovazione e investimenti tecnologici; la dimensione aziendale resta fissata come profilo o scenario.

### Output atteso

Il modello dovrebbe restituire combinazioni strategiche compatibili con il profilo dell'impresa, non soltanto una graduatoria di importanza delle variabili.

## Collegamenti

- [[xgboost-crescita-startup|XGBoost per la crescita delle startup]]
- [[fsqca-crescita-startup|fsQCA per la crescita delle startup]]
- [[framework-analitico-crescita-startup|Framework analitico per la crescita delle startup]]

## Contraddizioni o dubbi

- Non sono definiti variabili decisionali, costi, budget, capacità, domini, vincoli logici o scenari numerici reali.
- Gli esempi numerici della chat sono dichiaratamente inventati e non costituiscono parametri utilizzabili.
- Va stabilito come rendere ottimizzabile una funzione XGBoost e come tradurre formalmente le configurazioni fsQCA.

## Fonti

- `.codex_sources/source-chat-martina-xgboost-pls-sem-f07ec89b70.txt`.
- `.codex_sources/source-revenue-growth-in-tourism-startup-b7c2e2ec01.txt`.
