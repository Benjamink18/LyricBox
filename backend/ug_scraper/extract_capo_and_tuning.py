"""
EXTRACT CAPO AND TUNING: Extract capo position and tuning from Ultimate Guitar
===============================================================================
Capo changes the actual pitch of the chords being played.
"""


def extract_capo_and_tuning(page):
    """
    Extract capo position and tuning information from a tab page.
    
    Args:
        page: Playwright page instance (on a tab page)
    
    Returns:
        Dictionary with:
        {
            'capo': 0,  # Fret number (0 = no capo)
            'tuning': 'E A D G B E'  # String tuning (standard = 'E A D G B E')
        }
    """
    print("Extracting capo and tuning...")
    
    try:
        # Try to extract from JavaScript object (most reliable)
        result = page.evaluate("""
            () => {
                let capo = 0;
                let tuning = 'E A D G B E';  // Default standard tuning
                
                // Try multiple possible paths for capo
                if (window.UGAPP?.store?.page?.data?.tab_view?.meta?.capo) {
                    capo = window.UGAPP.store.page.data.tab_view.meta.capo;
                }
                if (window.UGAPP?.store?.page?.data?.tab?.capo) {
                    capo = window.UGAPP.store.page.data.tab.capo;
                }
                
                // Try multiple possible paths for tuning
                if (window.UGAPP?.store?.page?.data?.tab_view?.meta?.tuning) {
                    const t = window.UGAPP.store.page.data.tab_view.meta.tuning;
                    // Tuning might be an object with string values
                    if (typeof t === 'object' && t.value) {
                        tuning = t.value;
                    } else if (typeof t === 'string') {
                        tuning = t;
                    }
                }
                if (window.UGAPP?.store?.page?.data?.tab?.tuning) {
                    const t = window.UGAPP.store.page.data.tab.tuning;
                    // Tuning might be an object with string values
                    if (typeof t === 'object' && t.value) {
                        tuning = t.value;
                    } else if (typeof t === 'string') {
                        tuning = t;
                    }
                }
                
                return { capo: capo, tuning: tuning };
            }
        """)
        
        capo = result.get('capo', 0)
        tuning = result.get('tuning', 'E A D G B E')
        
        # Handle tuning if it's still a dict (shouldn't happen with updated JS, but safety check)
        if isinstance(tuning, dict):
            tuning = tuning.get('value', 'E A D G B E')
        
        # Ensure capo is an integer
        try:
            capo = int(capo)
        except (ValueError, TypeError):
            capo = 0
        
        print(f"✓ Capo: {capo}, Tuning: {tuning}")
        return {
            'capo': capo,
            'tuning': tuning
        }
    
    except Exception as e:
        print(f"Error extracting capo/tuning: {e}")
        return {
            'capo': 0,
            'tuning': 'E A D G B E'
        }

