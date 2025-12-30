#!/usr/bin/env python3
"""
Diagnostic script to check why applications weren't sent
"""

import json
from pathlib import Path

print("="*70)
print("APPLICATION STATUS DIAGNOSTIC")
print("="*70)

# Check applied.json
applied_path = "application_pipeline/application_materials/applied.json"
if Path(applied_path).exists():
    with open(applied_path, 'r') as f:
        applied = json.load(f)
    
    print(f"\n Jobs Processed: {len(applied['jobs'])}")
    print(f" Emails Contacted: {len(applied.get('email_history', {}))}")
    
    if applied['jobs']:
        print("\n" + "-"*70)
        print("JOB APPLICATION DETAILS:")
        print("-"*70)
        
        for job_id, job_info in applied['jobs'].items():
            print(f"\n Job ID: {job_id}")
            print(f"   Position: {job_info['position']}")
            print(f"   Similarity Score: {job_info['similarity_score']:.2f}")
            print(f"   Applied via Seek: {'' if job_info['applied_via_seek'] else ''}")
            print(f"   Applied via Email: {'' if job_info['applied_via_email'] else ''}")
            print(f"   Emails Contacted: {job_info['emails_contacted'] if job_info['emails_contacted'] else 'None'}")
            print(f"   Link: {job_info['link']}")
else:
    print(" No applied.json found")

# Check cached jobs for emails
print("\n" + "="*70)
print("CHECKING CACHED JOBS FOR EMAIL AVAILABILITY")
print("="*70)

info_path = "info.json"
if Path(info_path).exists():
    with open(info_path, 'r') as f:
        jobs = json.load(f)
    
    total_jobs = len(jobs)
    jobs_with_emails = sum(1 for job in jobs if job.get('emails'))
    jobs_without_emails = total_jobs - jobs_with_emails
    
    print(f"\n Total Cached Jobs: {total_jobs}")
    print(f" Jobs with Emails: {jobs_with_emails} ({jobs_with_emails/total_jobs*100:.1f}%)")
    print(f" Jobs without Emails: {jobs_without_emails} ({jobs_without_emails/total_jobs*100:.1f}%)")
    
    # Show some examples
    print("\n" + "-"*70)
    print("SAMPLE JOBS WITH EMAILS:")
    print("-"*70)
    count = 0
    for job in jobs:
        if job.get('emails') and count < 3:
            print(f"\n Job ID: {job['id']}")
            print(f"   Title: {job.get('title', 'N/A')}")
            print(f"   Emails: {job['emails']}")
            count += 1
else:
    print(" No info.json found")

# Check environment variables
print("\n" + "="*70)
print("ENVIRONMENT CONFIGURATION CHECK")
print("="*70)

import os
from dotenv import load_dotenv
load_dotenv()

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_APP_PASSWORD")
gemini_key = os.getenv("GEMINI_KEY")
apify_key = os.getenv("APIFY_KEY")

print(f"\n EMAIL_ADDRESS: {'Set ' if email_address else ' Not Set'}")
print(f" EMAIL_APP_PASSWORD: {'Set ' if email_password else ' Not Set'}")
print(f" GEMINI_KEY: {'Set ' if gemini_key else ' Not Set'}")
print(f" APIFY_KEY: {'Set ' if apify_key else ' Not Set'}")

print("\n" + "="*70)
print("DIAGNOSIS SUMMARY")
print("="*70)

if Path(applied_path).exists():
    with open(applied_path, 'r') as f:
        applied = json.load(f)
    
    jobs_processed = len(applied['jobs'])
    jobs_applied_seek = sum(1 for j in applied['jobs'].values() if j['applied_via_seek'])
    jobs_applied_email = sum(1 for j in applied['jobs'].values() if j['applied_via_email'])
    
    print(f"\n Summary:")
    print(f"   • Jobs processed: {jobs_processed}")
    print(f"   • Applied via Seek: {jobs_applied_seek}")
    print(f"   • Applied via Email: {jobs_applied_email}")
    print(f"   • Not applied: {jobs_processed - jobs_applied_seek - jobs_applied_email}")

print("\n" + "="*70)
print("POSSIBLE REASONS FOR NO APPLICATIONS:")
print("="*70)

reasons = []
if jobs_without_emails == total_jobs:
    reasons.append(" No cached jobs have email addresses")
elif jobs_with_emails < 10:
    reasons.append(f"  Only {jobs_with_emails} jobs have emails in cache")

if not email_address or not email_password:
    reasons.append(" Email credentials not configured in .env")

# Check if Seek is logged in
reasons.append("  Seek login may not be active (requires manual login)")
reasons.append("  Jobs may have 'hasRoleRequirements' or 'isExternalApply' set to True")

for i, reason in enumerate(reasons, 1):
    print(f"{i}. {reason}")

print("\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)
print("""
1.  Make sure jobs in info.json have email addresses
2.  Verify EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env
3.  Enable Gmail "App Passwords" (not regular password)
4.  Check logs when running for actual error messages
5.  For Seek applications: Login credentials needed
""")

print("="*70)
