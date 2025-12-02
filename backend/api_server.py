#!/usr/bin/env python3
"""
Flask API server for LyricBox custom concept generation.
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from concept_generator import generate_custom_concept
import traceback
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor

# Syllable counting function (matches frontend)
def count_syllables_server(text):
    """Count syllables in text using the same logic as frontend."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z\s\'-]', '', text)  # Remove punctuation except apostrophes/hyphens
    
    if not text:
        return 0
    
    # Count vowel groups
    vowel_groups = re.findall(r'[aeiouy]+', text)
    syllable_count = len(vowel_groups)
    
    # Adjust for silent e
    words = text.split()
    for word in words:
        if word.endswith('e') and len(word) > 2 and word[-2] not in 'aeiouy':
            syllable_count -= 1
    
    # Minimum of 1 syllable per word
    word_count = len([w for w in words if w])
    return max(syllable_count, word_count)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


@app.route('/api/find-matching-songs', methods=['POST'])
def find_matching_songs():
    """
    Find songs that match the user's concept idea.
    
    Expected JSON body:
    {
        "user_idea": "string",
        "num_songs": 10,
        "filters": {...}
    }
    """
    print("=" * 60, flush=True)
    print("FIND MATCHING SONGS ENDPOINT CALLED - NEW VERSION!", flush=True)
    print("=" * 60, flush=True)
    try:
        from concept_generator import ConceptGenerator
        
        data = request.json
        user_idea = data.get('user_idea')
        print(f"User idea: {user_idea}", flush=True)
        if not user_idea:
            return jsonify({'error': 'user_idea is required'}), 400
        
        num_songs = data.get('num_songs', 10)
        filters = data.get('filters', {})
        print(f"Num songs requested: {num_songs}, Filters: {filters}", flush=True)
        
        generator = ConceptGenerator()
        
        # Extract themes
        print("Extracting themes...", flush=True)
        themes = generator.extract_themes(user_idea)
        print(f"Extracted themes: {themes}", flush=True)
        
        # Find matching songs
        print(f"Finding matching songs...", flush=True)
        matching_songs = generator.find_matching_songs(themes, num_songs, filters)
        print(f"Got {len(matching_songs)} matching songs back", flush=True)
        
        # Format response
        songs_data = []
        for item in matching_songs:
            # Handle None value (not just missing key)
            song = item.get('song', {})
            song_info = song.get('songs') or {}
            song_id = song_info.get('id')
            match_score = item.get('score', 0)
            
            songs_data.append({
                'id': song_id,
                'title': song_info.get('title'),
                'artist': song_info.get('artist'),
                'rank': song_info.get('billboard_rank'),
                'themes': song.get('themes', []),
                'imagery': song.get('imagery', []),
                'tone': song.get('tone', ''),
                'universal_scenarios': song.get('universal_scenarios', []),
                'matchScore': match_score
            })
        
        print(f"Returning {len(songs_data)} songs")
        print(f"Sample song data: {songs_data[0] if songs_data else 'none'}")
        
        return jsonify({
            'extracted_themes': themes,
            'songs': songs_data
        })
    
    except Exception as e:
        print(f"Error finding matching songs: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-custom-concept', methods=['POST'])
def generate_concept():
    """
    Generate a custom song concept based on user input.
    
    Expected JSON body:
    {
        "user_idea": "string",
        "num_songs": 10,
        "filters": {
            "years": [2020, 2021],
            "minRank": 1,
            "maxRank": 20,
            "genres": ["pop"],
            "artists": ["Taylor Swift"]
        },
        "manual_song_ids": ["id1", "id2"]
    }
    """
    try:
        data = request.json
        
        user_idea = data.get('user_idea')
        if not user_idea:
            return jsonify({'error': 'user_idea is required'}), 400
        
        num_songs = data.get('num_songs', 10)
        filters = data.get('filters', {})
        manual_song_ids = data.get('manual_song_ids')
        
        # Generate concept
        concept = generate_custom_concept(
            user_idea=user_idea,
            num_songs=num_songs,
            filters=filters,
            manual_song_ids=manual_song_ids
        )
        
        return jsonify(concept)
    
    except Exception as e:
        print(f"Error generating concept: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-concept', methods=['POST'])
def export_concept():
    """
    Export a concept as a PDF.
    
    Expected JSON body:
    {
        "title": "Song Title - Artist",
        "concept_summary": "...",
        "themes": [...],
        "imagery": [...],
        "tone": "...",
        "universal_scenarios": [...],
        "alternative_titles": [...],
        "section_breakdown": [...],
        "thematic_vocabulary": [...]
    }
    """
    try:
        concept = request.json
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#4a9eff'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#4a9eff'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            leading=16
        )
        
        # Add title
        title = concept.get('title', 'Song Concept')
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add summary
        if concept.get('concept_summary'):
            elements.append(Paragraph('Summary', heading_style))
            elements.append(Paragraph(concept['concept_summary'], body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add themes
        if concept.get('themes'):
            elements.append(Paragraph('Themes', heading_style))
            themes_text = ', '.join(concept['themes'])
            elements.append(Paragraph(themes_text, body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add imagery
        if concept.get('imagery'):
            elements.append(Paragraph('Imagery', heading_style))
            for img in concept['imagery']:
                elements.append(Paragraph(f'• {img}', body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add tone
        if concept.get('tone'):
            elements.append(Paragraph('Tone', heading_style))
            elements.append(Paragraph(concept['tone'], body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add universal scenarios
        if concept.get('universal_scenarios'):
            elements.append(Paragraph('Universal Scenarios', heading_style))
            for scenario in concept['universal_scenarios']:
                elements.append(Paragraph(f'• {scenario}', body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add section breakdown
        if concept.get('section_breakdown'):
            elements.append(Paragraph('Section Breakdown', heading_style))
            for section in concept['section_breakdown']:
                elements.append(Paragraph(f'• {section}', body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add alternative titles
        if concept.get('alternative_titles'):
            elements.append(Paragraph('Alternative Titles', heading_style))
            for title in concept['alternative_titles']:
                elements.append(Paragraph(f'• {title}', body_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Add thematic vocabulary
        if concept.get('thematic_vocabulary'):
            elements.append(Paragraph('Thematic Vocabulary', heading_style))
            vocab_text = ', '.join(concept['thematic_vocabulary'])
            elements.append(Paragraph(vocab_text, body_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'concept-{concept.get("title", "export").replace(" ", "-")}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"Error exporting concept: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-more-titles', methods=['POST'])
def generate_more_titles():
    """
    Generate more alternative titles based on an existing concept.
    
    Expected JSON body:
    {
        "concept": {
            "concept_summary": "...",
            "themes": [...],
            "imagery": [...],
            "tone": "..."
        },
        "reference_songs": ["Song - Artist", ...],
        "existing_titles": ["Title 1", ...]
    }
    """
    try:
        from anthropic import Anthropic
        import os
        
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        data = request.json
        concept = data.get('concept', {})
        reference_songs = data.get('reference_songs', [])
        existing_titles = data.get('existing_titles', [])
        
        # Build context from reference songs
        if reference_songs:
            songs_context = f"\n\nBased on these hit songs:\n" + "\n".join([f"- {song}" for song in reference_songs])
        else:
            songs_context = ""
        
        # Build prompt
        prompt = f"""Generate 5 alternative song titles for this concept.

Concept:
Summary: {concept.get('concept_summary', 'N/A')}
Themes: {', '.join(concept.get('themes', []))}
Imagery: {', '.join(concept.get('imagery', []))}
Tone: {concept.get('tone', 'N/A')}
{songs_context}

Existing titles (don't duplicate):
{', '.join(existing_titles)}

Generate 5 NEW alternative titles that:
- Capture the concept's themes and tone
- Are memorable and emotionally resonant
- Learn from the style of the reference songs
- Are different from the existing titles

Return ONLY a JSON array of 5 title strings, no other text.
Example: ["Title One", "Title Two", "Title Three", "Title Four", "Title Five"]"""

        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        titles_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if titles_json.startswith('```'):
            titles_json = titles_json.split('```')[1]
            if titles_json.startswith('json'):
                titles_json = titles_json[4:]
            titles_json = titles_json.strip()
        
        # Find JSON array in response
        if '[' in titles_json:
            start = titles_json.index('[')
            end = titles_json.rindex(']') + 1
            titles_json = titles_json[start:end]
        
        import json
        new_titles = json.loads(titles_json)
        
        print(f"Generated {len(new_titles)} new titles")
        
        return jsonify({'titles': new_titles})
    
    except Exception as e:
        print(f"Error generating more titles: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-next-line', methods=['POST'])
def generate_next_line():
    """
    Generate next line suggestions for songwriting.
    
    Expected JSON body:
    {
        "concept": "...",
        "existing_lyrics": "...",
        "syllable_count": 9,
        "rhyme_target": "you",
        "rhyme_position": "end",
        "rhyme_type": "perfect" (optional),
        "reference_song_ids": ["id1", "id2", ...]
    }
    """
    try:
        from anthropic import Anthropic
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        data = request.json
        
        concept = data.get('concept', '')
        existing_lyrics = data.get('existing_lyrics', '')
        syllable_count = data.get('syllable_count', 10)
        rhyme_target = data.get('rhyme_target', '')
        rhyme_position = data.get('rhyme_position', 'end')
        rhyme_type = data.get('rhyme_type')
        reference_song_ids = data.get('reference_song_ids', [])
        line_meaning = data.get('line_meaning')
        specific_rhyme_word = data.get('specific_rhyme_word')
        partial_line = data.get('partial_line')
        line_type = data.get('line_type', 'regular')  # regular, metaphor, or simile
        words_to_avoid = data.get('words_to_avoid')  # Comma-separated string of words to avoid
        
        print(f"Generating next line for: {concept}")
        print(f"Line type: {line_type}")
        print(f"Rhyme target: {rhyme_target}, Position: {rhyme_position}, Type: {rhyme_type}")
        if words_to_avoid:
            print(f"Words to avoid: {words_to_avoid}")
        
        # Get rhyme options from database
        rhyme_options = []
        if rhyme_target:
            query = supabase.table('rhyme_pairs').select('rhymes_with, rhyme_type, songs(title, artist)')
            query = query.ilike('word', rhyme_target)
            
            if rhyme_type and rhyme_type != 'any':
                query = query.eq('rhyme_type', rhyme_type)
            
            result = query.limit(50).execute()
            
            if result.data:
                rhyme_words = set()
                for pair in result.data:
                    rhyme_word = pair['rhymes_with']
                    # Don't suggest the same word as the rhyme target
                    if rhyme_word.lower() != rhyme_target.lower():
                        rhyme_words.add(rhyme_word)
                rhyme_options = list(rhyme_words)[:20]  # Top 20 rhyme options
        
        print(f"Found {len(rhyme_options)} rhyme options")
        
        # Get reference songs
        reference_songs = []
        if reference_song_ids:
            result = supabase.table('song_analysis').select(
                'songs(title, artist), themes, thematic_vocabulary'
            ).in_('song_id', reference_song_ids).execute()
            
            reference_songs = result.data if result.data else []
        
        # Build reference songs context
        songs_context = ""
        if reference_songs:
            songs_context = "\n\nLearn from these hit songs:\n"
            for song in reference_songs[:5]:  # Top 5
                if song.get('songs'):
                    songs_context += f"- {song['songs']['title']} by {song['songs']['artist']}\n"
                    if song.get('thematic_vocabulary'):
                        vocab = ', '.join(song['thematic_vocabulary'][:10])
                        songs_context += f"  Vocabulary: {vocab}\n"
        
        # Build rhyme context
        rhyme_context = ""
        if specific_rhyme_word:
            # User specified exact rhyme word to use
            rhyme_context = f"\n\nMUST use this specific rhyme word: '{specific_rhyme_word}'"
        elif rhyme_options:
            rhyme_context = f"\n\nRhyme options for '{rhyme_target}': {', '.join(rhyme_options[:15])}"
        
        # Build additional constraints
        additional_constraints = []
        if line_meaning:
            additional_constraints.append(f"- Line should convey: {line_meaning}")
        if specific_rhyme_word:
            additional_constraints.append(f"- MUST end with the word '{specific_rhyme_word}' (at {rhyme_position})")
        if partial_line:
            additional_constraints.append(f"- Complete this partial line: '{partial_line}...'")
        if words_to_avoid:
            # Parse comma-separated words and clean them
            avoid_list = [w.strip().lower() for w in words_to_avoid.split(',') if w.strip()]
            if avoid_list:
                additional_constraints.append(f"- DO NOT use these words (already used in song): {', '.join(avoid_list)}")
        
        additional_constraints_text = "\n".join(additional_constraints) if additional_constraints else ""
        
        # Build line type instructions
        line_type_instructions = ""
        if line_type == 'metaphor':
            line_type_instructions = """
⭐ LINE TYPE: METAPHOR
- Each line MUST be a metaphor (direct comparison WITHOUT 'like' or 'as')
- Examples: "You are my sunshine", "Love is a battlefield", "Time is a thief"
- Make the metaphor creative, evocative, and emotionally resonant
- DO NOT use the words 'like' or 'as' for comparisons
"""
        elif line_type == 'simile':
            line_type_instructions = """
⭐ LINE TYPE: SIMILE
- Each line MUST be a simile (comparison USING 'like' or 'as')
- Examples: "Eyes like diamonds", "Cold as ice", "Free as a bird"
- The simile should be vivid, memorable, and emotionally powerful
- MUST include the word 'like' or 'as' in the comparison
"""
        
        # Build prompt with EXTREME emphasis on syllable count
        prompt = f"""You are an expert songwriter with PERFECT syllable counting ability.

⚠️ CRITICAL: SYLLABLE COUNT = {syllable_count} SYLLABLES EXACTLY ⚠️
Every single line MUST have EXACTLY {syllable_count} syllables. Count carefully!
{line_type_instructions}
SONG CONCEPT:
{concept}

EXISTING LYRICS:
{existing_lyrics if existing_lyrics else "(Starting fresh)"}
{songs_context}
{rhyme_context}

MANDATORY CONSTRAINTS (DO NOT VIOLATE):
1. ⭐ SYLLABLE COUNT: EXACTLY {syllable_count} syllables per line (COUNT CAREFULLY!)
2. Rhyme position: {rhyme_position} of line
{"3. Must rhyme with: '" + rhyme_target + "' (but NOT the word '" + rhyme_target + "' itself)" if rhyme_target and not specific_rhyme_word else ""}
{"4. Rhyme type: " + rhyme_type if rhyme_type and rhyme_type != 'any' else ""}
{additional_constraints_text}

REQUIREMENTS:
- Continue the narrative/emotional arc from existing lyrics
- Match the concept's themes and tone
- Use natural, conversational language (not forced)
- If rhyme target specified, rhyme must be natural and strong
- Each line should be unique and emotionally resonant
- Draw vocabulary and style from the reference songs
{"- DO NOT use the word '" + rhyme_target + "' as the rhyme - use a DIFFERENT word that rhymes with it" if rhyme_target and not specific_rhyme_word else ""}

SYLLABLE COUNTING RULES:
- Count every vowel sound as one syllable
- Silent 'e' at end doesn't count (e.g., "made" = 1 syllable, not 2)
- Compound words: add syllables together (e.g., "fire-fly" = 2 syllables)
- Contractions: count as pronounced (e.g., "don't" = 1, "I'm" = 1)

SYLLABLE COUNT TARGET: {syllable_count} syllables
TRY YOUR BEST to generate lines with exactly {syllable_count} syllables, but return ALL 20 lines regardless.

Count syllables carefully:
- Example: "I don't want you" = I(1) don't(1) want(1) you(1) = 4 syllables
- Silent 'e' doesn't count: "made" = 1 syllable
- Contractions count as pronounced: "don't" = 1 syllable

Generate EXACTLY 20 lines total. Aim for {syllable_count} syllables each, but return all 20 even if some don't match perfectly.

Return ONLY a JSON array of exactly 20 line strings.
Example: ["Line one here", "Line two here", "Line three here", ...]"""

        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        suggestions_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if suggestions_json.startswith('```'):
            suggestions_json = suggestions_json.split('```')[1]
            if suggestions_json.startswith('json'):
                suggestions_json = suggestions_json[4:]
            suggestions_json = suggestions_json.strip()
        
        # Find JSON array in response
        if '[' in suggestions_json:
            start = suggestions_json.index('[')
            end = suggestions_json.rindex(']') + 1
            suggestions_json = suggestions_json[start:end]
        
        import json
        all_suggestions = json.loads(suggestions_json)
        
        # Sort by syllable accuracy (exact matches first, then closest)
        suggestions_with_syllables = []
        for line in all_suggestions:
            line_syllables = count_syllables_server(line)
            syllable_diff = abs(line_syllables - syllable_count)
            suggestions_with_syllables.append({
                'line': line,
                'syllables': line_syllables,
                'diff': syllable_diff
            })
            
            if line_syllables == syllable_count:
                print(f"✅ '{line}' (exactly {syllable_count} syllables)")
            else:
                print(f"⚠️ '{line}' (has {line_syllables} syllables, need {syllable_count})")
        
        # Sort by difference (exact matches first), then alphabetically
        suggestions_with_syllables.sort(key=lambda x: (x['diff'], x['line']))
        
        exact_matches = sum(1 for s in suggestions_with_syllables if s['diff'] == 0)
        print(f"Generated {len(all_suggestions)} suggestions, {exact_matches} match syllable count exactly")
        
        # Return all suggestions sorted by accuracy
        return jsonify({
            'suggestions': suggestions_with_syllables,
            'total_generated': len(all_suggestions),
            'exact_matches': exact_matches,
            'target_syllables': syllable_count
        })
    
    except Exception as e:
        print(f"Error generating next line: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-more-like-this', methods=['POST'])
def generate_more_like_this():
    """
    Generate more variations similar to a specific line.
    
    Expected JSON body:
    {
        "base_line": "The line to generate variations of",
        "concept": "...",
        "existing_lyrics": "...",
        "syllable_count": 9,
        "rhyme_target": "you",
        "rhyme_position": "end",
        "rhyme_type": "perfect" (optional),
        "reference_song_ids": ["id1", "id2", ...]
    }
    """
    try:
        from anthropic import Anthropic
        import os
        
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        data = request.json
        
        base_line = data.get('base_line', '')
        concept = data.get('concept', '')
        syllable_count = data.get('syllable_count', 10)
        rhyme_target = data.get('rhyme_target', '')
        line_meaning = data.get('line_meaning')
        specific_rhyme_word = data.get('specific_rhyme_word')
        partial_line = data.get('partial_line')
        line_type = data.get('line_type', 'regular')  # regular, metaphor, or simile
        words_to_avoid = data.get('words_to_avoid')  # Comma-separated string of words to avoid
        
        print(f"Generating variations of: {base_line}")
        print(f"Line type: {line_type}")
        if words_to_avoid:
            print(f"Words to avoid: {words_to_avoid}")
        
        # Build additional constraints
        additional_constraints = []
        if line_meaning:
            additional_constraints.append(f"- Line should convey: {line_meaning}")
        if specific_rhyme_word:
            additional_constraints.append(f"- MUST use the rhyme word '{specific_rhyme_word}'")
        if partial_line:
            additional_constraints.append(f"- Complete this partial line: '{partial_line}...'")
        if words_to_avoid:
            # Parse comma-separated words and clean them
            avoid_list = [w.strip().lower() for w in words_to_avoid.split(',') if w.strip()]
            if avoid_list:
                additional_constraints.append(f"- DO NOT use these words (already used in song): {', '.join(avoid_list)}")
        
        additional_constraints_text = "\n".join(additional_constraints) if additional_constraints else ""
        
        # Build line type instructions
        line_type_instructions = ""
        if line_type == 'metaphor':
            line_type_instructions = """
⭐ LINE TYPE: METAPHOR
- Each line MUST be a metaphor (direct comparison WITHOUT 'like' or 'as')
- Examples: "You are my sunshine", "Love is a battlefield", "Time is a thief"
- DO NOT use the words 'like' or 'as' for comparisons
"""
        elif line_type == 'simile':
            line_type_instructions = """
⭐ LINE TYPE: SIMILE
- Each line MUST be a simile (comparison USING 'like' or 'as')
- Examples: "Eyes like diamonds", "Cold as ice", "Free as a bird"
- MUST include the word 'like' or 'as' in the comparison
"""
        
        # Build prompt with EXTREME emphasis on syllable count
        prompt = f"""You are an expert songwriter with PERFECT syllable counting ability.

⚠️ CRITICAL: SYLLABLE COUNT = {syllable_count} SYLLABLES EXACTLY ⚠️
{line_type_instructions}
BASE LINE (to vary):
"{base_line}"

SONG CONCEPT:
{concept}

MANDATORY CONSTRAINTS (DO NOT VIOLATE):
1. ⭐ SYLLABLE COUNT: EXACTLY {syllable_count} syllables per line (COUNT CAREFULLY!)
2. Similar emotional tone and style to the base line
{"3. Must rhyme with: '" + rhyme_target + "' (but NOT the word '" + rhyme_target + "' itself)" if rhyme_target and not specific_rhyme_word else ""}
4. Each variation should be unique but feel related
5. Maintain the same level of intensity/emotion
6. Keep natural, conversational language
{additional_constraints_text}

Generate 10 variations that:
- Have EXACTLY {syllable_count} syllables (count each one!)
- Convey a similar emotion/message
- Use different words/phrasing
- Feel like they belong in the same song
- Are equally strong and memorable
{"- DO NOT use the word '" + rhyme_target + "' as the rhyme - use a DIFFERENT word that rhymes with it" if rhyme_target and not specific_rhyme_word else ""}

SYLLABLE COUNTING RULES:
- Count every vowel sound as one syllable
- Silent 'e' at end doesn't count (e.g., "made" = 1 syllable)
- Contractions: count as pronounced (e.g., "don't" = 1)

SYLLABLE COUNT TARGET: {syllable_count} syllables
TRY YOUR BEST to match {syllable_count} syllables, but return ALL 20 variations regardless.

Generate EXACTLY 20 variations total. Aim for {syllable_count} syllables each, but return all 20 even if some don't match perfectly.

Return ONLY a JSON array of exactly 20 variation strings.
Example: ["Variation one", "Variation two", ...]"""

        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        suggestions_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if suggestions_json.startswith('```'):
            suggestions_json = suggestions_json.split('```')[1]
            if suggestions_json.startswith('json'):
                suggestions_json = suggestions_json[4:]
            suggestions_json = suggestions_json.strip()
        
        # Find JSON array in response
        if '[' in suggestions_json:
            start = suggestions_json.index('[')
            end = suggestions_json.rindex(']') + 1
            suggestions_json = suggestions_json[start:end]
        
        import json
        all_suggestions = json.loads(suggestions_json)
        
        # Sort by syllable accuracy (exact matches first, then closest)
        suggestions_with_syllables = []
        for line in all_suggestions:
            line_syllables = count_syllables_server(line)
            syllable_diff = abs(line_syllables - syllable_count)
            suggestions_with_syllables.append({
                'line': line,
                'syllables': line_syllables,
                'diff': syllable_diff
            })
            
            if line_syllables == syllable_count:
                print(f"✅ '{line}' (exactly {syllable_count} syllables)")
            else:
                print(f"⚠️ '{line}' (has {line_syllables} syllables, need {syllable_count})")
        
        # Sort by difference (exact matches first), then alphabetically
        suggestions_with_syllables.sort(key=lambda x: (x['diff'], x['line']))
        
        exact_matches = sum(1 for s in suggestions_with_syllables if s['diff'] == 0)
        print(f"Generated {len(all_suggestions)} variations, {exact_matches} match syllable count exactly")
        
        # Return all suggestions sorted by accuracy
        return jsonify({
            'suggestions': suggestions_with_syllables,
            'total_generated': len(all_suggestions),
            'exact_matches': exact_matches,
            'target_syllables': syllable_count
        })
    
    except Exception as e:
        print(f"Error generating variations: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-figurative-variations', methods=['POST'])
def generate_figurative_variations():
    """
    Generate variations of a figurative line with a new meaning.
    
    Expected JSON body:
    {
        "original_line": "Eyes like diamonds in the sky",
        "keyword": "like",
        "desired_meaning": "expressing hope and optimism"
    }
    """
    try:
        from anthropic import Anthropic
        import os
        
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        data = request.json
        original_line = data.get('original_line', '')
        keyword = data.get('keyword', 'like')
        desired_meaning = data.get('desired_meaning', '')
        
        print(f"Generating figurative variations for: {original_line}")
        print(f"Keyword: {keyword}, Desired meaning: {desired_meaning}")
        
        # Determine if it's a simile or metaphor based on keyword
        is_simile = keyword.lower() in ['like', 'as', 'than']
        
        prompt = f"""You are an expert songwriter specializing in figurative language.

ORIGINAL LINE:
"{original_line}"

KEYWORD USED: "{keyword}"
TYPE: {"Simile (comparison with 'like'/'as'/'than')" if is_simile else "Metaphor (direct comparison)"}

DESIRED NEW MEANING:
{desired_meaning}

Generate 10 new lines that:
1. {"Use 'like', 'as', or 'than' for comparison (simile)" if is_simile else "Make a direct comparison without 'like' or 'as' (metaphor)"}
2. Convey the desired meaning: {desired_meaning}
3. Have similar structure and length to the original
4. Are creative, evocative, and fit naturally in a song
5. Use vivid imagery that captures the emotional essence

Return ONLY a JSON array of 10 line strings, no other text.
Example: ["Line one", "Line two", ...]"""

        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        variations_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if variations_json.startswith('```'):
            variations_json = variations_json.split('```')[1]
            if variations_json.startswith('json'):
                variations_json = variations_json[4:]
            variations_json = variations_json.strip()
        
        # Find JSON array in response
        if '[' in variations_json:
            start = variations_json.index('[')
            end = variations_json.rindex(']') + 1
            variations_json = variations_json[start:end]
        
        import json
        variations = json.loads(variations_json)
        
        print(f"Generated {len(variations)} figurative variations")
        
        return jsonify({'variations': variations})
    
    except Exception as e:
        print(f"Error generating figurative variations: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/filter-figurative-by-meaning', methods=['POST'])
def filter_figurative_by_meaning():
    """
    Filter figurative language results by semantic meaning using Claude.
    
    Expected JSON body:
    {
        "lines": [
            {"line": "Eyes like diamonds", "song": "Song - Artist", "keyword": "like"},
            ...
        ],
        "desired_meaning": "expressing hope and optimism"
    }
    """
    try:
        from anthropic import Anthropic
        import os
        
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        data = request.json
        lines = data.get('lines', [])
        desired_meaning = data.get('desired_meaning', '')
        
        if not lines or not desired_meaning:
            return jsonify({'error': 'lines and desired_meaning are required'}), 400
        
        print(f"Filtering {len(lines)} figurative expressions by meaning: {desired_meaning}")
        
        # Build the prompt with all lines
        lines_text = "\n".join([f"{i+1}. \"{item['line']}\" (from {item['song']})" for i, item in enumerate(lines)])
        
        prompt = f"""You are an expert in figurative language and poetry analysis.

DESIRED MEANING:
"{desired_meaning}"

FIGURATIVE EXPRESSIONS TO ANALYZE:
{lines_text}

Task: Find ALL expressions that match the desired meaning (relevance score 5 or higher). Consider:
1. The literal imagery and comparison being made
2. The emotional tone and connotation
3. How well the metaphor/simile conveys the desired meaning
4. Cultural and poetic associations

Return a JSON array of ALL matches with relevance >= 5, ordered by relevance (best first).
Include even borderline matches - the user wants to see everything that's remotely relevant.

Each item should have:
- "line": the exact line text
- "relevance": a score from 1-10 (10 being perfect match)
- "reasoning": brief explanation (1 sentence) why it matches

Example format:
[
  {{"line": "exact line text here", "relevance": 9, "reasoning": "The diamond imagery perfectly conveys brilliance and value"}},
  {{"line": "another line here", "relevance": 6, "reasoning": "Somewhat captures the feeling through nature imagery"}},
  ...
]

Return ONLY the JSON array, no other text."""

        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        matches_json = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if matches_json.startswith('```'):
            matches_json = matches_json.split('```')[1]
            if matches_json.startswith('json'):
                matches_json = matches_json[4:]
            matches_json = matches_json.strip()
        
        # Find JSON array in response
        if '[' in matches_json:
            start = matches_json.index('[')
            end = matches_json.rindex(']') + 1
            matches_json = matches_json[start:end]
        
        import json
        matches = json.loads(matches_json)
        
        print(f"Claude selected {len(matches)} best matches")
        
        return jsonify({'matches': matches})
    
    except Exception as e:
        print(f"Error filtering by meaning: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================
# REAL TALK ENDPOINTS
# ============================================

@app.route('/api/real-talk/sources', methods=['GET'])
def get_real_talk_sources():
    """Get all Real Talk sources."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        result = supabase.table('real_talk_sources').select('*').order('created_at', desc=True).execute()
        
        return jsonify({'sources': result.data})
    
    except Exception as e:
        print(f"Error getting sources: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/sources', methods=['POST'])
def add_real_talk_source():
    """Add a new Real Talk source (Reddit subreddit or YouTube video)."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        data = request.json
        source_identifier = data.get('source_identifier', '').strip()
        source_type = data.get('source_type', 'youtube_video')
        
        if not source_identifier:
            return jsonify({'error': 'source_identifier is required'}), 400
        
        # Handle YouTube video sources
        if source_type == 'youtube_video':
            # Extract video ID if it's a URL
            from youtube_scraper import YouTubeScraper
            scraper = YouTubeScraper()
            video_id = scraper.extract_video_id(source_identifier)
            if video_id:
                source_identifier = video_id
                display_name = f"YouTube: {video_id}"
            else:
                return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Handle YouTube channel sources
        elif source_type == 'youtube_channel':
            from youtube_scraper import YouTubeScraper
            scraper = YouTubeScraper()
            channel_id = scraper.extract_channel_id(source_identifier)
            if channel_id:
                source_identifier = channel_id
                display_name = f"YT Channel: {channel_id}"
            else:
                return jsonify({'error': 'Invalid YouTube channel URL'}), 400
        
        else:
            return jsonify({'error': 'Invalid source_type'}), 400
        
        # Try to insert source, or return existing if duplicate
        try:
            result = supabase.table('real_talk_sources').insert({
                'source_type': source_type,
                'source_identifier': source_identifier,
                'display_name': display_name,
                'is_active': True
            }).execute()
            
            return jsonify({'source': result.data[0]})
        
        except Exception as insert_error:
            # If duplicate, fetch and return the existing source
            if 'duplicate' in str(insert_error).lower():
                print(f"Source already exists, fetching existing: {source_type}/{source_identifier}")
                existing = supabase.table('real_talk_sources')\
                    .select('*')\
                    .eq('source_type', source_type)\
                    .eq('source_identifier', source_identifier)\
                    .execute()
                
                if existing.data:
                    return jsonify({'source': existing.data[0], 'already_exists': True})
                else:
                    return jsonify({'error': 'Source exists but could not be retrieved'}), 500
            else:
                raise insert_error
    
    except Exception as e:
        print(f"Error adding source: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/sources/<source_id>', methods=['DELETE'])
def delete_real_talk_source(source_id):
    """Delete a Real Talk source and all its entries."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Delete entries first (cascade should handle this, but be explicit)
        supabase.table('real_talk_entries').delete().eq('source_id', source_id).execute()
        
        # Delete source
        supabase.table('real_talk_sources').delete().eq('id', source_id).execute()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error deleting source: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/sources/<source_id>/toggle', methods=['POST'])
def toggle_real_talk_source(source_id):
    """Toggle a Real Talk source active/inactive."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        data = request.json
        is_active = data.get('is_active', True)
        
        result = supabase.table('real_talk_sources').update({
            'is_active': is_active
        }).eq('id', source_id).execute()
        
        return jsonify({'source': result.data[0] if result.data else None})
    
    except Exception as e:
        print(f"Error toggling source: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/entries', methods=['GET'])
def get_real_talk_entries():
    """
    Get Real Talk entries with filtering.
    
    Query params:
    - search: Full-text search query
    - situations: Comma-separated situation tags
    - emotions: Comma-separated emotion tags
    - source_id: Filter by source
    - age_min: Minimum poster age
    - age_max: Maximum poster age
    - gender: Poster gender (M/F)
    - year_min: Minimum year posted
    - year_max: Maximum year posted
    - limit: Max results (default 50)
    - offset: Pagination offset
    """
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Start query
        query = supabase.table('real_talk_entries').select(
            '*, real_talk_sources(display_name, source_identifier)'
        )
        
        # Apply filters
        search = request.args.get('search')
        if search:
            # Full-text search
            query = query.ilike('raw_text', f'%{search}%')
        
        situations = request.args.get('situations')
        if situations:
            situation_list = situations.split(',')
            query = query.overlaps('situation_tags', situation_list)
        
        emotions = request.args.get('emotions')
        if emotions:
            emotion_list = emotions.split(',')
            query = query.overlaps('emotional_tags', emotion_list)
        
        source_id = request.args.get('source_id')
        if source_id:
            query = query.eq('source_id', source_id)
        
        age_min = request.args.get('age_min')
        if age_min:
            query = query.gte('poster_age', int(age_min))
        
        age_max = request.args.get('age_max')
        if age_max:
            query = query.lte('poster_age', int(age_max))
        
        gender = request.args.get('gender')
        if gender:
            query = query.eq('poster_gender', gender)
        
        year_min = request.args.get('year_min')
        if year_min:
            query = query.gte('posted_at', f'{year_min}-01-01')
        
        year_max = request.args.get('year_max')
        if year_max:
            query = query.lte('posted_at', f'{year_max}-12-31')
        
        # Pagination
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Order and execute
        query = query.order('posted_at', desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        
        return jsonify({
            'entries': result.data,
            'count': len(result.data),
            'offset': offset,
            'limit': limit
        })
    
    except Exception as e:
        print(f"Error getting entries: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/tags', methods=['GET'])
def get_real_talk_tags():
    """Get all available tags (situation and emotion)."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        result = supabase.table('real_talk_tags').select('*').order('usage_count', desc=True).execute()
        
        situations = [t for t in result.data if t['tag_type'] == 'situation']
        emotions = [t for t in result.data if t['tag_type'] == 'emotion']
        
        return jsonify({
            'situations': situations,
            'emotions': emotions
        })
    
    except Exception as e:
        print(f"Error getting tags: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/transcript/<transcript_id>', methods=['GET'])
def get_real_talk_transcript(transcript_id):
    """
    Get full transcript by transcript_id.
    Used for displaying transcript with highlighted quote in modal.
    
    Returns:
        {
            'transcript': 'full transcript text',
            'video_id': 'YouTube video ID'
        }
    """
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        result = supabase.table('real_talk_transcripts')\
            .select('full_transcript, video_id')\
            .eq('id', transcript_id)\
            .execute()
        
        if not result.data:
            return jsonify({'error': 'Transcript not found'}), 404
        
        transcript_data = result.data[0]
        
        return jsonify({
            'transcript': transcript_data['full_transcript'],
            'video_id': transcript_data['video_id']
        })
    
    except Exception as e:
        print(f"Error getting transcript: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/tags', methods=['POST'])
def add_real_talk_tag():
    """Add a new tag."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        data = request.json
        tag_type = data.get('tag_type')  # 'situation' or 'emotion'
        tag_name = data.get('tag_name', '').strip().lower().replace(' ', '_')
        
        if not tag_type or not tag_name:
            return jsonify({'error': 'tag_type and tag_name are required'}), 400
        
        if tag_type not in ['situation', 'emotion']:
            return jsonify({'error': 'tag_type must be "situation" or "emotion"'}), 400
        
        result = supabase.table('real_talk_tags').insert({
            'tag_type': tag_type,
            'tag_name': tag_name,
            'usage_count': 0
        }).execute()
        
        return jsonify({'tag': result.data[0]})
    
    except Exception as e:
        print(f"Error adding tag: {e}")
        traceback.print_exc()
        if 'duplicate' in str(e).lower():
            return jsonify({'error': 'This tag already exists'}), 400
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/tags/<tag_id>', methods=['DELETE'])
def delete_real_talk_tag(tag_id):
    """Delete a tag."""
    try:
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        supabase.table('real_talk_tags').delete().eq('id', tag_id).execute()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error deleting tag: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/intelligent-search', methods=['POST'])
def real_talk_intelligent_search():
    """
    Use Claude to find entries that match a semantic query.
    
    Expected JSON body:
    {
        "query": "moment of realization they were wrong",
        "entries": [...],  // Pre-filtered entries to analyze
        "limit": 50
    }
    """
    try:
        from real_talk_utils import intelligent_search
        
        data = request.json
        query = data.get('query', '')
        entries = data.get('entries', [])
        limit = data.get('limit', 50)
        
        if not query:
            return jsonify({'error': 'query is required'}), 400
        
        if not entries:
            return jsonify({'error': 'entries are required'}), 400
        
        print(f"Intelligent search for: {query} (analyzing {len(entries)} entries)")
        
        results = intelligent_search(query, entries, limit=limit)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'query': query
        })
    
    except Exception as e:
        print(f"Error in intelligent search: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/real-talk/scrape-youtube', methods=['GET', 'POST'])
def scrape_youtube_video():
    """
    Scrape a YouTube video and extract quotes.
    
    GET (SSE): Query parameters - video_url, source_id
    POST (JSON): Body - video_url, source_id
    """
    from youtube_scraper import YouTubeScraper
    
    # Support both GET (for SSE) and POST (for traditional)
    if request.method == 'POST':
        data = request.json
        video_url = data.get('video_url')
        source_id = data.get('source_id')
        use_sse = False
    else:
        video_url = request.args.get('video_url')
        source_id = request.args.get('source_id')
        use_sse = True
    
    if not video_url:
        return jsonify({'error': 'video_url is required'}), 400
    
    scraper = YouTubeScraper()
    
    # SSE mode
    if use_sse:
        def generate():
            try:
                entries = None
                for update in scraper.scrape_video_with_progress(video_url, source_id=source_id):
                    if isinstance(update, dict) and 'entries' in update:
                        entries = update['entries']
                    else:
                        yield f"data: {json.dumps({'status': update})}\n\n"
                
                if not entries:
                    yield f"data: {json.dumps({'error': 'Failed to scrape video'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'status': '💾 Saving to database...'})}\n\n"
                saved = scraper.save_entries(entries, source_id)
                
                if saved:
                    yield f"data: {json.dumps({'success': True, 'quotes_extracted': len(entries), 'title': entries[0]['title']})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'Failed to save entries'})}\n\n"
            
            except Exception as e:
                print(f"Error scraping YouTube video: {e}")
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    # Traditional POST mode (no progress updates)
    try:
        entries = scraper.scrape_video(video_url, source_id=source_id)
        
        if not entries:
            return jsonify({'error': 'Failed to scrape video (no transcript/quotes available or already scraped)'}), 400
        
        saved = scraper.save_entries(entries, source_id)
        
        if saved:
            return jsonify({
                'success': True,
                'quotes_extracted': len(entries),
                'title': entries[0]['title']
            })
        else:
            return jsonify({'error': 'Failed to save entries'}), 500
    
    except Exception as e:
        print(f"Error scraping YouTube video: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@app.route('/api/real-talk/scrape-youtube-channel', methods=['GET', 'POST'])
def scrape_youtube_channel():
    """
    Scrape all videos from a YouTube channel.
    
    GET (SSE): Query parameters - channel_url, source_id, limit
    POST (JSON): Body - channel_url, source_id, limit
    """
    from youtube_scraper import YouTubeScraper
    
    # Support both GET (for SSE) and POST (for traditional)
    if request.method == 'POST':
        data = request.json
        channel_url = data.get('channel_url')
        source_id = data.get('source_id')
        limit = data.get('limit', 50)
        use_sse = False
    else:
        channel_url = request.args.get('channel_url')
        source_id = request.args.get('source_id')
        limit = int(request.args.get('limit', 50))
        use_sse = True
    
    if not channel_url:
        return jsonify({'error': 'channel_url is required'}), 400
    
    scraper = YouTubeScraper()
    
    # SSE mode
    if use_sse:
        def generate():
            try:
                for update in scraper.scrape_channel_with_progress(channel_url, source_id=source_id, limit=limit):
                    if isinstance(update, dict) and 'success' in update:
                        yield f"data: {json.dumps(update)}\n\n"
                    else:
                        yield f"data: {json.dumps({'status': update})}\n\n"
            
            except Exception as e:
                print(f"Error scraping YouTube channel: {e}")
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    # Traditional POST mode (no progress updates)
    try:
        result = scraper.scrape_channel(channel_url, source_id=source_id, limit=limit)
        
        return jsonify({
            'success': True,
            'total_videos': result['total'],
            'scraped': result['scraped'],
            'saved': result['saved'],
            'failed': result['failed']
        })
    except Exception as e:
        print(f"Error scraping YouTube channel: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ===== MELODY ENDPOINTS =====

# Global Tidal client to persist OAuth state across requests
_tidal_client = None

def get_tidal_client():
    """Get or create the global Tidal client."""
    global _tidal_client
    if _tidal_client is None:
        from tidal_client import TidalClient
        _tidal_client = TidalClient()
    return _tidal_client


@app.route('/api/melody/search', methods=['POST'])
def melody_search():
    """
    Search for songs matching a chord progression.
    
    Expected JSON body:
    {
        "chords": "Am C F G",
        "key": "A minor",       // Optional - inferred from chords if not provided
        "bpm": 120,
        "bpm_tolerance": 10,    // Optional, default 10
        "time_signature": "4/4", // Optional, default "4/4"
        // Optional filters:
        "genres": ["Pop", "R&B"],
        "year_start": 2015,
        "year_end": 2024,
        "chart_position": "Top 20",  // e.g., "Top 10", "Top 20", "Top 50"
        "artist_style": "similar to Drake"
    }
    """
    try:
        from chord_converter import convert_progression
        from melody_claude import find_matching_songs
        
        data = request.json
        chord_input = data.get('chords')
        
        if not chord_input:
            return jsonify({'error': 'chords is required'}), 400
        
        bpm = data.get('bpm')
        if not bpm:
            return jsonify({'error': 'bpm is required'}), 400
        
        # Convert chords to Roman numerals
        key = data.get('key')
        progression = convert_progression(chord_input, key)
        
        # Get optional filters
        bpm_tolerance = data.get('bpm_tolerance', 10)
        time_signature = data.get('time_signature', '4/4')
        genres = data.get('genres') if data.get('genres') else None
        year_start = data.get('year_start')
        year_end = data.get('year_end')
        chart_position = data.get('chart_position')
        artist_style = data.get('artist_style')
        
        # Search using Claude
        songs = find_matching_songs(
            roman_numerals=progression.roman_numerals,
            original_chords=progression.original_chords,
            key=progression.key,
            bpm=bpm,
            bpm_tolerance=bpm_tolerance,
            time_signature=time_signature,
            genres=genres,
            year_start=year_start,
            year_end=year_end,
            chart_position=chart_position,
            artist_style=artist_style
        )
        
        return jsonify({
            'songs': [s.to_dict() for s in songs],
            'progression': {
                'roman_numerals': progression.roman_numerals,
                'original_chords': progression.original_chords,
                'key': progression.key
            },
            'search_criteria': {
                'bpm': bpm,
                'bpm_tolerance': bpm_tolerance,
                'time_signature': time_signature,
                'genres': genres,
                'year_start': year_start,
                'year_end': year_end,
                'chart_position': chart_position,
                'artist_style': artist_style
            }
        })
    
    except Exception as e:
        print(f"Error in melody search: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/melody/more', methods=['POST'])
def melody_more_like_these():
    """
    Find more songs similar to user's selections.
    
    Expected JSON body:
    {
        "original_criteria": { ... },  // From the search response
        "liked_songs": [ ... ],        // Array of song objects user liked
        "excluded_songs": ["Artist - Title", ...]  // Songs to exclude
    }
    """
    try:
        from melody_claude import find_more_like_these, MelodySong
        
        data = request.json
        original_criteria = data.get('original_criteria', {})
        liked_songs_data = data.get('liked_songs', [])
        excluded_songs = data.get('excluded_songs', [])
        
        if not liked_songs_data:
            return jsonify({'error': 'liked_songs is required'}), 400
        
        # Convert to MelodySong objects
        liked_songs = [
            MelodySong(
                rank=s.get('rank', 10),
                song_name=s.get('song_name', ''),
                artist_name=s.get('artist_name', ''),
                chorus_chords=s.get('chorus_chords', ''),
                bpm=s.get('bpm', 0),
                genre=s.get('genre', ''),
                year=s.get('year', 0)
            )
            for s in liked_songs_data
        ]
        
        # Get more songs
        new_songs = find_more_like_these(
            original_criteria=original_criteria,
            liked_songs=liked_songs,
            excluded_songs=excluded_songs
        )
        
        return jsonify({
            'songs': [s.to_dict() for s in new_songs]
        })
    
    except Exception as e:
        print(f"Error in melody more: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/melody/tidal/auth', methods=['GET'])
def melody_tidal_auth():
    """Initiate Tidal device authentication."""
    try:
        client = get_tidal_client()
        auth_info = client.authenticate_device()
        return jsonify(auth_info)
    except Exception as e:
        print(f"Error starting Tidal auth: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/api/melody/tidal/status', methods=['GET'])
def melody_tidal_status():
    """Check Tidal authentication status."""
    try:
        client = get_tidal_client()
        return jsonify({'authenticated': client.is_authenticated()})
    except Exception as e:
        print(f"Error checking Tidal status: {e}")
        return jsonify({'error': str(e), 'authenticated': False}), 500


@app.route('/api/melody/tidal/check-complete', methods=['GET'])
def melody_tidal_check_complete():
    """Check if Tidal auth is complete and save session."""
    try:
        client = get_tidal_client()
        is_complete = client.check_auth_complete()
        return jsonify({'authenticated': is_complete})
    except Exception as e:
        print(f"Error checking auth completion: {e}")
        return jsonify({'error': str(e), 'authenticated': False}), 500


@app.route('/api/melody/tidal/disconnect', methods=['POST'])
def melody_tidal_disconnect():
    """Disconnect from Tidal and clear session."""
    try:
        global _tidal_client
        if _tidal_client:
            _tidal_client.disconnect()
            _tidal_client = None
        return jsonify({'success': True, 'authenticated': False})
    except Exception as e:
        print(f"Error disconnecting from Tidal: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/melody/tidal/debug', methods=['GET'])
def melody_tidal_debug():
    """Get Tidal connection debug info."""
    try:
        client = get_tidal_client()
        return jsonify(client.get_debug_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/melody/playlist', methods=['POST'])
def melody_create_playlist():
    """
    Create Tidal playlist with selected songs.
    
    Expected JSON body:
    {
        "name": "My Mashup Playlist",
        "description": "Songs matching Am C F G at 120 BPM",
        "songs": [
            {"artist_name": "Artist", "song_name": "Title"},
            ...
        ]
    }
    """
    try:
        client = get_tidal_client()
        
        if not client.is_authenticated():
            return jsonify({'error': 'Not authenticated with Tidal'}), 401
        
        data = request.json
        name = data.get('name', 'Melody Playlist')
        description = data.get('description', '')
        songs_data = data.get('songs', [])
        
        if not songs_data:
            return jsonify({'error': 'songs is required'}), 400
        
        # Format songs for Tidal client
        songs = [
            {'artist': s.get('artist_name', ''), 'title': s.get('song_name', '')}
            for s in songs_data
        ]
        
        playlist_url = client.create_playlist(name, description, songs)
        
        if playlist_url:
            return jsonify({
                'success': True,
                'playlist_url': playlist_url,
                'track_count': len(songs)
            })
        else:
            return jsonify({'error': 'Failed to create playlist'}), 500
    
    except Exception as e:
        print(f"Error creating playlist: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("🚀 LyricBox API Server starting on http://localhost:3001")
    app.run(host='0.0.0.0', port=3001, debug=True)

