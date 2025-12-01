#!/usr/bin/env python3
"""
Reddit scraper for Real Talk feature.
Scrapes relationship subreddits, extracts demographics, and tags with Claude.
"""

import os
import re
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import time

import praw
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


@dataclass
class Demographics:
    """Extracted demographic information from a post."""
    poster_age: Optional[int] = None
    poster_gender: Optional[str] = None
    other_party_age: Optional[int] = None
    other_party_gender: Optional[str] = None
    inferred_location: Optional[str] = None
    confidence: str = "low"


@dataclass
class TagResult:
    """Claude-generated tags for a post."""
    situation_tags: List[str]
    emotional_tags: List[str]


class RedditScraper:
    """Scrapes Reddit posts and processes them with Claude."""
    
    # Regex patterns for demographic extraction
    # Matches: (24F), (27M), [35M], [32F], 24F, 27m, etc.
    AGE_GENDER_PATTERNS = [
        r'\((\d{1,2})\s*([MFmf])\)',      # (24F)
        r'\[(\d{1,2})\s*([MFmf])\]',      # [35M]
        r'\(([MFmf])\s*(\d{1,2})\)',      # (F24)
        r'\[([MFmf])\s*(\d{1,2})\]',      # [M35]
        r'(?:^|\s)(\d{1,2})\s*([MFmf])(?:\s|$|,|\.)',  # 24F or 24f
        r'(?:I\'m|I am|im)\s+(?:a\s+)?(\d{1,2})\s*(?:year[s]?\s*old\s*)?([MFmf])',  # I'm 24F
    ]
    
    # Location patterns
    LOCATION_PATTERNS = [
        r"(?:I'm|I am|im|i'm)\s+from\s+([A-Z][a-zA-Z\s]+)",
        r"(?:here|live|living)\s+in\s+([A-Z][a-zA-Z\s]+)",
        r"as\s+an?\s+([A-Z][a-zA-Z]+)",  # "as an American"
        r"in\s+the\s+(UK|US|USA|United States|United Kingdom)",
    ]
    
    def __init__(self):
        """Initialize the Reddit scraper."""
        self.reddit = None
        self._connect()
    
    def _connect(self):
        """Connect to Reddit API."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "LyricBox:v1.0")
        
        if not client_id or not client_secret:
            print("⚠️  Reddit credentials not configured. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
            return
        
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            # Test connection
            self.reddit.user.me()
            print("✅ Connected to Reddit API")
        except Exception as e:
            print(f"⚠️  Reddit connection failed: {e}")
            # Still create read-only instance for public subreddits
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
    
    def extract_demographics(self, title: str, body: str) -> Demographics:
        """Extract demographic information from post title and body."""
        demographics = Demographics()
        text = f"{title} {body}"
        
        # Find all age/gender mentions
        matches = []
        for pattern in self.AGE_GENDER_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                groups = match.groups()
                # Normalize: some patterns have age first, some gender first
                if groups[0].isdigit():
                    age, gender = int(groups[0]), groups[1].upper()
                else:
                    gender, age = groups[0].upper(), int(groups[1])
                matches.append((age, gender, match.start()))
        
        # Sort by position in text
        matches.sort(key=lambda x: x[2])
        
        if matches:
            # First mention is usually the poster
            demographics.poster_age = matches[0][0]
            demographics.poster_gender = matches[0][1]
            demographics.confidence = "high"
            
            # Second mention is often the other party
            if len(matches) > 1:
                demographics.other_party_age = matches[1][0]
                demographics.other_party_gender = matches[1][1]
        
        # Extract location
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up common issues
                if location.lower() not in ['a', 'an', 'the']:
                    demographics.inferred_location = location
                    break
        
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
            # Return defaults
            return (
                ['breakup', 'argument', 'reconciliation', 'missing_someone', 
                 'new_relationship', 'long_distance', 'cheating', 'family_conflict',
                 'friendship_ending', 'declaration_of_love'],
                ['angry', 'sad', 'hopeful', 'confused', 'desperate', 'relieved', 'bitter', 'loving']
            )
    
    def tag_with_claude(self, title: str, body: str) -> TagResult:
        """Use Claude to analyze and tag the post."""
        situations, emotions = self.get_available_tags()
        
        prompt = f"""Analyze this Reddit post about relationships/emotions.

TITLE: {title}

POST:
{body[:3000]}  # Limit to avoid token overflow

From these SITUATION tags, select ALL that apply (can be multiple):
{', '.join(situations)}

From these EMOTION tags, select ALL that apply (can be multiple):
{', '.join(emotions)}

Respond with JSON only:
{{"situations": ["tag1", "tag2"], "emotions": ["tag1", "tag2"]}}

Be thorough - most posts have 2-4 situation tags and 2-3 emotion tags."""

        try:
            response = anthropic.messages.create(
                model="claude-sonnet-4-5-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            text = response.content[0].text.strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return TagResult(
                    situation_tags=[s for s in data.get('situations', []) if s in situations],
                    emotional_tags=[e for e in data.get('emotions', []) if e in emotions]
                )
        except Exception as e:
            print(f"⚠️  Claude tagging failed: {e}")
        
        return TagResult(situation_tags=[], emotional_tags=[])
    
    def scrape_subreddit(self, subreddit_name: str, limit: int = 100, 
                         source_id: str = None) -> List[Dict[str, Any]]:
        """
        Scrape posts from a subreddit.
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            limit: Maximum posts to fetch
            source_id: UUID of the source in database
            
        Returns:
            List of processed entries
        """
        if not self.reddit:
            print("❌ Reddit not connected")
            return []
        
        entries = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get existing external IDs to avoid duplicates
            existing_ids = set()
            if source_id:
                result = supabase.table('real_talk_entries').select('external_id').eq('source_id', source_id).execute()
                existing_ids = {r['external_id'] for r in result.data}
            
            print(f"📥 Scraping r/{subreddit_name} (limit: {limit})...")
            
            for i, post in enumerate(subreddit.hot(limit=limit)):
                # Skip if already scraped
                if post.id in existing_ids:
                    continue
                
                # Skip non-text posts
                if not post.selftext or post.selftext == '[removed]' or post.selftext == '[deleted]':
                    continue
                
                # Rate limit - be nice to Reddit
                if i > 0 and i % 10 == 0:
                    time.sleep(1)
                
                print(f"  [{i+1}/{limit}] {post.title[:50]}...")
                
                # Extract demographics
                demographics = self.extract_demographics(post.title, post.selftext)
                
                # Get Claude tags
                tags = self.tag_with_claude(post.title, post.selftext)
                
                entry = {
                    'source_id': source_id,
                    'external_id': post.id,
                    'title': post.title,
                    'raw_text': post.selftext,
                    'url': f"https://reddit.com{post.permalink}",
                    'posted_at': datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
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
                
                entries.append(entry)
            
            print(f"✅ Scraped {len(entries)} new posts from r/{subreddit_name}")
            
        except Exception as e:
            print(f"❌ Error scraping r/{subreddit_name}: {e}")
        
        return entries
    
    def save_entries(self, entries: List[Dict[str, Any]], source_id: str) -> int:
        """Save entries to database and update source stats."""
        if not entries:
            return 0
        
        saved = 0
        for entry in entries:
            try:
                supabase.table('real_talk_entries').insert(entry).execute()
                saved += 1
            except Exception as e:
                # Likely duplicate
                if 'duplicate' not in str(e).lower():
                    print(f"⚠️  Failed to save entry: {e}")
        
        # Update source stats
        if saved > 0:
            try:
                # Get current count
                result = supabase.table('real_talk_entries').select('id', count='exact').eq('source_id', source_id).execute()
                total = result.count
                
                supabase.table('real_talk_sources').update({
                    'last_scraped_at': datetime.now(timezone.utc).isoformat(),
                    'total_entries': total
                }).eq('id', source_id).execute()
                
                # Update tag usage counts
                supabase.rpc('update_tag_usage_counts').execute()
                
            except Exception as e:
                print(f"⚠️  Failed to update source stats: {e}")
        
        return saved


def intelligent_search(query: str, entries: List[Dict[str, Any]], limit: int = 50) -> List[Dict[str, Any]]:
    """
    Use Claude to rank entries by relevance to a semantic query.
    
    Args:
        query: What the user is looking for (e.g., "moment of realization")
        entries: List of entries to rank
        limit: Max entries to analyze
        
    Returns:
        Entries with relevance scores, sorted by relevance
    """
    if not entries:
        return []
    
    # Limit entries for API efficiency
    entries_to_analyze = entries[:limit]
    
    # Build prompt with entries
    entries_text = ""
    for i, entry in enumerate(entries_to_analyze):
        excerpt = entry.get('raw_text', '')[:500]
        entries_text += f"\n[{i}] Title: {entry.get('title', 'Untitled')}\nExcerpt: {excerpt}\n"
    
    prompt = f"""I'm looking for conversations about: "{query}"

Score each of these conversations from 1-10 based on relevance to my query.
Only return entries scoring 6 or higher.

CONVERSATIONS:
{entries_text}

Respond with JSON array only:
[{{"index": 0, "score": 8, "reason": "brief reason"}}, ...]

Be selective - only high-relevance matches."""

    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-5-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text.strip()
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if json_match:
            results = json.loads(json_match.group())
            
            # Add scores to entries
            scored_entries = []
            for result in results:
                idx = result.get('index', 0)
                if idx < len(entries_to_analyze):
                    entry = entries_to_analyze[idx].copy()
                    entry['relevance_score'] = result.get('score', 0)
                    entry['relevance_reason'] = result.get('reason', '')
                    scored_entries.append(entry)
            
            # Sort by score descending
            scored_entries.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return scored_entries
            
    except Exception as e:
        print(f"⚠️  Intelligent search failed: {e}")
    
    return []


# CLI for testing
if __name__ == "__main__":
    scraper = RedditScraper()
    
    # Test demographic extraction
    test_title = "I (24F) caught my boyfriend (27M) texting his ex"
    test_body = "I'm from California and I don't know what to do..."
    
    demographics = scraper.extract_demographics(test_title, test_body)
    print(f"\nDemographics test:")
    print(f"  Poster: {demographics.poster_age}{demographics.poster_gender}")
    print(f"  Other: {demographics.other_party_age}{demographics.other_party_gender}")
    print(f"  Location: {demographics.inferred_location}")
    print(f"  Confidence: {demographics.confidence}")

