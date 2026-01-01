#!/usr/bin/env python3
import os
import sys
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')
cookies_file = "./credentials/linkedin_cookies.json"

print("="*70)
print("LINKEDIN AUTHENTICATION TEST")
print("="*70)
print(f"\nEmail: {email}")
print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
print(f"Cookies file: {cookies_file}")
print(f"Cookies exist: {os.path.exists(cookies_file)}")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("\n" + "="*70)
    print("TEST 1: Cookie-based Login")
    print("="*70)
    
    driver.get("https://www.linkedin.com")
    time.sleep(2)
    
    if os.path.exists(cookies_file):
        print("✓ Loading saved cookies...")
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"  Warning: Could not add cookie: {e}")
        
        print("✓ Cookies loaded, refreshing page...")
        driver.refresh()
        time.sleep(5)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"\nCurrent URL: {current_url}")
        print(f"Page Title: {page_title}")
        
        if "feed" in current_url or "mynetwork" in current_url or "messaging" in current_url:
            print("\n✅ SUCCESS: Cookie login worked!")
            print("User is logged in to LinkedIn")
        elif "login" in current_url or "uas/login" in current_url:
            print("\n❌ FAILED: Cookies expired or invalid")
            print("LinkedIn redirected to login page")
            
            print("\n" + "="*70)
            print("TEST 2: Fresh Login with Credentials")
            print("="*70)
            
            try:
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_field.clear()
                email_field.send_keys(email)
                
                password_field = driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(password)
                
                print("✓ Entered credentials")
                
                login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_btn.click()
                
                print("✓ Clicked login button")
                print("Waiting 10 seconds for login...")
                time.sleep(10)
                
                current_url = driver.current_url
                
                if "feed" in current_url or "checkpoint" in current_url:
                    print("\n✅ SUCCESS: Fresh login worked!")
                    
                    if "checkpoint" in current_url:
                        print("⚠️  WARNING: LinkedIn security checkpoint detected")
                        print("You may need to verify your identity")
                    
                    # Save new cookies
                    new_cookies = driver.get_cookies()
                    Path(cookies_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(cookies_file, 'w') as f:
                        json.dump(new_cookies, f)
                    print(f"✓ Saved new cookies to {cookies_file}")
                else:
                    print(f"\n❌ FAILED: Login unsuccessful")
                    print(f"Current URL: {current_url}")
                    
            except Exception as e:
                print(f"\n❌ ERROR during fresh login: {e}")
        else:
            print(f"\n⚠️  UNCERTAIN: Unexpected URL: {current_url}")
    else:
        print("❌ No cookies file found")
        print("Run the bot once to create cookies, or login manually")
    
    print("\n" + "="*70)
    print("TEST 3: Access Job Search Page")
    print("="*70)
    
    test_url = "https://www.linkedin.com/jobs/search/?keywords=Software+Engineer"
    print(f"Navigating to: {test_url}")
    driver.get(test_url)
    time.sleep(5)
    
    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    
    if "login" in current_url:
        print("❌ FAILED: Redirected to login (not authenticated)")
    elif "jobs" in current_url:
        print("✅ SUCCESS: Can access job search page")
        
        # Try to find job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container, li.jobs-search-results__list-item, div.base-card")
        print(f"Found {len(job_cards)} job cards on page")
        
        if len(job_cards) > 0:
            print("✅ Job cards are loading - scraper should work!")
        else:
            print("⚠️  No job cards found - may need to scroll or wait longer")
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    if "login" not in driver.current_url and ("feed" in driver.current_url or "jobs" in driver.current_url):
        print("✅ Authentication is WORKING")
        print("✅ Bot should be able to scrape jobs")
    else:
        print("❌ Authentication FAILED")
        print("❌ Bot will not be able to scrape jobs")
        print("\nTroubleshooting:")
        print("1. Check credentials in .env file")
        print("2. Delete cookies file and try fresh login")
        print("3. LinkedIn may require manual verification")
    
    print("\nBrowser will stay open for 30 seconds for inspection...")
    time.sleep(30)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\nBrowser closed.")
