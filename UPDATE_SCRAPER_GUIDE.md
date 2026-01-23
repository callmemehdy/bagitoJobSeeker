# How to Update Scraper Based on LinkedIn Analysis

## Quick Start

1. **Run the analysis script**:
   ```bash
   python3 analyze_linkedin_structure.py
   ```

2. **Check the outputs**:
   - Console output (shows emails found and context)
   - `linkedin_structure_analysis.json` (structured data)
   - `linkedin_debug_page.html` (raw HTML)

3. **Use this guide to update the scraper**

---

## Step-by-Step Update Process

### Step 1: Identify What's Wrong

Check the scraper logs for these patterns:

#### Pattern A: "Post found but no emails"
```
ℹ️  Post found but no emails: 'Some post text...'
```
**Meaning**: Post was found and text was extracted, but no emails detected
**Likely cause**: 
- Emails are in a different format (e.g., "user AT domain DOT com")
- Emails are in nested elements not being checked
- Email regex pattern doesn't match (e.g., internationalized domains)

#### Pattern B: "No post containers found"
```
Found 0 post containers on page
```
**Meaning**: Scraper can't find posts at all
**Likely cause**:
- Post container selectors are outdated
- LinkedIn changed their HTML structure
- Page not fully loaded

#### Pattern C: "Post text too short"
```
Post text length: 15 chars
Post text too short (15 chars), checking HTML...
```
**Meaning**: Found post but can't extract text content
**Likely cause**:
- Text selector doesn't match current HTML
- Content is in shadowDOM or iframe
- "See more" button not being clicked

---

### Step 2: Analyze the HTML Structure

Open `linkedin_debug_page.html` in browser:

```bash
firefox linkedin_debug_page.html
```

Then use DevTools (F12):

1. **Find a post with an email you can see visually**
2. **Right-click the email → Inspect Element**
3. **Note the path**: 
   ```
   div.feed-shared-update-v2 
     → div.feed-shared-text
       → span[dir="ltr"]
         → "email@example.com"
   ```

4. **Check parent containers**:
   - What class is on the main post container?
   - What classes are on the text content?
   - Are there any data attributes?

---

### Step 3: Update Post Container Selectors

**File**: `scrapers/linkedin_post_scraper.py`
**Line**: ~405

#### Current code:
```python
# Strategy 1: Traditional selectors
containers_1 = self.driver.find_elements(By.CSS_SELECTOR, 
    "li.reusable-search__result-container, div.feed-shared-update-v2")
```

#### How to update:
1. Find the class name of posts in DevTools
2. Add to the selector:
```python
containers_1 = self.driver.find_elements(By.CSS_SELECTOR, 
    "li.reusable-search__result-container, "
    "div.feed-shared-update-v2, "
    "div.NEW-CLASS-YOU-FOUND")  # ← Add here
```

**Example**:
```python
"li.search-result__wrapper, "
"div.update-components-update, "
"article[data-urn*='activity']"
```

---

### Step 4: Update Text Content Selectors

**File**: `scrapers/linkedin_post_scraper.py`
**Line**: ~575

#### Current code:
```python
text_selectors = [
    ".feed-shared-update-v2__description",
    ".feed-shared-text",
    ".update-components-text",
    # ...
]
```

#### How to update:
1. In DevTools, find where the email text is
2. Note its class or data attribute
3. Add to list:

```python
text_selectors = [
    ".feed-shared-update-v2__description",
    ".feed-shared-text",
    ".NEW-TEXT-CLASS",  # ← Add new selector
    "[data-testid='post-text']",  # ← Or data attribute
    # ...
]
```

---

### Step 5: Update "See More" Button Selectors

**File**: `scrapers/linkedin_post_scraper.py`
**Line**: ~545

#### Current code:
```python
see_more_buttons = container.find_elements(By.CSS_SELECTOR, 
    "button[aria-label*='see more'], "
    "button[aria-label*='Show more'], "
    # ...
)
```

#### How to update:
1. Find the "see more" button in DevTools
2. Check its attributes:
   - `aria-label`
   - `class`
   - `data-*` attributes
3. Add pattern:

```python
"button[aria-label*='voir plus'], "  # French
"button[aria-label*='ver más'], "     # Spanish
"button.NEW-SEE-MORE-CLASS"           # New class
```

---

### Step 6: Improve Email Extraction

**File**: `scrapers/linkedin_post_scraper.py`
**Line**: ~625

#### Current email regex:
```python
emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post_text)
```

#### If emails are obfuscated:

```python
# Also check for obfuscated formats
post_text_normalized = post_text.replace(' AT ', '@').replace(' DOT ', '.')
post_text_normalized = post_text_normalized.replace('[at]', '@').replace('[dot]', '.')

emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post_text_normalized)
```

---

### Step 7: Test Your Changes

```bash
# Run quick test
python3 analyze_linkedin_structure.py

# Or use make command
make test-linkedin
```

Check output for:
- ✅ "Found X post containers" (X > 0)
- ✅ "Post text length: XXX chars" (XXX > 100)
- ✅ "✓ Found post with N email(s)"

---

## Common Issues & Solutions

### Issue: "Emails visible in browser but not extracted"

**Solution**: The email might be in a nested element.

Try getting ALL text from container:
```python
# In _parse_post method, add this fallback:
if not post_text:
    post_text = container.get_attribute('innerText')
    # or
    post_text = container.get_attribute('textContent')
```

### Issue: "See more button not clicking"

**Solution**: Button might be in iframe or needs different click method.

```python
# Instead of:
button.click()

# Try:
self.driver.execute_script("arguments[0].click();", button)

# Or scroll into view first:
self.driver.execute_script("arguments[0].scrollIntoView();", button)
time.sleep(0.5)
button.click()
```

### Issue: "Posts load but immediately disappear"

**Solution**: Stale element reference. Re-find elements.

```python
# Before processing:
post_html = container.get_attribute('outerHTML')
# Then parse from HTML string instead of live element
```

---

## Validation Checklist

After updating, verify:

- [ ] Post containers are found (> 0)
- [ ] Text is extracted (> 100 chars per post)
- [ ] "See more" buttons are clicked
- [ ] Emails are found in text
- [ ] Emails pass filter (not noreply@, etc)
- [ ] Duplicate posts are skipped
- [ ] Scraper scrolls through all posts

---

## Need More Help?

1. Save the HTML: The scraper saves `linkedin_debug_page.html`
2. Inspect manually: Open in browser, find working post
3. Copy full path: Right-click element → Copy → Copy selector
4. Test selector in console:
   ```javascript
   document.querySelectorAll('YOUR_SELECTOR')
   ```
5. Update scraper with working selector

---

## Example: Full Update Flow

```python
# 1. Found posts use class "result-card"
containers_1 = self.driver.find_elements(By.CSS_SELECTOR, 
    "div.result-card")

# 2. Text is in span[dir="ltr"]
text_selectors = [
    "span[dir='ltr']",
    ".result-card__text"
]

# 3. See more button has data-control-name="see_more"
see_more_buttons = container.find_elements(By.CSS_SELECTOR,
    "button[data-control-name='see_more']")

# 4. Emails sometimes use [at] instead of @
post_text = post_text.replace('[at]', '@')
```

Test again and iterate!
