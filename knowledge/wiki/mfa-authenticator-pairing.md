# Pairing degli authenticator MFA

## Sintesi

Il servizio registra WK Authenticator e authenticator TOTP compatibili RFC 6238 associando una chiave all'identificativo applicativo dell'utente e presentandola tramite QR code o inserimento manuale.

## Dettagli

### Pairing TOTP diretto

`GetTotpKey` o `GenerateTotpKey` crea la chiave per lo `userId`; `CreateQrCode` produce il QR code. L'etichetta dell'account dovrebbe distinguere organizzazione/applicazione e utente. Ogni nuova generazione invalida la chiave precedente. La chiave può essere disabilitata e riabilitata con `SetTotpEnabled`, per esempio in caso di dispositivo smarrito.

Prima di rendere disponibile l'opzione nella Prompt UI, la registrazione deve essere verificata avviando una sessione TOTP e validando un codice. Ogni codice può essere accettato una sola volta.

### WK Authenticator

Il QR code include anche `wkmfaurl` e `wkmfauserguid`. L'app mobile usa `wkmfaurl` come base URL. Il server può avviare una sessione con `StartTotpWsSession`; l'app recupera l'ultima sessione e l'utente confronta l'identificativo mostrato sui due lati prima di approvare o negare.

In assenza di accesso del client al server, la guida indica l'uso del TOTP manuale come modalità offline.

### Pairing Prompt

`CreateAuthPairingPrompt` genera un URL valido un minuto per la UI di pairing. Il prompt supporta WK Authenticator e Google Authenticator; per WK il metodo predefinito è `WKA`. Il successo reindirizza con `completionId`, da validare con `ValidateAppPairingCompletionToken`; l'annullamento reindirizza con `errorCode=Cancelled`. Nel flusso web WK un pairing non completato può restituire `errorCode=NOTPAIRED`.

### Authenticator di terze parti

Google Authenticator, Microsoft Authenticator e altri client compatibili RFC 6238 seguono lo stesso modello TOTP.

## Collegamenti

- [[mfa-prompt-dialog|MFA Prompt Dialog]]
- [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]]
- [[mfa-signalr-notifications|Notifiche MFA tramite SignalR]]

## Contraddizioni o dubbi

- Il testo estratto usa sia `completionId` sia `authPairingCompletionId` per flussi di pairing correlati; va verificato lo schema esatto delle API interessate.
- La relazione tra `defaultPairingMethod` e `authPairMode` non è descritta in modo completo.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

