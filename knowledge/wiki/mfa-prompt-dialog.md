# MFA Prompt Dialog

## Sintesi

La MFA Prompt Dialog è la UI standard che presenta all'utente le modalità disponibili, avvia il challenge e restituisce all'applicazione un identificativo di completamento da validare sul server.

## Dettagli

### Creazione e redirect

L'applicazione chiama `CreateMfaPrompt` passando i recapiti disponibili, `clientUserId`, URI di ritorno ed eventuali parametri per dispositivi registrati, IP, user agent, banner e stylesheet. La risposta contiene `mfaUiUrl`, valido per un minuto; il browser deve essere reindirizzato a tale URL entro questa finestra. L'utente dispone poi del timeout configurato, indicato come cinque minuti per impostazione predefinita.

### Modalità presentate

La UI può presentare Email, SMS, Voice, authenticator TOTP/push, dispositivo ricordato e codice temporaneo. L'opzione Authenticator è mostrata solo quando il pairing è già stato verificato; i flussi di pairing tramite prompt verificano la registrazione nel loro processo.

### Completamento

In caso di successo, il browser ritorna a `redirectUri` con `mfaCompletionId`. L'applicazione deve chiamare `ValidateMfaCompletionToken` e può registrare modalità, stato e identificativo della sessione nei propri audit log.

### Esiti di errore

Gli errori documentati sono `Denied`, `SessionExpired`, `UserLockedOut`, `TooManyAttempts`, `MFAServiceUnknownError` e `MFABadRequest`. Sono inviati a `redirectOnErrorUri`, oppure a `redirectUri` quando l'URI di errore non è valorizzato.

### Personalizzazione

La UI può usare un foglio CSS minificato e un banner JPG/PNG caricato come allegato dell'istanza. Per il banner è indicato un rapporto 16:9.

## Collegamenti

- [[mfa-authenticator-pairing|Pairing degli authenticator MFA]]
- [[mfa-registered-devices|Dispositivi registrati MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-verify-dialog|MFA Verify Dialog]]

## Contraddizioni o dubbi

- La guida elenca più soglie di tentativo con formulazioni non perfettamente allineate; la relazione tra tentativi totali e tentativi falliti va verificata.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

