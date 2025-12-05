"""
CREATE SONG WITH METADATA - Schema V2
Creates a song entry in the normalized songs table with foreign keys.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def create_song_with_metadata(
    track_name,
    artist_id,
    album_id,
    peak_position,
    first_chart_date,
    song_genres,
    bpm,
    time_signature,
    musical_key,
    camelot_key,
    danceability,
    acousticness,
    metadata_source='musixmatch+getsongbpm'
):
    """
    Create a song in the normalized database with all metadata.
    
    Args:
        track_name: Song title
        artist_id: Foreign key to artists table
        album_id: Foreign key to albums table (can be None)
        peak_position: Billboard peak position
        first_chart_date: Date first charted (DATE type)
        song_genres: Array of song genres (from Musixmatch)
        bpm: Beats per minute (from GetSongBPM)
        time_signature: Time signature like "4/4" (from GetSongBPM)
        musical_key: Musical key like "F#m" (from GetSongBPM, backup)
        camelot_key: Camelot notation like "4m" (from GetSongBPM)
        danceability: 0-100 (from GetSongBPM)
        acousticness: 0-100 (from GetSongBPM)
        metadata_source: Source of metadata
    
    Returns:
        Dict with:
        {
            'success': True/False,
            'song_id': int or None,
            'error': None or error message
        }
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Prepare song data
        song_data = {
            'track_name': track_name,
            'artist_id': artist_id,
            'album_id': album_id,
            'peak_position': peak_position,
            'first_chart_date': first_chart_date,
            'song_genres': song_genres,
            'bpm': bpm,
            'time_signature': time_signature,
            'musical_key': musical_key,
            'camelot_key': camelot_key,
            'danceability': danceability,
            'acousticness': acousticness,
            'metadata_source': metadata_source
        }
        
        # Insert into database
        response = supabase.table('songs').insert(song_data).execute()
        
        if response.data:
            song_id = response.data[0]['song_id']
            print(f"  ✓ Created song (ID: {song_id})")
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
