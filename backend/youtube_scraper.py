#!/usr/bin/env python3
"""
YouTube transcript scraper for Real Talk feature.
Fetches transcripts, extracts demographics, and tags with Claude.
"""

import os
import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import time
import subprocess
import tempfile

from googleapiclient.discovery import build
from openai import OpenAI
import scrapetube
from anthropic import Anthropic
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize clients
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize OpenAI (for Whisper transcription)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize YouTube API
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
if youtube_api_key:
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
else:
    youtube = None
    print("⚠️ YOUTUBE_API_KEY not set - YouTube features will be limited")


@dataclass
class Demographics:
    """Extracted demographic information."""
    poster_age: Optional[int] = None
    poster_gender: Optional[str] = None
    other_party_age: Optional[int] = None
    other_party_gender: Optional[str] = None
    inferred_location: Optional[str] = None
    confidence: str = "low"


@dataclass
class TagResult:
    """Claude-generated tags."""
    situation_tags: List[str]
    emotional_tags: List[str]

@dataclass
class ExtractedQuote:
    """A single quote extracted from a video."""
    quote_text: str
    situation_tags: List[str]
    emotional_tags: List[str]
    context: Optional[str] = None


class YouTubeScraper:
    """Scrapes YouTube transcripts and processes them with Claude."""
    
    def __init__(self):
        """Initialize the YouTube scraper."""
        pass
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'  # Just the ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict[str, str]]:
        """Get video metadata using official YouTube Data API."""
        if not youtube:
            print("⚠️  YouTube API not initialized")
            return None
        
        try:
            request = youtube.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                print(f"⚠️  Video {video_id} not found")
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return {
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_name': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', '')
            }
        except Exception as e:
            print(f"⚠️  Failed to get metadata: {e}")
            return None
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetch transcript for a YouTube video using OpenAI Whisper."""
        try:
            print(f"🎙️  Downloading audio for video {video_id}...")
            
            # Create temporary directory and filename (but don't create the file)
            temp_dir = tempfile.gettempdir()
            audio_filename = f"yt_{video_id}_{int(time.time())}.m4a"
            audio_path = os.path.join(temp_dir, audio_filename)
            
            # Download audio using yt-dlp
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Use Python subprocess to run yt-dlp
            # Note: We ignore exit codes because yt-dlp sometimes returns non-zero even on success
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio',  # Download best available audio format
                '-o', audio_path,
                '--no-playlist',
                '--no-warnings',  # Suppress warnings
                video_url
            ]
            
            # Run and ignore exit code - we'll check if file exists instead
            try:
                subprocess.run(cmd, capture_output=True, timeout=120, check=False)
            except subprocess.TimeoutExpired:
                print(f"⚠️  Download timed out")
                return None
            
            # Give it a moment to finish writing
            time.sleep(1)
            
            # Check if file was created
            if not os.path.exists(audio_path):
                # Try with a different output pattern - yt-dlp might have added extension
                possible_paths = [
                    audio_path,
                    audio_path + '.m4a',
                    audio_path.replace('.m4a', '') + '.m4a',
                    audio_path.replace('.m4a', '.webm'),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        audio_path = path
                        break
                else:
                    print(f"⚠️  No audio file found")
                    return None
            
            if os.path.getsize(audio_path) == 0:
                print(f"⚠️  Audio file is empty")
                os.unlink(audio_path)
                return None
            
            print(f"✅ Audio downloaded ({os.path.getsize(audio_path) / 1024 / 1024:.1f} MB)")
            print(f"🎙️  Transcribing with Whisper...")
            
            # Transcribe with OpenAI Whisper
            with open(audio_path, 'rb') as audio_file:
                transcript_response = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            # Clean up temp file
            os.unlink(audio_path)
            
            transcript_text = transcript_response.strip()
            print(f"✅ Transcribed {len(transcript_text)} characters")
            
            return transcript_text
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Audio download timed out")
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            return None
        except Exception as e:
            print(f"⚠️  Transcription failed: {e}")
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.unlink(audio_path)
            return None
    
    def extract_demographics_with_claude(self, title: str, description: str, transcript_excerpt: str) -> Demographics:
        """Use Claude to extract demographics from video metadata and transcript."""
        demographics = Demographics()
        
        # Build context for Claude
        context = f"""VIDEO TITLE: {title}

DESCRIPTION:
{description[:500]}

TRANSCRIPT EXCERPT:
{transcript_excerpt[:1000]}"""
        
        prompt = f"""Analyze this YouTube video and extract demographic information if present.

{context}

Look for mentions of:
- Age (e.g., "I'm 24", "22-year-old", "in my twenties")
- Gender (M/F/Other)
- Location (e.g., "from London", "living in NYC")
- Other party's demographics if it's a relationship discussion

Return JSON:
{{
  "poster_age": <int or null>,
  "poster_gender": "<M/F/Other or null>",
  "other_party_age": <int or null>,
  "other_party_gender": "<M/F/Other or null>",
  "inferred_location": "<string or null>",
  "confidence": "<high/medium/low>"
}}

If nothing found, return all null with confidence "low"."""

        try:
            response = anthropic.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                import json
                data = json.loads(json_match.group())
                demographics.poster_age = data.get('poster_age')
                demographics.poster_gender = data.get('poster_gender')
                demographics.other_party_age = data.get('other_party_age')
                demographics.other_party_gender = data.get('other_party_gender')
                demographics.inferred_location = data.get('inferred_location')
                demographics.confidence = data.get('confidence', 'low')
        except Exception as e:
            print(f"⚠️  Claude demographics extraction failed: {e}")
        
        return demographics
    
    def get_available_tags(self) -> Tuple[List[str], List[str]]:
        """Get current situation and emotion tags from database."""
        try:
            situation_result = supabase.table('real_talk_tags').select('tag_name').eq('tag_type', 'situation').execute()
            emotion_result = supabase.table('real_talk_tags').select('tag_name').eq('tag_type', 'emotion').execute()
            
            situations = [r['tag_name'] for r in situation_result.data]
            emotions = [r['tag_name'] for r in emotion_result.data]
            
            return situations, emotions
        except Exception as e:
            print(f"⚠️  Could not fetch tags from database: {e}")
            return (
                ['breakup', 'argument', 'reconciliation', 'missing_someone', 
                 'new_relationship', 'long_distance', 'cheating', 'family_conflict',
                 'friendship_ending', 'declaration_of_love'],
                ['angry', 'sad', 'hopeful', 'confused', 'desperate', 'relieved', 'bitter', 'loving']
            )
    
    def extract_quotes_with_claude(self, title: str, transcript: str, progress_callback=None) -> Tuple[List[ExtractedQuote], List[str], List[str]]:
        """
        Extract interesting quotes from transcript using Claude.
        Returns: (quotes, new_situation_tags, new_emotion_tags)
        """
        if progress_callback:
            progress_callback("🤖 Extracting quotes with Claude...")
        
        situations, emotions = self.get_available_tags()
        
        prompt = f"""Analyze this YouTube video transcript and extract 5-10 of the most interesting, relatable, or emotionally resonant QUOTES.

TITLE: {title}

TRANSCRIPT:
{transcript[:8000]}  # Use more context for quote extraction

EXISTING SITUATION TAGS (prefer these):
{', '.join(situations)}

EXISTING EMOTION TAGS (prefer these):
{', '.join(emotions)}

GUIDELINES:
1. Extract 5-10 short quotes (1-3 sentences each)
2. Choose authentic, relatable moments that express real human experience
3. Each quote should be self-contained and meaningful
4. Tag each quote with 1-3 situation tags and 1-3 emotion tags
5. USE EXISTING TAGS when they fit
6. If existing tags don't fit, suggest NEW tags but:
   - Be specific (not vague like "feeling_bad")
   - Avoid synonyms (e.g., don't create "joyful" if "happy" exists)
   - Use snake_case (e.g., "first_date_anxiety")
   - Max 3 new tags total across all quotes

Return JSON ONLY:
{{
  "quotes": [
    {{
      "quote": "exact quote text here",
      "situations": ["tag1", "tag2"],
      "emotions": ["tag1"]
    }}
  ],
  "new_situation_tags": ["new_tag1"],
  "new_emotion_tags": ["new_tag2"]
}}

If no quotes are interesting enough, return empty arrays."""

        try:
            response = anthropic.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,  # More tokens for multiple quotes
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if not json_match:
                print(f"⚠️  Claude response not JSON: {text[:200]}")
                return ([], [], [])
            
            import json
            data = json.loads(json_match.group())
            
            # Extract quotes
            quotes = []
            for q in data.get('quotes', []):
                quote = ExtractedQuote(
                    quote_text=q.get('quote', ''),
                    situation_tags=q.get('situations', []),
                    emotional_tags=q.get('emotions', [])
                )
                quotes.append(quote)
            
            # Get new tags suggested by Claude
            new_situations = data.get('new_situation_tags', [])
            new_emotions = data.get('new_emotion_tags', [])
            
            if progress_callback:
                progress_callback(f"✅ Extracted {len(quotes)} quotes")
            
            print(f"📝 Extracted {len(quotes)} quotes")
            if new_situations:
                print(f"   New situation tags: {', '.join(new_situations)}")
            if new_emotions:
                print(f"   New emotion tags: {', '.join(new_emotions)}")
            
            return (quotes, new_situations, new_emotions)
            
        except Exception as e:
            print(f"⚠️  Claude quote extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return ([], [], [])
    
    def save_new_tags(self, situation_tags: List[str], emotion_tags: List[str]):
        """Save newly suggested tags to the database."""
        try:
            for tag in situation_tags:
                supabase.table('real_talk_tags').insert({
                    'tag_type': 'situation',
                    'tag_name': tag
                }).execute()
                print(f"   ✅ Added situation tag: {tag}")
            
            for tag in emotion_tags:
                supabase.table('real_talk_tags').insert({
                    'tag_type': 'emotion',
                    'tag_name': tag
                }).execute()
                print(f"   ✅ Added emotion tag: {tag}")
        except Exception as e:
            # Ignore duplicate key errors
            if "duplicate" not in str(e).lower():
                print(f"⚠️  Failed to save tags: {e}")
    
    def scrape_video(self, video_url: str, source_id: str = None, progress_callback=None) -> Optional[List[Dict[str, Any]]]:
        """
        Scrape a single YouTube video.
        
        Args:
            video_url: YouTube video URL or ID
            source_id: UUID of the source in database
            
        Returns:
            Processed entry dict or None
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            print(f"❌ Could not extract video ID from: {video_url}")
            return None
        
        # Check if already scraped
        if source_id:
            result = supabase.table('real_talk_entries').select('external_id').eq('source_id', source_id).eq('external_id', video_id).execute()
            if result.data:
                print(f"⏭️  Video {video_id} already scraped")
                return None
        
        if progress_callback:
            progress_callback(f"📥 Processing: {video_id}")
        
        print(f"📥 Scraping video {video_id}...")
        
        # Get video metadata from official API
        if progress_callback:
            progress_callback("📋 Fetching video metadata...")
        
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            print(f"❌ Could not get metadata for {video_id}")
            return None
        
        title = metadata['title']
        description = metadata['description']
        channel_name = metadata['channel_name']
        published_at = metadata.get('published_at', datetime.now(timezone.utc).isoformat())
        
        # Get transcript (with progress in get_transcript method)
        transcript = self.get_transcript(video_id)
        if not transcript:
            return None
        
        # Extract demographics
        if progress_callback:
            progress_callback("👤 Analyzing demographics...")
        
        demographics = self.extract_demographics_with_claude(title, description, transcript[:500])
        
        # Extract quotes with Claude
        quotes, new_situations, new_emotions = self.extract_quotes_with_claude(title, transcript, progress_callback)
        
        if not quotes:
            print(f"⚠️  No interesting quotes found in video")
            return None
        
        # Save new tags to database
        if new_situations or new_emotions:
            if progress_callback:
                progress_callback("🏷️  Adding new tags...")
            self.save_new_tags(new_situations, new_emotions)
        
        # Create entry for each quote
        entries = []
        for i, quote in enumerate(quotes):
            entry = {
                'source_id': source_id,
                'external_id': f"{video_id}_quote_{i+1}",  # Unique ID per quote
                'title': f"{title}",
                'raw_text': quote.quote_text,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'posted_at': published_at,
                'channel_name': channel_name,
                'poster_age': demographics.poster_age,
                'poster_gender': demographics.poster_gender,
                'other_party_age': demographics.other_party_age,
                'other_party_gender': demographics.other_party_gender,
                'inferred_location': demographics.inferred_location,
                'situation_tags': quote.situation_tags,  # Tags specific to this quote
                'emotional_tags': quote.emotional_tags,  # Tags specific to this quote
                'demographic_confidence': demographics.confidence,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            entries.append(entry)
        
        if progress_callback:
            progress_callback(f"✅ Created {len(entries)} quote entries")
        
        print(f"✅ Processed video {video_id} → {len(entries)} quotes")
        return entries
    
    def save_entries(self, entries: List[Dict[str, Any]], source_id: str, progress_callback=None) -> bool:
        """Save multiple entries to database and update source stats."""
        try:
            if progress_callback:
                progress_callback(f"💾 Saving {len(entries)} quotes...")
            
            # Insert all entries
            supabase.table('real_talk_entries').insert(entries).execute()
            
            # Update source stats
            result = supabase.table('real_talk_entries').select('id', count='exact').eq('source_id', source_id).execute()
            total = result.count
            
            supabase.table('real_talk_sources').update({
                'last_scraped_at': datetime.now(timezone.utc).isoformat(),
                'total_entries': total
            }).eq('id', source_id).execute()
            
            # Update tag usage counts
            supabase.rpc('update_tag_usage_counts').execute()
            
            return True
        except Exception as e:
            print(f"⚠️  Failed to save entry: {e}")
            return False


    def extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel handle from YouTube URLs."""
        patterns = [
            r'youtube\.com/@([^/\?]+)',
            r'youtube\.com/channel/([^/\?]+)',
            r'youtube\.com/c/([^/\?]+)',
            r'^@?([A-Za-z0-9_-]+)$'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_channel_videos(self, channel_id: str, limit: int = 50) -> List[str]:
        """Fetch video IDs from channel."""
        try:
            print(f"📥 Fetching videos from: {channel_id}")
            videos = scrapetube.get_channel(channel_username=channel_id, limit=limit)
            video_ids = [v['videoId'] for v in list(videos)[:limit]]
            print(f"✅ Found {len(video_ids)} videos")
            return video_ids
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def scrape_channel(self, channel_url: str, source_id: str = None, limit: int = 50, progress_callback=None) -> Dict[str, Any]:
        """Scrape all videos from a channel."""
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            return {'total': 0, 'scraped': 0, 'saved': 0, 'failed': 0}
        
        video_ids = self.get_channel_videos(channel_id, limit=limit)
        if not video_ids:
            return {'total': 0, 'scraped': 0, 'saved': 0, 'failed': 0}
        
        scraped, saved, failed = 0, 0, 0
        for i, vid in enumerate(video_ids):
            if progress_callback:
                progress_callback(f"📹 Video {i+1}/{len(video_ids)}: {vid}")
            
            print(f"[{i+1}/{len(video_ids)}] {vid}...")
            try:
                entries = self.scrape_video(f"https://www.youtube.com/watch?v={vid}", source_id=source_id, progress_callback=progress_callback)
                if entries and self.save_entries(entries, source_id, progress_callback):
                    scraped += 1
                    saved += len(entries)  # Count quotes, not videos
                else:
                    failed += 1
                if i < len(video_ids) - 1:
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Error scraping {vid}: {e}")
                failed += 1
        
        print(f"✅ Done! Saved: {saved} quotes from {scraped} videos")
        return {'total': len(video_ids), 'scraped': scraped, 'saved': saved, 'failed': failed}


# CLI for testing
if __name__ == '__main__':
    print('YouTube Scraper Ready')
