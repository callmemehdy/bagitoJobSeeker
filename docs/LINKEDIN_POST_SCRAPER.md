# LinkedIn Post Scraper Guide

## Overview

The LinkedIn Post Scraper is a new approach to finding job opportunities by scraping **LinkedIn posts** instead of traditional job listings. This method targets posts where recruiters and HR professionals share job opportunities with direct contact information.

## Why LinkedIn Posts?

- **Direct Contact**: Recruiters often share their email addresses in posts
- **More Personal**: Posts are more informal than job listings
- **Higher Response Rate**: Direct contact with recruiters leads to better responses
- **Bypass ATS**: Skip automated application tracking systems
- **Less Competition**: Not everyone searches posts for opportunities

## How It Works

### 1. Login Process
- Uses saved cookies for fast login
- Falls back to credential-based login if cookies expire
- Handles LinkedIn security challenges
- Saves authentication cookies for future sessions

### 2. Search Strategy
- Searches LinkedIn content feed for specific keywords
- Uses optimized search terms like "hiring email", "recruiting contact"
- Sorts by date to get recent posts
- Scrolls through results to load more posts

### 3. Post Parsing
- Expands "see more" to get full post text
- Extracts email addresses using regex
- Filters out invalid emails (noreply@, linkedin.com, etc.)
- Captures author information and post metadata

### 4. Data Extraction
Each post with valid emails returns:
- **Post ID**: Unique identifier
- **Title**: Generated from author and search term
- **Author**: Post creator's name
- **Emails**: List of valid contact emails found
- **Content**: First 500 characters of post text
- **Link**: Direct link to the LinkedIn post
- **Timestamp**: When the post was created

## Configuration

### Environment Variables (`.env`)

```bash
# Required for LinkedIn post scraping
LINKEDIN_EMAIL="your_linkedin_email@example.com"
LINKEDIN_PASSWORD="your_linkedin_password"
```

### Search Configuration (`config/run_config.json`)

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
  "platforms": ["linkedin"]
}
```

## Optimizing Search Terms

### Best Practices

✅ **Good Search Terms:**
- "hiring email" - Direct indication of hiring with contact
- "recruiting contact" - Recruiters sharing contact info
- "[job type] apply email" - Specific roles with application method
- "[role] opportunity contact" - Opportunities with contact details
- "[location] hiring email" - Location-specific searches

❌ **Poor Search Terms:**
- "software engineer" - Too generic, no email context
- "AI jobs" - Broad search without contact indication
- "internship" - Lacks context about contact information

### Examples by Industry

**Tech/Engineering:**
```
"software engineer hiring email"
"developer position contact"
"tech startup recruiting email"
```

**Internships:**
```
"internship apply email"
"summer intern opportunity contact"
"graduate position email"
```

**Remote Work:**
```
"remote hiring contact"
"work from home opportunity email"
```

## Usage

### Testing the Scraper

```bash
# Run the test script (with visible browser)
python test_linkedin_post_scraper.py
```

This will:
1. Open a browser window
2. Login to LinkedIn
3. Search multiple terms
4. Display results in console
5. Save results to `linkedin_posts_with_emails.json`

### Running in Production

```bash
# Run with the main pipeline
make run FIRST_NAME=YourName
```

The scraper will:
1. Use the search terms from `config/run_config.json`
2. Search for posts with each term
3. Extract posts with valid emails
4. Pass them to the application pipeline
5. Generate cover letters and send applications

## Troubleshooting

### No Posts with Emails Found

This is **normal and expected**. Most LinkedIn posts don't contain public email addresses.

**Solutions:**
1. Use more specific search terms focused on contact/email
2. Try location-specific searches
3. Search for recruiter posts specifically
4. Supplement with job board scrapers (Indeed, Seek)
5. Run searches regularly as new posts appear daily

### Login Issues

**Stuck on login page:**
```bash
# Delete old cookies
rm ./credentials/linkedin_cookies.json

# Run test again
python test_linkedin_post_scraper.py
```

**Security challenge appears:**
- Set `headless=False` in the test script
- Complete the challenge manually in the browser
- Press Enter to continue
- Cookies will be saved after successful challenge completion

### Browser Crashes

**Symptoms:**
- "session deleted" errors
- Browser closes unexpectedly
- Page timeouts

**Solutions:**
```bash
# Update Chrome driver
pip install --upgrade selenium webdriver-manager

# Clear Chrome cache
rm -rf ~/.cache/selenium/
```

### Rate Limiting

LinkedIn may rate limit if you scrape too frequently.

**Best Practices:**
- Don't run the scraper more than 3-4 times per day
- Use reasonable maxResults (10-20 per term)
- Add delays between searches (built-in)
- Vary search times throughout the day

## Technical Details

### CSS Selectors Used

The scraper uses multiple selectors for reliability:

**Post containers:**
- `li.reusable-search__result-container`
- `div.feed-shared-update-v2`

**Post text:**
- `.feed-shared-update-v2__description`
- `.feed-shared-text`
- `.update-components-text`
- `.break-words`
- `.feed-shared-inline-show-more-text`

**Author information:**
- `.update-components-actor__name`
- `.feed-shared-actor__name`
- `span[dir='ltr']`

### Email Extraction

Regex pattern used:
```python
r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```

Filtered out domains:
- `noreply`
- `linkedin.com`
- `example.com`

### Performance

**Timing:**
- Login: 5-10 seconds
- Search load: 3-5 seconds
- Per scroll: 3 seconds
- Total per search: ~30-60 seconds

**Results:**
- Expect 0-5 posts with emails per search term
- 5 search terms ≈ 0-25 posts with emails
- Highly variable based on search terms and timing

## Advanced Usage

### Headless vs Visible Browser

**Headless (production):**
```python
scraper = LinkedInPostScraper(
    email=email,
    password=password,
    headless=True
)
```

**Visible (testing/debugging):**
```python
scraper = LinkedInPostScraper(
    email=email,
    password=password,
    headless=False
)
```

### Custom Timeout Settings

Located in the scraper code:
- Page load timeout: 60 seconds
- Cookie validation: 10 seconds
- Login wait: 5 seconds
- Search load: 20 seconds

### Scroll Configuration

```python
max_scrolls = 10           # Maximum scroll attempts
stale_count = 3            # Retries when no new content
scroll_delay = 3           # Seconds between scrolls
```

## Best Practices

1. **Start with testing**: Always test with `headless=False` first
2. **Monitor results**: Check `linkedin_posts_with_emails.json` regularly
3. **Adjust search terms**: Based on what works for your target roles
4. **Combine approaches**: Use both post scraping and job board scraping
5. **Be patient**: Posts with emails are rare but valuable
6. **Stay compliant**: Don't over-scrape or spam applications

## Comparison: Posts vs Job Cards

| Feature | LinkedIn Posts | LinkedIn Jobs |
|---------|---------------|---------------|
| **Contact Info** | Often included | Rarely included |
| **Competition** | Lower | Higher |
| **Formality** | Informal | Formal |
| **Response Rate** | Higher | Lower |
| **Quantity** | Low | High |
| **Application** | Direct email | Through platform |
| **ATS** | Bypass | Must go through |

## Future Improvements

Potential enhancements:
- [ ] Filter by post author type (recruiters, HR)
- [ ] Track post engagement (likes, comments)
- [ ] Extract phone numbers in addition to emails
- [ ] Support for other languages
- [ ] Machine learning to identify valuable posts
- [ ] Integration with CRM for follow-ups

## Conclusion

The LinkedIn Post Scraper is a complementary tool to traditional job board scraping. While it finds fewer opportunities, the quality and response rate are typically higher due to direct recruiter contact. Use it alongside other scraping methods for best results.

For questions or issues, check the main README or open an issue on GitHub.
