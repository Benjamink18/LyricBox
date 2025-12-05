-- ============================================================================
-- APPLY SCHEMA V2 - COMPLETE MIGRATION SCRIPT
-- ============================================================================
-- Run this entire file in Supabase SQL Editor
-- This will: 1) Clear all existing data, 2) Drop old tables, 3) Create new schema
-- ============================================================================

-- Step 1: Clear all existing data (reverse order due to foreign keys)
DROP TABLE IF EXISTS youtube_data CASCADE;
DROP TABLE IF EXISTS song_youtube_data CASCADE;  -- Old name (in case it exists)
DROP TABLE IF EXISTS song_concepts CASCADE;
DROP TABLE IF EXISTS song_rhyme_analysis CASCADE;
DROP TABLE IF EXISTS song_chords CASCADE;
DROP TABLE IF EXISTS song_lyrics CASCADE;
DROP TABLE IF EXISTS songs CASCADE;

-- Step 2: Create new normalized tables

-- ============================================================================
-- TABLE 1: ARTISTS
-- ============================================================================
CREATE TABLE artists (
  artist_id BIGSERIAL PRIMARY KEY,
  artist_name TEXT NOT NULL UNIQUE,
  artist_genres TEXT[],
  artist_country VARCHAR(5),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_artists_name ON artists(artist_name);
CREATE INDEX idx_artists_country ON artists(artist_country);

-- ============================================================================
-- TABLE 2: ALBUMS
-- ============================================================================
CREATE TABLE albums (
  album_id BIGSERIAL PRIMARY KEY,
  album_title TEXT NOT NULL,
  album_year VARCHAR(10),
  artist_id BIGINT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(album_title, artist_id)
);

CREATE INDEX idx_albums_artist_id ON albums(artist_id);
CREATE INDEX idx_albums_year ON albums(album_year);

-- ============================================================================
-- TABLE 3: SONGS (NORMALIZED)
-- ============================================================================
CREATE TABLE songs (
  song_id BIGSERIAL PRIMARY KEY,
  track_name TEXT NOT NULL,
  
  -- Foreign Keys
  artist_id BIGINT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
  album_id BIGINT REFERENCES albums(album_id) ON DELETE SET NULL,
  
  -- Billboard Data
  peak_position INTEGER,
  first_chart_date DATE,
  
  -- Musixmatch Data
  song_genres TEXT[],
  metadata_source TEXT,
  
  -- GetSongBPM Data (ALL 10 fields)
  bpm INTEGER,
  time_signature VARCHAR(10),
  musical_key VARCHAR(10),
  camelot_key VARCHAR(10),
  danceability INTEGER,
  acousticness INTEGER,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(track_name, artist_id)
);

CREATE INDEX idx_songs_artist_id ON songs(artist_id);
CREATE INDEX idx_songs_album_id ON songs(album_id);
CREATE INDEX idx_songs_track_name ON songs(track_name);
CREATE INDEX idx_songs_first_chart_date ON songs(first_chart_date);
CREATE INDEX idx_songs_peak_position ON songs(peak_position);
CREATE INDEX idx_songs_bpm ON songs(bpm);
CREATE INDEX idx_songs_danceability ON songs(danceability);
CREATE INDEX idx_songs_acousticness ON songs(acousticness);

-- ============================================================================
-- TABLE 4: SONG_LYRICS
-- ============================================================================
CREATE TABLE song_lyrics (
  lyrics_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  section_name TEXT NOT NULL,
  lyrics_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lyrics_song_id ON song_lyrics(song_id);

-- ============================================================================
-- TABLE 5: SONG_CHORDS
-- ============================================================================
CREATE TABLE song_chords (
  chord_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  section_name TEXT NOT NULL,
  chords_original TEXT,
  chords_original_simplified TEXT,
  chords_transposed_c TEXT,
  chords_transposed_c_simplified TEXT,
  chords_roman TEXT,
  chords_roman_simplified TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chords_song_id ON song_chords(song_id);

-- ============================================================================
-- TABLE 6: SONG_RHYME_ANALYSIS
-- ============================================================================
CREATE TABLE song_rhyme_analysis (
  rhyme_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  section_name TEXT NOT NULL,
  rhyme_scheme TEXT NOT NULL,
  rhyme_analysis JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rhyme_song_id ON song_rhyme_analysis(song_id);

-- ============================================================================
-- TABLE 7: SONG_CONCEPTS
-- ============================================================================
CREATE TABLE song_concepts (
  concept_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  themes TEXT[],
  concepts JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(song_id)
);

CREATE INDEX idx_concepts_song_id ON song_concepts(song_id);

-- ============================================================================
-- TABLE 8: YOUTUBE_DATA (Real Talk Feature - Separate from Songs)
-- ============================================================================
CREATE TABLE youtube_data (
  youtube_id BIGSERIAL PRIMARY KEY,
  video_url TEXT,
  channel_name TEXT,
  transcript TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_youtube_video_url ON youtube_data(video_url);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Complete song information with artist and album names
CREATE VIEW songs_complete AS
SELECT 
  s.song_id,
  s.track_name,
  a.artist_name,
  a.artist_genres,
  a.artist_country,
  al.album_title,
  al.album_year,
  s.peak_position,
  s.first_chart_date,
  s.song_genres,
  s.bpm,
  s.time_signature,
  s.musical_key,
  s.camelot_key,
  s.danceability,
  s.acousticness,
  s.metadata_source,
  s.created_at
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
LEFT JOIN albums al ON s.album_id = al.album_id;

-- View: Artist summary with song count
CREATE VIEW artists_summary AS
SELECT 
  a.artist_id,
  a.artist_name,
  a.artist_genres,
  a.artist_country,
  COUNT(s.song_id) as song_count,
  ARRAY_AGG(s.track_name ORDER BY s.peak_position) as songs
FROM artists a
LEFT JOIN songs s ON a.artist_id = s.artist_id
GROUP BY a.artist_id, a.artist_name, a.artist_genres, a.artist_country;

-- ============================================================================
-- COMPLETE!
-- ============================================================================

