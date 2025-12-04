"""
MUSICBRAINZ MODULE
Fallback metadata source when Musixmatch fails.
Provides: genres, release_date (but NOT: BPM, key, moods)
"""

from .get_metadata import get_metadata

__all__ = ['get_metadata']

