"""
GENIUS BATCH SCRAPER: Batch lyrics scraper for data enrichment pipeline
Opens browser once, scrapes multiple songs, returns results.
"""

from .setup_browser import setup_browser
from .handle_cookies import handle_cookies
from .genius_search import search_song
from .click_top_song import click_top_song
from .click_edit_lyrics import click_edit_lyrics
from .extract_lyrics import extract_lyrics
from .parse_lyrics import parse_lyrics
from .lyrics_to_supabase import save_lyrics_to_supabase


def scrape_lyrics_batch(songs_to_scrape):
    """
    Batch scrape lyrics from Genius.com for multiple songs.
    
    Args:
        songs_to_scrape: List of dicts with 'artist' and 'track' keys
    
    Returns:
        Dict with 'successful', 'failed', 'total' counts
    """
    if not songs_to_scrape:
        return {'successful': 0, 'failed': 0, 'total': 0}
    
    # Setup browser and login once
    playwright, browser, page = setup_browser()
    
    # Handle cookies once at the beginning
    handle_cookies(page)
    
    successful = 0
    failed = 0
    
    # Process each song
    for i, song in enumerate(songs_to_scrape, 1):
        artist = song['artist']
        track = song['track']
        
        print(f"  [{i}/{len(songs_to_scrape)}] {artist} - {track}")
        
        try:
            # Search for the song
            search_song(page, artist, track)
            
            # Click top result
            click_top_song(page)
            
            # Click Edit Lyrics
            click_edit_lyrics(page)
            
            # Extract lyrics
            raw_lyrics = extract_lyrics(page)
            
            if not raw_lyrics:
                print(f"    ✗ Failed to extract lyrics")
                failed += 1
                continue
            
            # Parse into sections
            parsed_sections = parse_lyrics(raw_lyrics)
            
            if not parsed_sections:
                print(f"    ✗ No sections parsed")
                failed += 1
                continue
            
            # Save to Supabase
            rows_saved = save_lyrics_to_supabase(artist, track, parsed_sections)
            
            if rows_saved > 0:
                successful += 1
                print(f"    ✓ Saved {rows_saved} sections")
            else:
                failed += 1
                print(f"    ✗ Failed to save to database")
        
        except Exception as e:
            failed += 1
            print(f"    ✗ Error: {e}")
    
    # Close browser and stop Playwright
    browser.close()
    playwright.stop()
    
    print(f"\n  Genius Scraping: {successful} successful, {failed} failed\n")
    
    return {'successful': successful, 'failed': failed, 'total': len(songs_to_scrape)}


if __name__ == "__main__":
    print("Import this module from data_enrichment_main.py")

