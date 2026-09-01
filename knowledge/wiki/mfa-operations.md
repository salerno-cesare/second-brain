# Operatività e supporto MFA

## Sintesi

Il portale self-service supporta gestione dell'istanza, utenti e ruoli, codici temporanei, consultazione dei log, audit, dashboard, test API e controllo dei dispositivi registrati.

## Dettagli

### Supporto all'accesso

Dopo aver verificato l'identità dell'utente, un amministratore può generare un codice di accesso valido 24 ore quando le altre modalità MFA non sono utilizzabili. Un'applicazione può implementare la stessa capacità tramite `CreateAccessCode` e `VerifyAccessCode`.

### Log e audit

Il portale mostra log MFA e log Email filtrati per intervallo temporale e utente; dalla sezione Email è possibile inviare un messaggio di test. L'audit permette di scaricare eventi delle ultime 100 richieste e degli ultimi 30 giorni.

L'Admin API `/api/mfa/admin/serviceInstances/{name}/audit` accetta filtri quali istanza, intervallo e `ClientUserId`. La proprietà `deliveryInfo` riporta dettagli di consegna SMS/Voice, inclusi stati come queued, sent e delivered e informazioni specifiche dei provider Plivo o Twilio.

### Dashboard e profilo

La dashboard mostra contatori delle richieste nelle ultime 24 ore e negli ultimi 30 giorni. Il profilo del Service Owner espone dispositivi registrati, email, display name, chiavi primaria/secondaria, token JWT e authenticator associati.

### Verifica disponibilità

La disponibilità si controlla tramite `https://{base_url}/healthmonitor/laststatus?client=YourApplicationName`; è preferibile usare il nome dell'istanza come identificativo `client`.

### Test delle API

Il portale e Swagger consentono di invocare le API e osservare schema, identificativo e stato della sessione. Le API amministrative usano le credenziali del Service Owner associate alla chiave dell'istanza.

## Collegamenti

- [[mfa-service-instance|Istanza del servizio MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-registered-devices|Dispositivi registrati MFA]]

## Contraddizioni o dubbi

- La fonte non definisce conservazione complessiva, access control dettagliato o formato di esportazione dei log oltre alle finestre offerte dal portale.
- Il processo di verifica dell'identità che precede la generazione del codice temporaneo non è specificato.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

