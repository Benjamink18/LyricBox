"""
CLICK TAB: Navigate to a specific tab URL
Opens the official tab page.
"""


def click_tab(page, tab_url):
    """
    Navigate to a specific tab URL.
    
    Args:
        page: Playwright page instance
        tab_url: URL of the tab to open
    
    Returns:
        None (navigates to tab page)
    """
    print(f"Navigating to tab: {tab_url}")
    
    # Navigate to the tab URL
    page.goto(tab_url)
    page.wait_for_timeout(2000)
    
    print("Tab page loaded!")

