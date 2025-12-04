"""
TEST: Test the Genius scraper with a specific song
This is where we specify which song to scrape for testing purposes.
"""

from genius_scrape_main import scrape_lyrics


if __name__ == "__main__":
    # Song to test
    artist = "Lewis Capaldi"
    track = "Someone You Loved"
    
    print(f"Testing Genius scraper with: {artist} - {track}\n")
    
    # Call the scraper
    result = scrape_lyrics(artist, track)
    
    # Display results
    print("\n" + "="*70)
    print("SCRAPING RESULTS")
    print("="*70)
    
    if result and result['success']:
        print(f"✓ Success!")
        print(f"  Artist: {result['artist']}")
        print(f"  Track: {result['track']}")
        print(f"  Sections parsed: {result['sections_count']}")
        print(f"  Rows saved to Supabase: {result['rows_saved']}")
    else:
        print("✗ Failed to scrape and save lyrics")
        if result:
            print(f"  Artist: {result['artist']}")
            print(f"  Track: {result['track']}")
    
    print("\nTest complete!")

