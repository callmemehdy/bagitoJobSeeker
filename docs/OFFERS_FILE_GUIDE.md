# Applying to Jobs from Offers JSON File

This guide explains how to use the `apply_from_offers.py` script to automatically apply to jobs from a saved offers JSON file.

## Overview

The script processes job offers from a JSON file, calculates similarity scores between your resume and job descriptions, and automatically sends applications via email with personalized cover letters.

## Offers File Format

Your offers JSON file should be a list of job objects with the following structure:

```json
[
    {
        "id": 25913,
        "title": "CDI – Développeur Full Stack IA / Data",
        "little_description": "Short description...",
        "big_description": "Full detailed description...",
        "email": "recruiter@company.com",
        "salary": "45000",
        "contract_type": "cdi",
        "full_address": "92 rue jouffroy d'abbans, PARIS, 75017, France",
        "slug": "job-slug-url",
        "company_id": 12086
    }
]
```

### Required Fields
- `id`: Unique job identifier
- `title`: Job title
- `little_description`: Short job description
- `big_description`: Detailed job description
- `email`: Contact email for applications

### Optional Fields
- `salary`: Salary information
- `contract_type`: Type of contract (cdi, stage, etc.)
- `full_address`: Job location
- `slug`: URL slug for the job posting

## Quick Start

### Basic Usage

Apply to all jobs in the default offers file:

```bash
make apply-offers FIRST_NAME=YourName
```

### With Custom Parameters

```bash
# Use higher similarity threshold
make apply-offers FIRST_NAME=Mehdi MIN_SCORE=0.6

# Use custom offers file
make apply-offers FIRST_NAME=Mehdi OFFERS_FILE=my_custom_offers.json

# Combine parameters
make apply-offers FIRST_NAME=Mehdi OFFERS_FILE=offers_2025-11-10-10-57-35.json MIN_SCORE=0.4
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `FIRST_NAME` | **Required** | Your first name for personalizing emails |
| `OFFERS_FILE` | `offers_2025-11-10-10-57-35.json` | Path to your offers JSON file |
| `MIN_SCORE` | `0.3` | Minimum similarity score (0.0-1.0) to apply |

## How It Works

### 1. Similarity Calculation
- Uses sentence transformers to encode your resume and job descriptions
- Calculates cosine similarity scores (0.0 to 1.0)
- Higher score = better match between resume and job

### 2. Smart Filtering
The script automatically skips jobs that:
- You've already applied to (tracked in `applied.json`)
- Have emails you contacted in the last 7 days
- Have similarity score below `MIN_SCORE`
- Don't have contact email or job description

### 3. Application Process
For qualifying jobs:
1. Generates personalized cover letter using AI
2. Creates professional email introduction
3. Sends application with resume and cover letter attached
4. Records application in `applied.json` for tracking

### 4. Error Handling with Offset Tracking
- If an error occurs, the current position is saved to `offset.txt`
- Simply run the same command again to auto-resume from where it stopped
- When all jobs are processed successfully, `offset.txt` is automatically deleted

## Examples

### Process all 231 offers with default settings
```bash
make apply-offers FIRST_NAME=Mehdi
```

**Expected output:**
```
✓ Applying to all jobs from offers file...
   First Name: Mehdi
   Offers File: offers_2025-11-10-10-57-35.json
   Min Score: 0.3
   Start Index: 0

2026-01-05 15:30:00 - INFO - Loaded 231 job offers
2026-01-05 15:30:05 - INFO - Processing offer 25913: CDI – Développeur Full Stack IA / Data
2026-01-05 15:30:06 - INFO - Similarity score: 0.752
2026-01-05 15:30:10 - INFO - Successfully applied to job 25913
...
```

### Resume from error
If the script stops due to an error:
```bash
make apply-offers FIRST_NAME=Mehdi
# Will automatically resume from offset.txt
```

### Higher quality threshold
Only apply to jobs with 60%+ similarity:
```bash
make apply-offers FIRST_NAME=Mehdi MIN_SCORE=0.6
```

## Tracking Applications

All applications are tracked in:
```
application_pipeline/application_materials/applied.json
```

Structure:
```json
{
  "jobs": {
    "25913": {
      "applied_on": "2026-01-05T15:30:00",
      "similarity_score": 0.752,
      "applied_via_email": true,
      "emails_contacted": ["recruiter@company.com"],
      "position": "CDI – Développeur Full Stack IA / Data",
      "link": "job-slug-url",
      "source": "offers_file"
    }
  },
  "email_history": {
    "recruiter@company.com": {
      "last_contacted": "2026-01-05T15:30:00",
      "jobs_contacted": ["25913"]
    }
  }
}
```

## Tips for Best Results

### 1. Calibrate Your MIN_SCORE
- Start with `MIN_SCORE=0.5` to see what gets matched
- Check the similarity scores in the logs
- Adjust threshold based on your results:
  - `0.3-0.4`: Very broad matching
  - `0.5-0.6`: Balanced approach (recommended)
  - `0.7+`: Only very close matches

### 2. Review Generated Content
- First few applications: Check cover letters and emails manually
- Make sure AI is generating appropriate content
- Adjust your resume if matches are too low

### 3. Manage Application Rate
- Don't apply to hundreds of jobs at once
- Consider processing in batches over several days
- Respect the 7-day cooldown for repeated emails

### 4. Monitor Your Progress
```bash
# Check application status
make check-status

# View applied jobs
cat application_pipeline/application_materials/applied.json
```

## Troubleshooting

### Script stops with error
- **Solution**: Just run the same command again. It will resume from `offset.txt`

### "Already applied to job X"
- **Normal**: The script tracks applications and won't reapply
- **Reset**: If needed, use `make reset-applied` (careful: loses all history)

### Low similarity scores
- **Check**: Your resume content vs job descriptions
- **Update**: Make sure resume includes relevant keywords
- **Lower threshold**: Use `MIN_SCORE=0.3` for broader matching

### No email in offers
- **Skipped**: Jobs without email addresses are automatically skipped
- **Check**: Your offers JSON file has valid email fields

### Email generation issues
- **AI quality**: Emails are auto-generated with no placeholders
- **Fallback**: Uses MetaAI if no GEMINI_KEY is set

## Requirements

Before running, ensure you have:
- ✅ Resume PDF at `application_pipeline/application_materials/resume.pdf`
- ✅ Email credentials configured in `.env`
- ✅ Valid offers JSON file
- ✅ Dependencies installed (`make install`)

## Advanced: Direct Python Usage

If you need more control, use the Python script directly:

```bash
uv run python3 apply_from_offers.py \
  --offers_file offers_2025-11-10-10-57-35.json \
  --first_name Mehdi \
  --min_score 0.5 \
  --batch_size 20 \
  --start_index 0 \
  --offset_file offset.txt
```

Additional parameters:
- `--batch_size`: Process only N jobs (default: all)
- `--start_index`: Start from position N (default: 0)
- `--resume_pdf_path`: Custom resume path
- `--mail_protocol`: Email provider (default: gmail.com)
- `--spell_variant`: Cover letter spelling (american, british, australian)

## See Also

- [Main README](../README.md) - General project documentation
- [Quick Start Guide](QUICK_START.md) - Getting started with the bot
- [Makefile](../Makefile) - All available commands
