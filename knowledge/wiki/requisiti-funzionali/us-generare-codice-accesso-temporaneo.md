# Generare e verificare un codice di accesso temporaneo

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Amministrazione e supporto MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-operations|Operatività e supporto MFA]]

## Descrizione

Quando l'utente non può usare le modalità ordinarie, un amministratore o una utility applicativa può generare un codice temporaneo dopo la verifica dell'identità.

## User story

Come operatore di supporto, voglio generare un codice di accesso temporaneo per un utente identificato, così da consentirgli di completare l'MFA durante un'indisponibilità delle altre modalità.

## Criteri di accettazione

- Given un utente la cui identità è stata verificata, When l'amministratore genera il codice dal portale, Then il codice è valido per 24 ore.
- Given una utility autorizzata, When chiama `CreateAccessCode`, Then il servizio crea un codice associato allo scenario utente.
- Given un codice temporaneo, When viene sottoposto a `VerifyAccessCode`, Then il servizio ne restituisce l'esito di validità.
- Given un codice disponibile per il `clientUserId`, When la MFA Prompt viene aperta, Then mostra automaticamente l'opzione per usarlo.

## Regole funzionali

- La verifica dell'identità precede la generazione del codice.
- Il codice può essere creato da portale o tramite API applicativa.

## Dipendenze

- [[epica-amministrazione-supporto-mfa|Epica — Amministrazione e supporto MFA]]
- [[mfa-prompt-dialog|MFA Prompt Dialog]]

## Dubbi aperti

- Il processo di verifica dell'identità, il numero di codici contemporanei e le regole di revoca non sono specificati.

## Fonti

- [[mfa-operations|Operatività e supporto MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

