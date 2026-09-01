# Flusso MFA con UI personalizzata

## Sintesi

Le applicazioni possono sostituire la UI standard con un flusso proprietario, mantenendo sul server la selezione della modalità, l'identificativo della sessione e la verifica finale.

## Dettagli

### Selezione della modalità

Dopo l'autenticazione di primo fattore, l'applicazione determina se l'MFA è richiesta e quali modalità sono disponibili. La decisione può usare policy organizzative, dispositivo ricordato, recapiti disponibili, consenso dell'utente e presenza di una chiave TOTP già configurata. `CheckIfTotpKeyExists` verifica se per l'utente è stata generata una chiave.

Il server restituisce alla UI identificativi opachi delle opzioni, non recapiti utilizzabili direttamente. I numeri telefonici devono essere mascherati o rappresentati da etichette comprensibili, per impedire al client di sostituire il destinatario del secondo fattore.

### Email e SMS

L'applicazione avvia la sessione con `SendEmail` o `SendSMS`, raccoglie il codice ricevuto e chiama `VerifyCode`. Per una stessa sessione, `VerifyCode` può essere chiamato una sola volta.

### Voice

Nel flusso basato sulla conferma con tasto `#`, l'applicazione chiama `SendVoice` e poi `GetStatus`. Se il template vocale Twilio contiene `{{VerificationCode}}`, lo stato iniziale è `VerificationPending` e la verifica avviene con `VerifyCode`; senza token, lo stato è `InProgress` e viene controllato con `GetStatus`.

### TOTP

La UI raccoglie il codice dell'authenticator e il server lo verifica con `VerifyTotp`, oppure usa `StartTotpSession` e `VerifyTotpSession`. Ogni codice TOTP può essere verificato una sola volta.

### Correlazione e conclusione

L'identificativo MFA deve restare sul server o in una porzione crittograficamente firmata dello scambio. Il server deve verificare che la sessione appartenga all'utente autenticato. Dopo il successo è raccomandato registrare separatamente l'esito MFA e il momento in cui è avvenuto.

## Collegamenti

- [[mfa-integration-interfaces|Interfacce di integrazione MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-authenticator-pairing|Pairing degli authenticator MFA]]
- [[mfa-registered-devices|Dispositivi registrati MFA]]

## Contraddizioni o dubbi

- La guida descrive Azure MFA SDK come default per Voice e anche scenari Twilio, ma non specifica come venga selezionato il provider per una singola istanza.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

