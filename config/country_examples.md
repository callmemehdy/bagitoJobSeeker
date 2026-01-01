# Example configurations for different countries

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

## Configuration Fields Explained

### Required Fields:
- **searchTerms**: Array of job titles to search for
- **maxResults**: Maximum number of jobs per search term
- **suburbOrCity**: City or location to search in
- **country**: Full country name
- **countryCode**: ISO 2-letter country code
- **platforms**: Array of platforms to use (`["linkedin"]`, `["indeed"]`, or both)

### Locale Settings:
- **language**: ISO language-region code (e.g., `en-US`, `en-GB`)
- **spellVariant**: Spelling variant for cover letters
  - `"american"` - optimize, color, favor
  - `"british"` - optimise, colour, favour
  - `"australian"` - optimise, colour, favour (same as British)
  - `"canadian"` - mix of British and American
  - `"german"`, `"french"`, etc. - for non-English

### Optional Fields:
- **state**: State/province (use empty string `""` if not applicable)
- **dateRange**: Jobs posted within last N days
- **requireEmail**: Filter jobs that have email addresses
- **SortBy**: Sort order (`"KeywordsRelevance"` or `"ListedDate"`)

## Spell Variants Supported

| Variant | Example Words | Used In |
|---------|---------------|---------|
| **american** | optimize, color, center, labor | USA |
| **british** | optimise, colour, centre, labour | UK, Australia, NZ, India, Singapore |
| **australian** | optimise, colour, centre (same as British) | Australia, NZ |
| **canadian** | colour, organize (mix) | Canada |

## Platform Availability by Country

| Country | LinkedIn | Indeed | Seek | Notes |
|---------|----------|--------|------|-------|
|  Australia |  |  |  | Seek is AU/NZ specific |
|  USA |  |  |  | |
|  UK |  |  |  | |
|  Canada |  |  |  | |
|  Germany |  |  |  | LinkedIn best option |
|  France |  |  |  | LinkedIn best option |
|  India |  |  |  | LinkedIn best option |
|  Singapore |  |  |  | |

**Note**:  = Working,  = Partial support,  = Not available

## Usage

1. Copy the appropriate config example above
2. Paste it into `config/run_config.json`
3. Modify search terms and location as needed
4. Run: `make run FIRST_NAME=YourName`

The application will automatically use:
- Correct spelling variant for cover letters
- Correct country/location for job search
- Appropriate job platforms for that country
