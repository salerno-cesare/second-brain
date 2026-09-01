# Registrare e riconoscere un dispositivo

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Gestione di authenticator e dispositivi
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-registered-devices|Dispositivi registrati MFA]]

## Descrizione

Il servizio crea e verifica una credenziale firmata per evitare challenge ripetuti sullo stesso dispositivo entro la scadenza consentita.

## User story

Come utente, voglio registrare il mio dispositivo dopo un'MFA riuscita, così da non ripetere il challenge durante il periodo consentito.

## Criteri di accettazione

- Given una sessione MFA idonea, When l'utente sceglie di ricordare il dispositivo, Then il servizio crea un `DeviceCredential`.
- Given un `DeviceCredential` non scaduto, When l'applicazione lo verifica, Then il servizio restituisce l'esito di riconoscimento.
- Given il requisito IP o user agent attivo, When il dato richiesto manca, Then la verifica viene rifiutata.
- Given il requisito di uguaglianza attivo, When IP o user agent differisce dal valore registrato, Then la verifica viene rifiutata.

## Regole funzionali

- La scadenza massima è configurabile; il default documentato è 30 giorni.
- I claim relativi a MFA effettuata e dispositivo ricordato devono restare distinguibili.

## Dipendenze

- [[epica-gestione-autenticatori-dispositivi|Epica — Gestione di authenticator e dispositivi]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]

## Dubbi aperti

- Le policy applicative che stabiliscono quali operazioni possano accettare il dispositivo ricordato non sono definite dal servizio.

## Fonti

- [[mfa-registered-devices|Dispositivi registrati MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

