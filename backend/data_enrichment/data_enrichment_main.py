"""
DATA ENRICHMENT MAIN: Orchestrator for enriching song data
Reads songs from CSV and runs them through enrichment modules.
"""

import sys
sys.path.append('..')

from read_songs_csv import read_songs_from_csv
from ug_scraper.ug_scraper_main import scrape_chords


def run_enrichment():
    """
    Data enrichment pipeline orchestrator.
    Processes songs through multiple enrichment steps.
    """
    
    print("\n" + "="*70)
    print("DATA ENRICHMENT PIPELINE")
    print("="*70)
    
    # Step 1: Load songs from CSV
    print("\nStep 1: Loading songs from CSV...")
    songs = read_songs_from_csv('songs_list.csv')
    print(f"  ✓ Loaded {len(songs)} songs")
    
    # Step 2: Scrape chord data from Ultimate Guitar
    print("\nStep 2: Scraping chord data from Ultimate Guitar...")
    chord_results = scrape_chords(songs)
    print(f"  ✓ Chords: {chord_results['successful']}/{chord_results['total']} successful")
    
    # Future steps:
    # Step 3: Fetch Musixmatch metadata (BPM, genres, moods, release date)
    # Step 4: Fetch lyrics from multi-source API
    # Step 5: Generate concepts with Claude AI
    # Step 6: Generate rhyme analysis with Claude AI
    
    # Final summary
    print("\n" + "="*70)
    print("ENRICHMENT COMPLETE")
    print("="*70)
    print(f"Total songs processed: {len(songs)}")
    print(f"Chord data: {chord_results['successful']} successful, {chord_results['failed']} failed")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_enrichment()

