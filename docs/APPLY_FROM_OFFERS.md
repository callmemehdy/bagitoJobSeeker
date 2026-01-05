# Apply from Offers File

This feature allows you to apply to jobs from a saved offers JSON file using batch processing and similarity checking.

## Features

- **Batch Processing**: Process jobs in batches by specifying start index and batch size
- **Similarity Checking**: Uses sentence transformers to calculate resume-job description similarity
- **Smart Skip Logic**: 
  - Skips already applied jobs
  - Skips emails contacted within the last 7 days
  - Skips jobs below minimum similarity score
- **Automated Application**: Generates personalized cover letters and sends applications via email

## Usage

### Basic Usage (Apply to all matching jobs)

```bash
python apply_from_offers.py \
  --offers_file offers_2025-11-10-10-57-35.json \
  --first_name "Your Name" \
  --min_score 0.5
```

### Batch Processing (Process 10 jobs at a time)

```bash
# Process first 10 jobs
python apply_from_offers.py \
  --offers_file offers_2025-11-10-10-57-35.json \
  --first_name "Your Name" \
  --min_score 0.5 \
  --batch_size 10 \
  --start_index 0

# Process next 10 jobs
python apply_from_offers.py \
  --offers_file offers_2025-11-10-10-57-35.json \
  --first_name "Your Name" \
  --min_score 0.5 \
  --batch_size 10 \
  --start_index 10
```

### Advanced Options

```bash
python apply_from_offers.py \
  --offers_file offers_2025-11-10-10-57-35.json \
  --first_name "Your Name" \
  --min_score 0.6 \
  --batch_size 20 \
  --start_index 0 \
  --resume_pdf_path "path/to/resume.pdf" \
  --mail_protocol "gmail.com" \
  --spell_variant "american" \
  --model "gemini-2.5-flash"
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--offers_file` | Yes | - | Path to the offers JSON file |
| `--first_name` | Yes | - | Your first name for personalizing applications |
| `--batch_size` | No | All jobs | Number of jobs to process in this batch |
| `--start_index` | No | 0 | Starting position in the offers file |
| `--min_score` | No | 0.5 | Minimum similarity score (0.0-1.0) to apply |
| `--resume_pdf_path` | No | application_pipeline/application_materials/resume.pdf | Path to your resume |
| `--cover_letter_path` | No | application_pipeline/application_materials/cover_letter.pdf | Path for generated cover letter |
| `--applied_path` | No | application_pipeline/application_materials/applied.json | Path to track applied jobs |
| `--mail_protocol` | No | gmail.com | Email provider |
| `--spell_variant` | No | american | Spelling variant for cover letters |
| `--model` | No | gemini-2.5-flash | AI model for generating content |

## How It Works

1. **Loads Offers**: Reads the JSON file containing job offers
2. **Batch Selection**: Selects jobs based on start_index and batch_size
3. **Similarity Check**: Calculates similarity between your resume and job description
4. **Filtering**: Skips jobs that:
   - You've already applied to
   - Have emails contacted recently (< 7 days)
   - Have similarity score below min_score
   - Don't have contact email or description
5. **Application**: For qualifying jobs:
   - Generates personalized cover letter
   - Creates email content
   - Sends application with resume and cover letter
   - Records application in applied.json

## Tips

- Start with a higher `--min_score` (e.g., 0.6 or 0.7) to focus on best matches
- Use batch processing to manage applications over time and avoid overwhelming your email
- Monitor the `applied.json` file to track your applications
- Check logs for similarity scores to calibrate your `--min_score` threshold

## Environment Requirements

Ensure you have set up:
- `GEMINI_KEY` in your `.env` file (or it will use meta api)
- Email credentials configured for your mail protocol
- Resume PDF in the specified path
