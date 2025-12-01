-- Real Talk Database Schema
-- Run this in your Supabase SQL Editor (adds to existing schema, doesn't modify it)

-- ============================================
-- TAG CONFIGURATION TABLE
-- ============================================
-- Stores dynamic situation and emotion tags that can be added/removed

CREATE TABLE IF NOT EXISTS real_talk_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_type TEXT NOT NULL CHECK (tag_type IN ('situation', 'emotion')),
  tag_name TEXT NOT NULL,
  usage_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tag_type, tag_name)
);

-- Insert default situation tags
INSERT INTO real_talk_tags (tag_type, tag_name) VALUES
  ('situation', 'breakup'),
  ('situation', 'argument'),
  ('situation', 'reconciliation'),
  ('situation', 'missing_someone'),
  ('situation', 'new_relationship'),
  ('situation', 'long_distance'),
  ('situation', 'cheating'),
  ('situation', 'family_conflict'),
  ('situation', 'friendship_ending'),
  ('situation', 'declaration_of_love')
ON CONFLICT (tag_type, tag_name) DO NOTHING;

-- Insert default emotion tags
INSERT INTO real_talk_tags (tag_type, tag_name) VALUES
  ('emotion', 'angry'),
  ('emotion', 'sad'),
  ('emotion', 'hopeful'),
  ('emotion', 'confused'),
  ('emotion', 'desperate'),
  ('emotion', 'relieved'),
  ('emotion', 'bitter'),
  ('emotion', 'loving')
ON CONFLICT (tag_type, tag_name) DO NOTHING;

-- ============================================
-- SOURCE MANAGEMENT TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS real_talk_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL CHECK (source_type IN ('reddit', 'youtube_channel', 'youtube_video')),
  source_identifier TEXT NOT NULL,  -- subreddit name, channel ID, video URL
  display_name TEXT,
  is_active BOOLEAN DEFAULT true,
  last_scraped_at TIMESTAMPTZ,
  total_entries INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_type, source_identifier)
);

-- ============================================
-- SCRAPED ENTRIES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS real_talk_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES real_talk_sources(id) ON DELETE CASCADE,
  external_id TEXT NOT NULL,  -- Reddit post ID
  title TEXT,
  raw_text TEXT NOT NULL,
  url TEXT,
  posted_at TIMESTAMPTZ,
  -- Demographics
  poster_age INTEGER,
  poster_gender TEXT CHECK (poster_gender IN ('M', 'F', 'Other') OR poster_gender IS NULL),
  other_party_age INTEGER,
  other_party_gender TEXT CHECK (other_party_gender IN ('M', 'F', 'Other') OR other_party_gender IS NULL),
  inferred_location TEXT,
  -- Claude-generated tags
  situation_tags TEXT[],
  emotional_tags TEXT[],
  demographic_confidence TEXT CHECK (demographic_confidence IN ('high', 'medium', 'low') OR demographic_confidence IS NULL),
  -- Timestamps
  processed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_id, external_id)
);

-- ============================================
-- INDEXES FOR FAST FILTERING
-- ============================================

CREATE INDEX IF NOT EXISTS idx_rt_sources_active ON real_talk_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_rt_entries_source ON real_talk_entries(source_id);
CREATE INDEX IF NOT EXISTS idx_rt_entries_posted ON real_talk_entries(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_rt_entries_situations ON real_talk_entries USING gin(situation_tags);
CREATE INDEX IF NOT EXISTS idx_rt_entries_emotions ON real_talk_entries USING gin(emotional_tags);
CREATE INDEX IF NOT EXISTS idx_rt_entries_poster_age ON real_talk_entries(poster_age);
CREATE INDEX IF NOT EXISTS idx_rt_entries_poster_gender ON real_talk_entries(poster_gender);
CREATE INDEX IF NOT EXISTS idx_rt_entries_fulltext ON real_talk_entries USING gin(to_tsvector('english', raw_text));
CREATE INDEX IF NOT EXISTS idx_rt_tags_type ON real_talk_tags(tag_type);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

ALTER TABLE real_talk_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_talk_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_talk_entries ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow public read on real_talk_tags" 
  ON real_talk_tags FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public read on real_talk_sources" 
  ON real_talk_sources FOR SELECT TO anon USING (true);
CREATE POLICY "Allow public read on real_talk_entries" 
  ON real_talk_entries FOR SELECT TO anon USING (true);

-- Service role full access (for backend operations)
CREATE POLICY "Allow service role full on real_talk_tags" 
  ON real_talk_tags FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full on real_talk_sources" 
  ON real_talk_sources FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full on real_talk_entries" 
  ON real_talk_entries FOR ALL TO service_role USING (true);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Get all tags of a specific type
CREATE OR REPLACE FUNCTION get_real_talk_tags(p_tag_type TEXT)
RETURNS TABLE(tag_name TEXT, usage_count INTEGER) AS $$
BEGIN
  RETURN QUERY 
  SELECT rt.tag_name, rt.usage_count 
  FROM real_talk_tags rt 
  WHERE rt.tag_type = p_tag_type 
  ORDER BY rt.usage_count DESC, rt.tag_name;
END;
$$ LANGUAGE plpgsql;

-- Update tag usage counts (call after adding entries)
CREATE OR REPLACE FUNCTION update_tag_usage_counts()
RETURNS void AS $$
BEGIN
  -- Update situation tag counts
  UPDATE real_talk_tags SET usage_count = (
    SELECT COUNT(*) FROM real_talk_entries 
    WHERE real_talk_tags.tag_name = ANY(situation_tags)
  ) WHERE tag_type = 'situation';
  
  -- Update emotion tag counts
  UPDATE real_talk_tags SET usage_count = (
    SELECT COUNT(*) FROM real_talk_entries 
    WHERE real_talk_tags.tag_name = ANY(emotional_tags)
  ) WHERE tag_type = 'emotion';
END;
$$ LANGUAGE plpgsql;

