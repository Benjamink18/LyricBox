# 🎵 LyricBox AI Setup - Start Here!

## ✅ What's Already Done

- ✅ **797 songs imported** with lyrics from Genius
- ✅ **Rhyme search working** with genre/year/rank/artist filters  
- ✅ **All code implemented** - AI analyzer, concept generator, API ready
- ✅ **Frontend complete** - Concepts tab ready to use

## 🚀 What You Need to Do (10 minutes)

### Step 1: Update Supabase Database (2 min) ⚠️ REQUIRED

1. Open your Supabase project: https://supabase.com/dashboard
2. Click **SQL Editor** in the left sidebar
3. Open the file: `database/add_concepts_table.sql`
4. Copy ALL the SQL code
5. Paste into Supabase SQL Editor
6. Click **Run** (or press Cmd+Enter)
7. Should see: ✅ "Success. No rows returned"

### Step 2: Get Claude API Key (2 min) ⚠️ REQUIRED

1. Go to: https://console.anthropic.com/
2. Sign in with your Claude account
3. Click **API Keys** in the left menu
4. Click **Create Key**
5. Name it "LyricBox"  
6. **Copy the entire key** (starts with `sk-ant-`)

### Step 3: Add API Key to .env (1 min) ⚠️ REQUIRED

1. Open: `backend/.env`
2. Add this line at the end:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```
3. Save the file

### Step 4: Install Python Packages (1 min)

Open your terminal and run:

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
bash install_ai_packages.sh
```

### Step 5: Analyze All Songs (15-20 min)

This runs once to analyze all 797 songs:

```bash
# Make sure you're still in backend with venv activated
python analyze_concepts.py
```

You'll see a progress bar. This will:
- Analyze each song with Claude AI
- Extract themes, metaphors, tone, imagery
- Store in database
- Cost ~$2.40 total (one-time)

**Go get coffee while this runs!** ☕

---

## 🎯 Using the AI Features

### Option A: Use the Web App (Recommended)

1. **Start the API server** (in one terminal):
   ```bash
   cd /Users/benkohn/Desktop/LyricBox/backend
   source venv/bin/activate
   python api.py
   ```
   Leave this running.

2. **Start the frontend** (in another terminal):
   ```bash
   cd /Users/benkohn/Desktop/LyricBox/frontend
   npm run dev
   ```

3. **Open the app**: http://localhost:5174

4. **Click "Concepts" tab** → **"Generate Random Concept"**

You'll see:
- A random song's themes, tone, imagery
- 10 AI-generated song title ideas
- Click "Generate Another" for more!

### Option B: Use the CLI

```bash
cd /Users/benkohn/Desktop/LyricBox/backend
source venv/bin/activate
python concept_generator.py
```

Shows concepts and titles in your terminal!

---

## 📁 Files Created for You

### Code (All Implemented)
- ✅ `backend/ai_rhyme_analyzer.py` - Claude AI integration
- ✅ `backend/analyze_concepts.py` - Batch analyzer  
- ✅ `backend/concept_generator.py` - CLI tool
- ✅ `backend/api.py` - Flask API for frontend
- ✅ `frontend/src/pages/Concepts.tsx` - Concepts UI

### Database
- ✅ `database/add_concepts_table.sql` - Schema update

### Documentation
- ✅ `SETUP_AI.md` - Detailed setup guide
- ✅ `NEXT_STEPS.md` - What's done and what's next
- ✅ `AI_SETUP.md` - Technical documentation
- ✅ `START_HERE.md` - This file!

### Scripts
- ✅ `backend/install_ai_packages.sh` - Package installer

---

## 🎵 What the AI Extracts

For each song, Claude analyzes:

| Feature | Example |
|---------|---------|
| **Themes** | love, heartbreak, moving on, empowerment |
| **Tone** | playful yet bitter, melancholic, energetic |
| **Imagery** | red lips, white dress, midnight rain |
| **Metaphors** | "blank space" → new beginning after breakup |
| **Story Arc** | relationship cycle from infatuation to revenge |

---

## 💰 Cost

- **First run** (797 songs): ~$2.40 one-time
- **Each title generation**: ~$0.01
- **Monthly estimate**: <$5 (if you generate 100 concepts)

All using Claude 3.5 Sonnet - the best creative AI!

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
→ Check `backend/.env` has the key on its own line  
→ Format: `ANTHROPIC_API_KEY=sk-ant-...` (no spaces)

### "No concepts found"
→ Run `python analyze_concepts.py` first  
→ Takes 15-20 minutes to complete

### API not responding
→ Make sure `python api.py` is running  
→ Should show "Running on http://127.0.0.1:3001"

### SQL Error in Supabase
→ Make sure you copied ALL of `add_concepts_table.sql`  
→ Try running it again (it won't break anything)

---

## ⚡ Quick Start Checklist

- [ ] Run SQL in Supabase (Step 1)
- [ ] Get Claude API key (Step 2)  
- [ ] Add key to `.env` (Step 3)
- [ ] Install packages (Step 4)
- [ ] Run analysis (Step 5)
- [ ] Start API server
- [ ] Use Concepts tab!

---

**Ready? Start with Step 1 above!** 🚀

Once you've done Steps 1-3, come back and we'll run the analysis together.

