# Agent: Graphify Second Brain

Questo progetto usa Graphify come motore operativo del second brain.

## Regole
- Per domande su struttura, relazioni o contenuti del progetto, consulta prima `knowledge/graphify-out/graph.json` con `graphify query`, `graphify path` o `graphify explain` quando il grafo esiste.
- Per navigazione ampia usa `knowledge/wiki/_index.md`, che viene sincronizzato da `knowledge/graphify-out/wiki/index.md`.
- Non usare prompt applicativi custom per generare la wiki: la pipeline supportata e' la skill `/graphify <raw> --wiki` dentro la CLI. La modalita' `graphify extract` + `graphify export wiki` e' solo fallback headless con API key.
- Dopo modifiche alle fonti in `knowledge/raw/`, ricostruisci tramite la web app o con Graphify e poi sincronizza `knowledge/wiki/`.
- Se una informazione non e' presente nella wiki o nel grafo Graphify, dichiarala come mancante invece di inventarla.
