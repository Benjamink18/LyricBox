#!/usr/bin/env python3
"""
LyricBox API - Concept Generator endpoint.
"""
import os
import json
import random
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from anthropic import Anthropic
from supabase import create_client

load_dotenv()

app = Flask(__name__)
CORS(app)

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


@app.route('/api/analyze-random', methods=['GET'])
def analyze_random():
    """Generate a random songwriting concept from database lyrics."""
    
    try:
        # Get all songs with lyrics
        result = supabase.table('songs').select('id, title, artist, lyrics_raw').execute()
        
        if not result.data:
            return jsonify({"error": "No songs in database"}), 404
        
        # Filter to songs that have lyrics
        songs_with_lyrics = [s for s in result.data if s.get('lyrics_raw')]
        
        if not songs_with_lyrics:
            return jsonify({"error": "No songs with lyrics"}), 404
        
        # Pick a random song
        song = random.choice(songs_with_lyrics)
        lyrics = song['lyrics_raw']
        
        # Build the prompt
        prompt = f"""Research this song's background, context, and artist statements. Then provide:

(1) Brief concept summary with no song/artist names - explain it like you're talking to an 18-year-old fan about a new song idea, keep it casual and relatable

(2) Section-by-section breakdown using everyday language, describing what the main character is going through in each part without quoting any lyrics

(3) Universal themes that could inspire similar work, but explain them in a way that makes sense to young people

(4) Real-life scenarios when someone might feel this way

(5) 10 alternative song titles that could capture the same energy/concept

Focus on lyrical content only and frame it as developing a new song concept.

Lyrics:
{lyrics}

Return your response as JSON with this structure:
{{
  "concept_summary": "string",
  "section_breakdown": ["string", "string", ...],
  "universal_themes": ["string", "string", ...],
  "real_life_scenarios": ["string", "string", ...],
  "alternative_titles": ["string", "string", ...]
}}

Return ONLY the JSON, no markdown formatting."""

        response = anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text.strip()
        
        # Extract JSON from response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content
        
        analysis = json.loads(json_str)
        
        return jsonify({
            "song": {
                "id": song['id'],
                "title": song['title'],
                "artist": song['artist']
            },
            "analysis": analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=3001, debug=True)
