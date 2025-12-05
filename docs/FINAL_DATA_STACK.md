# Final Data Stack - LyricBox Metadata Sources

**Date:** December 5, 2024  
**Status:** Research Complete - Ready to Build

---

## 🎯 Required Metadata

| Field | Source | Status |
|-------|--------|--------|
| **Track Name** | CSV | ✅ Already have |
| **Artist Name** | CSV | ✅ Already have |
| **Peak Position** | CSV | ✅ Already have |
| **Year** | CSV (`first_chart_date`) | ✅ Already have |
| **Genres** | Musixmatch FREE | ✅ Tested |
| **BPM** | GetSongBPM API FREE | 🔄 Need to test |
| **Musical Key** | Ultimate Guitar scraping | ✅ Working |
| **Chords** | Ultimate Guitar scraping | ✅ Working |
| **Lyrics** | Genius scraping | ✅ Working |

---

## 📊 Data Source Details

### 1. **Billboard CSV** (Already Have)
**File:** `backend/billboard_2025_clean.csv`

**Fields:**
- `title` → Track Name
- `artist` → Artist Name
- `peak_position` → Chart Peak
- `first_chart_date` → Extract year (e.g., "2025-01-04" → 2025)

**Why:** More accurate than album release dates - represents when song charted/became popular

---

### 2. **Musixmatch API** (FREE Tier)
**Cost:** FREE  
**Rate Limit:** Unknown (but generous)  
**Status:** ✅ Tested and Working

**What We Get:**
- ✅ **Genres** - High quality, track-specific (e.g., Pop, R&B/Soul, Dance, Disco, Funk)
- ❌ BPM - Not available (even on paid plans)
- ❌ Musical Key - Not available
- ❌ Moods - Requires $119/month Scale plan (403 Forbidden)
- ❌ Release Date - Not in API response

**Implementation:** Already built in `backend/musixmatch/get_track_data.py`

**Test Results:** `backend/musixmatch/musixmatch_complete_test_20251205_121045.txt`

---

### 3. **GetSongBPM API** (FREE Tier)
**Cost:** FREE  
**Requirements:** API key + backlink to getsongkey.com  
**Status:** 🔄 Need to test

**What We Get:**
- ✅ **BPM** (Tempo)
- ✅ **Musical Key** (backup if UG chords not found)

**Why:** Only free API that provides BPM after Spotify restricted access in Dec 2024

**Next Step:** Research and test API endpoints

---

### 4. **Ultimate Guitar** (Scraping - Already Working)
**Cost:** FREE (scraping)  
**Status:** ✅ Tested and Working

**What We Get:**
- ✅ **Chords** - 6 versions per section (original, simplified, transposed C, transposed simplified, Roman, Roman simplified)
- ✅ **Tonality/Musical Key** - Extracted from chord pages
- ✅ **Sections** - Intro, Verse, Chorus, Bridge, etc.

**Implementation:** `backend/ug_scraper/`

**Key Decision:** Use UG tonality as **primary source** for musical key when chords are found. Only use GetSongBPM key as fallback when no chords exist.

---

### 5. **Genius** (Scraping - Already Working)
**Cost:** FREE (scraping)  
**Status:** ✅ Tested and Working

**What We Get:**
- ✅ **Lyrics** - Full lyrics text
- ✅ **Section Labels** - [Verse 1], [Chorus], [Bridge], etc.

**Implementation:** `backend/genius_scrape/`

**Why:** Only source with properly labeled lyric sections

---

## ❌ Sources We Tested But Won't Use

### Spotify API
**Tested:** December 5, 2024  
**Result:** ❌ Not viable

**Issues:**
- Audio Features endpoint (BPM, key) returns **403 Forbidden**
- New apps require **250,000+ monthly active users** for Extended Quota Mode
- December 2024 policy change blocked access to audio analysis features

**What worked:**
- ✅ Release dates (but we're using Billboard chart date instead)
- ✅ Search (but not needed)

**Test Results:** `backend/spotify/spotify_complete_test_20251205_121950.txt`

---

### MusicBrainz API
**Tested:** December 5, 2024  
**Result:** ❌ SSL certificate error on Mac

**What it would provide:**
- ⚠️ Genres (community tags, variable quality)
- ✅ Release dates
- ❌ BPM - Not available
- ❌ Key - Not available

**Decision:** Musixmatch genres are better quality

---

## 🔄 Data Enrichment Pipeline Flow

```
1. Load songs from CSV
   → Track, Artist, Peak Position, Year (from first_chart_date)

2. Musixmatch API (FREE)
   → Fetch genres

3. GetSongBPM API (FREE) 
   → Fetch BPM
   → Fetch Key (as backup)

4. Genius Scraping
   → Fetch lyrics with sections

5. Ultimate Guitar Scraping
   → Fetch chords (6 versions per section)
   → Extract tonality → OVERWRITE key from GetSongBPM if found

6. Save to Supabase
   → songs table: track, artist, peak, year, genres, bpm, key
   → song_lyrics table: sections with lyrics
   → song_chords table: sections with 6 chord versions
```

---

## 💾 Database Schema

### `songs` (Master Table)
```sql
- song_id (UUID, primary key)
- track_name (TEXT)
- artist_name (TEXT)
- peak_position (INTEGER) -- from CSV
- year (INTEGER) -- from first_chart_date
- genres (TEXT[]) -- from Musixmatch
- bpm (INTEGER) -- from GetSongBPM
- musical_key (TEXT) -- from UG (primary) or GetSongBPM (backup)
- metadata_source (TEXT) -- track sources
- created_at (TIMESTAMP)
```

### `song_lyrics` (Genius Data)
```sql
- id (UUID)
- song_id (UUID, foreign key)
- section_name (TEXT) -- Verse 1, Chorus, etc.
- lyrics_text (TEXT)
- lyrics_source (TEXT) -- 'genius'
- created_at (TIMESTAMP)
```

### `song_chords` (Ultimate Guitar Data)
```sql
- id (UUID)
- song_id (UUID, foreign key)
- section_name (TEXT)
- tonality (TEXT)
- chords_original (TEXT[])
- chords_original_simplified (TEXT[])
- chords_transposed_c (TEXT[])
- chords_transposed_c_simplified (TEXT[])
- chords_roman (TEXT[])
- chords_roman_simplified (TEXT[])
- created_at (TIMESTAMP)
```

---

## 📝 Next Steps

1. ✅ Cancel Musixmatch Scale plan ($119/month) - Not providing value
2. 🔄 Research GetSongBPM API - Test endpoints and rate limits
3. 🔄 Build GetSongBPM integration
4. 🔄 Update data enrichment pipeline to use new stack
5. 🔄 Test full pipeline with sample songs

---

## 💰 Cost Summary

| Service | Cost | What We Get |
|---------|------|-------------|
| **Musixmatch** | FREE | Genres |
| **GetSongBPM** | FREE* | BPM, Key (backup) |
| **Ultimate Guitar** | FREE | Chords, Key (primary) |
| **Genius** | FREE | Lyrics with sections |
| **Total** | FREE* | Everything we need |

*GetSongBPM requires backlink to their website

**Savings:** $119.50/month (cancelled Musixmatch Scale plan)

---

## 🎉 Key Decisions Made

1. ✅ Use **Billboard chart date** (year) instead of album release dates
2. ✅ Use **Musixmatch FREE** for genres only
3. ✅ Use **GetSongBPM** for BPM (Spotify no longer viable)
4. ✅ Use **Ultimate Guitar tonality** as PRIMARY key source
5. ✅ Use **GetSongBPM key** only as BACKUP when no chords found
6. ✅ Skip moods entirely (not critical, would cost $119/month)
7. ✅ Keep Genius for lyrics (better section labels than Musixmatch)

---

## 📚 Test Files Reference

- Musixmatch: `backend/musixmatch/musixmatch_complete_test_20251205_121045.txt`
- Spotify: `backend/spotify/spotify_complete_test_20251205_121950.txt`
- Data Sources Comparison: `docs/DATA_SOURCES.md`

