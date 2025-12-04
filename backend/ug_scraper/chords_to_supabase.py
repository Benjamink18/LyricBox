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
    Save chord data to Supabase ug_chords table.
    
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
    
    # Prepare rows for insertion (one row per section)
    rows = []
    for section_name, data in processed_sections.items():
        row = {
            "artist_name": artist_name,
            "track_name": track_name,
            "tonality": tonality,
            "section_name": section_name,
            "chords_original": data['original'],
            "chords_original_simple": data['original_simple'],
            "chords_in_c": data['in_c'],
            "chords_in_c_simple": data['in_c_simple'],
            "chords_roman": data['roman'],
            "chords_roman_simple": data['roman_simple']
        }
        rows.append(row)
    
    # Insert all rows
    try:
        result = supabase.table("ug_chords").insert(rows).execute()
        print(f"✓ Successfully saved {len(rows)} chord sections to database!")
        return len(rows)
    except Exception as e:
        print(f"✗ Error saving chords to database: {e}")
        return 0

