"""
HANDLE COOKIES: Manages cookie consent popups on Ultimate Guitar.
"""


def handle_cookies(page):
    """
    Attempts to dismiss cookie consent popups on Ultimate Guitar.
    Tries multiple common button texts.
    """
    print("  Checking for cookie popup...")
    
    # Common cookie consent button texts on UG
    button_texts = [
        "Accept",
        "Accept All",
        "I Accept",
        "Accept Cookies",
        "Got it",
        "OK",
        "Agree"
    ]
    
    for text in button_texts:
        try:
            # Look for button with this text
            button = page.get_by_role("button", name=text)
            if button.count() > 0:
                button.first.click(force=True)
                print(f"  ✓ Clicked '{text}' cookie button")
                page.wait_for_timeout(1000)
                return True
        except:
            continue
    
    # Also try looking for any button in a cookie banner
    try:
        cookie_banner = page.locator('[class*="cookie"], [class*="consent"], [id*="cookie"], [id*="consent"]').first
        if cookie_banner.count() > 0:
            accept_button = cookie_banner.locator('button').first
            if accept_button.count() > 0:
                accept_button.click(force=True)
                print("  ✓ Clicked cookie banner button")
                page.wait_for_timeout(1000)
                return True
    except:
        pass
    
    print("  (No cookie popup found)")
    return False

