# Confermare una modalità con MFA Verify

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Erogazione dei challenge MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-verify-dialog|MFA Verify Dialog]]

## Descrizione

L'applicazione specifica una singola modalità e il servizio avvia direttamente la relativa sessione nella UI MFA Verify.

## User story

Come utente di un'applicazione, voglio confermare la modalità MFA proposta, così da completare la verifica richiesta senza selezionare tra più opzioni.

## Criteri di accettazione

- Given una modalità `email`, `sms` o `voice`, When l'applicazione chiama `CreateMfaVerify`, Then il servizio restituisce un `mfaUiUrl` valido per un minuto.
- Given la Verify UI aperta, When l'utente completa il challenge entro il timeout, Then l'applicazione riceve un identificativo di completamento.
- Given l'identificativo di completamento, When l'applicazione lo valida, Then il successo viene accettato solo dopo la verifica server-side.

## Regole funzionali

- La Verify Dialog avvia una nuova sessione per la modalità ricevuta.
- Le modalità documentate per questo flusso sono Email, SMS e Voice.

## Dipendenze

- [[epica-erogazione-challenge-mfa|Epica — Erogazione dei challenge MFA]]
- [[mfa-prompt-dialog|MFA Prompt Dialog]]

## Dubbi aperti

- Il testo estratto non riporta per esteso tutti i campi della risposta di validazione.

## Fonti

- [[mfa-verify-dialog|MFA Verify Dialog]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

