#!/usr/bin/env python3
"""
Tidal API client for Melody feature.
Handles OAuth, track search, BPM retrieval, and playlist creation.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import tidalapi
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TidalTrack:
    """Track information from Tidal."""
    id: str
    artist: str
    title: str
    bpm: Optional[int]
    key: Optional[str]  # 'C major', 'A minor', etc.
    duration: int  # seconds
    url: str


class TidalClient:
    """Tidal API client for track search and playlist creation."""
    
    def __init__(self):
        """Initialize Tidal session."""
        self.session = tidalapi.Session()
        self.session_file = os.path.join(os.path.dirname(__file__), 'tidal_session.json')
        self.auth_future = None
        
        # Try to load existing session
        if os.path.exists(self.session_file):
            try:
                self.session.load_oauth_session_from_file(self.session_file)
                print("✅ Loaded existing Tidal session")
            except Exception as e:
                print(f"⚠️  Could not load session: {e}")
    
    def authenticate_device(self) -> Dict[str, str]:
        """
        Start device authentication flow.
        
        Returns:
            Dict with 'verification_url' and 'user_code' for user to visit
        """
        login, self.auth_future = self.session.login_oauth()
        
        return {
            'verification_url': f"https://{login.verification_uri_complete}",
            'user_code': login.user_code,
            'message': f"Go to {login.verification_uri_complete} and enter code: {login.user_code}"
        }
    
    def check_auth_complete(self) -> bool:
        """
        Check if device auth flow is complete.
        
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # If we have a pending future, check if it's done
            if self.auth_future and not self.auth_future.done():
                print("⏳ OAuth future not done yet...")
                return False
            
            print("🔍 Checking login status...")
            if self.session.check_login():
                # Save session for future use
                print(f"💾 Saving session to {self.session_file}")
                self.session.save_oauth_session_to_file(self.session_file)
                print("✅ Tidal authentication successful - session saved!")
                self.auth_future = None
                return True
            else:
                print("❌ Session check_login returned False")
        except Exception as e:
            print(f"⚠️  Auth check failed: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        try:
            return self.session.check_login()
        except:
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Tidal and remove session file."""
        try:
            # Remove session file
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(f"🗑️  Deleted session file: {self.session_file}")
            
            # Clear the session
            self.session = tidalapi.Session()
            self.auth_future = None
            print("✅ Disconnected from Tidal")
            return True
        except Exception as e:
            print(f"⚠️  Error disconnecting: {e}")
            return False
    
    def search_track(self, artist: str, title: str) -> Optional[TidalTrack]:
        """
        Search for a track on Tidal.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            TidalTrack if found, None otherwise
        """
        if not self.is_authenticated():
            print("⚠️  Not authenticated with Tidal")
            return None
        
        try:
            # Search for track
            query = f"{artist} {title}"
            results = self.session.search(query, models=[tidalapi.media.Track])
            
            if not results or not results.get('tracks'):
                print(f"⚠️  No Tidal results for: {query}")
                return None
            
            # Get first result
            track = results['tracks'][0]
            
            # Extract BPM and key if available
            # Note: Tidal API may not always provide BPM/key in basic search
            # May need to call track.get_metadata() or similar
            bpm = None
            key = None
            
            # Try to get audio features if available
            try:
                # Some Tidal implementations have get_url() or get_audio_features()
                # This varies by library version
                pass
            except:
                pass
            
            return TidalTrack(
                id=str(track.id),
                artist=track.artist.name,
                title=track.name,
                bpm=bpm,
                key=key,
                duration=track.duration,
                url=f"https://listen.tidal.com/track/{track.id}"
            )
            
        except Exception as e:
            print(f"⚠️  Tidal search failed for {artist} - {title}: {e}")
            return None
    
    def calculate_transpose_semitones(self, from_key: str, to_key: str) -> int:
        """
        Calculate semitones to transpose from one key to another.
        
        Args:
            from_key: Original key (e.g., "C major", "A minor")
            to_key: Target key
            
        Returns:
            Semitones to transpose (+/- 11)
        """
        # Map note names to semitones
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1,
            'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4,
            'F': 5, 'F#': 6, 'Gb': 6,
            'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10,
            'B': 11
        }
        
        # Extract root notes (first letter + possible sharp/flat)
        def extract_root(key_str):
            match = re.match(r'^([A-G][#b]?)', key_str)
            return match.group(1) if match else 'C'
        
        from_root = extract_root(from_key)
        to_root = extract_root(to_key)
        
        from_semitone = note_map.get(from_root, 0)
        to_semitone = note_map.get(to_root, 0)
        
        # Calculate difference
        diff = (to_semitone - from_semitone) % 12
        
        # Convert to +/- range (-6 to +6 is more intuitive than 0 to 11)
        if diff > 6:
            diff = diff - 12
        
        return diff
    
    def create_playlist(self, 
                       name: str,
                       description: str,
                       track_ids: List[str]) -> Optional[str]:
        """
        Create a Tidal playlist.
        
        Args:
            name: Playlist name
            description: Playlist description (include transpose guide)
            track_ids: List of Tidal track IDs
            
        Returns:
            Playlist URL if successful, None otherwise
        """
        if not self.is_authenticated():
            print("⚠️  Not authenticated with Tidal")
            return None
        
        try:
            # Get user playlists
            user = self.session.user
            playlist = user.create_playlist(name, description)
            
            # Add tracks
            for track_id in track_ids:
                track = self.session.track(track_id)
                playlist.add([track])
            
            print(f"✅ Created playlist: {name} with {len(track_ids)} tracks")
            return f"https://listen.tidal.com/playlist/{playlist.id}"
            
        except Exception as e:
            print(f"⚠️  Failed to create playlist: {e}")
            return None


# CLI for testing
if __name__ == "__main__":
    client = TidalClient()
    
    if not client.is_authenticated():
        print("Not authenticated. Starting device auth...")
        auth_info = client.authenticate_device()
        print(f"\n{auth_info['message']}")
        print("\nWaiting for authentication...")
        
        import time
        for i in range(60):  # Wait up to 60 seconds
            time.sleep(1)
            if client.check_auth_complete():
                break
    
    if client.is_authenticated():
        print("\n✅ Authenticated with Tidal")
        
        # Test search
        track = client.search_track("Dua Lipa", "Levitating")
        if track:
            print(f"\nFound: {track.artist} - {track.title}")
            print(f"BPM: {track.bpm or 'N/A'}")
            print(f"Key: {track.key or 'N/A'}")
            print(f"URL: {track.url}")
        
        # Test transpose calculation
        semitones = client.calculate_transpose_semitones("C major", "F major")
        print(f"\nTranspose from C to F: {semitones:+d} semitones")

