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

## CI-vianmääritys: `RESULTS_REPO_TOKEN is not set`

Jos GitHub Actions -lokissa näkyy viesti
`RESULTS_REPO_TOKEN is not set. Skipping upload.`, token ei ole saatavilla siinä
repossa, jossa workflow ajetaan.

Tärkeä huomio:
- Secretit **eivät** siirry automaattisesti template-/parent-reposta forkkeihin.
- Secretit **eivät** tule käyttöön toisesta (kohde-)reposta, vaikka upload menisikin sinne.

Korjaus:
1. Aseta secret `RESULTS_REPO_TOKEN` (tai vaihtoehtoisesti `AUTOGRADING_RESULTS_REPO_TOKEN`)
   **siihen repositoryyn, jossa autograding-workflow pyörii**.
2. Varmista, että tokenilla on oikeudet kirjoittaa kohderepoon
   (`Contents: Read and write`).
3. Aja workflow uudelleen `push`-eventillä (upload-vaihe ajetaan vain pushissa).
