import os
import json
import requests
import logging
from typing import List, Dict

class DiscordWebhook:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
    def send_jobs(self, jobs: List[Dict]) -> bool:
        """Send jobs without emails to Discord webhook"""
        if not self.webhook_url:
            logging.warning("DISCORD_WEBHOOK_URL not set in .env - skipping Discord notification")
            return False
        
        if not jobs:
            logging.info("No jobs to send to Discord")
            return True
        
        try:
            embeds = []
            
            for job in jobs[:10]:
                title = job.get('title', 'Unknown Position')
                company = job.get('company', 'Unknown Company')
                location = job.get('location', 'Unknown Location')
                link = job.get('jobLink', job.get('applyLink', 'No link'))
                description = job.get('description', '')[:500]
                
                embed = {
                    "title": f"{title} at {company}",
                    "description": description if description else "No description available",
                    "url": link,
                    "color": 3447003,
                    "fields": [
                        {
                            "name": "Location",
                            "value": location,
                            "inline": True
                        },
                        {
                            "name": "Company",
                            "value": company,
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "BagitoJobSeeker"
                    }
                }
                
                embeds.append(embed)
            
            message = {
                "content": f"Found {len(jobs)} job(s) without email contacts:",
                "embeds": embeds
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 204:
                logging.info(f"Successfully sent {len(jobs)} jobs to Discord")
                return True
            else:
                logging.error(f"Discord webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending to Discord webhook: {e}")
            return False
    
    def send_batch(self, all_jobs: Dict[str, List[Dict]]) -> bool:
        """Send all jobs grouped by search term"""
        if not self.webhook_url:
            return False
        
        total_jobs = sum(len(jobs) for jobs in all_jobs.values())
        if total_jobs == 0:
            return True
        
        try:
            for search_term, jobs in all_jobs.items():
                if not jobs:
                    continue
                
                embeds = []
                for idx, job in enumerate(jobs[:10], 1):
                    title = job.get('title', 'Unknown Position')
                    company = job.get('company', 'Unknown Company')
                    link = job.get('jobLink', job.get('applyLink', 'No link'))
                    
                    location_info = job.get('joblocationInfo', {})
                    if isinstance(location_info, dict):
                        location = location_info.get('displayLocation', 'Unknown Location')
                    else:
                        location = job.get('location', 'Unknown Location')
                    
                    description = job.get('content', job.get('description', ''))
                    if isinstance(description, dict):
                        description = description.get('jobHook', '')
                    if description:
                        description = description[:200] + "..." if len(description) > 200 else description
                    else:
                        description = "No description available"
                    
                    embed = {
                        "title": f"{idx}. {title}",
                        "description": description,
                        "url": link,
                        "color": 5814783,
                        "fields": [
                            {
                                "name": "🏢 Company",
                                "value": company,
                                "inline": True
                            },
                            {
                                "name": "📍 Location",
                                "value": location,
                                "inline": True
                            },
                            {
                                "name": "🔗 Apply",
                                "value": f"[Click here]({link})",
                                "inline": False
                            }
                        ]
                    }
                    embeds.append(embed)
                
                payload = {
                    "content": f"**🔍 {search_term}** - Found {len(jobs)} job(s) without email contacts:",
                    "embeds": embeds
                }
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 204:
                    logging.error(f"Discord webhook failed for {search_term}: {response.status_code}")
            
            logging.info(f"Sent {total_jobs} total jobs to Discord")
            return True
            
        except Exception as e:
            logging.error(f"Error sending batch to Discord: {e}")
            return False
