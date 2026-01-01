#!/usr/bin/env python3
"""
Test script to verify Gmail App Password configuration
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("GMAIL APP PASSWORD TEST")
print("="*70)

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_APP_PASSWORD")

print(f"\n EMAIL_ADDRESS: {email_address}")
print(f" EMAIL_APP_PASSWORD: {'*' * len(email_password) if email_password else 'NOT SET'}")

if not email_address or not email_password:
    print("\n ERROR: Email credentials not configured in .env")
    print("\nPlease add:")
    print("  EMAIL_ADDRESS=your@gmail.com")
    print("  EMAIL_APP_PASSWORD=your_app_password")
    exit(1)

print("\n" + "-"*70)
print("TESTING GMAIL CONNECTION...")
print("-"*70)

try:
    print("\n1. Connecting to smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    
    print("2. Starting TLS encryption...")
    server.starttls()
    
    print("3. Logging in with credentials...")
    server.login(email_address, email_password)
    
    print("4. Login successful!")
    
    print(f"\n5. Sending test email to {email_address}...")
    
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = " Job Application Bot - Test Email"
    
    body = """
This is a test email from your Job Application Bot.

If you're seeing this, your Gmail App Password is configured correctly!

 Email sending is working
 You're ready to send job applications

Next steps:
1. Run: uv run python3 main.py --first_name YourName
2. Check your sent folder for application emails
3. Monitor the logs for successful sends
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    server.send_message(msg)
    server.quit()
    
    print("\n" + "="*70)
    print(" SUCCESS! Test email sent successfully!")
    print("="*70)
    print(f"\nCheck your inbox at {email_address}")
    print("Subject:  Job Application Bot - Test Email")
    print("\nYour Gmail App Password is working correctly!")
    print("\nYou can now run the job application bot:")
    print("  uv run python3 main.py --first_name YourName")
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "="*70)
    print(" AUTHENTICATION FAILED")
    print("="*70)
    print(f"\nError: {e}")
    print("\n FIX:")
    print("\n1. Enable 2-Factor Authentication:")
    print("   https://myaccount.google.com/security")
    print("\n2. Generate App Password:")
    print("   https://myaccount.google.com/apppasswords")
    print("   - Select 'Mail' as app")
    print("   - Select 'Other' as device")
    print("   - Copy the 16-character password")
    print("\n3. Update .env file:")
    print(f"   EMAIL_APP_PASSWORD=your_16_char_password")
    print("\n  IMPORTANT: Remove all spaces from the App Password!")
    
except Exception as e:
    print("\n" + "="*70)
    print(" ERROR")
    print("="*70)
    print(f"\nError: {e}")
    print("\n Troubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify EMAIL_ADDRESS is correct")
    print("3. Ensure EMAIL_APP_PASSWORD has no spaces")
    print("4. Try generating a new App Password")

print("\n" + "="*70)
