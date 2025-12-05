"""
DATA ENRICHMENT MAIN - Schema V2
Orchestrator for enriching song data with normalized database structure.

Pipeline:
1. CSV → Track, Artist, Peak, Year
2. Musixmatch → Genres  
3. GetSongBPM → BPM + ALL 10 fields
4. Create/Get Artist → artist_id
5. Create/Get Album → album_id
6. Create Song → with foreign keys
7. Genius → Lyrics (REQUIRED - delete if fail)
8. Ultimate Guitar → Chords + Key (update musical_key if found)
"""

import sys
sys.path.append('..')

from read_songs_csv import read_songs_from_csv
from musixmatch.get_track_data import get_track_data
from getsongbpm.get_bpm import get_bpm_data
from create_or_get_artist import create_or_get_artist
from create_or_get_album import create_or_get_album
from create_song_with_metadata import create_song_with_metadata
from delete_song import delete_song
from update_musical_key import update_musical_key
from log_metadata_failures import log_metadata_failure
from genius_scrape.genius_batch import scrape_lyrics_batch
from ug_scraper.ug_scraper_main import scrape_chords


def run_enrichment():
    """
    Data enrichment pipeline with normalized schema.
    """
    
    print("\n" + "="*70)
    print("DATA ENRICHMENT PIPELINE - SCHEMA V2")
    print("="*70)
    
    # Step 1: Load songs from CSV
    print("\nStep 1: Loading songs from CSV...")
    songs = read_songs_from_csv('songs_list.csv')
    print(f"  ✓ Loaded {len(songs)} songs")
    
    # Step 2: Fetch metadata and create songs with normalized structure
    print("\nStep 2: Fetching metadata + creating normalized records...")
    
    songs_created = 0
    songs_failed = 0
    songs_with_metadata = []
    
    for i, song in enumerate(songs, 1):
        artist_name = song['artist']
        track_name = song['track']
        peak = song.get('peak_position')
        first_chart_date = song.get('first_chart_date')  # DATE type
        
        print(f"\n  [{i}/{len(songs)}] {artist_name} - {track_name}")
        
        # Fetch genres from Musixmatch (OPTIONAL - continue if fails)
        genres_data = get_track_data(artist_name, track_name)
        if not genres_data['success']:
            log_metadata_failure(artist_name, track_name, reason="no_genres")
            song_genres = []  # Empty array if not found
            print(f"    ⚠ No genres found - continuing with empty genres")
        else:
            song_genres = genres_data.get('genres')
            print(f"    ✓ Genres: {song_genres}")
        
        # Fetch GetSongBPM data (OPTIONAL - continue if fails)
        bpm_data = get_bpm_data(artist_name, track_name)
        if not bpm_data['success']:
            log_metadata_failure(artist_name, track_name, reason="no_bpm")
            # Set all GetSongBPM fields to None
            bpm = None
            time_signature = None
            musical_key = None
            camelot_key = None
            danceability = None
            acousticness = None
            artist_country = None
            artist_genres = None
            album_title = None
            album_year = None
            print(f"    ⚠ No GetSongBPM data - continuing with NULL values")
        else:
            # Extract ALL GetSongBPM fields
            bpm = bpm_data.get('bpm')
            time_signature = bpm_data.get('time_signature')
            musical_key = bpm_data.get('musical_key')
            camelot_key = bpm_data.get('camelot_key')
            danceability = bpm_data.get('danceability')
            acousticness = bpm_data.get('acousticness')
            artist_country = bpm_data.get('artist_country')
            artist_genres = bpm_data.get('artist_genres')
            album_title = bpm_data.get('album_title')
            album_year = bpm_data.get('album_year')
            print(f"    ✓ GetSongBPM: BPM={bpm}, Dance={danceability}, Acoustic={acousticness}")
        
        # Create or get artist (use empty values if not found)
        artist_id = create_or_get_artist(
            artist_name=artist_name,
            artist_genres=artist_genres if artist_genres else [],  # Empty array if None
            artist_country=artist_country
        )
        
        if not artist_id:
            songs_failed += 1
            print(f"    ✗ Failed to create/get artist")
            continue
        
        # Create or get album (only if album data exists)
        album_id = None
        if album_title:
            album_id = create_or_get_album(
                album_title=album_title,
                album_year=album_year,
                artist_id=artist_id
            )
            if not album_id:
                print(f"    ⚠ Failed to create/get album - continuing without album")
        else:
            print(f"    ⚠ No album data available")
        
        # Create song with ALL metadata
        result = create_song_with_metadata(
            track_name=track_name,
            artist_id=artist_id,
            album_id=album_id,
            peak_position=peak,
            first_chart_date=first_chart_date,
            song_genres=song_genres,
            bpm=bpm,
            time_signature=time_signature,
            musical_key=musical_key,
            camelot_key=camelot_key,
            danceability=danceability,
            acousticness=acousticness
        )
        
        if result['success']:
            songs_created += 1
            songs_with_metadata.append({
                'artist': artist_name,
                'track': track_name,
                'song_id': result['song_id']
            })
            print(f"    ✓ Song created (genres: {len(song_genres)}, BPM: {bpm}, Dance: {danceability}, Acoustic: {acousticness})")
        else:
            songs_failed += 1
            print(f"    ✗ Failed to create song: {result['error']}")
    
    print(f"\n  Metadata Results:")
    print(f"    ✓ {songs_created} songs created")
    print(f"    ✗ {songs_failed} failed")
    
    # Step 3: Fetch lyrics from Genius (REQUIRED - delete if fail)
    if songs_with_metadata:
        print(f"\nStep 3: Scraping lyrics from Genius (REQUIRED)...")
        print(f"  Processing {len(songs_with_metadata)} songs...")
        
        # Prepare songs for lyrics scraper
        songs_for_lyrics = [
            {'artist': s['artist'], 'track': s['track'], 'song_id': s['song_id']}
            for s in songs_with_metadata
        ]
        
        lyrics_results = scrape_lyrics_batch(songs_for_lyrics)
        
        # DELETE songs that failed to get lyrics
        if lyrics_results['failed'] > 0:
            print(f"\n  Deleting {lyrics_results['failed']} songs without lyrics from database...")
            
            for song_id, artist, track in lyrics_results['failed_song_ids']:
                delete_song(song_id, artist, track)
            
        print(f"  ✓ Lyrics: {lyrics_results['successful']}/{lyrics_results['total']} successful")
        print(f"  ✗ Deleted: {lyrics_results['failed']} songs without lyrics")
        
        # Update songs_with_metadata to only include songs that got lyrics
        deleted_song_ids = {song_id for song_id, _, _ in lyrics_results['failed_song_ids']}
        songs_with_metadata = [
            s for s in songs_with_metadata if s['song_id'] not in deleted_song_ids
        ]
    else:
        print("\n  No songs with metadata - skipping lyrics scraping")
        lyrics_results = {'successful': 0, 'failed': 0, 'total': 0}
    
    # Step 4: Scrape chords + key from Ultimate Guitar
    if songs_with_metadata:
        print(f"\nStep 4: Scraping chords + key from Ultimate Guitar...")
        print(f"  Processing {len(songs_with_metadata)} songs...")
        
        songs_for_chords = [
            {'artist': s['artist'], 'track': s['track'], 'song_id': s['song_id']}
            for s in songs_with_metadata
        ]
        
        chord_results = scrape_chords(songs_for_chords)
        
        # Update musical_key for songs where UG tonality was found
        # (UG tonality is more accurate than GetSongBPM since it's from actual chords)
        if chord_results.get('songs_with_key'):
            print(f"\n  Updating musical_key for songs with UG tonality...")
            for song_id, tonality in chord_results['songs_with_key']:
                update_musical_key(song_id, tonality)
        
        print(f"  ✓ Chords: {chord_results['successful']}/{chord_results['total']} successful")
    else:
        print("\n  No songs with metadata - skipping chord scraping")
        chord_results = {'successful': 0, 'failed': 0, 'total': 0}
    
    # Final summary
    print("\n" + "="*70)
    print("ENRICHMENT COMPLETE")
    print("="*70)
    print(f"Total songs processed: {len(songs)}")
    print(f"Songs created: {songs_created} successful, {songs_failed} failed")
    print(f"Lyrics: {lyrics_results['successful']} successful, {lyrics_results['failed']} failed (deleted)")
    print(f"Chords: {chord_results['successful']} successful, {chord_results['failed']} failed")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_enrichment()
