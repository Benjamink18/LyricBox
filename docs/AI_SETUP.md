# AI Features Setup Guide

## Overview

LyricBox now includes AI-powered concept analysis and title generation using Claude API.

## Features

1. **Concept Analysis** - AI analyzes all songs for:
   - Main themes (love, heartbreak, celebration, etc.)
   - Metaphors and what they represent
   - Emotional tone
   - Key imagery (colors, places, objects)
   - Story arcs

2. **Random Concept Generator** - In the "Concepts" tab:
   - Click "Generate Random Concept"
   - See a random song's analyzed themes
   - Get 10 AI-generated title ideas based on those concepts

## Setup Steps

### 1. Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### 2. Add to .env File

Add this line to `/Users/benkohn/Desktop/LyricBox/backend/.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Install Anthropic Package

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
pip install anthropic==0.39.0
```

### 4. Update Supabase Schema

Run the updated `database/schema.sql` in your Supabase SQL Editor to create the `song_concepts` table.

### 5. Analyze Songs

After all 800 songs are imported, run:

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
python analyze_concepts.py
```

This will take 15-20 minutes and analyze all songs with Claude.

### 6. Test the Generator

You can test it via CLI:

```bash
python concept_generator.py
```

Or use the "Concepts" tab in the web app!

## Cost Estimate

- Claude 3.5 Sonnet: ~$0.003 per song analysis
- 800 songs × $0.003 = ~$2.40 total
- Title generation: ~$0.01 per request

## Files Created

- `backend/ai_rhyme_analyzer.py` - AI analyzer class
- `backend/analyze_concepts.py` - Batch analysis script
- `backend/concept_generator.py` - CLI generator
- `database/schema.sql` - Updated with song_concepts table
- Frontend - Concepts page with generator UI

