"""
CONVERT TO ROMAN: Convert a chord to Roman numeral notation
Assumes input chord is in C major. Preserves embellishments.
"""


def convert_to_roman(chord):
    """
    Convert a chord in C major to Roman numeral notation.
    
    Args:
        chord: Chord in C major (e.g., "C", "Dm", "Fadd9")
    
    Returns:
        Roman numeral representation (e.g., "I", "ii", "IVadd9")
    """
    # Extract root note
    import re
    match = re.match(r'^([A-G][#b]?)(m|dim|aug|maj|add|sus)?(.*)$', chord)
    if not match:
        return chord  # Return as-is if we can't parse it
    
    root = match.group(1)
    quality_marker = match.group(2) or ''
    suffix = match.group(3) or ''
    
    # Full suffix (quality marker + remaining)
    full_suffix = quality_marker + suffix
    
    # Mapping for C major scale
    major_map = {
        'C': 'I',
        'D': 'ii',
        'E': 'iii',
        'F': 'IV',
        'G': 'V',
        'A': 'vi',
        'B': 'viio'
    }
    
    # Get the Roman numeral
    if root in major_map:
        roman = major_map[root]
        
        # Adjust for chord quality
        if 'm' not in quality_marker and root in ['D', 'E', 'A', 'B']:
            # Major chord where minor is expected - use uppercase
            roman = roman.upper()
        
        return roman + full_suffix
    else:
        return chord  # Return as-is if not in C major scale

