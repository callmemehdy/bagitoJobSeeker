#!/usr/bin/env python3
"""
Test LinkedIn Post Scraper
Run this to verify LinkedIn scraping is working
"""

import os
import sys
from dotenv import load_dotenv
from scrapers.linkedin_post_scraper import LinkedInPostScraper

load_dotenv()


def main():
    print("=" * 80)
    print("LinkedIn Post Scraper Test")
    print("=" * 80)
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    # Debug: Show credential status
    print(f"\n🔍 Debug - Checking credentials:")
    print(f"   Email: {email[:5] if email else '❌ NOT FOUND'}...@...")
    print(f"   Password: {'✓ Found (' + str(len(password)) + ' chars)' if password else '❌ NOT FOUND'}")
    
    if not email or not password:
        print("\n❌ ERROR: LinkedIn credentials not found!")
        print("\nPlease add to .env:")
        print("  LINKEDIN_EMAIL=\"your_email@example.com\"")
        print("  LINKEDIN_PASSWORD=\"your_password\"")
        sys.exit(1)
    
    import json
    try:
        with open('./config/run_config.json', 'r') as f:
            config = json.load(f)
        country = config.get('country', 'United Kingdom')
        country_code = config.get('countryCode', 'GB')
        location = config.get('suburbOrCity', 'London')
    except:
        country = 'United Kingdom'
        country_code = 'GB'
        location = 'London'
    
    print(f"\n✓ Found LinkedIn credentials for: {email}")
    print(f"✓ Country: {country} ({country_code})")
    print(f"✓ Location: {location}")
    print("\n⏳ Starting Chrome browser (this may take a moment)...")
    
    scraper = LinkedInPostScraper(
        email=email,
        password=password,
        headless=False,  # Set to True to hide browser
        location=f"{location}, {country}"
    )
    
    try:
        search_term = "Software Engineer"
        print(f"\n🔍 Scraping LinkedIn posts for: '{search_term}' in {location}")
        print("⏳ This will take 30-60 seconds...\n")
        
        posts = scraper.scrape_posts(
            search_term=search_term,
            max_results=10
        )
        
        print("\n" + "=" * 80)
        print(f"✅ SUCCESS! Found {len(posts)} posts with contact information")
        print("=" * 80)
        
        if posts:
            print("\n📋 Sample Posts:\n")
            
            for i, post in enumerate(posts[:5], 1):
                print(f"{i}. {post.get('title', 'No title')}")
                print(f"   Company: {post.get('company', 'Unknown')}")
                print(f"   Emails: {', '.join(post.get('emails', []))}")
                print(f"   Link: {post.get('jobLink', 'No link')[:80]}...")
                content = post.get('content', '')
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"   Preview: {preview}")
                print()
            
            if len(posts) > 5:
                print(f"   ... and {len(posts) - 5} more posts")
            
            # Save to file
            output_file = "linkedin_posts_test_results.json"
            with open(output_file, 'w') as f:
                json.dump(posts, f, indent=2)
            print(f"\n💾 Full results saved to: {output_file}")
        else:
            print("\n⚠️  No posts with contact information found.")
            print("\nThis could be because:")
            print("  1. LinkedIn is blocking automated access (common)")
            print("  2. No recent posts contain email addresses")
            print("  3. Cookies may need to be refreshed: run 'make login'")
            print("\n💡 TIP: Regular LinkedIn job search is more reliable")
            print("         Set 'use_selenium_for_linkedin': false in config")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n🔄 Closing browser...")
        scraper.close()
        print("✅ Test complete!")


if __name__ == "__main__":
    main()
