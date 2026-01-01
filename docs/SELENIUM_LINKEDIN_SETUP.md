# LinkedIn Selenium Scraping Setup Guide

## Overview

LinkedIn uses JavaScript to load content dynamically (Single Page Application). Regular HTTP scrapers can't execute JavaScript, so we use **Selenium** to control a real Chrome browser.

## Setup Instructions

### 1. Install Dependencies (Already Done ✅)

```bash
uv add selenium webdriver-manager
```

### 2. Add LinkedIn Credentials to `.env`

```bash
# LinkedIn Credentials (for Selenium scraping)
LINKEDIN_EMAIL="your_email@example.com"
LINKEDIN_PASSWORD="your_password"
```

⚠️ **Security Note**: Keep your `.env` file private and never commit it to Git!

### 3. Enable LinkedIn in Config

Edit `config/run_config.json`:

```json
{
  "platforms": ["seek", "indeed", "linkedin"],
  "use_selenium_for_linkedin": true
}
```

### 4. Test the Setup

```bash
# Test LinkedIn scraper (opens visible browser)
make test-linkedin

# Or run directly
uv run python3 test_linkedin_scraper.py
```

## How It Works

1. **Opens Chrome Browser**: Selenium launches Chrome in headless mode (no visible window in production)
2. **Logs Into LinkedIn**: Uses your credentials to authenticate
3. **Saves Session**: Stores cookies for faster future logins
4. **Searches Jobs**: Navigates to job search pages
5. **Scrolls & Extracts**: Scrolls to load more jobs and extracts:
   - Job title, company, location
   - Full job descriptions
   - Email addresses (if available)
   - Apply links

## Usage

### Enable for Production

In `config/run_config.json`:
```json
{
  "platforms": ["seek", "indeed", "linkedin"],
  "use_selenium_for_linkedin": true,
  "maxResults": 50
}
```

Then run normally:
```bash
make run FIRST_NAME=YourName
```

### Test Manually

```python
from scrapers.linkedin_selenium_scraper import LinkedInSeleniumScraper
import os
from dotenv import load_dotenv

load_dotenv()

scraper = LinkedInSeleniumScraper(
    email=os.getenv('LINKEDIN_EMAIL'),
    password=os.getenv('LINKEDIN_PASSWORD'),
    headless=True  # False to see browser
)

jobs = scraper.scrape_jobs("Software Engineer", "Sydney", max_results=10)
scraper.close()
```

## Features

### Automatic Cookie Management
- First run: Logs in and saves cookies
- Future runs: Uses saved cookies (faster)
- Auto-refresh if cookies expire

### Headless Mode
- Production: `headless=True` (no visible browser)
- Testing: `headless=False` (see what's happening)

### Verification Handling
If LinkedIn requires verification:
- Browser stays open for 60 seconds
- Complete verification manually
- Scraper continues automatically

## Troubleshooting

### Chrome Driver Not Found
```bash
# Reinstall webdriver-manager
uv add --upgrade webdriver-manager
```

### Login Failed
1. Check credentials in `.env`
2. Try manual login on LinkedIn website first
3. Check if 2FA is enabled (may need extra steps)

### No Jobs Found
1. Verify search terms in config
2. Check location spelling
3. Try broader search terms

### Browser Crashes
1. Update Chrome: `sudo apt update && sudo apt upgrade google-chrome-stable`
2. Increase system memory
3. Reduce `maxResults` in config

## Performance

- **Speed**: ~2-5 seconds per job (includes scrolling, clicking)
- **Recommended**: Set `maxResults: 20-50` to avoid long runs
- **Memory**: Chrome uses ~500MB RAM

## Comparison

| Platform | Method | Speed | Emails Found |
|----------|--------|-------|--------------|
| Indeed | BeautifulSoup | Fast ⚡ | Few |
| Seek | BeautifulSoup | Fast ⚡ | Some |
| LinkedIn | Selenium | Slower 🐢 | More |

## Best Practices

1. **Start Small**: Test with 5-10 jobs first
2. **Monitor Logs**: Check for scraping errors
3. **Rotate Platforms**: Don't scrape LinkedIn too frequently
4. **Respect Limits**: Don't abuse LinkedIn's platform
5. **Use Headless Mode**: Enable in production for efficiency

## Configuration Options

```json
{
  "platforms": ["seek", "indeed", "linkedin"],
  "use_selenium_for_linkedin": true,
  "maxResults": 50,
  "searchTerms": ["Software Engineer", "Python Developer"],
  "suburbOrCity": "Sydney"
}
```

## Files Created

- `credentials/linkedin_cookies.json` - Saved session cookies for faster login
- `application_pipeline/application_materials/applied.json` - Tracks applications sent

## Next Steps

1. ✅ Add credentials to `.env`
2. ✅ Enable in `run_config.json`
3. ✅ Run: `make test-linkedin`
4. ✅ Verify jobs are found
5. ✅ Run full pipeline: `make run FIRST_NAME=YourName`

## Support

- **Documentation**: [docs/LINKEDIN_SCRAPING_GUIDE.md](./LINKEDIN_SCRAPING_GUIDE.md)
- **Issues**: Check logs for detailed error messages
- **Selenium Docs**: https://selenium-python.readthedocs.io/
