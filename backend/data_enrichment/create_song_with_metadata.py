"""
CREATE SONG WITH METADATA: Insert song into database with metadata
Creates new song in the songs table using metadata from Musixmatch or MusicBrainz.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv


def create_song_with_metadata(artist_name, track_name, peak_position, metadata):
    """
    Create a new song in the database with metadata.
    
    Args:
        artist_name: Artist name
        track_name: Track name
        peak_position: Billboard chart peak position (can be None)
        metadata: Dict from Musixmatch or MusicBrainz with:
                  {bpm, key, genres, mood_tags, release_date}
    
    Returns:
        Dict with:
        {
            'success': True/False,
            'song_id': UUID (if successful),
            'error': str (if failed)
        }
    """
    print(f"Creating song in database: {artist_name} - {track_name}")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Prepare song data
        song_data = {
            'artist_name': artist_name,
            'track_name': track_name,
            'peak_position': peak_position,
            'bpm': metadata.get('bpm'),
            'musical_key': metadata.get('key'),
            'genres': metadata.get('genres'),
            'moods': metadata.get('mood_tags'),
            'release_date': metadata.get('release_date')
        }
        
        # Insert into songs table
        response = supabase.table('songs').insert(song_data).execute()
        
        if response.data:
            song_id = response.data[0]['song_id']
            print(f"  ✓ Created song with song_id: {song_id}")
            print(f"    Source: {metadata.get('source', 'unknown')}")
            
            return {
                'success': True,
                'song_id': song_id,
                'error': None
            }
        else:
            return {
                'success': False,
                'song_id': None,
                'error': 'No data returned from insert'
            }
    
    except Exception as e:
        return {
            'success': False,
            'song_id': None,
            'error': f'Database error: {str(e)}'
        }

