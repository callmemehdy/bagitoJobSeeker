# LinkedIn Structure Analysis

## How to Run Analysis

### Option 1: Capture Fresh Samples (Recommended)
```bash
python3 analyze_linkedin_structure.py
```
This will:
1. Open LinkedIn in browser (visible)
2. Login and search for posts
3. Save HTML structure to `linkedin_debug_page.html`
4. Analyze and find all emails
5. Save analysis report to `linkedin_structure_analysis.json`

### Option 2: Analyze Existing HTML
```bash
python3 analyze_linkedin_structure.py analyze
```
This analyzes `linkedin_debug_page.html` if it already exists.

## What the Analysis Shows

### 1. Email Discovery
- Total emails found in HTML
- Unique emails (deduplicated)
- Context around each email (150 chars before/after)

### 2. HTML Structure Patterns
- Post container classes used
- Text content selectors
- "See more" button patterns
- Expandable content elements

### 3. Sample Extraction
- Individual post HTML structure
- Common patterns across posts
- Element hierarchy

## Expected Output

```
================================================================================
ANALYZING LINKEDIN HTML STRUCTURE
================================================================================

🔍 SEARCHING FOR EMAIL PATTERNS:
   Total emails found: 15
   Unique emails: 8
      • recruit@company.com
      • contact@startup.fr
      • hr@techfirm.com
      ...

📝 EMAIL CONTEXT (150 chars before and after):
   Email: recruit@company.com
   Context: ...Nous recrutons! Envoyez votre CV à recruit@company.com pour postuler...

🏗️  ANALYZING POST STRUCTURE:
   feed-shared-update: 12 occurrences
   reusable-search__result: 15 occurrences
   update-components: 24 occurrences
   ...

🔘 'SEE MORE' BUTTON PATTERNS:
   'see more': 18 occurrences
   'voir plus': 12 occurrences
   'show more': 5 occurrences
   ...

📄 SAMPLE POST HTML STRUCTURES:
   Pattern 1 found 15 posts
   Sample (first 1000 chars): <li class="reusable-search__result-container">...

✅ Analysis saved to linkedin_structure_analysis.json
```

## Understanding the Results

### Email Patterns Found
The analysis will show you:
- Where emails appear in the HTML
- What text surrounds them
- Which posts contain emails vs which don't

### Structure Insights
You'll learn:
- Which CSS selectors reliably find posts
- How content is organized (nested divs, classes, etc.)
- Where "see more" buttons are and their selectors
- Whether content is in direct text or nested elements

### Next Steps Based on Results

#### If emails ARE in HTML but NOT extracted:
1. Check the context - emails might be in:
   - Comments/replies (not main post)
   - Images (not extractable as text)
   - Obfuscated format (e.g., "user AT domain DOT com")
   - Nested deep in HTML structure

2. Update selectors in `linkedin_post_scraper.py`:
   - Add new text selectors found in analysis
   - Update "see more" button selectors
   - Improve content extraction logic

#### If emails are NOT in HTML at all:
- They might be in:
  - Lazy-loaded content (need more scrolling)
  - Separate API calls (need network inspection)
  - Pop-ups or modals (need interaction)
  - User profiles (need to visit profile pages)

## Files Generated

1. **`linkedin_debug_page.html`** (11MB+)
   - Full HTML snapshot of search results page
   - Contains all posts visible at time of capture

2. **`linkedin_structure_analysis.json`**
   - Structured analysis report
   - Email list and patterns
   - HTML statistics

3. **`linkedin_test_output.log`**
   - Detailed scraper logs
   - Shows which posts were processed
   - Indicates where emails were/weren't found

## Troubleshooting

### If no emails found:
```bash
# Check if debug HTML was saved
ls -lh linkedin_debug_page.html

# Open in browser to manually inspect
firefox linkedin_debug_page.html

# Search for @ symbol
grep -o '@' linkedin_debug_page.html | wc -l
```

### If scraper can't login:
```bash
# Check credentials
cat .env | grep LINKEDIN

# Run with visible browser
# Edit analyze_linkedin_structure.py: headless=False (already set)
```

### If posts found but no content:
- Check the analysis report for which selectors matched
- Look at "SAMPLE POST HTML STRUCTURES" output
- Posts might need more time to load (increase sleep times)

## Updating the Scraper

Based on analysis results, update these sections in `linkedin_post_scraper.py`:

### 1. Text Selectors (line ~575)
```python
text_selectors = [
    # Add patterns found in analysis
    ".new-class-found",
    "[data-testid='new-pattern']",
]
```

### 2. See More Buttons (line ~545)
```python
see_more_buttons = container.find_elements(By.CSS_SELECTOR, 
    # Add patterns from analysis
    "button[aria-label*='new pattern']"
)
```

### 3. Post Containers (line ~405)
```python
post_containers = self.driver.find_elements(By.CSS_SELECTOR,
    # Add patterns from analysis
    "li.new-container-class"
)
```

## Example Workflow

1. **Run analysis**:
   ```bash
   python3 analyze_linkedin_structure.py
   ```

2. **Review results**:
   - Check console output
   - Open `linkedin_structure_analysis.json`
   - Look at email contexts

3. **Inspect HTML manually**:
   ```bash
   firefox linkedin_debug_page.html
   # Use browser DevTools to inspect post structure
   ```

4. **Update scraper** based on findings

5. **Test changes**:
   ```bash
   make test-linkedin
   ```

6. **Iterate** until emails are correctly extracted
