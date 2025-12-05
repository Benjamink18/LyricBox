-- ============================================================================
-- LYRICBOX DATABASE SCHEMA V2 - NORMALIZED
-- ============================================================================
-- Version: 2.0
-- Date: December 5, 2024
-- Description: Fully normalized schema with separate artists and albums tables
-- Status: DOCUMENTATION ONLY - To be implemented when rebuilding from scratch
-- ============================================================================

-- ============================================================================
-- TABLE 1: ARTISTS
-- ============================================================================
-- Primary table for artist information
-- One unique record per artist (no duplicates)
-- Populated from GetSongBPM API during enrichment

CREATE TABLE artists (
  -- Primary Key
  artist_id BIGSERIAL PRIMARY KEY,
  
  -- Core Fields
  artist_name TEXT NOT NULL UNIQUE,  -- Unique artist name (from CSV)
  
  -- GetSongBPM Artist Data
  artist_genres TEXT[],              -- Array of genres: ["funk", "pop", "soul"]
                                     -- Source: GetSongBPM artist.genres
                                     -- NOTE: Different from song_genres (Musixmatch)
  
  artist_country VARCHAR(5),         -- Country code: "US", "GB", "CA", etc.
                                     -- Source: GetSongBPM artist.from
  
  getsongbpm_artist_id VARCHAR(50),  -- GetSongBPM's internal artist ID
                                     -- Source: GetSongBPM artist.id
                                     -- Example: "GQ3" for Michael Jackson
  
  musicbrainz_id UUID,               -- MusicBrainz database ID
                                     -- Source: GetSongBPM artist.mbid
                                     -- Used for linking to external services
  
  getsongbpm_uri TEXT,               -- GetSongBPM artist page URL
                                     -- Source: GetSongBPM artist.uri
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for artists table
CREATE INDEX idx_artists_name ON artists(artist_name);
CREATE INDEX idx_artists_country ON artists(artist_country);

-- ============================================================================
-- TABLE 2: ALBUMS
-- ============================================================================
-- Album information linked to artists
-- Unique per artist (same album by different artists = different records)

CREATE TABLE albums (
  -- Primary Key
  album_id BIGSERIAL PRIMARY KEY,
  
  -- Core Fields
  album_title TEXT NOT NULL,         -- Album name: "Thriller", "Voodoo", etc.
  album_year VARCHAR(10),            -- Release year: "1982", "2000", etc.
                                     -- Source: GetSongBPM album.year OR CSV first_chart_date
  
  -- Foreign Key
  artist_id BIGINT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
  
  -- GetSongBPM Album Data
  getsongbpm_album_uri TEXT,         -- GetSongBPM album page URL
                                     -- Source: GetSongBPM album.uri
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(album_title, artist_id)     -- Same album can't exist twice for same artist
);

-- Indexes for albums table
CREATE INDEX idx_albums_artist_id ON albums(artist_id);
CREATE INDEX idx_albums_year ON albums(album_year);

-- ============================================================================
-- TABLE 3: SONGS (MASTER TABLE - UPDATED)
-- ============================================================================
-- Main song catalog - fully normalized with foreign keys to artists and albums
-- Created when metadata is successfully fetched

CREATE TABLE songs (
  -- Primary Key
  song_id BIGSERIAL PRIMARY KEY,
  
  -- Core Fields
  track_name TEXT NOT NULL,          -- Song title
  
  -- Foreign Keys (NORMALIZED - no more artist_name or album_title!)
  artist_id BIGINT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
  album_id BIGINT REFERENCES albums(album_id) ON DELETE SET NULL,
  
  -- -------------------------------------------------------------------------
  -- BILLBOARD DATA (from CSV)
  -- -------------------------------------------------------------------------
  peak_position INTEGER,             -- Highest Billboard chart position
  first_chart_date DATE,             -- First date on Billboard charts
  chart_year INTEGER,                -- Year extracted from first_chart_date
  
  -- -------------------------------------------------------------------------
  -- MUSIXMATCH METADATA
  -- -------------------------------------------------------------------------
  song_genres TEXT[],                -- Song-level genres from Musixmatch
                                     -- Example: ["pop", "dance", "electronic"]
                                     -- NOTE: Different from artist_genres!
  
  metadata_source TEXT,              -- 'musixmatch' or 'musicbrainz'
  
  -- -------------------------------------------------------------------------
  -- GETSONGBPM DATA (Musical Characteristics)
  -- -------------------------------------------------------------------------
  bpm INTEGER,                       -- Beats per minute (tempo)
                                     -- Source: GetSongBPM tempo field
                                     -- Example: 116 for Billie Jean
  
  time_signature VARCHAR(10),        -- Time signature
                                     -- Source: GetSongBPM time_sig
                                     -- Example: "4/4", "3/4", "6/8"
  
  musical_key VARCHAR(10),           -- Musical key notation
                                     -- Source: GetSongBPM key_of (BACKUP - UG is primary)
                                     -- Example: "F♯m", "C", "D♭"
                                     -- Used when Ultimate Guitar chords not found
  
  camelot_key VARCHAR(10),           -- Camelot wheel notation (for DJ mixing)
                                     -- Source: GetSongBPM open_key
                                     -- Example: "4m", "8d", "10m"
  
  -- -------------------------------------------------------------------------
  -- GETSONGBPM AUDIO ANALYSIS (0-100 scales)
  -- -------------------------------------------------------------------------
  danceability INTEGER,              -- How suitable for dancing (0-100)
                                     -- Source: GetSongBPM danceability
                                     -- Example: 92 = very danceable (Billie Jean)
                                     --          51 = moderate (Someone You Loved)
  
  acousticness INTEGER,              -- Acoustic vs electronic (0-100)
                                     -- Source: GetSongBPM acousticness
                                     -- Example: 3 = electronic (Billie Jean)
                                     --          76 = acoustic (Someone You Loved)
  
  -- -------------------------------------------------------------------------
  -- METADATA
  -- -------------------------------------------------------------------------
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(track_name, artist_id)      -- No duplicate songs per artist
);

-- Indexes for songs table
CREATE INDEX idx_songs_artist_id ON songs(artist_id);
CREATE INDEX idx_songs_album_id ON songs(album_id);
CREATE INDEX idx_songs_track_name ON songs(track_name);
CREATE INDEX idx_songs_chart_year ON songs(chart_year);
CREATE INDEX idx_songs_peak_position ON songs(peak_position);
CREATE INDEX idx_songs_bpm ON songs(bpm);
CREATE INDEX idx_songs_danceability ON songs(danceability);
CREATE INDEX idx_songs_acousticness ON songs(acousticness);
CREATE INDEX idx_songs_metadata_source ON songs(metadata_source);

-- ============================================================================
-- TABLE 4: SONG_LYRICS (Unchanged)
-- ============================================================================
-- Lyrics text organized by song sections
-- One row per section per song

CREATE TABLE song_lyrics (
  lyrics_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  
  section_name TEXT NOT NULL,        -- "Verse 1", "Chorus", "Bridge", etc.
  lyrics_text TEXT NOT NULL,         -- Actual lyrics for this section
  lyrics_source TEXT,                -- 'genius', 'musixmatch', 'lyrics.ovh', etc.
  
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lyrics_song_id ON song_lyrics(song_id);
CREATE INDEX idx_lyrics_source ON song_lyrics(lyrics_source);

-- ============================================================================
-- TABLE 5: SONG_CHORDS (Unchanged)
-- ============================================================================
-- Chord progressions from Ultimate Guitar
-- One row per section per song with 6 chord versions

CREATE TABLE song_chords (
  chord_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  
  section_name TEXT NOT NULL,        -- "Verse 1", "Chorus", "Bridge", etc.
  tonality TEXT,                     -- Original key from Ultimate Guitar
  
  -- 6 chord versions
  chords_original TEXT,              -- Original chords from tab
  chords_original_simplified TEXT,   -- Simplified (basic triads only)
  chords_transposed_c TEXT,          -- Transposed to key of C
  chords_transposed_c_simplified TEXT, -- Transposed to C + simplified
  chords_roman TEXT,                 -- Roman numeral notation
  chords_roman_simplified TEXT,      -- Roman numerals simplified
  
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chords_song_id ON song_chords(song_id);

-- ============================================================================
-- TABLE 6: SONG_RHYME_ANALYSIS (Unchanged)
-- ============================================================================
-- AI-generated rhyme scheme analysis by Claude
-- One row per section per song

CREATE TABLE song_rhyme_analysis (
  rhyme_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  
  section_name TEXT NOT NULL,        -- "Verse 1", "Chorus", "Bridge", etc.
  rhyme_scheme TEXT NOT NULL,        -- e.g., "ABAB", "AABB"
  rhyme_analysis JSONB NOT NULL,     -- Detailed rhyme breakdown from Claude
  
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rhyme_song_id ON song_rhyme_analysis(song_id);

-- ============================================================================
-- TABLE 7: SONG_CONCEPTS (Unchanged)
-- ============================================================================
-- AI-generated thematic analysis by Claude
-- One row per song

CREATE TABLE song_concepts (
  concept_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  
  themes TEXT[],                     -- Main themes/topics
  concepts JSONB NOT NULL,           -- Full concept analysis from Claude
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(song_id)                    -- One concept analysis per song
);

CREATE INDEX idx_concepts_song_id ON song_concepts(song_id);

-- ============================================================================
-- TABLE 8: SONG_YOUTUBE_DATA (Unchanged)
-- ============================================================================
-- YouTube video transcripts and comments
-- One row per song

CREATE TABLE song_youtube_data (
  youtube_id BIGSERIAL PRIMARY KEY,
  song_id BIGINT NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
  
  video_url TEXT,                    -- YouTube video URL
  channel_name TEXT,                 -- Channel that uploaded video
  transcript TEXT,                   -- Video transcript
  top_comments JSONB,                -- Top comments array
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(song_id)                    -- One YouTube record per song
);

CREATE INDEX idx_youtube_song_id ON song_youtube_data(song_id);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
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
  s.chart_year,
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
-- DATA SOURCES ATTRIBUTION
-- ============================================================================

/*
DATA SOURCE SUMMARY:

1. CSV (Billboard Data):
   - track_name, artist_name (used to create artists table)
   - peak_position, first_chart_date, chart_year

2. Musixmatch API (FREE tier):
   - song_genres (song-level genres)
   - metadata_source

3. GetSongBPM API (FREE tier):
   Artist data:
   - artist_genres, artist_country
   - getsongbpm_artist_id, musicbrainz_id, getsongbpm_uri
   
   Album data:
   - album_title, album_year, getsongbpm_album_uri
   
   Song data:
   - bpm (tempo), time_signature, musical_key (backup)
   - camelot_key, danceability, acousticness

4. Genius.com (scraping):
   - Lyrics with section markers
   - lyrics_source

5. Ultimate-Guitar.com (scraping):
   - 6 versions of chords per section
   - tonality (primary source for musical_key)

6. Claude AI (Anthropic API):
   - Rhyme scheme analysis
   - Thematic concept analysis

7. YouTube (scraping):
   - Video transcripts
   - Top comments

ATTRIBUTION REQUIREMENTS:
- GetSongBPM: Link to https://getsongbpm.com (in README Credits section)
*/

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================

/*
WHEN REBUILDING DATABASE FROM SCRATCH:

1. Run this schema file to create all tables

2. Clear any existing data:
   TRUNCATE TABLE songs CASCADE;
   TRUNCATE TABLE artists CASCADE;
   TRUNCATE TABLE albums CASCADE;

3. Run enrichment pipeline:
   - Read CSV → extract unique artists → create artists table
   - Fetch GetSongBPM data → populate artist_genres, artist_country
   - Create albums table from GetSongBPM album data
   - Create songs with foreign keys to artist_id and album_id
   - Populate all GetSongBPM fields: bpm, danceability, acousticness, etc.
   - Fetch lyrics, chords, etc. as before

4. Verify foreign key relationships:
   - All songs should have valid artist_id
   - Most songs should have valid album_id (some may be NULL if album unknown)

5. Use views for queries that need artist_name or album_title:
   SELECT * FROM songs_complete WHERE artist_name = 'Michael Jackson';
*/

-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

/*
-- Find all songs by an artist (using normalized structure)
SELECT s.track_name, s.bpm, s.danceability
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE a.artist_name = 'Michael Jackson';

-- Find danceable acoustic songs
SELECT a.artist_name, s.track_name, s.danceability, s.acousticness
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE s.danceability > 70 AND s.acousticness > 60;

-- Find songs by artist genre
SELECT a.artist_name, s.track_name, a.artist_genres
FROM songs s
JOIN artists a ON s.artist_id = a.artist_id
WHERE 'funk' = ANY(a.artist_genres);

-- Find all albums by an artist
SELECT al.album_title, al.album_year, COUNT(s.song_id) as track_count
FROM albums al
JOIN artists a ON al.artist_id = a.artist_id
LEFT JOIN songs s ON s.album_id = al.album_id
WHERE a.artist_name = 'D''Angelo'
GROUP BY al.album_id, al.album_title, al.album_year;

-- Find songs with compatible Camelot keys (DJ mixing)
SELECT s1.track_name as song1, s2.track_name as song2, s1.camelot_key
FROM songs s1
JOIN songs s2 ON s1.camelot_key = s2.camelot_key
WHERE s1.song_id < s2.song_id
LIMIT 10;
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

