#!/usr/bin/env python3
"""
Song analyzer using Claude Sonnet 4.5 with prompt caching.
Analyzes lyrics for rhyme pairs and conceptual themes.
"""

import os
import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


@dataclass
class RhymePair:
    word: str
    rhymes_with: str
    rhyme_type: str
    word_line: int
    rhymes_with_line: int


@dataclass
class SongAnalysisResult:
    concept_summary: str
    section_breakdown: List[str]
    themes: List[str]
    imagery: List[str]
    tone: str
    universal_scenarios: List[str]
    alternative_titles: List[str]
    thematic_vocabulary: List[str]
    rhyme_pairs: List[RhymePair]


class SongAnalyzer:
    """Analyzes song lyrics using Claude Sonnet 4.5."""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 20000
        
        # System prompt for caching
        self.ANALYSIS_PROMPT_SYSTEM = [
            {
                "type": "text",
                "text": """Analyze lyrics for ALL rhymes. Output JSON array of unique rhyme pairs.

## RULES
1. Different words only - never word with itself
2. Each pair once only (A→B, not also B→A)
3. First occurrence only - skip repeats from chorus/verse repetitions
   IMPORTANT: If a word rhymes with multiple partners, record ALL unique pairs
   Example: "happy"→"me" AND "happy"→"melancholy" are BOTH valid pairs
4. Check every word against every other word in entire song

## RHYME TYPES
- **perfect**: Exact match (love/dove, time/crime)
- **assonance**: Same vowel, different consonants (love/us, me/melancholy/happy)
- **consonance**: Same consonants, different vowels (love/live, black/block)
- **slant**: Close but imperfect (love/move, home/come)
- **multi**: 2+ syllable match (tower/power, fantasy/sanity)
- **compound**: Phrase rhymes phrase (above us/enough love, door hinge/orange)
- **embedded**: Rhyme hidden in longer word (apologize/lies, together/ever)

## OUTPUT FORMAT
[
  {"w":"love", "r":"dove", "t":"perfect", "wl":4, "rl":6}
]

Fields:
- w = word
- r = rhymes_with
- t = type
- wl = word_line (1-based)
- rl = rhymes_with_line

## WHAT TO CATCH
- End-of-line rhymes (adjacent AND distant)
- Internal rhymes (middle of line with end or other middle)
- Within-line rhymes (day/play in same line)
- Compound phrases (multi-word units)
- Embedded sounds (apologize contains lies)
- All vowel chains - spelled differently counts (ee/ea/e/y/ie/ey = long E)

## EXAMPLES
3+ words sharing sound = every pair:
"happy with me, settle for melancholy" → happy→me, happy→melancholy, me→melancholy

Compound: "door hinge" / "orange" → compound
"above us" / "enough love" → compound

Embedded: "apologize" / "lies" → embedded

---

## CONCEPT ANALYSIS

Also provide:
1. Concept summary (3-4 sentences about the song's core idea)
2. Section breakdown (describe what happens in each section)
3. Themes (key themes present)
4. Imagery (notable imagery)
5. Tone (overall emotional tone)
6. Universal scenarios (when might someone relate to this?)
7. Alternative titles (10 alternative song titles)
8. Thematic vocabulary (key words that capture the vibe)

Output format:
{
  "rhyme_pairs": [...],
  "concept_summary": "...",
  "section_breakdown": [...],
  "themes": [...],
  "imagery": [...],
  "tone": "...",
  "universal_scenarios": [...],
  "alternative_titles": [...],
  "thematic_vocabulary": [...]
}""",
                "cache_control": {"type": "ephemeral"}
            }
        ]
    
    def analyze(self, lyrics: str, title: str, artist: str) -> Optional[SongAnalysisResult]:
        """
        Analyze song lyrics for rhymes and concepts.
        
        Args:
            lyrics: The song lyrics
            title: Song title
            artist: Artist name
            
        Returns:
            SongAnalysisResult or None if analysis fails
        """
        try:
            # User prompt with just the lyrics (system has the instructions)
            user_prompt = f"""SONG: {title} by {artist}

LYRICS:
{lyrics}

Output JSON only."""
            
            # Call Claude with system message for prompt caching
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.ANALYSIS_PROMPT_SYSTEM,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            json_str = self._extract_json(response_text)
            
            if not json_str:
                print(f"❌ Failed to extract JSON from response for {title}")
                return None
            
            # Parse and transform
            return self._transform_response(json_str, title, artist)
            
        except Exception as e:
            print(f"❌ Error analyzing {title}: {str(e)}")
            return None
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from Claude's response."""
        try:
            # Try to find JSON code block
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
                return json_str
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
                # Remove language identifier if present
                if json_str.startswith("json\n"):
                    json_str = json_str[5:].strip()
                return json_str
            else:
                # Assume entire response is JSON
                return text.strip()
        except Exception as e:
            print(f"❌ Error extracting JSON: {e}")
            return None
    
    def _transform_response(self, json_str: str, title: str, artist: str) -> Optional[SongAnalysisResult]:
        """Transform JSON response into SongAnalysisResult."""
        try:
            data = json.loads(json_str)
            
            # Parse rhyme pairs
            rhyme_pairs = []
            for pair in data.get("rhyme_pairs", []):
                rhyme_pairs.append(RhymePair(
                    word=pair["w"],
                    rhymes_with=pair["r"],
                    rhyme_type=pair["t"],
                    word_line=pair["wl"],
                    rhymes_with_line=pair["rl"]
                ))
            
            return SongAnalysisResult(
                concept_summary=data.get("concept_summary", ""),
                section_breakdown=data.get("section_breakdown", []),
                themes=data.get("themes", []),
                imagery=data.get("imagery", []),
                tone=data.get("tone", ""),
                universal_scenarios=data.get("universal_scenarios", []),
                alternative_titles=data.get("alternative_titles", []),
                thematic_vocabulary=data.get("thematic_vocabulary", []),
                rhyme_pairs=rhyme_pairs
            )
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error for {title}: {e}")
            print(f"JSON string: {json_str[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Error transforming response for {title}: {e}")
            return None


if __name__ == "__main__":
    # Test the analyzer
    analyzer = SongAnalyzer()
    
    test_lyrics = """It can't be said I'm an early bird
It's ten o'clock before I say a word
Baby, I can never tell
How do you sleep so well?"""
    
    result = analyzer.analyze(test_lyrics, "Too Sweet", "Hozier")
    
    if result:
        print(f"✅ Analysis successful!")
        print(f"Rhyme pairs found: {len(result.rhyme_pairs)}")
        print(f"Concept summary: {result.concept_summary[:100]}...")
    else:
        print("❌ Analysis failed")

