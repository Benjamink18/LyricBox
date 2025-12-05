"""
DELETE SONG
Removes a song from the database (cascades to all related tables)
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def delete_song(song_id, artist_name=None, track_name=None):
    """
    Delete a song from the database.
    Cascades to song_lyrics, song_chords, etc.
    
    Args:
        song_id: Song ID to delete
        artist_name: Optional, for logging
        track_name: Optional, for logging
    
    Returns:
        True if successful, False if failed
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        response = supabase.table('songs').delete().eq('song_id', song_id).execute()
        
        if response.data or response.count == 0:  # Success if deleted or already gone
            if artist_name and track_name:
                print(f"  ✗ Deleted song: {artist_name} - {track_name} (ID: {song_id})")
            else:
                print(f"  ✗ Deleted song ID: {song_id}")
            return True
        else:
            print(f"  ✗ Failed to delete song ID: {song_id}")
            return False
    
    except Exception as e:
        print(f"  ✗ Error deleting song ID {song_id}: {e}")
        return False

