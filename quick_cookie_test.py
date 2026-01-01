import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

cookies_file = "./credentials/linkedin_cookies.json"

options = Options()
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("Step 1: Load LinkedIn homepage")
    driver.get("https://www.linkedin.com")
    time.sleep(2)
    
    print("Step 2: Add cookies")
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
    
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    
    print("Step 3: Navigate to feed (not refresh)")
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(5)
    
    print(f"\nResult URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    if "feed" in driver.current_url:
        print("\n✅ SUCCESS - Logged in!")
    else:
        print(f"\n❌ FAILED - Not logged in (URL: {driver.current_url})")
    
    input("\nCheck the browser - are you logged in? Press Enter...")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
