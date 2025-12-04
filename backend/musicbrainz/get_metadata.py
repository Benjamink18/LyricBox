"""
MUSICBRAINZ METADATA: Fallback metadata source
Fetches genres and release date from MusicBrainz API.
Does NOT provide: BPM, musical key, or mood tags (Musixmatch only).
"""

import musicbrainzngs
import time


def get_metadata(artist_name, track_name):
    """
    Get metadata from MusicBrainz API.
    
    Args:
        artist_name: Artist name (e.g., "Lewis Capaldi")
        track_name: Track name (e.g., "Someone You Loved")
    
    Returns:
        Dict with metadata if found, or error info:
        {
            'success': True/False,
            'source': 'musicbrainz',
            'genres': [...],
            'release_date': 'YYYY-MM-DD',
            'bpm': None,         # MusicBrainz doesn't have BPM
            'key': None,          # MusicBrainz doesn't have key
            'mood_tags': None,    # MusicBrainz doesn't have moods
            'error': None/str
        }
    """
    print(f"Fetching MusicBrainz data for: {artist_name} - {track_name}")
    
    try:
        # Set User-Agent (required by MusicBrainz)
        musicbrainzngs.set_useragent(
            "LyricBox",
            "1.0",
            "https://github.com/yourusername/lyricbox"
        )
        
        # Search for recording
        result = musicbrainzngs.search_recordings(
            artist=artist_name,
            recording=track_name,
            limit=5
        )
        
        if not result.get('recording-list'):
            return {
                'success': False,
                'source': 'musicbrainz',
                'error': 'No recordings found'
            }
        
        # Get the first (best) match
        recording = result['recording-list'][0]
        recording_id = recording['id']
        
        # Rate limiting - wait 1 second between requests
        time.sleep(1)
        
        # Get detailed info with genres
        detailed = musicbrainzngs.get_recording_by_id(
            recording_id,
            includes=['releases', 'genres', 'tags']
        )
        
        recording_data = detailed.get('recording', {})
        
        # Extract genres from tags (MusicBrainz uses tags for genres)
        genres = []
        for tag in recording_data.get('tag-list', []):
            tag_name = tag.get('name', '')
            # Only include music-related tags as genres
            if tag.get('count', 0) > 5:  # Filter low-confidence tags
                genres.append(tag_name)
        
        # Also check genre-list if available
        for genre in recording_data.get('genre-list', []):
            genre_name = genre.get('name', '')
            if genre_name and genre_name not in genres:
                genres.append(genre_name)
        
        # Extract release date from first release
        release_date = None
        releases = recording_data.get('release-list', [])
        if releases:
            first_release = releases[0]
            release_date = first_release.get('date')
        
        result_data = {
            'success': True,
            'source': 'musicbrainz',
            'genres': genres[:10],  # Limit to top 10 genres
            'release_date': release_date,
            'bpm': None,         # MusicBrainz doesn't provide BPM
            'key': None,          # MusicBrainz doesn't provide key
            'mood_tags': None,    # MusicBrainz doesn't provide moods
            'error': None
        }
        
        print(f"✓ MusicBrainz: Genres={genres}, Release={release_date}")
        print(f"  ⚠ Missing: BPM, key, moods (Musixmatch only)")
        
        return result_data
    
    except musicbrainzngs.WebServiceError as e:
        return {
            'success': False,
            'source': 'musicbrainz',
            'error': f'MusicBrainz API error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'source': 'musicbrainz',
            'error': f'Unexpected error: {str(e)}'
        }

