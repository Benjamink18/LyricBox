-- ============================================================================
-- CLEAR ALL EXISTING TABLES - Run this FIRST in Supabase
-- ============================================================================
-- This drops ALL existing tables and views to start fresh

-- Drop views first
DROP VIEW IF EXISTS songs_complete CASCADE;
DROP VIEW IF EXISTS artists_summary CASCADE;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS youtube_data CASCADE;
DROP TABLE IF EXISTS song_youtube_data CASCADE;
DROP TABLE IF EXISTS song_concepts CASCADE;
DROP TABLE IF EXISTS song_rhyme_analysis CASCADE;
DROP TABLE IF EXISTS song_chords CASCADE;
DROP TABLE IF EXISTS song_lyrics CASCADE;
DROP TABLE IF EXISTS songs CASCADE;
DROP TABLE IF EXISTS albums CASCADE;
DROP TABLE IF EXISTS artists CASCADE;

-- Confirm cleanup
SELECT 'All tables and views dropped successfully!' as status;

