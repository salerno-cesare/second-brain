# MFA Verify Dialog

## Sintesi

La MFA Verify Dialog è una UI standard che avvia una nuova sessione per una modalità MFA già specificata dall'applicazione e chiede all'utente di confermarla.

## Dettagli

### Flusso

L'applicazione chiama `CreateMfaVerify` con una modalità tra `email`, `sms` e `voice`, i dati di contatto, `clientUserId`, redirect ed eventuali allegati grafici. La risposta restituisce `mfaUiUrl`, valido per un minuto. L'utente ha il timeout di sessione configurato, indicato come cinque minuti per impostazione predefinita, per completare la conferma.

### Verifica del risultato

Dopo il redirect, l'applicazione valida il completamento con lo stesso schema della Prompt Dialog: deve verificare il token/identificativo restituito prima di considerare riuscita l'MFA.

### Differenza dalla Prompt Dialog

La Prompt Dialog consente la scelta tra più opzioni disponibili. La Verify Dialog riceve una singola modalità e avvia direttamente la relativa sessione.

### Personalizzazione ed errori

Stylesheet, banner e scenari di redirect seguono quanto documentato per la [[mfa-prompt-dialog|MFA Prompt Dialog]].

## Collegamenti

- [[mfa-prompt-dialog|MFA Prompt Dialog]]
- [[mfa-integration-interfaces|Interfacce di integrazione MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]

## Contraddizioni o dubbi

- La guida descrive la verifica per rinvio alla sezione della Prompt Dialog e non esplicita nel testo estratto tutti i campi della risposta.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

