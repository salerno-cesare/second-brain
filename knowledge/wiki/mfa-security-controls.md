# Controlli di sicurezza MFA

## Sintesi

Il servizio applica timeout, limitazione dei tentativi, protezione delle credenziali di sessione, modalità di conformità e controlli opzionali su IP, user agent e autenticazione dell'app mobile.

## Dettagli

### Sessioni e tentativi

Il timeout predefinito della sessione è cinque minuti ed è configurabile sull'istanza. La guida indica fallimento quando lo stesso `clientUserId` usa MFA più di cinque volte in quindici minuti. Per la Prompt UI documenta inoltre `UserLockedOut` dopo cinque tentativi falliti consecutivi in quindici minuti e `TooManyAttempts` dopo cinque tentativi consecutivi in un minuto.

Il codice OTP è di sei cifre. `VerifyCode` su Email/SMS e la verifica di un codice TOTP sono monouso per sessione/codice.

### Correlazione dell'identità

L'identificativo della sessione deve essere conservato sul server o protetto da firma crittografica. La verifica deve assicurare che la sessione sia stata avviata per l'utente autenticato. La UI personalizzata deve usare identificativi opachi e recapiti mascherati.

### Modalità di conformità

In modalità `Nist800-63b` Email non è ammessa e SMS/Voice verso numeri VoIP non sono ammessi. Se il testo Voice non contiene `{{verificationCode}}`, viene usato il prompt predefinito che include il token. In modalità `Audit Only`, l'uso di Email o di SMS/Voice verso VoIP genera un evento di audit, senza il blocco descritto per NIST.

### Bypass controllati

L'istanza può escludere dall'MFA specifici `clientUserId` per monitoraggio sintetico, utenti sandbox e richieste provenienti da IP fidati. La funzione MFA Short Circuit dell'SDK, attivata dalla configurazione applicativa `mfa:ShortCircuitService`, bypassa la Prompt UI e restituisce esiti sintetici di successo durante problemi di rete o del servizio.

### Autenticazione applicativa e dispositivo

L'istanza può imporre passcode o biometria per l'approvazione di sessioni nell'Authenticator App e può vincolare i dispositivi registrati a IP e user agent.

## Collegamenti

- [[mfa-service-instance|Istanza del servizio MFA]]
- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]
- [[mfa-registered-devices|Dispositivi registrati MFA]]
- [[mfa-operations|Operatività e supporto MFA]]

## Contraddizioni o dubbi

- Le tre formulazioni sulle soglie non chiariscono se “usi”, “tentativi consecutivi” e “tentativi falliti consecutivi” siano contatori indipendenti o descrizioni parzialmente sovrapposte.
- Short Circuit produce un successo sintetico e costituisce un rischio operativo; la fonte non specifica autorizzazioni, audit o processo di attivazione.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

