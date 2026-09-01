# Notifiche MFA tramite SignalR

## Sintesi

Per Voice e WK Authenticator, SignalR notifica al client il completamento asincrono della sessione, ma la notifica non sostituisce la verifica dello stato presso il servizio MFA.

## Dettagli

### Connessione

L'hub è disponibile a `https://<MFAServiceURL>/signalr/hubs` con nome `mfaHub`. Il client si iscrive chiamando `subscribe` con l'identificativo della sessione MFA e si disiscrive con `unsubscribe` al termine.

### Evento

L'evento client `loginCompleted` riceve un booleano: `true` indica sessione validata e approvata, `false` sessione validata e negata. Dopo l'evento, l'applicazione deve interrogare il servizio e validare lo stato prima di completare l'MFA.

### Timeout e CORS

Il client deve interrompere l'ascolto allo scadere della sessione, indicata come cinque minuti nell'esempio. Le applicazioni JavaScript devono consentire l'URL degli hub nella propria policy CORS.

## Collegamenti

- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]
- [[mfa-authenticator-pairing|Pairing degli authenticator MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]

## Contraddizioni o dubbi

- Le guide SignalR JavaScript e .NET citate dalla fonte non sono incluse; non sono quindi documentati versioni client, compatibilità e gestione della riconnessione.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

