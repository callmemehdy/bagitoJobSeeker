"""
Multi-Platform Job Scraper
Scrapes from Seek, LinkedIn, and Indeed
"""

import asyncio
import logging
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class MultiPlatformScraper:
    """Scrapes jobs from multiple platforms"""
    
    PLATFORMS = {
        'seek': 'https://www.seek.com.au',
        'indeed': 'https://au.indeed.com',
    }
    
    def __init__(self, run_config):
        self.run_config = run_config
        self.platforms = run_config.get('platforms', ['seek', 'indeed'])
        
        # Get country settings from config
        self.country = run_config.get('country', 'Australia')
        self.country_code = run_config.get('countryCode', 'AU')
        
        # Check if Selenium should be used for LinkedIn
        self.use_selenium_for_linkedin = run_config.get('use_selenium_for_linkedin', False)
        
        # Check if email is required
        self.require_email = run_config.get('requireEmail', False)
        
    async def scrape(self) -> Dict[str, List]:
        """Scrape jobs from all enabled platforms"""
        try:
            all_data = {}
            
            for search_term in self.run_config['searchTerms']:
                logging.info(f"Scraping jobs for: {search_term}")
                jobs = []
                
                for platform in self.platforms:
                    try:
                        platform_jobs = await self._scrape_platform(platform, search_term)
                        
                        jobs_with_emails = [
                            job for job in platform_jobs 
                            if job.get('emails') and len(job['emails']) > 0
                        ]
                        
                        jobs.extend(jobs_with_emails)
                        logging.info(f"Found {len(jobs_with_emails)} jobs with emails on {platform} for '{search_term}'")
                        await asyncio.sleep(2)
                    except Exception as e:
                        logging.error(f"Failed to scrape {platform}: {e}")
                        continue
                
                all_data[search_term] = jobs
                logging.info(f"Total: {len(jobs)} jobs with emails for '{search_term}'")
            
            return all_data
            
        except Exception as e:
            logging.error(f"Multi-platform scraping failed: {e}")
            raise
    
    async def _scrape_platform(self, platform: str, search_term: str) -> List[Dict]:
        """Scrape jobs from a specific platform"""
        if platform == 'seek':
            return await self._scrape_seek(search_term)
        elif platform == 'indeed':
            return await self._scrape_indeed(search_term)
        elif platform == 'linkedin':
            return await self._scrape_linkedin(search_term)
        else:
            logging.warning(f"Unknown platform: {platform}")
            return []
    
    async def _scrape_seek(self, search_term: str) -> List[Dict]:
        """Scrape Seek jobs from HTML pages"""
        jobs = []
        max_results = self.run_config.get('maxResults', 100)
        page = 1
        
        try:
            async with AsyncSession(impersonate="chrome110") as session:
                while len(jobs) < max_results and page <= 3:  # Limit to 3 pages
                    location = self.run_config.get('suburbOrCity', '')
                    country_code = self.run_config.get('countryCode', 'AU').lower()
                    domain = f"seek.com.{country_code}" if country_code != 'au' else "seek.com.au"
                    
                    url = f"https://www.{domain}/jobs?keywords={quote_plus(search_term)}&where={quote_plus(location)}&page={page}"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                    
                    logging.info(f"Fetching Seek page {page}: {url}")
                    response = await session.get(url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        job_cards = soup.find_all('article', attrs={'data-testid': 'job-card'})
                        if not job_cards:
                            job_cards = soup.find_all('article', class_=re.compile(r'.*job.*card.*', re.I))
                        if not job_cards:
                            job_cards = soup.find_all('div', attrs={'data-card-type': 'JobCard'})
                        
                        if not job_cards:
                            logging.info(f"No jobs found on Seek page {page}")
                            break
                        
                        logging.info(f"Found {len(job_cards)} job cards on Seek page {page}")
                        
                        for card in job_cards:
                            if len(jobs) >= max_results:
                                break
                            job = self._parse_seek_job(card)
                            if job:
                                jobs.append(job)
                        
                        page += 1
                        await asyncio.sleep(2)  # Be polite
                    else:
                        logging.warning(f"Seek returned status {response.status_code}")
                        break
                    
        except Exception as e:
            logging.error(f"Error scraping Seek: {e}")
        
        logging.info(f"Found {len(jobs)} jobs with emails on seek for '{search_term}'")
        return jobs
    
    async def _scrape_linkedin(self, search_term: str) -> List[Dict]:
        """Scrape LinkedIn jobs using Selenium"""
        if not self.use_selenium_for_linkedin:
            logging.info("Selenium for LinkedIn is disabled in config")
            return []
        
        try:
            # Import here to avoid dependency if not used
            from .linkedin_selenium_scraper import LinkedInSeleniumScraper
            
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if not email or not password:
                logging.warning("LINKEDIN_EMAIL and LINKEDIN_PASSWORD not set in .env - skipping LinkedIn")
                return []
            
            logging.info("Using Selenium to scrape LinkedIn...")
            
            # Run Selenium scraper synchronously (Selenium doesn't support async)
            loop = asyncio.get_event_loop()
            jobs = await loop.run_in_executor(
                None,
                self._scrape_linkedin_sync,
                email,
                password,
                search_term
            )
            
            return jobs
            
        except ImportError as e:
            logging.error(f"Failed to import LinkedIn scraper: {e}")
            logging.error("Install with: uv add selenium webdriver-manager")
            return []
        except Exception as e:
            logging.error(f"Error scraping LinkedIn with Selenium: {e}")
            return []
    
    def _scrape_linkedin_sync(self, email: str, password: str, search_term: str) -> List[Dict]:
        """Synchronous LinkedIn scraping (called in executor)"""
        from .linkedin_selenium_scraper import LinkedInSeleniumScraper
        
        scraper = LinkedInSeleniumScraper(
            email=email,
            password=password,
            headless=True,
            country=self.country,
            country_code=self.country_code
        )
        
        try:
            location = self.run_config.get('suburbOrCity', '')
            max_results = self.run_config.get('maxResults', 50)
            
            jobs = scraper.scrape_jobs(search_term, location, max_results)
            return jobs
        finally:
            scraper.close()
    
    async def _scrape_indeed(self, search_term: str) -> List[Dict]:
        """Scrape Indeed jobs"""
        jobs = []
        max_results = self.run_config.get('maxResults', 100)
        page = 0
        
        try:
            async with AsyncSession(impersonate="chrome110") as session:
                while len(jobs) < max_results:
                    location = self.run_config.get('suburbOrCity', self.country)
                    url = f"https://au.indeed.com/jobs?q={quote_plus(search_term)}&l={quote_plus(location)}&start={page}"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html',
                    }
                    
                    response = await session.get(url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Indeed uses different selectors
                        job_cards = soup.find_all('div', class_=re.compile(r'job_seen_beacon'))
                        if not job_cards:
                            job_cards = soup.find_all('a', class_=re.compile(r'jcs-JobTitle'))
                        
                        if not job_cards:
                            break
                        
                        for card in job_cards:
                            job = self._parse_indeed_job(card, soup)
                            if job and len(jobs) < max_results:
                                jobs.append(job)
                        
                        page += 10
                        await asyncio.sleep(1)
                    else:
                        break
                        
        except Exception as e:
            logging.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def _parse_seek_job(self, card) -> Optional[Dict]:
        """Parse Seek job card from HTML"""
        try:
            link = card.find('a', attrs={'data-testid': 'job-card-title-link'})
            if not link:
                link = card.find('a', href=re.compile(r'/job/'))
            if not link:
                return None
            
            job_url = link.get('href', '')
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.seek.com.au{job_url}"
            
            job_id_match = re.search(r'/job/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else 'unknown'
            
            title = link.get_text(strip=True) if link else "Unknown"
            
            company_elem = card.find('a', attrs={'data-testid': 'job-card-company-link'})
            if not company_elem:
                company_elem = card.find('span', class_=re.compile(r'.*company.*', re.I))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = card.find('span', attrs={'data-testid': 'job-card-location'})
            if not location_elem:
                location_elem = card.find('span', class_=re.compile(r'.*location.*', re.I))
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            salary_elem = card.find('span', attrs={'data-testid': 'job-card-salary'})
            if not salary_elem:
                salary_elem = card.find('span', class_=re.compile(r'.*salary.*', re.I))
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
            
            desc_elem = card.find('span', attrs={'data-testid': 'job-card-snippet'})
            if not desc_elem:
                desc_elem = card.find('p', class_=re.compile(r'.*snippet.*', re.I))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
            
            job_data = {
                'id': f"seek_{job_id}",
                'title': title,
                'roleId': self._generate_role_id(title),
                'company': company,
                'jobLink': job_url,
                'applyLink': job_url,
                'salary': salary,
                'workTypes': 'Full time',
                'workArrangements': 'Office',
                'content': description,
                'emails': list(set(emails)),  # Remove duplicates
                'phoneNumbers': [],
                'platform': 'seek',
                'joblocationInfo': {
                    'displayLocation': location,
                    'location': location,
                    'country': self.country,
                    'countryCode': self.country_code,
                }
            }
            
            if self.require_email and not emails:
                return None
            
            return job_data
            
        except Exception as e:
            logging.warning(f"Error parsing Seek job: {e}")
            return None
    
    def _parse_indeed_job(self, card, soup) -> Optional[Dict]:
        """Parse Indeed job card"""
        try:
            # Find job link
            link = card.find('a', {'class': re.compile(r'jcs-JobTitle')})
            if not link:
                link = card.find('a')
            
            if not link:
                return None
            
            job_url = link.get('href', '')
            if job_url and not job_url.startswith('http'):
                job_url = f"https://au.indeed.com{job_url}"
            
            # Extract job ID
            job_id_match = re.search(r'jk=([a-f0-9]+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else 'unknown'
            
            # Extract title
            title = link.get_text(strip=True) if link else "Unknown"
            
            # Extract company
            company_elem = card.find('span', {'class': re.compile(r'companyName')})
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('div', {'class': re.compile(r'companyLocation')})
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract salary
            salary_elem = card.find('div', {'class': re.compile(r'salary')})
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
            
            # Extract snippet (short description)
            snippet_elem = card.find('div', {'class': re.compile(r'job-snippet')})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            return {
                'id': f"indeed_{job_id}",
                'title': title,
                'roleId': self._generate_role_id(title),
                'company': company,
                'jobLink': job_url,
                'applyLink': job_url,
                'salary': salary,
                'workTypes': 'Full time',
                'workArrangements': 'Office',
                'emails': [],
                'phoneNumbers': [],
                'platform': 'indeed',
                'joblocationInfo': {
                    'displayLocation': location,
                    'location': location,
                    'country': self.country,
                    'countryCode': self.country_code,
                },
                'snippet': snippet,  # Store snippet for later use
                'hasRoleRequirements': True,  # Indeed jobs need external application
                'isExternalApply': True,
                # Basic content from snippet
                'content': {
                    'unEditedContent': f"<p>{snippet}</p>" if snippet else f"<p>{title} at {company}</p>",
                    'sections': [
                        f"{title} at {company}",
                        f"Location: {location}",
                        f"Salary: {salary}" if salary != "N/A" else "",
                        snippet if snippet else "Visit Indeed for full job details."
                    ],
                    'bulletPoints': [f"Position: {title}", f"Company: {company}"],
                    'jobHook': snippet[:200] if snippet else f"{title} at {company}"
                }
            }
        except Exception as e:
            logging.warning(f"Error parsing Indeed job: {e}")
            return None
    
    def _generate_role_id(self, title: str) -> str:
        """Generate a role ID from job title"""
        role_id = re.sub(r'[^a-z0-9]+', '-', title.lower())
        role_id = role_id.strip('-')
        return role_id
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Remove duplicates and common false positives
        valid_emails = []
        invalid_domains = ['example.com', 'test.com', 'domain.com', 'email.com']
        
        for email in set(emails):
            email = email.lower()
            domain = email.split('@')[1] if '@' in email else ''
            if domain not in invalid_domains and len(email) > 5:
                valid_emails.append(email)
        
        return valid_emails
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))
