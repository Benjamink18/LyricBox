# GetSongBPM - Complete Data Available

**Test Date:** December 5, 2024  
**Songs Tested:** 5 (Michael Jackson, Lewis Capaldi, D'Angelo, The Weeknd)  
**Full Data:** See `GETSONGBPM_ALL_DATA.txt`

---

## 🎯 ALL AVAILABLE FIELDS

### ✅ **Currently Using:**

| Field | Description | Example | Our DB Field |
|-------|-------------|---------|--------------|
| `tempo` | BPM (beats per minute) | 116 | `songs.bpm` |

---

### ⭐ **HIGHLY RECOMMENDED - Add to Database:**

| Field | Description | Range | Example Songs | Value |
|-------|-------------|-------|---------------|-------|
| **`danceability`** | How suitable for dancing | 0-100 | Billie Jean: 92<br>Someone You Loved: 51 | 🔥 Perfect for filtering danceable songs vs ballads |
| **`acousticness`** | Acoustic vs electronic | 0-100 | Billie Jean: 3<br>Someone You Loved: 76 | 🔥 Great for acoustic/electric filters |
| **`time_sig`** | Time signature | String | 4/4 | 💡 Useful for music theory features |
| **`open_key`** | Camelot wheel notation | String | 4m, 8d, 10m | 💡 DJ mixing / harmonic mixing features |

**Why these are useful:**
- **Danceability:** Users could filter "upbeat songs" vs "slow ballads" - very practical
- **Acousticness:** Filter acoustic songs vs electronic/produced - user-friendly feature
- **Time signature:** Most will be 4/4, but interesting to show 3/4 (waltz), 6/8, etc.
- **Open Key (Camelot):** DJs use this for harmonic mixing - could add "Find compatible keys" feature

---

### 🤔 **MAYBE USEFUL - Consider Later:**

| Field | Description | Example | Notes |
|-------|-------------|---------|-------|
| `key_of` | Musical key | F♯m, C♯, Cm | We get this from Ultimate Guitar (more accurate from chords) |
| `artist.genres` | Genre array | ["funk", "pop", "soul"] | We already get from Musixmatch |
| `artist.from` | Country code | US, GB, CA | Could add "artist origin" filter later |
| `album.year` | Release year | 1982, 2000, 2020 | We get from CSV `first_chart_date` |
| `artist.mbid` | MusicBrainz ID | UUID | Good for linking external data |

---

### ❌ **NOT AVAILABLE (Free Tier):**

The following fields showed as `None` for all tested songs:
- `energy` - Energy level
- `valence` - Musical positivity/happiness
- `speechiness` - Amount of spoken words
- `liveness` - Live performance detection
- `instrumentalness` - Vocal vs instrumental
- `loudness` - Track loudness in dB

**Note:** These might be premium-only fields or not available for all songs.

---

## 📊 **Real Data Examples:**

### Billie Jean (Michael Jackson)
```
Tempo: 116 BPM
Key: F♯m
Camelot: 4m
Time Sig: 4/4
Danceability: 92/100  ← Very danceable!
Acousticness: 3/100   ← Very electronic/produced
Artist Genres: funk, pop, rock, soul
Album: Thriller (1982)
Country: US
```

### Someone You Loved (Lewis Capaldi)
```
Tempo: 108 BPM
Key: C♯
Camelot: 8d
Time Sig: 4/4
Danceability: 51/100  ← Moderate (ballad)
Acousticness: 76/100  ← Very acoustic!
Country: GB
```

### Spanish Joint (D'Angelo)
```
Tempo: 111 BPM
Key: Cm
Camelot: 10m
Time Sig: 4/4
Danceability: 73/100  ← Danceable
Acousticness: 54/100  ← Mixed
Artist Genres: funk, r&b, soul
Album: Voodoo (2000)
Country: US
```

### Blinding Lights (The Weeknd)
```
Tempo: 172 BPM  ← Very fast!
Key: Cm
Camelot: 10m
Time Sig: 4/4
Danceability: 52/100
Acousticness: 1/100   ← Fully electronic!
Artist Genres: pop, r&b
Album: After Hours (2020)
Country: CA
```

---

## 💡 **Recommendations for Your Database:**

### Immediate Add (High Value):
```sql
ALTER TABLE songs
ADD COLUMN danceability INTEGER,  -- 0-100
ADD COLUMN acousticness INTEGER;  -- 0-100
```

**Frontend Features You Could Build:**
- Filter slider: "Danceability: 0-100" (find upbeat vs slow songs)
- Filter toggle: "Acoustic only" (acousticness > 60)
- Filter toggle: "Electronic only" (acousticness < 20)

---

### Consider Adding Later:
```sql
ALTER TABLE songs
ADD COLUMN time_signature VARCHAR(10),  -- "4/4", "3/4", "6/8"
ADD COLUMN camelot_key VARCHAR(10),     -- "4m", "8d" (DJ mixing)
ADD COLUMN artist_country VARCHAR(5);   -- "US", "GB", "CA"
```

**Future Features:**
- "Find songs in same key" (using Camelot wheel)
- "Songs from UK artists"
- "Songs in 3/4 time" (waltzes)

---

## 🎯 **Updated Pipeline Recommendation:**

### Current Pipeline:
1. CSV → Track, Artist, Peak, **Year** ✅
2. Musixmatch → **Genres** ✅
3. GetSongBPM → **BPM** ✅
4. Genius → **Lyrics** ✅
5. Ultimate Guitar → **Chords + Key** ✅

### Enhanced Pipeline (Add danceability + acousticness):
1. CSV → Track, Artist, Peak, **Year** ✅
2. Musixmatch → **Genres** ✅
3. GetSongBPM → **BPM, Danceability, Acousticness** ⭐ ENHANCED
4. Genius → **Lyrics** ✅
5. Ultimate Guitar → **Chords + Key** ✅

**Cost:** Still FREE  
**Extra API Calls:** None (same call, just save more fields)  
**User Value:** High - very useful filters

---

## 🚀 **Next Steps:**

1. ✅ ~~Test GetSongBPM API~~ DONE
2. ⏳ **Update database schema** - Add `danceability` and `acousticness` columns
3. ⏳ **Update `get_bpm.py`** - Return danceability and acousticness
4. ⏳ **Update `create_song_with_metadata.py`** - Save new fields
5. ⏳ **Test full pipeline** - Verify all data saves correctly

---

## 📁 Files:

- **Full Data Extraction:** `/docs/GETSONGBPM_ALL_DATA.txt`
- **Test Script:** `/backend/getsongbpm/extract_all_data.py`
- **Implementation:** `/backend/getsongbpm/get_bpm.py`

