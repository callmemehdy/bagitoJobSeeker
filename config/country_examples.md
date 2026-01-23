# Example configurations for different countries

> **Note:** LinkedIn post scraper uses only the `country` field for location filtering (not `suburbOrCity`). This provides broader nationwide results, which is especially useful for internships and remote opportunities.

## France - Internships & PFE (Current Config)
```json
{
    "searchTerms": [
        "Stage Ingénieur Informatique",
        "Internship Software Engineer",
        "PFE Développement Logiciel",
        "Stage Développeur",
        "PFE Informatique",
        "Stage Data Science",
        "Internship Python Developer",
        "Stage Machine Learning",
        "PFE Intelligence Artificielle",
        "Stage DevOps",
        "Internship Full Stack",
        "Stage Cybersécurité",
        "PFE Réseaux",
        "Stage Cloud Engineer",
        "Internship Backend Developer",
        "PFE Développement Web",
        "Stage Frontend",
        "Internship Data Engineer"
    ],
    "maxResults": 20,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Paris",
    "state": "",
    "country": "France",
    "countryCode": "FR",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "fr-FR",
        "spellVariant": "french",
        "currency": "EUR"
    },
    "use_selenium_for_linkedin": true
}
```

## Australia (Default)
```json
{
    "searchTerms": ["Software Engineer", "Python Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Sydney",
    "state": "NSW",
    "country": "Australia",
    "countryCode": "AU",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin", "indeed"],
    "locale": {
        "language": "en-AU",
        "spellVariant": "australian",
        "currency": "AUD"
    }
}
```

## United States
```json
{
    "searchTerms": ["Software Engineer", "Full Stack Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "San Francisco",
    "state": "CA",
    "country": "United States",
    "countryCode": "US",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin", "indeed"],
    "locale": {
        "language": "en-US",
        "spellVariant": "american",
        "currency": "USD"
    }
}
```

## United Kingdom
```json
{
    "searchTerms": ["Software Engineer", "Backend Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "London",
    "state": "",
    "country": "United Kingdom",
    "countryCode": "GB",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin", "indeed"],
    "locale": {
        "language": "en-GB",
        "spellVariant": "british",
        "currency": "GBP"
    }
}
```

## Canada
```json
{
    "searchTerms": ["Software Engineer", "DevOps Engineer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Toronto",
    "state": "ON",
    "country": "Canada",
    "countryCode": "CA",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin", "indeed"],
    "locale": {
        "language": "en-CA",
        "spellVariant": "canadian",
        "currency": "CAD"
    }
}
```

## Germany
```json
{
    "searchTerms": ["Software Engineer", "Backend Entwickler"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Berlin",
    "state": "",
    "country": "Germany",
    "countryCode": "DE",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "de-DE",
        "spellVariant": "german",
        "currency": "EUR"
    }
}
```

## France
```json
{
    "searchTerms": ["Ingénieur Logiciel", "Développeur Python"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Paris",
    "state": "",
    "country": "France",
    "countryCode": "FR",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "fr-FR",
        "spellVariant": "french",
        "currency": "EUR"
    }
}
```

## India
```json
{
    "searchTerms": ["Software Engineer", "Python Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Bangalore",
    "state": "Karnataka",
    "country": "India",
    "countryCode": "IN",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "en-IN",
        "spellVariant": "british",
        "currency": "INR"
    }
}
```

## Singapore
```json
{
    "searchTerms": ["Software Engineer", "Cloud Engineer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Singapore",
    "state": "",
    "country": "Singapore",
    "countryCode": "SG",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "en-SG",
        "spellVariant": "british",
        "currency": "SGD"
    }
}
```

## Morocco
```json
{
    "searchTerms": ["Software Engineer", "Développeur Web"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Casablanca",
    "state": "",
    "country": "Morocco",
    "countryCode": "MA",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "fr-MA",
        "spellVariant": "french",
        "currency": "MAD"
    }
}
```

## United Arab Emirates
```json
{
    "searchTerms": ["Software Engineer", "Data Scientist"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Dubai",
    "state": "",
    "country": "United Arab Emirates",
    "countryCode": "AE",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "en-AE",
        "spellVariant": "british",
        "currency": "AED"
    }
}
```

## Netherlands
```json
{
    "searchTerms": ["Software Engineer", "Backend Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Amsterdam",
    "state": "",
    "country": "Netherlands",
    "countryCode": "NL",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "nl-NL",
        "spellVariant": "dutch",
        "currency": "EUR"
    }
}
```

## Spain
```json
{
    "searchTerms": ["Ingeniero de Software", "Desarrollador Full Stack"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Madrid",
    "state": "",
    "country": "Spain",
    "countryCode": "ES",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "es-ES",
        "spellVariant": "spanish",
        "currency": "EUR"
    }
}
```

## Brazil
```json
{
    "searchTerms": ["Engenheiro de Software", "Desenvolvedor Python"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "São Paulo",
    "state": "SP",
    "country": "Brazil",
    "countryCode": "BR",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "pt-BR",
        "spellVariant": "portuguese",
        "currency": "BRL"
    }
}
```

## Japan
```json
{
    "searchTerms": ["Software Engineer", "ソフトウェアエンジニア"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Tokyo",
    "state": "",
    "country": "Japan",
    "countryCode": "JP",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "ja-JP",
        "spellVariant": "japanese",
        "currency": "JPY"
    }
}
```

## South Korea
```json
{
    "searchTerms": ["Software Engineer", "소프트웨어 엔지니어"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Seoul",
    "state": "",
    "country": "South Korea",
    "countryCode": "KR",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "ko-KR",
        "spellVariant": "korean",
        "currency": "KRW"
    }
}
```

## Switzerland
```json
{
    "searchTerms": ["Software Engineer", "DevOps Engineer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Zurich",
    "state": "",
    "country": "Switzerland",
    "countryCode": "CH",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "de-CH",
        "spellVariant": "german",
        "currency": "CHF"
    }
}
```

## Sweden
```json
{
    "searchTerms": ["Software Engineer", "Backend Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Stockholm",
    "state": "",
    "country": "Sweden",
    "countryCode": "SE",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin"],
    "locale": {
        "language": "sv-SE",
        "spellVariant": "swedish",
        "currency": "SEK"
    }
}
```

## New Zealand
```json
{
    "searchTerms": ["Software Engineer", "Full Stack Developer"],
    "maxResults": 50,
    "SortBy": "KeywordsRelevance",
    "suburbOrCity": "Auckland",
    "state": "",
    "country": "New Zealand",
    "countryCode": "NZ",
    "dateRange": 31,
    "requireEmail": false,
    "platforms": ["linkedin", "seek"],
    "locale": {
        "language": "en-NZ",
        "spellVariant": "british",
        "currency": "NZD"
    }
}
```

## Configuration Fields Explained

## Field Descriptions

### Required Fields:
- **searchTerms**: Array of job titles to search for
- **maxResults**: Maximum number of jobs per search term
- **suburbOrCity**: City name (for display/reference - LinkedIn uses `country` only)
- **country**: Full country name (used by LinkedIn scraper for location filtering)
- **countryCode**: ISO 2-letter country code
- **platforms**: Array of platforms to use (`["linkedin"]`, `["indeed"]`, or both)

### Locale Settings:
- **language**: ISO language-region code (e.g., `en-US`, `en-GB`, `fr-FR`)
- **spellVariant**: Spelling variant for cover letters
  - `"american"` - optimize, color, favor
  - `"british"` - optimise, colour, favour
  - `"australian"` - optimise, colour, favour (same as British)
  - `"canadian"` - mix of British and American
  - `"french"` - optimiser, couleur
  - `"german"`, `"spanish"`, etc. - for other languages

### Optional Fields:
- **state**: State/province (use empty string `""` if not applicable)
- **dateRange**: Jobs posted within last N days (default: 31)
- **requireEmail**: Filter jobs that have email addresses
- **SortBy**: Sort order (`"KeywordsRelevance"` or `"ListedDate"`)
- **use_selenium_for_linkedin**: Enable LinkedIn post scraping (default: false)

### Important Notes:
- **LinkedIn post scraper** uses only the `country` field for broad nationwide results
- The `suburbOrCity` field is used by other scrapers (Indeed, Seek) and for reference
- For internships and PFE, use country-level search for maximum coverage

## Popular Search Terms by Category

### Internships (France)
```json
"searchTerms": [
    "Stage Ingénieur Informatique",
    "Stage Développeur",
    "Stage Data Science",
    "PFE Informatique",
    "PFE Intelligence Artificielle",
    "Internship Software Engineer"
]
```

### Full-time (General)
```json
"searchTerms": [
    "Software Engineer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Engineer"
]
```

### Senior Roles
```json
"searchTerms": [
    "Senior Software Engineer",
    "Tech Lead",
    "Engineering Manager",
    "Software Architect",
    "Principal Engineer"
]
```

## Spell Variants Supported

| Variant | Example Words | Used In |
|---------|---------------|---------|
| **american** | optimize, color, center, labor | USA |
| **british** | optimise, colour, centre, labour | UK, UAE, India, Singapore, NZ |
| **australian** | optimise, colour, centre (same as British) | Australia, NZ |
| **canadian** | colour, organize (mix) | Canada |
| **french** | optimiser, couleur | France, Morocco |
| **german** | optimieren, farbe | Germany, Switzerland, Austria |
| **spanish** | optimizar, color | Spain, Latin America |
| **portuguese** | otimizar, cor | Brazil, Portugal |
| **dutch** | optimaliseren, kleur | Netherlands, Belgium |

## Platform Availability by Country

| Country | LinkedIn | Indeed | Seek | Notes |
|---------|----------|--------|------|-------|
| Australia | ✓ | ✓ | ✓ | Seek is AU/NZ specific |
| New Zealand | ✓ | ✓ | ✓ | Seek is AU/NZ specific |
| USA | ✓ | ✓ | ✗ | |
| UK | ✓ | ✓ | ✗ | |
| Canada | ✓ | ✓ | ✗ | |
| Germany | ✓ | ✗ | ✗ | LinkedIn best option |
| France | ✓ | ✗ | ✗ | LinkedIn best option |
| India | ✓ | ✗ | ✗ | LinkedIn best option |
| Singapore | ✓ | ✗ | ✗ | LinkedIn best option |
| Morocco | ✓ | ✗ | ✗ | LinkedIn best option |
| UAE | ✓ | ✗ | ✗ | LinkedIn best option |
| Netherlands | ✓ | ✗ | ✗ | LinkedIn best option |
| Spain | ✓ | ✗ | ✗ | LinkedIn best option |
| Brazil | ✓ | ✗ | ✗ | LinkedIn best option |
| Japan | ✓ | ✗ | ✗ | LinkedIn best option |
| South Korea | ✓ | ✗ | ✗ | LinkedIn best option |
| Switzerland | ✓ | ✗ | ✗ | LinkedIn best option |
| Sweden | ✓ | ✗ | ✗ | LinkedIn best option |

**Note**: ✓ = Working, ✗ = Not available

## Usage

1. Copy the appropriate config example above
2. Paste it into `config/run_config.json`
3. Modify search terms and location as needed
4. Run: `make run FIRST_NAME=YourName`

The application will automatically use:
- Correct spelling variant for cover letters
- Correct country/location for job search
- Appropriate job platforms for that country
