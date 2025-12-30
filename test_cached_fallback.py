#!/usr/bin/env python3
"""
Test script to verify the cached data fallback mechanism works correctly.
This is useful for testing without consuming Apify API credits.
"""

import asyncio
from scrapers.scraper import JobScraper
from common.utils import load_json_file
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

async def test_fallback():
    """Test the cached data fallback functionality"""
    
    print("\n" + "="*60)
    print("Testing Cached Data Fallback Mechanism")
    print("="*60 + "\n")
    
    # Load configuration
    run_config = load_json_file('./config/run_config.json')
    if not run_config:
        print(" Could not load run_config.json")
        return
    
    print(f" Loaded config with search terms: {run_config['searchTerms']}\n")
    
    # Create scraper with cached data
    scraper = JobScraper(run_config, cached_data_path='./info.json')
    
    # Test direct cached data loading
    print("Testing direct cached data loading...")
    cached_data = scraper._load_cached_data()
    
    if not cached_data:
        print(" No cached data loaded")
        return
    
    print(f" Successfully loaded cached data\n")
    
    # Display results
    print("Cached Data Summary:")
    print("-" * 60)
    total_jobs = 0
    for search_term, jobs in cached_data.items():
        print(f"   {search_term}: {len(jobs)} jobs")
        total_jobs += len(jobs)
        if jobs:
            sample_job = jobs[0]
            print(f"     Sample: {sample_job.get('title', 'N/A')}")
    
    print(f"\n  Total cached jobs across all search terms: {total_jobs}")
    print("-" * 60)
    
    # Test the actual scrape method (will use cache if API fails)
    print("\n\nTesting scrape() method with fallback...")
    print("(This will attempt API first, then fall back to cache if needed)\n")
    
    try:
        data = await scraper.scrape("websift/seek-job-scraper")
        
        if data:
            print("\n Scrape completed successfully!")
            print("\nResults Summary:")
            print("-" * 60)
            for search_term, jobs in data.items():
                print(f"   {search_term}: {len(jobs)} jobs")
            print("-" * 60)
        else:
            print(" No data returned from scrape")
            
    except Exception as e:
        print(f" Error during scrape: {e}")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_fallback())
