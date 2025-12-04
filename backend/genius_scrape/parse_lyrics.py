"""
PARSE LYRICS: Parse raw lyrics text into sections
Splits lyrics by section markers like [Verse 1], [Chorus], etc.
Returns structured data ready for database storage.
"""

import re


def parse_lyrics(raw_lyrics):
    """
    Parse raw lyrics text into sections.
    
    Args:
        raw_lyrics: String with section markers like "[Verse 1]\nlyrics..."
    
    Returns:
        List of dicts with 'section_name' and 'lyrics_text'
        Example: [
            {'section_name': 'Verse 1', 'lyrics_text': 'I'm going under...'},
            {'section_name': 'Chorus', 'lyrics_text': 'I need somebody...'}
        ]
    """
    if not raw_lyrics:
        return []
    
    print("Parsing lyrics into sections...")
    
    sections = []
    
    # Split by lines
    lines = raw_lyrics.split('\n')
    
    current_section = None
    current_lyrics = []
    
    for line in lines:
        # Check if line is a section marker like [Verse 1], [Chorus], etc.
        section_match = re.match(r'\[(.*?)\]', line.strip())
        
        if section_match:
            # Save previous section if it exists
            if current_section and current_lyrics:
                sections.append({
                    'section_name': current_section,
                    'lyrics_text': '\n'.join(current_lyrics).strip()
                })
            
            # Start new section
            current_section = section_match.group(1)
            current_lyrics = []
        else:
            # Add line to current section
            if current_section:
                current_lyrics.append(line)
    
    # Save the last section
    if current_section and current_lyrics:
        sections.append({
            'section_name': current_section,
            'lyrics_text': '\n'.join(current_lyrics).strip()
        })
    
    print(f"✓ Parsed {len(sections)} sections")
    
    return sections

