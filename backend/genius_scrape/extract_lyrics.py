"""
EXTRACT LYRICS: Extract lyrics with section markers from Genius edit page
Gets the raw lyrics text including [Verse 1], [Chorus], etc. markers.
"""


def extract_lyrics(page):
    """
    Extract lyrics from the edit lyrics page on Genius.
    
    Args:
        page: Playwright page instance (on edit lyrics page)
    
    Returns:
        String containing lyrics with section markers, or None if failed
    """
    print("Extracting lyrics from edit page...")
    
    try:
        # Wait for edit page to load
        page.wait_for_timeout(2000)
        
        # The lyrics are in a textarea or contenteditable div
        # We'll use JavaScript to get the text content
        js_code = """
        () => {
            // Look for textarea or contenteditable element with lyrics
            const textarea = document.querySelector('textarea');
            if (textarea) {
                return textarea.value;
            }
            
            // Fallback: look for contenteditable div
            const editable = document.querySelector('[contenteditable="true"]');
            if (editable) {
                return editable.innerText;
            }
            
            return null;
        }
        """
        
        lyrics = page.evaluate(js_code)
        
        if lyrics:
            print(f"✓ Extracted lyrics ({len(lyrics)} characters)")
            return lyrics
        else:
            print("✗ Could not find lyrics text area")
            return None
    
    except Exception as e:
        print(f"Error extracting lyrics: {e}")
        return None

