"""
LOG MISSING CHORDS: Log songs without official chords
Appends artist and track name to chords_not_found.txt.
"""

from datetime import datetime


def log_missing_chords(artist_name, track_name):
    """
    Log a song that doesn't have official chords on Ultimate Guitar.
    
    Args:
        artist_name: Artist name
        track_name: Track name
    
    Returns:
        None (appends to log file)
    """
    log_file = "../logs/chords_not_found.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {artist_name} - {track_name}\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    print(f"Logged to {log_file}: {artist_name} - {track_name}")

