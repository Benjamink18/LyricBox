# Data Sources - What's Available

## Summary

After testing with the Musixmatch free tier API, here's what metadata is actually available from each source:

---

## 📊 Musixmatch (Free Tier)

**Available:**
- ✅ Genres (working well)
- ✅ Track/artist/album names
- ✅ Track length, ratings

**NOT Available in Free Tier:**
- ❌ BPM (requires paid plan)
- ❌ Musical key (requires paid plan)
- ❌ Moods/mood tags (returns 403 Forbidden - requires paid plan)
- ❌ Release date (not in API response)

**API Endpoint:** `matcher.track.get`

---

## 🎵 MusicBrainz (Free)

**Available:**
- ✅ Genres (from tags)
- ✅ Release date ✓

**NOT Available:**
- ❌ BPM (not provided by MusicBrainz)
- ❌ Musical key (not provided by MusicBrainz)
- ❌ Moods (not provided by MusicBrainz)

**API:** `musicbrainzngs` library

---

## 🎸 Ultimate Guitar (Scraped)

**Available:**
- ✅ Tonality/Musical Key (extracted from chord pages)
- ✅ Chords by section (6 versions)

**Use Case:**
- When UG chords are found, the tonality can be used to populate `musical_key` field

---

## 🎤 Genius (Scraped)

**Available:**
- ✅ Lyrics with section markers ([Verse 1], [Chorus], etc.)

---

## Current Database Population

Based on free tier limitations:

| Field | Source | Available? |
|-------|--------|-----------|
| `track_name` | CSV | ✅ |
| `artist_name` | CSV | ✅ |
| `peak_position` | CSV | ✅ |
| `bpm` | ❌ None | ❌ Not available |
| `musical_key` | Ultimate Guitar (tonality) | ⚠️ Only if chords found |
| `genres` | Musixmatch → MusicBrainz | ✅ |
| `moods` | ❌ None | ❌ Not available |
| `release_date` | MusicBrainz | ⚠️ Only if Musixmatch fails |
| `metadata_source` | Auto-tracked | ✅ |

---

## Recommendations

### Option 1: Accept Limitations
- Use Musixmatch for genres
- Use MusicBrainz fallback for release_date
- Accept that BPM and moods won't be populated
- Use UG tonality for musical_key when available

### Option 2: Find Alternative Sources
Potential alternatives for missing data:
- **BPM**: 
  - Spotify API (free, requires auth)
  - Last.fm API (free)
  - Manual scraping from songbpm.com
  
- **Moods**:
  - Spotify's audio features API (valence, energy, etc.)
  - Manual tagging

### Option 3: Paid Musixmatch Plan
Upgrade to Musixmatch paid tier to get:
- BPM
- Musical key
- Moods

---

## Current Status

✅ **Working Well:**
- Genres from Musixmatch
- Lyrics from Genius
- Chords + tonality from Ultimate Guitar
- Source tracking (metadata_source, lyrics_source)

⚠️ **Partially Available:**
- Release date (MusicBrainz only)
- Musical key (UG only, when chords found)

❌ **Not Available:**
- BPM
- Moods

---

## Test Results (Billie Jean)

```
Musixmatch Response:
- Genres: ['Pop', 'R&B/Soul', 'Dance', 'Disco', 'Funk'] ✅
- BPM: None ❌
- Key: None ❌
- Moods: 403 Forbidden ❌
- Release Date: None ❌
```

