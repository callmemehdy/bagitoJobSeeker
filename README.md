# BagitoJobSeeker - Automated Job Application Bot 

An intelligent automation system that scrapes job listings from Seek, generates personalized cover letters using AI, and automatically sends job applications via email.

##  Features

- **Multi-Platform Scraping**: Scrapes from LinkedIn, Indeed, and Seek automatically
- **Job Scraping**: Uses Apify API or custom scrapers (LinkedIn/Indeed/Seek) as fallback
- **AI-Generated Content**: Creates personalized cover letters using Gemini or MetaAI
- **Smart Filtering**: Resume-based job matching with configurable similarity scores
- **Email Automation**: Automated application submission via Gmail
- **Seek Integration**: Direct application on Seek platform (when logged in)
- **Application Tracking**: Prevents duplicate applications
- **Australian English**: Automatic spelling conversion (organise vs organize)
- **Zero Cost Option**: Multi-platform scraper works without Apify API credits

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

# Optional: Gemini API (or will use MetaAI)
GEMINI_KEY="your_gemini_api_key"

# Optional: Apify API (or will use custom scraper)
APIFY_KEY="your_apify_api_key"

# Optional: LinkedIn Selenium Scraping (for LinkedIn jobs)
LINKEDIN_EMAIL="your_linkedin_email@example.com"
LINKEDIN_PASSWORD="your_linkedin_password"
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
    "Software Engineer",
    "AI Engineer",
    "Python Developer"
  ],
  "location": "All Australia",
  "maxJobsPerSearch": 50
}
```

### 5. Test Configuration

```bash
# Test email setup
make test-email

# Test LinkedIn Selenium scraper (optional)
make test-linkedin

# Test multi-platform scraper (optional)
make test-scraper
```

### 6. Run the Application

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
make test-scraper      # Test multi-platform scraper
make test-linkedin     # Test LinkedIn Selenium scraper
make check-status      # Check application status
make run FIRST_NAME=X  # Run the application
make reset-applied     # Reset applied jobs tracker
make clean             # Clean up temporary files
```

---

##  Documentation

| Document | Description |
|----------|-------------|
| [DOCUMENTATION.md](docs/DOCUMENTATION.md) | Complete documentation |
| [SELENIUM_LINKEDIN_SETUP.md](docs/SELENIUM_LINKEDIN_SETUP.md) | LinkedIn Selenium scraping setup |
| [LINKEDIN_SCRAPING_GUIDE.md](docs/LINKEDIN_SCRAPING_GUIDE.md) | LinkedIn scraper guide |

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
| `--australian_language` | Use Australian English | `1` (enabled) |
| `--show_recent_role` | Show recent role on Seek | `1` (enabled) |

---

##  Troubleshooting

### No Applications Sent?

**Check:**
1. Gmail App Password is configured correctly
2. Jobs are being scraped successfully (check logs)
3. `applied.json` doesn't already contain the jobs
4. Review logs for error messages

**Quick Fixes:**
```bash
# Reset applied jobs
make reset-applied

# Test email configuration
make test-email

# Test scraper
make test-scraper
```

 See complete documentation: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)

### Email Authentication Failed?

You need a Gmail App Password, not your regular password.

**Setup steps:**
1. Enable 2FA: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character code to `.env`

For detailed Gmail configuration, see the DOCUMENTATION.md file.

### Gemini API Quota Exceeded?

Switch to MetaAI (no limits):
```bash
# Comment out GEMINI_KEY in .env
# The app will automatically use MetaAI
```

### Apify Free Plan Expired?

The system automatically uses the custom multi-platform scraper:
```bash
# Remove or comment out APIFY_KEY in .env
# The app will automatically use the custom scraper

# OR test the scraper
make test-scraper
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
 credentials/                # Seek login credentials
 docs/                       # Documentation
 integrations/               # External service integrations
    agent.py                # AI agents (Gemini/MetaAI)
    mail_handler.py         # Email client
    seek_client.py          # Seek automation
 scrapers/                   # Job scraping
    scraper.py              # Main scraper (Apify + fallback)
    multi_platform_scraper.py # Multi-platform custom scraper
    seek_scraper.py         # Seek-specific scraper
    linkedin_selenium_scraper.py # LinkedIn Selenium scraper
 test_email_config.py        # Email testing
 test_linkedin_scraper.py    # LinkedIn scraper testing
 check_application_status.py # Status checker
 main.py                     # Main entry point
 Makefile                    # Build commands
 README.md                   # This file
```

---

## Documentation

Complete documentation available in: **[docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)**

Includes:
- Quick Start Guide
- Gmail Setup Instructions
- Platform Features (LinkedIn Posts, Indeed, Seek)
- Country Configuration
- Running 24/7 Instructions
- Complete Troubleshooting Guide

---

##  Notes

- **Rate Limits**: 
  - Gemini free tier: 20 requests/day (use MetaAI for unlimited)
  - Apify free tier: Monthly limits (custom scraper used as fallback)
  - MetaAI: 30-second delay between requests (built-in)

- **Email Sending**: 
  - Gmail has daily send limits (~500 emails/day)
  - Consider spacing out applications
  - Monitor your Gmail Sent folder

- **Seek Applications**:
  - Requires manual login (via email code)
  - Only for jobs without questions/requirements
  - Credentials stored in `credentials/seek_refresh_token.json`

---

##  Running 24/7

To run continuously in the background, use cron or systemd.

 See: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) for scheduling instructions.

---

##  Tips

1. **Start Small**: Test with 1-2 jobs first
2. **Check Sent Folder**: Verify emails are being sent
3. **Monitor Logs**: Watch for errors and successes
4. **Review Applications**: Track progress in `applied.json`
5. **Update Config**: Adjust search terms and filters as needed

---

**Made with  for job seekers**

 Good luck with your job search! 
