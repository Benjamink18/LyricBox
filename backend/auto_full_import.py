#!/usr/bin/env python3
"""
Automatic full import - waits for adaptive test, then imports all songs.
"""

import os
import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

from lyrics_client import MultiSourceLyricsClient
from song_analyzer import SongAnalyzer

load_dotenv()


class AutoFullImport:
    """Automatically import all songs after adaptive test."""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.lyrics_client = MultiSourceLyricsClient()
        self.analyzer = SongAnalyzer()
        
        # Results
        self.import_log = {
            "start_time": datetime.now().isoformat(),
            "batches": [],
            "errors": [],
            "total_songs": 0,
            "total_pairs": 0
        }
    
    def wait_for_adaptive_test(self):
        """Wait for adaptive test to finish."""
        print("⏳ Waiting for adaptive test to complete...")
        print("   (Checking for adaptive_test_results.json)")
        
        while not os.path.exists("adaptive_test_results.json"):
            time.sleep(30)
            print("   Still waiting...")
        
        print("✅ Adaptive test complete!")
        time.sleep(5)  # Give it time to finish writing
    
    def get_optimal_batch_size(self) -> int:
        """Read optimal batch size from test results."""
        with open("adaptive_test_results.json", "r") as f:
            results = json.load(f)
        
        optimal = results.get("optimal_batch_size", 20)
        safe_size = max(1, optimal - 1)  # Subtract 1 for safety
        
        print(f"\n📊 Adaptive test found: {optimal} songs/batch")
        print(f"🛡️  Using safe size: {safe_size} songs/batch (optimal - 1)")
        
        return safe_size
    
    def clear_database(self):
        """Clear the database for fresh import."""
        print("\n🗑️  Clearing database...")
        
        self.supabase.table('rhyme_pairs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        self.supabase.table('song_analysis').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        self.supabase.table('songs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        print("✅ Database cleared!")
    
    def load_all_songs(self) -> List[Dict[str, str]]:
        """Load all songs from Billboard CSV."""
        df = pd.read_csv("billboard_2025_clean.csv")
        songs = []
        
        for _, row in df.iterrows():
            detailed_genres = None
            if pd.notna(row.get("all_genres")):
                detailed_genres = [g.strip() for g in str(row["all_genres"]).split(';')]
            
            songs.append({
                "title": row["title"],
                "artist": row["artist"],
                "year": 2025,
                "billboard_rank": int(row["peak_position"]) if pd.notna(row.get("peak_position")) else None,
                "genre": row.get("main_genre", "Unknown"),
                "main_genre": row.get("main_genre", "Unknown"),
                "detailed_genres": detailed_genres,
                "genre_source": row.get("genre_source", None)
            })
        
        print(f"\n📋 Loaded {len(songs)} songs to import")
        return songs
    
    async def analyze_song(self, song: Dict[str, str], song_num: int, total: int) -> Dict[str, Any]:
        """Analyze a single song."""
        title = song["title"]
        artist = song["artist"]
        
        try:
            # Fetch lyrics
            lyrics_result = self.lyrics_client.get_lyrics(artist, title)
            
            if not lyrics_result.success:
                error_msg = f"❌ [{song_num}/{total}] {title} - {lyrics_result.error}"
                print(error_msg)
                return {"success": False, "error": lyrics_result.error, "song": title}
            
            # Analyze with Claude
            analysis = self.analyzer.analyze(lyrics_result.lyrics, title, artist)
            
            if not analysis:
                error_msg = f"❌ [{song_num}/{total}] {title} - Analysis failed"
                print(error_msg)
                return {"success": False, "error": "Analysis failed", "song": title}
            
            # Save to database
            self._save_to_database(song, lyrics_result, analysis)
            
            pairs_count = len(analysis.rhyme_pairs)
            print(f"✅ [{song_num}/{total}] {title} - {pairs_count} rhyme pairs ({lyrics_result.source})")
            
            return {
                "success": True,
                "song": title,
                "pairs": pairs_count,
                "source": lyrics_result.source
            }
            
        except Exception as e:
            error_msg = f"💥 [{song_num}/{total}] {title} - {str(e)}"
            print(error_msg)
            return {"success": False, "error": str(e), "song": title}
    
    def _save_to_database(self, song: Dict, lyrics_result: Any, analysis: Any):
        """Save song and analysis to database."""
        # Insert song
        song_data = {
            "title": song["title"],
            "artist": song["artist"],
            "lyrics_raw": lyrics_result.lyrics,
            "year": song.get("year"),
            "billboard_rank": song.get("billboard_rank"),
            "genre": song.get("genre"),
            "main_genre": song.get("main_genre"),
            "detailed_genres": song.get("detailed_genres"),
            "genre_source": song.get("genre_source"),
            "lyrics_source": lyrics_result.source
        }
        
        song_result = self.supabase.table('songs').insert(song_data).execute()
        song_id = song_result.data[0]['id']
        
        # Insert analysis
        analysis_data = {
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
        
        self.supabase.table('song_analysis').insert(analysis_data).execute()
        
        # Insert rhyme pairs
        if analysis.rhyme_pairs:
            pairs_data = []
            for pair in analysis.rhyme_pairs:
                pairs_data.append({
                    "song_id": song_id,
                    "word": pair.word,
                    "rhymes_with": pair.rhymes_with,
                    "rhyme_type": pair.rhyme_type,
                    "word_line": pair.word_line,
                    "rhymes_with_line": pair.rhymes_with_line
                })
            
            for i in range(0, len(pairs_data), 50):
                batch = pairs_data[i:i+50]
                self.supabase.table('rhyme_pairs').insert(batch).execute()
    
    async def import_batch(self, batch_num: int, songs: List[Dict], batch_size: int, total_songs: int):
        """Import a batch of songs."""
        start_time = time.time()
        batch_start_idx = (batch_num - 1) * batch_size + 1
        
        print(f"\n{'='*60}")
        print(f"BATCH {batch_num} - Songs {batch_start_idx} to {batch_start_idx + len(songs) - 1}")
        print(f"{'='*60}")
        
        # Process songs in parallel
        tasks = [
            self.analyze_song(song, batch_start_idx + i, total_songs)
            for i, song in enumerate(songs)
        ]
        results = await asyncio.gather(*tasks)
        
        # Track results
        successful = sum(1 for r in results if r.get("success", False))
        total_pairs = sum(r.get("pairs", 0) for r in results if r.get("success", False))
        errors = [r for r in results if not r.get("success", False)]
        
        duration = time.time() - start_time
        
        batch_info = {
            "batch_num": batch_num,
            "songs_attempted": len(songs),
            "successful": successful,
            "failed": len(errors),
            "total_pairs": total_pairs,
            "duration": duration
        }
        
        self.import_log["batches"].append(batch_info)
        self.import_log["total_songs"] += successful
        self.import_log["total_pairs"] += total_pairs
        self.import_log["errors"].extend(errors)
        
        print(f"\n✅ Batch {batch_num} complete: {successful}/{len(songs)} successful in {duration:.1f}s")
        print(f"   Total progress: {self.import_log['total_songs']}/{total_songs} songs, {self.import_log['total_pairs']} pairs")
        
        if errors:
            print(f"   ⚠️  {len(errors)} errors in this batch")
    
    async def run_full_import(self):
        """Run the complete import process."""
        print("=" * 60)
        print("🚀 AUTOMATIC FULL IMPORT")
        print("=" * 60)
        
        # Step 1: Wait for adaptive test
        self.wait_for_adaptive_test()
        
        # Step 2: Get optimal batch size
        batch_size = self.get_optimal_batch_size()
        
        # Step 3: Clear database
        self.clear_database()
        
        # Step 4: Load all songs
        all_songs = self.load_all_songs()
        total_songs = len(all_songs)
        total_batches = (total_songs + batch_size - 1) // batch_size
        
        print(f"\n📦 Will process {total_batches} batches of {batch_size} songs")
        print(f"⏱️  Estimated time: ~{total_batches * 8 / 60:.1f} hours")
        print(f"\nStarting import at {datetime.now().strftime('%I:%M %p')}")
        print("=" * 60)
        
        import_start = time.time()
        
        # Step 5: Import all batches
        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_songs)
            batch_songs = all_songs[start_idx:end_idx]
            
            await self.import_batch(batch_num, batch_songs, batch_size, total_songs)
            
            # Save progress after each batch
            self._save_progress()
        
        # Final summary
        total_duration = time.time() - import_start
        self.import_log["end_time"] = datetime.now().isoformat()
        self.import_log["total_duration_seconds"] = total_duration
        
        self._print_final_summary(total_duration)
        self._save_progress()
    
    def _save_progress(self):
        """Save current progress to file."""
        with open("full_import_log.json", "w") as f:
            json.dump(self.import_log, f, indent=2)
    
    def _print_final_summary(self, duration: float):
        """Print final import summary."""
        print("\n" + "=" * 60)
        print("🎉 FULL IMPORT COMPLETE!")
        print("=" * 60)
        
        print(f"\n📊 FINAL STATS:")
        print(f"   ✅ Successfully imported: {self.import_log['total_songs']} songs")
        print(f"   🎯 Total rhyme pairs: {self.import_log['total_pairs']}")
        print(f"   ❌ Failed: {len(self.import_log['errors'])} songs")
        print(f"   ⏱️  Total time: {duration / 3600:.2f} hours")
        
        if self.import_log['errors']:
            print(f"\n⚠️  ERRORS ({len(self.import_log['errors'])}):")
            for error in self.import_log['errors'][:10]:
                print(f"   - {error['song']}: {error['error']}")
            if len(self.import_log['errors']) > 10:
                print(f"   ... and {len(self.import_log['errors']) - 10} more")
        
        print(f"\n📝 Full log saved to: full_import_log.json")
        print(f"✅ Finished at {datetime.now().strftime('%I:%M %p')}")
        print("=" * 60)


async def main():
    importer = AutoFullImport()
    await importer.run_full_import()


if __name__ == "__main__":
    asyncio.run(main())

