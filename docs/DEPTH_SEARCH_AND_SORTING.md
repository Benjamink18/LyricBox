# Depth-Based Rhyme Network Search + Multi-Level Sorting

## 🎯 Overview

A sophisticated rhyme search system that:
1. **Searches by depth** - discovers rhyme connections across the entire database
2. **Multi-level sorting** - customizable sort priority with drag-and-drop

---

## 🔍 Depth-Based Search

### How It Works

**Searches ACROSS ALL SONGS** to build a rhyme network.

```
Search: "phone"

DEPTH 0: phone (search term)

DEPTH 1: Direct rhymes with "phone" found anywhere in database
  Song 12: phone ↔ tone
  Song 89: phone ↔ go
  Song 23: phone ↔ bone
  → New words: [tone, go, bone]

DEPTH 2: Rhymes with depth-1 words
  Song 47: go ↔ know
  Song 15: tone ↔ stone
  → New words: [know, stone]

DEPTH 3: Rhymes with depth-2 words
  Song 92: know ↔ flow
  Song 8: stone ↔ zone
  → New words: [flow, zone]
```

### Cross-Song Learning

**Example:**
- Song A teaches: "phone" ↔ "go"
- Song B teaches: "go" ↔ "flow"
- **Combined network:** phone → go → flow

The system learns rhyme relationships across the entire database!

### Why This Matters

Claude's analysis stores ALL rhyme pairs within a song:

```
Song with: "callin', bottom, autumn, got'em, problem"

Database stores:
- callin' ↔ bottom
- callin' ↔ autumn
- callin' ↔ got'em
- callin' ↔ problem
- bottom ↔ autumn
- bottom ↔ got'em
- ... (all combinations)
```

So **Depth 1** already captures sophisticated multi-word chains from individual songs.  
**Depth 2+** discovers creative connections between songs.

---

## 📊 Multi-Level Sorting

### Sort Criteria

1. **Depth** (1→3 or 3→1)
   - Depth 1 = Obvious/safe rhymes
   - Depth 3 = Creative/rare rhymes

2. **Rhyme Type** (quality-based priority)
   - perfect → multi → compound → assonance → consonance → slant → embedded

3. **Frequency** (how many times word appears)
   - High frequency = common across many songs
   - Low frequency = unique/rare

4. **Alphabetical** (A→Z or Z→A)

### How to Use

**Click-based priority:**
1. Click "Depth" → Primary sort by depth
2. Click "Frequency" → Secondary sort by frequency  
3. Click "A-Z" → Tertiary sort alphabetically

**Toggle direction:**
- Click same button again → Toggles ↑/↓

**Drag to reorder:**
- Drag sort items to change priority

**Example Sort Configuration:**

```
[1] Depth: ↓ (High to Low - rare rhymes first)
[2] Rhyme Type: ↑ (Perfect rhymes first)
[3] Frequency: ↓ (Common words first)
```

This would show:
- Depth 3 results first (creative)
- Within depth 3, perfect rhymes first
- Within perfect rhymes, most common words first

---

## 🚀 Implementation

### Backend (TypeScript)

**Search Function:**
```typescript
const result = await searchRhymeNetworkByDepth("phone", 3)

// Returns:
{
  searchWord: "phone",
  totalWords: 47,
  totalConnections: 156,
  maxDepth: 3,
  layers: [
    {
      depth: 1,
      wordsDiscovered: ["tone", "go", "bone"],
      connections: [...]
    },
    ...
  ]
}
```

**Prepare for Sorting:**
```typescript
const sortableResults = prepareResultsForSorting(result)

// Returns array of:
{
  word: "flow",
  depth: 3,
  rhymeType: "perfect",
  frequency: 7,  // Appears 7 times across results
  connections: [...]
}
```

**Apply Sorting:**
```typescript
const sortOrder: SortCriterion[] = [
  { id: '1', field: 'depth', direction: 'desc', label: 'Depth' },
  { id: '2', field: 'frequency', direction: 'desc', label: 'Frequency' }
]

const sorted = applySorting(sortableResults, sortOrder)
```

### Frontend (React Component)

**SortBuilder Component:**
```tsx
import { SortBuilder } from './components/SortBuilder'

function RhymeSearch() {
  const [sortOrder, setSortOrder] = useState<SortCriterion[]>([])
  const [results, setResults] = useState<SortableRhymeResult[]>([])
  
  // After search
  const handleSearch = async () => {
    const networkResult = await searchRhymeNetworkByDepth(query, 3)
    const sortable = prepareResultsForSorting(networkResult)
    const sorted = applySorting(sortable, sortOrder)
    setResults(sorted)
  }
  
  // When sort changes
  useEffect(() => {
    if (results.length > 0) {
      const sorted = applySorting(results, sortOrder)
      setResults(sorted)
    }
  }, [sortOrder])
  
  return (
    <div>
      <SortBuilder sortOrder={sortOrder} onChange={setSortOrder} />
      {/* Display results */}
    </div>
  )
}
```

---

## 💡 Use Cases

### 1. Find Obvious Rhymes
```
Sort: [1] Depth: ↑ (1 first)
```
Shows only direct rhymes (safe, common connections)

### 2. Find Creative/Rare Rhymes
```
Sort: [1] Depth: ↓ (3 first)
      [2] Frequency: ↑ (rare first)
```
Shows distant, unique connections (creative wordplay)

### 3. Find High-Quality Rhymes
```
Sort: [1] Rhyme Type: ↑ (perfect first)
      [2] Frequency: ↓ (common first)
```
Shows perfect rhymes that are commonly used

### 4. Discover Cross-Song Patterns
```
Sort: [1] Depth: ↓ (3 first)
      [2] Frequency: ↓ (common first)
```
Shows words that appear frequently at deep depths = creative patterns used across many songs

---

## 📁 Files Created

1. **`frontend/src/lib/supabase.ts`**
   - `searchRhymeNetworkByDepth()` - Depth-based search
   - `prepareResultsForSorting()` - Transform results
   - `applySorting()` - Multi-level sorting logic

2. **`frontend/src/components/SortBuilder.tsx`**
   - Drag-and-drop sort builder UI
   - Click to add/toggle
   - Visual priority indicators

---

## 🎨 UI Features

✅ **Click to add** - Click any sort button to add it to the chain  
✅ **Click to toggle** - Click active button to reverse direction (↑↓)  
✅ **Drag to reorder** - Change sort priority by dragging  
✅ **Visual priority** - Numbered badges show order (1, 2, 3...)  
✅ **Active indicators** - Highlighted buttons + direction arrows  
✅ **Easy removal** - X button to remove from chain  

---

## 🚀 Next Steps

1. **Integrate into main App.tsx**
   - Replace old search with `searchRhymeNetworkByDepth()`
   - Add `<SortBuilder />` component
   - Apply sorting to results

2. **Display depth layers**
   - Group results by depth visually
   - Show "Depth 1", "Depth 2", "Depth 3" sections
   - Different styling for each depth

3. **Add filtering**
   - Filter by specific rhyme types
   - Filter by depth range
   - Filter by frequency threshold

4. **Export/Share**
   - Save favorite sort configurations
   - Share rhyme network visualizations

---

**The system is ready to go! Once the adaptive batch test completes and the database is populated, this will provide powerful cross-song rhyme discovery.** 🎯





