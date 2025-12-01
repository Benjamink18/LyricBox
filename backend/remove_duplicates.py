#!/usr/bin/env python3
"""
Remove duplicate songs from the database.
Keeps the first occurrence of each song (by title + artist).
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def remove_duplicates():
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    print("🔍 Checking for duplicate songs...")
    
    # Get all songs
    result = supabase.table('songs').select('id, title, artist').order('created_at').execute()
    
    songs_to_keep = {}
    songs_to_delete = []
    
    for song in result.data:
        key = f"{song['title'].lower()}|{song['artist'].lower()}"
        
        if key in songs_to_keep:
            # This is a duplicate - mark for deletion
            songs_to_delete.append(song['id'])
            print(f"  🗑️  Duplicate: {song['title']} - {song['artist']} (ID: {song['id']})")
        else:
            # First occurrence - keep it
            songs_to_keep[key] = song['id']
    
    print(f"\n📊 Summary:")
    print(f"  Total songs: {len(result.data)}")
    print(f"  Unique songs: {len(songs_to_keep)}")
    print(f"  Duplicates to remove: {len(songs_to_delete)}")
    
    if songs_to_delete:
        print(f"\n🗑️  Deleting {len(songs_to_delete)} duplicates...")
        
        # Delete related data first (rhyme_pairs and song_analysis)
        deleted_count = 0
        for i, song_id in enumerate(songs_to_delete):
            # Delete rhyme pairs
            supabase.table('rhyme_pairs').delete().eq('song_id', song_id).execute()
            # Delete analysis
            supabase.table('song_analysis').delete().eq('song_id', song_id).execute()
            # Delete song
            supabase.table('songs').delete().eq('id', song_id).execute()
            deleted_count += 1
            if (deleted_count % 50 == 0):
                print(f"  Progress: {deleted_count}/{len(songs_to_delete)} deleted...")
        
        print(f"\n✅ Removed {len(songs_to_delete)} duplicate songs!")
        
        # Show final count
        final_result = supabase.table('songs').select('id').execute()
        print(f"📊 Final count: {len(final_result.data)} unique songs")
    else:
        print("\n✅ No duplicates found!")

if __name__ == "__main__":
    remove_duplicates()

