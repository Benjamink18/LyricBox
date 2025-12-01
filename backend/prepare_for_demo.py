#!/usr/bin/env python3
"""Prepare database for demo."""

import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("=" * 60)
print("🎯 PREPARING DATABASE FOR DEMO")
print("=" * 60)
print()

# Load clean 2025 dataset
print("📋 Loading billboard_2025_clean.csv...")
df = pd.read_csv("billboard_2025_clean.csv")
print(f"   Found {len(df)} songs in clean dataset")
print()

target_songs = set()
for _, row in df.iterrows():
    key = (row['title'].lower().strip(), row['artist'].lower().strip())
    target_songs.add(key)

print(f"✅ Target: {len(target_songs)} unique songs")
print()

# Check current database
print("🔍 Checking current database...")
all_db_songs = supabase.table('songs').select('id, title, artist, year, genre, billboard_rank, lyrics_raw').execute()
print(f"   Current database: {len(all_db_songs.data)} songs")
print()

# Identify songs to remove
songs_to_remove = []
songs_to_keep = {}
for song in all_db_songs.data:
    key = (song['title'].lower().strip(), song['artist'].lower().strip())
    if key in target_songs:
        songs_to_keep[key] = song
    else:
        songs_to_remove.append(song)

print(f"✅ Songs to keep: {len(songs_to_keep)}")
print(f"🗑️  Songs to remove: {len(songs_to_remove)}")
print()

# Remove songs
if songs_to_remove:
    print("🗑️  Removing extra songs...")
    for i, song in enumerate(songs_to_remove):
        if (i + 1) % 50 == 0:
            print(f"   Removed {i + 1}/{len(songs_to_remove)}...")
        
        supabase.table('rhyme_pairs').delete().eq('song_id', song['id']).execute()
        supabase.table('song_analysis').delete().eq('song_id', song['id']).execute()
        supabase.table('songs').delete().eq('id', song['id']).execute()
    
    print(f"✅ Removed {len(songs_to_remove)} songs")
    print()

# Missing songs
missing_songs = []
for key in target_songs:
    if key not in songs_to_keep:
        missing_songs.append(key)

print(f"📊 Missing songs: {len(missing_songs)}")
print()

# Check completeness
print("🔍 Checking data completeness...")
incomplete_songs = []
for key, song in songs_to_keep.items():
    issues = []
    if not song.get('lyrics_raw') or len(song['lyrics_raw'].strip()) < 50:
        issues.append('lyrics')
    if not song.get('year'):
        issues.append('year')
    if not song.get('genre'):
        issues.append('genre')
    if song.get('billboard_rank') is None:
        issues.append('rank')
    
    if issues:
        incomplete_songs.append({'song': song, 'issues': issues})

print(f"   Complete: {len(songs_to_keep) - len(incomplete_songs)}")
print(f"   Incomplete: {len(incomplete_songs)}")
print()

if incomplete_songs[:5]:
    print("⚠️  Songs with missing data:")
    for item in incomplete_songs[:5]:
        song = item['song']
        print(f"   - {song['title']} by {song['artist']}: missing {', '.join(item['issues'])}")
    print()

print("=" * 60)
print("📊 FINAL STATUS:")
print("=" * 60)
print(f"✅ Target: {len(target_songs)} songs (billboard_2025_clean.csv)")
print(f"📊 In database: {len(songs_to_keep)}")
print(f"📥 Need to import: {len(missing_songs)}")
print(f"⚠️  Need data fixes: {len(incomplete_songs)}")
print("=" * 60)
print()

if missing_songs:
    print(f"⏭️  NEXT: Import {len(missing_songs)} missing songs (~{len(missing_songs) * 30 / 60:.0f} min)")
if incomplete_songs:
    print(f"⚠️  THEN: Fix {len(incomplete_songs)} songs with missing data")

print()
