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
    
    # Try multiple selectors for the search box
    selectors = [
        'input[name="value"]',
        'input[placeholder*="Search"]',
        'input[type="search"]',
        'input.search'
    ]
    
    search_box = None
    for selector in selectors:
        try:
            search_box = page.locator(selector).first
            # Wait for it to be visible
            search_box.wait_for(state="visible", timeout=5000)
            print(f"  Found search box with selector: {selector}")
            break
        except:
            continue
    
    if not search_box:
        print(f"  ✗ Could not find search box on page")
        return False
    
    # Click to focus, then fill (skip clear to avoid issues)
    search_box.click()
    search_box.fill(search_query)
    
    # Press Enter to search
    search_box.press("Enter")
    
    # Wait for results to load
    page.wait_for_timeout(3000)
    
    print("  Search complete!")
    return True

