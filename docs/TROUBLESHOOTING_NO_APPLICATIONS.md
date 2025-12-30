# Troubleshooting: No Applications Sent

##  Problem

The application processes jobs but doesn't actually send emails or apply via Seek.

In `applied.json` you see:
```json
"applied_via_seek": false,
"applied_via_email": false,
"emails_contacted": []
```

---

##  Root Causes Identified

### 1.  Jobs Already Marked as Applied

**Issue:** Once a job is processed, it's added to `applied.json`. On subsequent runs, it's skipped with:
```
Already applied to job XXXXX, skipping.
```

**Solution:** Delete or reset `applied.json` to reprocess jobs:
```bash
# Backup first
cp application_pipeline/application_materials/applied.json applied.json.backup

# Reset to empty state
echo '{"jobs": {}, "email_history": {}}' > application_pipeline/application_materials/applied.json

# OR delete it completely
rm application_pipeline/application_materials/applied.json
```

### 2.  Gemini API Quota Exceeded

**Issue:** Free tier allows only 20 requests per day per model:
```
429 RESOURCE_EXHAUSTED: You exceeded your current quota
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20
```

**Solutions:**

**Option A: Wait for quota reset** (resets daily)
```bash
# Check your usage at:
https://ai.dev/usage?tab=rate-limit
```

**Option B: Use MetaAI as fallback** (No API quota limits)
```bash
# Remove GEMINI_KEY from .env temporarily
# The app will auto-fall back to MetaAI
```

**Option C: Upgrade Gemini plan**
- Go to [Google AI Studio](https://aistudio.google.com/)
- Upgrade to pay-as-you-go pricing

**Option D: Use a different free model**
```bash
# Try gemini-flash-lite (lower quota usage)
uv run python3 main.py --first_name YourName --model gemini-2.5-flash-lite
```

### 3.  Jobs Without Email Addresses

**Issue:** 66% of cached jobs don't have email addresses.

**Check your data:**
```bash
uv run python3 check_application_status.py
```

**Solution:** 
- Get fresh data from Apify when your plan is active (includes emails)
- Or manually add emails to `info.json` for specific jobs

### 4.  Seek Login Not Active

**Issue:** Seek applications require active login session.

**Solution:** 
- The app needs your Seek login credentials
- Check `integrations/seek_client.py` for login implementation
- Currently, most applications rely on email

---

##  How to Test if Applications Work

### Step 1: Reset applied.json
```bash
echo '{"jobs": {}, "email_history": {}}' > application_pipeline/application_materials/applied.json
```

### Step 2: Wait for Gemini quota OR use MetaAI
```bash
# Option A: Remove GEMINI_KEY from .env
# The app will use MetaAI (slower but no quota)

# Option B: Wait until quota resets (check at https://ai.dev/usage)
```

### Step 3: Run with a job that has email
```bash
# First, find a job with an email
uv run python3 -c "
import json
with open('info.json', 'r') as f:
    jobs = json.load(f)
for job in jobs:
    if job.get('emails'):
        print(f\"Job {job['id']}: {job['title']}\")
        print(f\"Email: {job['emails']}\")
        break
"

# Then run the application
uv run python3 main.py --first_name YourName
```

### Step 4: Check for success
```bash
# Check applied.json
cat application_pipeline/application_materials/applied.json | python3 -m json.tool

# Look for:
# "applied_via_email": true
# "emails_contacted": ["some@email.com"]

# Check your sent mail folder
```

---

##  Monitoring Applications

### Check Application Status Anytime
```bash
uv run python3 check_application_status.py
```

This shows:
-  How many jobs processed
-  How many applied via Seek
-  How many applied via Email
-  Which emails were contacted
-  Jobs with/without email addresses

### Watch Logs in Real-Time
```bash
# Run and watch for email-related logs
uv run python3 main.py --first_name YourName 2>&1 | grep -i email
```

Look for messages like:
-  `Sending application email to: xxx@company.com`
-  `successfully applied to job XXXXX via email`
-  `Error sending email:`

---

##  Quick Fix Checklist

- [ ] Delete or reset `applied.json`
- [ ] Check Gemini quota at https://ai.dev/usage
- [ ] Verify EMAIL_ADDRESS and EMAIL_APP_PASSWORD in `.env`
- [ ] Use Gmail App Password (not regular password)
- [ ] Ensure jobs in `info.json` have email addresses
- [ ] Check logs for actual errors when running
- [ ] Consider using MetaAI if Gemini quota exceeded

---

##  Complete Reset and Fresh Start

If you want to start completely fresh:

```bash
# 1. Backup your data
cp application_pipeline/application_materials/applied.json applied_backup.json

# 2. Reset applied jobs
echo '{"jobs": {}, "email_history": {}}' > application_pipeline/application_materials/applied.json

# 3. Remove Gemini key temporarily (use MetaAI)
# Comment out GEMINI_KEY in .env

# 4. Run with minimum score 0 (process all jobs)
uv run python3 main.py --first_name YourName --min_score 0

# 5. Monitor the output
```

---

##  Expected Behavior When Working

When applications are sent successfully, you'll see:

```
2025-12-30 XX:XX:XX - INFO - Processing job: 89000930
2025-12-30 XX:XX:XX - INFO - Sending application email to: recruiter@company.com
2025-12-30 XX:XX:XX - INFO - Successfully sent email to recruiter@company.com
2025-12-30 XX:XX:XX - INFO - successfully applied to job 89000930 via email
```

And in `applied.json`:
```json
{
  "89000930": {
    "applied_via_email": true,
    "emails_contacted": ["recruiter@company.com"]
  }
}
```

---

##  Still Not Working?

Run the diagnostic:
```bash
uv run python3 check_application_status.py
```

Then check:
1. Email credentials are correct
2. Gmail has "Less secure app access" OR using App Password
3. Jobs have email addresses
4. Gemini quota not exceeded
5. `applied.json` doesn't already have the job

---

##  Pro Tips

1. **Start small**: Reset `applied.json` and run with `--min_score 0.6` to only process best matches first
2. **Check sent folder**: Verify emails are actually being sent
3. **Use MetaAI for testing**: No API quotas to worry about
4. **Monitor logs**: Watch for error messages
5. **Fresh data**: Get new jobs from Apify when available (includes emails)
