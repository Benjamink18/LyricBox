"""
EXTRACT TONALITY: Extract the song's key from the tab page
Gets the "Tonality" value displayed on Ultimate Guitar.
"""


def extract_tonality(page):
    """
    Extract the musical key/tonality from a tab page.
    
    Args:
        page: Playwright page instance (on a tab page with chords visible)
    
    Returns:
        String with the tonality (e.g., "G", "Am", "C#"), or "Unknown" if not found
    """
    print("Extracting tonality...")
    
    try:
        # Method 1: Try to get from JavaScript object directly (most reliable)
        tonality = page.evaluate("""
            () => {
                // Try multiple possible paths in the UG data structure
                if (window.UGAPP?.store?.page?.data?.tab_view?.meta?.tonality) {
                    return window.UGAPP.store.page.data.tab_view.meta.tonality;
                }
                if (window.UGAPP?.store?.page?.data?.tab?.tonality_name) {
                    return window.UGAPP.store.page.data.tab.tonality_name;
                }
                if (window.UGAPP?.store?.page?.data?.tab?.tonality) {
                    return window.UGAPP.store.page.data.tab.tonality;
                }
                return null;
            }
        """)
        
        if tonality:
            print(f"✓ Tonality (from JS): {tonality}")
            return tonality
        
        # Method 2: Fallback to regex patterns in HTML
        page_text = page.content()
        import re
        
        # Pattern 1: Try "key" field
        tonality_match = re.search(r'"key":"([^"]+)"', page_text)
        
        # Pattern 2: Try "tonality_name" (old format)
        if not tonality_match:
            tonality_match = re.search(r'"tonality_name":"([^"]+)"', page_text)
        
        # Pattern 3: Try "tonality" field
        if not tonality_match:
            tonality_match = re.search(r'"tonality":"([^"]+)"', page_text)
        
        if tonality_match:
            tonality = tonality_match.group(1)
            print(f"✓ Tonality (from regex): {tonality}")
            return tonality
        else:
            print("✗ Tonality not found in JS or HTML, defaulting to Unknown")
            return "Unknown"
    
    except Exception as e:
        print(f"Error extracting tonality: {e}")
        return "Unknown"

