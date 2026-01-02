"""
LinkedIn Post Scraper using Selenium
Scrapes LinkedIn feed posts searching for job opportunities with emails
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class LinkedInPostScraper:
    """Scrapes LinkedIn feed posts for job opportunities"""
    
    def __init__(self, email: str, password: str, headless: bool = True, location: str = ""):
        self.email = email
        self.password = password
        self.headless = headless
        self.location = location
        self.driver = None
        self.cookies_file = './credentials/linkedin_cookies.json'
        
    def _setup_driver(self):
        """Setup Chrome driver with anti-detection options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Essential stability options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional prefs to prevent crashes
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(60)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logging.info("Chrome driver initialized")
    
    def _login(self) -> bool:
        """Login to LinkedIn"""
        try:
            # Try cookies first
            if self._load_cookies():
                logging.info("Checking if cookies are still valid...")
                try:
                    # Use smaller timeout for cookie validation
                    self.driver.set_page_load_timeout(10)
                    self.driver.get("https://www.linkedin.com/feed/")
                    time.sleep(3)
                    
                    current_url = self.driver.current_url
                    logging.info(f"After cookie load, current URL: {current_url}")
                    
                    if "feed" in current_url:
                        logging.info("Successfully logged in with saved cookies")
                        self.driver.set_page_load_timeout(60)
                        return True
                    else:
                        logging.info("Cookies expired or invalid, will login with credentials...")
                except TimeoutException:
                    logging.warning("Feed page timeout, stopping page load...")
                    try:
                        self.driver.execute_script("window.stop();")
                        time.sleep(1)
                        if "feed" in self.driver.current_url:
                            logging.info("Successfully logged in (page stopped but we're on feed)")
                            self.driver.set_page_load_timeout(60)
                            return True
                    except:
                        pass
                    logging.info("Cookies didn't work, will login with credentials...")
                except Exception as e:
                    logging.warning(f"Error validating cookies: {e}")
                    logging.info("Will login with credentials...")
            
            # Reset timeout
            self.driver.set_page_load_timeout(60)
            
            # Login with credentials
            logging.info("Logging in with credentials...")
            
            # Check if already on login page
            current_url = self.driver.current_url
            if "login" not in current_url and "uas/login" not in current_url:
                self.driver.get("https://www.linkedin.com/login")
                time.sleep(3)
            else:
                logging.info("Already on login page")
                time.sleep(2)
            
            try:
                # Wait for and fill in email
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_field.clear()
                time.sleep(0.5)
                email_field.send_keys(self.email)
                logging.info("Email entered")
                
                # Fill in password
                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(self.password)
                logging.info("Password entered")
                
                # Click login button
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                logging.info("Login button clicked, waiting for redirect...")
                
                # Wait for redirect
                time.sleep(5)
                
                current_url = self.driver.current_url
                logging.info(f"After login, current URL: {current_url}")
                
                if "feed" in current_url:
                    logging.info("Login successful - reached feed")
                    self._save_cookies()
                    return True
                elif "checkpoint" in current_url or "challenge" in current_url:
                    logging.warning("LinkedIn security challenge detected!")
                    if not self.headless:
                        logging.info("Please complete the security challenge in the browser...")
                        input("Press Enter after completing the challenge...")
                        if "feed" in self.driver.current_url:
                            logging.info("Challenge completed, login successful")
                            self._save_cookies()
                            return True
                    else:
                        logging.error("Security challenge requires manual intervention. Run with headless=False")
                        return False
                else:
                    logging.error(f"Login failed. Current URL: {current_url}")
                    # Take screenshot for debugging
                    try:
                        self.driver.save_screenshot("/tmp/linkedin_login_failed.png")
                        logging.info("Screenshot saved to /tmp/linkedin_login_failed.png")
                    except:
                        pass
                    return False
            except Exception as e:
                logging.error(f"Error during login form submission: {e}")
                return False
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_cookies(self):
        """Save cookies to file"""
        try:
            os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            logging.debug("Cookies saved")
        except Exception as e:
            logging.error(f"Error saving cookies: {e}")
    
    def _load_cookies(self) -> bool:
        """Load cookies from file"""
        try:
            if not os.path.exists(self.cookies_file):
                logging.info("No saved cookies found")
                return False
            
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            if not cookies:
                logging.info("Cookie file is empty")
                return False
            
            # Load LinkedIn first
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            # Add cookies
            cookies_added = 0
            for cookie in cookies:
                try:
                    # Remove problematic fields
                    cookie.pop('sameSite', None)
                    cookie.pop('expiry', None)
                    self.driver.add_cookie(cookie)
                    cookies_added += 1
                except Exception as e:
                    logging.debug(f"Could not add cookie {cookie.get('name', 'unknown')}: {e}")
            
            logging.info(f"Loaded {cookies_added} cookies successfully")
            return cookies_added > 0
            
        except Exception as e:
            logging.error(f"Error loading cookies: {e}")
            # If cookies are corrupted, delete them
            try:
                if os.path.exists(self.cookies_file):
                    os.remove(self.cookies_file)
                    logging.info("Deleted corrupted cookie file")
            except:
                pass
            return False
    
    def scrape_posts(self, search_term: str, max_results: int = 50) -> List[Dict]:
        """Scrape LinkedIn posts by searching for posts only"""
        try:
            if not self.driver:
                self._setup_driver()
            
            if not self._login():
                logging.error("Failed to login to LinkedIn")
                return []
            
            posts = []
            
            # Skip the feed entirely - go straight to posts search
            logging.info("Navigating directly to posts search...")
            
            # Build search URL with location if provided
            search_query = search_term.replace(' ', '%20')
            if self.location:
                search_query = f"{search_query}%20{self.location.replace(' ', '%20')}"
                logging.info(f"Including location in search: {self.location}")
            
            # Use posts-only search filter
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_query}&sortBy=%22date_posted%22"
            logging.info(f"Searching LinkedIn posts: {search_url}")
            
            try:
                self.driver.set_page_load_timeout(20)
                self.driver.get(search_url)
                time.sleep(3)
            except TimeoutException:
                logging.warning("Search page taking long to load, stopping page load...")
                try:
                    self.driver.execute_script("window.stop();")
                    time.sleep(2)
                except:
                    pass
            finally:
                self.driver.set_page_load_timeout(60)
            
            # Wait for search results
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main, div.search-results-container, div.scaffold-finite-scroll__content"))
                )
                logging.info("Search page loaded successfully")
            except TimeoutException:
                logging.warning("Timeout waiting for search page, but continuing anyway...")
            
            time.sleep(2)
            
            # Check current URL
            current_url = self.driver.current_url
            logging.info(f"Current URL: {current_url}")
            
            if "checkpoint" in current_url or "challenge" in current_url:
                logging.error("LinkedIn security challenge detected!")
                logging.error("Please complete the challenge manually")
                return []
            
            # Check if there are any results
            try:
                no_results = self.driver.find_elements(By.CSS_SELECTOR, ".search-results-container__no-results, .artdeco-empty-state")
                if no_results and len(no_results) > 0:
                    logging.warning("No search results found for this query")
                    return []
            except:
                pass
            
            logging.info("Starting to scrape posts...")
            
            # Scroll to load more posts
            scroll_attempts = 0
            max_scrolls = 10
            stale_count = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while scroll_attempts < max_scrolls and len(posts) < max_results and stale_count < 3:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Find all post containers - use specific selectors for search results
                post_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                    "li.reusable-search__result-container, div.feed-shared-update-v2")
                
                logging.info(f"Found {len(post_containers)} post containers on page (Posts collected so far: {len(posts)})")
                
                if len(post_containers) == 0:
                    logging.warning("No post containers found, page might still be loading...")
                    stale_count += 1
                    time.sleep(2)
                    continue
                
                for container in post_containers:
                    if len(posts) >= max_results:
                        break
                    
                    try:
                        post = self._parse_post(container, search_term)
                        if post:
                            # Check for duplicates
                            if post['id'] not in [p['id'] for p in posts]:
                                posts.append(post)
                                logging.info(f"✓ Found post with {len(post.get('emails', []))} email(s): {post.get('emails', [])}")
                    except (StaleElementReferenceException, Exception) as e:
                        logging.debug(f"Error parsing post: {e}")
                        continue
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                    logging.debug(f"Page height unchanged ({scroll_attempts}/{max_scrolls})")
                else:
                    scroll_attempts = 0
                    last_height = new_height
                    stale_count = 0
            
            logging.info(f"Scraped {len(posts)} posts with emails from LinkedIn for '{search_term}'")
            
            if len(posts) == 0:
                logging.warning("No posts with emails found. This could mean:")
                logging.warning("1. No posts about this topic contain public emails")
                logging.warning("2. Try more specific/popular search terms (e.g., 'hiring', 'recruiting')")
                logging.warning("3. LinkedIn posts rarely contain emails - consider scraping job boards instead")
            
            return posts
            
        except Exception as e:
            logging.error(f"Error scraping LinkedIn posts: {e}")
            return []
    
    def _parse_post(self, container, search_term: str) -> Optional[Dict]:
        """Parse a LinkedIn post container"""
        try:
            # Try to expand "see more" to get full post text
            try:
                see_more = container.find_element(By.CSS_SELECTOR, "button[aria-label*='see more'], button.feed-shared-inline-show-more-text__see-more-less-toggle")
                self.driver.execute_script("arguments[0].click();", see_more)
                time.sleep(0.5)
            except:
                pass
            
            # Get post text
            post_text = ""
            text_selectors = [
                ".feed-shared-update-v2__description",
                ".feed-shared-text",
                ".update-components-text",
                ".break-words",
                ".feed-shared-inline-show-more-text"
            ]
            
            for selector in text_selectors:
                try:
                    text_elem = container.find_element(By.CSS_SELECTOR, selector)
                    post_text = text_elem.text
                    if post_text and len(post_text) > 50:
                        break
                except:
                    continue
            
            logging.debug(f"Post text length: {len(post_text)} chars")
            
            if not post_text or len(post_text) < 50:
                logging.debug("Post text too short, skipping")
                return None
            
            # Extract emails from post text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post_text)
            emails = list(set(emails))  # Remove duplicates
            
            # Filter out common non-personal emails
            filtered_emails = [
                email for email in emails 
                if not any(domain in email.lower() for domain in ['noreply', 'linkedin.com', 'example.com'])
            ]
            
            logging.debug(f"Found {len(filtered_emails)} email(s) in post")
            
            if not filtered_emails:
                logging.debug("No valid emails found, skipping")
                return None
            
            # Get author info
            author = "Unknown"
            try:
                author_elem = container.find_element(By.CSS_SELECTOR, ".update-components-actor__name, .feed-shared-actor__name, span[dir='ltr']")
                author = author_elem.text.strip()
            except:
                pass
            
            # Get post link
            post_link = ""
            post_id = f"linkedin_post_{int(time.time() * 1000)}"
            try:
                # Try to get the post permalink
                permalink = container.find_element(By.CSS_SELECTOR, "a[href*='/feed/update/'], a[href*='activity']")
                post_link = permalink.get_attribute('href')
                # Extract ID from URL
                id_match = re.search(r'urn:li:activity:(\d+)', post_link)
                if id_match:
                    post_id = f"linkedin_post_{id_match.group(1)}"
            except:
                pass
            
            # Get timestamp
            timestamp = ""
            try:
                time_elem = container.find_element(By.CSS_SELECTOR, "time, .update-components-actor__sub-description")
                timestamp = time_elem.get_attribute('datetime') or time_elem.text
            except:
                pass
            
            return {
                'id': post_id,
                'title': f"LinkedIn Post by {author} - {search_term}",
                'company': author,
                'location': "LinkedIn Post",
                'jobLink': post_link,
                'applyLink': post_link,
                'content': post_text[:500],  # First 500 chars
                'emails': filtered_emails,
                'timestamp': timestamp,
                'source': 'linkedin_posts'
            }
            
        except Exception as e:
            logging.debug(f"Error parsing post container: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser closed")
            except:
                pass
