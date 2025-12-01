#!/usr/bin/env python3
"""
Backfill billboard_rank and genre for existing songs in the database.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def backfill_metadata():
    """Update existing songs with billboard_rank and genre from CSV."""
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    # Load Billboard data
    print("📋 Loading Billboard CSV...")
    df = pd.read_csv("billboard_2025_clean.csv")
    
    # Create lookup dict
    billboard_data = {}
    for _, row in df.iterrows():
        key = f"{row['title'].lower()}|{row['artist'].lower()}"
        
        # Convert all_genres string to array
        detailed_genres = None
        if pd.notna(row.get("all_genres")):
            # Split by semicolon and clean up
            detailed_genres = [g.strip() for g in str(row["all_genres"]).split(';')]
        
        billboard_data[key] = {
            "billboard_rank": int(row["peak_position"]) if pd.notna(row.get("peak_position")) else None,
            "genre": row.get("main_genre", "Unknown"),
            "main_genre": row.get("main_genre", "Unknown"),
            "detailed_genres": detailed_genres,
            "genre_source": row.get("genre_source", None)
        }
    
    print(f"✓ Loaded {len(billboard_data)} songs from CSV")
    
    # Get all songs from database
    print("\n📊 Fetching songs from database...")
    result = supabase.table('songs').select('id, title, artist, billboard_rank, genre, main_genre, detailed_genres, genre_source').execute()
    songs = result.data
    
    print(f"✓ Found {len(songs)} songs in database")
    
    # Update each song
    print("\n🔄 Updating songs...")
    updated = 0
    not_found = 0
    
    for song in songs:
        key = f"{song['title'].lower()}|{song['artist'].lower()}"
        
        if key in billboard_data:
            metadata = billboard_data[key]
            
            # Only update if data is missing or different
            needs_update = (
                song.get('billboard_rank') is None or 
                song.get('genre') in [None, 'Unknown'] or
                song.get('main_genre') in [None, 'Unknown'] or
                song.get('detailed_genres') is None or
                song.get('genre_source') is None
            )
            
            if needs_update:
                supabase.table('songs').update({
                    "billboard_rank": metadata["billboard_rank"],
                    "genre": metadata["genre"],
                    "main_genre": metadata["main_genre"],
                    "detailed_genres": metadata["detailed_genres"],
                    "genre_source": metadata["genre_source"]
                }).eq('id', song['id']).execute()
                
                updated += 1
                print(f"  ✓ Updated: {song['title']} - {song['artist']}")
                print(f"    Rank: {metadata['billboard_rank']}, Genre: {metadata['main_genre']}")
                print(f"    Detailed: {metadata['detailed_genres']}, Source: {metadata['genre_source']}")
        else:
            not_found += 1
            print(f"  ⚠️  Not in CSV: {song['title']} - {song['artist']}")
    
    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"✓ Updated: {updated}")
    print(f"⚠️  Not found in CSV: {not_found}")
    print(f"📊 Total songs: {len(songs)}")
    print("=" * 60)

if __name__ == "__main__":
    backfill_metadata()

