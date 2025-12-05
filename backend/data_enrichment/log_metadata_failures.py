"""
LOG METADATA FAILURES: Log songs where metadata fetch failed
These songs will NOT be added to the database.
"""

from datetime import datetime


def log_metadata_failure(artist_name, track_name, reason="unknown"):
    """
    Log a song that failed to get metadata.
    
    Args:
        artist_name: Artist name
        track_name: Track name
        reason: Why it failed (e.g., "no_genres", "no_bpm")
    
    Returns:
        None (appends to log file)
    """
    log_file = "../logs/metadata_not_found.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {artist_name} - {track_name} (reason: {reason})\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    print(f"  Logged to {log_file}: {artist_name} - {track_name} ({reason})")

