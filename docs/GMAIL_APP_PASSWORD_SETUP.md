# Gmail App Password Setup Guide

##  Problem

Getting this error:
```
Failed to send email: (535, b'5.7.8 Username and Password not accepted')
```

This means Gmail is rejecting your credentials because you're using a regular password instead of an App Password.

---

##  Complete Setup Guide

### Step 1: Enable 2-Factor Authentication (Required)

1. Go to **Google Account Security**:
   ```
   https://myaccount.google.com/security
   ```

2. Find **"2-Step Verification"** section

3. Click **"Get Started"**

4. Follow the wizard:
   - Enter your phone number
   - Verify with the code sent to your phone
   - Turn on 2-Step Verification

---

### Step 2: Generate Gmail App Password

1. Go to **App Passwords**:
   ```
   https://myaccount.google.com/apppasswords
   ```

2. You may need to sign in again

3. Select dropdown menus:
   - **Select app**: Choose "Mail"
   - **Select device**: Choose "Other (Custom name)"
   - **Name it**: "Job Application Bot" (or any name you like)

4. Click **"Generate"**

5. You'll see a 16-character password like:
   ```
   abcd efgh ijkl mnop
   ```

6. **COPY THIS PASSWORD** (you won't see it again!)

---

### Step 3: Update .env File

1. Open your `.env` file:
   ```bash
   nano .env
   # or
   code .env
   ```

2. Update the `EMAIL_APP_PASSWORD` line:
   ```bash
   EMAIL_ADDRESS="mehdyakr@gmail.com"
   EMAIL_APP_PASSWORD="abcdefghijklmnop"  #  REMOVE ALL SPACES!
   ```

3. **IMPORTANT**: Remove all spaces from the App Password!
   -  Wrong: `"abcd efgh ijkl mnop"`
   -  Correct: `"abcdefghijklmnop"`

4. Save the file

---

### Step 4: Test Your Configuration

Run the test script:

```bash
uv run python3 test_email_config.py
```

**Expected output if working:**
```
 SUCCESS! Test email sent successfully!
Check your inbox at mehdyakr@gmail.com
Subject:  Job Application Bot - Test Email
```

**If you get an error:**
- Double-check the App Password has no spaces
- Verify 2FA is enabled
- Try generating a new App Password
- Check your email address is correct

---

##  Troubleshooting

### Error: "Username and Password not accepted"

**Cause**: Using regular Gmail password or App Password has spaces

**Fix**:
1. Generate a new App Password at https://myaccount.google.com/apppasswords
2. Copy it WITHOUT spaces to `.env`
3. Example: `EMAIL_APP_PASSWORD="abcdefghijklmnop"`

---

### Error: "App Passwords option not available"

**Cause**: 2-Factor Authentication is not enabled

**Fix**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification first
3. Then App Passwords option will appear

---

### Error: "Less secure app access"

**Cause**: Google deprecated "Less secure app access" in May 2022

**Fix**:
- You MUST use App Passwords now
- "Less secure app access" no longer works
- Follow the App Password setup above

---

### Email sent but not received

**Check**:
1. Spam/Junk folder
2. Gmail Sent folder (to verify it was sent)
3. Correct recipient email address
4. Email quota limits

---

##  Quick Reference

### Required Settings in .env:

```bash
EMAIL_ADDRESS="your@gmail.com"
EMAIL_APP_PASSWORD="16characterapppassword"  # No spaces!
```

### Test Commands:

```bash
# Test email configuration
uv run python3 test_email_config.py

# Run the application
uv run python3 main.py --first_name YourName

# Check application status
uv run python3 check_application_status.py
```

### Important Links:

- **Enable 2FA**: https://myaccount.google.com/security
- **App Passwords**: https://myaccount.google.com/apppasswords
- **Google Help**: https://support.google.com/mail/?p=BadCredentials

---

##  Success Checklist

Before running the application, verify:

- [ ] 2-Factor Authentication is enabled on Gmail
- [ ] App Password is generated (16 characters)
- [ ] `.env` file has correct `EMAIL_ADDRESS`
- [ ] `.env` file has correct `EMAIL_APP_PASSWORD` (no spaces!)
- [ ] Test script runs successfully: `uv run python3 test_email_config.py`
- [ ] Test email received in your inbox

---

##  After Setup

Once your email is configured correctly:

```bash
# Run the job application bot
uv run python3 main.py --first_name YourName

# Watch for successful sends in logs:
# "INFO - Successfully sent email to recruiter@company.com"

# Check your Gmail Sent folder for application emails
```

---

##  Pro Tips

1. **Keep App Password secure**: Treat it like a password, don't share it
2. **One App Password per app**: Generate separate ones for different apps
3. **Revoke if compromised**: Go to App Passwords page and delete it
4. **Test before bulk sending**: Run with one job first to verify
5. **Monitor sent folder**: Verify emails are actually being sent

---

##  Still Having Issues?

If you're still getting errors after following this guide:

1. **Try a fresh App Password**:
   - Delete old one at https://myaccount.google.com/apppasswords
   - Generate a new one
   - Update `.env`

2. **Verify .env format**:
   ```bash
   cat .env | grep EMAIL
   # Should show:
   # EMAIL_ADDRESS="your@gmail.com"
   # EMAIL_APP_PASSWORD="abcdefghijklmnop"
   ```

3. **Check for hidden characters**:
   ```bash
   # Remove and recreate the line in .env
   # Type it manually, don't copy-paste
   ```

4. **Test with a simple Python script**:
   ```bash
   uv run python3 test_email_config.py
   ```

---

## Alternative: Use Outlook

If Gmail is giving you trouble, you can use Outlook/Hotmail:

1. Go to https://account.microsoft.com/security
2. Generate App Password
3. Update `.env`:
   ```bash
   EMAIL_ADDRESS="your@outlook.com"
   EMAIL_APP_PASSWORD="your_outlook_app_password"
   ```
4. Run with:
   ```bash
   uv run python3 main.py --first_name YourName --mail_protocol outlook.com
   ```
