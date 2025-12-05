# Rhyme Types Research Package

> Complete reference for songwriting rhyme techniques, compiled for use with AI music generation (Suno, etc.) and lyric analysis in Cursor.

---

## 📁 Package Contents

```
rhyme-research-package/
├── README.md                              # This file
├── RHYME_TYPES_REFERENCE.md               # Complete markdown reference (human-readable)
├── rhyme_types_data.json                  # Structured data (for code/prompts)
├── CHAT_SUMMARY.md                        # Summary of research conversation
├── bad-blood-rhyme-analysis.html          # Interactive analysis: Taylor Swift
└── love-the-way-you-lie-rhyme-analysis.html  # Interactive analysis: Eminem
```

---

## 🎯 Purpose

This package was created to support:

1. **Suno AI prompt templates** — Understanding rhyme complexity tiers for better music generation
2. **Lyric analysis** — Color-coded breakdown of professional songwriting techniques
3. **Songwriting education** — Complete reference of rhyme types from basic to elite
4. **Template creation** — Structured data for building lyric analysis tools

---

## 📚 Quick Start

### For Human Reference
Open `RHYME_TYPES_REFERENCE.md` — contains everything in readable format with examples.

### For Code/Prompts
Use `rhyme_types_data.json` — structured data you can parse and use programmatically.

### For Visual Examples
Open the HTML files in a browser to see color-coded rhyme analysis of real songs.

---

## 🎨 Rhyme Type Categories

### By Sound Quality
| Type | Strength | Example |
|------|----------|---------|
| Perfect | Strongest | cat/hat, cry/lie |
| Assonance | Medium | fate/save, bad/mad |
| Consonance | Weak-Medium | lamp/limp |
| Family | Weak-Medium | crate/braid |
| Slant/Near | Weak | worm/swarm |

### By Position
- **End rhyme** — At line endings (most common)
- **Internal rhyme** — Within lines
- **Cross rhyme** — Between non-adjacent lines

### By Syllable Count
- **Masculine** — 1 syllable (time/crime)
- **Feminine** — 2 syllables (walking/talking)
- **Triple** — 3 syllables (tornado/volcano)

### Hip-Hop Specific
- **Multisyllabic (Multis)** — 2+ syllables across words
- **Compound** — Phrase-to-phrase (problems/solve 'em)
- **Chain** — Extended sequences (5+ words)
- **Mosaic** — Vowel sounds spread throughout
- **Nested** — Rhymes inside rhymes
- **Embedded** — Hidden words (apologize contains "lies")

---

## 📊 Complexity Tiers (For AI Prompts)

| Tier | Name | Key Techniques | Example Artists |
|------|------|----------------|-----------------|
| 1 | Basic Pop | Perfect rhymes, end-of-line, AABB | Simple pop hooks |
| 2 | Advanced Pop | + Assonance, internal, 3-4 word chains | Ed Sheeran |
| 3 | Hip-Hop Standard | + Compound, multisyllabic (2-3 syl) | Drake, Kendrick |
| 4 | Hip-Hop Advanced | + 5+ word chains, nested, pattern switching | Nas, Big Pun |
| 5 | Elite | + Dual chains, embedded, 40%+ density | Eminem, MF DOOM |

---

## 🔍 Song Analysis Examples

### Pop: "Bad Blood" (Taylor Swift)
- **Primary technique**: Perfect rhymes + assonance layers
- **Notable**: Double-layer hook (bad/mad + blood/love)
- **Rhyme density**: Standard pop level
- **Compound rhyme**: "problems/solve 'em" (hip-hop borrowed)

### Hip-Hop: "Love The Way You Lie" (Eminem)
- **Primary technique**: Multisyllabic chains + compound rhymes
- **Notable**: 6-word chains, dual simultaneous chains, "windowpane" pun
- **Rhyme density**: 40%+ (elite level)
- **Embedded rhyme**: "apologize" contains "lies"

---

## 💡 Usage Ideas for Cursor

### 1. Suno Prompt Templates
```
Create a song with [Tier 3] rhyme complexity:
- Use compound rhymes
- 4-5 word assonance chains
- Mix internal and end rhymes
- XAXA scheme in verses
```

### 2. Lyric Analysis Tool
Parse `rhyme_types_data.json` to build a tool that:
- Identifies rhyme types in user lyrics
- Suggests improvements based on target complexity tier
- Color-codes rhymes by type

### 3. Rhyme Suggestion Engine
Use the JSON data to:
- Suggest rhymes by type (not just perfect)
- Build compound rhyme chains
- Find multisyllabic matches

---

## 📖 Sources

Research compiled from:
- ASCAP songwriting resources
- iZotope music production guides  
- Academic hip-hop analysis (Adam Krims, Adam Bradley)
- Wikipedia rhyme type entries
- MasterClass (Nas teaches hip-hop)
- Various songwriting education sites

---

## 🔗 Related

This package supports work on:
- SwearBy recommendations network
- Suno AI music generation templates
- Song analysis and template creation workflows

---

*Package created via Claude conversation — November 2025*
