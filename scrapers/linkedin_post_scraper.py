"""
LinkedIn Post Scraper using Selenium
Scrapes LinkedIn feed posts searching for job opportunities with emails
"""

import os
import json
import time
import logging
import re
import hashlib
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
        
        # DON'T use incognito - we need cookies to work
        # chrome_options.add_argument('--incognito')  # REMOVED - prevents cookies
        
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
            # Try cookies first - avoid re-login every time
            if self._load_cookies():
                logging.info("Checking if cookies are still valid...")
                try:
                    # Use smaller timeout for cookie validation
                    self.driver.set_page_load_timeout(10)
                    self.driver.get("https://www.linkedin.com/feed/")
                    time.sleep(3)
                    
                    current_url = self.driver.current_url
                    logging.info(f"After cookie load, current URL: {current_url}")
                    
                    # Check if we're logged in (not redirected to login)
                    if "feed" in current_url and "login" not in current_url and "uas/login" not in current_url:
                        logging.info("✓ Successfully logged in with saved cookies")
                        self.driver.set_page_load_timeout(60)
                        return True
                    else:
                        logging.info("Cookies expired or invalid, will login with credentials...")
                except TimeoutException:
                    logging.warning("Feed page timeout, stopping page load...")
                    try:
                        self.driver.execute_script("window.stop();")
                        time.sleep(1)
                        current = self.driver.current_url
                        if "feed" in current and "login" not in current:
                            logging.info("✓ Successfully logged in (page stopped but we're on feed)")
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
                # Check if it's the "Welcome Back" page with pre-filled email
                try:
                    time.sleep(2)  # Wait for page to fully load
                    # Look for "Sign in using another account" link - indicates Welcome Back page
                    another_account = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign in using another account')]")
                    if another_account:
                        logging.info("Detected 'Welcome Back' page with saved email")
                        # Click to use another account to get to standard login
                        another_account[0].click()
                        time.sleep(3)  # Wait for page transition
                        logging.info("Clicked 'Sign in using another account'")
                except Exception as e:
                    logging.debug(f"No 'Welcome Back' page detected (or error): {e}")
                
                # Wait for and fill in email - with better wait condition
                logging.info("Waiting for email field...")
                email_field = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "username"))
                )
                
                # Debug: Check if credentials are loaded
                logging.info(f"Email to use: {self.email[:5]}...@..." if self.email else "❌ EMAIL IS EMPTY!")
                logging.info(f"Password loaded: {'Yes' if self.password else '❌ NO PASSWORD!'}")
                
                if not self.email or not self.password:
                    logging.error("❌ Credentials are empty! Check your .env file")
                    logging.error(f"   LINKEDIN_EMAIL: {self.email}")
                    logging.error(f"   LINKEDIN_PASSWORD: {'***' if self.password else 'NOT SET'}")
                    return False
                
                # Click to focus, then clear
                email_field.click()
                time.sleep(0.5)
                email_field.clear()
                time.sleep(0.5)
                
                # Type email character by character (more human-like)
                logging.info("Typing email...")
                for char in self.email:
                    email_field.send_keys(char)
                    time.sleep(0.08)  # Slightly slower typing
                logging.info("✓ Email entered")
                
                time.sleep(1)
                
                # Fill in password - wait for field to be ready
                logging.info("Waiting for password field...")
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "password"))
                )
                password_field.click()
                time.sleep(0.5)
                password_field.clear()
                time.sleep(0.5)
                
                logging.info("Typing password...")
                for char in self.password:
                    password_field.send_keys(char)
                    time.sleep(0.08)
                logging.info("✓ Password entered")
                
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
                logging.info(f"Searching in country: {self.location}")
            
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
            
            # Check if redirected to login - cookies failed
            if "uas/login" in current_url or "/login" in current_url:
                logging.error("❌ LinkedIn redirected to login - cookies are not working!")
                logging.error("This means LinkedIn detected the bot despite using cookies.")
                logging.error("")
                logging.error("SOLUTIONS:")
                logging.error("1. Run 'make login' to regenerate cookies with fresh session")
                logging.error("2. LinkedIn may be blocking automated access - try again later")
                logging.error("3. Consider using regular job search instead of post search")
                logging.error("   (Regular job search is more reliable and less detectable)")
                return []
            
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
            
            # Save initial page HTML for debugging
            try:
                with open("linkedin_debug_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logging.info("📄 Saved initial page HTML to linkedin_debug_page.html")
            except Exception as e:
                logging.debug(f"Could not save debug HTML: {e}")
            
            # Track processed posts to avoid duplicates
            processed_post_ids = set()
            
            # Scroll to load more posts
            scroll_attempts = 0
            max_scrolls = 15  # Increased from 10
            stale_count = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            last_post_count = 0
            
            while scroll_attempts < max_scrolls and stale_count < 5:  # Allow more stale attempts
                # Human-like progressive scrolling - scroll to EACH post individually
                logging.info(f"🔽 Scroll attempt {scroll_attempts + 1}/{max_scrolls}")
                
                # Find all post containers FIRST
                post_containers = []
                
                # Strategy 1: Traditional selectors (may still work)
                containers_1 = self.driver.find_elements(By.CSS_SELECTOR, 
                    "li.reusable-search__result-container, div.feed-shared-update-v2")
                post_containers.extend(containers_1)
                
                # Strategy 2: Look for divs with multiple obfuscated classes (LinkedIn's pattern)
                if len(post_containers) == 0:
                    try:
                        main_element = self.driver.find_element(By.TAG_NAME, "main")
                        potential_posts = main_element.find_elements(By.XPATH, 
                            ".//div[contains(@class, '_') and string-length(@class) > 100]")
                        
                        seen = set()
                        for elem in potential_posts[:50]:
                            try:
                                elem_id = elem.get_attribute('class')
                                if elem_id not in seen:
                                    seen.add(elem_id)
                                    post_containers.append(elem)
                            except:
                                pass
                    except Exception as e:
                        logging.debug(f"Strategy 2 failed: {e}")
                
                # Strategy 3: Look for list items in main
                if len(post_containers) == 0:
                    try:
                        main_element = self.driver.find_element(By.TAG_NAME, "main")
                        list_items = main_element.find_elements(By.TAG_NAME, "li")
                        post_containers.extend(list_items[:20])
                    except Exception as e:
                        logging.debug(f"Strategy 3 failed: {e}")
                
                logging.info(f"Found {len(post_containers)} post containers on page (Posts collected so far: {len(posts)})")
                logging.info(f"   Processed {len(processed_post_ids)} unique containers, found {len(posts)} posts with emails")
                
                if len(post_containers) == 0:
                    logging.warning("No post containers found, page might still be loading...")
                    
                    # Debug: Try to find what elements ARE on the page
                    all_lis = self.driver.find_elements(By.TAG_NAME, "li")
                    all_divs_with_class = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='result'], div[class*='update']")
                    logging.debug(f"Debug: Found {len(all_lis)} <li> tags and {len(all_divs_with_class)} divs with 'result' or 'update' in class")
                    
                    # Save page source for debugging
                    if stale_count == 0:
                        try:
                            with open("linkedin_debug_page.html", "w", encoding="utf-8") as f:
                                f.write(self.driver.page_source)
                            logging.info("Saved page source to linkedin_debug_page.html for inspection")
                        except:
                            pass
                    
                    stale_count += 1
                    time.sleep(2)
                    
                    # Try scrolling anyway
                    try:
                        main_container = self.driver.find_element(By.TAG_NAME, "main")
                        self.driver.execute_script("arguments[0].scrollBy(0, 1000);", main_container)
                        time.sleep(2)
                    except:
                        self.driver.execute_script("window.scrollBy(0, 1000);")
                        time.sleep(2)
                    
                    scroll_attempts += 1
                    continue
                
                # Process each post container individually
                for idx, container in enumerate(post_containers):
                    if len(posts) >= max_results:
                        break
                    
                    try:
                        # Scroll THIS specific post into view to load its content
                        logging.info(f"   📌 Processing post {idx + 1}/{len(post_containers)}")
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container)
                        time.sleep(1)  # Wait for content to load
                        
                        # Generate a quick ID to check if we've seen this container
                        try:
                            container_text = container.text[:100]
                            container_id = hashlib.md5(container_text.encode()).hexdigest()
                            
                            # Skip if already processed
                            if container_id in processed_post_ids:
                                continue
                            
                            processed_post_ids.add(container_id)
                        except:
                            pass
                        
                        post = self._parse_post(container, search_term)
                        if post:
                            # Check for duplicates by post ID
                            if post['id'] not in [p['id'] for p in posts]:
                                posts.append(post)
                                logging.info(f"✓ Found post with {len(post.get('emails', []))} email(s): {post.get('emails', [])}")
                        else:
                            # Debug: Save first few containers that didn't yield posts
                            if scroll_attempts == 0 and len(posts) == 0:
                                try:
                                    text_sample = container.text[:200] if container.text else "NO TEXT"
                                    logging.debug(f"Container skipped. Text sample: {text_sample}")
                                except:
                                    pass
                    except (StaleElementReferenceException, Exception) as e:
                        logging.debug(f"Error parsing post: {e}")
                        continue
                
                # Check if we found new posts this scroll
                if len(posts) == last_post_count:
                    stale_count += 1
                    logging.debug(f"No new posts found ({stale_count}/5)")
                else:
                    stale_count = 0
                    last_post_count = len(posts)
                    logging.info(f"✅ Found new posts! Total now: {len(posts)}")
                
                # Scroll down to load more posts for next iteration
                try:
                    main_container = self.driver.find_element(By.TAG_NAME, "main")
                    # Scroll to bottom of main container
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_container)
                    logging.info(f"   ⬇️  Scrolled to bottom to load more posts")
                    time.sleep(2)  # Wait for new content to load
                except:
                    # Fallback to window scroll
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                
                scroll_attempts += 1
                
                # Don't double-increment scroll_attempts
                # (already incremented above)
            
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
                # Try multiple see more button selectors
                see_more_buttons = container.find_elements(By.CSS_SELECTOR, 
                    "button[aria-label*='see more'], "
                    "button[aria-label*='Show more'], "
                    "button.feed-shared-inline-show-more-text__see-more-less-toggle, "
                    "button.feed-shared-inline-show-more-text__button, "
                    "span.feed-shared-inline-show-more-text__button, "
                    "button.feed-shared-text-view-more, "
                    "button[class*='see-more'], "
                    "button[class*='show-more']"
                )
                
                if see_more_buttons:
                    logging.debug(f"Found {len(see_more_buttons)} 'see more' button(s)")
                    for button in see_more_buttons:
                        try:
                            # Check if button is visible and clickable
                            if button.is_displayed():
                                # Scroll button into view first
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                time.sleep(0.3)
                                # Click using JavaScript (more reliable)
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(0.8)  # Wait for expansion
                                logging.debug("✓ Expanded 'see more' button")
                        except Exception as e:
                            logging.debug(f"Failed to click see more: {e}")
                            continue
            except Exception as e:
                logging.debug(f"Error finding see more buttons: {e}")
            
            # Get post text - try multiple strategies
            post_text = ""
            
            # Wait a bit after expansion to let content load
            time.sleep(0.5)
            
            # Strategy 1: Known selectors - try each one
            text_selectors = [
                ".feed-shared-update-v2__description",
                ".feed-shared-text",
                ".update-components-text",
                ".break-words",
                ".feed-shared-inline-show-more-text",
                "[data-testid='expandable-text-box']",
                "div[dir='ltr']",  # Often used for text content
                ".artdeco-card__body",
                ".feed-shared-text-view",
                "span[dir='ltr']"
            ]
            
            for selector in text_selectors:
                try:
                    text_elems = container.find_elements(By.CSS_SELECTOR, selector)
                    for text_elem in text_elems:
                        text = text_elem.text
                        if text and len(text) > len(post_text):
                            post_text = text
                            logging.debug(f"Found longer text using selector: {selector} ({len(text)} chars)")
                except:
                    continue
            
            # Strategy 2: Get all visible text from container
            if not post_text or len(post_text) < 50:
                try:
                    full_text = container.text
                    if full_text and len(full_text) > len(post_text):
                        post_text = full_text
                        logging.debug(f"Using container.text, got {len(full_text)} chars")
                except:
                    pass
            
            logging.debug(f"Post text length: {len(post_text)} chars")
            
            # Don't skip if no text - still log it for debugging
            if not post_text or len(post_text) < 20:
                logging.debug(f"Post text too short ({len(post_text)} chars), checking HTML...")
                try:
                    html = container.get_attribute('innerHTML')
                    logging.debug(f"Container HTML length: {len(html)} chars")
                    # Try to extract text from HTML
                    post_text = container.text or ""
                except:
                    pass
                
                if not post_text or len(post_text) < 20:
                    logging.debug("Still no text found, skipping this container")
                    return None
            
            # IMPORTANT: Also extract emails from mailto links in HTML!
            # LinkedIn often wraps emails in <a href="mailto:..."> tags
            emails_from_links = []
            try:
                # Get all mailto links
                mailto_links = container.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
                for link in mailto_links:
                    href = link.get_attribute('href')
                    if href:
                        # Extract email from mailto:email@domain.com
                        email = href.replace('mailto:', '').strip()
                        if email and '@' in email:
                            emails_from_links.append(email)
                            logging.debug(f"Found email in mailto link: {email}")
            except Exception as e:
                logging.debug(f"Error extracting mailto links: {e}")
            
            # Extract emails from post text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post_text)
            
            # Combine emails from text and mailto links
            emails.extend(emails_from_links)
            emails = list(set(emails))  # Remove duplicates
            
            logging.debug(f"Raw emails found: {emails}")
            
            # Filter out personal/generic email domains (Gmail, Yahoo, Hotmail, etc.)
            # Only keep professional/company emails
            personal_domains = [
                # Common personal email providers
                'gmail.com', 'googlemail.com',
                'yahoo.com', 'yahoo.fr', 'yahoo.co.uk',
                'hotmail.com', 'hotmail.fr', 'hotmail.co.uk',
                'outlook.com', 'outlook.fr',
                'live.com', 'live.fr',
                'icloud.com', 'me.com', 'mac.com',
                'aol.com', 'protonmail.com', 'proton.me',
                'mail.com', 'gmx.com', 'gmx.fr',
                'yandex.com', 'yandex.ru',
                'zoho.com', 'zohomail.com',
                # Invalid/test domains
                'linkedin.com', 'example.com',
                'test.com', 'temp.com', 'tempmail.com'
            ]
            
            filtered_emails = []
            for email in emails:
                email_lower = email.lower()
                # Extract domain from email
                if '@' in email_lower:
                    domain = email_lower.split('@')[1]
                    local_part = email_lower.split('@')[0]
                    
                    # Skip if local part contains noreply/no-reply
                    if 'noreply' in local_part or 'no-reply' in local_part:
                        logging.debug(f"✗ Skipped noreply email: {email}")
                        continue
                    
                    # Check if it's a personal domain
                    if not any(personal_domain in domain for personal_domain in personal_domains):
                        filtered_emails.append(email)
                        logging.debug(f"✓ Professional email: {email}")
                    else:
                        logging.debug(f"✗ Skipped personal email: {email} (domain: {domain})")
            
            logging.debug(f"Filtered emails (professional only): {filtered_emails}")
            
            # Log post preview even if no emails
            preview = post_text[:150].replace('\n', ' ')
            if not filtered_emails:
                logging.info(f"ℹ️  Post found but no emails: '{preview}...'")
                
                # Save full post text to debug file for analysis
                try:
                    with open("linkedin_posts_no_emails.txt", "a", encoding="utf-8") as f:
                        f.write("="*80 + "\n")
                        f.write(f"POST (No emails found)\n")
                        f.write(f"Length: {len(post_text)} chars\n")
                        f.write("="*80 + "\n")
                        f.write(post_text)
                        f.write("\n\n")
                except:
                    pass
                
                return None
            
            # Get author info
            author = "Unknown"
            try:
                author_elem = container.find_element(By.CSS_SELECTOR, ".update-components-actor__name, .feed-shared-actor__name, span[dir='ltr']")
                author = author_elem.text.strip()
            except:
                pass
            
            # Get post link and generate ID
            post_link = ""
            post_id = None
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
            
            # If no post ID found, generate one from content hash to avoid duplicates
            if not post_id:
                content_hash = hashlib.md5(post_text[:500].encode()).hexdigest()
                post_id = f"linkedin_post_{content_hash}"
            
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
                'content': post_text,  # Full post text for job description
                'description': post_text,  # Also add as description field
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
