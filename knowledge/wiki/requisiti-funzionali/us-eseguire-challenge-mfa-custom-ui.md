# Eseguire un challenge MFA con UI personalizzata

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Erogazione dei challenge MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]

## Descrizione

L'applicazione presenta una UI propria e orchestra avvio, raccolta della prova e verifica del challenge tramite le API MFA.

## User story

Come utente di un'applicazione con esigenze UI specifiche, voglio completare il challenge nel flusso dell'applicazione, così da effettuare l'MFA senza usare la finestra standard.

## Criteri di accettazione

- Given più recapiti disponibili, When il server costruisce le opzioni, Then assegna identificativi opachi e non espone il recapito completo al client.
- Given una sessione Email o SMS, When l'utente inserisce il codice, Then il server usa `VerifyCode` una sola volta per quella sessione.
- Given un challenge Voice con conferma `#`, When l'utente conferma, Then l'applicazione verifica l'esito con `GetStatus`.
- Given un codice TOTP, When viene verificato con successo, Then lo stesso codice non è accettato una seconda volta.
- Given un identificativo MFA, When il server conclude il flusso, Then verifica che la sessione appartenga all'utente autenticato.

## Regole funzionali

- Email e SMS usano `SendEmail`/`SendSMS` e `VerifyCode`.
- Voice usa `GetStatus` oppure `VerifyCode` in base al template/provider documentato.
- TOTP usa `VerifyTotp` oppure una sessione TOTP dedicata.

## Dipendenze

- [[epica-erogazione-challenge-mfa|Epica — Erogazione dei challenge MFA]]
- [[mfa-integration-interfaces|Interfacce di integrazione MFA]]

## Dubbi aperti

- La selezione del provider Voice e le relative regole di configurazione non sono documentate completamente.

## Fonti

- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

