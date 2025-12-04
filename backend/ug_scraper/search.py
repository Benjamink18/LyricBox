"""
SEARCH: Search for a song on Ultimate Guitar
Uses the search box to find artist and track.
"""


def search_song(page, search_query):
    """
    Search for a song on Ultimate Guitar.
    
    Args:
        page: Playwright page instance
        search_query: Search string (e.g., "D'Angelo Spanish Joint")
    
    Returns:
        None (navigates to search results page)
    """
    print(f"Searching for: {search_query}")
    
    # Find the search input box
    search_box = page.locator('input[name="value"]')
    
    # Clear and type the search query
    search_box.clear()
    search_box.fill(search_query)
    
    # Press Enter to search
    search_box.press("Enter")
    
    # Wait for results to load
    page.wait_for_timeout(2000)
    
    print("Search complete!")

