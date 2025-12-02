#!/usr/bin/env python3
"""
Chord to Roman numeral converter for Melody feature.
Converts chord names (Am, C, F, G) to Roman numerals (vi, I, IV, V).
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ChordProgression:
    """Parsed chord progression with metadata."""
    roman_numerals: List[str]      # ['vi', 'I', 'IV', 'V']
    original_chords: List[str]     # ['Am', 'C', 'F', 'G']
    key: str                       # 'A minor' or 'C major'


# Note to semitone mapping (C = 0)
NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

# Major scale intervals (semitones from root)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

# Minor scale intervals (natural minor)  
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


def parse_chord(chord: str) -> Tuple[str, bool]:
    """
    Parse a chord name into root note and quality.
    
    Args:
        chord: Chord name like 'Am', 'C', 'F#m', 'Bbmaj7'
        
    Returns:
        Tuple of (root_note, is_major)
    """
    chord = chord.strip()
    
    # Match root note (supports sharps/flats)
    match = re.match(r'^([A-G][#b]?)', chord)
    if not match:
        raise ValueError(f"Invalid chord: {chord}")
    
    root = match.group(1)
    remainder = chord[len(root):]
    
    # Determine if major or minor
    # Minor: m, min, minor (but not maj)
    is_major = True
    if 'm' in remainder.lower() and 'maj' not in remainder.lower():
        is_major = False
    
    return root, is_major


def infer_key(chords: List[str]) -> Tuple[str, bool]:
    """
    Infer the key from a chord progression.
    
    Strategy: First chord is usually the tonic.
    
    Returns:
        Tuple of (key_root, is_major_key)
    """
    if not chords:
        return 'C', True
    
    first_root, first_is_major = parse_chord(chords[0])
    return first_root, first_is_major


def chord_to_roman(chord: str, key_root: str, is_major_key: bool) -> str:
    """
    Convert a chord to Roman numeral based on the key.
    
    Args:
        chord: 'Am', 'C', 'F', etc.
        key_root: 'C', 'A', etc.
        is_major_key: True for major key, False for minor
        
    Returns:
        Roman numeral like 'I', 'vi', 'IV', 'V'
    """
    root, is_major_chord = parse_chord(chord)
    
    # Get semitone values
    key_semitone = NOTE_TO_SEMITONE.get(key_root, 0)
    chord_semitone = NOTE_TO_SEMITONE.get(root, 0)
    
    # Calculate interval from key root
    interval = (chord_semitone - key_semitone) % 12
    
    # Choose scale based on key type
    scale = MAJOR_SCALE if is_major_key else MINOR_SCALE
    
    # Find position in scale
    try:
        position = scale.index(interval)
    except ValueError:
        # Chord not in scale - find closest
        position = min(range(len(scale)), key=lambda i: abs(scale[i] - interval))
    
    # Roman numerals (0-indexed)
    numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    roman = numerals[position]
    
    # Lowercase for minor chords
    if not is_major_chord:
        roman = roman.lower()
    
    return roman


def convert_progression(chord_input: str, key: str = None) -> ChordProgression:
    """
    Convert chord progression to Roman numerals.
    
    Args:
        chord_input: "Am C F G" or "Am-C-F-G" or "Am, C, F, G"
        key: Optional key like "A minor" or "C major". If not provided, inferred from first chord.
        
    Returns:
        ChordProgression with Roman numerals and metadata
    """
    # Clean input and split on spaces, hyphens, or commas
    chord_input = chord_input.strip()
    chords = re.split(r'[\s\-,]+', chord_input)
    chords = [c for c in chords if c]  # Remove empty strings
    
    if not chords:
        raise ValueError("No chords found in input")
    
    # Check if input is already Roman numerals
    roman_pattern = r'^(I|II|III|IV|V|VI|VII|i|ii|iii|iv|v|vi|vii)$'
    if all(re.match(roman_pattern, c) for c in chords):
        # Already Roman numerals
        is_major = chords[0].isupper()
        return ChordProgression(
            roman_numerals=chords,
            original_chords=chords,
            key=f"Unknown {'major' if is_major else 'minor'}"
        )
    
    # Parse key if provided
    if key:
        key_parts = key.lower().split()
        key_root = key_parts[0].capitalize()
        is_major_key = 'major' in key.lower()
    else:
        # Infer key from progression
        key_root, is_major_key = infer_key(chords)
    
    # Convert each chord to Roman numeral
    roman_numerals = [chord_to_roman(c, key_root, is_major_key) for c in chords]
    
    key_str = f"{key_root} {'major' if is_major_key else 'minor'}"
    
    return ChordProgression(
        roman_numerals=roman_numerals,
        original_chords=chords,
        key=key_str
    )


# CLI for testing
if __name__ == "__main__":
    test_cases = [
        ("Am C F G", None),
        ("C Am F G", None),
        ("D Bm G A", None),
        ("Am C F G", "A minor"),
        ("vi I IV V", None),
    ]
    
    for chord_input, key in test_cases:
        result = convert_progression(chord_input, key)
        print(f"\nInput: {chord_input}" + (f" (Key: {key})" if key else ""))
        print(f"  Roman: {' → '.join(result.roman_numerals)}")
        print(f"  Key: {result.key}")

