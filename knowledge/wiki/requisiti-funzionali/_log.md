# Log operativo Requisiti Funzionali

Questo log traccia le modifiche alla wiki parallela dei requisiti funzionali.

## 2026-09-01T15:24:31+02:00 - compilazione requisiti SSC MFA

- Modalità: `compile`.
- Progetto indicizzato: SSC Multi-Factor Authentication (MFA) Service.
- Epiche create:
  - [[epica-erogazione-challenge-mfa|Erogazione dei challenge MFA]].
  - [[epica-gestione-autenticatori-dispositivi|Gestione di authenticator e dispositivi]].
  - [[epica-amministrazione-supporto-mfa|Amministrazione e supporto MFA]].
- User story create:
  - [[us-presentare-mfa-prompt|Presentare e completare la MFA Prompt]].
  - [[us-verificare-modalita-mfa|Confermare una modalità con MFA Verify]].
  - [[us-eseguire-challenge-mfa-custom-ui|Eseguire un challenge MFA con UI personalizzata]].
  - [[us-associare-authenticator|Associare un authenticator all'utente]].
  - [[us-ricordare-dispositivo|Registrare e riconoscere un dispositivo]].
  - [[us-revocare-dispositivo|Revocare un dispositivo registrato]].
  - [[us-configurare-istanza-mfa|Configurare un'istanza MFA]].
  - [[us-generare-codice-accesso-temporaneo|Generare e verificare un codice di accesso temporaneo]].
  - [[us-consultare-log-audit-mfa|Consultare log e audit MFA]].
- Dubbi aperti:
  - Priorità e fase non sono indicate dalle fonti.
  - Non sono documentati tutti i criteri autorizzativi per configurazione, log e generazione dei codici temporanei.
  - La relazione esatta tra le soglie di lockout e rate limiting richiede verifica.

