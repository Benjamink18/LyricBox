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

from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
from anthropic import Anthropic
from dotenv import load_dotenv
from supabase import create_client
import requests
from http.cookiejar import MozillaCookieJar

load_dotenv()

# Initialize clients
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


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
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetch transcript for a YouTube video."""
        try:
            # Check for cookies file to bypass IP blocks
            cookies_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
            
            if os.path.exists(cookies_path):
                print(f"🔐 Using cookies from {cookies_path}")
                # Create a session with cookies loaded
                session = requests.Session()
                cookies = MozillaCookieJar(cookies_path)
                cookies.load(ignore_discard=True, ignore_expires=True)
                session.cookies = cookies
                api = YouTubeTranscriptApi(http_client=session)
            else:
                print("📝 No cookies file, trying without auth...")
                api = YouTubeTranscriptApi()
            
            fetched = api.fetch(video_id)
            transcript_data = fetched.fetch()
            
            # Combine all text segments into one string
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            return full_text
        except Exception as e:
            print(f"⚠️  Could not fetch transcript: {e}")
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
                model="claude-sonnet-4-5-20241022",
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
    
    def tag_with_claude(self, title: str, transcript: str) -> TagResult:
        """Use Claude to analyze and tag the transcript."""
        situations, emotions = self.get_available_tags()
        
        prompt = f"""Analyze this YouTube video transcript about relationships/emotions.

TITLE: {title}

TRANSCRIPT:
{transcript[:3000]}  # Limit to avoid token overflow

From these SITUATION tags, select ALL that apply (can be multiple):
{', '.join(situations)}

From these EMOTION tags, select ALL that apply (can be multiple):
{', '.join(emotions)}

Respond with JSON only:
{{"situations": ["tag1", "tag2"], "emotions": ["tag1", "tag2"]}}

Be thorough - most videos have 2-4 situation tags and 2-3 emotion tags."""

        try:
            response = anthropic.messages.create(
                model="claude-sonnet-4-5-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                import json
                data = json.loads(json_match.group())
                return TagResult(
                    situation_tags=[s for s in data.get('situations', []) if s in situations],
                    emotional_tags=[e for e in data.get('emotions', []) if e in emotions]
                )
        except Exception as e:
            print(f"⚠️  Claude tagging failed: {e}")
        
        return TagResult(situation_tags=[], emotional_tags=[])
    
    def scrape_video(self, video_url: str, source_id: str = None) -> Optional[Dict[str, Any]]:
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
        
        print(f"📥 Scraping video {video_id}...")
        
        # Get transcript
        transcript = self.get_transcript(video_id)
        if not transcript:
            return None
        
        # For now, use simple title (in real app, would fetch from YouTube API or scrape)
        title = f"YouTube Video {video_id}"
        description = ""
        
        # Extract demographics
        demographics = self.extract_demographics_with_claude(title, description, transcript[:500])
        
        # Get Claude tags
        tags = self.tag_with_claude(title, transcript)
        
        entry = {
            'source_id': source_id,
            'external_id': video_id,
            'title': title,
            'raw_text': transcript,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'posted_at': datetime.now(timezone.utc).isoformat(),  # Would get real date from API
            'poster_age': demographics.poster_age,
            'poster_gender': demographics.poster_gender,
            'other_party_age': demographics.other_party_age,
            'other_party_gender': demographics.other_party_gender,
            'inferred_location': demographics.inferred_location,
            'situation_tags': tags.situation_tags,
            'emotional_tags': tags.emotional_tags,
            'demographic_confidence': demographics.confidence,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"✅ Processed video {video_id}")
        return entry
    
    def save_entry(self, entry: Dict[str, Any], source_id: str) -> bool:
        """Save entry to database and update source stats."""
        try:
            supabase.table('real_talk_entries').insert(entry).execute()
            
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
    
    def scrape_channel(self, channel_url: str, source_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Scrape all videos from a channel."""
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            return {'total': 0, 'scraped': 0, 'saved': 0, 'failed': 0}
        
        video_ids = self.get_channel_videos(channel_id, limit=limit)
        if not video_ids:
            return {'total': 0, 'scraped': 0, 'saved': 0, 'failed': 0}
        
        scraped, saved, failed = 0, 0, 0
        for i, vid in enumerate(video_ids):
            print(f"[{i+1}/{len(video_ids)}] {vid}...")
            try:
                entry = self.scrape_video(f"https://www.youtube.com/watch?v={vid}", source_id=source_id)
                if entry and self.save_entry(entry, source_id):
                    scraped += 1
                    saved += 1
                else:
                    failed += 1
                if i < len(video_ids) - 1:
                    time.sleep(2)
            except Exception as e:
                failed += 1
        
        print(f"✅ Done! Saved: {saved}/{len(video_ids)}")
        return {'total': len(video_ids), 'scraped': scraped, 'saved': saved, 'failed': failed}


# CLI for testing
if __name__ == '__main__':
    print('YouTube Scraper Ready')
