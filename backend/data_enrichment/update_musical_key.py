"""
UPDATE MUSICAL KEY
Updates a song's musical_key field (from UG tonality)
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def update_musical_key(song_id, tonality):
    """
    Update the musical_key field for a song.
    Called after UG scraping when tonality is found.
    
    Args:
        song_id: Song ID to update
        tonality: Musical key from Ultimate Guitar (e.g., "Db", "F#m")
    
    Returns:
        True if successful, False if failed
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        response = supabase.table('songs')\
            .update({'musical_key': tonality, 'updated_at': 'NOW()'})\
            .eq('song_id', song_id)\
            .execute()
        
        if response.data:
            return True
        else:
            return False
    
    except Exception as e:
        print(f"  ✗ Error updating key for song ID {song_id}: {e}")
        return False

