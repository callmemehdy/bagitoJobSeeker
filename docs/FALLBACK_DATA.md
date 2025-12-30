## added by Mehdy
# Cached Data Fallback Feature
## Overview

The job scraper now includes an automatic fallback mechanism that uses cached job data from `info.json` when the Apify API fails or when your free plan expires.

## How It Works

1. **Primary Method**: The scraper attempts to fetch fresh job listings from the Apify Seek Job Scraper API
2. **Fallback Method**: If the API fails (e.g., expired free plan, network issues), it automatically loads jobs from `./info.json`
3. **Smart Matching**: Cached jobs are filtered and matched to your search terms when possible

## Usage

No changes needed! The fallback is automatic. When running:

```bash
uv run main.py
```

You'll see logs like:
- **Success**: `Found X jobs for search term: Software Engineer`
- **Fallback**: `All API calls failed. Falling back to cached data...`

## Updating Cached Data

To update your cached job data when the API is working:

1. Run the scraper when your Apify plan is active
2. Save the results to `info.json`:

```python
# After successful scrape
import json
with open('info.json', 'w') as f:
    json.dump(job_data, f, indent=2)
```

Or manually add job listings in the same format as the current `info.json`.

## Benefits

-  **Zero Downtime**: Continue processing applications even when API is unavailable
-  **No Code Changes**: Fallback happens automatically
-  **Cost Savings**: Use cached data instead of paying for API calls during testing
-  **Offline Testing**: Develop and test without API access

## Data Format

The cached data should be a JSON array of job objects:

```json
[
  {
    "id": "12345",
    "title": "Software Engineer",
    "roleId": "software-engineer",
    "emails": ["hr@company.com"],
    "content": {
      "sections": ["job description text..."]
    },
    ...
  }
]
```

## Limitations

- Cached jobs won't include newly posted positions
- You should update `info.json` periodically when the API is available
- The system will use ALL cached jobs for each search term if no specific matches are found

## Troubleshooting

**Issue**: No cached data found
- **Solution**: Ensure `info.json` exists in the project root directory

**Issue**: Wrong jobs being processed
- **Solution**: Update your cached data or modify the `_job_matches_search()` method in `scraper.py`

## Next Steps

When you're ready to use the live API again:
1. Upgrade your Apify plan at https://console.apify.com/
2. The system will automatically use live data
3. Consider saving fresh results to update your cache
