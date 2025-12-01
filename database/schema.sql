-- LyricBox Database Schema
-- Run this in your Supabase SQL Editor

-- Drop existing tables if they exist (for fresh start)
DROP TABLE IF EXISTS rhyme_pairs CASCADE;
DROP TABLE IF EXISTS lyrics_lines CASCADE;
DROP TABLE IF EXISTS songs CASCADE;

-- Songs table with Billboard metadata
CREATE TABLE songs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  genius_id INTEGER UNIQUE,
  year INTEGER,
  billboard_rank INTEGER,
  genre TEXT,
  lyrics_raw TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster filtering
CREATE INDEX idx_songs_year ON songs(year);
CREATE INDEX idx_songs_genre ON songs(genre);
CREATE INDEX idx_songs_artist ON songs(artist);
CREATE INDEX idx_songs_rank ON songs(billboard_rank);

-- Lyrics lines for searching
CREATE TABLE lyrics_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
  line_number INTEGER NOT NULL,
  line_text TEXT NOT NULL,
  line_text_clean TEXT NOT NULL,
  last_word TEXT,
  last_word_phonetic TEXT,
  context_before TEXT,
  context_after TEXT,
  context_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast searching
CREATE INDEX idx_lyrics_last_word ON lyrics_lines(last_word);
CREATE INDEX idx_lyrics_song_id ON lyrics_lines(song_id);
CREATE INDEX idx_lyrics_phonetic ON lyrics_lines(last_word_phonetic);
CREATE INDEX idx_lyrics_context_hash ON lyrics_lines(context_hash);
CREATE INDEX idx_lyrics_line_text ON lyrics_lines USING gin(to_tsvector('english', line_text));

-- Pre-computed rhyme pairs (optional, for faster lookups)
CREATE TABLE rhyme_pairs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  word TEXT NOT NULL,
  phonetic TEXT NOT NULL,
  rhyme_sound TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rhyme_word ON rhyme_pairs(word);
CREATE INDEX idx_rhyme_sound ON rhyme_pairs(rhyme_sound);

-- Enable Row Level Security
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE lyrics_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE rhyme_pairs ENABLE ROW LEVEL SECURITY;

-- Public read access (Cloudflare Access handles auth)
CREATE POLICY "Allow public read access on songs"
  ON songs FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow public read access on lyrics_lines"
  ON lyrics_lines FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow public read access on rhyme_pairs"
  ON rhyme_pairs FOR SELECT
  TO anon
  USING (true);

-- Service role has full access for imports
CREATE POLICY "Allow service role full access on songs"
  ON songs FOR ALL
  TO service_role
  USING (true);

CREATE POLICY "Allow service role full access on lyrics_lines"
  ON lyrics_lines FOR ALL
  TO service_role
  USING (true);

CREATE POLICY "Allow service role full access on rhyme_pairs"
  ON rhyme_pairs FOR ALL
  TO service_role
  USING (true);

-- Function to get distinct genres
CREATE OR REPLACE FUNCTION get_distinct_genres()
RETURNS TABLE(genre TEXT) AS $$
BEGIN
  RETURN QUERY SELECT DISTINCT s.genre FROM songs s WHERE s.genre IS NOT NULL ORDER BY s.genre;
END;
$$ LANGUAGE plpgsql;

-- Function to get distinct years
CREATE OR REPLACE FUNCTION get_distinct_years()
RETURNS TABLE(year INTEGER) AS $$
BEGIN
  RETURN QUERY SELECT DISTINCT s.year FROM songs s WHERE s.year IS NOT NULL ORDER BY s.year DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get distinct artists  
CREATE OR REPLACE FUNCTION get_distinct_artists()
RETURNS TABLE(artist TEXT) AS $$
BEGIN
  RETURN QUERY SELECT DISTINCT s.artist FROM songs s ORDER BY s.artist;
END;
$$ LANGUAGE plpgsql;

-- Concepts table for AI-analyzed themes
CREATE TABLE IF NOT EXISTS song_concepts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
  themes TEXT[],
  metaphors JSONB,
  tone TEXT,
  imagery TEXT[],
  story_arc TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_concepts_song_id ON song_concepts(song_id);
CREATE INDEX idx_concepts_themes ON song_concepts USING gin(themes);
CREATE INDEX idx_concepts_imagery ON song_concepts USING gin(imagery);

-- Enable RLS on concepts
ALTER TABLE song_concepts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access on song_concepts"
  ON song_concepts FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow service role full access on song_concepts"
  ON song_concepts FOR ALL
  TO service_role
  USING (true);
