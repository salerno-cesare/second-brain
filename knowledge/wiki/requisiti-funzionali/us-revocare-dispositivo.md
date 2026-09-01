# Revocare un dispositivo registrato

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Gestione di authenticator e dispositivi
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-registered-devices|Dispositivi registrati MFA]]

## Descrizione

Il servizio permette di elencare le registrazioni e revocare una credenziale dispositivo che non deve più bypassare il challenge.

## User story

Come utente o operatore autorizzato, voglio revocare un dispositivo registrato, così da impedirne il successivo riconoscimento MFA.

## Criteri di accettazione

- Given un utente con dispositivi registrati, When viene invocata `ReadRegisteredDevices`, Then il servizio restituisce le registrazioni associate.
- Given una registrazione selezionata, When viene invocata `RevokeRegisteredDevice`, Then la credenziale non è più accettata da `VerifyRegisteredDevice`.

## Regole funzionali

- La revoca opera su una registrazione esistente.
- Il profilo del Service Owner mostra i dispositivi registrati del relativo account.

## Dipendenze

- [[epica-gestione-autenticatori-dispositivi|Epica — Gestione di authenticator e dispositivi]]
- [[us-ricordare-dispositivo|Registrare e riconoscere un dispositivo]]

## Dubbi aperti

- Attori autorizzati, conferme UI e comportamento su sessioni già attive non sono documentati.

## Fonti

- [[mfa-registered-devices|Dispositivi registrati MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

