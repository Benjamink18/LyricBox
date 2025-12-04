"""
PROCESS CHORDS: Convert chords to all 6 versions
=================================================
Takes a list of chords and the key, returns:
- Original chords
- Original simplified
- Transposed to C
- Transposed to C simplified
- Roman numerals
- Roman numerals simplified
"""

from .simplify_chord import simplify_chord
from .transpose_to_c import transpose_to_c
from .convert_to_roman import convert_to_roman


def process_chords(tonality, chords_original):
    """
    Process chords into all 6 versions for storage.
    
    Args:
        tonality: The original key (e.g., "G", "Am")
        chords_original: List of chords (e.g., ["G", "D", "Em7", "Cadd9"])
    
    Returns:
        Dictionary with all 6 versions:
        {
            'original': ["G", "D", "Em7", "Cadd9"],
            'original_simple': ["G", "D", "Em", "C"],
            'in_c': ["C", "G", "Am7", "Fadd9"],
            'in_c_simple': ["C", "G", "Am", "F"],
            'roman': ["I", "V", "vi7", "IVadd9"],
            'roman_simple': ["I", "V", "vi", "IV"]
        }
    """
    
    # Initialize all 6 lists
    result = {
        'original': [],
        'original_simple': [],
        'in_c': [],
        'in_c_simple': [],
        'roman': [],
        'roman_simple': []
    }
    
    # Process each chord
    for chord in chords_original:
        
        # 1. Original (already have it)
        result['original'].append(chord)
        
        # 2. Original simplified
        simple = simplify_chord(chord)
        result['original_simple'].append(simple)
        
        # 3. Transpose to C (full chord)
        in_c = transpose_to_c(tonality, chord)
        result['in_c'].append(in_c)
        
        # 4. Transpose to C (simplified) - more efficient!
        in_c_simple = transpose_to_c(tonality, simple)
        result['in_c_simple'].append(in_c_simple)
        
        # 5. Roman numeral (full)
        roman = convert_to_roman(in_c)
        result['roman'].append(roman)
        
        # 6. Roman numeral (simplified)
        roman_simple = convert_to_roman(in_c_simple)
        result['roman_simple'].append(roman_simple)
    
    return result

