"""
DATA ENRICHMENT MAIN: Orchestrator for enriching song data
Reads songs from CSV and runs them through enrichment modules.
"""

import sys
sys.path.append('..')

from read_songs_csv import read_songs_from_csv
from musixmatch.get_track_data import get_track_data
from musicbrainz.get_metadata import get_metadata
from create_song_with_metadata import create_song_with_metadata
from log_metadata_failures import log_metadata_failure
from log_musicbrainz_partial import log_musicbrainz_partial
from genius_scrape.genius_batch import scrape_lyrics_batch
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
    
    # STEPS 2 & 3 COMMENTED OUT FOR TESTING CHORDS ONLY
    # Mock data for testing chord scraper
    songs_with_metadata = [
        {'artist': s['artist'], 'track': s['track'], 'song_id': 'mock-id'}
        for s in songs
    ]
    metadata_success = len(songs)
    metadata_failed = 0
    musicbrainz_partial = 0
    lyrics_results = {'successful': len(songs), 'failed': 0, 'total': len(songs)}
    
    print(f"\n  [SKIPPED] Step 2: Metadata fetching")
    print(f"  [SKIPPED] Step 3: Lyrics scraping")
    
    # # Step 2: Fetch metadata and create songs in database
    # print("\nStep 2: Fetching metadata (Musixmatch → MusicBrainz fallback)...")
    # 
    # metadata_success = 0
    # metadata_failed = 0
    # musicbrainz_partial = 0
    # songs_with_metadata = []
    # 
    # for i, song in enumerate(songs, 1):
    #     artist = song['artist']
    #     track = song['track']
    #     peak = song.get('peak_position')
    #     
    #     print(f"  [{i}/{len(songs)}] {artist} - {track}")
    #     
    #     # Try Musixmatch first
    #     metadata = get_track_data(artist, track)
    #     
    #     # If Musixmatch fails, try MusicBrainz
    #     if not metadata['success']:
    #         print(f"    Musixmatch failed, trying MusicBrainz...")
    #         metadata = get_metadata(artist, track)
    #         
    #         if metadata['success']:
    #             # MusicBrainz succeeded (partial data)
    #             musicbrainz_partial += 1
    #             log_musicbrainz_partial(artist, track)
    #     
    #     # If both failed, log and skip
    #     if not metadata['success']:
    #         log_metadata_failure(artist, track)
    #         metadata_failed += 1
    #         print(f"    ✗ No metadata found - skipped")
    #         continue
    #     
    #     # Create song in database
    #     result = create_song_with_metadata(artist, track, peak, metadata)
    #     
    #     if result['success']:
    #         metadata_success += 1
    #         songs_with_metadata.append({
    #             'artist': artist,
    #             'track': track,
    #             'song_id': result['song_id']
    #         })
    #         print(f"    ✓ Song created in database")
    #     else:
    #         metadata_failed += 1
    #         print(f"    ✗ Failed to create song: {result['error']}")
    # 
    # print(f"\n  Metadata Results:")
    # print(f"    ✓ {metadata_success} songs created")
    # print(f"    ⚠ {musicbrainz_partial} using MusicBrainz (partial metadata)")
    # print(f"    ✗ {metadata_failed} failed")
    # 
    # # Step 3: Fetch lyrics from Genius
    # # Only scrape lyrics for songs that made it into the database
    # if songs_with_metadata:
    #     print(f"\nStep 3: Scraping lyrics from Genius.com...")
    #     print(f"  Processing {len(songs_with_metadata)} songs with metadata...")
    #     
    #     # Convert to format expected by Genius scraper
    #     songs_for_lyrics = [
    #         {'artist': s['artist'], 'track': s['track']}
    #         for s in songs_with_metadata
    #     ]
    #     
    #     lyrics_results = scrape_lyrics_batch(songs_for_lyrics)
    #     print(f"  ✓ Lyrics: {lyrics_results['successful']}/{lyrics_results['total']} successful")
    # else:
    #     print("\n  No songs with metadata - skipping lyrics scraping")
    #     lyrics_results = {'successful': 0, 'failed': 0, 'total': 0}
    
    # Step 4: Scrape chord data from Ultimate Guitar
    # Only scrape chords for songs that made it into the database
    if songs_with_metadata:
        print(f"\nStep 4: Scraping chord data from Ultimate Guitar...")
        print(f"  Processing {len(songs_with_metadata)} songs with metadata...")
        
        # Convert to format expected by UG scraper
        songs_for_chords = [
            {'artist': s['artist'], 'track': s['track']}
            for s in songs_with_metadata
        ]
        
        chord_results = scrape_chords(songs_for_chords)
        print(f"  ✓ Chords: {chord_results['successful']}/{chord_results['total']} successful")
    else:
        print("\n  No songs with metadata - skipping chord scraping")
        chord_results = {'successful': 0, 'failed': 0, 'total': 0}
    
    # Final summary
    print("\n" + "="*70)
    print("ENRICHMENT COMPLETE")
    print("="*70)
    print(f"Total songs processed: {len(songs)}")
    print(f"Metadata: {metadata_success} successful, {metadata_failed} failed")
    if musicbrainz_partial > 0:
        print(f"  → {musicbrainz_partial} using MusicBrainz (see musicbrainz_partial_metadata.txt)")
    print(f"Lyrics: {lyrics_results['successful']} successful, {lyrics_results['failed']} failed")
    print(f"Chord data: {chord_results['successful']} successful, {chord_results['failed']} failed")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_enrichment()

