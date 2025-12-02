#!/usr/bin/env python3
"""
Claude-based song discovery for Melody feature.
Uses Claude to find songs with matching CHORUS chord progressions.
Claude provides ALL song data - no external API needed for metadata.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class MelodySong:
    """A song found by Claude."""
    rank: int              # 1-10, Claude's match confidence ranking
    song_name: str
    artist_name: str
    chorus_chords: str     # The actual chords used in the chorus (e.g., "Am C F G")
    bpm: int
    genre: str
    year: int
    
    def to_dict(self) -> dict:
        return asdict(self)


def build_search_prompt(
    roman_numerals: List[str],
    original_chords: List[str],
    key: str,
    bpm: int,
    bpm_tolerance: int,
    time_signature: str,
    # Optional filters
    genres: List[str] = None,
    year_start: int = None,
    year_end: int = None,
    chart_position: str = None,  # e.g., "Top 10", "Top 20", "Top 50"
    artist_style: str = None
) -> str:
    """Build the Claude prompt for finding matching songs."""
    
    progression_str = ' → '.join(roman_numerals)
    chord_str = ' → '.join(original_chords)
    bpm_min = bpm - bpm_tolerance
    bpm_max = bpm + bpm_tolerance
    
    # Build optional filters section
    filter_lines = []
    if genres:
        filter_lines.append(f"- Genres: {', '.join(genres)}")
    if year_start and year_end:
        filter_lines.append(f"- Release year range: {year_start}-{year_end}")
    elif year_start:
        filter_lines.append(f"- Released after: {year_start}")
    elif year_end:
        filter_lines.append(f"- Released before: {year_end}")
    if chart_position:
        filter_lines.append(f"- Chart position: {chart_position} hits only")
    if artist_style:
        filter_lines.append(f"- Style similar to: {artist_style}")
    
    filters_section = ""
    if filter_lines:
        filters_section = "\nAdditional filters:\n" + "\n".join(filter_lines)
    
    prompt = f"""Find 10 songs where the CHORUS uses this chord progression:

Roman numerals: {progression_str}
Original chords: {chord_str}
Key: {key}
Target BPM: {bpm} (acceptable range: {bpm_min}-{bpm_max})
Time Signature: {time_signature}{filters_section}

CRITICAL REQUIREMENTS:
1. The chord progression MUST match the CHORUS specifically - NOT verses, bridges, or other sections
2. Match the HARMONIC function (Roman numerals), not necessarily the exact chord names
3. BPM should be within the specified range
4. Only include songs you are confident about

For each song, provide:
- rank: Your confidence ranking 1-10 (1 = best match)
- song_name: The song title
- artist_name: The artist/band name
- chorus_chords: The actual chord progression used in that song's chorus
- bpm: The actual BPM of the song
- genre: The primary genre
- year: Release year

Return ONLY a JSON array, no other text:
[
  {{
    "rank": 1,
    "song_name": "Example Song",
    "artist_name": "Example Artist",
    "chorus_chords": "Am C F G",
    "bpm": 120,
    "genre": "Pop",
    "year": 2020
  }}
]"""
    
    return prompt


def build_more_like_these_prompt(
    original_criteria: Dict[str, Any],
    liked_songs: List[MelodySong],
    excluded_songs: List[str]  # List of "Artist - Title" strings
) -> str:
    """Build prompt for finding more songs similar to liked ones."""
    
    # Format the original search criteria
    progression = ' → '.join(original_criteria.get('roman_numerals', []))
    key = original_criteria.get('key', 'Unknown')
    bpm = original_criteria.get('bpm', 120)
    bpm_tolerance = original_criteria.get('bpm_tolerance', 10)
    time_sig = original_criteria.get('time_signature', '4/4')
    
    # Format liked songs
    liked_lines = []
    for song in liked_songs:
        liked_lines.append(f"- {song.artist_name} - {song.song_name} (BPM: {song.bpm}, Genre: {song.genre}, Chords: {song.chorus_chords})")
    liked_section = "\n".join(liked_lines)
    
    # Format excluded songs
    excluded_section = "\n".join(f"- {s}" for s in excluded_songs) if excluded_songs else "None"
    
    prompt = f"""Find 10 MORE songs similar to the user's selections.

ORIGINAL SEARCH CRITERIA:
- Chord progression (Roman numerals): {progression}
- Key: {key}
- Target BPM: {bpm} (±{bpm_tolerance})
- Time Signature: {time_sig}

THE USER LIKED THESE SONGS:
{liked_section}

DO NOT SUGGEST THESE SONGS (already seen/rejected):
{excluded_section}

Find songs that:
1. Have similar CHORUS chord progressions
2. Are in a similar style/vibe to the liked songs
3. Match the original BPM range
4. DO NOT repeat any previously suggested songs

Return ONLY a JSON array with the same format:
[
  {{
    "rank": 1,
    "song_name": "Song Title",
    "artist_name": "Artist Name",
    "chorus_chords": "Am C F G",
    "bpm": 120,
    "genre": "Pop",
    "year": 2020
  }}
]"""
    
    return prompt


def parse_claude_response(response_text: str) -> List[MelodySong]:
    """Parse Claude's JSON response into MelodySong objects."""
    
    # Extract JSON from response (handles if Claude adds extra text)
    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
    if not json_match:
        print("⚠️  Could not find JSON array in Claude response")
        return []
    
    try:
        data = json.loads(json_match.group())
        
        songs = []
        for item in data:
            songs.append(MelodySong(
                rank=int(item.get('rank', 10)),
                song_name=item.get('song_name', ''),
                artist_name=item.get('artist_name', ''),
                chorus_chords=item.get('chorus_chords', ''),
                bpm=int(item.get('bpm', 0)),
                genre=item.get('genre', ''),
                year=int(item.get('year', 0))
            ))
        
        # Sort by rank
        songs.sort(key=lambda s: s.rank)
        return songs
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse JSON: {e}")
        return []


def find_matching_songs(
    roman_numerals: List[str],
    original_chords: List[str],
    key: str,
    bpm: int,
    bpm_tolerance: int = 10,
    time_signature: str = "4/4",
    genres: List[str] = None,
    year_start: int = None,
    year_end: int = None,
    chart_position: str = None,
    artist_style: str = None
) -> List[MelodySong]:
    """
    Use Claude to find songs with matching chorus progressions.
    
    Returns:
        List of MelodySong objects sorted by rank
    """
    prompt = build_search_prompt(
        roman_numerals=roman_numerals,
        original_chords=original_chords,
        key=key,
        bpm=bpm,
        bpm_tolerance=bpm_tolerance,
        time_signature=time_signature,
        genres=genres,
        year_start=year_start,
        year_end=year_end,
        chart_position=chart_position,
        artist_style=artist_style
    )
    
    print("🎵 Asking Claude for song suggestions...")
    
    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        songs = parse_claude_response(response_text)
        
        print(f"✅ Claude found {len(songs)} matching songs")
        return songs
        
    except Exception as e:
        print(f"⚠️  Claude request failed: {e}")
        return []


def find_more_like_these(
    original_criteria: Dict[str, Any],
    liked_songs: List[MelodySong],
    excluded_songs: List[str]
) -> List[MelodySong]:
    """
    Find more songs similar to the ones the user liked.
    
    Args:
        original_criteria: The original search parameters
        liked_songs: Songs the user wants more like
        excluded_songs: List of "Artist - Title" strings to exclude
        
    Returns:
        List of new MelodySong suggestions
    """
    prompt = build_more_like_these_prompt(
        original_criteria=original_criteria,
        liked_songs=liked_songs,
        excluded_songs=excluded_songs
    )
    
    print("🎵 Asking Claude for more songs like your selections...")
    
    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        songs = parse_claude_response(response_text)
        
        print(f"✅ Claude found {len(songs)} more similar songs")
        return songs
        
    except Exception as e:
        print(f"⚠️  Claude request failed: {e}")
        return []


# CLI for testing
if __name__ == "__main__":
    from chord_converter import convert_progression
    
    # Test search
    progression = convert_progression("Am C F G")
    print(f"Searching for songs with: {' → '.join(progression.roman_numerals)}")
    print(f"Key: {progression.key}")
    
    songs = find_matching_songs(
        roman_numerals=progression.roman_numerals,
        original_chords=progression.original_chords,
        key=progression.key,
        bpm=120,
        bpm_tolerance=15,
        time_signature="4/4",
        genres=["Pop", "R&B"],
        year_start=2015,
        year_end=2024
    )
    
    print(f"\n🎵 Found {len(songs)} songs:")
    for song in songs:
        print(f"  {song.rank}. {song.artist_name} - {song.song_name}")
        print(f"     Chords: {song.chorus_chords} | BPM: {song.bpm} | {song.genre} ({song.year})")

