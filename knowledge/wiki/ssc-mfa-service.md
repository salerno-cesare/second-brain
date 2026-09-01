# SSC Multi-Factor Authentication (MFA) Service

## Sintesi

- Servizio Shared Services & Components (SSC) che aggiunge un secondo fattore a scenari applicativi già dotati di autenticazione di primo fattore.
- Supporta Email, SMS, Voice, WK Authenticator, authenticator TOTP compatibili RFC 6238, codici di accesso temporanei e dispositivi ricordati.
- Espone REST API, Client SDK .NET/Java, UI standard e possibilità di UI personalizzata.
- La fonte sintetica dichiara un utilizzo superiore a 75 milioni di autenticazioni annue, senza indicare la data della misurazione.

## Dettagli

### Scopo e casi d'uso

Il servizio è destinato ad applicazioni che usano provider di identità WK, autenticazione proprietaria, provider interni o provider terzi privi di MFA. È indicato anche quando l'MFA del provider terzo è ritenuto troppo costoso o quando serve una riconvalida leggera dell'identità durante un flusso critico avviato dall'utente.

### Modalità supportate

- SMS e Voice richiedono un numero telefonico.
- Email richiede un indirizzo email.
- WK Authenticator supporta TOTP e approvazione tramite applicazione mobile.
- Google Authenticator, Microsoft Authenticator e altri authenticator compatibili usano TOTP secondo RFC 6238.
- Il codice di accesso temporaneo è generato tramite portale di supporto o API applicativa.
- “Remember My Device” usa credenziali/cookie di dispositivo registrato.
- WhatsApp è annunciato come futuro nel 2026, non come capacità già disponibile.

### Capacità trasversali

Il servizio offre UI standard, integrazione tramite UI personalizzata, provider multipli per Email/SMS/Voice per disponibilità e consegna, nonché un portale amministrativo self-service.

## Collegamenti

- [[mfa-service-instance|Istanza del servizio MFA]]
- [[mfa-integration-interfaces|Interfacce di integrazione MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]
- [[mfa-operations|Operatività e supporto MFA]]

## Contraddizioni o dubbi

- La disponibilità di WhatsApp non è confermata: entrambe le fonti la descrivono come prevista nel 2026.
- Il valore “oltre 75 milioni di autenticazioni per anno” non riporta periodo di osservazione o data di aggiornamento.

## Fonti

- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`
- `.codex_sources/source-ssc-multi-factor-authentication-mfa-service-010926-122813-836ae5fb18.txt`

