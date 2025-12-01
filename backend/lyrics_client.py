#!/usr/bin/env python3
"""
Multi-source lyrics client with automatic fallback.

Priority order:
1. Musixmatch (reliable, but has 500/day limit on free tier)
2. Lyrics.ovh (free API, unlimited, clean data)
3. LRCLIB (free API, unlimited, crowdsourced)
"""

import os
import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LyricsResult:
    """Standardized lyrics result."""
    lyrics: str
    source: str
    artist: str
    title: str
    success: bool = True
    error: Optional[str] = None


class MultiSourceLyricsClient:
    """Lyrics client with multiple sources and automatic fallback."""
    
    def __init__(self):
        self.musixmatch_key = os.getenv("MUSIXMATCH_API_KEY")
    
    def get_lyrics(self, artist: str, title: str) -> LyricsResult:
        """
        Get lyrics with automatic fallback through multiple sources.
        
        Returns LyricsResult with lyrics and source info.
        """
        errors = []
        
        # Try Musixmatch first (most reliable when quota available)
        if self.musixmatch_key:
            try:
                result = self._fetch_musixmatch(artist, title)
                if result.success:
                    return result
                errors.append(f"Musixmatch: {result.error}")
            except Exception as e:
                errors.append(f"Musixmatch: {str(e)}")
        
        # Try Lyrics.ovh second (free, unlimited, clean)
        try:
            result = self._fetch_lyrics_ovh(artist, title)
            if result.success:
                return result
            errors.append(f"Lyrics.ovh: {result.error}")
        except Exception as e:
            errors.append(f"Lyrics.ovh: {str(e)}")
        
        # Try LRCLIB last (free, unlimited, crowdsourced)
        try:
            result = self._fetch_lrclib(artist, title)
            if result.success:
                return result
            errors.append(f"LRCLIB: {result.error}")
        except Exception as e:
            errors.append(f"LRCLIB: {str(e)}")
        
        # All sources failed
        return LyricsResult(
            lyrics="",
            source="none",
            artist=artist,
            title=title,
            success=False,
            error=" | ".join(errors)
        )
    
    def _fetch_musixmatch(self, artist: str, title: str) -> LyricsResult:
        """Fetch from Musixmatch API."""
        try:
            # Search for track
            search_url = "https://api.musixmatch.com/ws/1.1/track.search"
            search_params = {
                "apikey": self.musixmatch_key,
                "q_artist": artist,
                "q_track": title,
                "f_has_lyrics": 1,
                "s_track_rating": "desc"
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["message"]["header"]["status_code"] != 200:
                return LyricsResult(
                    lyrics="",
                    source="musixmatch",
                    artist=artist,
                    title=title,
                    success=False,
                    error=f"API error: {data['message']['header']['status_code']}"
                )
            
            tracks = data["message"]["body"]["track_list"]
            if not tracks:
                return LyricsResult(
                    lyrics="",
                    source="musixmatch",
                    artist=artist,
                    title=title,
                    success=False,
                    error="Track not found"
                )
            
            track_id = tracks[0]["track"]["track_id"]
            
            # Get lyrics
            lyrics_url = "https://api.musixmatch.com/ws/1.1/track.lyrics.get"
            lyrics_params = {
                "apikey": self.musixmatch_key,
                "track_id": track_id
            }
            
            response = requests.get(lyrics_url, params=lyrics_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["message"]["header"]["status_code"] != 200:
                return LyricsResult(
                    lyrics="",
                    source="musixmatch",
                    artist=artist,
                    title=title,
                    success=False,
                    error=f"Lyrics API error: {data['message']['header']['status_code']}"
                )
            
            lyrics_body = data["message"]["body"]["lyrics"]["lyrics_body"]
            
            # Remove Musixmatch footer
            if "******* This Lyrics is NOT for Commercial use *******" in lyrics_body:
                lyrics_body = lyrics_body.split("*******")[0].strip()
            
            return LyricsResult(
                lyrics=lyrics_body,
                source="musixmatch",
                artist=artist,
                title=title,
                success=True
            )
            
        except Exception as e:
            return LyricsResult(
                lyrics="",
                source="musixmatch",
                artist=artist,
                title=title,
                success=False,
                error=str(e)
            )
    
    def _fetch_lyrics_ovh(self, artist: str, title: str) -> LyricsResult:
        """Fetch from Lyrics.ovh free API."""
        try:
            url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "lyrics" not in data:
                return LyricsResult(
                    lyrics="",
                    source="lyrics.ovh",
                    artist=artist,
                    title=title,
                    success=False,
                    error="No lyrics in response"
                )
            
            return LyricsResult(
                lyrics=data["lyrics"],
                source="lyrics.ovh",
                artist=artist,
                title=title,
                success=True
            )
            
        except Exception as e:
            return LyricsResult(
                lyrics="",
                source="lyrics.ovh",
                artist=artist,
                title=title,
                success=False,
                error=str(e)
            )
    
    def _fetch_lrclib(self, artist: str, title: str) -> LyricsResult:
        """Fetch from LRCLIB free API."""
        try:
            url = "https://lrclib.net/api/get"
            params = {
                "artist_name": artist,
                "track_name": title
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # LRCLIB returns plain lyrics or synced lyrics
            lyrics = data.get("plainLyrics") or data.get("syncedLyrics", "")
            
            if not lyrics:
                return LyricsResult(
                    lyrics="",
                    source="lrclib",
                    artist=artist,
                    title=title,
                    success=False,
                    error="No lyrics in response"
                )
            
            # If synced lyrics, remove timestamps
            if lyrics.startswith("["):
                lines = []
                for line in lyrics.split("\n"):
                    # Remove timestamp format [00:12.34]
                    if "]" in line:
                        clean_line = line.split("]", 1)[1].strip()
                        if clean_line:
                            lines.append(clean_line)
                lyrics = "\n".join(lines)
            
            return LyricsResult(
                lyrics=lyrics,
                source="lrclib",
                artist=artist,
                title=title,
                success=True
            )
            
        except Exception as e:
            return LyricsResult(
                lyrics="",
                source="lrclib",
                artist=artist,
                title=title,
                success=False,
                error=str(e)
            )


# Convenience function
def get_lyrics(artist: str, title: str) -> LyricsResult:
    """Get lyrics from any available source."""
    client = MultiSourceLyricsClient()
    return client.get_lyrics(artist, title)


if __name__ == "__main__":
    # Test the client
    client = MultiSourceLyricsClient()
    
    test_songs = [
        ("Hozier", "Too Sweet"),
        ("Taylor Swift", "Anti-Hero"),
        ("The Weeknd", "Blinding Lights"),
        ("Kendrick Lamar", "HUMBLE.")
    ]
    
    print("Testing multi-source lyrics client (3 sources)...\n")
    print("Sources: Musixmatch → Lyrics.ovh → LRCLIB\n")
    
    for artist, title in test_songs:
        print(f"🎵 {artist} - {title}")
        result = client.get_lyrics(artist, title)
        
        if result.success:
            preview = result.lyrics[:80].replace("\n", " ")
            print(f"   ✅ Success via {result.source.upper()}")
            print(f"   📝 {preview}...")
            print(f"   📊 {len(result.lyrics)} characters")
        else:
            print(f"   ❌ Failed: {result.error}")
        
        print()

