"""
HANDLE COOKIES: Deal with Genius.com cookie consent popup
Clicks accept/consent button if the popup appears.
"""


def handle_cookies(page):
    """
    Handle cookie consent popup on Genius.com.
    Clicks the accept button if it appears.
    
    Args:
        page: Playwright page instance
    
    Returns:
        None
    """
    print("Checking for cookie popup...")
    
    try:
        # Wait a moment for popup to appear
        page.wait_for_timeout(2000)
        
        # Try to find "I Accept" button (Genius uses this)
        button = page.get_by_text("I Accept", exact=True)
        
        if button.count() > 0:
            button.first.click(force=True)
            print("✓ Clicked 'I Accept' cookie button")
            page.wait_for_timeout(1000)
            return
        
        print("No cookie popup found (already accepted or not present)")
        
    except Exception as e:
        print(f"Cookie handling completed: {e}")

