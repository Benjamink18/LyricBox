"""
SCRAPE SONG: Core scraping logic for a single song
===================================================
Reusable function that takes an artist/track and scrapes chord data.
Designed to be called in a loop for batch processing.
Returns the raw chord data - does NOT save to database.
"""

from .search import search_song
from .find_official import find_official_tabs
from .click_tab import click_tab
from .handle_cookies import handle_cookies
from .click_chords import click_chords
from .extract_tonality import extract_tonality
from .extract_capo_and_tuning import extract_capo_and_tuning
from .check_tuning import is_standard_tuning, get_tuning_name
from .extract_chords import extract_chords
from .transpose_by_capo import transpose_chord_list
from .process_chords import process_chords
from utils.human_behavior import act_human
from .log_missing_chords import log_missing_chords
from .log_alternate_tuning import log_alternate_tuning


def scrape_song(page, artist_name, track_name):
    """
    Scrape chord data for a single song from Ultimate Guitar.
    
    Args:
        page: Browser page (already logged in to Ultimate Guitar)
        artist_name: Artist name (e.g., "D'Angelo")
        track_name: Track name (e.g., "Spanish Joint")
    
    Returns:
        Dictionary with chord data if successful:
        {
            'tonality': 'G',
            'processed_sections': {
                'Intro': {6 chord versions},
                'Verse 1': {6 chord versions},
                ...
            }
        }
        Returns None if no official tab found
    """
    
    print(f"\n{'='*70}")
    print(f"SCRAPING: {artist_name} - {track_name}")
    print(f"{'='*70}\n")
    
    # Search for the song
    search_success = search_song(page, f"{artist_name} {track_name}")
    if not search_success:
        print("✗ Search failed - could not find search box")
        log_missing_chords(artist_name, track_name)
        return None
    act_human(page)
    
    # Find official tabs
    official_urls = find_official_tabs(page)
    
    # Check if we found an official tab
    if not official_urls:
        print("✗ No official tabs found")
        log_missing_chords(artist_name, track_name)
        # Navigate back to homepage for next song in batch
        page.goto("https://www.ultimate-guitar.com/")
        page.wait_for_timeout(2000)
        return None
    
    # Navigate to the tab
    click_tab(page, official_urls[0])
    
    # Handle cookie popup if it appears
    handle_cookies(page)
    
    # Click CHORDS button
    click_chords(page)
    
    # Extract metadata
    tonality = extract_tonality(page)
    capo_info = extract_capo_and_tuning(page)
    tuning = capo_info['tuning']
    capo_fret = capo_info['capo']
    
    # CHECK: Skip if alternate tuning (not standard E A D G B E)
    if not is_standard_tuning(tuning):
        tuning_name = get_tuning_name(tuning)
        print(f"⚠ Alternate tuning detected: {tuning_name}")
        log_alternate_tuning(artist_name, track_name, tuning_name, capo_fret)
        print(f"✗ Skipping - alternate tuning not yet supported")
        # Navigate back to homepage
        page.goto("https://www.ultimate-guitar.com/")
        page.wait_for_timeout(2000)
        return None
    
    # Extract chords
    sections = extract_chords(page)
    
    # IMPORTANT: The key shown is already the ACTUAL key
    # But chord shapes need to be transposed by capo to match
    if capo_fret > 0:
        print(f"🎸 Capo on fret {capo_fret} - transposing chord shapes to actual sound...")
        print(f"   Key: {tonality} (already actual key, not transposed)")
    
    # Process chords into all 6 versions (using actual sounding chords)
    processed_sections = {}
    for section_name, chord_shapes in sections.items():
        # Transpose shapes by capo to get actual chords
        actual_chords = transpose_chord_list(chord_shapes, capo_fret)
        # Process the actual chords (transpose to C/Am, Roman numerals, etc.)
        processed = process_chords(tonality, actual_chords)
        processed_sections[section_name] = processed
    
    # Navigate back to homepage for next song in batch
    page.goto("https://www.ultimate-guitar.com/")
    page.wait_for_timeout(2000)
    
    print(f"✓ Successfully scraped {artist_name} - {track_name}")
    
    # Return the chord data
    return {
        'tonality': tonality,
        'processed_sections': processed_sections
    }

