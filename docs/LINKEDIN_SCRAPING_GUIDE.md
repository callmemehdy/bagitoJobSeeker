# LinkedIn Scraping Guide

## The Problem with LinkedIn

LinkedIn is a **Single Page Application (SPA)** that uses JavaScript to load content dynamically. When you visit LinkedIn:

1. Browser loads basic HTML shell
2. JavaScript code executes
3. JavaScript fetches data from LinkedIn's API  
4. JavaScript renders posts/content on the page

**Regular HTTP scrapers (curl, requests, etc.) can't execute JavaScript**, so they only get the empty HTML shell without any posts.

## Solutions for LinkedIn Scraping

### Option 1: Selenium/Playwright (Recommended)

Uses a **real browser** to scrape LinkedIn.

**Setup:**
```bash
# Install dependencies
pip install selenium webdriver-manager

# Add to config/run_config.json
{
  "platforms": ["linkedin"]
}

# Add LinkedIn credentials to .env
LINKEDIN_EMAIL="your_email@example.com"
LINKEDIN_PASSWORD="your_password"
```

**How it works:**
1. Opens Chrome browser in headless mode
2. Logs into LinkedIn with your credentials
3. Navigates to search pages and scrolls
4. Extracts text, emails, and links
5. Saves cookies for future sessions

**Pros:** Full access, handles JavaScript, extracts emails  
**Cons:** Slower, requires Chrome, uses more resources

---

### Option 2: LinkedIn API (Best for Production)

Official API from LinkedIn - requires approval (2-4 weeks).

---

## Current Implementation

**What Works:**
-  Indeed - Full scraping
-  Seek - Full scraping  
-  LinkedIn Posts - Requires Selenium

**Enable LinkedIn (Selenium):**
```bash
pip install selenium webdriver-manager
# Add LINKEDIN_EMAIL/PASSWORD to .env
# Selenium is enabled by default for LinkedIn
make run FIRST_NAME=YourName
```

## Recommendations

**For Job Applications:**
1. Use Indeed + Seek (work great, no setup)
2. Add Selenium for LinkedIn (optional)
3. Focus on emails over links

**Why Indeed/Seek are better:**
- No JavaScript needed
- Many jobs include emails
- No authentication required
- Faster and more reliable
