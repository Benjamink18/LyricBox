<!-- e742983f-761d-494c-adf7-9d2e471cd9b7 fc1c08ea-ba55-4f39-bb66-24956cfe0562 -->
# Melody Feature - Simplified Rebuild

## The Flow (Plain English)

1. **User inputs:** chord sequence, BPM, key, time signature
2. **User adds filters (optional):** genre, year range, chart position, artist
3. **System converts:** chords to Roman numerals based on key
4. **Claude query:** Find 10 songs where the **CHORUS** matches these chords/BPM/key
5. **Claude returns:** song name, artist, chorus chords, BPM, genre (ranked 1-10)
6. **User reviews results:**

   - Deletes songs they don't want
   - **Option 1:** Connect to Tidal → Create playlist
   - **Option 2:** "More like these" → Claude finds similar songs (excludes removed ones)
   - New results append to list, repeat

## Architecture Changes

### What to KEEP

- [`backend/chord_converter.py`](backend/chord_converter.py) - Roman numeral conversion (works fine)
- [`backend/tidal_client.py`](backend/tidal_client.py) - But ONLY for playlist creation

### What to REMOVE/SIMPLIFY

- [`backend/melody_matcher.py`](backend/melody_matcher.py) - Delete entirely (no Tidal metadata lookup)
- [`backend/melody_claude.py`](backend/melody_claude.py) - Rewrite to return ALL data from Claude

### New Claude Prompt Structure

**Required fields (always sent):**

- Roman numerals (chord progression)
- Target BPM
- Target Key
- Time Signature

**Optional filters (only included if user provides them):**

- Genres (e.g., Pop, R&B, Hip-Hop)
- Year range (e.g., 2015-2024)
- Chart position range (e.g., "Top 10", "Top 20", "Top 50", "Top 100")
- Specific artist (e.g., "similar to Drake")

**Example prompt (with some filters used):**

```
Find 10 songs where the CHORUS uses this chord progression:
Roman numerals: vi → I → IV → V
Target BPM: 120 (±10)
Target Key: A minor
Time Signature: 4/4

Additional filters:
- Genres: Pop, R&B
- Chart position: Top 20 hits only
- Years: 2015-2024

IMPORTANT: Match the CHORUS only, not verses or bridges.

Return JSON array with these fields for each song:
- rank (1-10, your confidence in the match)
- song_name
- artist_name  
- chorus_chords (the actual chords used)
- bpm (actual song BPM)
- genre
- year (release year)

Rank by how closely the chorus matches the input progression.
```

**Example prompt (no optional filters):**

```
Find 10 songs where the CHORUS uses this chord progression:
Roman numerals: vi → I → IV → V
Target BPM: 120 (±10)
Target Key: A minor
Time Signature: 4/4

IMPORTANT: Match the CHORUS only, not verses or bridges.
[... rest of prompt ...]
```

### "More Like These" Feature

When user selects songs and clicks "More like these":

```
Original search criteria: [include original prompt]

The user liked these songs:
1. Artist - Song (BPM, Key, Genre)
2. Artist - Song (BPM, Key, Genre)

The user removed these songs (do not suggest again):
- Artist - Song
- Artist - Song

Find 10 MORE songs similar to the liked ones, matching the original criteria.
Do not repeat any previously suggested songs.
```

## Implementation Steps

### Step 1: Simplify melody_claude.py

Remove complex scoring. New `find_matching_songs()` returns:

```python
@dataclass
class MelodySong:
    rank: int           # 1-10 Claude's ranking
    song_name: str
    artist_name: str
    chorus_chords: str  # "Am C F G"
    bpm: int
    genre: str
    year: int
```

### Step 2: Add "more like these" method

```python
def find_more_like_these(
    original_criteria: dict,      # Original search params
    liked_songs: List[MelodySong], 
    excluded_songs: List[str]     # "Artist - Title" strings
) -> List[MelodySong]
```

### Step 3: Delete melody_matcher.py

No longer needed - Claude provides all data.

### Step 4: Update tidal_client.py

Remove BPM/key extraction code (lines 143-165). Keep only:

- `search_track()` - Just to get Tidal track ID for playlist
- `create_playlist()` - Create playlist from track IDs

### Step 5: Update API endpoints

**`/api/melody/search`** - Simplified:

- Input: chords, bpm, key, time_sig, filters
- Output: List of MelodySong from Claude

**`/api/melody/more`** - NEW:

- Input: original_criteria, liked_songs, excluded_songs
- Output: Additional MelodySong results

**`/api/melody/playlist`** - Keep but simplify:

- Input: List of songs (artist + title)
- Searches each on Tidal, creates playlist

### Step 6: Update Frontend

- Display results with: Rank, Song, Artist, Chorus Chords, BPM, Genre
- Checkboxes to select/deselect songs
- "Create Tidal Playlist" button (requires Tidal auth)
- "Find More Like These" button (sends selection back to Claude)
- Results append to list (don't replace)

## Files to Modify

1. [`backend/melody_claude.py`](backend/melody_claude.py) - Rewrite prompt, add "more like these"
2. [`backend/melody_matcher.py`](backend/melody_matcher.py) - DELETE
3. [`backend/tidal_client.py`](backend/tidal_client.py) - Remove BPM/key code, keep playlist only
4. [`backend/api_server.py`](backend/api_server.py) - Simplify endpoints, add `/api/melody/more`
5. [`frontend/src/App.tsx`](frontend/src/App.tsx) - Update UI for new flow

## Tidal Fix (Separate)

Still need to fix Tidal connection:

- Update `tidalapi` to v0.8.3
- Fix session file path for Railway
- Add proper error logging

This can be done alongside the feature rebuild.

### To-dos

- [ ] Add line_rhyme_words table to database schema
- [ ] Update import script to extract and store phonetic word data with positions
- [ ] Create enhanced search that queries line_rhyme_words and returns position data