"""
GENIUS SEARCH: Search for a song on Genius.com
Uses Playwright to interact with the search bar and enter song query.
"""


def search_song(page, artist_name, track_name):
    """
    Search for a song on Genius.com using the search bar.
    
    Args:
        page: Playwright page instance (already on Genius.com)
        artist_name: Artist name (e.g., "Travie McCoy")
        track_name: Track name (e.g., "Billionaire")
    
    Returns:
        None (navigates to search results page)
    """
    # Combine artist and track for search query
    search_query = f"{artist_name} {track_name}"
    
    print(f"Searching for: {search_query}")
    
    # Click into the search bar (using specific selector to avoid cookie search box)
    search_input = page.get_by_role("textbox", name="Search lyrics & more")
    search_input.click()
    
    # Type the search query
    search_input.fill(search_query)
    
    # Press Enter to submit search
    search_input.press("Enter")
    
    # Wait for search results to load
    page.wait_for_timeout(2000)
    
    print("Search complete!")

