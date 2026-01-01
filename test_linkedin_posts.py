import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print("Going to LinkedIn feed search...")
    driver.get("https://www.linkedin.com/search/results/content/?keywords=software+engineer+hiring")
    time.sleep(5)
    
    print("\nLooking for feed posts...")
    selectors = [
        "div.feed-shared-update-v2",
        "div.update-components-text",
        "div[class*='feed']",
        "div[class*='update']",
        "article",
        "div.scaffold-finite-scroll__content > div"
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"Selector '{selector}': found {len(elements)} elements")
        if len(elements) > 0:
            print(f"  First element text preview: {elements[0].text[:200] if elements[0].text else 'NO TEXT'}")
    
    print("\n\nPage source preview (first 2000 chars):")
    print(driver.page_source[:2000])
    
except Exception as e:
    print(f"Error: {e}")
finally:
    input("\nPress Enter to close browser...")
    driver.quit()
