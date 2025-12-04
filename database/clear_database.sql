-- CLEAR SUPABASE DATABASE
-- Run this FIRST to remove all existing tables
-- WARNING: This will delete ALL data!

-- Drop all existing tables (CASCADE removes dependencies)
DROP TABLE IF EXISTS song_concepts CASCADE;
DROP TABLE IF EXISTS song_youtube_data CASCADE;
DROP TABLE IF EXISTS song_rhyme_analysis CASCADE;
DROP TABLE IF EXISTS song_chords CASCADE;
DROP TABLE IF EXISTS song_lyrics CASCADE;
DROP TABLE IF EXISTS song_metadata CASCADE;
DROP TABLE IF EXISTS lyrics_lines CASCADE;
DROP TABLE IF EXISTS rhyme_pairs CASCADE;
DROP TABLE IF EXISTS line_rhyme_words CASCADE;
DROP TABLE IF EXISTS line_word_pairs CASCADE;
DROP TABLE IF EXISTS songs CASCADE;

-- Drop any existing functions
DROP FUNCTION IF EXISTS get_distinct_genres();
DROP FUNCTION IF EXISTS get_distinct_years();
DROP FUNCTION IF EXISTS get_distinct_artists();
DROP FUNCTION IF EXISTS get_full_lyrics(UUID);

-- Confirmation message
SELECT 'Database cleared successfully!' as status;

