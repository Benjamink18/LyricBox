# Data Enrichment Flow - Complete Walkthrough

## Overview

This document explains exactly what happens when you run the data enrichment pipeline, step by step, following one song ("Billie Jean" by Michael Jackson) through the entire process.

---

## How to Run

```bash
cd /Users/benkohn/Desktop/LyricBox/backend/data_enrichment
source ../venv/bin/activate
python data_enrichment_main.py
```

---

## The Complete Journey

### **START: You Run the Orchestrator**

File: `data_enrichment_main.py`  
Function: `run_enrichment()`

---

## STEP 1: Load Songs from CSV

**File:** `data_enrichment_main.py`  
**Function:** `read_songs_from_csv('songs_list.csv')`  
**Location:** `read_songs_csv.py`

### What Happens:
1. Opens `songs_list.csv`
2. Reads each row using Python's CSV reader
3. Converts each row to a Python dictionary:
   ```python
   {
       'artist': 'Michael Jackson',
       'track': 'Billie Jean',
       'peak_position': '1'
   }
   ```
4. Skips empty rows
5. Returns list of all 10 songs

### Output:
```python
[
    {'artist': 'James Bay', 'track': 'Hold Back The River', 'peak_position': '26'},
    {'artist': 'Michael Jackson', 'track': 'Billie Jean', 'peak_position': '1'},
    ... 8 more songs
]
```

---

## STEP 2: Call UG Scraper Module

**File:** `data_enrichment_main.py`  
**Function:** `scrape_chords(songs)`  
**Location:** `ug_scraper/ug_scraper_main.py`

### What Happens:
- Passes the entire list of 10 songs to the UG scraper module
- Waits for it to complete all scraping
- Receives results back when done

**Now we go INSIDE the UG scraper module...**

---

## STEP 3: Setup Browser (Once for All Songs)

**File:** `ug_scraper_main.py`  
**Function:** `setup_browser()`  
**Location:** `setup.py`

### What Happens:
1. Opens Chrome browser (visible window)
2. Navigates to `https://www.ultimate-guitar.com/`
3. Waits for page to load (2 seconds)
4. Looks for cookie popup
5. Clicks "I Accept" on cookie consent
6. **PAUSES and waits for YOU**
   - Displays message: "Please log in to your Ultimate Guitar Pro account"
   - You manually log in with your credentials
   - You press Enter when done
7. Returns the browser `page` object

### Why Only Once:
You log in ONCE and the browser stays open for all 10 songs - much more efficient!

---

## STEP 4: Loop Through Each Song

**File:** `ug_scraper_main.py`  
**Loop:** `for i, song in enumerate(songs_to_scrape, 1):`

### For Song #2: Michael Jackson - Billie Jean

Prints: `[2/10] Michael Jackson - Billie Jean`

Now calls: `scrape_song(page, 'Michael Jackson', 'Billie Jean')`

---

## INSIDE SCRAPE_SONG (The Core Scraping Logic)

**File:** `scrape_song.py`

---

## STEP 5: Search for the Song

**Function:** `search_song(page, "Michael Jackson Billie Jean")`  
**Location:** `search.py`

### What Happens:
1. Clicks the search icon button on Ultimate Guitar
2. Finds the search input box (HTML: `input[placeholder*='artist']`)
3. Types "Michael Jackson Billie Jean" into the box
4. Presses Enter key
5. Waits 2 seconds for search results to load

---

## STEP 6: Act Like a Human

**Function:** `act_human(page)`  
**Location:** `human_behavior.py`

### What Happens:
1. Pauses for 1-3 seconds (random amount)
2. Randomly moves mouse to 2-4 different positions
3. Maybe scrolls down 200-800 pixels
4. Maybe scrolls back up 100-200 pixels
5. Small delays between actions (0.3-1 seconds)

### Why:
Makes the scraper look like a real person browsing the site, avoiding bot detection.

---

## STEP 7: Find Official Tab URL

**Function:** `find_official_tabs(page)`  
**Location:** `find_official.py`

### What Happens:
1. Scans all links on the search results page
2. Looks for links containing both:
   - `/tab/` in the URL
   - `official` in the URL (case-insensitive)
3. Collects all matching URLs

### Example URL Found:
```
https://www.ultimate-guitar.com/tab/michael-jackson/billie-jean-official-2138495
```

### If No Official Tab:
- Returns empty list `[]`
- Song fails
- Gets logged to `chords_not_found.txt`
- Moves to next song

---

## STEP 8: Navigate to Tab Page

**Function:** `click_tab(page, url)`  
**Location:** `click_tab.py`

### What Happens:
1. Navigates browser to the official tab URL
2. Waits 3 seconds for page to fully load
3. Checks for ANOTHER cookie popup on this page
4. If found, clicks "I Accept" using:
   ```python
   page.get_by_text("I Accept", exact=True).first.click(force=True)
   ```

### Why Force Click:
Sometimes cookie popups are technically "hidden" but still work when clicked.

---

## STEP 9: Switch to Chord Mode

**Function:** `click_chords(page)`  
**Location:** `click_chords.py`

### What Happens:
1. Finds button with text "Chords" (case-insensitive)
2. Uses `page.get_by_text("Chords", exact=True).first`
3. Force-clicks it (bypasses visibility checks)
4. Waits 2 seconds for page to re-render with chords visible

### Why Force Click:
The button might not be considered "visible" by Playwright but works fine when clicked.

---

## STEP 10: Extract the Musical Key

**Function:** `extract_tonality(page)`  
**Location:** `extract_tonality.py`

### What Happens:
1. Gets all visible text from the page: `page.inner_text("body")`
2. Searches for pattern: `Key: X` using regex: `r'Key:\s*([A-G][#b]?m?)'`
3. Extracts just the key part

### For Billie Jean:
Finds: `Key: F#m`  
Returns: `"F#m"`

---

## STEP 11: Extract All Chords

**Function:** `extract_chords(page)`  
**Location:** `extract_chords.py`

### What Happens:
1. Runs JavaScript code directly in the browser using `page.evaluate()`
2. Creates a `TreeWalker` to traverse the DOM tree in order
3. Looks for two types of elements:
   - **Text nodes** containing section markers: `[Intro]`, `[Verse 1]`, `[Chorus]`
   - **Chord elements**: `<span data-name="F#m">` tags
4. Groups chords by their section
5. Auto-numbers duplicate sections: "Chorus", "Chorus (2)", "Chorus (3)"

### For Billie Jean, Returns:
```python
{
    'Intro': ['F#m', 'G#m', 'F#m', 'G#m'],
    'Verse 1': ['F#m', 'D', 'F#m', 'D', 'F#m', 'E'],
    'Chorus': ['F#m', 'D', 'A', 'E', 'F#m', 'D'],
    'Verse 2': ['F#m', 'D', 'F#m', 'D'],
    'Chorus (2)': ['F#m', 'D', 'A', 'E']
}
```

---

## STEP 12: Process Chords into 6 Versions

**Function:** `process_chords(tonality, chords)`  
**Location:** `process_chords.py`

For EACH section (Intro, Verse 1, Chorus, etc.), creates 6 different versions of the chord sequence.

### Taking the Chorus as an Example:
Original chords: `['F#m', 'D', 'A', 'E']`

#### **Version 1: Original (As Scraped)**
```python
['F#m', 'D', 'A', 'E']
```
Just stores exactly what was on Ultimate Guitar.

---

#### **Version 2: Original Simplified**
**Function:** `simplify_chord(chord)`  
**Location:** `simplify_chord.py`

Removes embellishments like:
- `7`, `9`, `11`, `13`
- `maj7`, `min7`
- `add9`, `add11`
- `sus2`, `sus4`

Keeps only:
- Root note (F#, D, A, E)
- Basic quality: `m` (minor), `dim` (diminished), `aug` (augmented)

**Result:**
```python
['F#m', 'D', 'A', 'E']  # Already simple in this case
```

**Example with complex chords:**
- `Gmaj7` → `G`
- `Am7` → `Am`
- `Dsus4` → `D`
- `Cadd9` → `C`

---

#### **Version 3: Transposed to C Major**
**Function:** `transpose_to_c(tonality, chord)`  
**Location:** `transpose_to_c.py`

**Step 1:** If key is minor (F#m), convert to relative major
- F#m relative major = A major

**Step 2:** Calculate interval from A to C
- A to C = 3 semitones up

**Step 3:** Transpose every chord by 3 semitones:
- F#m + 3 = Am
- D + 3 = F
- A + 3 = C
- E + 3 = G

**Result:**
```python
['Am', 'F', 'C', 'G']
```

**Why:** Puts all songs in the same key for easier comparison.

---

#### **Version 4: Transposed to C Simplified**

**Optimization:** Instead of transposing then simplifying, we:
1. Simplify the ORIGINAL chords first
2. Then transpose the simplified version

**Result:**
```python
['Am', 'F', 'C', 'G']
```

---

#### **Version 5: Roman Numerals (Full)**
**Function:** `convert_to_roman(chord_in_c)`  
**Location:** `convert_to_roman.py`

Takes the "in C" version and converts to scale degrees:

**C Major Scale:**
- C = I (1st degree, major)
- D = ii (2nd degree, minor)
- E = iii (3rd degree, minor)
- F = IV (4th degree, major)
- G = V (5th degree, major)
- A = vi (6th degree, minor)
- B = vii° (7th degree, diminished)

**For our chords:**
- Am = vi (6th degree, minor)
- F = IV (4th degree, major)
- C = I (1st degree, major)
- G = V (5th degree, major)

**Result:**
```python
['vi', 'IV', 'I', 'V']
```

**Why:** Shows harmonic function - "vi-IV-I-V" is a common progression regardless of key.

---

#### **Version 6: Roman Numerals Simplified**
Same as Version 5 but uses the simplified chords.

**Result:**
```python
['vi', 'IV', 'I', 'V']
```

---

### Why 6 Versions?

Allows flexible searching:
- **Original** - How the song is actually played
- **Simplified** - Basic harmonic structure
- **In C** - Compare all songs in the same key
- **Roman numerals** - Search by harmonic function
- Users can search using any version depending on their needs

---

## STEP 13: Navigate Back to Homepage

**File:** `scrape_song.py`

### What Happens:
```python
page.goto("https://www.ultimate-guitar.com/")
page.wait_for_timeout(2000)
```

### Why:
Ensures the search box is available for the next song in the batch.

---

## STEP 14: Return Chord Data

**File:** `scrape_song.py`

Returns to `ug_scraper_main.py`:
```python
{
    'tonality': 'F#m',
    'processed_sections': {
        'Intro': {
            'original': ['F#m', 'G#m', 'F#m', 'G#m'],
            'original_simple': ['F#m', 'G#m', 'F#m', 'G#m'],
            'in_c': ['Am', 'Bm', 'Am', 'Bm'],
            'in_c_simple': ['Am', 'Bm', 'Am', 'Bm'],
            'roman': ['vi', 'vii', 'vi', 'vii'],
            'roman_simple': ['vi', 'vii', 'vi', 'vii']
        },
        'Verse 1': { ... 6 versions },
        'Chorus': { ... 6 versions },
        'Verse 2': { ... 6 versions },
        'Chorus (2)': { ... 6 versions }
    }
}
```

---

## BACK IN UG_SCRAPER_MAIN

**File:** `ug_scraper_main.py`

---

## STEP 15: Save to Supabase

**Function:** `save_chords_to_supabase(...)`  
**Location:** `chords_to_supabase.py`

### What Happens:
1. Gets Supabase credentials from `.env` file:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
2. Creates Supabase client connection
3. For EACH section (Intro, Verse 1, Chorus, Verse 2, Chorus 2), creates ONE database row:

```python
{
    "artist_name": "Michael Jackson",
    "track_name": "Billie Jean",
    "tonality": "F#m",
    "section_name": "Chorus",
    "chords_original": ['F#m', 'D', 'A', 'E', 'F#m', 'D'],
    "chords_original_simple": ['F#m', 'D', 'A', 'E', 'F#m', 'D'],
    "chords_in_c": ['Am', 'F', 'C', 'G', 'Am', 'F'],
    "chords_in_c_simple": ['Am', 'F', 'C', 'G', 'Am', 'F'],
    "chords_roman": ['vi', 'IV', 'I', 'V', 'vi', 'IV'],
    "chords_roman_simple": ['vi', 'IV', 'I', 'V', 'vi', 'IV']
}
```

4. Inserts ALL rows in one batch: `supabase.table("ug_chords").insert(rows).execute()`
5. Returns number of rows saved (e.g., 5 sections = 5 rows)

### Database Result:
**Table:** `ug_chords`  
**New Rows:** 5 (one for each section of Billie Jean)  
**Each Row Contains:** All 6 chord versions as PostgreSQL arrays

---

## STEP 16: Track Success

**File:** `ug_scraper_main.py`

### If Save Successful:
```python
successful += 1
print("  ✓ Success")
```

### If Save Failed:
```python
failed += 1
print("  ✗ Failed (database save error)")
```

---

## STEP 17: Loop Continues

**File:** `ug_scraper_main.py`

Repeats Steps 5-16 for songs #3, #4, #5, etc. until all 10 songs are processed.

Browser stays open the whole time - only logs in once!

---

## STEP 18: Close Browser

**File:** `ug_scraper_main.py`

```python
browser.close()
```

Closes the Chrome window after all songs are processed.

---

## STEP 19: Return Results

**File:** `ug_scraper_main.py`  
**Returns to:** `data_enrichment_main.py`

```python
{
    'successful': 8,  # Songs successfully scraped AND saved
    'failed': 2,      # Either no official tab OR database save error
    'total': 10
}
```

---

## BACK IN DATA_ENRICHMENT_MAIN

**File:** `data_enrichment_main.py`  
**Function:** `run_enrichment()`

---

## STEP 20: Display Summary

### Console Output:
```
======================================================================
DATA ENRICHMENT PIPELINE
======================================================================

Step 1: Loading songs from CSV...
  ✓ Loaded 10 songs

Step 2: Scraping chord data from Ultimate Guitar...
[1/10] James Bay - Hold Back The River
  ✓ Success
[2/10] Michael Jackson - Billie Jean
  ✓ Success
[3/10] Myles Smith - Stay If You Wanna Dance
  ✓ Success
...
[9/10] Hotel California - Eagles
  ✗ Failed (no official tab)
[10/10] Smells Like Teen Spirit - Nirvana
  ✓ Success

UG Scraping: 8 successful, 2 failed

  ✓ Chords: 8/10 successful

======================================================================
ENRICHMENT COMPLETE
======================================================================
Total songs processed: 10
Chord data: 8 successful, 2 failed
======================================================================
```

---

## FINAL RESULTS

### In Supabase Database (`ug_chords` table):
- **Total Rows:** ~40 (8 successful songs × ~5 sections each)
- **Each Row Contains:**
  - Artist name
  - Track name
  - Original key (tonality)
  - Section name
  - 6 versions of chord sequences (as arrays)

### In `chords_not_found.txt`:
```
2025-12-04 15:30:45 - Eagles - Hotel California
2025-12-04 15:31:20 - Some Other Artist - Some Song
```

### Songs WITHOUT official tabs are logged for future reference.

---

## Future Expansion

The pipeline is designed to easily add more enrichment steps:

### Step 3: Musixmatch Metadata
- BPM
- Musical key
- Genres
- Mood tags
- Release date

### Step 4: Lyrics
- Multi-source API (Genius, Musixmatch, etc.)

### Step 5: Concepts
- Claude AI analysis of themes

### Step 6: Rhymes
- Claude AI rhyme scheme analysis

Each step follows the same pattern:
1. Create a function that accepts the song list
2. Process each song
3. Save to Supabase
4. Return success/failure counts
5. Call from `run_enrichment()` in sequence

---

## File Structure Summary

```
backend/
├── data_enrichment/
│   ├── data_enrichment_main.py    # Orchestrator (run_enrichment)
│   ├── read_songs_csv.py          # CSV reader
│   └── songs_list.csv             # Input data (10 songs)
│
└── ug_scraper/
    ├── ug_scraper_main.py         # Batch processor (scrape_chords)
    ├── scrape_song.py             # Core logic for one song
    ├── setup.py                   # Browser setup & login
    ├── search.py                  # Search functionality
    ├── find_official.py           # Find official tab URLs
    ├── click_tab.py               # Navigate to tab page
    ├── click_chords.py            # Switch to chord view
    ├── extract_tonality.py        # Get musical key
    ├── extract_chords.py          # Extract chord data
    ├── process_chords.py          # Create 6 versions
    ├── simplify_chord.py          # Remove embellishments
    ├── transpose_to_c.py          # Transpose to C major
    ├── convert_to_roman.py        # Convert to Roman numerals
    ├── chords_to_supabase.py      # Save to database
    ├── human_behavior.py          # Anti-bot behavior
    └── log_missing_chords.py      # Log failed songs
```

---

## Key Design Principles

1. **One file per function** - Easy to understand and maintain
2. **Well-commented** - Plain English explanations
3. **Modular** - Each piece does one thing well
4. **Reusable** - Functions can be imported and called from anywhere
5. **Testable** - Each file can be run independently for testing
6. **Separation of concerns** - Scraping vs. enrichment vs. storage

---

**End of Flow Documentation**

