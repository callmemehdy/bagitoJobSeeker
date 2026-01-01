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
    driver.get("https://www.linkedin.com")
    time.sleep(2)
    
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.refresh()
        time.sleep(5)
    
    # Just go to feed and let user search manually
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(3)
    
    print("\n" + "="*70)
    print("LINKEDIN FEED LOADED")
    print("="*70)
    print("\nInstructions:")
    print("1. Use LinkedIn's search bar")
    print("2. Search for: 'software engineer hiring'")
    print("3. Look at the posts")
    print("4. Do you see ANY emails in the visible posts?")
    print("\nLet me know what you see!")
    print("="*70 + "\n")
    
    input("Press Enter when done...")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
