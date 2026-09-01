# Associare un authenticator all'utente

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Gestione di authenticator e dispositivi
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-authenticator-pairing|Pairing degli authenticator MFA]]

## Descrizione

Il servizio genera una chiave e un QR code per associare WK Authenticator o un authenticator TOTP compatibile all'identificativo dell'utente.

## User story

Come utente, voglio associare un'app authenticator al mio identificativo, così da usare codici TOTP o approvazioni mobili come secondo fattore.

## Criteri di accettazione

- Given uno `userId`, When viene richiesta una nuova chiave TOTP, Then il servizio genera chiave e QR code associati all'utente.
- Given una chiave precedente, When ne viene generata una nuova, Then la chiave precedente è invalidata.
- Given il QR code visualizzato, When l'utente lo acquisisce e presenta un codice valido, Then il pairing può essere verificato.
- Given un Pairing Prompt completato, When l'applicazione riceve l'identificativo di completamento, Then lo valida tramite l'API dedicata.
- Given un pairing annullato o non completato, When la UI effettua il redirect, Then restituisce rispettivamente `Cancelled` o, nel flusso WK documentato, `NOTPAIRED`.

## Regole funzionali

- Sono supportati WK Authenticator e authenticator compatibili RFC 6238.
- La chiave può essere disabilitata e riabilitata.
- L'opzione non deve apparire nella MFA Prompt prima della verifica del pairing.

## Dipendenze

- [[epica-gestione-autenticatori-dispositivi|Epica — Gestione di authenticator e dispositivi]]
- [[mfa-prompt-dialog|MFA Prompt Dialog]]

## Dubbi aperti

- Lo schema dei nomi `completionId` e `authPairingCompletionId` deve essere verificato sulle API effettive.

## Fonti

- [[mfa-authenticator-pairing|Pairing degli authenticator MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

