"""
TRANSPOSE TO C: Transpose a chord from its original key to C major
Preserves embellishments (e.g., add9, maj7) while changing the root note.
"""


def transpose_to_c(tonality, chord):
    """
    Transpose a chord to C major scale framework.
    Handles slash chords (e.g., D/F#) by transposing both parts.
    
    Major keys → C major
    Minor keys → Am (the vi of C major)
    
    Args:
        tonality: Original key (e.g., "G", "Am", "F#m")
        chord: Chord to transpose (e.g., "G", "Cadd9", "D/F#")
    
    Returns:
        Transposed chord string (e.g., "C", "Fadd9", "C/E")
    """
    # Check for slash chord (e.g., D/F#)
    import re
    if '/' in chord:
        parts = chord.split('/')
        if len(parts) == 2:
            # Transpose both the chord and the bass note
            transposed_chord = transpose_to_c(tonality, parts[0])
            transposed_bass = transpose_to_c(tonality, parts[1])
            return f"{transposed_chord}/{transposed_bass}"
    
    # Chromatic scale
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Determine target: C for major keys, A for minor keys
    is_minor = tonality.endswith('m')
    target = 'A' if is_minor else 'C'
    
    # Get the root of the tonality (strip 'm' if minor)
    tonality_root = tonality[:-1] if is_minor else tonality
    
    # Extract root note from chord (handle sharps/flats)
    match = re.match(r'^([A-G][#b]?)', chord)
    if not match:
        return chord  # Return as-is if we can't parse it
    
    root = match.group(1)
    suffix = chord[len(root):]  # Everything after the root (maj7, add9, etc.)
    
    # Calculate transposition interval
    try:
        from_index = notes.index(tonality_root)
        to_index = notes.index(target)
        interval = (to_index - from_index) % 12
        
        # Transpose the root note
        root_index = notes.index(root)
        new_root_index = (root_index + interval) % 12
        new_root = notes[new_root_index]
        
        return new_root + suffix
    
    except (ValueError, IndexError):
        return chord  # Return as-is if transposition fails

