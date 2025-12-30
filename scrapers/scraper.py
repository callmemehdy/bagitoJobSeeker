
from apify_client import ApifyClientAsync
from dotenv import load_dotenv
from pathlib import Path
import logging
import asyncio
import json
import os
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class JobScraper:
    def __init__(self, run_config, cached_data_path='./info.json'):
        self.run_config = run_config
        self.cached_data_path = cached_data_path
        apify_key = os.getenv("APIFY_KEY")
        self.client = ApifyClientAsync(apify_key) if apify_key else None
        self.has_apify = apify_key is not None
        
    async def scrape(self, actor):
        try:
            # Check if Apify is available
            if not self.has_apify:
                logging.warning("No APIFY_KEY found. Checking cached data...")
                cached_data = self._load_cached_data()
                if self._is_cache_empty(cached_data):
                    logging.info("Cache is empty. Using custom Seek scraper...")
                    return await self._use_custom_scraper()
                return cached_data
            
            # Try Apify scraping
            all_data = {}
            tasks = []
            searchTerms = []
            for query in self.run_config['searchTerms']:
                config = {k: v for k, v in self.run_config.items() if k != 'searchTerms'}
                config['searchTerm'] = query
                
                # Map country to Apify's allowed values
                country = config.get('country', 'Australia')
                config['country'] = self._map_country_to_apify(country)
                
                searchTerms.append(query)
                tasks.append(self.client.actor(actor).call(run_input=config))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for searchTerm, response in zip(searchTerms, responses):
                if isinstance(response, Exception):
                    logging.warning(f"API call failed for '{searchTerm}': {response}")
                    continue
                all_data[searchTerm] = await self._get_dataset(response)

            # If API failed completely, check cache or use custom scraper
            if not all_data:
                logging.warning("All Apify API calls failed. Checking cached data...")
                cached_data = self._load_cached_data()
                if self._is_cache_empty(cached_data):
                    logging.info("Cache is empty. Using custom Seek scraper...")
                    return await self._use_custom_scraper()
                return cached_data

            return all_data
        except Exception as e:
            logging.error(f"Apify scraping failed: {e}")
            logging.info("Attempting to use cached data from info.json...")
            cached_data = self._load_cached_data()
            if self._is_cache_empty(cached_data):
                logging.info("Cache is empty. Using custom Seek scraper...")
                return await self._use_custom_scraper()
            return cached_data

    def _load_cached_data(self):
        """Load job data from cached JSON file"""
        try:
            if not Path(self.cached_data_path).exists():
                logging.error(f"Cached data file not found at {self.cached_data_path}")
                return {}
            
            with open(self.cached_data_path, 'r', encoding='utf-8') as f:
                cached_jobs = json.load(f)
            
            # Group jobs by search terms if they match
            grouped_data = {}
            for search_term in self.run_config['searchTerms']:
                # Filter jobs that might match this search term
                matching_jobs = [
                    job for job in cached_jobs 
                    if self._job_matches_search(job, search_term)
                ]
                if matching_jobs:
                    grouped_data[search_term] = matching_jobs
                    logging.info(f"Loaded {len(matching_jobs)} cached jobs for search term: {search_term}")
                else:
                    # If no specific matches, just use all cached data for this term
                    grouped_data[search_term] = cached_jobs
                    logging.info(f"Using all {len(cached_jobs)} cached jobs for search term: {search_term}")
            
            return grouped_data if grouped_data else {self.run_config['searchTerms'][0]: cached_jobs}
            
        except Exception as e:
            logging.error(f"Error loading cached data: {e}")
            return {}
    
    def _map_country_to_apify(self, country):
        """Map config country to Apify's allowed values"""
        country_map = {
            'australia': 'australia',
            'hong kong': 'hongkong',
            'hongkong': 'hongkong',
            'indonesia': 'indonesia',
            'malaysia': 'malaysia',
            'new zealand': 'new zealand',
            'newzealand': 'new zealand',
            'philippines': 'philippines',
            'singapore': 'singapore',
            'thailand': 'thailand'
        }
        return country_map.get(country.lower(), 'australia')
    
    def _job_matches_search(self, job, search_term):
        """Check if job matches the search term"""
        search_lower = search_term.lower()
        title = job.get('title', '').lower()
        role_id = job.get('roleId', '').lower()
        
        # Simple keyword matching
        return (search_lower in title or 
                search_lower in role_id or
                any(word in title for word in search_lower.split()))

    async def _get_dataset(self, run):
        data = await self.client.dataset(run["defaultDatasetId"]).list_items()
        return data.items
    
    def _is_cache_empty(self, cached_data):
        """Check if cached data is empty or insufficient"""
        if not cached_data:
            return True
        
        # Check if all search terms have empty results
        total_jobs = 0
        for jobs in cached_data.values():
            total_jobs += len(jobs) if jobs else 0
        
        return total_jobs == 0
    
    async def _use_custom_scraper(self):
        """Use the custom scraper as fallback"""
        try:
            # Try multi-platform scraper first
            try:
                from scrapers.multi_platform_scraper import MultiPlatformScraper
                logging.info("Initializing multi-platform scraper...")
                
                custom_scraper = MultiPlatformScraper(self.run_config, self.cached_data_path)
                result = await custom_scraper.scrape()
                
                logging.info("Multi-platform scraper completed successfully!")
                return result
            except Exception as e:
                logging.warning(f"Multi-platform scraper failed: {e}, trying Seek-only scraper...")
                
                # Fallback to Seek-only scraper
                from scrapers.seek_scraper import SeekScraper
                logging.info("Initializing Seek scraper...")
                
                custom_scraper = SeekScraper(self.run_config, self.cached_data_path)
                result = await custom_scraper.scrape()
                
                logging.info("Seek scraper completed successfully!")
                return result
            
        except ImportError as e:
            logging.error(f"Failed to import custom scraper: {e}")
            logging.error("Please install required packages: pip install beautifulsoup4 lxml")
            return {}
        except Exception as e:
            logging.error(f"Custom scraper failed: {e}")
            return {}