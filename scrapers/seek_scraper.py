"""
Custom Seek Job Scraper
Scrapes job listings directly from Seek.com.au without Apify
"""

import asyncio
import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from curl_cffi import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class SeekScraper:
    """Direct Seek scraper without Apify dependency"""
    
    BASE_URL = "https://www.seek.com.au"
    
    def __init__(self, run_config):
        self.run_config = run_config
        self.session = requests.Session(impersonate="chrome110")
        
    async def scrape(self) -> Dict[str, List]:
        """
        Scrape jobs from Seek based on run_config
        Returns data in same format as Apify scraper
        """
        try:
            all_data = {}
            
            for search_term in self.run_config['searchTerms']:
                logging.info(f"Scraping jobs for: {search_term}")
                jobs = await self._scrape_search_term(search_term)
                all_data[search_term] = jobs
                logging.info(f"Found {len(jobs)} jobs for '{search_term}'")
                
                # Be nice to the server
                await asyncio.sleep(2)
            
            # Save to cache
            if all_data:
                self._save_to_cache(all_data)
            
            return all_data
            
        except Exception as e:
            logging.error(f"Custom scraping failed: {e}")
            raise
    
    async def _scrape_search_term(self, search_term: str) -> List[Dict]:
        """Scrape jobs for a single search term"""
        jobs = []
        page = 1
        max_results = self.run_config.get('maxResults', 100)
        
        while len(jobs) < max_results:
            try:
                url = self._build_search_url(search_term, page)
                logging.info(f"Fetching: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                page_jobs = self._parse_search_page(response.text)
                
                if not page_jobs:
                    logging.info(f"No more jobs found for '{search_term}' on page {page}")
                    break
                
                jobs.extend(page_jobs)
                logging.info(f"Scraped page {page}: {len(page_jobs)} jobs (total: {len(jobs)})")
                
                page += 1
                await asyncio.sleep(1.5)  # Rate limiting
                
                if len(jobs) >= max_results:
                    jobs = jobs[:max_results]
                    break
                    
            except Exception as e:
                logging.error(f"Error scraping page {page}: {e}")
                break
        
        detailed_jobs = []
        for i, job in enumerate(jobs[:max_results], 1):
            try:
                detailed_job = await self._get_job_details(job)
                detailed_jobs.append(detailed_job)
                
                if i % 10 == 0:
                    logging.info(f"Fetched details for {i}/{len(jobs)} jobs")
                    await asyncio.sleep(2)  # Longer pause every 10 jobs
                else:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logging.warning(f"Error getting details for job {job.get('id')}: {e}")
                detailed_jobs.append(job)  # Use basic info if details fail
        
        return detailed_jobs
    
    def _build_search_url(self, search_term: str, page: int = 1) -> str:
        """Build Seek search URL with parameters"""
        params = {
            'keywords': search_term,
            'page': page,
        }
        
        # Add location if specified
        if 'suburbOrCity' in self.run_config:
            params['where'] = self.run_config['suburbOrCity']
        
        # Add date range if specified
        if 'dateRange' in self.run_config:
            params['daterange'] = self.run_config['dateRange']
        
        # Add sort by
        sort_by = self.run_config.get('SortBy', 'KeywordsRelevance')
        if sort_by == 'ListedDate':
            params['sortmode'] = 'ListedDate'
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.BASE_URL}/jobs?{query_string}"
    
    def _parse_search_page(self, html: str) -> List[Dict]:
        """Parse job listings from search results page"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        job_cards = soup.find_all('article', {'data-search-sol-meta': True})
        
        if not job_cards:
            job_cards = soup.find_all('div', {'data-card-type': 'JobCard'})
        
        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                logging.warning(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Extract job info from a job card element"""
        try:
            # Find job link
            link_elem = card.find('a', {'data-job-id': True})
            if not link_elem:
                link_elem = card.find('a', href=re.compile(r'/job/\d+'))
            
            if not link_elem:
                return None
            
            job_url = link_elem.get('href', '')
            if not job_url.startswith('http'):
                job_url = self.BASE_URL + job_url
            
            # Extract job ID from URL
            job_id_match = re.search(r'/job/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else None
            
            if not job_id:
                return None
            
            # Extract title
            title_elem = card.find('a', {'data-job-id': job_id})
            if not title_elem:
                title_elem = link_elem
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('a', {'data-automation': 'jobCompany'})
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('a', {'data-automation': 'jobLocation'})
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Extract salary
            salary_elem = card.find('span', {'data-automation': 'jobSalary'})
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
            
            # Extract work type
            work_type_elem = card.find('span', {'data-automation': 'jobWorkType'})
            work_type = work_type_elem.get_text(strip=True) if work_type_elem else "Full time"
            
            return {
                'id': job_id,
                'title': title,
                'roleId': self._generate_role_id(title),
                'jobLink': job_url,
                'applyLink': f"{job_url}/apply",
                'company': company,
                'salary': salary,
                'workTypes': work_type,
                'joblocationInfo': {
                    'displayLocation': location,
                    'location': location,
                    'country': 'Australia',
                    'countryCode': 'AU',
                }
            }
            
        except Exception as e:
            logging.warning(f"Error parsing job card: {e}")
            return None
    
    async def _get_job_details(self, job: Dict) -> Dict:
        """Fetch detailed job information"""
        try:
            response = self.session.get(job['jobLink'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            description = self._extract_description(soup)
            
            emails = self._extract_emails(response.text)
            phones = self._extract_phone_numbers(response.text)
            
            work_arrangements = self._extract_work_arrangements(soup)
            
            bullet_points, job_hook = self._extract_highlights(soup, description)
            
            job.update({
                'emails': emails,
                'phoneNumbers': phones,
                'workArrangements': work_arrangements,
                'numApplicants': self._extract_applicant_count(soup),
                'content': {
                    'unEditedContent': description,
                    'sections': self._split_into_sections(description),
                    'bulletPoints': bullet_points,
                    'jobHook': job_hook,
                }
            })
            
            return job
            
        except Exception as e:
            logging.warning(f"Error fetching job details for {job['id']}: {e}")
            return job
    
    def _extract_description(self, soup) -> str:
        """Extract job description from page"""
        # Try different selectors for job description
        selectors = [
            {'data-automation': 'jobAdDetails'},
            {'data-automation': 'jobDescription'},
            {'class': re.compile(r'job.*description', re.I)},
        ]
        
        for selector in selectors:
            desc_elem = soup.find('div', selector)
            if desc_elem:
                return str(desc_elem)
        
        return ""
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Australian phone numbers from text"""
        # Australian phone number patterns
        patterns = [
            r'\b(?:\+?61|0)[2-478](?:[ -]?\d){8}\b',  # Standard format
            r'\b04\d{2}[ -]?\d{3}[ -]?\d{3}\b',  # Mobile
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))  # Remove duplicates
    
    def _extract_work_arrangements(self, soup) -> str:
        """Extract work arrangement (Remote, Hybrid, etc.)"""
        arrangement_elem = soup.find('span', string=re.compile(r'Remote|Hybrid|Work from home', re.I))
        if arrangement_elem:
            return arrangement_elem.get_text(strip=True)
        
        desc = soup.get_text()
        if re.search(r'\bremote\b', desc, re.I):
            return "Remote"
        elif re.search(r'\bhybrid\b', desc, re.I):
            return "Hybrid"
        
        return "Office"
    
    def _extract_applicant_count(self, soup) -> str:
        """Extract number of applicants"""
        applicant_elem = soup.find(string=re.compile(r'\d+\+?\s*applicants?', re.I))
        if applicant_elem:
            match = re.search(r'(\d+\+?)', applicant_elem)
            if match:
                return f"{match.group(1)}+"
        return "N/A"
    
    def _extract_highlights(self, soup, description: str) -> tuple:
        """Extract bullet points and job hook"""
        bullet_points = []
        job_hook = ""
        
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                if text and len(text) > 10:
                    bullet_points.append(text)
        
        bullet_points = bullet_points[:5]
        
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50 and len(text) < 300:
                job_hook = text
                break
        
        return bullet_points, job_hook
    
    def _split_into_sections(self, html_content: str) -> List[str]:
        """Split content into sections"""
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = []
        
        for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4']):
            text = elem.get_text(strip=True)
            if text:
                sections.append(text)
        
        return sections[:20]  # Limit to first 20 sections
    
    def _generate_role_id(self, title: str) -> str:
        """Generate a role ID from job title"""
        role_id = re.sub(r'[^a-z0-9]+', '-', title.lower())
        role_id = role_id.strip('-')
        return role_id
    
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
