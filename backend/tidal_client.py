#!/usr/bin/env python3
"""
Tidal API client for Melody feature.
Uses tidalapi v0.8.3 for authentication and playlist creation ONLY.
BPM/key data comes from Claude, not Tidal.

Based on tidalapi documentation: https://tidalapi.netlify.app/
"""

import os
from typing import List, Dict, Any, Optional
import tidalapi
from dotenv import load_dotenv

load_dotenv()

print(f"🎵 tidalapi version: {tidalapi.__version__}")


class TidalClient:
    """Tidal API client for playlist creation."""
    
    def __init__(self):
        """Initialize Tidal session."""
        self.session = tidalapi.Session()
        
        # Use /tmp for Railway compatibility, local path for development
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            self.session_file = '/tmp/tidal_session.json'
        else:
            self.session_file = os.path.join(os.path.dirname(__file__), 'tidal_session.json')
        
        self.auth_future = None
        
        print(f"📁 Session file: {self.session_file}")
        
        # Try to load existing session
        if os.path.exists(self.session_file):
            try:
                print(f"🔄 Loading existing Tidal session...")
                self.session.load_oauth_session_from_file(self.session_file)
                if self.session.check_login():
                    print("✅ Existing session is valid")
                else:
                    print("⚠️  Session loaded but check_login() returned False")
            except Exception as e:
                print(f"⚠️  Could not load session: {type(e).__name__}: {e}")
    
    def authenticate_device(self) -> Dict[str, str]:
        """
        Start device authentication flow.
        User visits URL and enters code to authorize.
        
        Returns:
            Dict with 'verification_url', 'user_code', 'message'
        """
        try:
            print("🔐 Initiating Tidal OAuth device flow...")
            login, self.auth_future = self.session.login_oauth()
            
            # The verification URL and code
            url = login.verification_uri_complete
            code = login.user_code
            
            print(f"✅ OAuth initiated")
            print(f"   URL: https://{url}")
            print(f"   Code: {code}")
            
            return {
                'verification_url': f"https://{url}",
                'user_code': code,
                'message': f"Visit link.tidal.com and enter code: {code}"
            }
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"❌ OAuth initiation failed: {error_msg}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Tidal OAuth failed: {error_msg}")
    
    def check_auth_complete(self) -> bool:
        """
        Check if device auth flow is complete.
        Call this periodically after starting auth.
        
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # If we have a pending future, check if done
            if self.auth_future:
                if hasattr(self.auth_future, 'done') and not self.auth_future.done():
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
                print("❌ session.check_login() returned False")
                return False
                
        except Exception as e:
            print(f"⚠️  Auth check failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with Tidal."""
        try:
            return self.session.check_login()
        except Exception as e:
            print(f"⚠️  is_authenticated check failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Tidal and remove session file."""
        try:
            # Remove session file
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(f"🗑️  Deleted session file: {self.session_file}")
            
            # Reset session
            self.session = tidalapi.Session()
            self.auth_future = None
            print("✅ Disconnected from Tidal")
            return True
        except Exception as e:
            print(f"⚠️  Error disconnecting: {e}")
            return False
    
    def search_track(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Search for a track on Tidal.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            Dict with track info (id, name, artist, url) or None
        """
        if not self.is_authenticated():
            print("⚠️  Not authenticated with Tidal")
            return None
        
        try:
            query = f"{artist} {title}"
            results = self.session.search(query, models=[tidalapi.media.Track])
            
            if not results or not results.get('tracks'):
                print(f"⚠️  No Tidal results for: {query}")
                return None
            
            track = results['tracks'][0]
            
            return {
                'id': str(track.id),
                'name': track.name,
                'artist': track.artist.name,
                'url': f"https://listen.tidal.com/track/{track.id}"
            }
            
        except Exception as e:
            print(f"⚠️  Tidal search failed: {e}")
            return None
    
    def create_playlist(
        self,
        name: str,
        description: str,
        songs: List[Dict[str, str]]  # List of {'artist': str, 'title': str}
    ) -> Optional[str]:
        """
        Create a Tidal playlist with the given songs.
        
        Args:
            name: Playlist name
            description: Playlist description
            songs: List of dicts with 'artist' and 'title' keys
            
        Returns:
            Playlist URL if successful, None otherwise
        """
        if not self.is_authenticated():
            print("⚠️  Not authenticated with Tidal")
            return None
        
        try:
            # Get user for playlist creation
            user = self.session.user
            
            # Create playlist
            print(f"📝 Creating playlist: {name}")
            playlist = user.create_playlist(name, description)
            
            # Search and add each track one by one
            added_count = 0
            track_ids = []
            
            for song in songs:
                track_info = self.search_track(song['artist'], song['title'])
                if track_info:
                    track_ids.append(track_info['id'])
                    print(f"  ✅ Found: {song['artist']} - {song['title']} (ID: {track_info['id']})")
                else:
                    print(f"  ❌ Not found: {song['artist']} - {song['title']}")
            
            # Add all found tracks to the playlist
            if track_ids:
                try:
                    print(f"📥 Adding {len(track_ids)} tracks to playlist...")
                    playlist.add(track_ids)
                    added_count = len(track_ids)
                    print(f"  ✅ Successfully added {added_count} tracks")
                except Exception as e:
                    print(f"  ⚠️  Bulk add failed: {e}")
                    # Try adding one by one as fallback
                    print("  🔄 Trying one-by-one...")
                    for track_id in track_ids:
                        try:
                            playlist.add([track_id])
                            added_count += 1
                        except Exception as e2:
                            print(f"    ❌ Failed to add track {track_id}: {e2}")
            
            playlist_url = f"https://listen.tidal.com/playlist/{playlist.id}"
            print(f"✅ Created playlist with {added_count}/{len(songs)} tracks")
            print(f"   URL: {playlist_url}")
            
            return playlist_url
            
        except Exception as e:
            print(f"⚠️  Failed to create playlist: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the Tidal client state."""
        return {
            'tidalapi_version': tidalapi.__version__,
            'session_file': self.session_file,
            'session_file_exists': os.path.exists(self.session_file),
            'session_file_writable': os.access(os.path.dirname(self.session_file) or '.', os.W_OK),
            'is_authenticated': self.is_authenticated(),
            'has_auth_future': self.auth_future is not None,
            'railway_env': os.environ.get('RAILWAY_ENVIRONMENT', 'not set')
        }


# CLI for testing
if __name__ == "__main__":
    client = TidalClient()
    
    print("\n🔍 Debug info:")
    for key, value in client.get_debug_info().items():
        print(f"  {key}: {value}")
    
    if not client.is_authenticated():
        print("\n🔐 Not authenticated. Starting device auth...")
        auth_info = client.authenticate_device()
        print(f"\n{auth_info['message']}")
        print("\nWaiting for authentication...")
        
        import time
        for i in range(60):  # Wait up to 60 seconds
            time.sleep(2)
            print(f"  Checking... ({i+1}/30)")
            if client.check_auth_complete():
                break
    
    if client.is_authenticated():
        print("\n✅ Authenticated with Tidal!")
        
        # Test search
        result = client.search_track("Dua Lipa", "Levitating")
        if result:
            print(f"\n🔍 Found: {result['artist']} - {result['name']}")
            print(f"   URL: {result['url']}")

