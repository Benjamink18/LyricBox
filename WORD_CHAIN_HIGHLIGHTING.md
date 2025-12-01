# Word Chain Highlighting - Perfect! 🎯

## How It Works

When you click a song from Network mode, the modal highlights **all words in the chain** that led to this result.

---

## Examples

### Depth 1 (Direct Rhyme)
**Search:** "mine"  
**Result:** "fine" (rhymes with "mine")  
**Highlights:** **mine** + **fine**

Click "Shape of You":
```
If this world was mine
I'd take your dreams and make 'em multiply
If this world was mine, I'd take your enemies in front of fine people
```
Both **mine** and **fine** highlighted in blue!

---

### Depth 2 (Rhyme of Rhyme)
**Search:** "mine"  
**Depth 1:** "fine" (rhymes with "mine")  
**Depth 2:** "line" (rhymes with "fine")  
**Highlights:** **mine** + **fine** + **line**

Click any song with "line":
```
Walking on a fine line
The world is mine
This is my time to shine
```
All three words (**mine**, **fine**, **line**) highlighted!

---

### Depth 3 (Even Deeper)
**Search:** "mine"  
**Depth 1:** "fine"  
**Depth 2:** "line"  
**Depth 3:** "wine" (rhymes with "line")  
**Highlights:** **mine** + **fine** + **line** + **wine**

All four words highlighted in the song!

---

## Visual Design

### Context View:
```
┌─────────────────────────────────────┐
│ Shape of You - Ed Sheeran           │
│ [View Full Song] ×                  │
├─────────────────────────────────────┤
│                                     │
│ If this world was mine              │  ← "mine" in bold blue
│ I'd take your dreams                │
│ If this world was mine              │  ← "mine" in bold blue again
│ And make 'em fine                   │  ← "fine" in bold blue too!
│ ─────────────────────               │
│                                     │
│ (Next occurrence)                   │
└─────────────────────────────────────┘
```

### Highlighted Words:
- **Bold blue text** (#4a9eff)
- **Soft blue background glow**
- **Multiple words** can be highlighted in same line
- Works in both context and full view modes

---

## Toggle Label Update

**Old:** "Show all matches" (unchecked by default)  
**New:** **"1 result per song"** (checked by default ✓)

Makes it crystal clear what the checkbox does!

---

## Test It!

**Refresh http://localhost:5173**

### Test Depth 1:
1. Network mode → Search **"mine"**
2. Click on **"fine"** word card (Depth 1)
3. Click any song
4. See both **mine** and **fine** highlighted!

### Test Depth 2:
1. Network mode → Search **"mine"** (depth 3)
2. Click on a **Depth 2** word (e.g., "line")
3. Click any song  
4. See **mine**, the depth 1 word, AND **line** highlighted!

---

## Files Changed

### `/frontend/src/App.tsx`
- Changed `modalHighlightWord` → `modalHighlightWords` (array)
- Updated `handleViewLyrics()` to accept array of words
- Updated `getContextView()` to search for multiple words
- Pass word chain when clicking songs: `[searchWord, currentWord]`
- Highlight all words in both context and full views

### Label Changes:
- Renamed `showAllMatches` → `onePerSong`
- Default: `true` (checked)
- Label: "1 result per song"

---

**Status:** Word chain highlighting complete! 🚀

