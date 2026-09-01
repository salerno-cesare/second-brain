# Consultare log e audit MFA

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Amministrazione e supporto MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-operations|Operatività e supporto MFA]]

## Descrizione

Il portale e l'Admin API consentono agli operatori autorizzati di consultare sessioni MFA, invii Email e stato di consegna SMS/Voice.

## User story

Come operatore di supporto autorizzato, voglio filtrare e consultare log e audit MFA, così da analizzare sessioni e problemi di consegna per uno specifico utente o intervallo.

## Criteri di accettazione

- Given un utente e un intervallo temporale, When l'operatore consulta MFA Logs, Then il portale mostra i relativi eventi MFA.
- Given un utente e un intervallo temporale, When consulta MFA Email Logs, Then il portale mostra gli invii Email e consente un invio di test.
- Given i filtri istanza, tempo e `ClientUserId`, When viene invocata l'Admin API audit, Then restituisce i log corrispondenti.
- Given un evento SMS/Voice, When è presente `deliveryInfo`, Then sono disponibili stato e dettagli di consegna forniti dal provider.
- Given la funzione Audit del portale, When viene richiesto il download, Then rende disponibili gli eventi delle ultime 100 richieste e degli ultimi 30 giorni.

## Regole funzionali

- Il Product Support Representative accede alla sezione Support con log MFA ed Email.
- Il Product Support Supervisor accede a utenti e log SMS.
- Il Service Owner dispone di accesso completo all'istanza.

## Dipendenze

- [[epica-amministrazione-supporto-mfa|Epica — Amministrazione e supporto MFA]]
- [[mfa-service-instance|Istanza del servizio MFA]]

## Dubbi aperti

- Non sono documentati formato di export, retention complessiva e visibilità esatta di ogni campo per ruolo.

## Fonti

- [[mfa-operations|Operatività e supporto MFA]]
- [[mfa-service-instance|Istanza del servizio MFA]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

