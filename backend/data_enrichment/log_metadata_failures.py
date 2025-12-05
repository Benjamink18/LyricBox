"""
LOG METADATA FAILURES: Log songs where both Musixmatch and MusicBrainz failed
These songs will NOT be added to the database.
"""

from datetime import datetime


def log_metadata_failure(artist_name, track_name):
    """
    Log a song that has no metadata from any source.
    
    Args:
        artist_name: Artist name
        track_name: Track name
    
    Returns:
        None (appends to log file)
    """
    log_file = "../logs/metadata_not_found.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {artist_name} - {track_name} (no sources)\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    print(f"  Logged to {log_file}: {artist_name} - {track_name}")

