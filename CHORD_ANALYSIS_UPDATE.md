# Chord Analysis Pipeline - Major Update

## Date: December 5, 2025

---

## Summary

Fixed critical issues with chord analysis logic and added capo/tuning support for accurate musical analysis.

---

## Changes Made

### 1. Fixed Minor Key Analysis
**Files:** `backend/ug_scraper/transpose_to_c.py`, `backend/ug_scraper/convert_to_roman.py`

**Problem:** Minor keys were being converted to relative major (Em → G major), breaking Roman numeral analysis.

**Solution:**
- Minor keys now transpose to **Am** (the vi of C major)
- Major keys transpose to **C**
- All analysis happens within C major scale framework
- Am correctly becomes "vi" (not analyzed as separate minor key)

**Example:**
```
Song in Em with chords: Em, C, G, D
OLD: Em → G major → C → Wrong analysis
NEW: Em → Am (vi of C) → Correct analysis in C major framework
```

---

### 2. Fixed Roman Numeral Output
**File:** `backend/ug_scraper/convert_to_roman.py`

**Problem:** Roman numerals had redundant 'm' markers (e.g., "vim", "iiim").

**Solution:**
- Lowercase = minor (vi, iii, ii)
- Uppercase = major (I, V, IV)
- No redundant quality markers
- Clean output: `vi7`, `viadd9` (not `vim7`, `vimad9`)

---

### 3. Added Capo Support
**New Files:**
- `backend/ug_scraper/extract_capo_and_tuning.py` - Extracts capo position and tuning from UG
- `backend/ug_scraper/transpose_by_capo.py` - Transposes chord shapes by capo amount

**Problem:** UG shows chord **shapes** (finger positions), not actual sounds when capo is used.

**Solution:**
- Extract capo position from UG metadata
- Transpose all chord shapes by capo amount to get actual sounding chords
- The key shown is already correct (don't transpose)
- Analyze actual chords in the correct key

**Example:**
```
UG Shows: Key=Dm, Capo=5, Shape=Dm
OLD: Analyzed Dm shape as i chord (wrong - it's actually Gm)
NEW: Dm shape + capo 5 → Gm actual → iv chord in Dm ✓
```

---

### 4. Added Alternate Tuning Detection
**New Files:**
- `backend/ug_scraper/check_tuning.py` - Detects standard vs alternate tunings
- `backend/ug_scraper/log_alternate_tuning.py` - Logs alternate tunings for analysis

**Problem:** Alternate tunings (DADGAD, Drop D, etc.) make chord shapes produce different notes.

**Solution:**
- Detect if tuning is standard (E A D G B E)
- If alternate: Log to `backend/logs/chords_alternate_tuning.txt` and skip
- Allows data-driven decision on which tunings to support later

**Log Format:**
```
2025-12-05 14:30:15 | Artist | Track | Tuning: DADGAD | Capo: 0
```

---

### 5. Fixed Metadata Handling
**File:** `backend/data_enrichment/data_enrichment_main.py`

**Problem:** Pipeline was failing songs if any metadata was missing (too strict).

**Solution:**
- **Partial metadata = OK** → Log warning and continue with NULL values
- **No lyrics = FAIL** → Delete song from database (lyrics are required)
- Songs can now have partial GetSongBPM data and still be created

---

### 6. Fixed Tuning Extraction
**File:** `backend/ug_scraper/extract_capo_and_tuning.py`

**Problem:** UG returns tuning as dict: `{'name': 'Standard', 'value': 'E A D G B E', 'index': 1}`

**Solution:**
- Extract `value` field from tuning object
- Handle both dict and string formats (safety)
- Works with all UG tuning variations

---

## Updated Files

### Core Chord Processing
- ✅ `backend/ug_scraper/transpose_to_c.py` - Fixed minor key logic
- ✅ `backend/ug_scraper/convert_to_roman.py` - Fixed Roman numeral output
- ✅ `backend/ug_scraper/process_chords.py` - No changes (still works perfectly)
- ✅ `backend/ug_scraper/simplify_chord.py` - No changes

### Ultimate Guitar Scraping
- ✅ `backend/ug_scraper/scrape_song.py` - Added capo + tuning handling
- ✅ `backend/ug_scraper/extract_tonality.py` - No changes
- ✅ `backend/ug_scraper/extract_chords.py` - No changes
- ✅ `backend/ug_scraper/__init__.py` - Added new exports

### Data Enrichment
- ✅ `backend/data_enrichment/data_enrichment_main.py` - Fixed metadata failure logic

---

## Test Results

### 1. Minor Key Analysis ✓
```
Em → Am → vi (correct)
C  → F  → IV (correct)
G  → C  → I  (correct)
```

### 2. Capo Transposition ✓
```
Dm shape + capo 5 → Gm (actual sound) ✓
Key Dm stays Dm (not transposed) ✓
Gm analyzed as iv in Dm ✓
```

### 3. Tuning Detection ✓
```
"E A D G B E" → Standard ✓
"DADGAD"      → Alternate (logged & skipped) ✓
"Drop D"      → Alternate (logged & skipped) ✓
```

### 4. Partial Metadata ✓
```
No genres → Continue with empty array ✓
No BPM    → Continue with NULL values ✓
No lyrics → DELETE song ✓
```

---

## File Structure

```
backend/
├── ug_scraper/
│   ├── transpose_to_c.py              [UPDATED - Fixed minor keys]
│   ├── convert_to_roman.py            [UPDATED - Fixed Roman output]
│   ├── extract_capo_and_tuning.py     [NEW - Capo extraction]
│   ├── transpose_by_capo.py           [NEW - Capo transposition]
│   ├── check_tuning.py                [NEW - Tuning detection]
│   ├── log_alternate_tuning.py        [NEW - Tuning logging]
│   ├── scrape_song.py                 [UPDATED - Capo + tuning]
│   └── __init__.py                    [UPDATED - New exports]
├── data_enrichment/
│   └── data_enrichment_main.py        [UPDATED - Metadata handling]
└── logs/
    └── chords_alternate_tuning.txt    [NEW - Auto-generated]
```

---

## Benefits

1. **Accurate Analysis** - Chord analysis now matches actual musical content
2. **Capo Support** - Handles capo correctly (critical for many songs)
3. **Flexible Metadata** - Doesn't fail on partial data
4. **Data-Driven Tuning** - Track which alternate tunings are common
5. **Clean Output** - Roman numerals are properly formatted

---

## Next Steps

1. Run full pipeline on larger dataset
2. Review `chords_alternate_tuning.txt` after processing
3. If DADGAD/Drop D are common → Add support for them
4. Otherwise → Keep skipping alternate tunings

---

## Breaking Changes

None - all changes are backward compatible with existing database schema.

---

## Commit Message

```
feat: Fix chord analysis + add capo/tuning support

- Fixed minor key transposition (Em → Am, not Em → C)
- Fixed Roman numerals (vi not vim)
- Added capo transposition for accurate chord analysis
- Added alternate tuning detection and logging
- Fixed metadata handling (partial = OK, no lyrics = FAIL)
- All chord analysis now matches actual musical content
```

