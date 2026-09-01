# Presentare e completare la MFA Prompt

## Metadati Requisiti
- Tipo requisito: User story
- Epica: Erogazione dei challenge MFA
- Priorita: Non indicata
- Stato: Parziale
- Fase: Non indicata
- Fonte wiki: [[mfa-prompt-dialog|MFA Prompt Dialog]]

## Descrizione

L'applicazione crea una sessione Prompt, indirizza l'utente alla UI standard e valida il completamento restituito dal servizio.

## User story

Come utente di un'applicazione già autenticato con il primo fattore, voglio scegliere e completare una modalità MFA disponibile, così da riconvalidare la mia identità nel flusso applicativo.

## Criteri di accettazione

- Given una richiesta valida, When l'applicazione crea la Prompt, Then il servizio restituisce un `mfaUiUrl` valido per un minuto.
- Given recapiti e metodi disponibili, When la UI viene aperta, Then mostra soltanto le opzioni supportate dai dati forniti e dalla configurazione dell'utente.
- Given un completamento riuscito, When il servizio effettua il redirect, Then include `mfaCompletionId`.
- Given `mfaCompletionId`, When l'applicazione valida il token, Then ottiene stato, modalità e identificativo della sessione.
- Given un errore documentato, When il flusso termina, Then viene restituito il relativo `errorCode` all'URI di errore o di ritorno configurato.

## Regole funzionali

- Un authenticator deve essere verificato prima di essere mostrato come opzione nella Prompt.
- Il timeout è configurato sull'istanza; il valore predefinito documentato è cinque minuti.

## Dipendenze

- [[epica-erogazione-challenge-mfa|Epica — Erogazione dei challenge MFA]]
- [[mfa-security-controls|Controlli di sicurezza MFA]]

## Dubbi aperti

- Non è specificato il comportamento della UI per tutte le combinazioni di metodi indisponibili.

## Fonti

- [[mfa-prompt-dialog|MFA Prompt Dialog]]
- `.codex_sources/source-ssc-mfa-developer-guide-010926-122942-4f24c338d2.txt`

