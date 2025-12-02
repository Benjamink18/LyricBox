#!/usr/bin/env python3
"""
Shared utilities for Real Talk feature.
"""

import os
import re
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Claude client
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


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
            model="claude-sonnet-4-5",
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

