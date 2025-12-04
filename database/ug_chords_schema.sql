-- LyricBox Ultimate Guitar Scraper Database Schema
-- Run this in your Supabase SQL Editor
-- Creates table for chord data with 6 versions per section

-- ============================================================================
-- SONG_CHORDS TABLE (Ultimate Guitar Scraper Target)
-- ============================================================================
-- Stores chord data by section (one row per section)
-- 6 versions: original, simplified, transposed to C, transposed simplified,
--             roman numerals, roman simplified

CREATE TABLE IF NOT EXISTS song_chords (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  song_id UUID NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  section_name TEXT NOT NULL,  -- "Intro", "Verse 1", "Chorus", etc.
  tonality TEXT,               -- Musical key from UG (e.g., "G", "Am")
  
  -- 6 chord versions (stored as TEXT[] arrays)
  chords_original TEXT[],
  chords_original_simplified TEXT[],
  chords_transposed_c TEXT[],
  chords_transposed_c_simplified TEXT[],
  chords_roman TEXT[],
  chords_roman_simplified TEXT[],
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Standard lookup indexes
CREATE INDEX IF NOT EXISTS idx_chords_song_id ON song_chords(song_id);
CREATE INDEX IF NOT EXISTS idx_chords_section ON song_chords(section_name);
CREATE INDEX IF NOT EXISTS idx_chords_tonality ON song_chords(tonality);

-- GIN indexes for array searching (enables "contains" queries)
CREATE INDEX IF NOT EXISTS idx_chords_original 
  ON song_chords USING gin(chords_original);
  
CREATE INDEX IF NOT EXISTS idx_chords_transposed 
  ON song_chords USING gin(chords_transposed_c);
  
CREATE INDEX IF NOT EXISTS idx_chords_roman 
  ON song_chords USING gin(chords_roman);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE song_chords ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow public read on song_chords"
  ON song_chords FOR SELECT
  TO anon
  USING (true);

-- Service role full access (for UG scraper)
CREATE POLICY "Allow service role full access on song_chords"
  ON song_chords FOR ALL
  TO service_role
  USING (true);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get all chord progressions for a song (concatenated by section)
CREATE OR REPLACE FUNCTION get_chord_progressions(p_song_id UUID, p_version TEXT DEFAULT 'original')
RETURNS TABLE(section_name TEXT, chords TEXT[]) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    sc.section_name,
    CASE p_version
      WHEN 'original' THEN sc.chords_original
      WHEN 'simplified' THEN sc.chords_original_simplified
      WHEN 'transposed' THEN sc.chords_transposed_c
      WHEN 'transposed_simplified' THEN sc.chords_transposed_c_simplified
      WHEN 'roman' THEN sc.chords_roman
      WHEN 'roman_simplified' THEN sc.chords_roman_simplified
      ELSE sc.chords_original
    END as chords
  FROM song_chords sc
  WHERE sc.song_id = p_song_id
  ORDER BY sc.created_at;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- Example 1: Insert chord data for a section
-- INSERT INTO song_chords (
--   song_id, section_name, tonality,
--   chords_original, chords_original_simplified,
--   chords_transposed_c, chords_transposed_c_simplified,
--   chords_roman, chords_roman_simplified
-- )
-- VALUES (
--   'your-song-id-here',
--   'Verse 1',
--   'G',
--   ARRAY['G', 'Cadd9', 'Asus4'],
--   ARRAY['G', 'C', 'A'],
--   ARRAY['C', 'Fadd9', 'Dsus4'],
--   ARRAY['C', 'F', 'D'],
--   ARRAY['I', 'IVadd9', 'IIsus4'],
--   ARRAY['I', 'IV', 'II']
-- );

-- Example 2: Get all chords for a song
-- SELECT section_name, tonality, chords_original
-- FROM song_chords
-- WHERE song_id = 'your-song-id-here'
-- ORDER BY created_at;

-- Example 3: Search for songs with specific chord progression
-- SELECT DISTINCT s.track_name, s.artist_name
-- FROM songs s
-- JOIN song_chords sc ON s.song_id = sc.song_id
-- WHERE sc.chords_transposed_c @> ARRAY['C', 'F', 'G'];  -- Contains C, F, G

-- Example 4: Get chord progressions in different formats
-- SELECT * FROM get_chord_progressions('your-song-id-here', 'roman');

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. One row per section (e.g., multiple rows for multiple choruses)
-- 2. All 6 chord versions stored in same row for easy querying
-- 3. TEXT[] arrays allow native PostgreSQL array operations
-- 4. GIN indexes enable fast "contains" queries (e.g., find all songs with I-IV-V)
-- 5. tonality from Ultimate Guitar may differ from musical_key in songs table
--    (UG tonality is more specific to the tab)
-- 6. If UG tonality found, update songs.musical_key with this value

