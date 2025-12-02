-- Add channel_name column to real_talk_entries table
-- This stores the YouTube channel name for each entry

ALTER TABLE real_talk_entries
ADD COLUMN IF NOT EXISTS channel_name TEXT;

-- Create an index for filtering/sorting by channel
CREATE INDEX IF NOT EXISTS idx_rt_entries_channel_name ON real_talk_entries(channel_name);

