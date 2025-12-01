# LyricBox Database - Technical Handover Document

**Last Updated:** November 28, 2025  
**Database Status:** Production-ready with 500 songs (expandable to 3,258)  
**Purpose:** Complete reference for analyzing and extending the LyricBox database

---

## Table of Contents
1. [Database Overview](#database-overview)
2. [Database Schema](#database-schema)
3. [Data Import Pipeline](#data-import-pipeline)
4. [Genre System](#genre-system)
5. [Lyrics Sources](#lyrics-sources)
6. [File Structure](#file-structure)
7. [How to Run Imports](#how-to-run-imports)
8. [Extending for Analysis](#extending-for-analysis)
9. [Important: DO NOT BREAK](#important-do-not-break)

---

## Database Overview

### Current Status
- **Platform:** Supabase (PostgreSQL)
- **Songs in Database:** 500 (top Billboard hits)
- **Available for Import:** 3,258 songs (Billboard Hot 100, Nov 2020 - Nov 2025)
- **Genres:** 15 main categories + detailed Spotify subgenres
- **Lyrics Quality:** Multi-source (LrcLib → Lyrics.ovh → Genius fallback)

### Key Features
✅ Clean, normalized lyrics (no timestamps, no metadata junk)  
✅ Billboard chart metadata (peak position, weeks on chart, release year)  
✅ Dual genre system (broad categories + specific subgenres)  
✅ Genre autocomplete list for frontend  
✅ Row-level security enabled  
✅ Full-text search on lyrics  

---

## Database Schema

### Core Tables

#### `songs` - Main song metadata
```sql
CREATE TABLE songs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  genius_id INTEGER UNIQUE,
  year INTEGER,                    -- Release year
  billboard_rank INTEGER,          -- Peak position on Billboard Hot 100
  genre TEXT,                      -- Main genre category
  lyrics_raw TEXT,                 -- Full lyrics text
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Important Fields:**
- `billboard_rank`: 1-100 (lower = more popular)
- `genre`: One of 15 main categories (see Genre System section)
- `lyrics_raw`: Clean lyrics without section markers

**Indexes:**
- `idx_songs_year` - Filter by year
- `idx_songs_genre` - Filter by genre
- `idx_songs_artist` - Search by artist
- `idx_songs_rank` - Sort by popularity

#### `lyrics_lines` - Individual lyrics lines for rhyme detection
```sql
CREATE TABLE lyrics_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
  line_number INTEGER NOT NULL,
  line_text TEXT NOT NULL,           -- Original line
  line_text_clean TEXT NOT NULL,     -- No punctuation (for matching)
  last_word TEXT,                    -- Last word of line (for rhyme detection)
  last_word_phonetic TEXT,           -- Phonetic representation (future)
  context_before TEXT,               -- Previous line
  context_after TEXT,                -- Next line
  context_hash TEXT,                 -- Deduplication hash
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Purpose:** Enables rhyme detection and contextual lyric search

**Indexes:**
- `idx_lyrics_last_word` - Rhyme matching
- `idx_lyrics_song_id` - Lookup by song
- `idx_lyrics_line_text` - Full-text search (GIN index)
- `idx_lyrics_context_hash` - Prevent duplicates

#### Additional Tables (Ready for Extension)
- `line_rhyme_words` - Internal rhyme detection (words within lines)
- `line_word_pairs` - Mosaic rhyme detection (multi-word rhymes)
- `rhyme_pairs` - Pre-computed rhyme dictionary
- `song_concepts` - AI-analyzed themes (future feature)

See `/database/schema.sql` for complete schema.

---

## Data Import Pipeline

### Pipeline Architecture

```
Billboard Charts (Web) 
    ↓
1. fetch_billboard_charts.py
    ↓
master_songs_2020_2025_billboard.csv (3,258 songs)
    ↓
2. fetch_genres.py (Spotify API)
    ↓
master_songs_2020_2025_billboard_with_genres.csv
    ↓
3. consolidate_genres.py
    ↓
master_songs_2020_2025_billboard_consolidated.csv
    ├→ genre_autocomplete.json (frontend)
    ↓
4. import_lyrics_batch.py (Multi-source)
    ↓
master_songs_2020_2025_with_lyrics.csv
    ↓
5. import_to_supabase.py
    ↓
Supabase Database
```

### Pipeline Scripts

#### 1. `fetch_billboard_charts.py`
**Purpose:** Scrapes Billboard Hot 100 charts for date range  
**Input:** Start date, end date  
**Output:** CSV with title, artist, peak_position, weeks_on_chart  
**Features:**
- Deduplicates songs automatically
- Filters out live/remix/acoustic versions
- Tracks peak position and chart longevity

#### 2. `fetch_genres.py`
**Purpose:** Enriches songs with Spotify genre data  
**Requirements:** Spotify API credentials (see `.env`)  
**Output:** Adds `spotify_genres` and `spotify_id` columns  
**Rate Limit:** ~3,000 songs = 10-15 minutes  
**Success Rate:** ~70-80% (some songs not on Spotify)

#### 3. `consolidate_genres.py`
**Purpose:** Maps detailed Spotify genres → 15 main categories  
**Output:** 
- Adds `main_genre` column
- Creates `genre_autocomplete.json` for UI
**Logic:** Keyword-based mapping with priority system (see Genre System)

#### 4. `import_lyrics_batch.py`
**Purpose:** Fetches clean lyrics using multi-source approach  
**Sources (in order):**
1. LrcLib (primary) - Clean, no metadata
2. Lyrics.ovh (secondary) - Backup
3. Genius (fallback) - Web scraping with cleanup

**Features:**
- Progress saved every 50 songs
- Removes LRC timestamps `[00:00.00]`
- Removes BOM characters
- Cleans Genius junk ("You might also like", etc.)
- Counts lyrics lines

**Can import:**
- Top N songs: `python import_lyrics_batch.py 500`
- All songs: `python import_lyrics_batch.py`

#### 5. `import_to_supabase.py`
**Purpose:** Uploads songs and lyrics to database  
**Features:**
- Checks for duplicates (title + artist)
- Splits lyrics into individual lines
- Generates context hashes
- Extracts last words for rhyme detection

---

## Genre System

### The Two-Tier Approach

**Why two tiers?**
- **Main genres:** Simple filtering for users (15 categories)
- **Spotify genres:** Detailed search for power users (166+ subgenres)

### Main Genre Categories (15)

1. **Pop** - Any genre containing "pop" (electropop, indie pop, dance pop, etc.)
2. **Hip Hop/Rap** - rap, hip hop, trap, drill, grime, conscious hip hop
3. **Country** - country, americana, bluegrass, outlaw country
4. **R&B** - r&b, contemporary r&b, alternative r&b, neo soul
5. **Latin** - reggaeton, latin pop, latin trap, bachata, salsa, corrido
6. **Rock** - rock, alternative rock, punk, grunge, emo
7. **Electronic/Dance** - edm, house, techno, dubstep, drum and bass
8. **Indie/Alternative** - indie, alternative, shoegaze, dream pop
9. **Metal** - metal, metalcore, death metal, heavy metal
10. **Soul/Funk** - soul, funk, motown, disco
11. **Folk/Acoustic** - folk, acoustic, singer-songwriter
12. **Reggae/Dancehall** - reggae, dancehall, ska, dub
13. **Jazz** - jazz, bebop, smooth jazz, swing
14. **Blues** - blues, delta blues, chicago blues
15. **Classical** - classical, orchestral, opera
16. **Other** - Anything unmatched or no Spotify data

### Genre Mapping Rules

**Critical Rule:** If genre contains "pop" → Pop category
- "dance pop" → Pop (NOT Dance)
- "indie pop" → Pop (NOT Indie)
- "pop rap" → Pop (NOT Hip Hop)

**Priority:** Checked top-to-bottom in `consolidate_genres.py`

**Spotify Genres Preserved:** Original detailed genres stored in CSV for keyword search

### Genre Files

- **`genre_autocomplete.json`** - For frontend autocomplete
  ```json
  {
    "genres": ["country", "rap", "reggaeton", "trap", ...],
    "genre_counts": {"country": 341, "rap": 289, ...}
  }
  ```

---

## Lyrics Sources

### Multi-Source Strategy

**Order matters!** Each source is tried in sequence until success.

#### 1. LrcLib (Primary) ✅
- **URL:** `https://lrclib.net/api/get`
- **Quality:** Excellent - clean plain text
- **Coverage:** Good for popular songs
- **Speed:** Fast
- **Auth:** None required
- **Pros:** No junk, no timestamps in plain lyrics
- **Cons:** Smaller catalog than others

#### 2. Lyrics.ovh (Secondary) ✅
- **URL:** `https://api.lyrics.ovh/v1/{artist}/{title}`
- **Quality:** Good - mostly clean
- **Coverage:** Moderate
- **Speed:** Fast (when it works)
- **Auth:** None required
- **Pros:** Simple API, no auth
- **Cons:** Often times out (timeout set to 10s)

#### 3. Genius (Fallback) ✅
- **Method:** API search + web scraping
- **Quality:** Good after cleanup
- **Coverage:** Excellent - largest catalog
- **Speed:** Slower (web scraping)
- **Auth:** Requires `GENIUS_ACCESS_TOKEN` in `.env`
- **Pros:** Almost always has the song
- **Cons:** Returns annotations/metadata that needs cleaning

### Lyrics Cleaning Process

All sources go through cleaning in `lyrics_fetcher.py`:

```python
# Remove BOM characters
lyrics = lyrics.lstrip('\ufeff')

# Remove LRC timestamp lines [00:00.00]
if re.match(r'^\[[\d:\.]+\]', line):
    continue

# Remove Genius junk
junk_phrases = [
    "You might also like",
    "Embed", "See Live", "Get tickets",
    "[Produced by", "[Written by"
]

# Remove consecutive blank lines
# Keep section markers [Verse 1], [Chorus]
```

### Success Rates (Top 500 songs)

Based on testing:
- LrcLib: ~85% success
- Lyrics.ovh: ~10% success (many timeouts)
- Genius: ~5% fallback
- **Overall: ~100% success rate**

---

## File Structure

```
LyricBox/
├── backend/
│   ├── .env                           # API credentials (NEVER commit!)
│   ├── config.py                      # Loads environment variables
│   ├── lyrics_fetcher.py              # Multi-source lyrics fetcher
│   ├── fetch_billboard_charts.py      # Step 1: Chart data
│   ├── fetch_genres.py                # Step 2: Spotify genres
│   ├── consolidate_genres.py          # Step 3: Genre mapping
│   ├── import_lyrics_batch.py         # Step 4: Fetch lyrics
│   ├── import_to_supabase.py          # Step 5: Upload to DB
│   ├── run_import_pipeline.py         # Master script (all steps)
│   ├── requirements.txt               # Python dependencies
│   ├── venv/                          # Virtual environment
│   └── Data Files:
│       ├── master_songs_2020_2025_billboard.csv
│       ├── master_songs_2020_2025_billboard_with_genres.csv
│       ├── master_songs_2020_2025_billboard_consolidated.csv
│       ├── master_songs_2020_2025_with_lyrics.csv
│       ├── genre_autocomplete.json    # For frontend
│       └── import_stats.json          # Import results
│
├── database/
│   ├── schema.sql                     # Complete DB schema
│   ├── add_concepts_table.sql         # Song concepts extension
│   └── add_line_rhyme_words.sql       # Rhyme detection extension
│
├── frontend/
│   └── src/
│       └── lib/
│           └── supabase.ts            # DB client & queries
│
└── Documentation:
    ├── README.md                      # Project overview
    ├── HANDOVER_DATABASE.md           # This file
    ├── AI_SETUP.md                    # Setup instructions
    └── NEXT_STEPS.md                  # Feature roadmap
```

---

## How to Run Imports

### Prerequisites

1. **Environment Variables** (`.env` file):
```bash
GENIUS_ACCESS_TOKEN=your_genius_token
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
```

2. **Python Environment**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Quick Start (Top 500 Songs)

```bash
cd backend
source venv/bin/activate

# All-in-one (recommended)
python run_import_pipeline.py

# Or step-by-step:
python consolidate_genres.py
python import_lyrics_batch.py 500
python import_to_supabase.py
```

### Full Import (All 3,258 Songs)

```bash
python run_import_pipeline.py --all
# OR
python import_lyrics_batch.py  # No limit = all songs
python import_to_supabase.py
```

### Import More Chart Years

To add additional years (e.g., 2015-2020):

```bash
# Edit fetch_billboard_charts.py dates:
start_date = datetime(2015, 11, 28)
end_date = datetime(2020, 11, 27)

python fetch_billboard_charts.py
# Then run full pipeline on new CSV
```

---

## Extending for Analysis

### Safe Ways to Extend

#### ✅ Add New Analysis Tables

Safe to create new tables that reference existing ones:

```sql
CREATE TABLE song_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
  analysis_type TEXT,
  analysis_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### ✅ Add Columns to Songs Table

Safe to add nullable columns:

```sql
ALTER TABLE songs 
ADD COLUMN sentiment_score FLOAT,
ADD COLUMN complexity_score FLOAT;
```

#### ✅ Create Materialized Views

Safe for performance optimization:

```sql
CREATE MATERIALIZED VIEW popular_songs_by_genre AS
SELECT genre, COUNT(*) as song_count, AVG(billboard_rank) as avg_rank
FROM songs
GROUP BY genre;
```

#### ✅ Add New Indexes

Safe for query optimization:

```sql
CREATE INDEX idx_songs_year_genre ON songs(year, genre);
```

### Analysis Ideas (Safe to Implement)

1. **Rhyme Pattern Analysis**
   - Use `lyrics_lines.last_word` for end rhymes
   - Query `line_rhyme_words` for internal rhymes
   - Count rhyme schemes per song

2. **Lyrical Complexity**
   - Unique word count
   - Average syllables per line
   - Vocabulary diversity

3. **Theme Extraction**
   - Full-text search on `lyrics_raw`
   - Use `song_concepts` table for AI analysis
   - Topic modeling across genres

4. **Temporal Analysis**
   - Genre popularity over years
   - Lyric trends by decade
   - Billboard performance correlation

5. **Cross-Genre Comparison**
   - Lyric length by genre
   - Rhyme density by genre
   - Topic differences

---

## Important: DO NOT BREAK

### ⚠️ DO NOT Modify These

#### 1. Genre Consolidation Logic
**File:** `backend/consolidate_genres.py`  
**Rule:** "pop" keyword priority

**Why:** Frontend relies on consistent 15 categories. Changing mapping breaks filters.

**If you must change:**
- Update `GENRE_MAPPINGS` dictionary
- Re-run consolidation: `python consolidate_genres.py`
- Regenerate autocomplete: included automatically
- Update frontend genre list

#### 2. Lyrics Fetcher Multi-Source Order
**File:** `backend/lyrics_fetcher.py`  
**Order:** LrcLib → Lyrics.ovh → Genius

**Why:** Optimizes for speed and cleanliness. LrcLib is fastest and cleanest.

**If you must change:**
- Keep multi-source fallback pattern
- Maintain cleaning functions (`_fetch_from_lrclib`, etc.)
- Test thoroughly with 50+ songs

#### 3. Database Foreign Keys
**File:** `/database/schema.sql`  
**Cascade:** `ON DELETE CASCADE` on all references to `songs(id)`

**Why:** Deleting a song should clean up all lyrics_lines automatically.

**If you must change:**
- Understand cascade implications
- Test with dev data first
- Consider orphaned records

#### 4. Import Deduplication
**File:** `backend/import_to_supabase.py`  
**Check:** `title + artist` uniqueness before insert

**Why:** Prevents duplicate songs in database.

**If you must change:**
- Keep duplicate checking
- Consider case sensitivity
- Test with known duplicates

### ⚠️ DO NOT Delete These Files

Critical for re-imports and updates:

- `master_songs_2020_2025_billboard_consolidated.csv` - Master song list
- `genre_autocomplete.json` - Frontend autocomplete
- `lyrics_fetcher.py` - Lyrics source code
- `consolidate_genres.py` - Genre logic
- `/database/schema.sql` - Schema reference

### ✅ Safe to Delete

Temporary/intermediate files:

- `master_songs_2020_2025_billboard.csv` (pre-genre)
- `master_songs_2020_2025_billboard_with_genres.csv` (pre-consolidation)
- `master_songs_2020_2025_with_lyrics.csv` (after DB import)
- `import_stats.json` (regenerated each import)
- `imported_songs_*.txt` (test files)

---

## Environment Variables Reference

### Required for All Operations

```bash
# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key  # NOT anon key!

# Genius (Lyrics Fallback)
GENIUS_ACCESS_TOKEN=your_token_here
```

### Required Only for Genre Fetching

```bash
# Spotify (Genre Data)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Optional (Future Features)

```bash
# Anthropic Claude (AI Analysis)
ANTHROPIC_API_KEY=your_claude_key
```

---

## Common Issues & Solutions

### Issue: Lyrics Import Fails

**Symptoms:** Many songs show "Failed" in import  
**Causes:**
1. Genius API token expired/invalid
2. Network connectivity issues
3. Songs not in any database

**Solutions:**
- Check `.env` has valid `GENIUS_ACCESS_TOKEN`
- Test single song: `python -c "from lyrics_fetcher import LyricsFetcher; f=LyricsFetcher(); print(f.search_song('Hello', 'Adele'))"`
- Check import_stats.json for source breakdown

### Issue: Genre Import Shows Mostly "Other"

**Symptoms:** 50%+ songs categorized as "Other"  
**Causes:**
1. Spotify API credentials missing/invalid
2. Songs not on Spotify (rare/old songs)
3. Artist genre data unavailable

**Solutions:**
- Check `.env` has valid Spotify credentials
- Run genre fetch again: `python fetch_genres.py`
- Accept that some songs won't have genres (it's normal)

### Issue: Duplicate Songs in Database

**Symptoms:** Same song appears multiple times  
**Causes:**
1. Import run multiple times
2. Deduplication check failed
3. Title/artist variations

**Solutions:**
- Clear database: `python import_to_supabase.py --clear`
- Re-import from CSV
- Check for title variations (e.g., "feat." vs "featuring")

### Issue: Supabase Import Fails

**Symptoms:** "Permission denied" or connection errors  
**Causes:**
1. Using anon key instead of service_role key
2. RLS policies blocking insert
3. Network/firewall issues

**Solutions:**
- Verify `SUPABASE_KEY` is service_role (not anon)
- Check Supabase dashboard for RLS policy
- Test connection: `python -c "from supabase import create_client; from config import SUPABASE_URL, SUPABASE_KEY; c=create_client(SUPABASE_URL, SUPABASE_KEY); print(c.table('songs').select('count').execute())"`

---

## Database Statistics

### Current Dataset (Top 500)

- **Songs:** 500
- **Artists:** ~200 unique
- **Years:** 2020-2025
- **Genres:**
  - Hip Hop/Rap: ~100 songs
  - Country: ~50 songs
  - Pop: ~40 songs
  - Latin: ~15 songs
  - R&B: ~15 songs
  - Other: ~280 songs
- **Lyrics Lines:** ~20,000 lines (avg 40 lines/song)

### Full Dataset Available (3,258 Songs)

- **Peak Position Range:** #1 to #100
- **Chart Weeks Range:** 1 to 112 weeks
- **Most Represented Artists:**
  - Taylor Swift: 146 songs
  - Morgan Wallen: 83 songs
  - Drake: 57 songs
  - Rod Wave: 62 songs

---

## Performance Considerations

### Query Optimization

**Fast Queries:**
- Filter by `genre` (indexed)
- Filter by `year` (indexed)
- Sort by `billboard_rank` (indexed)
- Search by `artist` (indexed)

**Slower Queries:**
- Full-text search on `lyrics_raw` (use GIN index on `lyrics_lines`)
- Complex JOIN across all lyrics_lines
- Unindexed WHERE clauses

**Recommendations:**
- Use `lyrics_lines` table for lyric analysis (indexed, structured)
- Use `songs.lyrics_raw` only for display
- Add indexes for your specific queries
- Consider materialized views for heavy analysis

### Import Performance

- **Consolidate genres:** ~1 second (3,258 songs)
- **Fetch genres (Spotify):** ~10-15 minutes (3,258 songs)
- **Import lyrics:** 
  - Top 500: ~30-45 minutes
  - All 3,258: ~2-4 hours
- **Upload to Supabase:** ~10-20 minutes (500 songs)

---

## Future Extensions (Roadmap)

### Planned Features

1. **Phonetic Rhyme Detection**
   - Use CMU Pronouncing Dictionary
   - Populate `last_word_phonetic` in `lyrics_lines`
   - Enable true rhyme matching (not just exact words)

2. **Internal Rhyme Analysis**
   - Populate `line_rhyme_words` table
   - Detect multi-syllable rhymes
   - Mosaic rhyme detection (multi-word)

3. **AI Song Concept Analysis**
   - Use Claude API to analyze themes
   - Populate `song_concepts` table
   - Enable semantic search

4. **Rhyme Scheme Visualization**
   - ABAB, AABB pattern detection
   - Per-song rhyme density
   - Genre comparisons

### How to Add Extensions

1. Create new tables (don't modify existing)
2. Reference `songs(id)` with foreign key
3. Add indexes for your queries
4. Create separate import script
5. Update this document

---

## Contact & Maintenance

### Updating This Document

When making changes to the import pipeline or database schema:

1. Update relevant sections here
2. Update `Last Updated` date at top
3. Add to "Change Log" if major change
4. Commit with descriptive message

### Questions?

Refer to:
- `README.md` - Project overview
- `AI_SETUP.md` - Initial setup
- `NEXT_STEPS.md` - Feature roadmap
- Code comments in `backend/*.py`

---

## Change Log

### 2025-11-28 - Initial Handover
- Documented complete import pipeline
- Explained genre system and multi-source lyrics
- Added extension guidelines
- Listed DO NOT BREAK items

---

**End of Handover Document**



