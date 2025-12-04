"""
CLICK TOP SONG: Click the first song result in the SONGS section
Navigates to the lyrics page from the search results.
"""


def click_top_song(page):
    """
    Click the first song result under the "SONGS" section on search results page.
    
    Args:
        page: Playwright page instance (on search results page)
    
    Returns:
        None (navigates to lyrics page)
    """
    print("Looking for top song result in SONGS section...")
    
    try:
        # Wait for search results to load
        page.wait_for_timeout(3000)
        
        # Simple approach: Find any link containing "lyrics" and click the first one
        # This should get the top song result regardless of section
        lyrics_links = page.locator('a[href*="-lyrics"]')
        
        if lyrics_links.count() > 0:
            # Click the first lyrics link
            first_link = lyrics_links.first
            first_link.click()
            print("✓ Clicked top song result")
            page.wait_for_timeout(2000)
        else:
            print("✗ Could not find any song lyrics links")
    
    except Exception as e:
        print(f"Error clicking top song: {e}")

