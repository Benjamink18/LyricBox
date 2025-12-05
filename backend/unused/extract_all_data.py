"""
EXTRACT ALL DATA FROM GETSONGBPM
Comprehensive test to see every piece of data available from the API.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Test with multiple songs to see data variety
test_songs = [
    ("Michael Jackson", "Billie Jean"),
    ("Lewis Capaldi", "Someone You Loved"),
    ("D'Angelo", "Spanish Joint"),
    ("Taylor Swift", "Anti-Hero"),
    ("The Weeknd", "Blinding Lights")
]

api_key = os.getenv("GETSONGBPM_API_KEY")

# Output file
output_file = f"getsongbpm_all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
output = []

def log(text):
    """Log to both console and output list"""
    print(text)
    output.append(text)

def separator(char="="):
    return char * 80

# ============================================================================
# START TEST
# ============================================================================
log(separator())
log(f"GETSONGBPM - COMPLETE DATA EXTRACTION TEST")
log(f"Testing {len(test_songs)} songs to see all available fields")
log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(separator())

if not api_key:
    log("\n✗ ERROR: GETSONGBPM_API_KEY not found in .env")
    exit(1)

log(f"\n✓ API Key: {api_key[:10]}...\n")

# Track all unique fields we encounter
all_fields_found = set()

# ============================================================================
# TEST EACH SONG
# ============================================================================
for i, (artist, track) in enumerate(test_songs, 1):
    log(f"\n{separator()}")
    log(f"SONG {i}/{len(test_songs)}: {artist} - {track}")
    log(separator())
    
    try:
        # Build query
        search_query = f"song:{track} artist:{artist}"
        url = "https://api.getsong.co/search/"
        params = {
            "api_key": api_key,
            "type": "both",
            "lookup": search_query
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        log(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('search', [])
            
            if not results:
                log(f"✗ No results found")
                continue
            
            # Get first result
            song_data = results[0]
            
            log(f"✓ Found: {song_data.get('title')}")
            log(f"\n{'='*80}")
            log(f"ALL AVAILABLE FIELDS:")
            log(f"{'='*80}")
            
            # Track all field names
            for key in song_data.keys():
                all_fields_found.add(key)
            
            # Song-level fields
            log(f"\n📊 SONG DATA:")
            log(f"  ID: {song_data.get('id')}")
            log(f"  Title: {song_data.get('title')}")
            log(f"  URI: {song_data.get('uri')}")
            
            log(f"\n🎵 MUSICAL DATA:")
            log(f"  Tempo/BPM: {song_data.get('tempo')}")
            log(f"  Key: {song_data.get('key_of')}")
            log(f"  Open Key (Camelot): {song_data.get('open_key')}")
            log(f"  Time Signature: {song_data.get('time_sig')}")
            
            log(f"\n🎨 AUDIO CHARACTERISTICS:")
            log(f"  Danceability: {song_data.get('danceability')}/100")
            log(f"  Acousticness: {song_data.get('acousticness')}/100")
            log(f"  Energy: {song_data.get('energy')}")
            log(f"  Valence: {song_data.get('valence')}")
            log(f"  Speechiness: {song_data.get('speechiness')}")
            log(f"  Liveness: {song_data.get('liveness')}")
            log(f"  Instrumentalness: {song_data.get('instrumentalness')}")
            log(f"  Loudness: {song_data.get('loudness')}")
            
            # Artist data
            artist_data = song_data.get('artist', {})
            if artist_data:
                log(f"\n🎤 ARTIST DATA:")
                log(f"  ID: {artist_data.get('id')}")
                log(f"  Name: {artist_data.get('name')}")
                log(f"  URI: {artist_data.get('uri')}")
                log(f"  Country: {artist_data.get('from')}")
                log(f"  MusicBrainz ID: {artist_data.get('mbid')}")
                
                genres = artist_data.get('genres', [])
                log(f"  Genres ({len(genres)}): {', '.join(genres)}")
            
            # Album data
            album_data = song_data.get('album', {})
            if album_data:
                log(f"\n💿 ALBUM DATA:")
                log(f"  Title: {album_data.get('title')}")
                log(f"  Year: {album_data.get('year')}")
                log(f"  URI: {album_data.get('uri')}")
            
            # Show ALL fields (raw)
            log(f"\n{'-'*80}")
            log(f"COMPLETE RAW JSON (all fields):")
            log(f"{'-'*80}")
            log(json.dumps(song_data, indent=2))
            log(f"{'-'*80}")
            
        else:
            log(f"✗ Error: {response.status_code}")
            log(f"Response: {response.text}")
    
    except Exception as e:
        log(f"✗ Exception: {e}")
        import traceback
        log(traceback.format_exc())

# ============================================================================
# SUMMARY OF ALL FIELDS FOUND
# ============================================================================
log(f"\n\n{separator()}")
log(f"SUMMARY: ALL UNIQUE FIELDS FOUND ACROSS ALL SONGS")
log(separator())

log(f"\nTotal unique fields: {len(all_fields_found)}")
log(f"\nField names:")
for field in sorted(all_fields_found):
    log(f"  - {field}")

# ============================================================================
# FIELD RECOMMENDATIONS
# ============================================================================
log(f"\n\n{separator()}")
log(f"RECOMMENDATIONS FOR DATABASE")
log(separator())

log(f"\n✅ CRITICAL (Already Using):")
log(f"  - tempo (BPM) → songs.bpm")

log(f"\n⚠️ USEFUL (Consider Adding):")
log(f"  - danceability → Could add to songs table")
log(f"  - energy → Could add to songs table")
log(f"  - acousticness → Could add to songs table")
log(f"  - time_sig → Could add to songs table")
log(f"  - open_key (Camelot notation) → For DJ mixing features")
log(f"  - album.year → Backup for CSV year data")

log(f"\n❌ NOT NEEDED (Have Better Sources):")
log(f"  - key_of → Ultimate Guitar is more accurate (when chords found)")
log(f"  - artist.genres → Musixmatch genres are better")

log(f"\n💡 BONUS FIELDS (Future Features):")
log(f"  - valence → Musical positivity (mood proxy)")
log(f"  - speechiness → How much spoken word")
log(f"  - liveness → Live performance detection")
log(f"  - loudness → Track loudness in dB")

# ============================================================================
# SAVE TO FILE
# ============================================================================
log(f"\n\n{separator()}")
log(f"TEST COMPLETE!")
log(f"Saving complete data extraction to: {output_file}")
log(separator())

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\n✓ Results saved to: {output_file}")
print(f"✓ File location: {os.path.abspath(output_file)}")
print(f"\n📄 Review this file to see ALL available data from GetSongBPM")

