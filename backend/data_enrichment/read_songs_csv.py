"""
READ SONGS CSV: Load songs from CSV file
Converts CSV data to list format for enrichment pipeline.
Extracts year from first_chart_date field.
"""

import csv


def read_songs_from_csv(csv_path):
    """
    Read songs from CSV file.
    
    Args:
        csv_path: Path to CSV file with columns:
                  - track_name (or title)
                  - artist_name (or artist)
                  - peak_position
                  - first_chart_date (optional, e.g., "2025-01-04")
    
    Returns: List of dicts with 'artist', 'track', 'peak_position', 'year'
    """
    songs = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle both column name formats
            track = row.get('track_name') or row.get('title')
            artist = row.get('artist_name') or row.get('artist')
            
            # Skip empty rows
            if not track or not artist:
                continue
            
            # Get first_chart_date as-is (YYYY-MM-DD format for SQL DATE type)
            first_chart_date = row.get('first_chart_date') if 'first_chart_date' in row else None
                
            songs.append({
                'artist': artist,
                'track': track,
                'peak_position': row.get('peak_position'),
                'first_chart_date': first_chart_date
            })
    
    return songs


if __name__ == "__main__":
    # Test reading the CSV
    songs = read_songs_from_csv('songs_list.csv')
    print(f"Loaded {len(songs)} songs:")
    for song in songs[:3]:  # Show first 3
        print(f"  {song['artist']} - {song['track']} (#{song['peak_position']}, Year: {song['year']})")

