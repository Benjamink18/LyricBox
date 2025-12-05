"""
GetSongBPM - Extract EVERYTHING from API
Single song test to see every available field
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Test with one well-known song
ARTIST = "Michael Jackson"
TRACK = "Billie Jean"

api_key = os.getenv("GETSONGBPM_API_KEY")

if not api_key:
    print("✗ ERROR: GETSONGBPM_API_KEY not found in .env")
    exit(1)

print("="*80)
print(f"GETSONGBPM - COMPLETE FIELD EXTRACTION")
print(f"Artist: {ARTIST}")
print(f"Track: {TRACK}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Build query
search_query = f"song:{TRACK} artist:{ARTIST}"
url = "https://api.getsong.co/search/"
params = {
    "api_key": api_key,
    "type": "both",
    "lookup": search_query
}

print(f"\nRequest URL: {url}")
print(f"Query: {search_query}\n")

response = requests.get(url, params=params, timeout=10)

print(f"Status Code: {response.status_code}\n")

if response.status_code != 200:
    print(f"✗ Error: {response.text}")
    exit(1)

data = response.json()
results = data.get('search', [])

if not results:
    print("✗ No results found")
    exit(1)

# Get first result
song = results[0]

print("="*80)
print("COMPLETE RAW JSON RESPONSE")
print("="*80)
print(json.dumps(song, indent=2, ensure_ascii=False))
print("="*80)

print("\n\n")
print("="*80)
print("FIELD-BY-FIELD BREAKDOWN")
print("="*80)

def print_field(name, value, description=""):
    """Print a field in a clean format"""
    value_str = str(value) if value is not None else "None"
    type_str = type(value).__name__
    
    if description:
        print(f"\n{name}:")
        print(f"  Value: {value_str}")
        print(f"  Type: {type_str}")
        print(f"  Description: {description}")
    else:
        print(f"\n{name}: {value_str} ({type_str})")

# ============================================================================
# SONG LEVEL FIELDS
# ============================================================================
print("\n" + "="*80)
print("📊 SONG LEVEL FIELDS")
print("="*80)

print_field("id", song.get('id'), "GetSong unique ID for this song")
print_field("title", song.get('title'), "Song title")
print_field("uri", song.get('uri'), "GetSong URL for this song page")

# ============================================================================
# MUSICAL CHARACTERISTICS
# ============================================================================
print("\n" + "="*80)
print("🎵 MUSICAL CHARACTERISTICS")
print("="*80)

print_field("tempo", song.get('tempo'), "BPM (beats per minute) - THE KEY FIELD")
print_field("time_sig", song.get('time_sig'), "Time signature (4/4, 3/4, etc.)")
print_field("key_of", song.get('key_of'), "Musical key (e.g., F♯m, C, D♭)")
print_field("open_key", song.get('open_key'), "Camelot wheel notation for DJ mixing")

# ============================================================================
# AUDIO ANALYSIS METRICS
# ============================================================================
print("\n" + "="*80)
print("🎨 AUDIO ANALYSIS METRICS (0-100)")
print("="*80)

print_field("danceability", song.get('danceability'), "How suitable for dancing (0-100)")
print_field("acousticness", song.get('acousticness'), "Acoustic vs electronic (0-100)")
print_field("energy", song.get('energy'), "Energy/intensity level (0-100)")
print_field("valence", song.get('valence'), "Musical positivity/happiness (0-100)")
print_field("speechiness", song.get('speechiness'), "Amount of spoken words (0-100)")
print_field("liveness", song.get('liveness'), "Live performance detection (0-100)")
print_field("instrumentalness", song.get('instrumentalness'), "Vocal vs instrumental (0-100)")
print_field("loudness", song.get('loudness'), "Track loudness in dB")
print_field("popularity", song.get('popularity'), "Song popularity metric")

# ============================================================================
# ARTIST DATA
# ============================================================================
artist_data = song.get('artist', {})
if artist_data:
    print("\n" + "="*80)
    print("🎤 ARTIST DATA")
    print("="*80)
    
    print_field("artist.id", artist_data.get('id'), "GetSong artist ID")
    print_field("artist.name", artist_data.get('name'), "Artist name")
    print_field("artist.uri", artist_data.get('uri'), "GetSong artist page URL")
    print_field("artist.from", artist_data.get('from'), "Country code (US, GB, etc.)")
    print_field("artist.mbid", artist_data.get('mbid'), "MusicBrainz ID (external database)")
    print_field("artist.genres", artist_data.get('genres'), "Array of genre tags")
    print_field("artist.similar", artist_data.get('similar'), "Similar artists list")

# ============================================================================
# ALBUM DATA
# ============================================================================
album_data = song.get('album', {})
if album_data:
    print("\n" + "="*80)
    print("💿 ALBUM DATA")
    print("="*80)
    
    print_field("album.title", album_data.get('title'), "Album name")
    print_field("album.uri", album_data.get('uri'), "GetSong album page URL")
    print_field("album.year", album_data.get('year'), "Release year")

# ============================================================================
# CHECK FOR ANY ADDITIONAL FIELDS
# ============================================================================
print("\n" + "="*80)
print("🔍 ALL FIELD NAMES (Top Level)")
print("="*80)

all_keys = sorted(song.keys())
print("\nSong object keys:")
for key in all_keys:
    print(f"  - {key}")

if artist_data:
    print("\nArtist object keys:")
    for key in sorted(artist_data.keys()):
        print(f"  - artist.{key}")

if album_data:
    print("\nAlbum object keys:")
    for key in sorted(album_data.keys()):
        print(f"  - album.{key}")

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================
print("\n\n" + "="*80)
print("💡 RECOMMENDATIONS FOR DATABASE")
print("="*80)

print("\n✅ CURRENTLY USING:")
print("  - tempo → songs.bpm")

print("\n⭐ SHOULD ADD (High Value):")
if song.get('danceability') is not None:
    print(f"  - danceability → songs.danceability (value: {song.get('danceability')})")
if song.get('acousticness') is not None:
    print(f"  - acousticness → songs.acousticness (value: {song.get('acousticness')})")

print("\n🤔 CONSIDER ADDING:")
if song.get('time_sig') is not None:
    print(f"  - time_sig → songs.time_signature (value: {song.get('time_sig')})")
if song.get('open_key') is not None:
    print(f"  - open_key → songs.camelot_key (value: {song.get('open_key')})")
if song.get('energy') is not None:
    print(f"  - energy → songs.energy (value: {song.get('energy')})")
if song.get('valence') is not None:
    print(f"  - valence → songs.valence (value: {song.get('valence')})")

print("\n❌ NOT AVAILABLE (returned None):")
none_fields = []
for field in ['energy', 'valence', 'speechiness', 'liveness', 'instrumentalness', 'loudness', 'popularity']:
    if song.get(field) is None:
        none_fields.append(field)
if none_fields:
    for field in none_fields:
        print(f"  - {field}")
else:
    print("  (All fields have data!)")

print("\n" + "="*80)

