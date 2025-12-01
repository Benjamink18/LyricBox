#!/usr/bin/env python3
"""
Chord progression parser and converter for Melody feature.
Converts chord names (Am, C, F, G) to Roman numerals (vi, I, IV, V).
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ChordProgression:
    """Parsed chord progression with metadata."""
    roman_numerals: List[str]  # ['vi', 'I', 'IV', 'V']
    original_chords: List[str]  # ['Am', 'C', 'F', 'G']
    inferred_key: str  # 'C' or 'Am'
    is_major: bool  # True for major key, False for minor


class ChordConverter:
    """Convert chord progressions to key-agnostic Roman numerals."""
    
    # Mapping of notes to semitones (C = 0)
    NOTE_TO_SEMITONE = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }
    
    SEMITONE_TO_NOTE = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    
    # Major scale intervals (semitones from root)
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # I, ii, iii, IV, V, vi, vii
    
    # Minor scale intervals (natural minor)
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # i, ii, III, iv, v, VI, VII
    
    def parse_chord_name(self, chord: str) -> Tuple[str, bool]:
        """
        Parse a chord name and return (root_note, is_major).
        
        Examples:
            'C' or 'Cmaj' -> ('C', True)
            'Am' or 'Amin' -> ('A', False)
            'F#m' -> ('F#', False)
        """
        chord = chord.strip()
        
        # Match root note (supports sharps/flats)
        match = re.match(r'^([A-G][#b]?)', chord)
        if not match:
            raise ValueError(f"Invalid chord: {chord}")
        
        root = match.group(1)
        remainder = chord[len(root):]
        
        # Determine if major or minor
        is_major = True
        if 'm' in remainder.lower() and 'maj' not in remainder.lower():
            is_major = False
        
        return root, is_major
    
    def infer_key(self, chords: List[str]) -> Tuple[str, bool]:
        """
        Infer the key from a chord progression.
        
        Strategy:
            1. Count major vs minor chords
            2. First chord is often the tonic
            3. Return most likely key
        """
        if not chords:
            return 'C', True
        
        # Parse all chords
        parsed = [self.parse_chord_name(c) for c in chords]
        
        # Count major/minor
        major_count = sum(1 for _, is_maj in parsed if is_maj)
        minor_count = len(parsed) - major_count
        
        # Use first chord as likely tonic
        first_root, first_is_major = parsed[0]
        
        # If mostly major chords or first chord is major, assume major key
        if major_count >= minor_count or first_is_major:
            return first_root, True
        else:
            return first_root, False
    
    def chord_to_roman(self, chord: str, key_root: str, is_major_key: bool) -> str:
        """
        Convert a chord to Roman numeral based on the key.
        
        Args:
            chord: 'Am', 'C', 'F', etc.
            key_root: 'C', 'A', etc.
            is_major_key: True for major, False for minor
            
        Returns:
            Roman numeral like 'I', 'vi', 'IV', 'V'
        """
        root, is_major_chord = self.parse_chord_name(chord)
        
        # Get semitone values
        key_semitone = self.NOTE_TO_SEMITONE.get(key_root, 0)
        chord_semitone = self.NOTE_TO_SEMITONE.get(root, 0)
        
        # Calculate interval from key root
        interval = (chord_semitone - key_semitone) % 12
        
        # Choose scale based on key type
        scale = self.MAJOR_SCALE if is_major_key else self.MINOR_SCALE
        
        # Find position in scale
        try:
            position = scale.index(interval)
        except ValueError:
            # Chord not in scale - try to find closest
            position = 0
        
        # Roman numerals (1-indexed)
        numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        roman = numerals[position]
        
        # Lowercase for minor chords
        if not is_major_chord:
            roman = roman.lower()
        
        return roman
    
    def convert_progression(self, chord_input: str) -> ChordProgression:
        """
        Convert chord progression input to Roman numerals.
        
        Args:
            chord_input: "Am C F G" or "Am-C-F-G" or "vi I IV V"
            
        Returns:
            ChordProgression with Roman numerals and metadata
        """
        # Clean input
        chord_input = chord_input.strip()
        
        # Split on spaces, hyphens, or commas
        chords = re.split(r'[\s\-,]+', chord_input)
        
        # Filter out empty strings and "BPM" markers
        chords = [c for c in chords if c and not c.lower().endswith('bpm') and '@' not in c]
        
        if not chords:
            raise ValueError("No chords found in input")
        
        # Check if already in Roman numerals
        if all(re.match(r'^(I|II|III|IV|V|VI|VII|i|ii|iii|iv|v|vi|vii)$', c) for c in chords):
            # Already Roman numerals - just return
            return ChordProgression(
                roman_numerals=chords,
                original_chords=chords,
                inferred_key='C',  # Default
                is_major=chords[0].isupper()
            )
        
        # Infer key from progression
        key_root, is_major_key = self.infer_key(chords)
        
        # Convert each chord to Roman numeral
        roman_numerals = [self.chord_to_roman(c, key_root, is_major_key) for c in chords]
        
        return ChordProgression(
            roman_numerals=roman_numerals,
            original_chords=chords,
            inferred_key=key_root,
            is_major=is_major_key
        )


# CLI for testing
if __name__ == "__main__":
    converter = ChordConverter()
    
    # Test cases
    test_inputs = [
        "C Am F G",
        "Am C F G",
        "D Bm G A",
        "I vi IV V",
        "vi I IV V"
    ]
    
    for test in test_inputs:
        result = converter.convert_progression(test)
        print(f"\nInput: {test}")
        print(f"  Roman: {' '.join(result.roman_numerals)}")
        print(f"  Key: {result.inferred_key} {'major' if result.is_major else 'minor'}")

