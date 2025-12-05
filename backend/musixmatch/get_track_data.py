"""
Get track metadata from Musixmatch.

IMPORTANT: Musixmatch free tier only provides:
- Genres ✓
- Track/artist/album names
- Track length, ratings

NOT available in free tier:
- BPM (requires paid plan)
- Musical key (requires paid plan)
- Moods (requires paid plan)
- Release date (not in API response)

For BPM/key/moods, use MusicBrainz fallback or other sources.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_track_data(artist_name, track_name):
    """Get track metadata from Musixmatch."""
    
    print(f"Fetching Musixmatch data for: {artist_name} - {track_name}")
    api_key = os.getenv("MUSIXMATCH_API_KEY")
    if not api_key:
        return {
            'success': False,
            'error': 'MUSIXMATCH_API_KEY not found in .env'
        }
    
    try:
        # Use matcher.track.get for exact matching (recommended by Musixmatch)
        matcher_url = "https://api.musixmatch.com/ws/1.1/matcher.track.get"
        params = {
            "apikey": api_key,
            "q_artist": artist_name,
            "q_track": track_name
        }
        
        response = requests.get(matcher_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["message"]["header"]["status_code"] != 200:
            return {
                'success': False,
                'error': f"Musixmatch API error: {data['message']['header']['status_code']}"
            }
        
        track = data["message"]["body"].get("track")
        if not track:
            return {
                'success': False,
                'error': 'Track not found in Musixmatch'
            }
        
        # Extract genres (only metadata available in free tier)
        genres = []
        primary_genre = track.get('primary_genres', {}).get('music_genre_list', [])
        for g in primary_genre:
            name = g.get('music_genre', {}).get('music_genre_name')
            if name:
                genres.append(name)
        
        # NOTE: BPM, key, moods, release_date not available in Musixmatch free tier
        # These will be None - use MusicBrainz or other sources for this data
        
        result = {
            'success': True,
            'source': 'musixmatch',
            'bpm': None,  # Not available in free tier
            'key': None,  # Not available in free tier
            'release_date': None,  # Not in API response
            'genres': genres,
            'mood_tags': None,  # Requires paid plan (403 Forbidden)
            'error': None
        }
        
        print(f"✓ Musixmatch: Genres={genres}")
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Network error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

