"""
SETUP BROWSER: Initialize Playwright browser for Genius scraping
Simple browser setup with headless=False to see what's happening during testing.
"""

from playwright.sync_api import sync_playwright


def setup_browser():
    """
    Launch browser and create a new page.
    
    Returns:
        browser: Playwright browser instance
        page: Playwright page instance
    """
    print("Setting up browser for Genius.com...")
    
    # Start Playwright
    playwright = sync_playwright().start()
    
    # Launch browser (headless=False so we can see it during testing)
    browser = playwright.chromium.launch(headless=False)
    
    # Create a new page
    page = browser.new_page()
    
    # Navigate to Genius homepage
    print("Navigating to Genius.com...")
    page.goto("https://genius.com")
    page.wait_for_timeout(2000)  # Wait for page to load
    
    # Wait for manual login
    print("\n" + "="*70)
    print("PLEASE LOG IN TO GENIUS.COM")
    print("="*70)
    print("Press Enter when you have logged in...")
    input()
    
    print("Login complete! Browser ready!")
    
    return browser, page

