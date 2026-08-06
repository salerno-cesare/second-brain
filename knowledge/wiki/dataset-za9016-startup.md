# Dataset ZA9016 per l'analisi delle startup

## Sintesi

- Il foglio `Foglio1` contiene 17.791 record e 327 colonne.
- La variabile `Startups` identifica 311 startup con valore `1`.
- Tra queste, 21 hanno `d1b = 14`; pertanto il campione non è composto da 311 startup turistiche.
- `Q4_2` è utilizzabile per 301 startup; 10 record startup hanno codice `998`.

## Dettagli

### Perimetro verificato

I conteggi sono stati ricavati direttamente dal testo estratto del file ZA9016 durante la compilazione:

- record complessivi: 17.791;
- startup (`Startups = 1`): 311;
- record complessivi con `d1b = 14`: 1.266;
- startup con `d1b = 14`: 21.

### Distribuzione di `Q4_2` nelle startup

| Codice | Conteggio |
|---|---:|
| 1 | 45 |
| 2 | 77 |
| 3 | 98 |
| 4 | 81 |
| 998 | 10 |

La proposta di target binario considera alta crescita il codice `4`; sui 301 casi con codice da 1 a 4, la classe positiva conta 81 osservazioni. Il significato dei codici è riportato nella chat: riduzione, stabilità, crescita inferiore al 30%, crescita almeno pari al 30%.

### Colonne composite

Il dataset contiene dieci colonne composite riconducibili a innovativeness, open innovation e tecnologie. Queste colonne risultano valorizzate per tutte le 311 startup, ma la sola presenza del valore non dimostra la correttezza della formula di aggregazione.

## Collegamenti

- [[costrutti-crescita-startup|Costrutti per la crescita delle startup]]
- [[xgboost-crescita-startup|XGBoost per la crescita delle startup]]
- [[framework-analitico-crescita-startup|Framework analitico per la crescita delle startup]]

## Contraddizioni o dubbi

- Manca un codebook esplicito che confermi il significato di `d1b = 14` e dei codici speciali `997`, `998`, `999`.
- Va verificato se `Q13` sia già invertito nelle colonne composite o debba essere ricodificato prima dell'aggregazione.
- Vanno documentati scala, direzione e formula di aggregazione di ogni colonna composita.

## Fonti

- `.codex_sources/source-za9016-v1-0-0-final-638abfdbcd.txt` (origine: `raw/ZA9016_v1-0-0_FINAL.xlsx`; conteggi calcolati sul testo estratto completo).
- `.codex_sources/source-chat-martina-xgboost-pls-sem-f07ec89b70.txt`.
- `.codex_sources/source-conceptual-model-data-carlo-1-f2ecf19d79.txt`.

