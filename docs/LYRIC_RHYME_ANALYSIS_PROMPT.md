# Lyric Rhyme Analysis Prompt

Use this prompt with Claude or another LLM to analyze any song lyric for rhyme types. Output is structured JSON for easy searching and filtering.

---

## The Prompt

```
You are an expert lyric analyst specializing in rhyme detection and classification. Analyze the following lyrics and identify ALL rhyme instances, categorizing them by type.

## RHYME TYPE DEFINITIONS

### By Sound Quality
- **perfect**: Exact match of vowel + ending consonant (cat/hat, cry/lie)
- **assonance**: Same vowel sounds, different consonants (fate/save, bad/mad)
- **consonance**: Same consonant sounds, different vowels (lamp/limp, milk/walk)
- **family**: Consonants from same phonetic family - plosives (p/b/t/d/k/g), fricatives (f/v/s/z), nasals (m/n/ng)
- **additive_subtractive**: Same vowels plus/minus a consonant (eve/believe, art/heart)
- **identity**: Same word repeated or homophones (last/last, pane/pain)
- **slant**: Similar but not identical sounds that don't fit above categories

### By Syllable Count
- **masculine**: 1 syllable (time/crime)
- **feminine**: 2 syllables (walking/talking)
- **triple**: 3 syllables (tornado/volcano)
- **multi_4plus**: 4+ syllables

### By Position
- **end**: At line endings
- **internal**: Within lines
- **cross**: Between non-adjacent lines

### Hip-Hop Techniques
- **compound**: Phrase-to-phrase rhyming (problems/solve 'em)
- **chain**: Extended sequence of 4+ rhymes on same sound
- **mosaic**: Vowel sounds spread throughout (not just at rhyme points)
- **nested**: Secondary rhyme pattern within a primary chain
- **embedded**: Rhyme word hidden inside longer word (apologize contains "lies")
- **monorhyme**: 4+ consecutive lines with same end sound
- **wordplay_pun**: Homophone or double-meaning punchline

## OUTPUT FORMAT

Return a JSON object with this structure:

{
  "song_metadata": {
    "complexity_tier": 1-5,
    "complexity_tier_name": "Basic Pop | Advanced Pop | Hip-Hop Standard | Hip-Hop Advanced | Elite",
    "primary_techniques": ["list of main techniques used"],
    "rhyme_density_estimate": "low | medium | high | very_high"
  },
  
  "rhyme_groups": [
    {
      "group_id": "A1",
      "sound": "describe the sound (e.g., 'long I', 'short A', '-ight')",
      "sound_type": "perfect | assonance | consonance | family | slant | identity",
      "syllable_type": "masculine | feminine | triple | multi_4plus",
      "technique": "standard | compound | chain | mosaic | nested | embedded | monorhyme | wordplay_pun",
      "words": [
        {
          "word": "the word or phrase",
          "line_number": 1,
          "position": "end | internal | cross",
          "context": "few words before and after for context"
        }
      ],
      "chain_length": 2,
      "notes": "any special observations"
    }
  ],
  
  "schemes_by_section": [
    {
      "section": "Chorus 1 | Verse 1 | Bridge | etc",
      "line_range": "1-4",
      "scheme": "ABAB | AABB | XAXA | etc",
      "scheme_description": "brief description"
    }
  ],
  
  "notable_techniques": [
    {
      "technique": "name of technique",
      "location": "section and line numbers",
      "words_involved": ["word1", "word2"],
      "description": "why this is notable"
    }
  ],
  
  "statistics": {
    "total_rhyme_groups": 0,
    "perfect_rhymes": 0,
    "assonance_chains": 0,
    "consonance_pairs": 0,
    "compound_rhymes": 0,
    "multisyllabic_rhymes": 0,
    "identity_rhymes": 0,
    "internal_rhymes": 0,
    "longest_chain": 0,
    "wordplay_instances": 0
  }
}

## ANALYSIS INSTRUCTIONS

1. Read through the entire lyric first to identify the overall structure
2. Label sections (Verse 1, Chorus, Bridge, etc.) based on repetition patterns
3. For each section, identify the rhyme scheme using letters (A, B, C, X for non-rhyme)
4. Find ALL rhyme instances - don't miss internal rhymes or slant rhymes
5. Group rhymes by their sound (all words sharing "long I" go together, etc.)
6. Identify any advanced techniques (compounds, chains, wordplay)
7. Assess overall complexity tier based on techniques used
8. Be thorough - hip-hop lyrics especially have dense rhyming that's easy to miss

## COMPLEXITY TIER CRITERIA

- **Tier 1 (Basic Pop)**: Mostly perfect rhymes, end-of-line only, 2-word groups, AABB/ABAB
- **Tier 2 (Advanced Pop)**: + assonance, some internal rhymes, 3-4 word chains
- **Tier 3 (Hip-Hop Standard)**: + compound rhymes, multisyllabic (2-3 syl), 4-5 word chains
- **Tier 4 (Hip-Hop Advanced)**: + 5+ word chains, nested rhymes, pattern switching
- **Tier 5 (Elite)**: + dual simultaneous chains, embedded rhymes, wordplay punchlines, 40%+ density

---

## LYRICS TO ANALYZE

[PASTE LYRICS HERE]

---

Analyze these lyrics completely, identifying every rhyme instance. Output valid JSON only.
```

---

## Example Usage

Paste the prompt above into Claude, then replace `[PASTE LYRICS HERE]` with any song lyrics.

---

## Searching the Results

Once you have the JSON output, you can search/filter by:

### By Sound Type
```javascript
results.rhyme_groups.filter(g => g.sound_type === "assonance")
```

### By Technique
```javascript
results.rhyme_groups.filter(g => g.technique === "compound")
```

### By Position
```javascript
results.rhyme_groups.flatMap(g => g.words).filter(w => w.position === "internal")
```

### By Chain Length (find long chains)
```javascript
results.rhyme_groups.filter(g => g.chain_length >= 4)
```

### By Section
```javascript
results.schemes_by_section.filter(s => s.section.includes("Verse"))
```

### Get All Notable Techniques
```javascript
results.notable_techniques
```

### Get Statistics Summary
```javascript
results.statistics
```

---


```

---

