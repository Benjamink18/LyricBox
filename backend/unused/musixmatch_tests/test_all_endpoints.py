"""
COMPREHENSIVE MUSIXMATCH API TEST
Tests every available endpoint and saves all results to a text file.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

artist_name = "Michael Jackson"
track_name = "Billie Jean"

api_key = os.getenv("MUSIXMATCH_API_KEY")
if not api_key:
    print("ERROR: MUSIXMATCH_API_KEY not found in .env")
    exit(1)

# Output file
output_file = f"musixmatch_complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
output = []

def log(text):
    """Log to both console and output list"""
    print(text)
    output.append(text)

def separator(char="="):
    """Create separator line"""
    return char * 80

def make_request(url, params, endpoint_name):
    """Make API request and log results"""
    log(f"\n{separator()}")
    log(f"{endpoint_name}")
    log(separator())
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        status = data["message"]["header"]["status_code"]
        status_msg = data["message"]["header"].get("status_message", "")
        
        log(f"Status: {status} {status_msg}")
        
        if status == 200:
            log(f"✓ SUCCESS")
            return data, True
        elif status == 401:
            log(f"✗ 401 - Authentication failed or API key issue")
            return data, False
        elif status == 403:
            log(f"✗ 403 Forbidden - Requires higher plan tier")
            return data, False
        elif status == 404:
            log(f"✗ 404 - Data not found")
            return data, False
        else:
            log(f"✗ Error: {status}")
            return data, False
            
    except Exception as e:
        log(f"✗ Exception: {e}")
        return None, False

# ============================================================================
# START TEST
# ============================================================================
log(separator("="))
log(f"MUSIXMATCH COMPLETE API TEST")
log(f"Song: {artist_name} - {track_name}")
log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(separator("="))

# Store IDs for later use
track_id = None
artist_id = None
album_id = None

# ============================================================================
# 1. MATCHER.TRACK.GET
# ============================================================================
data, success = make_request(
    "https://api.musixmatch.com/ws/1.1/matcher.track.get",
    {"apikey": api_key, "q_artist": artist_name, "q_track": track_name},
    "1. MATCHER.TRACK.GET - Main Track Matcher"
)

if success and data:
    track = data["message"]["body"].get("track", {})
    track_id = track.get('track_id')
    artist_id = track.get('artist_id')
    album_id = track.get('album_id')
    
    log(f"\nFull Response:")
    log(separator("-"))
    log(json.dumps(track, indent=2))
    log(separator("-"))

# ============================================================================
# 2. TRACK.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.get",
        {"apikey": api_key, "track_id": track_id},
        "2. TRACK.GET - Track by ID"
    )
    
    if success and data:
        track = data["message"]["body"].get("track", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(track, indent=2))
        log(separator("-"))

# ============================================================================
# 3. MATCHER.LYRICS.GET
# ============================================================================
data, success = make_request(
    "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get",
    {"apikey": api_key, "q_artist": artist_name, "q_track": track_name},
    "3. MATCHER.LYRICS.GET - Lyrics via Matcher"
)

if success and data:
    lyrics = data["message"]["body"].get("lyrics", {})
    log(f"\nFull Response:")
    log(separator("-"))
    log(json.dumps(lyrics, indent=2))
    log(separator("-"))

# ============================================================================
# 4. TRACK.LYRICS.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.lyrics.get",
        {"apikey": api_key, "track_id": track_id},
        "4. TRACK.LYRICS.GET - Lyrics by Track ID"
    )
    
    if success and data:
        lyrics = data["message"]["body"].get("lyrics", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(lyrics, indent=2))
        log(separator("-"))

# ============================================================================
# 5. MATCHER.SUBTITLE.GET
# ============================================================================
data, success = make_request(
    "https://api.musixmatch.com/ws/1.1/matcher.subtitle.get",
    {"apikey": api_key, "q_artist": artist_name, "q_track": track_name},
    "5. MATCHER.SUBTITLE.GET - Subtitles via Matcher"
)

if success and data:
    subtitle = data["message"]["body"].get("subtitle", {})
    log(f"\nFull Response:")
    log(separator("-"))
    log(json.dumps(subtitle, indent=2))
    log(separator("-"))

# ============================================================================
# 6. TRACK.SUBTITLE.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.subtitle.get",
        {"apikey": api_key, "track_id": track_id},
        "6. TRACK.SUBTITLE.GET - Subtitles by Track ID"
    )
    
    if success and data:
        subtitle = data["message"]["body"].get("subtitle", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(subtitle, indent=2))
        log(separator("-"))

# ============================================================================
# 7. TRACK.RICHSYNC.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.richsync.get",
        {"apikey": api_key, "track_id": track_id},
        "7. TRACK.RICHSYNC.GET - Time-Synced Lyrics"
    )
    
    if success and data:
        richsync = data["message"]["body"].get("richsync", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(richsync, indent=2))
        log(separator("-"))

# ============================================================================
# 8. TRACK.LYRICS.MOOD.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.lyrics.mood.get",
        {"apikey": api_key, "track_id": track_id},
        "8. TRACK.LYRICS.MOOD.GET - Mood Tags"
    )
    
    if success and data:
        mood_list = data["message"]["body"].get("mood_list", [])
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(mood_list, indent=2))
        log(separator("-"))

# ============================================================================
# 9. TRACK.SNIPPET.GET (if we have track_id)
# ============================================================================
if track_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/track.snippet.get",
        {"apikey": api_key, "track_id": track_id},
        "9. TRACK.SNIPPET.GET - Lyrics Snippet"
    )
    
    if success and data:
        snippet = data["message"]["body"].get("snippet", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(snippet, indent=2))
        log(separator("-"))

# ============================================================================
# 10. TRACK.SEARCH
# ============================================================================
data, success = make_request(
    "https://api.musixmatch.com/ws/1.1/track.search",
    {"apikey": api_key, "q_artist": artist_name, "q_track": track_name},
    "10. TRACK.SEARCH - Search for Track"
)

if success and data:
    track_list = data["message"]["body"].get("track_list", [])
    log(f"\nFound {len(track_list)} tracks:")
    log(separator("-"))
    log(json.dumps(track_list, indent=2))
    log(separator("-"))

# ============================================================================
# 11. ARTIST.GET (if we have artist_id)
# ============================================================================
if artist_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/artist.get",
        {"apikey": api_key, "artist_id": artist_id},
        "11. ARTIST.GET - Artist Information"
    )
    
    if success and data:
        artist = data["message"]["body"].get("artist", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(artist, indent=2))
        log(separator("-"))

# ============================================================================
# 12. ALBUM.GET (if we have album_id)
# ============================================================================
if album_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/album.get",
        {"apikey": api_key, "album_id": album_id},
        "12. ALBUM.GET - Album Information (CHECK FOR RELEASE DATE!)"
    )
    
    if success and data:
        album = data["message"]["body"].get("album", {})
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(album, indent=2))
        log(separator("-"))

# ============================================================================
# 13. ARTIST.ALBUMS.GET (if we have artist_id)
# ============================================================================
if artist_id:
    data, success = make_request(
        "https://api.musixmatch.com/ws/1.1/artist.albums.get",
        {"apikey": api_key, "artist_id": artist_id, "s_release_date": "desc", "g_album_name": 1},
        "13. ARTIST.ALBUMS.GET - Artist's Albums"
    )
    
    if success and data:
        album_list = data["message"]["body"].get("album_list", [])
        log(f"\nFound {len(album_list)} albums:")
        log(separator("-"))
        log(json.dumps(album_list[:3], indent=2))  # Show first 3
        log(separator("-"))

# ============================================================================
# SAVE TO FILE
# ============================================================================
log(f"\n\n{separator('=')}")
log(f"TEST COMPLETE!")
log(f"Saving results to: {output_file}")
log(separator('='))

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\n✓ Results saved to: {output_file}")
print(f"✓ File location: {os.path.abspath(output_file)}")

