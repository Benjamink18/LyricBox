# LyricBox Database Schema V2 - Normalized Structure

**Version:** 2.0  
**Status:** Documentation Only - To Be Implemented  
**Date:** December 5, 2024

---

## 🎯 Overview

This document defines the **fully normalized** database schema for LyricBox, incorporating:
- Separate `artists` and `albums` tables (no more duplication)
- Complete GetSongBPM data integration (all 10 fields)
- Clear separation: **artist genres** (GetSongBPM) vs **song genres** (Musixmatch)
- Foreign key relationships for data integrity

**Key Change:** The `songs` table no longer stores `artist_name` or `album_title` directly. Instead, it references `artist_id` and `album_id` from the new normalized tables.

---

## 📊 Table Structure

### Table Relationships

```
artists (1) ──────< songs (many)
   │
   │
   └──────< albums (many)
              │
              └──────< songs (many)

songs (1) ──────< song_lyrics (many)
          ──────< song_chords (many)
          ──────< song_rhyme_analysis (many)
          ──────< song_concepts (1)
          ──────< song_youtube_data (1)
```

---

## 1️⃣ Artists Table (NEW)

**Purpose:** One unique record per artist, no duplicates

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| `artist_id` | BIGSERIAL PK | Auto | Unique artist identifier |
| `artist_name` | TEXT UNIQUE | CSV | Artist name (unique) |
| `artist_genres` | TEXT[] | GetSongBPM | Array of artist-level genres |
| `artist_country` | VARCHAR(5) | GetSongBPM | Country code (US, GB, CA) |
| `getsongbpm_artist_id` | VARCHAR(50) | GetSongBPM | GetSongBPM's internal ID |
| `musicbrainz_id` | UUID | GetSongBPM | MusicBrainz database ID |
| `getsongbpm_uri` | TEXT | GetSongBPM | Artist page URL |
| `created_at` | TIMESTAMP | Auto | Record creation timestamp |

**Example Record:**
```json
{
  "artist_id": 1,
  "artist_name": "Michael Jackson",
  "artist_genres": ["funk", "pop", "rock", "soul"],
  "artist_country": "US",
  "getsongbpm_artist_id": "GQ3",
  "musicbrainz_id": "f27ec8db-af05-4f36-916e-3d57f91ecf5e",
  "getsongbpm_uri": "https://getsongbpm.com/artist/michael-jackson/GQ3"
}
```

**Indexes:**
- `idx_artists_name` on `artist_name`
- `idx_artists_country` on `artist_country`

---

## 2️⃣ Albums Table (NEW)

**Purpose:** Album information linked to artists  
**Uniqueness:** `UNIQUE(album_title, artist_id)` - Same album by different artists = different records

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| `album_id` | BIGSERIAL PK | Auto | Unique album identifier |
| `album_title` | TEXT | GetSongBPM | Album name |
| `album_year` | VARCHAR(10) | GetSongBPM or CSV | Release year |
| `artist_id` | BIGINT FK | → artists | Foreign key to artists table |
| `getsongbpm_album_uri` | TEXT | GetSongBPM | Album page URL |
| `created_at` | TIMESTAMP | Auto | Record creation timestamp |

**Example Record:**
```json
{
  "album_id": 5,
  "album_title": "Thriller",
  "album_year": "1982",
  "artist_id": 1,
  "getsongbpm_album_uri": "https://getsongbpm.com/album/thriller/xgR9"
}
```

**Indexes:**
- `idx_albums_artist_id` on `artist_id`
- `idx_albums_year` on `album_year`

---

## 3️⃣ Songs Table (UPDATED - Normalized)

**Purpose:** Main song catalog with foreign keys to artists and albums  
**Key Change:** No more `artist_name` or `album_title` columns!

### Billboard Data (from CSV)

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| `song_id` | BIGSERIAL PK | Auto | Unique song identifier |
| `track_name` | TEXT | CSV | Song title |
| `artist_id` | BIGINT FK | → artists | Foreign key to artists table |
| `album_id` | BIGINT FK | → albums | Foreign key to albums table (nullable) |
| `peak_position` | INTEGER | CSV | Highest Billboard chart position |
| `first_chart_date` | DATE | CSV | First date on Billboard charts |
| `chart_year` | INTEGER | CSV | Year extracted from first_chart_date |

### Musixmatch Metadata

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| `song_genres` | TEXT[] | Musixmatch | **Song-level** genres (different from artist_genres!) |
| `metadata_source` | TEXT | Musixmatch | 'musixmatch' or 'musicbrainz' |

### GetSongBPM Musical Characteristics

| Column | Type | Source | Description | Example |
|--------|------|--------|-------------|---------|
| `bpm` | INTEGER | GetSongBPM | Beats per minute (tempo) | 116 |
| `time_signature` | VARCHAR(10) | GetSongBPM | Time signature | "4/4", "3/4" |
| `musical_key` | VARCHAR(10) | GetSongBPM | Musical key (backup - UG primary) | "F♯m", "C" |
| `camelot_key` | VARCHAR(10) | GetSongBPM | Camelot notation (DJ mixing) | "4m", "8d" |
| `danceability` | INTEGER | GetSongBPM | How danceable (0-100) | 92 |
| `acousticness` | INTEGER | GetSongBPM | Acoustic vs electronic (0-100) | 3 |

**Example Record:**
```json
{
  "song_id": 42,
  "track_name": "Billie Jean",
  "artist_id": 1,
  "album_id": 5,
  "peak_position": 1,
  "chart_year": 1983,
  "song_genres": ["pop", "dance", "funk"],
  "metadata_source": "musixmatch",
  "bpm": 116,
  "time_signature": "4/4",
  "musical_key": "F♯m",
  "camelot_key": "4m",
  "danceability": 92,
  "acousticness": 3
}
```

**Indexes:**
- `idx_songs_artist_id`, `idx_songs_album_id`, `idx_songs_track_name`
- `idx_songs_bpm`, `idx_songs_danceability`, `idx_songs_acousticness`

**Constraint:**
- `UNIQUE(track_name, artist_id)` - No duplicate songs per artist

---

## 4️⃣ Existing Tables (Unchanged)

### song_lyrics
- Links via `song_id`
- One row per section per song
- Columns: `lyrics_id`, `song_id`, `section_name`, `lyrics_text`, `lyrics_source`

### song_chords
- Links via `song_id`
- One row per section per song with 6 chord versions
- Columns: `chord_id`, `song_id`, `section_name`, `tonality`, `chords_original`, etc.

### song_rhyme_analysis
- Links via `song_id`
- AI-generated rhyme schemes by Claude

### song_concepts
- Links via `song_id`
- AI-generated thematic analysis

### song_youtube_data
- Links via `song_id`
- YouTube transcripts and comments

---

## 🔍 Important Distinctions

### Artist Genres vs Song Genres

**Artist Genres** (from GetSongBPM):
- Stored in: `artists.artist_genres`
- Source: GetSongBPM `artist.genres`
- Describes the artist's overall style
- Example: Michael Jackson → `["funk", "pop", "rock", "soul"]`

**Song Genres** (from Musixmatch):
- Stored in: `songs.song_genres`
- Source: Musixmatch API
- Describes the specific song's genre
- Example: "Billie Jean" → `["pop", "dance", "funk"]`

**Why separate?**
- Artist genres apply to ALL their songs
- Song genres are specific to each track
- Enables better filtering: "Find funk artists" vs "Find funk songs"

---

## 📝 Views for Easy Querying

### songs_complete
Since `songs` table is fully normalized, use this view when you need artist/album names:

```sql
CREATE VIEW songs_complete AS
SELECT 
  s.song_id,
  s.track_name,
  a.artist_name,           -- ← From artists table
  a.artist_genres,
  a.artist_country,
  al.album_title,          -- ← From albums table
  al.album_year,
  s.peak_position,
  s.chart_year,
  s.song_genres,
  s.bpm,
  s.danceability,
  s.acousticness,
  -- ... all other song fields
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
LEFT JOIN albums al ON s.album_id = al.album_id;
```

**Usage:**
```sql
-- Instead of: SELECT * FROM songs WHERE artist_name = 'Michael Jackson';
-- Use:
SELECT * FROM songs_complete WHERE artist_name = 'Michael Jackson';
```

---

## 🎯 Example Queries

### Find danceable acoustic songs
```sql
SELECT 
  a.artist_name, 
  s.track_name, 
  s.danceability, 
  s.acousticness
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE s.danceability > 70 
  AND s.acousticness > 60;
```

### Find all songs by an artist
```sql
SELECT s.track_name, s.bpm, s.danceability
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE a.artist_name = 'D''Angelo';
```

### Find songs by artist genre
```sql
SELECT a.artist_name, s.track_name, a.artist_genres
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE 'funk' = ANY(a.artist_genres);
```

### Find all albums by an artist
```sql
SELECT 
  al.album_title, 
  al.album_year, 
  COUNT(s.song_id) as track_count
FROM albums al
JOIN artists a ON al.artist_id = a.artist_id
LEFT JOIN songs s ON s.album_id = al.album_id
WHERE a.artist_name = 'Michael Jackson'
GROUP BY al.album_id, al.album_title, al.album_year;
```

### Find songs with compatible Camelot keys (DJ mixing)
```sql
SELECT 
  s1.track_name as song1, 
  s2.track_name as song2, 
  s1.camelot_key
FROM songs s1
JOIN songs s2 ON s1.camelot_key = s2.camelot_key
WHERE s1.song_id < s2.song_id
LIMIT 10;
```

### Filter by danceability and acousticness
```sql
-- Electronic bangers (high dance, low acoustic)
SELECT a.artist_name, s.track_name, s.danceability, s.acousticness
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE s.danceability > 70 AND s.acousticness < 20;

-- Acoustic ballads (low dance, high acoustic)
SELECT a.artist_name, s.track_name, s.danceability, s.acousticness
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE s.danceability < 50 AND s.acousticness > 60;
```

---

## 📊 Data Sources Summary

| Data Field | Source | API/Method | Cost |
|------------|--------|------------|------|
| **CSV Data** | Billboard | Manual export | Free |
| track_name, artist_name, peak_position, first_chart_date | | | |
| **Artist Genres** | GetSongBPM | `artist.genres` | Free |
| **Artist Country** | GetSongBPM | `artist.from` | Free |
| **Album Data** | GetSongBPM | `album` object | Free |
| **Song Genres** | Musixmatch | Free tier API | Free |
| **BPM** | GetSongBPM | `tempo` | Free |
| **Time Signature** | GetSongBPM | `time_sig` | Free |
| **Musical Key** | GetSongBPM (backup) | `key_of` | Free |
| **Camelot Key** | GetSongBPM | `open_key` | Free |
| **Danceability** | GetSongBPM | `danceability` | Free |
| **Acousticness** | GetSongBPM | `acousticness` | Free |
| **Lyrics** | Genius.com | Web scraping | Free |
| **Chords** | Ultimate Guitar | Web scraping | Free |
| **Musical Key (primary)** | Ultimate Guitar | From chord tonality | Free |
| **Rhyme Analysis** | Claude AI | Anthropic API | Paid (~$0.003/song) |
| **Concept Analysis** | Claude AI | Anthropic API | Paid (~$0.003/song) |

**Total Cost:** ~$0.006 per song for AI analysis only

---

## 🚀 Migration Plan (When Rebuilding)

### Step 1: Clear Existing Data
```sql
TRUNCATE TABLE songs CASCADE;
TRUNCATE TABLE artists CASCADE;
TRUNCATE TABLE albums CASCADE;
```

### Step 2: Create Schema
```bash
psql -h YOUR_HOST -U YOUR_USER -d YOUR_DB -f database/schema_v2_normalized.sql
```

### Step 3: Run Enrichment Pipeline

1. **Read CSV** → Extract unique artists
2. **Create artists records** → Get auto-generated `artist_id`
3. **Fetch GetSongBPM data** → Populate `artist_genres`, `artist_country`, etc.
4. **Create albums records** → Get auto-generated `album_id`
5. **Create songs records** → Link via `artist_id` and `album_id` foreign keys
6. **Save all GetSongBPM fields** → `bpm`, `danceability`, `acousticness`, etc.
7. **Fetch lyrics, chords, etc.** → Link via `song_id`

### Step 4: Verify
```sql
-- Check all songs have valid artist_id
SELECT COUNT(*) FROM songs WHERE artist_id IS NULL;  -- Should be 0

-- Check artist distribution
SELECT artist_name, COUNT(s.song_id) as song_count
FROM artists a
LEFT JOIN songs s ON a.artist_id = s.artist_id
GROUP BY a.artist_id, artist_name
ORDER BY song_count DESC
LIMIT 10;
```

---

## ✅ Benefits of Normalized Structure

1. **No Data Duplication**
   - Artist info stored once, not repeated for every song
   - Album info stored once per artist

2. **Data Integrity**
   - Foreign keys enforce valid relationships
   - Can't have orphaned songs without an artist

3. **Easy Updates**
   - Update artist genres once → applies to all their songs
   - Update album year once → applies to all tracks

4. **Better Queries**
   - "All songs by artists from US" → simple WHERE clause
   - "Artists with most albums" → easy GROUP BY

5. **Future-Proof**
   - Easy to add artist-level features (bio, photo, etc.)
   - Easy to add album-level features (cover art, label, etc.)

---

## 📁 Files

- **SQL Schema:** [`database/schema_v2_normalized.sql`](../database/schema_v2_normalized.sql)
- **This Document:** [`docs/DATABASE_SCHEMA_V2.md`](DATABASE_SCHEMA_V2.md)
- **GetSongBPM Field Analysis:** [`docs/GETSONGBPM_FIELDS_SUMMARY.md`](GETSONGBPM_FIELDS_SUMMARY.md)
- **Complete Field Extraction:** [`docs/GETSONGBPM_COMPLETE_FIELDS.txt`](GETSONGBPM_COMPLETE_FIELDS.txt)

---

**Status:** Ready to implement when rebuilding database from scratch 🚀

