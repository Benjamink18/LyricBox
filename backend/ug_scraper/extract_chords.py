"""
EXTRACT CHORDS: Extract chords grouped by section
Uses DOM traversal to associate chords with their section markers.
"""


def extract_chords(page):
    """
    Extract chords from the tab page, grouped by section.
    
    Args:
        page: Playwright page instance (on a tab page with chords visible)
    
    Returns:
        Dictionary mapping section names to lists of chords
        Example: {
            'Intro': ['G', 'Cadd9'],
            'Verse 1': ['G', 'Asus4', 'Em7'],
            'Chorus': ['G', 'Cadd9', 'G']
        }
    """
    print("Extracting chords...")
    
    # Use JavaScript to traverse DOM and extract chords by section
    js_code = """
    () => {
        const sections = {};
        const sectionCounts = {};
        let currentSection = 'Unknown';
        
        // Find all content areas that might contain chords
        const contentAreas = document.querySelectorAll('pre, [class*="chord"], [class*="content"]');
        
        for (const area of contentAreas) {
            // Use TreeWalker to traverse in order
            const walker = document.createTreeWalker(
                area,
                NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                // Check for section markers in text nodes
                if (node.nodeType === Node.TEXT_NODE) {
                    const text = node.textContent;
                    const sectionMatch = text.match(/\\[(Intro|Verse\\s*\\d*|Chorus|Bridge|Outro|Pre-Chorus|Interlude|Solo)[^\\]]*\\]/i);
                    
                    if (sectionMatch) {
                        let baseName = sectionMatch[0].replace(/[\\[\\]]/g, '');
                        
                        // Auto-number duplicate sections
                        if (!sectionCounts[baseName]) {
                            sectionCounts[baseName] = 0;
                        }
                        sectionCounts[baseName]++;
                        
                        if (sectionCounts[baseName] > 1) {
                            currentSection = baseName + ' (' + sectionCounts[baseName] + ')';
                        } else {
                            currentSection = baseName;
                        }
                        
                        sections[currentSection] = [];
                    }
                }
                
                // Check for chord elements
                if (node.nodeType === Node.ELEMENT_NODE && node.hasAttribute('data-name')) {
                    const chordName = node.getAttribute('data-name');
                    if (chordName) {
                        if (!sections[currentSection]) {
                            sections[currentSection] = [];
                        }
                        sections[currentSection].push(chordName);
                    }
                }
            }
        }
        
        return sections;
    }
    """
    
    sections = page.evaluate(js_code)
    
    print(f"✓ Extracted {len(sections)} section(s)")
    for section_name, chords in sections.items():
        print(f"  {section_name}: {len(chords)} chords")
    
    return sections

