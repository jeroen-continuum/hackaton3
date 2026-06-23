Om de hackathon-teams een vliegende start te geven, hebben we gekeken naar bronnen die **geen blokkades** (zoals zware
CAPTCHA's of IP-bans) opwerpen.

In plaats van traditioneel "web scraping" (wat vaak traag en kwetsbaar is), focust dit overzicht op **Open Data
Downloads, Gratis Developer API's, en legitiem scrapable alternatieven** voor elk specifiek requirement.

---

## Programmeerbare & Scrapable Bronnen per Requirement

| Requirement                      | Specifieke Data                       | Toegestane Scrapable / API Bron             | Hoe dit werkt voor het Hackathon-team                                                                                                                                                                                           |
|----------------------------------|---------------------------------------|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. Regio (België)**            | Adres, status (actief)                | **KBO Open Data (FOD Economie)**            | **Geen live scraping nodig:** Download het wekelijkse XML/CSV-pakket. Dit bevat *alle* actieve Belgische bedrijven. Laad dit in een lokale database (bijv. SQLite of PostgreSQL) en je hebt direct je basislijst.               |
| **2. Bedrijfsgrootte (100-500)** | Aantal werknemers                     | **NBB (Nationale Bank) Open Data API**      | De NBB heeft een open API (*Standardized Data* / XBRL) waar je op basis van het ondernemingsnummer (uit de KBO-lijst) direct de 'Sociale Balans' kunt opvragen. Dit geeft direct het exacte aantal FTE's terug in JSON-formaat. |
| **3. Focussectoren**             | NACE-codes (Finance, Industrie, etc.) | **KBO Open Data (FOD Economie)**            | Zit verwerkt in dezelfde gratis KBO-download als de Regio. Filter programmatisch op de eerste twee cijfers van de NACE-code (bijv. `64` en `65` voor financiële diensten).                                                      |
| **4. Financiële Kracht**         | EBITDA / Winst (`code 9901`)          | **NBB (Nationale Bank) Open Data API**      | Via dezelfde JSON/XBRL API van de Nationale Bank kun je de winst-en-verliesrekening uitlezen. Laat een script automatisch de EBITDA berekenen om te zien of ze het budget (€150k+) hebben.                                      |
| **5. IT-Volwassenheid**          | Grootte IT-team & huidige tech-stack  | **Wappalyzer API** / **BuiltWith API** <br> 

<br>*(beide hebben gratis test-credits)* | Scraping van de bedrijfswebsite zelf duurt te lang. Schiet de domeinnaam naar
deze API's; je krijgt direct een JSON terug met alle gebruikte software. Gebruiken ze verouderde systemen? Dan is de
impact/nood hoog. |
| **6. Beslisser (Buyer)** | Namen/rollen van CEO, CFO, Directors | **Apollo.io API** of **Hunter.io API** | Aangezien
LinkedIn scrapen verboden is, zijn deze B2B-databases het perfecte alternatief. Via hun gratis API-tiers kun je zoeken
op `bedrijfsnaam` + `CFO` of `CEO`. Je krijgt direct de naam, functietitel en vaak het zakelijke e-mailadres terug. |
| **7. Uitsluitingen** | Filteren van zorg, overheid, enterprise | **KBO & NBB Open Data** | Schrijf een
uitsluitingsfilter (blacklisting) in de code. Filter NACE-codes die beginnen met `86` (gezondheidszorg) of sluit
bedrijven uit met een balanstotaal dat te enterprise-achtig is. |
| **8. Buyer Intent** | Actieve vacatures (groeipijn/IT-nood) | **VDAB Developer API** of **Adzuna API** | Registreer
gratis op het VDAB-ontwikkelaarsportaal. Je kunt via hun API live zoeken naar openstaande vacatures per bedrijf. Zoekt
een mid-market bedrijf al maanden een IT-manager? Bingo, dat is een hoge *Buyer Intent*. |

---

## 💡 Aanbevolen Architectuur voor de Hackathon

Als de teams slim zijn, bouwen ze de pipeline als volgt op (volledig geautomatiseerd en legaal):

1. **Stap 1 (De Vijver):** Download de **KBO Open Data** en filter in Python direct op Belgische bedrijven in de juiste
   NACE-sectoren. Dit is je ruwe lijst.
2. **Stap 2 (De Filter):** Loop door deze lijst heen met een script dat de **NBB API** aanroept. Filter er alle
   bedrijven uit die *niet* tussen de 100-500 werknemers hebben of een te lage EBITDA draaien.
3. **Stap 3 (De Verrijking):** De overgebleven bedrijven (de shortlist) worden automatisch verrijkt via de **Apollo.io
   API** (voor de namen van de CFO/CEO) en de **VDAB API** (om te kijken of ze IT-vacatures hebben openstaan).
4. **Stap 4 (De Heatmap):** Geef elk bedrijf punten op basis van deze metrics. De top 10 rolt er zo automatisch uit voor
   Geert zijn **Rolling 10**!