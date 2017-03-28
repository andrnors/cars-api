# cars

API for å hente informasjon om: 
  - "Alle" sivile politibiler i Norge"
  - Hente mer informasjon om hver enkelt sivile politibil i Norge. Krever eksakt registreringsnummer
  - Hente informasjon om alle kjøretøy i Norge. Krever eksakt registreringsnummer for hver bil du sjekker.
  - Sjekker også om et kjøretøy er meldt stjålet.
  
  JSON-filene i prosjektet er eksempel output på hva de forskjellige funksjonene returnerer.
  
  
#  For å kjøre server:
- $ export FLASK_APP=scrape.py
- $ flask run
 * Running on http://127.0.0.1:5000/
 
- Hvis du bruker Windows, må du bruke 'set' istedenfor 'export'.

Evt. kan du bruke python -m flask:
- $ export FLASK_APP=scrape.py
- $ python -m flask run
 * Running on http://127.0.0.1:5000/
