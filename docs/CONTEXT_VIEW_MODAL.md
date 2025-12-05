# Context View in Lyrics Modal! 🎯

## What's New

When you click a song from **Network mode**, the lyrics modal now has **two view modes**:

### 1. 📍 Context View (Default)
- Shows only the parts where the search word appears
- 4 lines before + match line + 4 lines after
- Word highlighted in **bold blue**
- Multiple occurrences shown separately
- **Button:** "View Full Song" to expand

### 2. 📄 Full Song View
- Shows complete lyrics from start to finish
- Word still highlighted throughout
- **Button:** "View in Context" to collapse back

---

## User Flow

### From Network Mode:
1. Search "love" in Network mode
2. See network results (e.g., "dove", "above", "shove")
3. Click any song name (e.g., "Shape of You - Ed Sheeran")
4. **Modal opens in Context View:**
   ```
   ┌──────────────────────────────────────┐
   │ Shape of You - Ed Sheeran            │
   │ [View Full Song] ×                   │
   ├──────────────────────────────────────┤
   │ I've been looking for someone        │
   │ Put my faith in so much              │
   │ I'm asking you to stay               │
   │ Say you'll never, never leave        │
   │ I'm in love with your body           │  ← love highlighted
   │ Oh, I                                │
   │ Oh, I                                │
   │ Oh, I                                │
   │ Oh, I                                │
   │ ─────────────────────────            │
   │                                      │
   │ (next occurrence of "love")          │
   │ ...                                  │
   └──────────────────────────────────────┘
   ```

5. Click **"View Full Song"** → Expands to show entire lyrics (love still highlighted)
6. Click **"View in Context"** → Collapses back to context view

### From Simple Mode:
1. Search "love" in Simple mode
2. Click any result card
3. **Modal opens in Full View** (no context view needed - already shown in results)

---

## Visual Design

### Context View:
- **Context lines:** Gray text (#666)
- **Match line:** Bright text with word in **bold blue**
- **Divider:** Thin line between multiple occurrences
- **Spacing:** Clean 32px between contexts
- **Font:** Georgia serif for readability

### Toggle Button:
- **Blue button** next to × close button
- **Context mode:** Shows "View Full Song"
- **Full mode:** Shows "View in Context"
- Smooth hover effect

### Highlighted Words:
- **Bold blue text** (#4a9eff)
- **Soft blue background glow**
- **Slight padding** for emphasis
- Works in both context and full views

---

## Example

Search **"love"** in Network mode → Click "ducks" → Click "Squabble Up":

**Context View Shows:**
```
Occurrence 1:
  Four lines before...
  I'm showing love        ← "love" in bold blue
  Four lines after...
  ────────────────

Occurrence 2:
  Four lines before...
  Can't get enough love   ← "love" in bold blue
  Four lines after...
```

Click **"View Full Song"** → See entire lyrics with all instances of "love" highlighted

---

## Files Changed

### `/frontend/src/App.tsx`
- Added `modalViewMode` state ('context' or 'full')
- Added `modalHighlightWord` state
- Added `getContextView()` function (extracts word contexts)
- Updated modal JSX to support both view modes
- Added toggle button in modal header

### `/frontend/src/App.css`
- Added `.modal-actions` styling
- Added `.view-toggle-btn` styling  
- Added `.context-view` and `.context-block` styling
- Added `.context-divider` for separating occurrences

---

## Test It!

**Refresh http://localhost:5173**

1. Click **"Network"** mode
2. Search for **"love"** (depth 3)
3. Click any song name in the results
4. See **Context View** with word highlighted
5. Click **"View Full Song"** → See complete lyrics
6. Click **"View in Context"** → Back to context view

Perfect for quickly finding where the word appears! 🎯





