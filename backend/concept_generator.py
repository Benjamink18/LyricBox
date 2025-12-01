#!/usr/bin/env python3
"""
Custom Concept Generator
Generates song concepts based on user ideas, learning from similar hit songs in the database.
"""

import os
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

THEME_EXTRACTION_PROMPT = """Extract 3-5 key themes from this song concept idea. Return ONLY a JSON array of theme strings.

Examples:
Input: "A song about missing your ex but pretending you're over them at a party"
Output: ["heartbreak", "facade", "social situations", "moving on", "emotional conflict"]

Input: "Finding strength after being betrayed by someone you trusted"
Output: ["betrayal", "trust issues", "empowerment", "resilience", "self-discovery"]

Now extract themes from this concept:
{user_idea}

Return only the JSON array, no other text."""

CONCEPT_GENERATION_PROMPT = """You are a professional songwriter analyzing hit songs to help create compelling song concepts.

Below are {num_examples} hit songs with similar themes to learn from:

{examples}

---

Based on these hit songs, generate a detailed concept for this new song idea:
"{user_idea}"

Learn from the examples above - notice how hit songs:
- Balance universal themes with specific imagery
- Use concrete metaphors and sensory details
- Create emotional resonance through relatable scenarios
- Structure ideas with clear narrative arcs

Generate a concept following this exact JSON structure:
{{
  "concept_summary": "2-3 sentence overview of the core concept",
  "themes": ["theme1", "theme2", "theme3"],
  "imagery": ["visual/sensory image 1", "image 2", "image 3"],
  "tone": "emotional tone description",
  "universal_scenarios": ["relatable scenario 1", "scenario 2"],
  "alternative_titles": ["title 1", "title 2", "title 3", "title 4", "title 5"],
  "thematic_vocabulary": ["word1", "word2", "word3", "word4", "word5"],
  "section_breakdown": [
    "Opening: how to start",
    "Verse 1: what to explore",
    "Chorus: central message",
    "Verse 2: how to deepen",
    "Bridge: perspective shift",
    "Outro: how to conclude"
  ]
}}

Return ONLY valid JSON, no other text."""


class ConceptGenerator:
    """Generates custom song concepts using Claude AI."""
    
    def extract_themes(self, user_idea: str) -> List[str]:
        """Extract key themes from user's concept idea."""
        print(f"Extracting themes from: {user_idea}")
        
        response = anthropic.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": THEME_EXTRACTION_PROMPT.format(user_idea=user_idea)
            }]
        )
        
        themes_json = response.content[0].text.strip()
        print(f"Raw theme extraction response: {themes_json}")
        
        # Remove markdown code blocks if present
        if themes_json.startswith('```'):
            themes_json = themes_json.split('```')[1]
            if themes_json.startswith('json'):
                themes_json = themes_json[4:]
            themes_json = themes_json.strip()
        
        # Try to find JSON array in the response
        if '[' in themes_json:
            start = themes_json.index('[')
            end = themes_json.rindex(']') + 1
            themes_json = themes_json[start:end]
        
        themes = json.loads(themes_json)
        print(f"Extracted themes: {themes}")
        return themes
    
    def find_matching_songs(
        self,
        themes: List[str],
        num_songs: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Find songs in database with matching themes."""
        filters = filters or {}
        
        print(f"Searching for {num_songs} songs matching themes: {themes}")
        
        # Build query - use !inner to ensure we only get rows where song join succeeds
        query = supabase.table('song_analysis').select(
            'song_id, concept_summary, themes, imagery, tone, universal_scenarios, section_breakdown, songs!inner(id, title, artist, year, billboard_rank, genre)'
        )
        
        # Apply filters (note: years filter on songs table)
        if filters.get('years'):
            query = query.filter('songs.year', 'in', f"({','.join(map(str, filters['years']))})")
        
        if filters.get('minRank') and filters.get('maxRank'):
            query = query.filter('songs.billboard_rank', 'gte', filters['minRank'])
            query = query.filter('songs.billboard_rank', 'lte', filters['maxRank'])
        
        if filters.get('artists'):
            query = query.filter('songs.artist', 'in', f"({','.join(filters['artists'])})")
        
        # Execute query - NO LIMIT! Get ALL songs that match filters
        print(f"Executing query with filters applied (no limit - getting ALL matching songs)...")
        result = query.execute()
        
        # Apply genre filter in Python (case-insensitive partial matching)
        if filters.get('genres'):
            filtered_genres = [g.lower() for g in filters['genres']]
            original_count = len(result.data) if result.data else 0
            result.data = [
                song for song in (result.data or [])
                if song.get('songs') and song['songs'].get('genre') and 
                any(fg in song['songs']['genre'].lower() for fg in filtered_genres)
            ]
            print(f"Genre filter applied: {original_count} -> {len(result.data)} songs")
        
        print(f"Query returned {len(result.data) if result.data else 0} total songs")
        
        if not result.data:
            print("No songs found at all - database might be empty!")
            return []
        
        # Score songs by theme overlap
        print(f"Scoring {len(result.data)} songs by theme overlap with: {themes}")
        scored_songs = []
        for song in result.data:
            song_themes = song.get('themes', [])
            if not song_themes:
                continue
            
            # Get billboard rank - handle different data structures
            billboard_rank = 999
            if 'songs' in song and song['songs']:
                billboard_rank = song['songs'].get('billboard_rank') or 999
            
            # Calculate overlap score - fuzzy matching
            # Check if extracted theme keywords appear in song theme phrases
            overlap = 0
            for extracted_theme in themes:
                extracted_lower = extracted_theme.lower()
                for song_theme in song_themes:
                    song_theme_lower = song_theme.lower()
                    # Check if keyword appears in phrase
                    if extracted_lower in song_theme_lower or song_theme_lower in extracted_lower:
                        overlap += 1
                        break  # Count each extracted theme only once
            
            scored_songs.append({
                'song': song,
                'score': overlap,
                'billboard_rank': billboard_rank
            })
        
        # Sort by overlap score (desc), then billboard rank (asc)
        scored_songs.sort(key=lambda x: (-x['score'], x['billboard_rank']))
        
        # Deduplicate by song ID (database has duplicates)
        seen_song_ids = set()
        deduplicated = []
        for item in scored_songs:
            song_info = item['song'].get('songs') or {}
            song_id = song_info.get('id')
            if song_id and song_id not in seen_song_ids:
                seen_song_ids.add(song_id)
                deduplicated.append(item)
        
        # Debug: Show top scores
        print(f"\nTop 10 song scores (after deduplication):")
        for i, item in enumerate(deduplicated[:10]):
            song_info = item['song'].get('songs', {}) or {}
            print(f"  {i+1}. Score={item['score']}, Rank=#{item['billboard_rank']}, {song_info.get('title', 'Unknown')} - {song_info.get('artist', 'Unknown')}")
        
        # Return top N with scores
        top_songs = deduplicated[:num_songs]
        print(f"Found {len(top_songs)} unique matching songs")
        
        return top_songs
    
    def format_example(self, song_data: Dict) -> str:
        """Format a song's concept data as an example for Claude."""
        song_info = song_data.get('songs', {})
        title = song_info.get('title', 'Unknown')
        artist = song_info.get('artist', 'Unknown')
        rank = song_info.get('billboard_rank', 'N/A')
        
        return f"""
Song: "{title}" by {artist} (#{rank})
Summary: {song_data.get('concept_summary', 'N/A')}
Themes: {', '.join(song_data.get('themes', []))}
Imagery: {', '.join(song_data.get('imagery', [])[:3])}
Tone: {song_data.get('tone', 'N/A')}
""".strip()
    
    def generate_concept(
        self,
        user_idea: str,
        example_songs: List[Dict]
    ) -> Dict:
        """Generate a custom concept based on user idea and example songs."""
        print(f"Generating concept for: {user_idea}")
        print(f"Using {len(example_songs)} example songs")
        
        # Format examples
        examples_text = "\n\n".join([
            self.format_example(song) for song in example_songs
        ])
        
        # Generate concept
        response = anthropic.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            system=[{
                "type": "text",
                "text": "You are an expert songwriter and concept developer.",
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[{
                "role": "user",
                "content": CONCEPT_GENERATION_PROMPT.format(
                    num_examples=len(example_songs),
                    examples=examples_text,
                    user_idea=user_idea
                )
            }]
        )
        
        # Parse response
        concept_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if concept_json.startswith('```'):
            concept_json = concept_json.split('```')[1]
            if concept_json.startswith('json'):
                concept_json = concept_json[4:]
            concept_json = concept_json.strip()
        
        concept = json.loads(concept_json)
        print("✓ Concept generated successfully")
        
        return concept


def generate_custom_concept(
    user_idea: str,
    num_songs: int = 10,
    filters: Optional[Dict] = None,
    manual_song_ids: Optional[List[str]] = None
) -> Dict:
    """
    Main function to generate a custom concept.
    
    Args:
        user_idea: User's concept description
        num_songs: Number of example songs to use
        filters: Optional filters for song selection
        manual_song_ids: Optional list of manually selected song IDs
    
    Returns:
        Generated concept dictionary
    """
    generator = ConceptGenerator()
    
    # Extract themes from user idea
    themes = generator.extract_themes(user_idea)
    
    # Get example songs
    if manual_song_ids:
        # Use manually selected songs
        result = supabase.table('song_analysis').select('''
            concept_summary,
            themes,
            imagery,
            tone,
            universal_scenarios,
            section_breakdown,
            songs!inner (title, artist, billboard_rank)
        ''').filter('song_id', 'in', f"({','.join(manual_song_ids)})").execute()
        example_songs = result.data
    else:
        # Find matching songs by theme
        example_songs = generator.find_matching_songs(themes, num_songs, filters)
    
    # Generate concept
    concept = generator.generate_concept(user_idea, example_songs)
    
    # Add metadata
    example_song_names = []
    for s in example_songs:
        if 'songs' in s and s['songs']:
            example_song_names.append(f"{s['songs'].get('title', 'Unknown')} - {s['songs'].get('artist', 'Unknown')}")
    
    concept['_meta'] = {
        'user_idea': user_idea,
        'extracted_themes': themes,
        'num_examples': len(example_songs),
        'example_songs': example_song_names
    }
    
    return concept


if __name__ == '__main__':
    # Test the generator
    test_idea = "A song about missing your ex but pretending you're over them at a party"
    
    print("=" * 60)
    print("CUSTOM CONCEPT GENERATOR TEST")
    print("=" * 60)
    
    concept = generate_custom_concept(
        user_idea=test_idea,
        num_songs=5,
        filters={'maxRank': 20}  # Only top 20 hits
    )
    
    print("\n" + "=" * 60)
    print("GENERATED CONCEPT")
    print("=" * 60)
    print(json.dumps(concept, indent=2))

