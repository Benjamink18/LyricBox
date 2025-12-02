#!/usr/bin/env python3
"""
Check progress of song analysis in database.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def check_progress():
    """Check how many songs have been analyzed."""
    
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    # Count songs
    songs_result = supabase.table('songs').select('id', count='exact').execute()
    songs_count = songs_result.count
    
    # Count analyses
    analysis_result = supabase.table('song_analysis').select('id', count='exact').execute()
    analysis_count = analysis_result.count
    
    # Count rhyme pairs
    pairs_result = supabase.table('rhyme_pairs').select('id', count='exact').execute()
    pairs_count = pairs_result.count
    
    print("=" * 60)
    print("DATABASE PROGRESS")
    print("=" * 60)
    print()
    print(f"📊 Songs:          {songs_count}")
    print(f"🔍 Analyses:       {analysis_count}")
    print(f"🎯 Rhyme pairs:    {pairs_count}")
    print()
    
    if songs_count > 0:
        avg_pairs = pairs_count / songs_count if songs_count > 0 else 0
        print(f"📈 Average rhyme pairs per song: {avg_pairs:.1f}")
    
    print("=" * 60)


if __name__ == "__main__":
    check_progress()


