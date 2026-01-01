"""
LinkedIn Job Scraper using Selenium
Handles JavaScript-rendered content and authentication
"""

import os
import json
import time
import logging
import re
from typing import List, Dict, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class LinkedInSeleniumScraper:
    """Scrapes LinkedIn jobs using Selenium for JavaScript-rendered content"""
    
    def __init__(self, email: str, password: str, headless: bool = True, country: str = 'Australia', country_code: str = 'AU'):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.cookies_file = './credentials/linkedin_cookies.json'
        self.country = country
        self.country_code = country_code
        
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logging.info("Chrome driver initialized")
    
    def _login(self) -> bool:
        """Login to LinkedIn"""
        try:
            # Try to load saved cookies first
            if self._load_cookies():
                logging.info("Loaded saved cookies, checking if still valid...")
                self.driver.get("https://www.linkedin.com/feed/")
                time.sleep(3)
                
                # Check if we're logged in
                if "feed" in self.driver.current_url:
                    logging.info("Successfully logged in with saved cookies")
                    return True
                else:
                    logging.info("Cookies expired, logging in with credentials...")
            
            # Login with credentials
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if login successful
            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                logging.info("Login successful")
                self._save_cookies()
                
                # Handle checkpoint/verification if present
                if "checkpoint" in self.driver.current_url:
                    logging.warning("LinkedIn requires verification. Please complete it manually.")
                    logging.warning("Waiting 60 seconds for manual verification...")
                    time.sleep(60)
                
                return True
            else:
                logging.error("Login failed - unexpected redirect")
                return False
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            return False
    
    def _save_cookies(self):
        """Save cookies to file for future use"""
        try:
            Path(self.cookies_file).parent.mkdir(parents=True, exist_ok=True)
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            logging.info(f"Saved cookies to {self.cookies_file}")
        except Exception as e:
            logging.warning(f"Could not save cookies: {e}")
    
    def _load_cookies(self) -> bool:
        """Load cookies from file"""
        try:
            if not Path(self.cookies_file).exists():
                return False
            
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            return True
        except Exception as e:
            logging.warning(f"Could not load cookies: {e}")
            return False
    
    def scrape_jobs(self, search_term: str, location: str = "", max_results: int = 50) -> List[Dict]:
        """Scrape LinkedIn feed posts about jobs"""
        try:
            if not self.driver:
                self._setup_driver()
            
            if not self._login():
                logging.error("Failed to login to LinkedIn")
                return []
            
            jobs = []
            
            from urllib.parse import quote_plus
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={quote_plus(search_term + ' hiring')}"
            
            logging.info(f"Searching LinkedIn posts: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while scroll_attempts < max_scrolls and len(jobs) < max_results:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                posts = self.driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2, div.update-components-text")
                
                logging.info(f"Found {len(posts)} posts on page")
                
                for post in posts:
                    if len(jobs) >= max_results:
                        break
                    
                    try:
                        job = self._parse_post(post, search_term)
                        if job and job['id'] not in [j['id'] for j in jobs]:
                            jobs.append(job)
                    except Exception as e:
                        logging.debug(f"Error parsing post: {e}")
                        continue
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                
                last_height = new_height
                scroll_attempts += 1
            
            logging.info(f"Scraped {len(jobs)} jobs from LinkedIn posts for '{search_term}'")
            return jobs
            
        except Exception as e:
            logging.error(f"Error scraping LinkedIn posts: {e}")
            return []
    
    def _parse_post(self, post, search_term: str) -> Optional[Dict]:
        """Parse a LinkedIn feed post"""
        try:
            post_text = post.text
            
            if not post_text or len(post_text) < 50:
                return None
            
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post_text)
            emails = list(set(emails))
            
            if not emails:
                return None
            
            try:
                author_elem = post.find_element(By.CSS_SELECTOR, ".update-components-actor__name, .feed-shared-actor__name")
                author = author_elem.text.strip()
            except:
                author = "Unknown"
            
            try:
                post_link_elem = post.find_element(By.CSS_SELECTOR, "a[href*='/feed/update/']")
                post_link = post_link_elem.get_attribute('href')
                post_id = re.search(r'urn:li:activity:(\d+)', post_link)
                post_id = post_id.group(1) if post_id else str(hash(post_text[:100]))
            except:
                post_id = str(hash(post_text[:100]))
                post_link = "https://www.linkedin.com/feed/"
            
            logging.info(f"✓ Found post with {len(emails)} email(s): {emails}")
            
            job_data = {
                'id': f"linkedin_post_{post_id}",
                'title': f"{search_term} - LinkedIn Post",
                'roleId': self._generate_role_id(search_term),
                'company': author,
                'jobLink': post_link,
                'applyLink': post_link,
                'salary': 'N/A',
                'workTypes': 'See post',
                'workArrangements': 'See post',
                'content': post_text,
                'description': post_text,
                'emails': emails,
                'phoneNumbers': [],
                'platform': 'linkedin',
                'location': 'See post',
                'joblocationInfo': {
                    'displayLocation': 'See post',
                    'location': 'See post',
                    'country': self.country,
                    'countryCode': self.country_code,
                }
            }
            
            return job_data
            
        except Exception as e:
            logging.debug(f"Error parsing post: {e}")
            return None
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse a LinkedIn job card"""
        try:
            # Try to find job link
            link_elem = card.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
            job_url = link_elem.get_attribute('href')
            
            # Extract job ID from URL
            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else 'unknown'
            
            # Extract title
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, ".job-card-list__title, h3")
                title = title_elem.text.strip()
            except:
                title = "Unknown"
            
            # Extract company
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name, h4")
                company = company_elem.text.strip()
            except:
                company = "Unknown"
            
            # Extract location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item, .job-card-container__location")
                location = location_elem.text.strip()
            except:
                location = "Unknown"
            
            # Click on job to get full description
            description = ""
            emails = []
            
            try:
                link_elem.click()
                time.sleep(2)
                
                # Get job description
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-description, .jobs-box__html-content")
                description = desc_elem.text
                
                logging.debug(f"Job {job_id} description length: {len(description)} chars")
                
                # Extract emails from description
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
                emails = list(set(emails))  # Remove duplicates
                
                if emails:
                    logging.info(f"✓ Found {len(emails)} email(s) in job {job_id}: {emails}")
                else:
                    logging.debug(f"No emails found in job {job_id}")
                
            except Exception as e:
                logging.debug(f"Could not get full description for job {job_id}: {e}")
            
            job_data = {
                'id': f"linkedin_{job_id}",
                'title': title,
                'roleId': self._generate_role_id(title),
                'company': company,
                'jobLink': job_url,
                'applyLink': job_url,
                'salary': 'N/A',
                'workTypes': 'Full time',
                'workArrangements': 'Office',
                'content': description,
                'emails': emails,
                'phoneNumbers': [],
                'platform': 'linkedin',
                'joblocationInfo': {
                    'displayLocation': location,
                    'location': location,
                    'country': self.country,
                    'countryCode': self.country_code,
                }
            }
            
            return job_data
            
        except Exception as e:
            logging.debug(f"Error parsing LinkedIn job card: {e}")
            return None
    
    def _generate_role_id(self, title: str) -> str:
        """Generate a role ID from job title"""
        role_id = re.sub(r'[^a-z0-9]+', '-', title.lower())
        role_id = role_id.strip('-')
        return role_id
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed")


def main():
    """Test the LinkedIn scraper"""
    from dotenv import load_dotenv
    load_dotenv()
    
    import json
    try:
        with open('./config/run_config.json', 'r') as f:
            config = json.load(f)
        country = config.get('country', 'Australia')
        country_code = config.get('countryCode', 'AU')
        location = config.get('suburbOrCity', 'Sydney, Australia')
    except:
        country = 'Australia'
        country_code = 'AU'
        location = 'Sydney, Australia'
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        logging.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")
        return
    
    scraper = LinkedInSeleniumScraper(
        email=email,
        password=password,
        headless=False,
        country=country,
        country_code=country_code
    )
    
    try:
        jobs = scraper.scrape_jobs("Software Engineer", location=location, max_results=10)
        
        print(f"\n Found {len(jobs)} jobs\n")
        
        for job in jobs[:5]:  # Show first 5
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['joblocationInfo']['displayLocation']}")
            print(f"Country: {job['joblocationInfo']['country']} ({job['joblocationInfo']['countryCode']})")
            print(f"Emails: {job['emails']}")
            print(f"Link: {job['jobLink']}")
            print("-" * 80)
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
