"""
COMPREHENSIVE SPOTIFY API TEST
Tests every available endpoint and saves all results to a text file.
Similar to the Musixmatch test but for Spotify.
"""

import os
import requests
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

artist_name = "Michael Jackson"
track_name = "Billie Jean"

# Get Spotify credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

if not client_id or not client_secret:
    print("ERROR: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be in .env")
    print(f"Found CLIENT_ID: {'Yes' if client_id else 'No'}")
    print(f"Found CLIENT_SECRET: {'Yes' if client_secret else 'No'}")
    exit(1)

# Output file
output_file = f"spotify_complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
output = []

def log(text):
    """Log to both console and output list"""
    print(text)
    output.append(text)

def separator(char="="):
    """Create separator line"""
    return char * 80

def make_request(url, headers, endpoint_name):
    """Make API request and log results"""
    log(f"\n{separator()}")
    log(f"{endpoint_name}")
    log(separator())
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            log(f"✓ SUCCESS")
            return response.json(), True
        elif response.status_code == 401:
            log(f"✗ 401 - Unauthorized (check access token)")
            return None, False
        elif response.status_code == 429:
            log(f"✗ 429 - Rate limit exceeded")
            return None, False
        elif response.status_code == 404:
            log(f"✗ 404 - Not found")
            return None, False
        else:
            log(f"✗ Error: {response.status_code}")
            log(f"Response: {response.text}")
            return None, False
            
    except Exception as e:
        log(f"✗ Exception: {e}")
        return None, False

# ============================================================================
# START TEST
# ============================================================================
log(separator("="))
log(f"SPOTIFY WEB API COMPLETE TEST")
log(f"Song: {artist_name} - {track_name}")
log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(separator("="))

# ============================================================================
# STEP 1: AUTHENTICATION (Client Credentials Flow)
# ============================================================================
log(f"\n{separator()}")
log(f"STEP 1: AUTHENTICATION - Client Credentials Flow")
log(separator())

try:
    # Encode credentials
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    # Request access token
    token_url = "https://accounts.spotify.com/api/token"
    token_headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_data = {"grant_type": "client_credentials"}
    
    log(f"Requesting access token...")
    token_response = requests.post(token_url, headers=token_headers, data=token_data, timeout=10)
    
    if token_response.status_code == 200:
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        expires_in = token_json.get("expires_in")
        
        log(f"✓ Authentication successful!")
        log(f"  Access token received (expires in {expires_in} seconds)")
        log(f"  Token type: {token_json.get('token_type')}")
        
        # Set up headers for all future requests
        api_headers = {
            "Authorization": f"Bearer {access_token}"
        }
    else:
        log(f"✗ Authentication failed: {token_response.status_code}")
        log(f"Response: {token_response.text}")
        exit(1)
        
except Exception as e:
    log(f"✗ Authentication error: {e}")
    exit(1)

# Store track/artist/album IDs
spotify_track_id = None
spotify_artist_id = None
spotify_album_id = None

# ============================================================================
# STEP 2: SEARCH FOR TRACK
# ============================================================================
log(f"\n{separator()}")
log(f"STEP 2: SEARCH - Find Spotify ID")
log(separator())

try:
    search_query = f"track:{track_name} artist:{artist_name}"
    search_url = f"https://api.spotify.com/v1/search?q={requests.utils.quote(search_query)}&type=track&limit=5"
    
    response = requests.get(search_url, headers=api_headers, timeout=10)
    
    if response.status_code == 200:
        search_data = response.json()
        tracks = search_data.get("tracks", {}).get("items", [])
        
        log(f"✓ Search successful!")
        log(f"  Found {len(tracks)} tracks")
        
        if tracks:
            # Get first result
            track = tracks[0]
            spotify_track_id = track.get("id")
            spotify_artist_id = track["artists"][0]["id"]
            spotify_album_id = track["album"]["id"]
            
            log(f"\nTop Result:")
            log(f"  Track: {track.get('name')}")
            log(f"  Artist: {track['artists'][0]['name']}")
            log(f"  Album: {track['album']['name']}")
            log(f"  Spotify Track ID: {spotify_track_id}")
            log(f"  Spotify Artist ID: {spotify_artist_id}")
            log(f"  Spotify Album ID: {spotify_album_id}")
            
            log(f"\nFull Search Results:")
            log(separator("-"))
            log(json.dumps(search_data, indent=2))
            log(separator("-"))
        else:
            log(f"✗ No tracks found")
            exit(1)
    else:
        log(f"✗ Search failed: {response.status_code}")
        exit(1)
        
except Exception as e:
    log(f"✗ Search error: {e}")
    exit(1)

# ============================================================================
# STEP 3: GET TRACK
# ============================================================================
if spotify_track_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/tracks/{spotify_track_id}",
        api_headers,
        "STEP 3: GET TRACK - Full Track Object"
    )
    
    if success and data:
        log(f"\nKey Fields:")
        log(f"  Name: {data.get('name')}")
        log(f"  Duration: {data.get('duration_ms')}ms")
        log(f"  Popularity: {data.get('popularity')}/100")
        log(f"  Explicit: {data.get('explicit')}")
        log(f"  ISRC: {data.get('external_ids', {}).get('isrc')}")
        log(f"  Preview URL: {data.get('preview_url')}")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
        log(separator("-"))

# ============================================================================
# STEP 4: GET AUDIO FEATURES (BPM, KEY, TIME SIGNATURE, etc.)
# ============================================================================
if spotify_track_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/audio-features/{spotify_track_id}",
        api_headers,
        "STEP 4: GET AUDIO FEATURES - BPM, Key, Audio Characteristics"
    )
    
    if success and data:
        # Convert key number to note name
        key_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_num = data.get('key', -1)
        key_name = key_map[key_num] if 0 <= key_num < 12 else 'Unknown'
        mode = 'Major' if data.get('mode') == 1 else 'Minor'
        
        log(f"\n🎵 MUSICAL DATA:")
        log(f"  BPM/Tempo: {data.get('tempo')}")
        log(f"  Key: {key_name} {mode} (key={key_num}, mode={data.get('mode')})")
        log(f"  Time Signature: {data.get('time_signature')}/4")
        
        log(f"\n🎨 AUDIO CHARACTERISTICS:")
        log(f"  Acousticness: {data.get('acousticness')} (0.0-1.0)")
        log(f"  Danceability: {data.get('danceability')} (0.0-1.0)")
        log(f"  Energy: {data.get('energy')} (0.0-1.0)")
        log(f"  Instrumentalness: {data.get('instrumentalness')} (0.0-1.0)")
        log(f"  Liveness: {data.get('liveness')} (0.0-1.0)")
        log(f"  Loudness: {data.get('loudness')} dB")
        log(f"  Speechiness: {data.get('speechiness')} (0.0-1.0)")
        log(f"  Valence: {data.get('valence')} (0.0-1.0 - musical positivity)")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
        log(separator("-"))

# ============================================================================
# STEP 5: GET AUDIO ANALYSIS (Detailed Structure)
# ============================================================================
if spotify_track_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/audio-analysis/{spotify_track_id}",
        api_headers,
        "STEP 5: GET AUDIO ANALYSIS - Detailed Structural Analysis"
    )
    
    if success and data:
        log(f"\nStructural Data:")
        log(f"  Track duration: {data.get('track', {}).get('duration')}s")
        log(f"  Sections: {len(data.get('sections', []))}")
        log(f"  Bars: {len(data.get('bars', []))}")
        log(f"  Beats: {len(data.get('beats', []))}")
        log(f"  Tatums: {len(data.get('tatums', []))}")
        log(f"  Segments: {len(data.get('segments', []))}")
        
        # Show first 3 sections
        sections = data.get('sections', [])
        if sections:
            log(f"\nFirst 3 Sections (unlabeled - no verse/chorus info):")
            for i, section in enumerate(sections[:3], 1):
                log(f"  Section {i}:")
                log(f"    Start: {section.get('start')}s")
                log(f"    Duration: {section.get('duration')}s")
                log(f"    Loudness: {section.get('loudness')} dB")
                log(f"    Tempo: {section.get('tempo')} BPM")
                log(f"    Key: {section.get('key')}")
        
        log(f"\nFull Response (first 5000 chars):")
        log(separator("-"))
        response_str = json.dumps(data, indent=2)
        log(response_str[:5000])
        if len(response_str) > 5000:
            log("... (truncated - full data is very large)")
        log(separator("-"))

# ============================================================================
# STEP 6: GET ARTIST
# ============================================================================
if spotify_artist_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/artists/{spotify_artist_id}",
        api_headers,
        "STEP 6: GET ARTIST - Artist Information & Genres"
    )
    
    if success and data:
        log(f"\nArtist Data:")
        log(f"  Name: {data.get('name')}")
        log(f"  Popularity: {data.get('popularity')}/100")
        log(f"  Followers: {data.get('followers', {}).get('total')}")
        
        genres = data.get('genres', [])
        log(f"\n  Genres ({len(genres)}):")
        for genre in genres:
            log(f"    - {genre}")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
        log(separator("-"))

# ============================================================================
# STEP 7: GET ALBUM (Release Date)
# ============================================================================
if spotify_album_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/albums/{spotify_album_id}",
        api_headers,
        "STEP 7: GET ALBUM - Album Info & Release Date"
    )
    
    if success and data:
        log(f"\nAlbum Data:")
        log(f"  Name: {data.get('name')}")
        log(f"  Release Date: {data.get('release_date')}")
        log(f"  Release Date Precision: {data.get('release_date_precision')}")
        log(f"  Total Tracks: {data.get('total_tracks')}")
        log(f"  Label: {data.get('label')}")
        log(f"  Popularity: {data.get('popularity')}/100")
        
        genres = data.get('genres', [])
        if genres:
            log(f"\n  Album Genres:")
            for genre in genres:
                log(f"    - {genre}")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
        log(separator("-"))

# ============================================================================
# STEP 8: BATCH REQUESTS - Get Several Tracks
# ============================================================================
if spotify_track_id:
    # Test batch endpoint with the same track (in real use, you'd pass multiple IDs)
    data, success = make_request(
        f"https://api.spotify.com/v1/tracks?ids={spotify_track_id}",
        api_headers,
        "STEP 8: GET SEVERAL TRACKS - Batch Request (up to 50 tracks)"
    )
    
    if success and data:
        tracks = data.get('tracks', [])
        log(f"\nReturned {len(tracks)} track(s)")
        log(f"Note: In production, you can request up to 50 tracks at once")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
        log(separator("-"))

# ============================================================================
# STEP 9: BATCH AUDIO FEATURES
# ============================================================================
if spotify_track_id:
    data, success = make_request(
        f"https://api.spotify.com/v1/audio-features?ids={spotify_track_id}",
        api_headers,
        "STEP 9: GET SEVERAL TRACKS' AUDIO FEATURES - Batch (up to 100 tracks)"
    )
    
    if success and data:
        features = data.get('audio_features', [])
        log(f"\nReturned {len(features)} audio feature set(s)")
        log(f"Note: In production, you can request up to 100 tracks at once")
        
        log(f"\nFull Response:")
        log(separator("-"))
        log(json.dumps(data, indent=2))
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

