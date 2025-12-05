"""
LYRICS TO SUPABASE: Save parsed lyrics sections to Supabase database
Uses song_id directly (Schema V2)
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv


def save_lyrics_to_supabase(song_id, parsed_sections):
    """
    Save lyrics sections to Supabase.
    
    Args:
        song_id: Song ID (foreign key to songs table)
        parsed_sections: List of dicts with 'section_name' and 'lyrics_text'
    
    Returns:
        Number of rows saved, or 0 if failed
    """
    print(f"Saving lyrics to Supabase for song_id: {song_id}...")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Delete existing lyrics for this song (if any)
        supabase.table('song_lyrics').delete().eq('song_id', song_id).execute()
        
        # Insert new lyrics sections
        rows_to_insert = []
        for section in parsed_sections:
            rows_to_insert.append({
                'song_id': song_id,
                'section_name': section['section_name'],
                'lyrics_text': section['lyrics_text']
            })
        
        # Batch insert
        supabase.table('song_lyrics').insert(rows_to_insert).execute()
        
        print(f"✓ Saved {len(rows_to_insert)} sections to song_lyrics table")
        
        return len(rows_to_insert)
    
    except Exception as e:
        print(f"✗ Error saving to Supabase: {e}")
        return 0
