"""
CREATE OR GET ALBUM
Creates a new album record or returns existing album_id
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client


def create_or_get_album(album_title, album_year, artist_id):
    """
    Create a new album or return existing album_id.
    
    Args:
        album_title: Album name
        album_year: Release year (string)
        artist_id: Foreign key to artists table
    
    Returns:
        album_id (int) if successful, None if failed
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Check if album already exists for this artist
        existing = supabase.table('albums')\
            .select('album_id')\
            .eq('album_title', album_title)\
            .eq('artist_id', artist_id)\
            .execute()
        
        if existing.data:
            # Album exists, return existing ID
            return existing.data[0]['album_id']
        
        # Create new album
        album_data = {
            'album_title': album_title,
            'album_year': album_year,
            'artist_id': artist_id
        }
        
        response = supabase.table('albums').insert(album_data).execute()
        
        if response.data:
            album_id = response.data[0]['album_id']
            print(f"  ✓ Created album: {album_title} (ID: {album_id})")
            return album_id
        else:
            print(f"  ✗ Failed to create album: {album_title}")
            return None
    
    except Exception as e:
        print(f"  ✗ Error with album {album_title}: {e}")
        return None

