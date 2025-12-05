"""
TEST UPGRADED MUSIXMATCH PLAN
Fetch every possible piece of data to see what your upgraded plan provides.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

artist_name = "Michael Jackson"
track_name = "Billie Jean"

print("="*70)
print(f"MUSIXMATCH UPGRADED PLAN TEST")
print(f"Song: {artist_name} - {track_name}")
print("="*70)

api_key = os.getenv("MUSIXMATCH_API_KEY")
if not api_key:
    print("ERROR: MUSIXMATCH_API_KEY not found in .env")
    exit(1)

# Store track_id for later endpoints
track_id = None

# ============================================================================
# 1. MATCHER.TRACK.GET - Main track data
# ============================================================================
print("\n1️⃣  MATCHER.TRACK.GET - Main Track Data")
print("="*70)
try:
    response = requests.get("https://api.musixmatch.com/ws/1.1/matcher.track.get", params={
        "apikey": api_key,
        "q_artist": artist_name,
        "q_track": track_name
    }, timeout=10)
    
    data = response.json()
    if data["message"]["header"]["status_code"] == 200:
        track = data["message"]["body"]["track"]
        track_id = track.get('track_id')
        
        print(f"✓ Track found! ID: {track_id}")
        print(f"\n📊 Basic Info:")
        print(f"  Track Name: {track.get('track_name')}")
        print(f"  Artist: {track.get('artist_name')}")
        print(f"  Album: {track.get('album_name')}")
        print(f"  Track Length: {track.get('track_length')} seconds")
        print(f"  Track Rating: {track.get('track_rating')}/100")
        
        print(f"\n🎵 Musical Data:")
        print(f"  BPM: {track.get('track_bpm')}")
        print(f"  Key: {track.get('track_key')}")
        print(f"  Tempo: {track.get('track_tempo')}")
        print(f"  Time Signature: {track.get('track_time_signature')}")
        print(f"  Mode: {track.get('track_mode')}")
        
        print(f"\n🎨 Audio Features:")
        print(f"  Acousticness: {track.get('acousticness')}")
        print(f"  Danceability: {track.get('danceability')}")
        print(f"  Energy: {track.get('energy')}")
        print(f"  Instrumentalness: {track.get('instrumentalness')}")
        print(f"  Valence: {track.get('valence')}")
        print(f"  Speechiness: {track.get('speechiness')}")
        
        print(f"\n📅 Dates:")
        print(f"  First Release Date: {track.get('first_release_date')}")
        print(f"  Album Release Date: {track.get('album_release_date')}")
        
        print(f"\n🏷️  IDs:")
        print(f"  Spotify ID: {track.get('track_spotify_id')}")
        print(f"  ISRC: {track.get('track_isrc')}")
        
        # Genres
        genres = []
        primary_genre = track.get('primary_genres', {}).get('music_genre_list', [])
        for g in primary_genre:
            name = g.get('music_genre', {}).get('music_genre_name')
            if name:
                genres.append(name)
        print(f"\n🎼 Genres:")
        for genre in genres:
            print(f"  - {genre}")
    else:
        print(f"✗ Error: {data['message']['header']['status_code']}")
except Exception as e:
    print(f"✗ Error: {e}")

# ============================================================================
# 2. TRACK.LYRICS.GET - Lyrics
# ============================================================================
if track_id:
    print("\n\n2️⃣  TRACK.LYRICS.GET - Lyrics")
    print("="*70)
    try:
        response = requests.get("https://api.musixmatch.com/ws/1.1/track.lyrics.get", params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        status = data["message"]["header"]["status_code"]
        
        if status == 200:
            lyrics = data["message"]["body"].get("lyrics", {})
            lyrics_body = lyrics.get("lyrics_body", "")
            
            print(f"✓ Lyrics found!")
            print(f"  Lyrics ID: {lyrics.get('lyrics_id')}")
            print(f"  Language: {lyrics.get('lyrics_language')}")
            print(f"  Explicit: {lyrics.get('explicit')}")
            print(f"  Copyright: {lyrics.get('lyrics_copyright')}")
            
            # Show first 500 chars of lyrics
            if lyrics_body:
                print(f"\n📝 Lyrics Preview (first 500 chars):")
                print("-" * 70)
                print(lyrics_body[:500])
                if len(lyrics_body) > 500:
                    print("... (truncated)")
                print("-" * 70)
        elif status == 401:
            print("✗ 401 - API key issue or lyrics not available")
        elif status == 403:
            print("✗ 403 Forbidden - Requires higher plan tier")
        elif status == 404:
            print("✗ 404 - Lyrics not found for this track")
        else:
            print(f"✗ Status: {status} - {data['message']['header'].get('status_message', 'Unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")

# ============================================================================
# 3. TRACK.LYRICS.MOOD.GET - Mood Tags
# ============================================================================
if track_id:
    print("\n\n3️⃣  TRACK.LYRICS.MOOD.GET - Mood Tags")
    print("="*70)
    try:
        response = requests.get("https://api.musixmatch.com/ws/1.1/track.lyrics.mood.get", params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        status = data["message"]["header"]["status_code"]
        
        if status == 200:
            mood_list = data["message"]["body"].get("mood_list", [])
            print(f"✓ Found {len(mood_list)} moods:")
            for mood in mood_list:
                print(f"  - {mood.get('label')}")
        elif status == 403:
            print("✗ 403 Forbidden - Requires higher plan tier")
        elif status == 404:
            print("✗ 404 - Moods not found for this track")
        else:
            print(f"✗ Status: {status} - {data['message']['header'].get('status_message', 'Unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")

# ============================================================================
# 4. TRACK.RICHSYNC.GET - Time-synced lyrics with sections
# ============================================================================
if track_id:
    print("\n\n4️⃣  TRACK.RICHSYNC.GET - Time-Synced Lyrics")
    print("="*70)
    try:
        response = requests.get("https://api.musixmatch.com/ws/1.1/track.richsync.get", params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        status = data["message"]["header"]["status_code"]
        
        if status == 200:
            richsync = data["message"]["body"].get("richsync", {})
            richsync_body = richsync.get("richsync_body", "")
            
            print(f"✓ RichSync found!")
            print(f"  Length: {richsync.get('richsync_length')} seconds")
            print(f"  Language: {richsync.get('richsync_language')}")
            
            # Show first 1000 chars
            if richsync_body:
                print(f"\n⏱️  RichSync Preview (first 1000 chars):")
                print("-" * 70)
                print(richsync_body[:1000])
                if len(richsync_body) > 1000:
                    print("... (truncated)")
                print("-" * 70)
        elif status == 403:
            print("✗ 403 Forbidden - Requires higher plan tier")
        elif status == 404:
            print("✗ 404 - RichSync not found for this track")
        else:
            print(f"✗ Status: {status} - {data['message']['header'].get('status_message', 'Unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")

# ============================================================================
# 5. TRACK.SNIPPET.GET - Short lyrics snippet
# ============================================================================
if track_id:
    print("\n\n5️⃣  TRACK.SNIPPET.GET - Lyrics Snippet")
    print("="*70)
    try:
        response = requests.get("https://api.musixmatch.com/ws/1.1/track.snippet.get", params={
            "apikey": api_key,
            "track_id": track_id
        }, timeout=10)
        
        data = response.json()
        status = data["message"]["header"]["status_code"]
        
        if status == 200:
            snippet = data["message"]["body"].get("snippet", {})
            snippet_body = snippet.get("snippet_body", "")
            
            print(f"✓ Snippet found!")
            print(f"  Language: {snippet.get('snippet_language')}")
            print(f"\n📄 Snippet:")
            print("-" * 70)
            print(snippet_body)
            print("-" * 70)
        elif status == 403:
            print("✗ 403 Forbidden - Requires higher plan tier")
        elif status == 404:
            print("✗ 404 - Snippet not found")
        else:
            print(f"✗ Status: {status}")
    except Exception as e:
        print(f"✗ Error: {e}")

# ============================================================================
# Summary
# ============================================================================
print("\n\n" + "="*70)
print("TEST COMPLETE!")
print("="*70)
print("\n💡 What you're getting with your upgraded plan:")
print("  - Check which endpoints returned ✓ vs ✗ 403 Forbidden")
print("  - 403 = Still requires higher tier")
print("  - ✓ = Available in your current plan")
print("\n")

