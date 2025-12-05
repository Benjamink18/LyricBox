"""
CHORDS TO SUPABASE: Save chord data to the database
====================================================
Takes processed chord sections and saves each one as a row in Supabase.
One row per section (Intro, Verse 1, Chorus, etc.)
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def save_chords_to_supabase(artist_name, track_name, tonality, processed_sections):
    """
    Save chord data to Supabase song_chords table.
    
    Args:
        artist_name: Artist name
        track_name: Song title
        tonality: Original key from Ultimate Guitar
        processed_sections: Chord data by section (6 versions per section)
    
    Returns:
        Number of rows inserted
    """
    
    print("\n--- Saving Chords to Supabase ---")
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Supabase credentials not found in .env file!")
        return 0
    
    # Initialize Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    # Find the song_id from the songs table
    try:
        response = supabase.table('songs').select('song_id').eq(
            'artist_name', artist_name
        ).eq('track_name', track_name).execute()
        
        if not response.data:
            print(f"✗ Song not found in database: {artist_name} - {track_name}")
            print("  (Chords can only be saved for songs that exist in 'songs' table)")
            return 0
        
        song_id = response.data[0]['song_id']
        print(f"  Found song_id: {song_id}")
    except Exception as e:
        print(f"✗ Error looking up song: {e}")
        return 0
    
    # Delete existing chords for this song (if any)
    try:
        supabase.table('song_chords').delete().eq('song_id', song_id).execute()
    except:
        pass  # Ignore errors if no existing chords
    
    # Prepare rows for insertion (one row per section)
    rows = []
    for section_name, data in processed_sections.items():
        row = {
            "song_id": song_id,
            "section_name": section_name,
            "tonality": tonality,
            "chords_original": data['original'],
            "chords_original_simplified": data['original_simple'],
            "chords_transposed_c": data['in_c'],
            "chords_transposed_c_simplified": data['in_c_simple'],
            "chords_roman": data['roman'],
            "chords_roman_simplified": data['roman_simple']
        }
        rows.append(row)
    
    # Insert all rows
    try:
        result = supabase.table("song_chords").insert(rows).execute()
        print(f"✓ Successfully saved {len(rows)} chord sections to database!")
        return len(rows)
    except Exception as e:
        print(f"✗ Error saving chords to database: {e}")
        return 0

