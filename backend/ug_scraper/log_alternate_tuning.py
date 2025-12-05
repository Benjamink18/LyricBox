"""
LOG ALTERNATE TUNING: Track songs that use non-standard tunings
================================================================
Logs songs with alternate tunings so we can analyze which tunings
are common and decide whether to implement support for them.
"""

from datetime import datetime
import os


def log_alternate_tuning(artist_name, track_name, tuning, capo=0):
    """
    Log a song that uses alternate (non-standard) tuning.
    
    Args:
        artist_name: Artist name
        track_name: Track name
        tuning: The alternate tuning (e.g., "D A D G A D", "Drop D")
        capo: Capo position (for additional context)
    """
    log_file = os.path.join(os.path.dirname(__file__), '../logs/chords_alternate_tuning.txt')
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format: timestamp | artist | track | tuning | capo
    log_entry = f"{timestamp} | {artist_name} | {track_name} | Tuning: {tuning}"
    if capo > 0:
        log_entry += f" | Capo: {capo}"
    log_entry += "\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(f"  → Logged to chords_alternate_tuning.txt")

