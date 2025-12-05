# GetSongBPM API Integration ✅

**Date:** December 5, 2024  
**Status:** Fully Working

---

## 🎯 What We Get

For each song, GetSongBPM provides:

| Field | Example (Billie Jean) | Database Field |
|-------|----------------------|----------------|
| **BPM/Tempo** | 116 | `songs.bpm` |
| **Musical Key** | F♯m | `songs.musical_key` (backup) |
| **Time Signature** | 4/4 | Not saved |
| **Year** | 1982 | Not saved (using CSV year) |
| **Danceability** | 92/100 | Not saved |
| **Acousticness** | 3/100 | Not saved |

**Note:** We only use BPM. Musical key comes from Ultimate Guitar chords (more accurate).

---

## 📚 API Details

**Base URL:** `https://api.getsong.co/`  
**Rate Limit:** 3,000 requests/hour  
**Cost:** FREE (requires backlink to getsongbpm.com)  
**Backlink:** Added to README.md Credits section

### API Endpoint

**Endpoint:** `/search/`

**Parameters:**
- `api_key` (required): Your API key
- `type` (required): `"both"` (search song and artist together)
- `lookup` (required): `"song:TRACK_NAME artist:ARTIST_NAME"`

**Example Request:**
```
GET https://api.getsong.co/search/?api_key=YOUR_KEY&type=both&lookup=song:Billie Jean artist:Michael Jackson
```

**Response Format:**
```json
{
  "search": [
    {
      "id": "voKlYL",
      "title": "Billie Jean",
      "tempo": "116",
      "key_of": "F♯m",
      "time_sig": "4/4",
      "artist": {
        "name": "Michael Jackson",
        "genres": ["funk", "pop", "rock", "soul"]
      },
      "album": {
        "title": "Thriller",
        "year": "1982"
      }
    }
  ]
}
```

---

## 💻 Implementation

**File:** `backend/getsongbpm/get_bpm.py`

**Function:** `get_bpm_data(artist_name, track_name)`

**Returns:**
```python
{
    'success': True,
    'bpm': 116,
    'key': 'F♯m',
    'source': 'getsongbpm',
    'error': None
}
```

**Usage in Pipeline:**
```python
from getsongbpm.get_bpm import get_bpm_data

bpm_data = get_bpm_data("Michael Jackson", "Billie Jean")
if bpm_data['success']:
    print(f"BPM: {bpm_data['bpm']}")
    # Save to database
```

---

## 🔧 Configuration

**In `.env` file:**
```bash
GETSONGBPM_API_KEY=3747293d1de08fa6222e3874553780a9
```

**Backlink Requirement:**
Must include this on your live website:
```html
BPM data provided by <a href="https://getsongbpm.com">GetSongBPM</a>
```

Already added to README.md Credits section.

---

## ✅ Test Results

**Test Song:** Michael Jackson - Billie Jean  
**Test Date:** December 5, 2024, 13:53:11

**Results:**
- ✅ Authentication: SUCCESS
- ✅ API Call: 200 OK
- ✅ BPM Retrieved: 116
- ✅ Key Retrieved: F♯m
- ✅ Data Quality: Excellent

**Test File:** `backend/unused/getsongbpm_test_20251205_135311.txt`

---

## 🎯 Integration Status

| Component | Status |
|-----------|--------|
| API Key | ✅ Obtained |
| .env Configuration | ✅ Added |
| Function Implementation | ✅ Complete |
| Testing | ✅ Successful |
| Backlink Requirement | ✅ Met |
| Pipeline Integration | ⚠️ Ready to integrate |

---

## 📋 Next Steps

1. ✅ ~~Get API key~~ DONE
2. ✅ ~~Implement get_bpm.py~~ DONE
3. ✅ ~~Test API~~ DONE
4. ⏳ Update database schema (add `year` column)
5. ⏳ Test full enrichment pipeline
6. ⏳ Process all songs from Billboard CSV

---

## 🚀 Ready to Use

The GetSongBPM integration is **fully functional** and ready to be used in the data enrichment pipeline!

**Final Data Stack:**
1. CSV → Track, Artist, Peak, Year ✅
2. Musixmatch → Genres ✅
3. **GetSongBPM → BPM ✅** (NEW!)
4. Genius → Lyrics ✅
5. Ultimate Guitar → Chords + Key ✅

