"""
Get track metadata from Musixmatch (BPM, key, genres, mood tags, release date).
Reusable across different features in the app.
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
        
        genres = []
        primary_genre = track.get('primary_genres', {}).get('music_genre_list', [])
        for g in primary_genre:
            name = g.get('music_genre', {}).get('music_genre_name')
            if name:
                genres.append(name)
        
        moods = []
        try:
            mood_url = "https://api.musixmatch.com/ws/1.1/track.lyrics.mood.get"
            mood_response = requests.get(mood_url, params={
                "apikey": api_key,
                "track_id": track.get('track_id')
            }, timeout=5)
            mood_data = mood_response.json()
            if mood_data["message"]["header"]["status_code"] == 200:
                for m in mood_data["message"]["body"].get("mood_list", []):
                    if m.get('label'):
                        moods.append(m['label'])
        except:
            pass
        
        result = {
            'success': True,
            'bpm': track.get('track_bpm'),
            'key': track.get('track_key'),
            'release_date': track.get('first_release_date'),
            'genres': genres,
            'mood_tags': moods,
            'error': None
        }
        
        print(f"✓ BPM={result['bpm']}, Key={result['key']}, Genres={genres}, Moods={moods}")
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

