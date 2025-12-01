#!/usr/bin/env python3
"""
Melody matching algorithm.
Combines Claude suggestions with Tidal BPM data and calculates match scores.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from melody_claude import SongSuggestion
from tidal_client import TidalTrack, TidalClient


@dataclass
class MelodyMatch:
    """A matched track with score and transpose info."""
    artist: str
    title: str
    original_key: str
    bpm: int
    tidal_id: str
    tidal_url: str
    match_score: int  # 0-100
    transpose_semitones: int  # +/- semitones to match target key
    claude_confidence: float
    claude_reason: str


class MelodyMatcher:
    """Score and rank Claude suggestions using Tidal data."""
    
    def __init__(self):
        """Initialize the matcher."""
        self.tidal = TidalClient()
    
    def calculate_bpm_score(self, track_bpm: int, target_bpm: int, tolerance: int = 15) -> int:
        """
        Score based on BPM proximity.
        
        Args:
            track_bpm: Track's actual BPM
            target_bpm: Target BPM
            tolerance: Acceptable BPM range
            
        Returns:
            Score 0-40 (0 = outside tolerance, 40 = exact match)
        """
        diff = abs(track_bpm - target_bpm)
        
        if diff > tolerance:
            return 0
        
        if diff == 0:
            return 40  # Perfect match
        
        # Linear scale: closer = higher score
        score = int(40 * (1 - (diff / tolerance)))
        return max(0, score)
    
    def calculate_total_score(self,
                             claude_confidence: float,
                             bpm_score: int) -> int:
        """
        Calculate total match score.
        
        Scoring breakdown:
            - Claude confidence: 0-50 points
            - BPM proximity: 0-40 points
            - Exact BPM match: +10 bonus points
            
        Args:
            claude_confidence: 0.0 to 1.0
            bpm_score: 0-40
            
        Returns:
            Total score 0-100
        """
        confidence_points = int(claude_confidence * 50)
        
        # Bonus for exact BPM match
        bonus = 10 if bpm_score == 40 else 0
        
        total = confidence_points + bpm_score + bonus
        return min(100, total)
    
    def match_songs(self,
                   suggestions: List[SongSuggestion],
                   target_bpm: int,
                   target_key: str,
                   bpm_tolerance: int = 15,
                   max_results: int = 10) -> List[MelodyMatch]:
        """
        Match Claude suggestions with Tidal data and calculate scores.
        
        Args:
            suggestions: Songs from Claude
            target_bpm: User's target BPM
            target_key: User's input key ('C major', 'A minor', etc.)
            bpm_tolerance: BPM matching tolerance
            max_results: Maximum results to return
            
        Returns:
            List of scored and ranked matches
        """
        if not self.tidal.is_authenticated():
            print("⚠️  Not authenticated with Tidal")
            return []
        
        matches = []
        
        for suggestion in suggestions:
            print(f"🔍 Searching Tidal: {suggestion.artist} - {suggestion.title}")
            
            # Search Tidal
            tidal_track = self.tidal.search_track(suggestion.artist, suggestion.title)
            
            if not tidal_track:
                print(f"  ❌ Not found on Tidal")
                continue
            
            # Check if BPM is available
            if not tidal_track.bpm:
                print(f"  ⚠️  No BPM data available")
                # Could still include but with lower score
                track_bpm = target_bpm  # Assume target BPM if not available
                bpm_score = 20  # Reduced score
            else:
                track_bpm = tidal_track.bpm
                bpm_score = self.calculate_bpm_score(track_bpm, target_bpm, bpm_tolerance)
            
            # Skip if BPM is too far off
            if bpm_score == 0:
                print(f"  ❌ BPM {track_bpm} outside tolerance ({target_bpm} ± {bpm_tolerance})")
                continue
            
            # Calculate transpose
            track_key = tidal_track.key or suggestion.original_key
            transpose = self.tidal.calculate_transpose_semitones(track_key, target_key)
            
            # Calculate total score
            total_score = self.calculate_total_score(suggestion.confidence, bpm_score)
            
            matches.append(MelodyMatch(
                artist=tidal_track.artist,
                title=tidal_track.title,
                original_key=track_key,
                bpm=track_bpm,
                tidal_id=tidal_track.id,
                tidal_url=tidal_track.url,
                match_score=total_score,
                transpose_semitones=transpose,
                claude_confidence=suggestion.confidence,
                claude_reason=suggestion.reason
            ))
            
            print(f"  ✅ Score: {total_score} | BPM: {track_bpm} | Transpose: {transpose:+d}")
        
        # Sort by score (highest first)
        matches.sort(key=lambda m: m.match_score, reverse=True)
        
        # Return top N
        return matches[:max_results]
    
    def create_playlist_with_guide(self,
                                  matches: List[MelodyMatch],
                                  playlist_name: str,
                                  target_key: str,
                                  target_bpm: int) -> Optional[str]:
        """
        Create Tidal playlist with transpose guide in description.
        
        Args:
            matches: Matched tracks to add
            playlist_name: Name for playlist
            target_key: Backing track key
            target_bpm: Target BPM
            
        Returns:
            Playlist URL if successful
        """
        if not matches:
            print("⚠️  No matches to add to playlist")
            return None
        
        # Build description with transpose guide
        description_lines = [
            f"Backing Track Key: {target_key} | Target BPM: {target_bpm}",
            "",
            "TRANSPOSE GUIDE:"
        ]
        
        for i, match in enumerate(matches, 1):
            transpose_str = f"{match.transpose_semitones:+d}" if match.transpose_semitones != 0 else "0 (perfect!)"
            description_lines.append(
                f"{i}. {match.artist} - {match.title} [{match.original_key}]: {transpose_str} semitones"
            )
        
        description = '\n'.join(description_lines)
        
        # Create playlist
        track_ids = [m.tidal_id for m in matches]
        playlist_url = self.tidal.create_playlist(playlist_name, description, track_ids)
        
        return playlist_url


# CLI for testing
if __name__ == "__main__":
    from chord_converter import ChordConverter
    from melody_claude import MelodyClaude
    
    # Test full pipeline
    converter = ChordConverter()
    progression = converter.convert_progression("Am C F G")
    
    claude = MelodyClaude()
    suggestions = claude.find_matching_songs(
        progression.roman_numerals,
        progression.original_chords,
        {'bpm': 120, 'bpm_tolerance': 15, 'genres': ['Pop']}
    )
    
    matcher = MelodyMatcher()
    matches = matcher.match_songs(
        suggestions,
        target_bpm=120,
        target_key=f"{progression.inferred_key} {'major' if progression.is_major else 'minor'}",
        bpm_tolerance=15,
        max_results=10
    )
    
    print(f"\n🎵 Top Matches:")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.artist} - {match.title}")
        print(f"   Score: {match.match_score}/100 | BPM: {match.bpm} | Transpose: {match.transpose_semitones:+d}")

