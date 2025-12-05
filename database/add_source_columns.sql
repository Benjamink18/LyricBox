-- Add source tracking columns to songs and song_lyrics tables
-- Run this in your Supabase SQL Editor

-- Add metadata_source to songs table
-- Tracks whether metadata came from 'musixmatch' or 'musicbrainz'
ALTER TABLE songs 
ADD COLUMN IF NOT EXISTS metadata_source TEXT;

-- Add lyrics_source to song_lyrics table
-- Tracks where lyrics came from (e.g., 'genius', 'musixmatch', 'lyrics.ovh')
ALTER TABLE song_lyrics 
ADD COLUMN IF NOT EXISTS lyrics_source TEXT;

-- Add indexes for filtering by source
CREATE INDEX IF NOT EXISTS idx_songs_metadata_source ON songs(metadata_source);
CREATE INDEX IF NOT EXISTS idx_lyrics_source ON song_lyrics(lyrics_source);

