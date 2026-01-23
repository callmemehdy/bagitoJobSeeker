#!/usr/bin/env python3
"""
Analyze LinkedIn Post HTML Structure
This script captures LinkedIn post HTML and analyzes the structure to find email patterns
"""

import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from scrapers.linkedin_post_scraper import LinkedInPostScraper

load_dotenv()


def analyze_html_structure(html_file="linkedin_debug_page.html"):
    """Analyze saved HTML to understand structure"""
    if not os.path.exists(html_file):
        print(f"❌ {html_file} not found. Run the scraper first to generate it.")
        return
    
    print("="*80)
    print("ANALYZING LINKEDIN HTML STRUCTURE")
    print("="*80)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. Find all email patterns
    print("\n🔍 SEARCHING FOR EMAIL PATTERNS:")
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
    print(f"   Total emails found: {len(emails)}")
    unique_emails = list(set(emails))
    print(f"   Unique emails: {len(unique_emails)}")
    for email in unique_emails[:10]:
        print(f"      • {email}")
    
    # 2. Find context around emails
    print("\n📝 EMAIL CONTEXT (150 chars before and after):")
    for email in unique_emails[:3]:
        match = re.search(rf'.{{0,150}}{re.escape(email)}.{{0,150}}', html, re.DOTALL)
        if match:
            context = match.group(0).replace('\n', ' ').replace('\r', '')
            context = ' '.join(context.split())  # Clean whitespace
            print(f"\n   Email: {email}")
            print(f"   Context: ...{context}...")
    
    # 3. Analyze post structure
    print("\n🏗️  ANALYZING POST STRUCTURE:")
    
    # Look for common LinkedIn post classes
    patterns = {
        'feed-shared-update': html.count('feed-shared-update'),
        'reusable-search__result': html.count('reusable-search__result'),
        'update-components': html.count('update-components'),
        'feed-shared-text': html.count('feed-shared-text'),
        'break-words': html.count('break-words'),
        'data-testid="expandable': html.count('data-testid="expandable'),
    }
    
    for pattern, count in patterns.items():
        print(f"   {pattern}: {count} occurrences")
    
    # 4. Find "see more" button patterns
    print("\n🔘 'SEE MORE' BUTTON PATTERNS:")
    see_more_patterns = [
        'see more',
        'show more', 
        'voir plus',
        'see-more',
        'show-more',
        'expandable-text'
    ]
    
    for pattern in see_more_patterns:
        count = html.lower().count(pattern.lower())
        if count > 0:
            print(f"   '{pattern}': {count} occurrences")
    
    # 5. Extract sample post HTML
    print("\n📄 SAMPLE POST HTML STRUCTURES:")
    
    # Try to extract individual posts
    post_patterns = [
        r'<li[^>]*class="[^"]*reusable-search__result[^"]*"[^>]*>(.*?)</li>',
        r'<div[^>]*class="[^"]*feed-shared-update[^"]*"[^>]*>(.*?)</div>',
    ]
    
    for i, pattern in enumerate(post_patterns, 1):
        matches = re.findall(pattern, html, re.DOTALL)
        if matches:
            print(f"\n   Pattern {i} found {len(matches)} posts")
            # Save first post sample
            if matches:
                sample = matches[0][:1000]
                print(f"   Sample (first 1000 chars): {sample[:200]}...")
    
    # 6. Save analysis report
    report = {
        'total_emails': len(emails),
        'unique_emails': unique_emails,
        'patterns_found': patterns,
        'html_size': len(html),
        'post_count_estimate': max(patterns.values())
    }
    
    with open('linkedin_structure_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis saved to linkedin_structure_analysis.json")


def capture_fresh_samples():
    """Capture fresh LinkedIn samples with detailed logging"""
    print("="*80)
    print("CAPTURING FRESH LINKEDIN SAMPLES")
    print("="*80)
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LinkedIn credentials not found in .env")
        return
    
    # Load config
    with open('./config/run_config.json', 'r') as f:
        config = json.load(f)
    
    country = config.get('country', 'France')
    search_term = config.get('searchTerms', ['Stage Ingénieur Informatique'])[0]
    
    print(f"\n🔍 Searching for: {search_term}")
    print(f"🌍 Country: {country}")
    print(f"📧 Using credentials: {email}")
    
    # Create scraper with headless=False to see what's happening
    scraper = LinkedInPostScraper(
        email=email,
        password=password,
        headless=False,  # Show browser
        location=country
    )
    
    try:
        print("\n⏳ Starting scraper (check browser window)...")
        print("   The scraper will:")
        print("   1. Login to LinkedIn")
        print("   2. Search for posts")
        print("   3. Scroll through results")
        print("   4. Save HTML for analysis")
        print("   5. Extract emails")
        
        posts = scraper.scrape_posts(search_term=search_term, max_results=10)
        
        print(f"\n✅ Scraping complete!")
        print(f"   Posts with emails found: {len(posts)}")
        
        if posts:
            print("\n📧 EMAILS FOUND:")
            for i, post in enumerate(posts, 1):
                print(f"\n   {i}. {post.get('title', 'No title')}")
                print(f"      Emails: {', '.join(post.get('emails', []))}")
                print(f"      Preview: {post.get('content', '')[:100]}...")
        
        # Now analyze the saved HTML
        if os.path.exists('linkedin_debug_page.html'):
            print("\n📄 Analyzing saved HTML...")
            analyze_html_structure('linkedin_debug_page.html')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        # Just analyze existing HTML
        analyze_html_structure()
    else:
        # Capture fresh samples
        capture_fresh_samples()


if __name__ == "__main__":
    main()
