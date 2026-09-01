# Istanza del servizio MFA

## Sintesi

Un'istanza del servizio rappresenta la registrazione di un'applicazione presso SSC MFA e costituisce il contesto di accesso, configurazione, rendicontazione e gestione degli utenti.

## Dettagli

### Creazione e identificazione

La creazione avviene dal portale TechBV Shared Web Services autenticato tramite SSO. Il nome deve essere univoco, lungo almeno otto caratteri e composto da caratteri alfanumerici o underscore, senza spazi. L'istanza associa Division, uno o più Product, Billing Code ed Environment; l'ambiente Production deve essere scelto solo per istanze di produzione in ambiente produttivo.

### Configurazione funzionale

Sono configurabili timeout della sessione, domini email consentiti, modalità predefinita della Prompt UI, soft-disable dell'Email, modalità di conformità, metadati JSON, client OneID autorizzati, IP fidati, utenti sandbox, utenti esclusi per monitoraggio sintetico, pairing Standard o IDaaS e obbligo di passcode/biometria per l'approvazione nell'app.

La modalità Sandbox è destinata al load test e, quando attiva, include il codice di verifica nella risposta. Gli IP fidati possono causare il bypass dell'MFA quando l'indirizzo client corrisponde alla lista configurata.

### Chiavi e messaggi

L'istanza espone chiavi di accesso primaria e secondaria; la rigenerazione invalida le chiavi precedenti. I messaggi Email e SMS sono template Liquid localizzati che possono usare `{{verificationCode}}`, sostituzioni JSON e allegati. Gli allegati HTML inline richiedono corrispondenza tra Content ID e attributo `cid`.

### Ruoli

- Service Owner: accesso completo all'istanza.
- Product Support Representative: accesso alla sezione Support, inclusi log MFA ed Email.
- Product Support Supervisor: accesso a utenti e log SMS.

## Collegamenti

- [[ssc-mfa-service|SSC Multi-Factor Authentication (MFA) Service]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-operations|Operatività e supporto MFA]]

## Contraddizioni o dubbi

- La guida rimanda a un Environment Selection Guide e a un Support Role Guide non presenti nelle fonti preparate.
- Non è documentato il processo autorizzativo per assegnare o revocare i tre ruoli.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

