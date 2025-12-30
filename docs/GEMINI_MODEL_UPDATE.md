# Gemini Model Update Guide

## Issue
If you encounter an error like:
```
404 NOT_FOUND: models/gemini-1.5-flash is not found for API version v1beta
```

This means the Gemini model name has been deprecated and updated by Google.

## Solution

The project has been updated to use **`gemini-2.5-flash`** as the default model (December 2025).

### Available Models (as of December 2025)

#### **Recommended Models:**
- `gemini-2.5-flash` (default) - Fast, balanced performance
- `gemini-2.5-pro` - Higher quality, slower
- `gemini-flash-latest` - Always points to latest flash version

#### **Other Available Models:**
- `gemini-2.0-flash` - Previous generation flash
- `gemini-2.0-flash-001` - Specific version
- `gemini-exp-1206` - Experimental model
- `gemini-3-flash-preview` - Preview of next generation
- `gemini-3-pro-preview` - Preview of next generation pro

### How to Change Model

You can specify a different model when running the application:

```bash
# Use gemini-2.5-pro for better quality
uv run python3 main.py --first_name YourName --model gemini-2.5-pro

# Use the latest flash model
uv run python3 main.py --first_name YourName --model gemini-flash-latest
```

### How to Check Available Models

Run this script to see all currently available models:

```python
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_KEY'))

print('Available Gemini models:')
for model in client.models.list():
    if 'gemini' in model.name.lower():
        print(f'  - {model.name}')
```

### Updating Default Model

If you want to permanently change the default model, edit `config/args.py`:

```python
parser.add_argument('--model', 
                    type=str,
                    help='gemini model',
                    default="gemini-2.5-flash")  # Change this line
```

## Cost Considerations

- **Flash models** (e.g., `gemini-2.5-flash`) - Faster and cheaper, good for most use cases
- **Pro models** (e.g., `gemini-2.5-pro`) - Higher quality but slower and more expensive
- **Latest aliases** (e.g., `gemini-flash-latest`) - Always use newest version but may change behavior

## Troubleshooting

### Error: "Model not found"
- Check your Gemini API key is valid
- Ensure you're using a current model name
- Run the check script above to see available models

### Error: "Quota exceeded"
- You've reached your Gemini API quota
- Wait for quota to reset or upgrade your plan
- Consider using the MetaAI fallback (remove GEMINI_KEY from .env)

### Error: "Invalid API key"
- Check your `.env` file has the correct `GEMINI_KEY`
- Regenerate your API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

## History

- **December 2025**: Updated default from `gemini-1.5-flash` to `gemini-2.5-flash`
- **Reason**: Google deprecated the 1.5 series models in favor of 2.x series
