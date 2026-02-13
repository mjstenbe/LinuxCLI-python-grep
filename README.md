# LinuxCLI-python-grep

Projekti harjoituksia Linux-komentoriviltä käyttäen `grep`, `awk`, `sed` jne.

Uusi hakemistorakenne:

- `src/` - lähdekoodi ja paketti
- `data/` - lähdeaineistot
- `data/tasks/` - tehtävä- ja esimerkkikomennot
- `configs/` - tallennettu tila (esim. `tila.json`)
- `output/` - generoituja tuloksia (esim. `results.json`)
- `tools/` - kehitystyökalut
- `harjoitus.py` - CLI/harjoitusskripti (sijoitettu juureen säilytettäväksi)

## Autograding-repon yhteenvetotaulukko

Aja tämä skripti **autograding-repositoryn juuressa** (siellä missä JSON-tulokset ovat).
Skripti odottaa tiedostonimen muodossa `opiskelija-YYYY-MM-DDTHH-MM-SS.json` ja ottaa
kustakin opiskelijasta uusimman tuloksen mukaan.

```bash
python3 tools/summarize_autograding_results.py --results-dir . --output SUMMARY.md
```

Skripti lukee kentät `score` ja `total` ja tuottaa Markdown-taulukon, jossa näkyy opiskelija,
pistekertymä ja viimeisimmän tuloksen aikaleima.
