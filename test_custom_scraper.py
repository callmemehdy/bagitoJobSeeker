#!/usr/bin/env python3
"""
Test the multi-platform job scraper
Usage: python test_custom_scraper.py
"""

import asyncio
import json
import logging
from scrapers.multi_platform_scraper import MultiPlatformScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

async def main():
    # Test configuration
    run_config = {
        "searchTerms": ["Software Engineer"],
        "maxResults": 10,  # Keep it small for testing
        "suburbOrCity": "Sydney",
        "state": "NSW",
        "dateRange": 31,
        "platforms": ["indeed", "linkedin"]  # Test multiple platforms
    }
    
    print("\n" + "="*60)
    print("Testing Multi-Platform Job Scraper")
    print("="*60 + "\n")
    print(f"Platforms: {', '.join(run_config['platforms'])}")
    print()
    
    scraper = MultiPlatformScraper(run_config, cached_data_path='./test_info.json')
    
    try:
        print("Starting scrape...")
        results = await scraper.scrape()
        
        print("\n" + "="*60)
        print("Results:")
        print("="*60)
        
        for search_term, jobs in results.items():
            print(f"\n{search_term}: {len(jobs)} jobs found")
            
            # Group by platform
            by_platform = {}
            for job in jobs:
                platform = job.get('platform', 'unknown')
                by_platform.setdefault(platform, []).append(job)
            
            for platform, platform_jobs in by_platform.items():
                print(f"  - {platform}: {len(platform_jobs)} jobs")
            
            if jobs:
                print("\nFirst job example:")
                job = jobs[0]
                print(f"  Platform: {job.get('platform', 'unknown')}")
                print(f"  ID: {job.get('id')}")
                print(f"  Title: {job.get('title')}")
                print(f"  Company: {job.get('company')}")
                print(f"  Location: {job.get('joblocationInfo', {}).get('displayLocation')}")
                print(f"  Link: {job.get('jobLink')}")
                print(f"  Salary: {job.get('salary', 'N/A')}")
        
        print("\n Multi-platform scraper test completed successfully!")
        print(f" Results saved to: ./test_info.json")
        
    except Exception as e:
        print(f"\n Scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
