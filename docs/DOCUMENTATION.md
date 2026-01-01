# Complete Documentation - Job Application Bot

**Last Updated**: January 1, 2026

This document contains all essential information for setting up and using the automated job application system.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Gmail Setup](#gmail-setup)
3. [Platform Features](#platform-features)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd bagitoJobSeeker
make install
```

### Basic Setup

1. **Configure Email** (Gmail App Password required)
2. **Add Resume**: `application_pipeline/application_materials/resume.pdf`
3. **Edit Config**: `config/run_config.json`
4. **Run**: `make run FIRST_NAME=YourName`

### Minimum Configuration

Create `.env` file:
```bash
EMAIL_ADDRESS="your@gmail.com"
EMAIL_APP_PASSWORD="your_16_char_app_password"
```

Edit `config/run_config.json`:
```json
{
    "searchTerms": ["Software Engineer"],
    "maxResults": 20,
    "platforms": ["linkedin"],
    "suburbOrCity": "Sydney",
    "country": "Australia",
    "countryCode": "AU",
    "locale": {
        "language": "en-AU",
        "spellVariant": "australian",
        "currency": "AUD"
    }
}
```

---

## Gmail Setup

### Why You Need This

Gmail requires **App Passwords** for applications to send emails. Your regular Gmail password won't work.

### Step-by-Step Setup

#### 1. Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow setup wizard
4. Verify with phone

#### 2. Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other"
3. Name it: "Job Application Bot"
4. Click "Generate"
5. Copy the 16-character password (no spaces)

**Example**: `abcd efgh ijkl mnop` → Use as: `abcdefghijklmnop`

#### 3. Add to .env File

```bash
EMAIL_ADDRESS="your@gmail.com"
EMAIL_APP_PASSWORD="abcdefghijklmnop"
```

### Testing Email

```bash
# Test your email configuration
python3 test_email_config.py
```

**Expected Output**:
```
 Email sent successfully
 Check your inbox for test email
```

### Common Issues

**"Invalid credentials"**
- Using regular password instead of app password
- Solution: Generate app password

**"2FA not enabled"**
- 2-Factor Authentication required
- Solution: Enable 2FA first

**"App password not found"**
- Typo in password
- Solution: Generate new app password

---

## Platform Features

### Supported Platforms

#### 1. LinkedIn Posts (RECOMMENDED)

**What it does**:
- Scrapes LinkedIn feed/posts (not job listings)
- Finds posts with hiring keywords + emails
- Enables automatic email applications

**Configuration**:
```json
{
    "platforms": ["linkedin"],
    "searchTerms": ["Software Engineer"]
}
```

**Advantages**:
- Direct contact emails
- Less competition
- Auto-apply via email
- Personal touch

**Example Post**:
```
"We're hiring a Software Engineer!
Send resume to: jobs@company.com"
```
→ Email sent automatically!

#### 2. LinkedIn Jobs

**What it does**:
- Scrapes official LinkedIn job listings
- Extracts job details

**Limitation**: Manual application required (no emails)

#### 3. Indeed

**What it does**:
- Scrapes Indeed job listings
- Sometimes includes contact emails

**Configuration**:
```json
{
    "platforms": ["indeed"]
}
```

#### 4. Seek (Australia/NZ)

**What it does**:
- Scrapes Seek job listings
- Can auto-apply if logged in

**Configuration**:
```json
{
    "platforms": ["seek"]
}
```

### Platform Comparison

| Platform | Source | Emails | Auto-Apply | Best For |
|----------|--------|--------|------------|----------|
| **linkedin** | Job posts (Selenium) | Common | NO | Direct contact, startups |
| **indeed** | Job listings | Rare | NO | General jobs |
| **seek** | Job listings | Sometimes | YES* | Australia/NZ |

*Seek requires login

### Multiple Platforms

Combine for maximum coverage:
```json
{
    "platforms": ["linkedin", "indeed", "seek"]
}
```

---

## Configuration

### Country Settings

The bot supports any country. Configure in `config/run_config.json`:

#### Australia
```json
{
    "suburbOrCity": "Sydney",
    "country": "Australia",
    "countryCode": "AU",
    "locale": {
        "language": "en-AU",
        "spellVariant": "australian",
        "currency": "AUD"
    }
}
```

#### United States
```json
{
    "suburbOrCity": "San Francisco",
    "country": "United States",
    "countryCode": "US",
    "locale": {
        "language": "en-US",
        "spellVariant": "american",
        "currency": "USD"
    }
}
```

#### United Kingdom
```json
{
    "suburbOrCity": "London",
    "country": "United Kingdom",
    "countryCode": "GB",
    "locale": {
        "language": "en-GB",
        "spellVariant": "british",
        "currency": "GBP"
    }
}
```

#### Canada
```json
{
    "suburbOrCity": "Toronto",
    "country": "Canada",
    "countryCode": "CA",
    "locale": {
        "language": "en-CA",
        "spellVariant": "canadian",
        "currency": "CAD"
    }
}
```

### Spelling Variants

The bot adapts spelling based on country:

**American** (`american`):
- optimize, customize, color, center

**British/Australian** (`british` or `australian`):
- optimise, customise, colour, centre

**Canadian** (`canadian`):
- Mix of both

### Search Configuration

```json
{
    "searchTerms": [
        "Software Engineer",
        "Python Developer",
        "Full Stack Developer"
    ],
    "maxResults": 50,
    "dateRange": 31,
    "requireEmail": false
}
```

**Parameters**:
- `searchTerms`: Job titles to search for
- `maxResults`: Maximum jobs per search term
- `dateRange`: Days (e.g., 31 = last month)
- `requireEmail`: Only process jobs with emails

### AI Configuration

**.env file**:
```bash
# Use Gemini (recommended)
GEMINI_KEY="your_gemini_api_key"

# Or use MetaAI (free, unlimited)
# Leave GEMINI_KEY empty
```

**Gemini**:
- Better quality cover letters
- 20 requests/day (free tier)
- Fast responses

**MetaAI**:
- Unlimited requests
- 30-second delay between requests
- Good quality

---

## Running the Bot

### Basic Run

```bash
make run FIRST_NAME=Mehdi
```

### What Happens

1. **Scrapes Jobs** from configured platforms
2. **Filters Jobs** by resume similarity
3. **Generates Cover Letters** using AI
4. **Sends Applications** via email
5. **Tracks Applications** to avoid duplicates

### Output Example

```
INFO - Scraping jobs for: Software Engineer
INFO - Searching LinkedIn posts for: Software Engineer hiring
INFO - Found 15 posts
INFO - Post with email found: linkedin_post_12345
INFO - Found 3 posts with email addresses

INFO - Processing job: linkedin_post_12345
INFO - Job: Software Engineer at Tech Startup
INFO - Similarity score: 0.85 (matches resume!)
INFO - Generating cover letter...
INFO - Sending email to jobs@techstartup.io
INFO - Email sent successfully!

INFO - Application complete: 1 of 3 jobs processed
```

### Files Generated

**Applied Jobs Tracking** (`applied.json`):
```json
{
  "jobs": {
    "linkedin_post_12345": {
      "applied_on": "2024-12-30T10:30:00",
      "position": "Software Engineer",
      "similarity_score": 0.85
    }
  }
}
}
```

**applied.json**: Application tracking
```json
{
  "jobs": {
    "linkedin_post_12345": {
      "applied_date": "2024-12-30",
      "company": "Tech Startup",
      "method": "email"
    }
  }
}
```

**cover_letter.pdf**: Generated cover letter

### Running 24/7

#### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run every day at 9 AM
0 9 * * * cd /home/user/bgt && make run FIRST_NAME=Mehdi >> logs/cron.log 2>&1

# Run every 6 hours
0 */6 * * * cd /home/user/bgt && make run FIRST_NAME=Mehdi >> logs/cron.log 2>&1
```

#### Using systemd (Linux)

Create `/etc/systemd/system/job-bot.service`:
```ini
[Unit]
Description=Job Application Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/bgt
ExecStart=/usr/bin/make run FIRST_NAME=Mehdi
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable job-bot
sudo systemctl start job-bot
```

#### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `C:\Windows\System32\cmd.exe`
   - Arguments: `/c cd C:\bgt && make run FIRST_NAME=Mehdi`

### Testing

**Test Email**:
```bash
python3 test_email_config.py
```

**Test Scraper**:
```bash
make test-scraper
```

**Dry Run** (no emails sent):
- Comment out email sending in `application_pipeline/job_application_pipeline.py`

---

## Troubleshooting

### No Jobs Found

**Problem**: "No jobs found for search term"

**Solutions**:

1. **Increase maxResults**
```json
{
    "maxResults": 100
}
```

2. **Try Different Platforms**
```json
{
    "platforms": ["linkedin", "indeed", "seek"]
}
```

3. **Broader Search Terms**
```json
{
    "searchTerms": [
        "Software Developer",
        "Engineer",
        "Developer"
    ]
}
```

4. **Check Internet Connection**
```bash
curl https://www.linkedin.com
```

### No Emails Found

**Problem**: Jobs found but no email addresses

**Solutions**:

1. **Use linkedin Platform**
```json
{
    "platforms": ["linkedin"]
}
```
LinkedIn posts often include emails, official jobs don't.

2. **Try Indeed**
Indeed jobs sometimes include contact emails.

3. **Increase Search Volume**
More jobs = higher chance of finding emails.

4. **Use LinkedIn with Selenium**
LinkedIn posts often have contact emails.

### Email Sending Failed

**Problem**: "Authentication failed" or "Invalid credentials"

**Solutions**:

1. **Verify App Password**
- Must be 16 characters
- No spaces
- Generated from Google Account settings

2. **Check .env File**
```bash
cat .env | grep EMAIL
```
Verify EMAIL_ADDRESS and EMAIL_APP_PASSWORD are correct.

3. **Test Email Configuration**
```bash
python3 test_email_config.py
```

4. **Enable 2FA**
App passwords require 2-Factor Authentication.

5. **Generate New App Password**
Old one might be revoked.

### Low Similarity Scores

**Problem**: "Low similarity score, skipping job"

**Solutions**:

1. **Lower Minimum Score**
Edit `config/args.py`:
```python
parser.add_argument('--min_score', type=float, default=0.5)
```
Change default to 0.4 or 0.3.

2. **Update Resume**
Add keywords from job descriptions to your resume.

3. **Check Resume Format**
Ensure resume.pdf is readable text (not scanned image).

4. **View Scores**
```bash
# Check logs for scores
grep "similarity score" logs/*.log
```

### Duplicate Applications

**Problem**: Applying to same job multiple times

**Solution**: Bot tracks applications automatically in `applied.json`. If seeing duplicates:

1. **Check applied.json**
```bash
cat application_pipeline/application_materials/applied.json
```

2. **Clear If Needed**
```bash
# Backup first
cp applied.json applied.json.backup

# Start fresh
echo '{"jobs": {}, "email_history": {}}' > applied.json
```

### API Rate Limits

**Problem**: "API rate limit exceeded"

**Solutions**:

**Apify** (if using):
- Monthly limit exceeded
- Solution: Custom scraper is used automatically

**Gemini** (if using):
- 20 requests/day free tier
- Solution: Switch to MetaAI (unlimited)
```bash
# Remove GEMINI_KEY from .env
# Bot automatically uses MetaAI
```

**MetaAI**:
- 30-second delay between requests (built-in)
- No rate limits

### Scraping Errors

**Problem**: "Error scraping platform"

**Solutions**:

1. **Check Internet**
```bash
ping linkedin.com
```

2. **Try Different Platform**
```json
{
    "platforms": ["indeed", "linkedin"]
}
```

4. **Update Dependencies**
```bash
make install
```

5. **Check Logs**
```bash
tail -100 logs/application.log
```

### Wrong Spelling in Cover Letters

**Problem**: American spelling in Australian job application

**Solutions**:

1. **Check Config**
```json
{
    "locale": {
        "spellVariant": "australian"
    }
}
```

2. **Override with Command Line**
```bash
make run FIRST_NAME=Mehdi --spell_variant australian
```

3. **Supported Variants**
- american
- british
- australian
- canadian

### Cover Letter Not Generated

**Problem**: Email sent without cover letter

**Solutions**:

1. **Check Gemini API Key**
```bash
grep GEMINI_KEY .env
```

2. **Use MetaAI**
Remove GEMINI_KEY from .env - MetaAI is automatic fallback.

3. **Check Logs**
```bash
grep -i "cover letter" logs/*.log
```

4. **Verify Resume**
Cover letter needs resume to compare against job.

### Seek Login Issues

**Problem**: "Seek login required"

**Solution**: Seek auto-apply requires login.

1. **Run Once Manually**
Bot will prompt for email verification code.

2. **Token Stored**
Refresh token saved in `credentials/seek_refresh_token.json`.

3. **Or Skip Seek**
```json
{
    "platforms": ["linkedin", "indeed"]
}
```

### No Applications Sent

**Problem**: Jobs found, no applications sent

**Check**:

1. **Email Requirements**
Jobs need email addresses for auto-apply. Check logs to see if scraped jobs have emails.

2. **Similarity Scores**
```bash
grep "similarity" logs/*.log
```
Might be too low.

3. **Already Applied**
```bash
cat application_pipeline/application_materials/applied.json
```
Bot prevents duplicates.

4. **Dry Run Mode**
Check if email sending is commented out in code.

---

## Quick Reference

### File Locations

```
bgt/
 .env                                  # Email credentials
 config/run_config.json                # Job search config
 application_pipeline/
    application_materials/
        resume.pdf                    # Your resume
        cover_letter.pdf              # Generated cover letter
        applied.json                  # Application tracking
 logs/
     application.log                   # Detailed logs
```

### Common Commands

```bash
# Run bot
make run FIRST_NAME=Mehdi

# Test email
python3 test_email_config.py

# Test scraper
make test-scraper

# Check applications
cat application_pipeline/application_materials/applied.json

# View logs
tail -f logs/application.log

# Clear application history
echo '{"jobs": {}, "email_history": {}}' > application_pipeline/application_materials/applied.json
```

### Configuration Templates

**Maximum Coverage**:
```json
{
    "searchTerms": ["Software Engineer", "Developer"],
    "maxResults": 100,
    "platforms": ["linkedin", "indeed", "seek"],
    "dateRange": 31
}
```

**Email-Only (Most Automatic)**:
```json
{
    "searchTerms": ["Software Engineer"],
    "maxResults": 50,
    "platforms": ["linkedin"],
    "requireEmail": true
}
```

**Australia**:
```json
{
    "suburbOrCity": "Sydney",
    "country": "Australia",
    "countryCode": "AU",
    "platforms": ["seek", "linkedin"],
    "locale": {
        "spellVariant": "australian"
    }
}
```

**USA**:
```json
{
    "suburbOrCity": "San Francisco",
    "country": "United States",
    "countryCode": "US",
    "platforms": ["linkedin", "indeed"],
    "locale": {
        "spellVariant": "american"
    }
}
```

---

## Best Practices

### 1. Start Small
- Test with 5-10 jobs first
- Verify emails are sent correctly
- Check cover letter quality

### 2. Use linkedin
- Higher success rate
- Direct contact emails
- Automatic applications

### 3. Monitor Applications
```bash
# Check sent emails
cat application_pipeline/application_materials/applied.json

# View logs
tail -50 logs/application.log
```

### 4. Update Resume Regularly
- Add new skills
- Include keywords from job descriptions
- Better matching scores

### 5. Customize Search Terms
- Be specific: "Senior Python Developer"
- Try variations: "Software Engineer", "Developer", "Programmer"
- Use job titles from your target industry

### 6. Respect Rate Limits
- Don't send 100+ emails per day
- Space out applications (use cron scheduling)
- Monitor Gmail sent folder

### 7. Review Cover Letters
- Check generated cover_letter.pdf
- Ensure quality before mass sending
- Adjust AI prompts if needed

---

## Support

### Getting Help

1. **Check This Documentation** - Most common issues covered
2. **Review Logs** - `logs/application.log` has detailed errors
3. **Test Components** - Use test scripts to isolate issues
4. **Check Configuration** - Verify .env and run_config.json

### Common Mistakes

-  Using regular Gmail password instead of app password
-  Not enabling 2FA for Gmail
-  Wrong spelling variant for country
-  Resume not in correct location
-  Empty search terms in config
-  Expecting LinkedIn jobs to have emails (use linkedin)

### Success Checklist

-  Gmail app password generated and added to .env
-  Resume.pdf in application_materials folder
-  run_config.json configured for your country
-  Test email sent successfully
-  Platforms configured (linkedin recommended)
-  Search terms relevant to your skills

---

**End of Documentation**

For the latest updates, check the repository's README.md file.

Good luck with your job search!
