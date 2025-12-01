#!/usr/bin/env python3
"""
Smart adaptive batch test - finds optimal batch size quickly.
Strategy:
1. Start at 20, increment by 5 until it breaks
2. Go back 5, increment by 1 until it breaks
3. We have our optimal size
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


class SmartAdaptiveBatchTest:
    """Smart batch size finder with minimal testing."""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.lyrics_client = MultiSourceLyricsClient()
        self.analyzer = SongAnalyzer()
        
        # Load Billboard data
        self.songs = self._load_songs()
        
        # Test configuration - MINIMAL testing
        self.batches_per_test = 2  # Only 2 batches per size
        self.coarse_increment = 5  # Start with 5-song jumps
        self.fine_increment = 1    # Then 1-song precision
        self.start_size = 20       # Start at 20 songs
        
        # Results tracking
        self.results = {
            "test_start": datetime.now().isoformat(),
            "phase": "coarse",  # coarse -> fine
            "batch_tests": []
        }
    
    def _load_songs(self) -> List[Dict[str, str]]:
        """Load songs from Billboard CSV."""
        try:
            df = pd.read_csv("billboard_2025_clean.csv")
            songs = []
            for _, row in df.iterrows():
                # Convert all_genres string to array
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
            print(f"📋 Loaded {len(songs)} songs from Billboard data")
            return songs
        except Exception as e:
            print(f"❌ Error loading songs: {e}")
            return []
    
    async def analyze_song(self, song: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single song."""
        title = song["title"]
        artist = song["artist"]
        
        try:
            # Fetch lyrics
            lyrics_result = self.lyrics_client.get_lyrics(artist, title)
            
            if not lyrics_result.success:
                return {
                    "success": False,
                    "error": lyrics_result.error,
                    "song": title,
                    "rate_limit": "429" in str(lyrics_result.error)
                }
            
            # Analyze with Claude
            analysis = self.analyzer.analyze(
                lyrics_result.lyrics,
                title,
                artist
            )
            
            if not analysis:
                return {
                    "success": False,
                    "error": "Analysis failed",
                    "song": title,
                    "rate_limit": False
                }
            
            # Save to database
            self._save_to_database(song, lyrics_result, analysis)
            
            return {
                "success": True,
                "song": title,
                "source": lyrics_result.source,
                "rhyme_pairs": len(analysis.rhyme_pairs),
                "rate_limit": False
            }
            
        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "rate" in error_str.lower()
            
            return {
                "success": False,
                "error": error_str,
                "song": title,
                "rate_limit": is_rate_limit
            }
    
    def _save_to_database(self, song: Dict, lyrics_result: Any, analysis: Any):
        """Save song and analysis to database."""
        try:
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
            
            # Insert rhyme pairs in batches
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
                
                # Insert in batches of 50
                for i in range(0, len(pairs_data), 50):
                    batch = pairs_data[i:i+50]
                    self.supabase.table('rhyme_pairs').insert(batch).execute()
            
        except Exception as e:
            print(f"⚠️  Database error for {song['title']}: {e}")
    
    async def test_batch_size(self, batch_size: int, song_offset: int) -> Dict[str, Any]:
        """Test a batch size with 2 batches."""
        print(f"\n{'='*60}")
        print(f"Testing batch size: {batch_size}")
        print(f"{'='*60}")
        
        batch_results = []
        rate_limited = False
        
        for batch_num in range(1, self.batches_per_test + 1):
            start_idx = song_offset + (batch_num - 1) * batch_size
            end_idx = start_idx + batch_size
            
            if start_idx >= len(self.songs):
                print(f"\n⚠️  Ran out of songs to test")
                break
            
            songs_subset = self.songs[start_idx:end_idx]
            
            print(f"\nBatch {batch_num}/{self.batches_per_test} - Songs {start_idx + 1} to {end_idx}")
            
            start_time = time.time()
            
            # Process songs in parallel
            tasks = [self.analyze_song(song) for song in songs_subset]
            results = await asyncio.gather(*tasks)
            
            # Check for rate limits
            rate_limited = any(r.get("rate_limit", False) for r in results)
            successful = sum(1 for r in results if r.get("success", False))
            total_pairs = sum(r.get("rhyme_pairs", 0) for r in results if r.get("success", False))
            
            duration = time.time() - start_time
            
            print(f"Completed in {duration:.1f}s ({successful}/{len(songs_subset)} successful)")
            
            batch_results.append({
                "batch_num": batch_num,
                "duration": duration,
                "successful": successful,
                "total": len(songs_subset),
                "total_pairs": total_pairs,
                "rate_limited": rate_limited
            })
            
            if rate_limited:
                print(f"\n❌ RATE LIMIT HIT at batch size {batch_size}")
                break
        
        avg_duration = sum(b["duration"] for b in batch_results) / len(batch_results) if batch_results else 0
        total_songs = sum(b["successful"] for b in batch_results)
        
        return {
            "batch_size": batch_size,
            "rate_limited": rate_limited,
            "avg_duration": avg_duration,
            "total_songs": total_songs,
            "batches_completed": len(batch_results)
        }
    
    async def run_test(self):
        """Run smart adaptive test."""
        print("=" * 60)
        print("🧪 SMART ADAPTIVE BATCH SIZE TEST")
        print("=" * 60)
        print(f"\nStrategy:")
        print(f"  Phase 1: Start at {self.start_size}, increment by {self.coarse_increment} until it breaks")
        print(f"  Phase 2: Go back {self.coarse_increment}, increment by {self.fine_increment} for precision")
        print(f"  Only {self.batches_per_test} batches per test = FAST!")
        print()
        
        test_start = time.time()
        song_offset = 0  # Track where we are in the song list
        
        # PHASE 1: Coarse search (increments of 5)
        print("\n🔍 PHASE 1: Coarse search (steps of 5)")
        current_size = self.start_size
        last_successful_size = self.start_size
        
        while True:
            result = await self.test_batch_size(current_size, song_offset)
            self.results["batch_tests"].append(result)
            song_offset += result["total_songs"]
            
            if result["rate_limited"]:
                print(f"\n💥 Hit rate limit at {current_size} songs/batch")
                print(f"✅ Last successful: {last_successful_size} songs/batch")
                break
            else:
                last_successful_size = current_size
                current_size += self.coarse_increment
                print(f"✅ {last_successful_size} works! Trying {current_size}...")
        
        # PHASE 2: Fine search (increments of 1)
        print(f"\n🎯 PHASE 2: Fine search from {last_successful_size}")
        current_size = last_successful_size + 1
        
        while True:
            result = await self.test_batch_size(current_size, song_offset)
            self.results["batch_tests"].append(result)
            song_offset += result["total_songs"]
            
            if result["rate_limited"]:
                optimal_size = current_size - 1
                print(f"\n🎯 OPTIMAL BATCH SIZE FOUND: {optimal_size} songs/batch")
                self.results["optimal_batch_size"] = optimal_size
                break
            else:
                print(f"✅ {current_size} works! Trying {current_size + 1}...")
                current_size += 1
        
        test_duration = time.time() - test_start
        self.results["test_end"] = datetime.now().isoformat()
        self.results["total_duration_seconds"] = test_duration
        
        self._print_summary()
        self._save_results()
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("🎉 ADAPTIVE TEST COMPLETE!")
        print("=" * 60)
        
        optimal = self.results.get("optimal_batch_size", 0)
        duration = self.results.get("total_duration_seconds", 0)
        
        print(f"\n🎯 OPTIMAL BATCH SIZE: {optimal} songs/batch")
        print(f"⏱️  Test duration: {int(duration // 60)}m {int(duration % 60)}s")
        
        print(f"\n📊 All tested batch sizes:")
        for test in self.results["batch_tests"]:
            status = "✅" if not test["rate_limited"] else "❌"
            print(f"  {status} {test['batch_size']} songs: {test['avg_duration']:.1f}s avg ({test['total_songs']} songs processed)")
        
        # Estimate full import time
        total_songs = len(self.songs)
        if optimal > 0:
            # Get avg time from last successful batch
            successful_tests = [t for t in self.results["batch_tests"] if not t["rate_limited"]]
            if successful_tests:
                avg_batch_time = successful_tests[-1]["avg_duration"]
                estimated_batches = (total_songs + optimal - 1) // optimal
                estimated_time = estimated_batches * avg_batch_time
                
                print(f"\n💡 RECOMMENDATION FOR FULL IMPORT:")
                print(f"  Batch size: {optimal} songs")
                print(f"  Total batches: {estimated_batches}")
                print(f"  Estimated time: ~{estimated_time / 3600:.1f} hours for {total_songs} songs")
        
        print(f"\n📝 Results saved to: adaptive_test_results.json")
        print("=" * 60)
        print()
    
    def _save_results(self):
        """Save results to JSON file."""
        with open("adaptive_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)


async def main():
    tester = SmartAdaptiveBatchTest()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())
