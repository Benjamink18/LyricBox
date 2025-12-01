#!/usr/bin/env python3
"""Import the 84 missing songs for demo."""

import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
from song_analyzer import SongAnalyzer
from lyrics_client import MultiSourceLyricsClient

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

analyzer = SongAnalyzer()
lyrics_client = MultiSourceLyricsClient()

# Load clean dataset
df = pd.read_csv("billboard_2025_clean.csv")

# Get songs already in DB
existing = supabase.table('songs').select('title, artist').execute()
existing_keys = {(s['title'].lower().strip(), s['artist'].lower().strip()) for s in existing.data}

# Find missing songs
missing = []
for _, row in df.iterrows():
    key = (row['title'].lower().strip(), row['artist'].lower().strip())
    if key not in existing_keys:
        missing.append(row)

print(f"🚀 Importing {len(missing)} missing songs")
print(f"⏱️  Estimated time: ~{len(missing) * 30 / 60:.0f} minutes")
print()

async def analyze_song(song_data, idx, total):
    """Analyze one song."""
    title = song_data['title']
    artist = song_data['artist']
    
    print(f"[{idx}/{total}] {title} - {artist}")
    
    try:
        # Get lyrics
        lyrics_result = lyrics_client.get_lyrics(artist, title)
        if not lyrics_result.success:
            print(f"  ❌ No lyrics found")
            return False
        
        # Analyze
        analysis = analyzer.analyze(lyrics_result.lyrics, title, artist)
        if not analysis:
            print(f"  ❌ Analysis failed")
            return False
        
        # Save to database
        song_db = {
            "title": title,
            "artist": artist,
            "lyrics_raw": lyrics_result.lyrics,
            "year": int(song_data.get("release_year", 2025)),
            "billboard_rank": int(song_data.get("peak_position", 100)),
            "genre": song_data.get("genre", "Unknown"),
            "lyrics_source": lyrics_result.source
        }
        
        song_result = supabase.table('songs').insert(song_db).execute()
        song_id = song_result.data[0]['id']
        
        # Save analysis
        analysis_db = {
            "song_id": song_id,
            "concept_summary": analysis.concept_summary,
            "section_breakdown": analysis.section_breakdown,
            "themes": analysis.themes,
            "imagery": analysis.imagery,
            "tone": analysis.tone,
            "universal_scenarios": analysis.universal_scenarios,
            "alternative_titles": analysis.alternative_titles,
            "thematic_vocabulary": analysis.thematic_vocabulary
        }
        supabase.table('song_analysis').insert(analysis_db).execute()
        
        # Save rhyme pairs
        if analysis.rhyme_pairs:
            pairs_db = [{
                "song_id": song_id,
                "word1": p.word1,
                "word2": p.word2,
                "rhyme_type": p.rhyme_type,
                "line1": p.line1,
                "line2": p.line2,
                "line1_number": p.line1_number,
                "line2_number": p.line2_number,
                "is_first_occurrence": p.is_first_occurrence
            } for p in analysis.rhyme_pairs[:500]]
            
            supabase.table('rhyme_pairs').insert(pairs_db).execute()
        
        print(f"  ✅ Complete ({len(analysis.rhyme_pairs)} rhyme pairs)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

async def main():
    tasks = [analyze_song(song, i+1, len(missing)) for i, song in enumerate(missing)]
    results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if r)
    print()
    print("=" * 60)
    print(f"✅ Imported {successful}/{len(missing)} songs")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
