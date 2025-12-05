"""
UG SCRAPER MAIN: Batch chord scraper
Scrapes chord data from Ultimate Guitar for a list of songs.
"""

from .setup import setup_browser
from .scrape_song import scrape_song
from .chords_to_supabase import save_chords_to_supabase


def scrape_chords(songs_to_scrape):
    """
    Batch scrape chord data from Ultimate Guitar.
    Returns: Dict with 'successful', 'failed', 'total' counts + songs_with_key
    """
    if not songs_to_scrape:
        return {'successful': 0, 'failed': 0, 'total': 0, 'songs_with_key': []}
    
    # Setup browser and login once
    playwright, browser, page = setup_browser()
    
    # Navigate to homepage to ensure search box is available
    print("\n  Navigating to homepage...")
    page.goto("https://www.ultimate-guitar.com/")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    print("  ✓ Ready to scrape!")
    
    successful = 0
    failed = 0
    songs_with_key = []  # Track (song_id, tonality) for updating musical_key
    
    # Process each song
    for i, song in enumerate(songs_to_scrape, 1):
        print(f"[{i}/{len(songs_to_scrape)}] {song['artist']} - {song['track']}")
        
        chord_data = scrape_song(page, song['artist'], song['track'])
        
        if chord_data:
            # Save chord data to Supabase (using song_id directly)
            rows_saved = save_chords_to_supabase(
                song_id=song['song_id'],
                processed_sections=chord_data['processed_sections']
            )
            
            if rows_saved > 0:
                successful += 1
                print("  ✓ Success")
                
                # Track if tonality was found (for updating songs.musical_key)
                if chord_data['tonality'] and chord_data['tonality'] != "Unknown":
                    songs_with_key.append((song['song_id'], chord_data['tonality']))
            else:
                failed += 1
                print("  ✗ Failed (database save error)")
        else:
            failed += 1
            print("  ✗ Failed (no official tab)")
    
    browser.close()
    playwright.stop()
    
    print(f"\nUG Scraping: {successful} successful, {failed} failed\n")
    
    return {
        'successful': successful,
        'failed': failed,
        'total': len(songs_to_scrape),
        'songs_with_key': songs_with_key
    }


if __name__ == "__main__":
    print("Import this module from data_enrichment_main.py")
