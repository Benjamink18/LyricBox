"""
TEST GETSONGBPM API
Test the GetSongBPM API to verify it works and see what data it provides.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

artist_name = "Michael Jackson"
track_name = "Billie Jean"

api_key = os.getenv("GETSONGBPM_API_KEY")

# Output file
output_file = f"getsongbpm_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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
log(f"GETSONGBPM API TEST")
log(f"Song: {artist_name} - {track_name}")
log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(separator())

if not api_key:
    log("\n✗ ERROR: GETSONGBPM_API_KEY not found in .env")
    log("\nTo get an API key:")
    log("1. Visit: https://getsongbpm.com/api")
    log("2. Register with your email")
    log("3. Add to .env: GETSONGBPM_API_KEY=your_key_here")
    log("4. Remember: Must include backlink to getsongbpm.com on your site")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"\n✓ Results saved to: {output_file}")
    exit(1)

log(f"\n✓ API Key found: {api_key[:10]}...")

# ============================================================================
# TEST 1: SEARCH ENDPOINT
# ============================================================================
log(f"\n{separator()}")
log("TEST 1: SEARCH ENDPOINT - Search by Artist and Song")
log(separator())

try:
    # Format: "song:track_name artist:artist_name" for type=both
    search_query = f"song:{track_name} artist:{artist_name}"
    url = "https://api.getsong.co/search/"
    
    params = {
        "api_key": api_key,
        "type": "both",
        "lookup": search_query
    }
    
    log(f"\nRequest URL: {url}")
    log(f"Params: type=both, lookup={search_query}")
    
    response = requests.get(url, params=params, timeout=10)
    
    log(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        log(f"✓ SUCCESS")
        
        # Check results
        results = data.get('search', [])
        log(f"\nFound {len(results)} result(s)")
        
        if results:
            # Show first result
            song = results[0]
            
            log(f"\nTop Result:")
            log(f"  ID: {song.get('id')}")
            log(f"  Name: {song.get('song_title')}")
            log(f"  Artist: {song.get('artist', {}).get('name')}")
            log(f"  BPM/Tempo: {song.get('tempo')}")
            log(f"  Key: {song.get('song_key')}")
            log(f"  Album: {song.get('album', {}).get('title')}")
            log(f"  URI: {song.get('uri')}")
            
            log(f"\nFull Response:")
            log(separator("-"))
            log(json.dumps(data, indent=2))
            log(separator("-"))
        else:
            log("\n✗ No results found")
    
    elif response.status_code == 403:
        log(f"✗ 403 Forbidden - Check API key or account status")
        log(f"Response: {response.text}")
    elif response.status_code == 429:
        log(f"✗ 429 Too Many Requests - Rate limit exceeded")
        log(f"Limit: 3,000 requests/hour")
    else:
        log(f"✗ Error: {response.status_code}")
        log(f"Response: {response.text}")
        
except Exception as e:
    log(f"✗ Exception: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# SAVE TO FILE
# ============================================================================
log(f"\n\n{separator()}")
log(f"TEST COMPLETE!")
log(f"Saving results to: {output_file}")
log(separator())

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\n✓ Results saved to: {output_file}")
print(f"✓ File location: {os.path.abspath(output_file)}")

