
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
    def __init__(self, run_config):
        self.run_config = run_config
        apify_key = os.getenv("APIFY_KEY")
        self.client = ApifyClientAsync(apify_key) if apify_key else None
        self.has_apify = apify_key is not None
        
    async def scrape(self, actor):
        try:
            if not self.has_apify:
                logging.warning("No APIFY_KEY found. Using custom scraper...")
                return await self._use_custom_scraper()
            
            all_data = {}
            tasks = []
            searchTerms = []
            for query in self.run_config['searchTerms']:
                config = {k: v for k, v in self.run_config.items() if k != 'searchTerms'}
                config['searchTerm'] = query
                
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

            if not all_data:
                logging.warning("All Apify API calls failed. Using custom scraper...")
                return await self._use_custom_scraper()

            return all_data
        except Exception as e:
            logging.error(f"Apify scraping failed: {e}")
            logging.info("Falling back to custom scraper...")
            return await self._use_custom_scraper()
    
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

    async def _get_dataset(self, run):
        data = await self.client.dataset(run["defaultDatasetId"]).list_items()
        return data.items
    
    async def _use_custom_scraper(self):
        """Use the custom scraper as fallback"""
        try:
            try:
                from scrapers.multi_platform_scraper import MultiPlatformScraper
                logging.info("Initializing multi-platform scraper...")
                
                custom_scraper = MultiPlatformScraper(self.run_config)
                result = await custom_scraper.scrape()
                
                logging.info("Multi-platform scraper completed successfully!")
                return result
            except Exception as e:
                logging.warning(f"Multi-platform scraper failed: {e}, trying Seek-only scraper...")
                
                from scrapers.seek_scraper import SeekScraper
                logging.info("Initializing Seek scraper...")
                
                custom_scraper = SeekScraper(self.run_config)
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