#!/usr/bin/env python3
import os
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
print("FRESH LINKEDIN LOGIN")
print("="*70)
print(f"Email: {email}")
print(f"Password: {'*' * len(password)}")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("\n1. Going to LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    
    print("2. Entering credentials...")
    
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    email_field.clear()
    email_field.send_keys(email)
    
    password_field = driver.find_element(By.ID, "password")
    password_field.clear()
    password_field.send_keys(password)
    
    print("3. Clicking Sign In...")
    sign_in_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    sign_in_btn.click()
    
    print("4. Waiting for login (10 seconds)...")
    time.sleep(10)
    
    current_url = driver.current_url
    print(f"\nCurrent URL: {current_url}")
    
    if "checkpoint" in current_url:
        print("\n⚠️  LinkedIn Security Checkpoint Detected!")
        print("Please complete verification in the browser...")
        input("Press Enter after completing verification...")
        time.sleep(3)
        current_url = driver.current_url
    
    if "feed" in current_url or "mynetwork" in current_url:
        print("\n✅ LOGIN SUCCESSFUL!")
        
        # Save cookies
        cookies = driver.get_cookies()
        Path(cookies_file).parent.mkdir(parents=True, exist_ok=True)
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✅ Saved {len(cookies)} cookies to {cookies_file}")
        
        # Test accessing job search
        print("\n5. Testing job search access...")
        driver.get("https://www.linkedin.com/jobs/search/?keywords=Software+Engineer")
        time.sleep(5)
        
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container, li.jobs-search-results__list-item, div.base-card")
        print(f"✅ Found {len(job_cards)} job cards")
        
        print("\n" + "="*70)
        print("SUCCESS! You are now logged in.")
        print("The bot can now scrape LinkedIn jobs.")
        print("="*70)
        
    else:
        print(f"\n❌ LOGIN FAILED")
        print(f"Current URL: {current_url}")
        print("Please check credentials in .env file")
    
    print("\nBrowser will stay open for 20 seconds...")
    time.sleep(20)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\nBrowser closed.")
