# Dispositivi registrati MFA

## Sintesi

La funzione “Remember My Device” riduce le richieste MFA riconoscendo un dispositivo tramite una credenziale firmata, soggetta a scadenza e a controlli opzionali su IP e user agent.

## Dettagli

### Ciclo di vita

`CreateRegisteredDevice` crea il `DeviceCredential`; `VerifyRegisteredDevice` lo verifica. `ReadRegisteredDevices` elenca le registrazioni e `RevokeRegisteredDevice` le revoca. La Prompt UI può offrire la registrazione del dispositivo e supportare scadenza scorrevole.

### Scadenza

L'istanza configura una scadenza massima in giorni. Il valore predefinito indicato è 30 giorni, motivato dalla ri-autenticazione prevista per NIST 800-63b AAL1. La Prompt API accetta tempi di scadenza per creazione e verifica.

### Vincoli contestuali

La configurazione può richiedere la presenza di IP o user agent e, separatamente, la loro uguaglianza rispetto ai valori registrati. Quando tali dati sono obbligatori, devono essere inclusi anche nella creazione della sessione MFA.

### Uso raccomandato

La guida raccomanda il dispositivo ricordato per funzionalità utente ordinarie. Per operazioni amministrative, come l'aggiornamento del numero telefonico, può essere richiesta MFA nella sessione corrente; per la configurazione di Google Authenticator può essere richiesta MFA effettuata negli ultimi cinque minuti. In un'identità a claim, “MFA Performed” e “RememberMe Verified” devono restare distinti.

## Collegamenti

- [[mfa-prompt-dialog|MFA Prompt Dialog]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-operations|Operatività e supporto MFA]]

## Contraddizioni o dubbi

- I requisiti di ri-autenticazione per operazioni amministrative sono presentati come raccomandazioni (“may require”), non come policy obbligatorie del servizio.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

