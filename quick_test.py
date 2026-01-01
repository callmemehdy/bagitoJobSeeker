import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')

options = Options()
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("Logging in...")
    driver.get("https://www.linkedin.com")
    time.sleep(2)
    
    driver.get("https://www.linkedin.com/search/results/content/?keywords=Software+Engineer+hiring")
    time.sleep(6)
    
    posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
    print(f"\nFound {len(posts)} posts\n")
    
    for i, post in enumerate(posts[:3], 1):
        text = post.text
        print(f"--- POST {i} ---")
        print(f"Length: {len(text)} chars")
        print(f"Preview: {text[:300]}")
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        print(f"Emails found: {emails if emails else 'NONE'}")
        print()
        
finally:
    input("Press Enter to close...")
    driver.quit()
