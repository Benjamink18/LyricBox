"""
CLICK EDIT LYRICS: Click the "Edit Lyrics" button on Genius lyrics page
This reveals the raw lyrics text with section markers.
"""


def click_edit_lyrics(page):
    """
    Click the "Edit Lyrics" button on a Genius lyrics page.
    
    Args:
        page: Playwright page instance (on a lyrics page)
    
    Returns:
        None (navigates to edit view)
    """
    print("Looking for 'Edit Lyrics' button...")
    
    try:
        # Wait for page to fully load
        page.wait_for_timeout(2000)
        
        # Find and click the "Edit Lyrics" button
        edit_button = page.get_by_text("Edit Lyrics", exact=True)
        
        if edit_button.count() > 0:
            edit_button.click()
            print("✓ Clicked 'Edit Lyrics' button")
            page.wait_for_timeout(2000)
        else:
            print("✗ 'Edit Lyrics' button not found")
    
    except Exception as e:
        print(f"Error clicking Edit Lyrics: {e}")

