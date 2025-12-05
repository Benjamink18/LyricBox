# GetSongBPM API - All Available Fields

**Test Song:** Michael Jackson - Billie Jean  
**Full Output:** See `GETSONGBPM_COMPLETE_FIELDS.txt`

---

## ✅ **FIELDS THAT WORK (Returned with Data)**

### **Song Information**
| Field | Type | Example | Use in DB? |
|-------|------|---------|-----------|
| `id` | String | "voKlYL" | ❌ No need |
| `title` | String | "Billie Jean" | ❌ We have from CSV |
| `uri` | String | "https://getsongbpm.com/song/..." | ❌ No need |

### **Musical Characteristics** ⭐
| Field | Type | Example | Use in DB? |
|-------|------|---------|-----------|
| **`tempo`** | String | "116" | ✅ **YES** → `songs.bpm` |
| **`time_sig`** | String | "4/4" | 🤔 **MAYBE** → `songs.time_signature` |
| **`key_of`** | String | "F♯m" | ❌ UG is better |
| **`open_key`** | String | "4m" | 🤔 **MAYBE** → `songs.camelot_key` (DJ feature) |

### **Audio Analysis** ⭐⭐⭐
| Field | Type | Example | Use in DB? |
|-------|------|---------|-----------|
| **`danceability`** | Integer | 92 | ✅ **YES** → `songs.danceability` |
| **`acousticness`** | Integer | 3 | ✅ **YES** → `songs.acousticness` |

### **Artist Information**
| Field | Type | Example | Use in DB? |
|-------|------|---------|-----------|
| `artist.id` | String | "GQ3" | ❌ No need |
| `artist.name` | String | "Michael Jackson" | ❌ We have from CSV |
| `artist.uri` | String | "https://getsongbpm.com/artist/..." | ❌ No need |
| `artist.from` | String | "US" | 🤔 **MAYBE** → `songs.artist_country` |
| `artist.mbid` | String | "f27ec8db..." | ❌ No need |
| `artist.genres` | Array | ["funk", "pop", "rock", "soul"] | ❌ Musixmatch is better |

### **Album Information**
| Field | Type | Example | Use in DB? |
|-------|------|---------|-----------|
| `album.title` | String | "Thriller" | ❌ Not needed |
| `album.uri` | String | "https://getsongbpm.com/album/..." | ❌ Not needed |
| `album.year` | String | "1982" | ❌ We have from CSV |

---

## ❌ **FIELDS THAT DON'T WORK (Returned None)**

These are probably premium-only or not in their database:

| Field | Description | Value |
|-------|-------------|-------|
| `energy` | Energy/intensity level (0-100) | None |
| `valence` | Musical positivity/happiness (0-100) | None |
| `speechiness` | Amount of spoken words (0-100) | None |
| `liveness` | Live performance detection (0-100) | None |
| `instrumentalness` | Vocal vs instrumental (0-100) | None |
| `loudness` | Track loudness in dB | None |
| `popularity` | Song popularity metric | None |
| `artist.similar` | Similar artists list | None |

---

## 🎯 **FINAL RECOMMENDATION: What to Save**

### **Immediate Add (No-Brainers)**
```sql
ALTER TABLE songs
ADD COLUMN danceability INTEGER,  -- 0-100, VERY useful for filters
ADD COLUMN acousticness INTEGER;  -- 0-100, VERY useful for filters
```

**Why?**
- Free (same API call we're already making)
- High user value (danceable vs ballad, acoustic vs electronic)
- Easy to understand and filter

**Example Filters:**
- "Danceable songs" → `danceability > 70`
- "Acoustic songs" → `acousticness > 60`
- "Electronic bangers" → `danceability > 70 AND acousticness < 20`

---

### **Consider Later (Nice to Have)**
```sql
ALTER TABLE songs
ADD COLUMN time_signature VARCHAR(10),  -- "4/4", "3/4", etc.
ADD COLUMN camelot_key VARCHAR(10),     -- "4m", "8d" (DJ mixing)
ADD COLUMN artist_country VARCHAR(5);   -- "US", "GB", "CA"
```

**Why Later?**
- Time signature: Mostly 4/4, but could be fun to find 3/4 waltzes
- Camelot key: Only useful for DJ mixing features
- Artist country: Minor feature (filter by country)

---

## 📊 **Complete Data Example (Billie Jean)**

```json
{
  "id": "voKlYL",
  "title": "Billie Jean",
  "tempo": "116",              ← BPM ✅ SAVE THIS
  "time_sig": "4/4",           ← Maybe save
  "key_of": "F♯m",             ← Have from UG
  "open_key": "4m",            ← Maybe save (DJ feature)
  "danceability": 92,          ← ⭐ SAVE THIS (0-100)
  "acousticness": 3,           ← ⭐ SAVE THIS (0-100)
  "artist": {
    "name": "Michael Jackson",
    "genres": ["funk", "pop", "rock", "soul"],  ← Have from Musixmatch
    "from": "US",              ← Maybe save
    "mbid": "f27ec8db-af05-4f36-916e-3d57f91ecf5e"
  },
  "album": {
    "title": "Thriller",
    "year": "1982"             ← Have from CSV
  }
}
```

---

## 🎵 **Real-World Examples**

### Billie Jean - Very Danceable, Very Electronic
```
BPM: 116
Danceability: 92/100  ← Great for dancing!
Acousticness: 3/100   ← Fully produced/electronic
```

### Someone You Loved - Moderate Dance, Very Acoustic
```
BPM: 108
Danceability: 51/100  ← Slower ballad
Acousticness: 76/100  ← Piano/acoustic guitar
```

### Spanish Joint - Danceable, Mixed
```
BPM: 111
Danceability: 73/100  ← Groovy!
Acousticness: 54/100  ← Mix of live instruments + production
```

### Blinding Lights - Moderate Dance, Fully Electronic
```
BPM: 172  ← Very fast!
Danceability: 52/100  ← Moderate
Acousticness: 1/100   ← Pure synth/electronic
```

---

## ✅ **Action Items**

1. ✅ ~~Extract all fields from API~~ **DONE**
2. ⏳ Update database schema (add `danceability`, `acousticness`)
3. ⏳ Update `get_bpm.py` to return these fields
4. ⏳ Update `create_song_with_metadata.py` to save them
5. ⏳ Test with real songs

---

## 📁 **Files**

- **Complete extraction:** `/docs/GETSONGBPM_COMPLETE_FIELDS.txt`
- **Test script:** `/backend/getsongbpm/extract_everything.py`
- **Current implementation:** `/backend/getsongbpm/get_bpm.py`

