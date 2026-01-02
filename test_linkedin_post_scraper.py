#!/usr/bin/env python3
"""
Test script for LinkedIn Post Scraper
"""
import os
import sys
from dotenv import load_dotenv
from scrapers.linkedin_post_scraper import LinkedInPostScraper

load_dotenv()

def main():
    # Get credentials from environment
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("ERROR: LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env file")
        sys.exit(1)
    
    print("Starting LinkedIn Post Scraper test...")
    print("=" * 60)
    
    # Create scraper instance (headless=False to see browser)
    scraper = LinkedInPostScraper(
        email=email,
        password=password,
        headless=False  # Set to True for headless mode
    )
    
    try:
        # Test with multiple search terms
        search_terms = [
            "hiring email",
            "recruiting contact", 
            "AI internship apply",
            "software engineer opportunity"
        ]
        
        all_posts = []
        
        for search_term in search_terms:
            max_results = 10
            
            print(f"\n{'=' * 60}")
            print(f"Searching for: '{search_term}'")
            print(f"Max results: {max_results}")
            print("-" * 60)
            
            posts = scraper.scrape_posts(search_term, max_results=max_results)
            
            print(f"\nFound {len(posts)} posts with emails for '{search_term}'")
            
            for i, post in enumerate(posts, 1):
                print(f"\n{i}. {post.get('title', 'No title')}")
                print(f"   Author: {post.get('company', 'Unknown')}")
                print(f"   Emails: {', '.join(post.get('emails', []))}")
                print(f"   Link: {post.get('jobLink', 'No link')[:80]}...")
                print(f"   Content preview: {post.get('content', '')[:100]}...")
                print(f"   Timestamp: {post.get('timestamp', 'Unknown')}")
            
            all_posts.extend(posts)
            
            if len(posts) > 0:
                print(f"\n✓ Success! Found {len(posts)} posts with emails")
            else:
                print(f"\n✗ No posts with emails found for this search term")
        
        print("\n" + "=" * 60)
        print(f"FINAL RESULTS: Found {len(all_posts)} total posts with emails")
        print("=" * 60)
        
        if len(all_posts) == 0:
            print("\n⚠️  No posts with emails found across all searches.")
            print("\nPossible reasons:")
            print("- LinkedIn posts rarely contain public email addresses")
            print("- Try more specific search terms related to job postings")
            print("- Consider using job board scrapers instead (Indeed, LinkedIn Jobs)")
            print("\nTips:")
            print("- Search for: 'hiring email', 'recruiting contact', 'apply to'")
            print("- Look for posts from recruiters or HR professionals")
            print("- Check if the scraper is working by watching the browser (headless=False)")
        else:
            print(f"\n✓ Successfully found {len(all_posts)} posts with contact emails!")
            
            # Save results to file
            import json
            output_file = "linkedin_posts_with_emails.json"
            with open(output_file, 'w') as f:
                json.dump(all_posts, f, indent=2)
            print(f"\nResults saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing browser...")
        scraper.close()
        print("Test complete!")

if __name__ == "__main__":
    main()
