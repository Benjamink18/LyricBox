"""
LOG MUSICBRAINZ PARTIAL METADATA: Log songs using MusicBrainz fallback
These songs are in the database but missing BPM, key, and moods.
Use this log to manually enrich data later.
"""

from datetime import datetime


def log_musicbrainz_partial(artist_name, track_name):
    """
    Log a song that used MusicBrainz (partial metadata).
    
    Args:
        artist_name: Artist name
        track_name: Track name
    
    Returns:
        None (appends to log file)
    """
    log_file = "../logs/musicbrainz_partial_metadata.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {artist_name} - {track_name} (missing: BPM, key, moods)\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    print(f"  Logged to {log_file} for manual enrichment")

