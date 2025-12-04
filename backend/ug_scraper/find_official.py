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
    print("  Looking for official tabs...")
    
    # Wait for results to load properly
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # Use JavaScript to find official tabs with multiple strategies
    js_code = """
    () => {
        const officialTabs = [];
        
        // Strategy 1: Look for "OFFICIAL" badge/text
        const officialElements = Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent.includes('OFFICIAL') || 
            el.textContent.includes('Official') ||
            el.classList.toString().includes('official')
        );
        
        for (const el of officialElements) {
            const link = el.closest('a') || el.querySelector('a');
            if (link && link.href && link.href.includes('/tab/')) {
                officialTabs.push(link.href);
            }
        }
        
        // Strategy 2: Look for verified/pro tabs (common on UG)
        const verifiedLinks = Array.from(document.querySelectorAll('a[href*="/tab/"]')).filter(link =>
            link.textContent.includes('Pro') || 
            link.textContent.includes('Verified') ||
            link.querySelector('[class*="official"]') ||
            link.querySelector('[class*="verified"]')
        );
        
        verifiedLinks.forEach(link => {
            if (link.href.includes('/tab/')) {
                officialTabs.push(link.href);
            }
        });
        
        // Strategy 3: If no official found, just get the first chord tab
        if (officialTabs.length === 0) {
            const firstTab = document.querySelector('a[href*="/tab/"]');
            if (firstTab) {
                officialTabs.push(firstTab.href);
            }
        }
        
        return [...new Set(officialTabs)]; // Remove duplicates
    }
    """
    
    official_urls = page.evaluate(js_code)
    
    if official_urls:
        print(f"  ✓ Found {len(official_urls)} tab(s)")
    else:
        print("  ✗ No tabs found")
    
    return official_urls

