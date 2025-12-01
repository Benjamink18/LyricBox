import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)

export interface Song {
  id: string
  title: string
  artist: string
  year: number | null
  billboard_rank: number | null
  genre: string | null
}

export interface LyricsLine {
  id: string
  song_id: string
  line_number: number
  line_text: string
  last_word: string
  context_before: string
  context_after: string
  context_hash: string
}

export interface RhymeResult {
  line: LyricsLine
  song: Song
}

export interface Filters {
  genres?: string[]
  years?: number[]
  minRank?: number
  maxRank?: number
  artist?: string
}

export interface RhymeNetworkFilters {
  rhymeTypes?: string[]      // Filter by rhyme type
  genres?: string[]           // Filter by main genre
  detailedGenres?: string[]  // Filter by detailed genre tags
  years?: number[]            // Filter by year
  minRank?: number           // Minimum Billboard rank (1 = best)
  maxRank?: number           // Maximum Billboard rank (40 = worst)
  artists?: string[]         // Filter by specific artists
  depths?: number[]          // Which depths to include (1, 2, 3)
  minFrequency?: number      // Minimum word frequency
}

export interface SimpleRhymeResult {
  word: string
  linesBefore: string[]
  matchLine: string
  linesAfter: string[]
  lineNumber: number
  song: Song
}

/**
 * Simple search - finds the word at the end of lines and shows context.
 */
export async function searchRhymes(
  word: string,
  filters: RhymeNetworkFilters = {},
  showAllMatches: boolean = false
): Promise<SimpleRhymeResult[]> {
  const normalizedWord = word.toLowerCase().trim()
  
  // Get all songs with lyrics
  let query = supabase
    .from('songs')
    .select(`
      id,
      title,
      artist,
      year,
      billboard_rank,
      genre,
      lyrics_raw
    `)

  // Apply filters
  if (filters.genres && filters.genres.length > 0) {
    query = query.in('genre', filters.genres)
  }
  
  if (filters.years && filters.years.length > 0) {
    query = query.in('year', filters.years)
  }
  
  if (filters.minRank !== undefined) {
    query = query.gte('billboard_rank', filters.minRank)
  }
  
  if (filters.maxRank !== undefined) {
    query = query.lte('billboard_rank', filters.maxRank)
  }

  const { data, error } = await query

  if (error) {
    console.error('Search error:', error)
    return []
  }

  const results: SimpleRhymeResult[] = []
  const seenSongs = new Set<string>() // Track by title+artist to avoid duplicates

  for (const song of data || []) {
    // Skip if we've already processed this song (by title+artist)
    const songKey = `${song.title.toLowerCase()}|${song.artist.toLowerCase()}`
    if (seenSongs.has(songKey) && !showAllMatches) {
      continue
    }
    
    const lyrics = song.lyrics_raw || ''
    const lines = lyrics.split('\n')
    
    // Find all lines where the search word is the LAST word
    let matchesInSong: SimpleRhymeResult[] = []
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      if (!trimmedLine) return
      
      // Get the last word (remove punctuation)
      const words = trimmedLine.split(/\s+/)
      const lastWord = words[words.length - 1].replace(/[.,!?;:"'()[\]]/g, '').toLowerCase()
      
      // Check if last word matches search word
      if (lastWord === normalizedWord) {
        // Get 4 non-empty lines before and after (ignoring blank lines)
        const linesBefore: string[] = []
        const linesAfter: string[] = []
        
        // Get lines before (going backwards)
        let beforeIndex = index - 1
        while (linesBefore.length < 4 && beforeIndex >= 0) {
          const beforeLine = lines[beforeIndex].trim()
          if (beforeLine) {
            linesBefore.unshift(beforeLine)
          }
          beforeIndex--
        }
        
        // Get lines after (going forwards)
        let afterIndex = index + 1
        while (linesAfter.length < 4 && afterIndex < lines.length) {
          const afterLine = lines[afterIndex].trim()
          if (afterLine) {
            linesAfter.push(afterLine)
          }
          afterIndex++
        }
        
        matchesInSong.push({
          word: normalizedWord,
          linesBefore,
          matchLine: trimmedLine,
          linesAfter,
          lineNumber: index + 1,
          song: {
            id: song.id,
            title: song.title,
            artist: song.artist,
            year: song.year,
            billboard_rank: song.billboard_rank,
            genre: song.genre
          }
        })
      }
    })
    
    // If showAllMatches is false, only take the first match per song
    if (matchesInSong.length > 0) {
      seenSongs.add(songKey)
      if (showAllMatches) {
        results.push(...matchesInSong)
      } else {
        results.push(matchesInSong[0])
      }
    }
  }

  return results
}

export async function getSongStats(): Promise<{ songs: number; lines: number }> {
  const [songsResult, linesResult] = await Promise.all([
    supabase.from('songs').select('id', { count: 'exact', head: true }),
    supabase.from('lyrics_lines').select('id', { count: 'exact', head: true })
  ])

  return {
    songs: songsResult.count || 0,
    lines: linesResult.count || 0
  }
}

export async function getDistinctGenres(): Promise<string[]> {
  const { data, error } = await supabase
    .from('songs')
    .select('genre')
    .not('genre', 'is', null)
    .order('genre')

  if (error) return []
  
  const genres = [...new Set(data.map(d => d.genre as string))]
  return genres.sort()
}

export async function getDistinctYears(): Promise<number[]> {
  const { data, error } = await supabase
    .from('songs')
    .select('year')
    .not('year', 'is', null)
    .order('year', { ascending: false })

  if (error) return []
  
  const years = [...new Set(data.map(d => d.year as number))]
  return years.sort((a, b) => b - a)
}

export async function getDistinctArtists(): Promise<string[]> {
  const { data, error } = await supabase
    .from('songs')
    .select('artist')
    .order('artist')

  if (error) return []
  
  const artists = [...new Set(data.map(d => d.artist as string))]
  return artists.sort()
}

export async function getAllSongs(): Promise<Song[]> {
  const { data, error } = await supabase
    .from('songs')
    .select('id, title, artist, year, billboard_rank, genre')
    .order('year', { ascending: false })
    .order('billboard_rank')

  if (error) return []
  return data || []
}

export interface Concept {
  id: string
  song_id: string
  concept_summary: string
  themes: string[]
  imagery: string[]
  tone: string
  universal_scenarios: string[]
  alternative_titles: string[]
  thematic_vocabulary: string[]
  section_breakdown: string[]
}

export interface ConceptWithSong extends Concept {
  songs: Song
}

export async function getRandomConcept(): Promise<ConceptWithSong | null> {
  const { data, error } = await supabase
    .from('song_analysis')
    .select(`
      id,
      song_id,
      concept_summary,
      themes,
      imagery,
      tone,
      universal_scenarios,
      alternative_titles,
      thematic_vocabulary,
      section_breakdown,
      songs (
        id,
        title,
        artist,
        year,
        billboard_rank,
        genre
      )
    `)

  if (error || !data || data.length === 0) {
    console.error('Error fetching concepts:', error)
    return null
  }
  
  // Pick random concept
  const randomIndex = Math.floor(Math.random() * data.length)
  return data[randomIndex] as any
}

export async function generateCustomConcept(
  userIdea: string,
  numSongs: number = 10,
  filters: {
    years?: number[]
    minRank?: number
    maxRank?: number
    genres?: string[]
    artists?: string[]
  } = {},
  manualSongIds?: string[]
): Promise<Concept | null> {
  try {
    const response = await fetch('http://localhost:3001/api/generate-custom-concept', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_idea: userIdea,
        num_songs: numSongs,
        filters,
        manual_song_ids: manualSongIds
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate custom concept')
    }
    
    const concept = await response.json()
    return concept
  } catch (error) {
    console.error('Error generating custom concept:', error)
    return null
  }
}

// ============================================================================
// DEPTH-BASED RHYME NETWORK SEARCH
// ============================================================================

export interface RhymeConnection {
  fromWord: string
  toWord: string
  rhymeType: string
  song: Song
  fromLine: number
  toLine: number
  path: string[] // Full path from search word to this word
}

export interface DepthLayer {
  depth: number
  wordsDiscovered: string[]  // New words found at this depth
  connections: RhymeConnection[]  // All rhyme pairs that taught us these words
}

export interface RhymeNetworkResult {
  searchWord: string
  totalWords: number
  totalConnections: number
  maxDepth: number
  layers: DepthLayer[]
}

// ============================================================================
// MULTI-LEVEL SORTING SYSTEM
// ============================================================================

export type SortField = 'depth' | 'rhyme_type' | 'frequency' | 'alphabetical'
export type SortDirection = 'asc' | 'desc'

export interface SortCriterion {
  id: string
  field: SortField
  direction: SortDirection
  label: string
}

export interface SortableRhymeResult {
  word: string
  depth: number
  rhymeType: string
  frequency: number  // How many times this word appears across all results
  connections: RhymeConnection[]
}

const RHYME_TYPE_PRIORITY: { [key: string]: number } = {
  'perfect': 1,
  'multi': 2,
  'compound': 3,
  'assonance': 4,
  'consonance': 5,
  'slant': 6,
  'embedded': 7
}

/**
 * Apply multi-level sorting to rhyme results.
 * Sorts are applied in order of the sortOrder array (first = highest priority).
 */
export function applySorting(
  results: SortableRhymeResult[],
  sortOrder: SortCriterion[]
): SortableRhymeResult[] {
  if (sortOrder.length === 0) return results
  
  return [...results].sort((a, b) => {
    // Apply each sort criterion in order until we find a difference
    for (const criterion of sortOrder) {
      let comparison = 0
      
      switch (criterion.field) {
        case 'depth':
          comparison = a.depth - b.depth
          break
          
        case 'rhyme_type':
          const aPriority = RHYME_TYPE_PRIORITY[a.rhymeType] || 99
          const bPriority = RHYME_TYPE_PRIORITY[b.rhymeType] || 99
          comparison = aPriority - bPriority
          break
          
        case 'frequency':
          comparison = a.frequency - b.frequency
          break
          
        case 'alphabetical':
          comparison = a.word.localeCompare(b.word)
          break
      }
      
      // If this criterion found a difference, apply direction and return
      if (comparison !== 0) {
        return criterion.direction === 'asc' ? comparison : -comparison
      }
    }
    
    // All criteria were equal
    return 0
  })
}

/**
 * Transform network result into sortable format with frequency counts.
 */
export function prepareResultsForSorting(
  networkResult: RhymeNetworkResult
): SortableRhymeResult[] {
  const wordMap = new Map<string, SortableRhymeResult>()
  
  // Process each depth layer
  for (const layer of networkResult.layers) {
    for (const connection of layer.connections) {
      const word = connection.toWord
      
      if (!wordMap.has(word)) {
        wordMap.set(word, {
          word,
          depth: layer.depth,
          rhymeType: connection.rhymeType,
          frequency: 0,
          connections: []
        })
      }
      
      const result = wordMap.get(word)!
      
      // Only add this connection if we haven't seen this song yet for this word
      const songAlreadyAdded = result.connections.some(c => c.song.id === connection.song.id)
      if (!songAlreadyAdded) {
        result.connections.push(connection)
      }
      
      result.frequency++
      
      // Use the best (lowest priority number) rhyme type if multiple
      const currentPriority = RHYME_TYPE_PRIORITY[result.rhymeType] || 99
      const newPriority = RHYME_TYPE_PRIORITY[connection.rhymeType] || 99
      if (newPriority < currentPriority) {
        result.rhymeType = connection.rhymeType
      }
    }
  }
  
  return Array.from(wordMap.values())
}

/**
 * Depth-based rhyme network search with comprehensive filtering.
 * 
 * Searches across ALL songs in database to build a network of rhyming words.
 * 
 * Depth 0: Search word itself (e.g. "phone")
 * Depth 1: All words that rhyme with "phone" (tone, alone, go, bone)
 * Depth 2: All words that rhyme with depth-1 words (know rhymes with "go", stone rhymes with "tone")
 * Depth 3: All words that rhyme with depth-2 words
 * 
 * Example cross-song learning:
 *   Song A: phone ↔ go
 *   Song B: go ↔ flow
 *   Result: phone → go → flow (depths 0 → 1 → 2)
 */
export async function searchRhymeNetworkByDepth(
  searchWord: string,
  maxDepth: number = 3,
  filters: RhymeNetworkFilters = {}
): Promise<RhymeNetworkResult> {
  const normalizedSearch = searchWord.toLowerCase().trim()
  
  const result: RhymeNetworkResult = {
    searchWord: normalizedSearch,
    totalWords: 0,
    totalConnections: 0,
    maxDepth: 0,
    layers: []
  }
  
  // Track all words we've discovered (starts with search term)
  const allDiscoveredWords = new Set<string>([normalizedSearch])
  
  // Track the path to each word (search word has path of just itself)
  const wordPaths = new Map<string, string[]>([[normalizedSearch, [normalizedSearch]]])
  
  // Words to search in current depth (starts with search term)
  let currentDepthWords = new Set<string>([normalizedSearch])
  
  // Build each depth layer
  for (let depth = 1; depth <= maxDepth; depth++) {
    if (currentDepthWords.size === 0) break
    
    console.log(`Searching depth ${depth} with words:`, Array.from(currentDepthWords))
    
    // Build query with filters
    let query = supabase
      .from('rhyme_pairs')
      .select(`
        id,
        song_id,
        word,
        rhymes_with,
        rhyme_type,
        word_line,
        rhymes_with_line,
        songs!inner (
          id,
          title,
          artist,
          year,
          billboard_rank,
          genre
        )
      `)
      .or(
        [
          ...Array.from(currentDepthWords).map(w => `word.ilike.${w}`),
          ...Array.from(currentDepthWords).map(w => `rhymes_with.ilike.${w}`)
        ].join(',')
      )
    
    // Apply filters
    if (filters.rhymeTypes && filters.rhymeTypes.length > 0) {
      query = query.in('rhyme_type', filters.rhymeTypes)
    }
    
    if (filters.genres && filters.genres.length > 0) {
      query = query.in('songs.genre', filters.genres)
    }
    
    if (filters.years && filters.years.length > 0) {
      query = query.in('songs.year', filters.years)
    }
    
    if (filters.minRank !== undefined) {
      query = query.gte('songs.billboard_rank', filters.minRank)
    }
    
    if (filters.maxRank !== undefined) {
      query = query.lte('songs.billboard_rank', filters.maxRank)
    }
    
    if (filters.artists && filters.artists.length > 0) {
      query = query.in('songs.artist', filters.artists)
    }
    
    const { data: pairs, error } = await query
    
    if (error) {
      console.error(`Depth ${depth} search error:`, error)
      break
    }
    
    if (!pairs || pairs.length === 0) {
      console.log(`No pairs found at depth ${depth}`)
      break
    }
    
    console.log(`Found ${pairs.length} pairs at depth ${depth}`)
    
    const layer: DepthLayer = {
      depth,
      wordsDiscovered: [],
      connections: []
    }
    
    const newWords = new Set<string>()
    
    // Process each pair
    for (const pair of pairs) {
      const pairWord = pair.word.toLowerCase()
      const pairRhymesWith = pair.rhymes_with.toLowerCase()
      
      // Determine which word is from current depth and which is new
      let fromWord: string
      let toWord: string
      let fromLine: number
      let toLine: number
      
      if (currentDepthWords.has(pairWord)) {
        fromWord = pairWord
        toWord = pairRhymesWith
        fromLine = pair.word_line
        toLine = pair.rhymes_with_line
      } else if (currentDepthWords.has(pairRhymesWith)) {
        fromWord = pairRhymesWith
        toWord = pairWord
        fromLine = pair.rhymes_with_line
        toLine = pair.word_line
      } else {
        // Neither word is in current depth (shouldn't happen with our query)
        continue
      }
      
      // Build the path for this connection
      const fromPath = wordPaths.get(fromWord) || [normalizedSearch, fromWord]
      const fullPath = [...fromPath, toWord]
      
      // Add connection with full path
      layer.connections.push({
        fromWord,
        toWord,
        rhymeType: pair.rhyme_type,
        song: pair.songs as any,
        fromLine,
        toLine,
        path: fullPath
      })
      
      // Track new word if we haven't seen it before
      if (!allDiscoveredWords.has(toWord)) {
        newWords.add(toWord)
        allDiscoveredWords.add(toWord)
        // Store the path to this new word
        wordPaths.set(toWord, fullPath)
      }
    }
    
    // Convert new words to array and sort
    layer.wordsDiscovered = Array.from(newWords).sort()
    
    console.log(`Depth ${depth}: Found ${layer.wordsDiscovered.length} new words, ${layer.connections.length} connections`)
    
    // Add layer if we found anything
    if (layer.wordsDiscovered.length > 0 || layer.connections.length > 0) {
      result.layers.push(layer)
      result.totalWords += layer.wordsDiscovered.length
      result.totalConnections += layer.connections.length
      result.maxDepth = depth
    }
    
    // If no new words, we're done
    if (newWords.size === 0) {
      console.log(`No new words at depth ${depth}, stopping`)
      break
    }
    
    // Next depth searches for the new words we just found
    currentDepthWords = newWords
  }
  
  return result
}

/**
 * Get song lyrics by song ID
 */
export async function getSongLyrics(songId: string): Promise<string | null> {
  const { data, error } = await supabase
    .from('songs')
    .select('lyrics_raw')
    .eq('id', songId)
    .single()
  
  if (error || !data) return null
  return data.lyrics_raw
}
