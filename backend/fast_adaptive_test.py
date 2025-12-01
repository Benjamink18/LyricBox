#!/usr/bin/env python3
"""
FAST adaptive test - multi-stage increments.
Strategy:
1. Start at 60 (we know this works), jump by 50 until it breaks
2. Go back 50, jump by 25 until it breaks  
3. Go back 25, jump by 10 until it breaks
4. Go back 10, jump by 1 until it breaks
Result: Find optimal in ~10-15 tests instead of 50+
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


class FastAdaptiveTest:
    """Multi-stage increment strategy for fast optimal batch finding."""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.lyrics_client = MultiSourceLyricsClient()
        self.analyzer = SongAnalyzer()
        
        self.songs = self._load_songs()
        self.batches_per_test = 1  # Single batch per test = maximum speed!
        
        # Multi-stage increments
        self.start_size = 60  # We know 60 works from previous test
        self.increment_stages = [
            {"increment": 50, "name": "Coarse (50)"},
            {"increment": 25, "name": "Medium (25)"},
            {"increment": 10, "name": "Fine (10)"},
            {"increment": 1, "name": "Precision (1)"}
        ]
        
        self.results = {
            "test_start": datetime.now().isoformat(),
            "batch_tests": []
        }
    
    def _load_songs(self) -> List[Dict[str, str]]:
        """Load songs from CSV."""
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
        print(f"📋 Loaded {len(songs)} songs")
        return songs
    
    async def analyze_song(self, song: Dict[str, str], song_num: int, total: int) -> Dict[str, Any]:
        """Analyze a single song."""
        title = song["title"]
        artist = song["artist"]
        
        try:
            lyrics_result = self.lyrics_client.get_lyrics(artist, title)
            
            if not lyrics_result.success:
                return {
                    "success": False,
                    "error": lyrics_result.error,
                    "song": title,
                    "rate_limit": "429" in str(lyrics_result.error)
                }
            
            analysis = self.analyzer.analyze(lyrics_result.lyrics, title, artist)
            
            if not analysis:
                return {
                    "success": False,
                    "error": "Analysis failed",
                    "song": title,
                    "rate_limit": False
                }
            
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
        """Save to database."""
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
            tasks = [self.analyze_song(song, start_idx + i + 1, len(self.songs)) for i, song in enumerate(songs_subset)]
            results = await asyncio.gather(*tasks)
            
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
        """Run fast multi-stage adaptive test."""
        print("=" * 60)
        print("🚀 FAST MULTI-STAGE ADAPTIVE TEST")
        print("=" * 60)
        print(f"\nStrategy:")
        print(f"  Start at {self.start_size} (known working)")
        for stage in self.increment_stages:
            print(f"  → {stage['name']}: increment by {stage['increment']}")
        print(f"  Only {self.batches_per_test} batches per test = ULTRA FAST!")
        print()
        
        test_start = time.time()
        song_offset = 0
        last_successful = self.start_size
        
        # Multi-stage search
        for stage_idx, stage in enumerate(self.increment_stages):
            increment = stage["increment"]
            stage_name = stage["name"]
            
            print(f"\n{'🔍' if stage_idx == 0 else '🎯'} STAGE {stage_idx + 1}: {stage_name}")
            print("=" * 60)
            
            current_size = last_successful + increment
            
            while True:
                result = await self.test_batch_size(current_size, song_offset)
                self.results["batch_tests"].append(result)
                song_offset += result["total_songs"]
                
                if result["rate_limited"]:
                    print(f"\n💥 Hit rate limit at {current_size} songs/batch")
                    print(f"✅ Last successful in this stage: {last_successful}")
                    break
                else:
                    last_successful = current_size
                    next_size = current_size + increment
                    print(f"✅ {current_size} works! Trying {next_size}...")
                    current_size = next_size
            
            # If this is the last stage, we found the optimal
            if stage_idx == len(self.increment_stages) - 1:
                optimal_size = last_successful
                print(f"\n🎯 OPTIMAL BATCH SIZE FOUND: {optimal_size} songs/batch")
                self.results["optimal_batch_size"] = optimal_size
                break
            
            # Otherwise, back up by this increment and move to next stage
            print(f"\n→ Moving to next stage from {last_successful}...")
        
        test_duration = time.time() - test_start
        self.results["test_end"] = datetime.now().isoformat()
        self.results["total_duration_seconds"] = test_duration
        
        self._print_summary()
        self._save_results()
    
    def _print_summary(self):
        """Print summary."""
        print("\n" + "=" * 60)
        print("🎉 FAST ADAPTIVE TEST COMPLETE!")
        print("=" * 60)
        
        optimal = self.results.get("optimal_batch_size", 0)
        duration = self.results.get("total_duration_seconds", 0)
        
        print(f"\n🎯 OPTIMAL BATCH SIZE: {optimal} songs/batch")
        print(f"⏱️  Test duration: {int(duration // 60)}m {int(duration % 60)}s")
        print(f"📊 Total tests run: {len(self.results['batch_tests'])}")
        
        print(f"\n📈 All tested batch sizes:")
        for test in self.results["batch_tests"]:
            status = "✅" if not test["rate_limited"] else "❌"
            print(f"  {status} {test['batch_size']:3d} songs: {test['avg_duration']:.1f}s avg")
        
        total_songs = len(self.songs)
        if optimal > 0:
            successful_tests = [t for t in self.results["batch_tests"] if not t["rate_limited"]]
            if successful_tests:
                avg_batch_time = successful_tests[-1]["avg_duration"]
                estimated_batches = (total_songs + optimal - 1) // optimal
                estimated_time = estimated_batches * avg_batch_time
                
                print(f"\n💡 FULL IMPORT ESTIMATE:")
                print(f"  Batch size: {optimal} songs")
                print(f"  Total batches: {estimated_batches}")
                print(f"  Estimated time: ~{estimated_time / 3600:.1f} hours for {total_songs} songs")
        
        print(f"\n📝 Results saved to: adaptive_test_results.json")
        print("=" * 60)
    
    def _save_results(self):
        """Save results."""
        with open("adaptive_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)


async def main():
    tester = FastAdaptiveTest()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())

