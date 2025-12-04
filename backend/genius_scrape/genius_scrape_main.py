"""
GENIUS SCRAPE MAIN: Orchestrator for scraping lyrics from Genius.com
Sets up browser and coordinates the scraping process.
"""

from setup_browser import setup_browser
from handle_cookies import handle_cookies
from genius_search import search_song
from click_top_song import click_top_song
from click_edit_lyrics import click_edit_lyrics
from extract_lyrics import extract_lyrics
from parse_lyrics import parse_lyrics
from lyrics_to_supabase import save_lyrics_to_supabase


def scrape_lyrics(artist_name, track_name):
    """
    Main function to scrape lyrics from Genius.com.
    
    Args:
        artist_name: Artist name (e.g., "Lewis Capaldi")
        track_name: Track name (e.g., "Someone You Loved")
    
    Returns:
        Lyrics data if successful, None otherwise
    """
    print(f"Starting Genius lyrics scraper for {artist_name} - {track_name}...")
    
    # Setup browser and navigate to starting page
    browser, page = setup_browser()
    
    # Handle cookie consent popup if it appears
    handle_cookies(page)
    
    # Search for the song
    search_song(page, artist_name, track_name)
    
    # Click the top song result in SONGS section
    click_top_song(page)
    
    # Click the Edit Lyrics button
    click_edit_lyrics(page)
    
    # Extract the lyrics with section markers
    raw_lyrics = extract_lyrics(page)
    
    if not raw_lyrics:
        print("✗ Failed to extract lyrics")
        browser.close()
        return {'success': False, 'artist': artist_name, 'track': track_name}
    
    # Parse lyrics into sections
    parsed_sections = parse_lyrics(raw_lyrics)
    
    # Save to Supabase
    rows_saved = save_lyrics_to_supabase(artist_name, track_name, parsed_sections)
    
    print("\nBrowser is open and ready!")
    print("Press Enter to close browser...")
    input()
    
    # Close browser
    browser.close()
    print("Done!")
    
    # Return lyrics data
    return {
        'artist': artist_name,
        'track': track_name,
        'sections_count': len(parsed_sections),
        'rows_saved': rows_saved,
        'success': rows_saved > 0
    }


if __name__ == "__main__":
    print("Import this module from test.py or data_enrichment_main.py")

