# Log operativo
## 2026-09-01T15:22:22+02:00 - configurazione lingua

- Pagine create:
  - [[_config|Configurazione Wiki]]
- Pagine aggiornate:
  - [[_log|Log operativo]]
- Lingua wiki bloccata: Italian (`it`).
- Dubbi aperti:
  - Nessuno.

## 2026-09-01T15:24:31+02:00 - compilazione SSC MFA

- Modalità: `compile`.
- Fonti considerate:
  - `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt` (origine `raw/SSC-MFA Developer Guide-010926-122942.pdf`).
  - `.codex_sources/source-ssc-multi-factor-authentication-mfa-service-010926-122813-836ae5fb18.txt` (origine `raw/SSC-Multi-Factor Authentication (MFA) Service-010926-122813.pdf`).
- Pagine create:
  - [[ssc-mfa-service|SSC Multi-Factor Authentication (MFA) Service]].
  - [[mfa-service-instance|Istanza del servizio MFA]].
  - [[mfa-security-controls|Controlli di sicurezza MFA]].
  - [[mfa-integration-interfaces|Interfacce di integrazione MFA]].
  - [[mfa-prompt-dialog|MFA Prompt Dialog]].
  - [[mfa-verify-dialog|MFA Verify Dialog]].
  - [[mfa-custom-ui-flow|Flusso MFA con UI personalizzata]].
  - [[mfa-signalr-notifications|Notifiche MFA tramite SignalR]].
  - [[mfa-authenticator-pairing|Pairing degli authenticator MFA]].
  - [[mfa-registered-devices|Dispositivi registrati MFA]].
  - [[mfa-operations|Operatività e supporto MFA]].
- Pagine aggiornate:
  - [[_index|Indice Wiki]].
  - [[_log|Log operativo]].
- Pagine unite o divise:
  - Nessuna pagina preesistente da unire; i contenuti della guida sono stati divisi in pagine atomiche per servizio, integrazione, sicurezza e operatività.
- Dubbi aperti:
  - WhatsApp è indicato soltanto come “coming in 2026”; la disponibilità effettiva non è confermata.
  - Le formulazioni sui limiti dei tentativi distinguono uso, tentativi consecutivi e tentativi falliti, ma non chiariscono completamente la relazione tra le soglie.
  - La fonte sintetica dichiara oltre 75 milioni di autenticazioni annue senza data di rilevazione.
  - La guida cita documenti esterni non inclusi nelle fonti estratte: Environment Selection Guide, Support Role Guide e guide SignalR.

## 2026-09-01T15:45:39+02:00 - architettura Gateway MFA su OneID

- Modalità: proposta architetturale derivata dalla wiki (nessuna nuova fonte esterna).
- Pagine create:
  - [[architettura-gateway-mfa-oneid|Architettura Gateway MFA condiviso su OneID]].
- Pagine aggiornate:
  - [[_index|Indice Wiki]] (nuova sezione "Architetture proposte").
  - [[_log|Log operativo]].
- Contenuto: gateway web condiviso che integra [[ssc-mfa-service|SSC MFA]] nel flusso di login OneID; attivazione opt-in tramite flag sul profilo utente; blocco del login se il flag è attivo e il challenge non è completato.
- Dubbi aperti:
  - OneID come identity provider e meccanismo di delega step MFA a gateway esterno non sono descritti in wiki.
  - Il flag MFA sul profilo utente non è documentato: owner del dato, storage, superficie di gestione e audit sono da definire.
  - Policy di condivisione dell'istanza SSC MFA fra portali (istanza unica vs una per portale) non documentata.
  - Comportamento del gateway con flag disattivo in modalità di conformità `Nist800-63b` non definito.
  - Gestione utenti con flag attivo ma senza modalità MFA configurate non definita.

## 2026-09-01T17:35:42+02:00 - diagrammi Gateway MFA su OneID

- Modalità: aggiornamento pagina esistente (nessuna nuova fonte).
- Pagine aggiornate:
  - [[architettura-gateway-mfa-oneid|Architettura Gateway MFA condiviso su OneID]]: aggiunta sezione "Diagrammi" con vista dei componenti (Mermaid `flowchart`) e vista di sequenza del login (Mermaid `sequenceDiagram`).
  - [[_log|Log operativo]].
- Dubbi aperti:
  - Nessuno nuovo rispetto alla voce precedente.

