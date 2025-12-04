"""
READ SONGS CSV: Load songs from CSV file
Converts CSV data to list format for enrichment pipeline.
"""

import csv


def read_songs_from_csv(csv_path):
    """
    Read songs from CSV file.
    Returns: List of dicts with 'artist', 'track', 'peak_position'
    """
    songs = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows
            if not row.get('track_name') or not row.get('artist_name'):
                continue
                
            songs.append({
                'artist': row['artist_name'],
                'track': row['track_name'],
                'peak_position': row['peak_position']
            })
    
    return songs


if __name__ == "__main__":
    # Test reading the CSV
    songs = read_songs_from_csv('songs_list.csv')
    print(f"Loaded {len(songs)} songs:")
    for song in songs[:3]:  # Show first 3
        print(f"  {song['artist']} - {song['track']} (#{song['peak_position']})")

