import os
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.linkedin_selenium_scraper import LinkedInSeleniumScraper

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')

if not email or not password:
    print("ERROR: Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
    sys.exit(1)

print(f"Testing with email: {email}")

scraper = LinkedInSeleniumScraper(
    email=email,
    password=password,
    headless=False,
    country="Morocco",
    country_code="MA"
)

try:
    print("\nSearching for 'Software Engineer' jobs...")
    jobs = scraper.scrape_jobs("Software Engineer", "Rabat", max_results=10)
    
    print(f"\n\n{'='*60}")
    print(f"RESULTS: Found {len(jobs)} jobs total")
    print(f"{'='*60}\n")
    
    jobs_with_emails = [j for j in jobs if j.get('emails')]
    jobs_without_emails = [j for j in jobs if not j.get('emails')]
    
    print(f"✓ Jobs WITH emails: {len(jobs_with_emails)}")
    print(f"✗ Jobs WITHOUT emails: {len(jobs_without_emails)}")
    
    if jobs_with_emails:
        print("\n--- JOBS WITH EMAILS ---")
        for job in jobs_with_emails:
            print(f"\nTitle: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Emails: {job['emails']}")
            print(f"Content preview: {job.get('content', '')[:200]}...")
    
    if jobs_without_emails:
        print("\n--- SAMPLE JOB WITHOUT EMAIL ---")
        sample = jobs_without_emails[0]
        print(f"\nTitle: {sample['title']}")
        print(f"Company: {sample['company']}")
        print(f"Content length: {len(sample.get('content', ''))} chars")
        print(f"Content preview:\n{sample.get('content', '')[:500]}")
        
finally:
    scraper.close()
    print("\n\nDone! Browser closed.")
