# Interfacce di integrazione MFA

## Sintesi

Il servizio MFA può essere invocato tramite REST API o Client SDK per .NET e Java. Ogni chiamata opera nel contesto di un'istanza identificata da nome e chiave di accesso.

## Dettagli

### REST API

Il servizio e le funzioni amministrative sono disponibili via REST. La descrizione dei metodi, dei parametri e delle risposte è esposta tramite Swagger all'URL `{Service_URL}/swagger`. La gestione amministrativa usa come API key l'email del Service Owner combinata con la chiave di accesso.

### Client SDK

Per .NET la guida indica il pacchetto NuGet `WK.TAA.SharedWebServices.ClientSdk.NSwag.Mfa`. Il client `MultiFactorAuthenticationClient` viene inizializzato con nome istanza, chiave dell'istanza e URI base del server. L'SDK usa SharedKey; l'orologio del chiamante deve differire da quello del server per meno di 15 minuti.

### Evoluzione SDK

Dalla versione 1.23 il tipo `SharedWebServicesClient`, presente nella 1.21, non è più disponibile. Il pacchetto è stato rinominato da `WK.TAA.SharedWebServices.ClientSdk.Mfa` e i metodi sono invocati direttamente su `MultiFactorAuthenticationClient`.

### Autenticazione supportata

Le REST API supportano gli schemi Basic e SharedKey. L'SDK client usa esclusivamente SharedKey. L'istanza può inoltre autorizzare specifici `OneIdClientId` per chiamate non amministrative.

## Collegamenti

- [[mfa-prompt-dialog|MFA Prompt Dialog]]
- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]
- [[mfa-service-instance|Istanza del servizio MFA]]

## Contraddizioni o dubbi

- La fonte dichiara supporto SDK .NET e Java, ma fornisce dettagli di installazione ed evoluzione soltanto per il pacchetto .NET.
- Gli URL di ambiente sono sostituiti da segnaposto e dipendono da una guida esterna non inclusa.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

