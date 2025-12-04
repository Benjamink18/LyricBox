"""
FIND OFFICIAL: Find official tabs from search results
Looks for tabs with the "OFFICIAL" tag.
"""


def find_official_tabs(page):
    """
    Find official tabs on the search results page.
    
    Args:
        page: Playwright page instance (on search results page)
    
    Returns:
        List of URLs for official tabs, or empty list if none found
    """
    print("Looking for official tabs...")
    
    # Wait for results to load
    page.wait_for_timeout(2000)
    
    # Use JavaScript to find all official tabs
    js_code = """
    () => {
        const officialTabs = [];
        
        // Look for elements with "OFFICIAL" text
        const elements = Array.from(document.querySelectorAll('*'));
        
        for (const el of elements) {
            if (el.textContent.includes('OFFICIAL')) {
                // Find the closest link (tab URL)
                const link = el.closest('a') || el.querySelector('a');
                if (link && link.href && link.href.includes('/tab/')) {
                    officialTabs.push(link.href);
                }
            }
        }
        
        return [...new Set(officialTabs)]; // Remove duplicates
    }
    """
    
    official_urls = page.evaluate(js_code)
    
    if official_urls:
        print(f"✓ Found {len(official_urls)} official tab(s)")
    else:
        print("✗ No official tabs found")
    
    return official_urls

