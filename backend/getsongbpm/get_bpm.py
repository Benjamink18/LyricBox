"""
GET BPM DATA: Fetch BPM and musical key from GetSongBPM API
Free API for tempo and key information.

API Info:
- Base URL: https://api.getsong.co/
- Free to use (requires backlink to getsongbpm.com)
- Rate limit: 3,000 requests/hour
- Sign up: https://getsongbpm.com/api
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_bpm_data(artist_name, track_name):
    """
    Get BPM and musical key from GetSongBPM API.
    
    Args:
        artist_name: Artist name (e.g., "Michael Jackson")
        track_name: Track name (e.g., "Billie Jean")
    
    Returns:
        Dict with:
        {
            'success': True/False,
            'bpm': int or None,
            'key': str or None (e.g., "F#m"),
            'source': 'getsongbpm',
            'error': None or error message
        }
    """
    print(f"Fetching BPM data for: {artist_name} - {track_name}")
    
    api_key = os.getenv("GETSONGBPM_API_KEY")
    if not api_key:
        return {
            'success': False,
            'bpm': None,
            'key': None,
            'source': 'getsongbpm',
            'error': 'GETSONGBPM_API_KEY not found in .env'
        }
    
    try:
        # Build search query (format: "song:track_name artist:artist_name")
        search_query = f"song:{track_name} artist:{artist_name}"
        
        # API endpoint
        base_url = "https://api.getsong.co/search/"
        params = {
            "api_key": api_key,
            "type": "both",  # Search both artist and song
            "lookup": search_query
        }
        
        # Make request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if we got results
        if not data.get('search') or len(data['search']) == 0:
            print(f"  ✗ No results found")
            return {
                'success': False,
                'bpm': None,
                'key': None,
                'source': 'getsongbpm',
                'error': 'No results found'
            }
        
        # Get first result (best match)
        song = data['search'][0]
        
        # Extract ALL available fields
        bpm = song.get('tempo')
        time_signature = song.get('time_sig')
        musical_key = song.get('key_of')
        camelot_key = song.get('open_key')
        danceability = song.get('danceability')
        acousticness = song.get('acousticness')
        
        # Extract artist data
        artist_data = song.get('artist', {})
        artist_country = artist_data.get('from')
        artist_genres = artist_data.get('genres')  # Array
        
        # Extract album data
        album_data = song.get('album', {})
        album_title = album_data.get('title')
        album_year = album_data.get('year')
        
        # Convert BPM to integer if it exists
        if bpm:
            try:
                bpm = int(float(bpm))
            except (ValueError, TypeError):
                bpm = None
        
        if not bpm:
            print(f"  ✗ No BPM data in result")
            return {
                'success': False,
                'bpm': None,
                'source': 'getsongbpm',
                'error': 'No BPM data available'
            }
        
        print(f"  ✓ Found: BPM={bpm}, Key={musical_key}, Dance={danceability}, Acoustic={acousticness}")
        
        return {
            'success': True,
            'bpm': bpm,
            'time_signature': time_signature,
            'musical_key': musical_key,
            'camelot_key': camelot_key,
            'danceability': danceability,
            'acousticness': acousticness,
            'artist_country': artist_country,
            'artist_genres': artist_genres,
            'artist_data': artist_data,  # Full artist object for IDs/URIs
            'album_title': album_title,
            'album_year': album_year,
            'album_data': album_data,  # Full album object for URIs
            'source': 'getsongbpm',
            'error': None
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'bpm': None,
            'key': None,
            'source': 'getsongbpm',
            'error': 'Request timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'bpm': None,
            'key': None,
            'source': 'getsongbpm',
            'error': f'Network error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'bpm': None,
            'key': None,
            'source': 'getsongbpm',
            'error': f'Unexpected error: {str(e)}'
        }

