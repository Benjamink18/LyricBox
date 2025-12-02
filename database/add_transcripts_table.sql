-- Add transcripts table for storing full YouTube video transcripts
-- Each transcript is linked to multiple quotes via transcript_id foreign key

CREATE TABLE IF NOT EXISTS real_talk_transcripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id TEXT UNIQUE NOT NULL,  -- YouTube video ID (e.g., 'dQw4w9WgXcQ')
  full_transcript TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for fast video_id lookups
CREATE INDEX IF NOT EXISTS idx_rt_transcripts_video_id ON real_talk_transcripts(video_id);

-- Add transcript_id column to real_talk_entries
ALTER TABLE real_talk_entries 
ADD COLUMN IF NOT EXISTS transcript_id UUID REFERENCES real_talk_transcripts(id) ON DELETE SET NULL;

-- Add index for transcript lookups from entries
CREATE INDEX IF NOT EXISTS idx_rt_entries_transcript_id ON real_talk_entries(transcript_id);

-- Migration complete
-- Usage:
-- 1. Run this SQL in your Supabase SQL editor
-- 2. Each video gets ONE transcript in real_talk_transcripts
-- 3. All quotes from that video reference the same transcript_id

