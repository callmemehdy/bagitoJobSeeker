
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
        self.client = ApifyClientAsync(os.getenv("APIFY_KEY"))
        self.cached_data_path = cached_data_path
        
    async def scrape(self, actor):
        try:
            all_data = {}
            tasks = []
            searchTerms = []
            for query in self.run_config['searchTerms']:
                config = {k: v for k, v in self.run_config.items() if k != 'searchTerms'}
                config['searchTerm'] = query
                searchTerms.append(query)
                tasks.append(self.client.actor(actor).call(run_input=config))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for searchTerm, response in zip(searchTerms, responses):
                if isinstance(response, Exception):
                    logging.warning(f"API call failed for '{searchTerm}': {response}")
                    continue
                all_data[searchTerm] = await self._get_dataset(response)

            # If API failed completely, use cached data
            if not all_data:
                logging.warning("All API calls failed. Falling back to cached data...")
                return self._load_cached_data()

            return all_data
        except Exception as e:
            logging.error(f"Scraping failed: {e}")
            logging.info("Attempting to use cached data from info.json...")
            return self._load_cached_data()

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