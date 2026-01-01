#!/usr/bin/env python3
import os
import sys
import time
import re
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')
cookies_file = "./credentials/linkedin_cookies.json"

print(f"Using email: {email}")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("\n1. Loading LinkedIn...")
    driver.get("https://www.linkedin.com")
    time.sleep(2)
    
    # Try to load cookies
    if os.path.exists(cookies_file):
        print("2. Loading saved cookies...")
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.refresh()
        time.sleep(5)
        
        if "feed" in driver.current_url or "search" in driver.current_url:
            print("✓ Logged in with cookies!")
        else:
            print("✗ Cookies didn't work, please login manually...")
            input("Press Enter after logging in...")
    else:
        print("2. No saved cookies - please login manually...")
        input("Press Enter after logging in...")
    
    print("\n3. Going to feed search...")
    driver.get("https://www.linkedin.com/search/results/content/?keywords=software+engineer+hiring")
    time.sleep(8)
    
    print("4. Scrolling to load more posts...")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    print("\n5. Analyzing posts for emails...\n")
    posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
    print(f"Found {len(posts)} posts total\n")
    
    total_with_emails = 0
    
    for i, post in enumerate(posts[:20], 1):
        text = post.text
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        
        if emails:
            total_with_emails += 1
            print(f"{'='*60}")
            print(f"✓✓✓ POST {i} HAS {len(emails)} EMAIL(S) ✓✓✓")
            print(f"{'='*60}")
            print(f"Emails: {emails}")
            print(f"Text:\n{text[:800]}\n")
        else:
            print(f"✗ Post {i}: {len(text)} chars, no emails")
    
    print(f"\n{'='*70}")
    print(f"RESULT: {total_with_emails}/{len(posts)} posts have emails")
    print(f"{'='*70}\n")
    
    if total_with_emails == 0:
        print("Checking page source for ANY emails...")
        page_source = driver.page_source
        all_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
        unique_emails = list(set([e for e in all_emails if not e.endswith('.png') and not e.endswith('.jpg')]))
        print(f"\nFound {len(unique_emails)} unique emails in page source:")
        for email in unique_emails[:30]:
            print(f"  - {email}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
        
finally:
    input("\nPress Enter to close browser...")
    driver.quit()
