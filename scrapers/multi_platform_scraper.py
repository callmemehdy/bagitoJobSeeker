"""
Multi-Platform Job Scraper
Scrapes from Seek, LinkedIn, and Indeed
"""

import asyncio
import logging
import json
import re
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
    
    def __init__(self, run_config, cached_data_path='./info.json'):
        self.run_config = run_config
        self.cached_data_path = cached_data_path
        self.links_path = './links.json'  # For jobs without emails
        self.platforms = run_config.get('platforms', ['seek', 'indeed'])
        
        # Get country settings from config
        self.country = run_config.get('country', 'Australia')
        self.country_code = run_config.get('countryCode', 'AU')
        
    async def scrape(self) -> Dict[str, List]:
        """Scrape jobs from all enabled platforms"""
        try:
            all_data = {}
            jobs_without_emails = []  # Track jobs without emails but with apply links
            
            for search_term in self.run_config['searchTerms']:
                logging.info(f"Scraping jobs for: {search_term}")
                jobs = []
                
                # Scrape from each platform
                for platform in self.platforms:
                    try:
                        platform_jobs = await self._scrape_platform(platform, search_term)
                        
                        # Separate jobs with emails vs just links
                        jobs_with_emails = []
                        for job in platform_jobs:
                            if job.get('emails') and len(job['emails']) > 0:
                                jobs_with_emails.append(job)
                            elif job.get('applyLink') or job.get('jobLink'):
                                # Has apply link but no email - save to links.json
                                jobs_without_emails.append(job)
                                logging.info(f"Job without email but with link: {job['id']} - {job['title']}")
                        
                        jobs.extend(jobs_with_emails)
                        logging.info(f"Found {len(jobs_with_emails)} jobs with emails on {platform} for '{search_term}'")
                        await asyncio.sleep(2)
                    except Exception as e:
                        logging.error(f"Failed to scrape {platform}: {e}")
                        continue
                
                all_data[search_term] = jobs
                logging.info(f"Total: {len(jobs)} jobs with emails for '{search_term}'")
            
            # Save jobs with emails to cache
            if all_data:
                self._save_to_cache(all_data)
            
            # Save jobs without emails to links.json
            if jobs_without_emails:
                self._save_links(jobs_without_emails)
                logging.info(f"Saved {len(jobs_without_emails)} jobs with apply links (no emails) to {self.links_path}")
            
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
                        
                        # Try multiple selectors for Seek's job cards
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
            # Find job link
            link = card.find('a', attrs={'data-testid': 'job-card-title-link'})
            if not link:
                link = card.find('a', href=re.compile(r'/job/'))
            if not link:
                return None
            
            job_url = link.get('href', '')
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.seek.com.au{job_url}"
            
            # Extract job ID from URL
            job_id_match = re.search(r'/job/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else 'unknown'
            
            # Extract title
            title = link.get_text(strip=True) if link else "Unknown"
            
            # Extract company
            company_elem = card.find('a', attrs={'data-testid': 'job-card-company-link'})
            if not company_elem:
                company_elem = card.find('span', class_=re.compile(r'.*company.*', re.I))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('span', attrs={'data-testid': 'job-card-location'})
            if not location_elem:
                location_elem = card.find('span', class_=re.compile(r'.*location.*', re.I))
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract salary
            salary_elem = card.find('span', attrs={'data-testid': 'job-card-salary'})
            if not salary_elem:
                salary_elem = card.find('span', class_=re.compile(r'.*salary.*', re.I))
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
            
            # Extract short description
            desc_elem = card.find('span', attrs={'data-testid': 'job-card-snippet'})
            if not desc_elem:
                desc_elem = card.find('p', class_=re.compile(r'.*snippet.*', re.I))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Look for email or apply link in description
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
            
            # Only return if has email (if requireEmail is True)
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
        # Phone number patterns (international and local formats)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        # Remove duplicates
        return list(set(phones))
    
    def _save_to_cache(self, data: Dict):
        """Save scraped data to cache file"""
        try:
            # Flatten all jobs into a single list for cache
            all_jobs = []
            for search_term, jobs in data.items():
                all_jobs.extend(jobs)
            
            # Remove duplicates by job ID
            seen_ids = set()
            unique_jobs = []
            for job in all_jobs:
                if job['id'] not in seen_ids:
                    seen_ids.add(job['id'])
                    unique_jobs.append(job)
            
            with open(self.cached_data_path, 'w', encoding='utf-8') as f:
                json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Saved {len(unique_jobs)} jobs to {self.cached_data_path}")
            
        except Exception as e:
            logging.error(f"Error saving to cache: {e}")
    
    def _save_links(self, jobs: List[Dict]):
        """Save jobs without emails but with apply links to links.json"""
        try:
            # Load existing links if file exists
            existing_links = []
            if Path(self.links_path).exists():
                try:
                    with open(self.links_path, 'r', encoding='utf-8') as f:
                        existing_links = json.load(f)
                except:
                    pass
            
            # Format job data for links file
            for job in jobs:
                link_entry = {
                    'id': job['id'],
                    'title': job.get('title', 'Unknown'),
                    'company': job.get('company', 'Unknown'),
                    'platform': job.get('platform', 'unknown'),
                    'applyLink': job.get('applyLink', job.get('jobLink', '')),
                    'jobLink': job.get('jobLink', ''),
                    'description': job.get('content', {}).get('jobHook', '')[:500],  # First 500 chars
                    'fullDescription': job.get('content', {}).get('sections', []),
                    'location': job.get('joblocationInfo', {}).get('displayLocation', 'Unknown'),
                    'salary': job.get('salary', 'N/A'),
                    'scrapedDate': datetime.now().isoformat()
                }
                
                # Check if not already in list
                if not any(link['id'] == link_entry['id'] for link in existing_links):
                    existing_links.append(link_entry)
            
            # Save to file
            with open(self.links_path, 'w', encoding='utf-8') as f:
                json.dump(existing_links, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Updated {self.links_path} with {len(existing_links)} total job links")
            
        except Exception as e:
            logging.error(f"Error saving links: {e}")
