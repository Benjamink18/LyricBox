# AI Features Setup - Quick Guide

## 🚀 Complete Setup in 5 Steps (10 minutes)

### Step 1: Update Database Schema (2 minutes)

1. Open Supabase: https://supabase.com/dashboard/project/_/sql
2. Copy the contents of `database/add_concepts_table.sql`
3. Paste into SQL Editor
4. Click **Run**
5. You should see "Success. No rows returned"

### Step 2: Get Claude API Key (2 minutes)

1. Go to: https://console.anthropic.com/
2. Sign in (you already have Claude Max)
3. Click **API Keys** in left sidebar
4. Click **Create Key**
5. Name it "LyricBox"
6. Copy the key (starts with `sk-ant-`)

### Step 3: Add API Key to .env (30 seconds)

Open `backend/.env` and add this line:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Save the file.

### Step 4: Install Python Packages (1 minute)

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
pip install anthropic==0.39.0 flask==3.0.0 flask-cors==4.0.0
```

### Step 5: Run Concept Analysis (15-20 minutes)

Analyze all 797 songs with AI:

```bash
python analyze_concepts.py
```

This will:
- Process ~797 songs with Claude
- Extract themes, metaphors, tone, imagery from each
- Store in `song_concepts` table
- Take 15-20 minutes (1 second per song for rate limiting)
- Cost ~$2.40 total

Watch the progress bar to see it working!

---

## ✅ After Setup: Using AI Features

### Start the API Server (in a new terminal)

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
python api.py
```

Leave this running - it serves the AI title generation endpoint on port 3001.

### Use the Concepts Tab

1. Frontend should already be running at http://localhost:5174
2. Click **Concepts** tab
3. Click **Generate Random Concept**
4. See:
   - Random song's analyzed themes, tone, imagery
   - 10 AI-generated song title ideas based on those concepts
5. Click **Generate Another** for a new concept

### Test CLI Generator

```bash
cd backend
python concept_generator.py
```

This shows a random concept and generates titles in your terminal!

---

## 📊 What Gets Analyzed

For each of 797 songs, Claude extracts:

- **Themes**: love, heartbreak, celebration, rebellion, nostalgia, etc.
- **Tone**: melancholic, energetic, playful, reflective, angry, etc.
- **Imagery**: colors, seasons, places, objects mentioned
- **Metaphors**: key metaphors and what they represent
- **Story Arc**: if the song tells a story

---

## 💰 Cost Breakdown

- **One-time analysis**: 797 songs × $0.003/song = ~$2.40
- **Title generation**: $0.01 per concept (each time you click "Generate")
- **Total monthly estimate**: <$5 if you generate 100 concepts

Uses Claude 3.5 Sonnet - the best model for creative tasks!

---

## 🐛 Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you added it to `backend/.env`
- Make sure there are no spaces around the `=`
- Format: `ANTHROPIC_API_KEY=sk-ant-...`

**"No concepts found"**
- Run `python analyze_concepts.py` first
- Check Supabase SQL Editor to see if `song_concepts` table exists

**API server not responding**
- Make sure `python api.py` is running in a separate terminal
- Should show: `Running on http://127.0.0.1:3001`
- If port 3001 is taken, edit `api.py` and change the port

---

Ready to get started? Just follow the 5 steps above! 🎵

