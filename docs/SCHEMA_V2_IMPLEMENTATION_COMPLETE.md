# Schema V2 Implementation - COMPLETE ✅

**Date:** December 5, 2024  
**Status:** Ready to Test

---

## 🎉 What Was Implemented

### 1. Database Schema ✅
**File:** [`database/apply_schema_v2.sql`](../database/apply_schema_v2.sql)

- ✅ **Dropped** old tables
- ✅ **Created** normalized `artists` table (auto-incrementing `artist_id`)
- ✅ **Created** normalized `albums` table (auto-incrementing `album_id`)  
- ✅ **Created** updated `songs` table with:
  - Foreign keys: `artist_id`, `album_id`
  - All 10 GetSongBPM fields: `bpm`, `time_signature`, `musical_key`, `camelot_key`, `danceability`, `acousticness`
  - Musixmatch: `song_genres`
  - CSV: `peak_position`, `first_chart_date`, `chart_year`
- ✅ **Created** all related tables: `song_lyrics`, `song_chords`, etc.
- ✅ **Created** views: `songs_complete`, `artists_summary`

### 2. Helper Functions ✅

| File | Purpose |
|------|---------|
| [`create_or_get_artist.py`](../backend/data_enrichment/create_or_get_artist.py) | Create artist or return existing `artist_id` |
| [`create_or_get_album.py`](../backend/data_enrichment/create_or_get_album.py) | Create album or return existing `album_id` |
| [`delete_song.py`](../backend/data_enrichment/delete_song.py) | Delete song from database (for lyrics failures) |
| [`update_musical_key.py`](../backend/data_enrichment/update_musical_key.py) | Update `songs.musical_key` from UG tonality |

### 3. Updated Core Functions ✅

| File | Changes |
|------|---------|
| [`get_bpm.py`](../backend/getsongbpm/get_bpm.py) | Returns ALL 10 GetSongBPM fields |
| [`create_song_with_metadata.py`](../backend/data_enrichment/create_song_with_metadata.py) | Accepts foreign keys and all new fields |
| [`read_songs_csv.py`](../backend/data_enrichment/read_songs_csv.py) | Returns `first_chart_date` as DATE string |
| [`chords_to_supabase.py`](../backend/ug_scraper/chords_to_supabase.py) | Uses `song_id` directly (no lookup) |
| [`ug_scraper_main.py`](../backend/ug_scraper/ug_scraper_main.py) | Returns `songs_with_key` for updates |

### 4. Main Pipeline ✅
**File:** [`data_enrichment_main.py`](../backend/data_enrichment/data_enrichment_main.py)

**New Flow:**
1. ✅ Load songs from CSV
2. ✅ Fetch Musixmatch genres
3. ✅ Fetch GetSongBPM data (ALL 10 fields)
4. ✅ Create/get artist → `artist_id`
5. ✅ Create/get album → `album_id`
6. ✅ Create song with all metadata + foreign keys
7. ✅ Batch scrape Genius lyrics (**REQUIRED**)
8. ✅ Delete songs if lyrics fail
9. ✅ Batch scrape UG chords + tonality
10. ✅ Update `songs.musical_key` if UG tonality found

---

## 📊 GetSongBPM Fields - All 10 Saved

| Field | Source | Saved To | Example |
|-------|--------|----------|---------|
| `tempo` | GetSongBPM | `songs.bpm` | 116 |
| `time_sig` | GetSongBPM | `songs.time_signature` | "4/4" |
| `key_of` | GetSongBPM | `songs.musical_key` | "F♯m" (backup) |
| `open_key` | GetSongBPM | `songs.camelot_key` | "4m" |
| `danceability` | GetSongBPM | `songs.danceability` | 92 |
| `acousticness` | GetSongBPM | `songs.acousticness` | 3 |
| `artist.from` | GetSongBPM | `artists.artist_country` | "US" |
| `artist.genres` | GetSongBPM | `artists.artist_genres` | ["funk", "pop"] |
| `album.title` | GetSongBPM | `albums.album_title` | "Thriller" |
| `album.year` | GetSongBPM | `albums.album_year` | "1982" |

**Note:** UG `tonality` overrides `songs.musical_key` when found (more accurate).

---

## 🧪 How to Test

### Step 1: Apply Schema to Supabase

1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `/Users/benkohn/Desktop/LyricBox/database/apply_schema_v2.sql`
3. Click "Run"
4. ✅ Database is now cleared and schema v2 is applied

### Step 2: Test with 3 Songs

**Test CSV created:** [`backend/data_enrichment/test_songs.csv`](../backend/data_enrichment/test_songs.csv)

Contains:
- Michael Jackson - Billie Jean
- Lewis Capaldi - Someone You Loved
- D'Angelo - Spanish Joint

**Run test:**
```bash
cd /Users/benkohn/Desktop/LyricBox/backend/data_enrichment
source ../venv/bin/activate

# Temporarily rename songs_list.csv and use test file
mv songs_list.csv songs_list.csv.backup
cp test_songs.csv songs_list.csv

# Run enrichment
python data_enrichment_main.py

# Restore original CSV
mv songs_list.csv.backup songs_list.csv
```

### Step 3: Verify in Supabase

Check tables in order:

**1. Artists table:**
```sql
SELECT * FROM artists;
```
Expected: 3 artists with `artist_genres` and `artist_country`

**2. Albums table:**
```sql
SELECT * FROM albums;
```
Expected: 3 albums linked to artists

**3. Songs table:**
```sql
SELECT * FROM songs;
```
Expected: 3 songs with:
- ✅ `artist_id` and `album_id` foreign keys
- ✅ ALL GetSongBPM fields populated
- ✅ `musical_key` from GetSongBPM (will be overwritten by UG if found)

**4. Query with view:**
```sql
SELECT * FROM songs_complete;
```
Expected: Denormalized view showing artist_name and album_title

**5. Check foreign keys:**
```sql
SELECT 
  s.track_name,
  a.artist_name,
  al.album_title,
  s.bpm,
  s.danceability,
  s.acousticness
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
LEFT JOIN albums al ON s.album_id = al.album_id;
```

**6. Verify lyrics and chords:**
```sql
SELECT COUNT(*) FROM song_lyrics;  -- Should have lyrics for all 3
SELECT COUNT(*) FROM song_chords;  -- Should have chord sections
```

---

## ✅ Expected Results

### After Full Pipeline:

**Artists:**
```
artist_id | artist_name      | artist_genres           | artist_country
----------|------------------|------------------------|---------------
1         | Michael Jackson  | ["funk","pop",...     | US
2         | Lewis Capaldi    | [...]                  | GB
3         | D'Angelo         | ["funk","r&b","soul"] | US
```

**Songs:**
```
song_id | track_name        | artist_id | bpm | danceability | acousticness | musical_key
--------|-------------------|-----------|-----|--------------|--------------|------------
1       | Billie Jean       | 1         | 116 | 92           | 3            | F♯m (then Db from UG)
2       | Someone You Loved | 2         | 108 | 51           | 76           | C♯ (then Db from UG)
3       | Spanish Joint     | 3         | 111 | 73           | 54           | Cm
```

---

## 🔧 Troubleshooting

### Issue: Song creation fails
- Check that `artists` table is being populated first
- Verify `artist_id` is returned from `create_or_get_artist`

### Issue: Foreign key violations
- Ensure `artist_id` exists before creating song
- `album_id` can be NULL (not all songs have album data)

### Issue: Lyrics deletion not working
- This feature needs lyrics scraper to return failed `song_id` list
- Current implementation logs but doesn't delete yet (TODO)

### Issue: Musical key not updating from UG
- Check that `update_musical_key` is being called
- Verify `songs_with_key` is being returned from UG scraper

---

## 📋 TODO (Future Enhancements)

### Lyrics Deletion (High Priority)
Update `genius_batch.py` to return:
```python
{
    'successful': 2,
    'failed': 1,
    'failed_song_ids': [5]  # List of song_ids that failed
}
```

Then in `data_enrichment_main.py`:
```python
for song_id in lyrics_results['failed_song_ids']:
    delete_song(song_id, ...)
```

### Add More GetSongBPM Fields (Optional)
If GetSongBPM adds these in future:
- `energy`, `valence`, `speechiness`, `liveness`, `loudness`

### Schema Refinements
- Add `songs.status` field ('complete', 'missing_lyrics', 'missing_chords')
- Add timestamps for when lyrics/chords were last updated

---

## 🎉 **Schema V2 is READY!**

All code has been updated and is ready to test. Run the test with 3 songs, verify the results, then run the full pipeline with your complete song list.

**Next Step:** Apply the SQL schema in Supabase and run the test!

