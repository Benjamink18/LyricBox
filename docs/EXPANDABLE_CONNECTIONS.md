# Expandable Connections with Word Highlighting! ✨

## New Features

### 1. ✅ "+X more" is Now Clickable
- Click to expand and see ALL songs for that word
- Click "Show less" to collapse back to 2 songs
- Smooth hover effect (blue highlight)

### 2. ✅ All Songs Are Clickable
- Click any song name → Opens lyrics modal
- Works for both initial 2 songs AND expanded songs

### 3. ✅ Search Word Highlighted in Lyrics
- When you click a song from network results, the word is **highlighted in blue**
- Blue background glow around the word
- Makes it easy to find where the word appears in the song

---

## How It Works

### Expandable State
```typescript
const [expandedWords, setExpandedWords] = useState<Set<string>>(new Set())

const toggleExpanded = (word: string) => {
  // Add or remove word from expanded set
}
```

### Word Highlighting
```typescript
const handleViewLyrics = async (songId, title, artist, highlightWord?) => {
  let lyrics = await getSongLyrics(songId)
  
  if (highlightWord) {
    // Replace word with <strong>word</strong>
    const regex = new RegExp(`\\b(${highlightWord})\\b`, 'gi')
    lyrics = lyrics.replace(regex, '<strong>$1</strong>')
  }
  
  // Display with HTML rendering
}
```

---

## Visual Design

### "+X more" Button
- **Default:** Gray italic text
- **Hover:** Blue text with dark background
- **Expanded:** Shows "Show less" instead

### Highlighted Words in Lyrics
- **Color:** Bright blue (#4a9eff)
- **Background:** Soft blue glow
- **Padding:** Small padding for visibility
- **Font:** Bold weight

---

## Example Flow

1. Search for **"love"** in Network mode
2. See results like:
   ```
   love
   Depth 1 | perfect | ×24
   
   Shape of You - Ed Sheeran
   Perfect - Ed Sheeran
   +22 more  ← CLICK HERE
   ```

3. Click **"+22 more"** → Expands to show all 24 songs

4. Click any song (e.g., "Shape of You") → Opens lyrics modal

5. In the lyrics, every instance of **"love"** is highlighted in **blue**

6. Click **"Show less"** → Collapses back to 2 songs

---

## Test It!

**http://localhost:5173**

1. Click **"Network"** mode
2. Search for **"love"** (depth 3)
3. Find a word with **"+X more"**
4. Click **"+X more"** → See all songs expand
5. Click any song → See lyrics with **love** highlighted in blue
6. Click **"Show less"** → Collapse

---

## Status

**✅ Expandable connections working**  
**✅ All songs clickable**  
**✅ Word highlighting in lyrics modal**  
**✅ Smooth animations**

Network search is now fully interactive! 🎉





