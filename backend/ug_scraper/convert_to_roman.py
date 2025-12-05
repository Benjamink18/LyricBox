"""
CONVERT TO ROMAN: Convert a chord to Roman numeral notation
Assumes input chord is in C major. Preserves embellishments.
"""


def convert_to_roman(chord):
    """
    Convert a chord in C major scale framework to Roman numeral notation.
    Handles slash chords (e.g., C/E) by converting both parts.
    
    All chords are analyzed within C major scale:
    - C = I, Dm = ii, Em = iii, F = IV, G = V, Am = vi, Bdim = vii°
    
    Args:
        chord: Chord (e.g., "C", "Dm", "Am", "Fadd9", "C/E")
    
    Returns:
        Roman numeral representation (e.g., "I", "ii", "vi", "IVadd9", "I/iii")
    """
    # Check for slash chord (e.g., C/E)
    import re
    if '/' in chord:
        parts = chord.split('/')
        if len(parts) == 2:
            # Convert both the chord and the bass note
            roman_chord = convert_to_roman(parts[0])
            roman_bass = convert_to_roman(parts[1])
            return f"{roman_chord}/{roman_bass}"
    
    # Extract root note and quality
    match = re.match(r'^([A-G][#b]?)(m|dim|aug)?(.*)$', chord)
    if not match:
        return chord  # Return as-is if we can't parse it
    
    root = match.group(1)
    quality = match.group(2) or ''  # m, dim, aug
    suffix = match.group(3) or ''   # Everything else (7, add9, sus4, etc.)
    
    # C major scale degree mapping (natural quality)
    scale_map = {
        'C': ('I', ''),      # Major (I)
        'D': ('II', 'm'),    # Minor (ii)
        'E': ('III', 'm'),   # Minor (iii)
        'F': ('IV', ''),     # Major (IV)
        'G': ('V', ''),      # Major (V)
        'A': ('VI', 'm'),    # Minor (vi)
        'B': ('VII', 'dim')  # Diminished (vii°)
    }
    
    # Get the scale degree and natural quality
    if root not in scale_map:
        return chord  # Return as-is if not in C major scale
    
    roman_base, natural_quality = scale_map[root]
    
    # Determine case based on actual chord quality
    is_minor = (quality == 'm')
    is_diminished = (quality == 'dim')
    is_augmented = (quality == 'aug')
    
    # Default: use lowercase for minor/diminished, uppercase for major/augmented
    if is_minor or is_diminished:
        roman_numeral = roman_base.lower()
    else:
        roman_numeral = roman_base.upper()
    
    # Add quality markers and suffix
    if is_diminished:
        return roman_numeral + '°' + suffix
    elif is_augmented:
        return roman_numeral + '+' + suffix
    else:
        return roman_numeral + suffix

