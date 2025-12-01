# LyricBox

A personal songwriting toolkit that shows you how words rhyme in real songs. Instead of just seeing "tie" and "fly", see the full lyrical context where those rhymes are used.

## Features

- **Rhyme Search**: Find lines ending with any word across your song database
- **Context View**: See surrounding lyrics to understand the full rhyme scheme
- **Deduplication**: No repeated choruses cluttering results
- **Multiple Results**: Toggle to show all unique rhymes from each song
- **Concepts** *(coming soon)*: Explore thematic connections in lyrics

## Architecture

- **Backend**: Python scripts to fetch lyrics and analyze rhymes
- **Frontend**: React PWA (Progressive Web App)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Cloudflare Pages
- **Auth**: Cloudflare Access (Google Workspace)

## Quick Start

### 1. Set up Supabase

1. Go to [supabase.com](https://supabase.com) and open your project
2. Go to **SQL Editor** and run the contents of `database/schema.sql`
3. Go to **Settings > API** and get your keys

### 2. Get a Genius API Token

1. Go to [genius.com/api-clients](https://genius.com/api-clients)
2. Create a free API client
3. Copy the **Client Access Token**

### 3. Set up the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your credentials
cp env.example .env
# Edit .env with your Genius token and Supabase keys
```

### 4. Import Songs

```bash
# Import from your curated song list
python import_songs.py

# Or add specific songs
python main.py add "Song Title" "Artist Name"

# Search via CLI
python main.py search "word"
```

### 5. Set up the Frontend

```bash
cd frontend
npm install
cp env.example .env
# Edit .env with Supabase URL + anon key
npm run dev
```

Visit http://localhost:5173

### 6. Deploy to Cloudflare Pages

1. Push to GitHub
2. Connect repo in Cloudflare Pages
3. Build settings:
   - Build command: `cd frontend && npm run build`
   - Build output directory: `frontend/dist`
4. Add environment variables
5. Enable Cloudflare Access for privacy

## Project Structure

```
LyricBox/
├── backend/
│   ├── main.py              # CLI for database operations
│   ├── import_songs.py      # Import from songs.json
│   ├── lyrics_fetcher.py    # Genius API integration
│   ├── rhyme_analyzer.py    # CMU phonetic matching
│   ├── database.py          # Supabase operations
│   └── songs.json           # Curated song list
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main app with sidebar
│   │   ├── App.css          # Styling
│   │   └── lib/supabase.ts  # Database queries
│   └── dist/                # Built PWA
├── database/
│   └── schema.sql           # Supabase schema
└── README.md
```

## Current Status

✅ **Database**: 797 songs imported (2005-2024 Billboard Top 40)
✅ **Rhyme Search**: Fully functional with filters
✅ **Filters**: Genre, Year, Billboard Rank, Artist
⏳ **AI Concepts**: Ready to analyze (see below)

## Next Steps: AI Concept Analysis

### 1. Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up/login with your email
3. Go to API Keys → Create Key
4. Copy the key (starts with `sk-ant-`)

### 2. Add to .env

Edit `backend/.env` and add:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Install AI Dependencies

```bash
cd backend
source venv/bin/activate
pip install anthropic==0.39.0 flask==3.0.0 flask-cors==4.0.0
```

### 4. Run Concept Analysis

This will analyze all 797 songs with Claude (~$2.40 total cost, 15-20 min):

```bash
python analyze_concepts.py
```

### 5. Start the API Server

In a separate terminal:

```bash
cd backend
source venv/bin/activate
python api.py
```

### 6. Use the Concepts Feature

- Go to the Concepts tab in the app
- Click "Generate Random Concept"
- See themes, tone, imagery from a random song
- Get 10 AI-generated title ideas

## CLI Tools

### Test Concept Generator

```bash
python concept_generator.py
```

### Add More Songs Manually

```bash
python main.py add "Song Title" "Artist Name"
```

## Adding More Songs

Edit `backend/songs.json` and re-run:

```bash
cd backend
source venv/bin/activate
python import_songs.py
```

---

*Personal use only - not for commercial distribution*
