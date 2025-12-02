#!/usr/bin/env python3
"""
Clear analysis-related tables in Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def clear_tables():
    """Clear rhyme_pairs and song_analysis tables."""
    
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    print("🗑️  Clearing analysis tables...")
    print()
    
    # Clear rhyme_pairs
    print("Clearing rhyme_pairs...")
    result = supabase.table('rhyme_pairs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"✅ Cleared rhyme_pairs")
    
    # Clear song_analysis
    print("Clearing song_analysis...")
    result = supabase.table('song_analysis').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"✅ Cleared song_analysis")
    
    print()
    print("✅ Database cleared and ready for fresh import!")


if __name__ == "__main__":
    clear_tables()


