# Indice Wiki

Knowledge base tecnica del servizio Shared Services & Components (SSC) Multi-Factor Authentication.

## Servizio e configurazione

- [[ssc-mfa-service|SSC Multi-Factor Authentication (MFA) Service]] — scopo, casi d'uso, modalità supportate e capacità principali.
- [[mfa-service-instance|Istanza del servizio MFA]] — registrazione applicativa, configurazione, ruoli e template dei messaggi.
- [[mfa-security-controls|Controlli di sicurezza MFA]] — timeout, limitazione dei tentativi, conformità, bypass e protezione dei dati.

## Integrazione applicativa

- [[mfa-integration-interfaces|Interfacce di integrazione MFA]] — REST API, Client SDK .NET/Java, autenticazione e migrazione SDK.
- [[mfa-prompt-dialog|MFA Prompt Dialog]] — flusso della UI standard per la scelta e il completamento del secondo fattore.
- [[mfa-verify-dialog|MFA Verify Dialog]] — flusso della UI standard per confermare una modalità MFA già scelta.
- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]] — orchestrazione applicativa di Email, SMS, Voice e TOTP.
- [[mfa-signalr-notifications|Notifiche MFA tramite SignalR]] — aggiornamenti asincroni per Voice e WK Authenticator.

## Autenticatori e continuità d'accesso

- [[mfa-authenticator-pairing|Pairing degli authenticator MFA]] — registrazione di WK Authenticator e authenticator TOTP tramite chiave e QR code.
- [[mfa-registered-devices|Dispositivi registrati MFA]] — funzione “Remember My Device”, credenziali dispositivo e revoca.

## Amministrazione e operatività

- [[mfa-operations|Operatività e supporto MFA]] — portale self-service, codici temporanei, log, audit, dashboard e monitoraggio.

## Architetture proposte

- [[architettura-gateway-mfa-oneid|Architettura Gateway MFA condiviso su OneID]] — gateway web condiviso che integra SSC MFA nel flusso di login OneID, con attivazione opt-in tramite flag di profilo utente.

## Viste derivate

- [[requisiti-funzionali/_index|Requisiti funzionali]] — indice progetto, epiche e user story estratti dalla wiki e dalle fonti.

