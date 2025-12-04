"""
SIMPLIFY CHORD: Strip embellishments from a chord
Keeps only root note and basic quality (major, minor, diminished, augmented).
"""


def simplify_chord(chord):
    """
    Simplify a chord by removing embellishments.
    
    Args:
        chord: Complex chord (e.g., "Cadd9", "Gmaj7", "Asus4")
    
    Returns:
        Simplified chord (e.g., "C", "G", "A")
    """
    import re
    
    # Extract root note and basic quality
    match = re.match(r'^([A-G][#b]?)(m|dim|aug)?', chord)
    
    if match:
        root = match.group(1)
        quality = match.group(2) or ''  # m, dim, or aug
        return root + quality
    else:
        return chord  # Return as-is if we can't parse it

