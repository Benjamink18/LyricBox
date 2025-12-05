"""
TEST PAID PLAN: Check what fields are available with your paid Musixmatch API key
Tests multiple endpoints to see what data you have access to.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

artist_name = "Michael Jackson"
track_name = "Billie Jean"

print(f"Testing Musixmatch API for: {artist_name} - {track_name}")
print("="*70)

api_key = os.getenv("MUSIXMATCH_API_KEY")
if not api_key:
    print("ERROR: MUSIXMATCH_API_KEY not found in .env")
    exit(1)

# Test 1: matcher.track.get (what we're currently using)
print("\n1️⃣  MATCHER.TRACK.GET (current endpoint)")
print("="*70)
try:
    matcher_url = "https://api.musixmatch.com/ws/1.1/matcher.track.get"
    response = requests.get(matcher_url, params={
        "apikey": api_key,
        "q_artist": artist_name,
        "q_track": track_name
    }, timeout=10)
    
    data = response.json()
    if data["message"]["header"]["status_code"] == 200:
        track = data["message"]["body"].get("track", {})
        
        print(f"✓ Status: {data['message']['header']['status_code']}")
        print(f"\nKey fields:")
        print(f"  track_id: {track.get('track_id')}")
        print(f"  track_bpm: {track.get('track_bpm')}")
        print(f"  track_key: {track.get('track_key')}")
        print(f"  track_mbid: {track.get('track_mbid')}")
        print(f"  first_release_date: {track.get('first_release_date')}")
        print(f"  album_release_date: {track.get('album_release_date')}")
        print(f"  updated_time: {track.get('updated_time')}")
        
        # Save track_id for later tests
        track_id = track.get('track_id')
    else:
        print(f"✗ Status: {data['message']['header']['status_code']}")
        track_id = None
except Exception as e:
    print(f"✗ Error: {e}")
    track_id = None

# Test 2: track.get (alternative endpoint)
if track_id:
    print("\n2️⃣  TRACK.GET (alternative endpoint)")
    print("="*70)
    try:
        track_url = "https://api.musixmatch.com/ws/1.1/track.get"
        response = requests.get(track_url, params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        print(f"Status: {data['message']['header']['status_code']}")
        
        if data["message"]["header"]["status_code"] == 200:
            track = data["message"]["body"].get("track", {})
            print(f"\nAdditional fields:")
            print(f"  track_bpm: {track.get('track_bpm')}")
            print(f"  track_key: {track.get('track_key')}")
            print(f"  track_tempo: {track.get('track_tempo')}")
            print(f"  track_mode: {track.get('track_mode')}")
            print(f"  track_time_signature: {track.get('track_time_signature')}")
            print(f"  acousticness: {track.get('acousticness')}")
            print(f"  danceability: {track.get('danceability')}")
            print(f"  energy: {track.get('energy')}")
            print(f"  instrumentalness: {track.get('instrumentalness')}")
            print(f"  valence: {track.get('valence')}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Test 3: track.lyrics.mood.get
if track_id:
    print("\n3️⃣  TRACK.LYRICS.MOOD.GET")
    print("="*70)
    try:
        mood_url = "https://api.musixmatch.com/ws/1.1/track.lyrics.mood.get"
        response = requests.get(mood_url, params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        status = data['message']['header']['status_code']
        print(f"Status: {status}")
        
        if status == 200:
            moods = data["message"]["body"].get("mood_list", [])
            print(f"✓ Found {len(moods)} moods:")
            for m in moods:
                print(f"  - {m.get('label')}")
        elif status == 403:
            print("✗ 403 Forbidden - requires higher plan tier")
        else:
            print(f"Message: {data['message']['header'].get('status_message', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Test 4: Check all available fields in matcher response
print("\n4️⃣  ALL FIELDS FROM MATCHER.TRACK.GET")
print("="*70)
try:
    response = requests.get("https://api.musixmatch.com/ws/1.1/matcher.track.get", params={
        "apikey": api_key,
        "q_artist": artist_name,
        "q_track": track_name
    }, timeout=10)
    
    track = response.json()["message"]["body"]["track"]
    
    print("All available field names:")
    for key in sorted(track.keys()):
        value = track[key]
        # Truncate long values
        if isinstance(value, (dict, list)):
            value = f"{type(value).__name__} (length: {len(value)})"
        elif isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"  {key}: {value}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("Testing complete!")
print("="*70)

