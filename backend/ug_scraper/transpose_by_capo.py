"""
TRANSPOSE BY CAPO: Convert chord shapes to actual sounding chords
==================================================================
When a capo is used, the finger shapes don't match the actual sound.
This function transposes the shapes up by the capo amount.

Example: Capo 5, shape "Dm" → actual sound "Gm"
"""


def transpose_by_capo(chord, capo_fret):
    """
    Transpose a chord shape by the capo position to get the actual sounding chord.
    Handles slash chords (e.g., D/F#) by transposing both parts.
    
    Args:
        chord: Chord shape (e.g., "Dm", "Cadd9", "D/F#")
        capo_fret: Capo position (0 = no capo, 5 = 5th fret, etc.)
    
    Returns:
        Actual sounding chord (e.g., "Gm", "Fadd9", "G/B")
    """
    if capo_fret == 0:
        return chord  # No capo, return as-is
    
    # Check for slash chord (e.g., D/F#)
    import re
    if '/' in chord:
        parts = chord.split('/')
        if len(parts) == 2:
            # Transpose both the chord and the bass note
            transposed_chord = transpose_by_capo(parts[0], capo_fret)
            transposed_bass = transpose_by_capo(parts[1], capo_fret)
            return f"{transposed_chord}/{transposed_bass}"
    
    # Chromatic scale
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Also support flat notation
    flats_to_sharps = {
        'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
    }
    
    # Extract root note from chord
    match = re.match(r'^([A-G][#b]?)', chord)
    if not match:
        return chord  # Can't parse, return as-is
    
    root = match.group(1)
    suffix = chord[len(root):]  # Everything after root (m, 7, add9, etc.)
    
    # Convert flats to sharps for consistency
    if root in flats_to_sharps:
        root = flats_to_sharps[root]
    
    # Transpose up by capo amount
    try:
        root_index = notes.index(root)
        new_index = (root_index + capo_fret) % 12
        new_root = notes[new_index]
        
        return new_root + suffix
    
    except (ValueError, IndexError):
        return chord  # If anything fails, return original


def transpose_chord_list(chords, capo_fret):
    """
    Transpose a list of chord shapes by capo position.
    
    Args:
        chords: List of chord shapes (e.g., ["Dm", "C", "Bb"])
        capo_fret: Capo position (0-12)
    
    Returns:
        List of actual sounding chords (e.g., ["Gm", "F", "Eb"])
    """
    return [transpose_by_capo(chord, capo_fret) for chord in chords]

