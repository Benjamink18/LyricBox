# Multi-Source Lyrics Setup Guide

## Overview

You now have a **3-tier automatic fallback system** for fetching CLEAN lyrics:

1. **Musixmatch** - Reliable, clean data (500 calls/day on free tier)
2. **Lyrics.ovh** - Free, unlimited, clean API
3. **LRCLIB** - Free, unlimited, crowdsourced

The system automatically tries each source in order until one succeeds.

**Note:** Genius was intentionally removed due to messy data (annotations, "Embed" text, etc.)

---

## Setup Instructions

### 1. Check Your `.env` File

Your `.env` should have:
```bash
MUSIXMATCH_API_KEY=your_musixmatch_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ANTHROPIC_API_KEY=your_anthropic_key
```

**Note:** Musixmatch free tier has a 500 calls/day limit that resets at midnight UTC.

### 2. Test the Setup

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
python lyrics_client.py
```

You should see successful fetches from various sources!

---

## How to Use in Your Scripts

### Simple Usage

```python
from lyrics_client import get_lyrics

# Automatic fallback through all sources
result = get_lyrics("Hozier", "Too Sweet")

if result.success:
    print(f"✅ Got lyrics via {result.source}")
    lyrics = result.lyrics
else:
    print(f"❌ All sources failed: {result.error}")
```

### Advanced Usage

```python
from lyrics_client import MultiSourceLyricsClient

client = MultiSourceLyricsClient()
result = client.get_lyrics("Artist Name", "Song Title")

print(f"Source: {result.source}")
print(f"Success: {result.success}")
print(f"Lyrics length: {len(result.lyrics)}")
```

---

## Source Comparison

| Source | Cost | Limit | Reliability | Data Quality | Speed |
|--------|------|-------|-------------|--------------|-------|
| Musixmatch | Free tier | 500/day | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Fast |
| Lyrics.ovh | Free | Unlimited | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Fast |
| LRCLIB | Free | Unlimited | ⭐⭐⭐ | ⭐⭐⭐⭐ | Fast |

---

## Benefits

✅ **No single point of failure** - if one source is down, others work  
✅ **Free unlimited access** - Lyrics.ovh + LRCLIB are unlimited  
✅ **Clean data only** - no Genius artifacts, annotations, or "Embed" text  
✅ **Automatic fallback** - no code changes needed, just works  
✅ **Source tracking** - know which API provided each song's lyrics  

---

## Next Steps

1. ✅ System already configured and working!
2. Wait for Musixmatch to reset (midnight UTC)
3. Run adaptive test (all 3 sources will be available)
4. Full import with clean lyrics data!

The import scripts will automatically use the new multi-source client - no code changes needed!

