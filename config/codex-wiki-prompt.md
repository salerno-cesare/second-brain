Usa la skill Agent locale `{skill_name}` come workflow primario per la LLM Wiki.

Prima di operare:
1. Leggi `{skill_path}/SKILL.md`.
2. Quando la skill rimanda ai template, usa `{skill_path}/references/`.
3. Applica la skill come fonte operativa principale per ingest/compile/lint della wiki.

Modalita corrente: {mode}

Obiettivo:
{task}

Lingua della wiki:
{language_instruction}

Cartelle relative alla working directory:
- raw/: fonti originali caricate dall'utente. Non modificarle.
- .codex_sources/: estratti testuali preparati dall'app a partire da raw/. Usali come vista normalizzata delle fonti.
- wiki/: knowledge base Markdown da creare e mantenere.
- wiki/togaf/: vista TOGAF locale derivata solo dalla LLM Wiki principale.
- wiki/requisiti-funzionali/: vista locale dei soli requisiti software funzionali.

Fonti preparate per questa esecuzione:
{source_list}

Adattamenti locali rispetto alla skill:
- Il fetch in raw/ e' gia' gestito dall'app. Per mode=compile esegui la parte Compile della skill usando .codex_sources/ e le fonti preparate, senza modificare raw/.
- Mantieni le convenzioni esistenti della app: wiki/_index.md e wiki/_log.md al posto di wiki/index.md e wiki/log.md.
- Mantieni pagine principali flat in wiki/*.md e link interni in formato Obsidian `[[slug|Titolo]]`.
- Non modificare wiki/_config.md.
- Non modificare codice applicativo, database, raw/ o .codex_sources/.
- Se mode=compile, aggiorna anche wiki/requisiti-funzionali/ con soli requisiti software funzionali supportati.
- Se mode=togaf, non usare raw/ o .codex_sources/: parti da wiki/_index.md, wiki/_log.md e dalle pagine principali rilevanti; aggiorna solo wiki/togaf/.
- Se mode=lint, applica la parte Lint della skill alle convenzioni locali e segnala contraddizioni o link dubbi senza inventare contenuto.

Regole anti-allucinazione:
- Scrivi solo informazioni supportate dalle fonti preparate o gia' presenti nella wiki.
- Se le fonti non bastano, registra il gap in "Contraddizioni o dubbi" o "Dubbi aperti" e in wiki/_log.md.
- In caso di conflitto tra fonti o pagine, conserva la contraddizione con attribuzione invece di risolverla per deduzione.

Struttura artefatti TOGAF di riferimento, da usare solo se mode=togaf:
{togaf_reference}

Output finale richiesto:
- Riepilogo breve di pagine create, aggiornate, unite o divise.
- Dubbi residui, contraddizioni aperte e fonti mancanti.
