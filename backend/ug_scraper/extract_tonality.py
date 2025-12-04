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
        # Get page text
        page_text = page.content()
        
        # Look for tonality in the page
        # Ultimate Guitar shows it as "Tonality: G" or similar
        import re
        tonality_match = re.search(r'"tonality_name":"([^"]+)"', page_text)
        
        if tonality_match:
            tonality = tonality_match.group(1)
            print(f"✓ Tonality: {tonality}")
            return tonality
        else:
            print("✗ Tonality not found, defaulting to Unknown")
            return "Unknown"
    
    except Exception as e:
        print(f"Error extracting tonality: {e}")
        return "Unknown"

