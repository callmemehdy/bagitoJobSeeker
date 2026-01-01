#!/usr/bin/env python3
"""
Test LinkedIn Selenium Scraper
Run this to verify LinkedIn scraping is working
"""

import os
import sys
from dotenv import load_dotenv
from scrapers.linkedin_selenium_scraper import LinkedInSeleniumScraper

load_dotenv()


def main():
    print("=" * 80)
    print("LinkedIn Selenium Scraper Test")
    print("=" * 80)
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("\n ERROR: LinkedIn credentials not found!")
        print("\nPlease add to .env:")
        print("  LINKEDIN_EMAIL=\"your_email@example.com\"")
        print("  LINKEDIN_PASSWORD=\"your_password\"")
        sys.exit(1)
    
    import json
    try:
        with open('./config/run_config.json', 'r') as f:
            config = json.load(f)
        country = config.get('country', 'Australia')
        country_code = config.get('countryCode', 'AU')
        location = config.get('suburbOrCity', 'Sydney')
    except:
        country = 'Australia'
        country_code = 'AU'
        location = 'Sydney'
    
    print(f"\n Found LinkedIn credentials for: {email}")
    print(f" Country: {country} ({country_code})")
    print(f" Location: {location}")
    print("\n  Starting Chrome browser (this may take a moment)...")
    
    scraper = LinkedInSeleniumScraper(
        email=email,
        password=password,
        headless=False,
        country=country,
        country_code=country_code
    )
    
    try:
        print(f" Scraping jobs for: 'Software Engineer' in {location}")
        print("⏳ This will take 30-60 seconds...\n")
        
        jobs = scraper.scrape_jobs(
            search_term="Software Engineer",
            location=location,
            max_results=10
        )
        
        print("\n" + "=" * 80)
        print(f" SUCCESS! Found {len(jobs)} jobs from LinkedIn")
        print("=" * 80)
        
        if jobs:
            print("\n Sample Jobs:\n")
            
            for i, job in enumerate(jobs[:5], 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['joblocationInfo']['displayLocation']}")
                print(f"   Country: {job['joblocationInfo']['country']} ({job['joblocationInfo']['countryCode']})")
                print(f"   Emails: {job['emails'] if job['emails'] else 'None found'}")
                print(f"   Link: {job['jobLink']}")
                print()
            
            if len(jobs) > 5:
                print(f"   ... and {len(jobs) - 5} more jobs")
        else:
            print("\n  No jobs found. Try adjusting search terms or location.")
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n Closing browser...")
        scraper.close()
        print(" Test complete!")


if __name__ == "__main__":
    main()
