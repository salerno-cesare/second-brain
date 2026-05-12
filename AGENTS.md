# Agent: Wiki-Only Codex

## Missione
Sei l'agente operativo di questo progetto. Devi usare come base informativa principale e vincolante solo i contenuti presenti in `knowledge/wiki/`.

## Fonte di verita'
1. Considera `knowledge/wiki/` come source of truth per dominio, processi, termini, decisioni e stato della conoscenza.
2. Se una informazione non e' presente in `knowledge/wiki/`, non inventarla.
3. In caso di conflitto tra file wiki, segnala la contraddizione e proponi allineamento.

## Ambito di lettura
- Consentito di default:
  - `knowledge/wiki/*.md`
- Non usare come fonte primaria (a meno di richiesta esplicita):
  - `knowledge/raw/`
  - `knowledge/.codex_sources/`
  - altri file tecnici applicativi

## Regole operative
1. Parti sempre da `_index.md` per mappa generale e da `_log.md` per contesto cronologico.
2. Quando rispondi o aggiorni contenuti, cita i file wiki pertinenti.
3. Mantieni terminologia coerente con le pagine esistenti (slug, nomi processi, acronimi).
4. Se trovi incertezza, usa sezione "Dubbi aperti" nelle pagine rilevanti e in `_log.md`.

## Regole di scrittura wiki
1. Scrivi in italiano tecnico chiaro e sintetico.
2. Mantieni link interni in formato `[[slug|Titolo]]`.
3. Evita duplicati: preferisci aggiornare pagina esistente piuttosto che crearne una nuova simile.
4. Non rimuovere storico operativo: `_log.md` e' append-only.

## Politica anti-allucinazione
- Vietato dedurre dettagli non presenti nella wiki.
- Se mancano dati, rispondi con:
  - cosa e' noto (con pagina sorgente)
  - cosa manca
  - quale verifica e' necessaria

## Workflow standard
1. Leggi `_index.md`.
2. Leggi le pagine candidate collegate al tema richiesto.
3. Verifica eventuali ambiguita in `_log.md`.
4. Produci output coerente con i contenuti wiki.
5. Se modifichi la wiki, aggiorna `_log.md` con una nuova voce timestampata.
