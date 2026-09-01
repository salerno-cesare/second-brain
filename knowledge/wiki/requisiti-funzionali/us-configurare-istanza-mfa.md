# Configurare un'istanza MFA

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Amministrazione e supporto MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-service-instance|Istanza del servizio MFA]]

## Descrizione

Il portale consente di creare un contesto applicativo e configurarne ambiente, modalità, recapiti ammessi, messaggi, chiavi e controlli.

## User story

Come Service Owner, voglio configurare un'istanza MFA per la mia applicazione, così da definire accesso, modalità e comportamento del servizio.

## Criteri di accettazione

- Given un nuovo nome istanza, When contiene meno di otto caratteri, spazi o caratteri non ammessi, Then la creazione non deve accettarlo.
- Given un'istanza valida, When viene creata, Then rende disponibili chiavi primaria e secondaria e template predefiniti `en-US` per Email e SMS.
- Given una lista di domini Email, When viene salvata, Then l'istanza limita l'invio ai domini consentiti.
- Given la rigenerazione delle chiavi, When l'operazione termina, Then le chiavi precedenti risultano invalidate.
- Given un template con `{{verificationCode}}`, When viene usato per Email, SMS o Voice secondo la configurazione, Then il servizio sostituisce il token con il codice.

## Regole funzionali

- Il nome ammette caratteri alfanumerici e underscore, senza spazi.
- Production deve essere selezionato solo per istanze di produzione in ambiente produttivo.
- Sandbox include il codice di verifica nella risposta ed è destinato al load test.

## Dipendenze

- [[epica-amministrazione-supporto-mfa|Epica — Amministrazione e supporto MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]

## Dubbi aperti

- Non è documentato il workflow di approvazione della creazione o della modifica dell'istanza.

## Fonti

- [[mfa-service-instance|Istanza del servizio MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

