from application_pipeline.job_application_pipeline import ApplicationPipeline
from common.utils import load_json_file, extract_text_from_pdf, write_json_file
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from integrations.mail_handler import MailClient
from integrations.agent import AIAgent
from common.utils import generate_cover_letter_pdf
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import argparse
import logging
import time
import sys
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class OffersApplicator:
    def __init__(self, args):
        self.args = args
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        resume_txt = extract_text_from_pdf(args.resume_pdf_path)
        self.args.resume_txt = resume_txt
        self.encoded_resume_txt = self.model.encode(resume_txt, convert_to_numpy=True)
        
        self.agent = AIAgent(args.first_name, args.model).agent
        self.mail_client = MailClient(args.mail_protocol)
        self.applied = self._load_applied(args.applied_path)
        
        self.spell_variant = args.spell_variant or 'american'

    def _load_applied(self, path):
        applied = load_json_file(path)
        if not applied:
            return {'jobs': {}, 'email_history': {}}
        return applied

    def calculate_resume_jd_similarity(self, jd_text):
        jd_vector = self.model.encode(jd_text, convert_to_numpy=True)
        sim_score = 1 - cosine(self.encoded_resume_txt, jd_vector)
        return float(sim_score)

    def should_skip_email(self, email):
        if email in self.applied['email_history']:
            last_contacted = datetime.fromisoformat(self.applied['email_history'][email]['last_contacted'])
            days_since_contact = (datetime.now() - last_contacted).days
            if days_since_contact < 7:
                logging.info(f"Recently contacted {email} {days_since_contact} days ago, skipping.")    
                return True
        return False

    def format_job_for_agent(self, offer):
        """Convert offer format to the format expected by the agent"""
        job_description = f"{offer.get('little_description', '')} {offer.get('big_description', '')}"
        
        # Extract company name from email domain or job title
        company_name = ''
        email = offer.get('email', '')
        if email:
            # Extract from email domain (e.g., name@company.com -> company)
            domain = email.split('@')[-1].split('.')[0]
            company_name = domain.capitalize()
        
        # Try to extract from title if it contains company indicators
        title = offer.get('title', '')
        if 'by ' in title.lower():
            parts = title.lower().split('by ')
            if len(parts) > 1:
                # Get company name after "by" and clean it
                company_part = parts[-1].strip()
                # Remove parentheses and get first word
                company_part = company_part.replace(')', '').replace('(', '')
                company_name = company_part.split()[0].strip().capitalize()
        elif ' - ' in title:
            # Check if company name is at the start (e.g., "Scholé AI - Position")
            parts = title.split(' - ')
            if len(parts) > 1 and len(parts[0].split()) <= 3:
                # Likely a company name (short, at start)
                company_name = parts[0].strip().replace(',', '')
        
        # Fallback: try to find capitalized words in description
        if not company_name or len(company_name) < 3:
            for desc in [offer.get('big_description', ''), offer.get('little_description', '')]:
                if desc:
                    words = desc.split()[:15]  # Check first 15 words
                    for word in words:
                        # Look for words that are all caps or start with capital (excluding common words)
                        clean_word = word.strip('.,!?()[]{}";:')
                        if (clean_word.isupper() and len(clean_word) > 2) or \
                           (clean_word and clean_word[0].isupper() and len(clean_word) > 4 and 
                            clean_word not in ['Rejoins', 'Participe', 'Développeur', 'Engineer']):
                            company_name = clean_word
                            break
                    if company_name:
                        break
        
        return {
            'id': offer.get('id'),
            'title': offer.get('title'),
            'content': job_description,
            'jobLink': offer.get('slug', ''),
            'companyProfile': {'name': company_name} if company_name else {},
            'location': offer.get('full_address', ''),
            'salary': offer.get('salary', ''),
            'contractType': offer.get('contract_type', ''),
            'emails': [offer.get('email')] if offer.get('email') else []
        }

    def apply_to_offers(self, offers_file, batch_size=None, start_index=0, offset_file=None):
        """Apply to jobs from offers JSON file with similarity checking"""
        offers_data = load_json_file(offers_file)
        
        if not offers_data:
            logging.error(f"Failed to load offers from {offers_file}")
            return
        
        total_offers = len(offers_data)
        logging.info(f"Loaded {total_offers} job offers from {offers_file}")
        
        end_index = start_index + batch_size if batch_size else total_offers
        end_index = min(end_index, total_offers)
        
        offers_to_process = offers_data[start_index:end_index]
        logging.info(f"Processing offers {start_index} to {end_index-1} (batch of {len(offers_to_process)})")
        
        applied_count = 0
        skipped_count = 0
        current_offset = start_index
        
        for idx, offer in enumerate(offers_to_process):
            try:
                current_offset = start_index + idx
                offer_id = str(offer.get('id'))
                logging.info(f"Processing offer {offer_id}: {offer.get('title', 'No title')}")
                
                if offer_id in self.applied['jobs']:
                    logging.info(f"Already applied to job {offer_id}, skipping.")
                    skipped_count += 1
                    continue
                
                job_description = f"{offer.get('little_description', '')} {offer.get('big_description', '')}"
                
                if not job_description.strip():
                    logging.warning(f"No job description found for offer {offer_id}, skipping.")
                    skipped_count += 1
                    continue
                
                score = self.calculate_resume_jd_similarity(job_description)
                logging.info(f"Similarity score: {score:.3f}")
                
                if score < self.args.min_score:
                    logging.info(f"Low similarity score {score:.3f} for job {offer_id}, skipping.")
                    skipped_count += 1
                    continue
                
                contact_email = offer.get('email')
                if not contact_email:
                    logging.warning(f"No contact email found for offer {offer_id}, skipping.")
                    skipped_count += 1
                    continue
                
                if self.should_skip_email(contact_email):
                    skipped_count += 1
                    continue
                
                formatted_job = self.format_job_for_agent(offer)
                
                # Retry logic for AI generation
                max_retries = 3
                retry_delay = 10
                
                for attempt in range(max_retries):
                    try:
                        if not self.args.use_gemini:
                            self.agent = AIAgent(self.args.first_name).agent
                        
                        cover_letter = self.agent.prepare_cover_letter(
                            formatted_job, 
                            self.args.resume_txt, 
                            self.spell_variant
                        )
                        generate_cover_letter_pdf(cover_letter, self.args.cover_letter_path)
                        
                        msg = self.agent.write_email_contents()
                        break
                        
                    except Exception as ai_error:
                        if attempt < max_retries - 1:
                            logging.warning(f"AI generation failed (attempt {attempt + 1}/{max_retries}): {ai_error}")
                            logging.info(f"Waiting {retry_delay} seconds before retry...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logging.error(f"AI generation failed after {max_retries} attempts")
                            raise
                
                success = self.mail_client.send_application(
                    contact_email,
                    formatted_job,
                    msg,
                    self.args.resume_pdf_path,
                    self.args.cover_letter_path
                )
                
                if success:
                    applied_count += 1
                    logging.info(f"Successfully applied to job {offer_id}")
                    
                    if contact_email in self.applied['email_history']:
                        self.applied['email_history'][contact_email]['last_contacted'] = datetime.now().isoformat()
                        self.applied['email_history'][contact_email]['jobs_contacted'].append(offer_id)
                    else:
                        self.applied['email_history'][contact_email] = {
                            'last_contacted': datetime.now().isoformat(),
                            'jobs_contacted': [offer_id]
                        }
                    
                    self.applied['jobs'][offer_id] = {
                        'applied_on': datetime.now().isoformat(),
                        'similarity_score': score,
                        'applied_via_seek': False,
                        'applied_via_email': True,
                        'emails_contacted': [contact_email],
                        'position': offer.get('title', ''),
                        'link': offer.get('slug', ''),
                        'source': 'offers_file'
                    }
                    
                    write_json_file(self.args.applied_path, self.applied)
                    
                    # Add delay between applications to avoid rate limits
                    if not self.args.use_gemini:
                        logging.info('Waiting 30 seconds before next application...')
                        time.sleep(30)
                
            except Exception as e:
                logging.error(f"Error processing offer {offer_id}: {e}")
                if offset_file:
                    with open(offset_file, 'w') as f:
                        f.write(str(current_offset + 1))
                    logging.info(f"Saved offset {current_offset + 1} to {offset_file}")
                raise
        
        logging.info(f"Batch complete: Applied to {applied_count} jobs, skipped {skipped_count} jobs")


def main():
    parser = argparse.ArgumentParser(description='Apply to jobs from offers JSON file with batch processing')
    
    parser.add_argument('--offers_file', 
                        type=str, 
                        help='Path to offers JSON file',
                        required=True)
    
    parser.add_argument('--first_name', 
                        type=str, 
                        help='Name of the user',
                        required=True)
    
    parser.add_argument('--batch_size', 
                        type=int,
                        help='Number of jobs to process in this batch (default: all)',
                        default=None)
    
    parser.add_argument('--start_index', 
                        type=int,
                        help='Starting index in the offers file (default: 0)',
                        default=0)
    
    parser.add_argument('--min_score', 
                        type=float,
                        help='Minimum similarity score to apply (0.0-1.0, default: 0.5)',
                        default=0.5)
    
    parser.add_argument('--resume_pdf_path', 
                        type=str,
                        help='Path to resume',
                        default="application_pipeline/application_materials/resume.pdf")
    
    parser.add_argument('--cover_letter_path', 
                        type=str,
                        help='Path to cover letter',
                        default="application_pipeline/application_materials/cover_letter.pdf")
    
    parser.add_argument('--applied_path', 
                        type=str,
                        help='Path to applied jobs',
                        default="application_pipeline/application_materials/applied.json")
    
    parser.add_argument('--mail_protocol', 
                        type=str,
                        help='Mail protocol e.g gmail.com, outlook.com',
                        default="gmail.com")
    
    parser.add_argument('--spell_variant', 
                        type=str,
                        help='Spelling variant: british, american, australian, canadian, etc.',
                        default='american')
    
    parser.add_argument('--model', 
                        type=str,
                        help='Gemini model',
                        default="gemini-2.5-flash")
    
    parser.add_argument('--offset_file', 
                        type=str,
                        help='File to save offset on error',
                        default=None)
    
    args = parser.parse_args()
    
    try:
        assert Path(args.resume_pdf_path).exists(), f"resume.pdf not found in {args.resume_pdf_path}"
        assert Path(args.offers_file).exists(), f"offers file not found in {args.offers_file}"
    except AssertionError as e:
        logging.error(f"AssertionError: {e}")
        sys.exit(1)
    
    if os.getenv("GEMINI_KEY"):
        args.use_gemini = True
    else:
        args.use_gemini = False
        logging.warning("No gemini api found defaulting to meta api")
    
    applicator = OffersApplicator(args)
    applicator.apply_to_offers(args.offers_file, args.batch_size, args.start_index, args.offset_file)


if __name__ == "__main__":
    main()
