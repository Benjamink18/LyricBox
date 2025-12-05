"""
TEST MUSICBRAINZ: Check what data MusicBrainz actually provides
"""

import musicbrainzngs
import json
import time

artist_name = "Michael Jackson"
track_name = "Billie Jean"

print(f"Testing MusicBrainz API for: {artist_name} - {track_name}")
print("="*70)

try:
    # Set User-Agent (required)
    musicbrainzngs.set_useragent("LyricBox", "1.0", "https://github.com/test/lyricbox")
    
    # Search for recording
    print("\n1️⃣  SEARCHING FOR RECORDING")
    print("="*70)
    result = musicbrainzngs.search_recordings(
        artist=artist_name,
        recording=track_name,
        limit=5
    )
    
    if not result.get('recording-list'):
        print("✗ No recordings found")
        exit(1)
    
    print(f"✓ Found {len(result['recording-list'])} recordings")
    
    # Get the first (best) match
    recording = result['recording-list'][0]
    recording_id = recording['id']
    
    print(f"\nBest match:")
    print(f"  ID: {recording_id}")
    print(f"  Title: {recording.get('title')}")
    print(f"  Artist: {recording['artist-credit'][0]['artist']['name']}")
    print(f"  Score: {recording.get('ext:score')}")
    
    # Rate limiting
    time.sleep(1)
    
    # Get detailed info
    print("\n2️⃣  GETTING DETAILED RECORDING INFO")
    print("="*70)
    detailed = musicbrainzngs.get_recording_by_id(
        recording_id,
        includes=['releases', 'genres', 'tags', 'artist-credits', 'isrcs']
    )
    
    recording_data = detailed.get('recording', {})
    
    # Check for BPM/tempo
    print("\nChecking for BPM/Tempo:")
    print(f"  tempo: {recording_data.get('tempo')}")
    print(f"  bpm: {recording_data.get('bpm')}")
    
    # Check for key
    print("\nChecking for Musical Key:")
    print(f"  key: {recording_data.get('key')}")
    print(f"  musical_key: {recording_data.get('musical_key')}")
    
    # Extract genres from tags
    print("\n3️⃣  GENRES/TAGS")
    print("="*70)
    tags = recording_data.get('tag-list', [])
    print(f"Found {len(tags)} tags:")
    for tag in tags[:15]:  # Show top 15
        print(f"  - {tag.get('name')} (count: {tag.get('count')})")
    
    genres = recording_data.get('genre-list', [])
    if genres:
        print(f"\nFound {len(genres)} official genres:")
        for genre in genres:
            print(f"  - {genre.get('name')}")
    
    # Extract release date
    print("\n4️⃣  RELEASE DATE")
    print("="*70)
    releases = recording_data.get('release-list', [])
    if releases:
        print(f"Found {len(releases)} releases:")
        for i, release in enumerate(releases[:5], 1):  # Show first 5
            print(f"  {i}. {release.get('title')} - {release.get('date', 'No date')}")
        
        # First release date
        first_release = releases[0]
        print(f"\nFirst release date: {first_release.get('date')}")
    
    # ISRCs (can be used to link to other services)
    print("\n5️⃣  ISRCs (Industry Standard Recording Codes)")
    print("="*70)
    isrcs = recording_data.get('isrc-list', [])
    if isrcs:
        print(f"Found {len(isrcs)} ISRCs:")
        for isrc in isrcs:
            print(f"  - {isrc}")
    else:
        print("No ISRCs found")
    
    # Print ALL available fields
    print("\n6️⃣  ALL AVAILABLE FIELDS")
    print("="*70)
    print("Recording object keys:")
    for key in sorted(recording_data.keys()):
        value = recording_data[key]
        if isinstance(value, (dict, list)):
            print(f"  {key}: {type(value).__name__} (length: {len(value)})")
        else:
            print(f"  {key}: {value}")

except musicbrainzngs.WebServiceError as e:
    print(f"✗ MusicBrainz API error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Testing complete!")
print("="*70)

