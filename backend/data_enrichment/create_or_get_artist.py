"""
CREATE OR GET ARTIST
Creates a new artist record or returns existing artist_id
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def create_or_get_artist(artist_name, artist_genres=None, artist_country=None):
    """
    Create a new artist or return existing artist_id.
    
    Args:
        artist_name: Artist name (unique identifier)
        artist_genres: Array of genres from GetSongBPM
        artist_country: Country code (e.g., "US", "GB")
    
    Returns:
        artist_id (int) if successful, None if failed
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Check if artist already exists
        existing = supabase.table('artists').select('artist_id').eq('artist_name', artist_name).execute()
        
        if existing.data:
            # Artist exists, return existing ID
            return existing.data[0]['artist_id']
        
        # Create new artist
        artist_data = {
            'artist_name': artist_name,
            'artist_genres': artist_genres,
            'artist_country': artist_country
        }
        
        response = supabase.table('artists').insert(artist_data).execute()
        
        if response.data:
            artist_id = response.data[0]['artist_id']
            print(f"  ✓ Created artist: {artist_name} (ID: {artist_id})")
            return artist_id
        else:
            print(f"  ✗ Failed to create artist: {artist_name}")
            return None
    
    except Exception as e:
        print(f"  ✗ Error with artist {artist_name}: {e}")
        return None

