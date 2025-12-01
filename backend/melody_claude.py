#!/usr/bin/env python3
"""
Claude-based song discovery for Melody feature.
Uses Claude's knowledge to find songs with matching chorus chord progressions.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class SongSuggestion:
    """A song suggested by Claude."""
    artist: str
    title: str
    original_key: str
    confidence: float  # 0.0 to 1.0
    reason: str


class MelodyClaude:
    """Use Claude to find songs with matching chorus progressions."""
    
    def build_prompt(self, 
                    roman_numerals: List[str],
                    original_chords: List[str],
                    filters: Dict[str, Any]) -> str:
        """
        Build Claude prompt with chord progression and filters.
        
        Args:
            roman_numerals: ['vi', 'I', 'IV', 'V']
            original_chords: ['Am', 'C', 'F', 'G']
            filters: {
                'bpm': 120,
                'bpm_tolerance': 15,
                'time_signature': '4/4',
                'year_start': 2010,
                'year_end': 2024,
                'genres': ['Pop', 'R&B'],
                'chart': 'Billboard Hot 100',
                'artist_style': 'similar to Drake'
            }
        """
        progression_str = ' → '.join(roman_numerals)
        chord_str = ' → '.join(original_chords)
        
        # Build filter description
        filter_parts = []
        
        if filters.get('bpm'):
            bpm_min = filters['bpm'] - filters.get('bpm_tolerance', 15)
            bpm_max = filters['bpm'] + filters.get('bpm_tolerance', 15)
            filter_parts.append(f"Tempo: {bpm_min}-{bpm_max} BPM (target: {filters['bpm']})")
        
        if filters.get('time_signature'):
            filter_parts.append(f"Time signature: {filters['time_signature']}")
        
        if filters.get('year_start') and filters.get('year_end'):
            filter_parts.append(f"Released: {filters['year_start']}-{filters['year_end']}")
        
        if filters.get('genres'):
            genres_str = ', '.join(filters['genres'])
            filter_parts.append(f"Genres: {genres_str}")
        
        if filters.get('chart'):
            filter_parts.append(f"Chart preference: {filters['chart']}")
        
        if filters.get('artist_style'):
            filter_parts.append(f"Style: {filters['artist_style']}")
        
        filters_str = '\n'.join(f"- {f}" for f in filter_parts)
        
        prompt = f"""You are a music expert helping a DJ find songs for mashups.

Find songs where the CHORUS (or main hook) uses this chord progression:
**{progression_str}**

Original chord names: {chord_str}

FILTERS:
{filters_str if filter_parts else "- No specific filters"}

TASK:
Find up to 20 well-known songs that match these criteria. Focus on popular songs that DJs would recognize.

IMPORTANT:
- Only include songs where you're confident the CHORUS uses this exact progression
- Provide the song's original key (e.g., "C major", "A minor")
- Rate your confidence 0.0 (uncertain) to 1.0 (very confident)
- Explain briefly why it matches

RESPONSE FORMAT (JSON only):
[
  {{
    "artist": "Artist Name",
    "title": "Song Title",
    "original_key": "C major",
    "confidence": 0.9,
    "reason": "Chorus uses vi-I-IV-V in C major, Billboard hit 2019"
  }}
]

Return ONLY the JSON array, no other text."""

        return prompt
    
    def parse_claude_response(self, response_text: str) -> List[SongSuggestion]:
        """
        Parse Claude's JSON response into SongSuggestion objects.
        
        Args:
            response_text: Claude's response text
            
        Returns:
            List of SongSuggestion objects
        """
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            print("⚠️  Could not find JSON in Claude response")
            return []
        
        try:
            data = json.loads(json_match.group())
            
            suggestions = []
            for item in data:
                suggestions.append(SongSuggestion(
                    artist=item.get('artist', ''),
                    title=item.get('title', ''),
                    original_key=item.get('original_key', 'C major'),
                    confidence=float(item.get('confidence', 0.5)),
                    reason=item.get('reason', '')
                ))
            
            return suggestions
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse JSON: {e}")
            return []
    
    def find_matching_songs(self,
                           roman_numerals: List[str],
                           original_chords: List[str],
                           filters: Dict[str, Any]) -> List[SongSuggestion]:
        """
        Use Claude to find songs with matching chorus progressions.
        
        Args:
            roman_numerals: Key-agnostic progression
            original_chords: Original chord names
            filters: Search filters
            
        Returns:
            List of song suggestions from Claude
        """
        prompt = self.build_prompt(roman_numerals, original_chords, filters)
        
        print("🎵 Asking Claude for song suggestions...")
        
        try:
            response = anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            suggestions = self.parse_claude_response(response_text)
            
            print(f"✅ Claude suggested {len(suggestions)} songs")
            return suggestions
            
        except Exception as e:
            print(f"⚠️  Claude request failed: {e}")
            return []


# CLI for testing
if __name__ == "__main__":
    from chord_converter import ChordConverter
    
    # Test progression
    converter = ChordConverter()
    progression = converter.convert_progression("Am C F G")
    
    print(f"Chord progression: {' '.join(progression.original_chords)}")
    print(f"Roman numerals: {' '.join(progression.roman_numerals)}")
    print(f"Key: {progression.inferred_key} {'major' if progression.is_major else 'minor'}")
    print("\nSearching for matches...")
    
    # Test Claude query
    claude = MelodyClaude()
    filters = {
        'bpm': 120,
        'bpm_tolerance': 15,
        'year_start': 2015,
        'year_end': 2024,
        'genres': ['Pop', 'R&B']
    }
    
    suggestions = claude.find_matching_songs(
        progression.roman_numerals,
        progression.original_chords,
        filters
    )
    
    print(f"\nFound {len(suggestions)} suggestions:")
    for i, song in enumerate(suggestions[:5], 1):
        print(f"{i}. {song.artist} - {song.title}")
        print(f"   Key: {song.original_key} | Confidence: {song.confidence:.1%}")
        print(f"   Reason: {song.reason}")

