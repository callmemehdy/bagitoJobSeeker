# BagitoJobSeeker - Automated Job Application Bot 

An intelligent automation system that scrapes LinkedIn posts and job listings, generates personalized cover letters using AI, and automatically sends job applications via email.

##  Features

- **LinkedIn Post Scraping**: Scrapes LinkedIn posts searching for job opportunities with contact emails
- **Multi-Platform Support**: LinkedIn posts, Indeed, and Seek job boards
- **Smart Search**: Uses optimized keywords like "hiring email", "recruiting contact" to find posts with contact info
- **AI-Generated Content**: Creates personalized cover letters using Gemini or MetaAI
- **Smart Filtering**: Resume-based job matching with configurable similarity scores
- **Email Automation**: Automated application submission via Gmail
- **Seek Integration**: Direct application on Seek platform (when logged in)
- **Application Tracking**: Prevents duplicate applications
- **Multi-Language Support**: Automatic spelling conversion based on locale (British, American, French, etc.)
- **Zero Cost Option**: Works without Apify API credits

---

##  Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd bagitoJobSeeker

# Install dependencies
make install
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

**Required in `.env`:**

```bash
# Email Configuration (Gmail)
EMAIL_ADDRESS="your@gmail.com"
EMAIL_APP_PASSWORD="your_gmail_app_password"  # See setup guide below

# LinkedIn Credentials (Required for post scraping)
LINKEDIN_EMAIL="your_linkedin_email@example.com"
LINKEDIN_PASSWORD="your_linkedin_password"

# Optional: Gemini API (or will use MetaAI)
GEMINI_KEY="your_gemini_api_key"

# Optional: Apify API (or will use custom scraper)
APIFY_KEY="your_apify_api_key"
```

**Important:** You need a Gmail App Password (not your regular password)

**How to get Gmail App Password:**

1. Enable 2-Factor Authentication on your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Other (Custom name)"
4. Name it: "Job Application Bot"
5. Click "Generate"
6. Copy the 16-character password (no spaces)
7. Add it to your `.env` file as `EMAIL_APP_PASSWORD`

### 3. Add Your Resume

Place your resume at:
```
application_pipeline/application_materials/resume.pdf
```

### 4. Configure Job Search

Edit `config/run_config.json`:

```json
{
  "searchTerms": [
    "hiring email",
    "recruiting contact",
    "internship apply email",
    "software engineer opportunity contact",
    "AI jobs email"
  ],
  "maxResults": 20,
  "suburbOrCity": "Your City",
  "country": "Your Country",
  "countryCode": "XX",
  "platforms": ["linkedin"],
  "locale": {
    "language": "en-US",
    "spellVariant": "american",
    "currency": "USD"
  }
}
```

**Note:** The scraper searches LinkedIn posts for job opportunities. Use search terms that are likely to appear in posts where recruiters share contact emails.

### 5. Test LinkedIn Post Scraper

Test the new post scraper:

```bash
python test_linkedin_post_scraper.py
```

This will:
- Open a browser window (set `headless=False` to watch)
- Log you into LinkedIn
- Search for posts with emails
- Show results in console
- Save results to `linkedin_posts_with_emails.json`

### 6. Test Configuration

```bash
# Test email setup
make test-email

# Test the complete pipeline
make run FIRST_NAME=YourName
```

### 7. Run the Application

```bash
# Run with your first name
make run FIRST_NAME=YourName
```

---

##  Available Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make test-email        # Test Gmail configuration
make check-status      # Check application status
make run FIRST_NAME=X  # Run the application
make reset-applied     # Reset applied jobs tracker
make clean             # Clean up temporary files
```

---

##  How It Works

### LinkedIn Post Scraping

The bot now scrapes **LinkedIn posts** instead of job cards:

1. **Logs into LinkedIn** using your credentials
2. **Searches for posts** using keywords like "hiring email", "recruiting contact"
3. **Finds posts with emails** by parsing post content
4. **Extracts contact information** (emails, author, link, timestamp)
5. **Filters results** to remove non-personal emails (noreply@, linkedin.com, etc.)
6. **Returns jobs** with valid contact emails for the application pipeline

**Why LinkedIn Posts?**
- Recruiters often share job opportunities on LinkedIn posts
- Posts frequently include contact emails for direct applications
- More personal than formal job postings
- Higher response rates

**Search Term Tips:**
- Use "hiring email", "recruiting contact" for better results
- Combine job type with "apply email": "AI internship apply email"
- Include "opportunity contact" or "jobs email" in searches
- Avoid generic terms like just "software engineer"

---

##  Configuration Options

### Command Line Arguments

```bash
# Basic usage
python3 main.py --first_name YourName

# With custom options
python3 main.py \
  --first_name YourName \
  --min_score 0.0 \
  --model gemini-2.5-flash \
  --mail_protocol gmail.com
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--first_name` | Your first name (required) | - |
| `--resume_pdf_path` | Path to resume PDF | `application_pipeline/application_materials/resume.pdf` |
| `--cover_letter_path` | Cover letter save location | `application_pipeline/application_materials/cover_letter.pdf` |
| `--config_path` | Job search configuration | `config/run_config.json` |
| `--applied_path` | Application tracking file | `application_pipeline/application_materials/applied.json` |
| `--min_score` | Minimum similarity score (0.0-1.0) | `0.0` (disabled) |
| `--model` | Gemini model to use | `gemini-2.5-flash` |
| `--mail_protocol` | Email provider | `gmail.com` |

---

##  Troubleshooting

### No Posts with Emails Found?

**This is normal!** LinkedIn posts rarely contain public email addresses.

**Tips:**
- Use more specific search terms: "hiring email", "recruiting contact"
- Try location-specific searches: "hiring email [your city]"
- Look for recruiter/HR posts rather than general job postings
- Consider supplementing with job board scrapers (Indeed, Seek)

### LinkedIn Login Issues?

**If stuck on login page:**
```bash
# Delete old cookies and login fresh
rm ./credentials/linkedin_cookies.json
python test_linkedin_post_scraper.py
```

**If security challenge appears:**
- Run with `headless=False` to complete challenge manually
- Complete the challenge in the browser
- Press Enter to continue

### Email Authentication Failed?

You need a Gmail App Password, not your regular password.

**Setup steps:**
1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character code to `.env`

### No Applications Sent?

**Check:**
1. Posts were found with emails (check logs)
2. Gmail App Password is configured correctly
3. `applied.json` doesn't already contain the jobs
4. Review logs for error messages

**Quick Fixes:**
```bash
# Reset applied jobs
make reset-applied

# Test email configuration
make test-email

# Test LinkedIn post scraper
python test_linkedin_post_scraper.py
```

---

##  Project Structure

```
bagitoJobSeeker/
 application_pipeline/       # Application processing
    application_materials/  # Resume, cover letters, tracking
    job_application_pipeline.py
 common/                     # Shared utilities
 config/                     # Configuration files
    args.py                 # CLI arguments
    run_config.json         # Job search config
 credentials/                # LinkedIn cookies
 docs/                       # Documentation
 integrations/               # External service integrations
    agent.py                # AI agents (Gemini/MetaAI)
    mail_handler.py         # Email client
    seek_client.py          # Seek automation
 scrapers/                   # Job scraping
    scraper.py              # Main scraper (Apify + fallback)
    multi_platform_scraper.py # Multi-platform custom scraper
    linkedin_post_scraper.py # LinkedIn post scraper (NEW)
    seek_scraper.py         # Seek-specific scraper
 test_email_config.py        # Email testing
 test_linkedin_post_scraper.py # LinkedIn post scraper testing
 check_application_status.py # Status checker
 main.py                     # Main entry point
 Makefile                    # Build commands
 README.md                   # This file
```

---

##  Notes

- **Rate Limits**: 
  - Gemini free tier: 20 requests/day (use MetaAI for unlimited)
  - Apify free tier: Monthly limits (custom scraper used as fallback)
  - MetaAI: 30-second delay between requests (built-in)
  - LinkedIn: Be mindful of scraping frequency to avoid rate limits

- **Email Sending**: 
  - Gmail has daily send limits (~500 emails/day)
  - Consider spacing out applications
  - Monitor your Gmail Sent folder

- **LinkedIn Posts**:
  - Posts with emails are rare (expect low results)
  - Best for niche/specialized roles where recruiters share contact info
  - Supplement with traditional job board scrapers for better coverage

---

##  Tips

1. **Start Small**: Test with the post scraper first to see results
2. **Check Sent Folder**: Verify emails are being sent
3. **Monitor Logs**: Watch for errors and successes
4. **Review Applications**: Track progress in `applied.json`
5. **Update Search Terms**: Adjust to find posts with emails
6. **Combine Approaches**: Use both post scraping and job board scraping

---

**Made with  for job seekers**

 Good luck with your job search! 
