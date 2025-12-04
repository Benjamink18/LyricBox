"""
SETUP: Browser initialization and login
Opens Ultimate Guitar and waits for manual login.
"""

from playwright.sync_api import sync_playwright


def setup_browser():
    """
    Set up Playwright browser and navigate to Ultimate Guitar.
    Waits for manual login.
    
    Returns:
        browser: Playwright browser instance
        page: Playwright page instance (logged in)
    """
    print("Setting up browser for Ultimate Guitar...")
    
    # Start Playwright
    playwright = sync_playwright().start()
    
    # Launch browser (headless=False to see what's happening)
    browser = playwright.chromium.launch(headless=False)
    
    # Create a new page
    page = browser.new_page()
    
    # Navigate to Ultimate Guitar homepage
    print("Navigating to Ultimate Guitar...")
    page.goto("https://www.ultimate-guitar.com/")
    page.wait_for_timeout(2000)
    
    # Wait for manual login
    print("\n" + "="*70)
    print("PLEASE LOG IN TO ULTIMATE GUITAR")
    print("="*70)
    print("Press Enter when you have logged in...")
    input()
    
    print("Login complete! Browser ready!")
    
    return playwright, browser, page

