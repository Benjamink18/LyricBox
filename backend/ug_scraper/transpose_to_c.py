"""
TRANSPOSE TO C: Transpose a chord from its original key to C major
Preserves embellishments (e.g., add9, maj7) while changing the root note.
"""


def transpose_to_c(tonality, chord):
    """
    Transpose a chord from a given key to C major.
    
    Args:
        tonality: Original key (e.g., "G", "Am")
        chord: Chord to transpose (e.g., "G", "Cadd9")
    
    Returns:
        Transposed chord string (e.g., "C", "Fadd9")
    """
    # Chromatic scale
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Handle minor keys - convert to relative major
    if tonality.endswith('m'):
        minor_to_major = {
            'Am': 'C', 'A#m': 'C#', 'Bm': 'D', 'Cm': 'D#', 'C#m': 'E',
            'Dm': 'F', 'D#m': 'F#', 'Em': 'G', 'Fm': 'G#', 'F#m': 'A',
            'Gm': 'A#', 'G#m': 'B'
        }
        tonality = minor_to_major.get(tonality, 'C')
    
    # Extract root note from chord (handle sharps/flats)
    import re
    match = re.match(r'^([A-G][#b]?)', chord)
    if not match:
        return chord  # Return as-is if we can't parse it
    
    root = match.group(1)
    suffix = chord[len(root):]  # Everything after the root (maj7, add9, etc.)
    
    # Calculate transposition interval
    try:
        from_index = notes.index(tonality)
        to_index = notes.index('C')
        interval = (to_index - from_index) % 12
        
        # Transpose the root note
        root_index = notes.index(root)
        new_root_index = (root_index + interval) % 12
        new_root = notes[new_root_index]
        
        return new_root + suffix
    
    except (ValueError, IndexError):
        return chord  # Return as-is if transposition fails

