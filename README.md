# BagitoJobSeeker - Automated Job Application Bot 

An intelligent automation system that scrapes job listings from Seek, generates personalized cover letters using AI, and automatically sends job applications via email.

##  Features

- **Job Scraping**: Uses Apify Seek Job Scraper or falls back to cached data
- **AI-Generated Content**: Creates personalized cover letters using Gemini or MetaAI
- **Smart Filtering**: Resume-based job matching with configurable similarity scores
- **Email Automation**: Automated application submission via Gmail
- **Seek Integration**: Direct application on Seek platform (when logged in)
- **Application Tracking**: Prevents duplicate applications
- **Australian English**: Automatic spelling conversion (organise vs organize)

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

# Optional: Apify API (or will use cached data)
APIFY_KEY="your_apify_api_key"
```

**Important:** You need a Gmail App Password (not your regular password)
-  See: [docs/GMAIL_APP_PASSWORD_SETUP.md](docs/GMAIL_APP_PASSWORD_SETUP.md)

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

# Test cached data fallback
make test-cache
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
make test-cache        # Test cached data fallback
make check-status      # Check application status
make run FIRST_NAME=X  # Run the application
make reset-applied     # Reset applied jobs tracker
make clean             # Clean up cache files
```

---

##  Documentation

| Document | Description |
|----------|-------------|
| [QUICK_START.md](docs/QUICK_START.md) | Quick setup guide |
| [GMAIL_APP_PASSWORD_SETUP.md](docs/GMAIL_APP_PASSWORD_SETUP.md) | Gmail configuration guide |
| [FALLBACK_DATA.md](docs/FALLBACK_DATA.md) | Cached data fallback system |
| [GEMINI_MODEL_UPDATE.md](docs/GEMINI_MODEL_UPDATE.md) | Gemini API configuration |
| [TROUBLESHOOTING_NO_APPLICATIONS.md](docs/TROUBLESHOOTING_NO_APPLICATIONS.md) | Common issues and fixes |
| [CHANGES_SUMMARY.md](docs/CHANGES_SUMMARY.md) | Recent changes and fixes |
| [SCHEDULING.md](docs/SCHEDULING.md) | Run 24/7 with cron |

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
2. Jobs in `info.json` have email addresses
3. `applied.json` doesn't already contain the jobs
4. Review logs for error messages

**Quick Fixes:**
```bash
# Reset applied jobs
make reset-applied

# Test email configuration
make test-email

# Check what jobs are available
make test-cache
```

 See: [docs/TROUBLESHOOTING_NO_APPLICATIONS.md](docs/TROUBLESHOOTING_NO_APPLICATIONS.md)

### Email Authentication Failed?

You need a Gmail App Password, not your regular password.

 See: [docs/GMAIL_APP_PASSWORD_SETUP.md](docs/GMAIL_APP_PASSWORD_SETUP.md)

### Gemini API Quota Exceeded?

Switch to MetaAI (no limits):
```bash
# Comment out GEMINI_KEY in .env
# The app will automatically use MetaAI
```

 See: [docs/GEMINI_MODEL_UPDATE.md](docs/GEMINI_MODEL_UPDATE.md)

### Apify Free Plan Expired?

The system automatically uses cached data:
```bash
# Test fallback
make test-cache
```

 See: [docs/FALLBACK_DATA.md](docs/FALLBACK_DATA.md)

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
    scraper.py              # Apify integration + fallback
 test_email_config.py        # Email testing
 test_cached_fallback.py     # Cache testing
 check_application_status.py # Status checker
 main.py                     # Main entry point
 Makefile                    # Build commands
 README.md                   # This file
```

---

##  Notes

- **Rate Limits**: 
  - Gemini free tier: 20 requests/day (use MetaAI for unlimited)
  - Apify free tier: Monthly limits (use cached data fallback)
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

To run continuously in the background:

 See: [docs/SCHEDULING.md](docs/SCHEDULING.md)

---

##  Tips

1. **Start Small**: Test with 1-2 jobs first
2. **Check Sent Folder**: Verify emails are being sent
3. **Monitor Logs**: Watch for errors and successes
4. **Update Cache**: Refresh `info.json` periodically
5. **Track Applications**: Review `applied.json` regularly

---

**Made with  for job seekers**

 Good luck with your job search! 
