import { useState, useEffect } from 'react'
import { API_URL } from './config'
import { 
  searchRhymes,
  searchRhymeNetworkByDepth,
  prepareResultsForSorting,
  applySorting,
  getSongStats, 
  getDistinctGenres, 
  getDistinctYears,
  getRandomConcept,
  generateCustomConcept,
  getSongLyrics,
  supabase,
  type SimpleRhymeResult,
  type ConceptWithSong,
  type Concept,
  type RhymeNetworkFilters as RhymeNetworkFiltersType,
  type SortCriterion,
  type SortableRhymeResult,
  type RhymeNetworkResult
} from './lib/supabase'
import { SortBuilder } from './components/SortBuilder'
import { FilterSidebar } from './components/FilterSidebar'
import './App.css'

type Page = 'rhymes' | 'figurative' | 'concepts' | 'nextline' | 'realtalk' | 'melody'
type SearchMode = 'simple' | 'network'

// Keyword constants for figurative language
const SIMILE_KEYWORDS = ['like', 'as', 'than']
const METAPHOR_KEYWORDS = ['is a', 'is the', 'was a', 'are the', 'am a']

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('rhymes')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [searchMode, setSearchMode] = useState<SearchMode>('simple')
  const [filterSidebarOpen, setFilterSidebarOpen] = useState(false)
  
  // Search state
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({ songs: 0, lines: 0 })
  const [searched, setSearched] = useState(false)
  
  // Simple search state
  const [unfilteredSimpleResults, setUnfilteredSimpleResults] = useState<SimpleRhymeResult[]>([])
  const [simpleResults, setSimpleResults] = useState<SimpleRhymeResult[]>([])
  const [onePerSong, setOnePerSong] = useState(true)
  
  // Network search state
  const [networkResult, setNetworkResult] = useState<RhymeNetworkResult | null>(null)
  const [unfilteredResults, setUnfilteredResults] = useState<SortableRhymeResult[]>([])
  const [sortedResults, setSortedResults] = useState<SortableRhymeResult[]>([])
  const [sortOrder, setSortOrder] = useState<SortCriterion[]>([])
  const [maxDepth, setMaxDepth] = useState(3)
  const [expandedWords, setExpandedWords] = useState<Set<string>>(new Set())
  
  // Unified filters for both modes
  const [filters, setFilters] = useState<RhymeNetworkFiltersType>({})
  
  // Concepts page state
  const [concept, setConcept] = useState<ConceptWithSong | null>(null)
  const [titles, setTitles] = useState<string[]>([])
  const [conceptLoading, setConceptLoading] = useState(false)
  const [generatingTitles, setGeneratingTitles] = useState(false)
  const [referenceSongs, setReferenceSongs] = useState<string[]>([])
  const [conceptMode, setConceptMode] = useState<'random' | 'custom'>('random')
  const [customIdea, setCustomIdea] = useState('')
  const [conceptFilters, setConceptFilters] = useState({
    numSongs: 10,
    years: [] as number[],
    minRank: undefined as number | undefined,
    maxRank: undefined as number | undefined,
    genres: [] as string[],
    artists: [] as string[]
  })
  const [matchedSongs, setMatchedSongs] = useState<Array<{id: string, title: string, artist: string, rank: number | null, themes: string[], matchScore?: number, imagery?: string[], tone?: string, universal_scenarios?: string[]}>>([])
  const [extractedThemes, setExtractedThemes] = useState<string[]>([])
  const [viewingSongDetails, setViewingSongDetails] = useState<string | null>(null)
  const [songSearchQuery, setSongSearchQuery] = useState('')
  const [songSearchResults, setSongSearchResults] = useState<Array<{id: string, title: string, artist: string}>>([])
  const [showingSongMatches, setShowingSongMatches] = useState(false)
  
  // Next Line state
  const [nextLineConcept, setNextLineConcept] = useState('')
  const [existingLyrics, setExistingLyrics] = useState('')
  const [exampleLine, setExampleLine] = useState('')
  const [rhymeTarget, setRhymeTarget] = useState('')
  const [rhymePosition, setRhymePosition] = useState<'end' | 'internal'>('end')
  const [rhymeTypeFilter, setRhymeTypeFilter] = useState<string>('any')
  const [lineMeaning, setLineMeaning] = useState('')
  const [specificRhymeWord, setSpecificRhymeWord] = useState('')
  const [partialLine, setPartialLine] = useState('')
  const [lineType, setLineType] = useState<'regular' | 'metaphor' | 'simile'>('regular')
  const [wordsToAvoid, setWordsToAvoid] = useState('')
  const [nextLineMatchedSongs, setNextLineMatchedSongs] = useState<Array<{id: string, title: string, artist: string, rank: number | null, themes?: string[], matchScore?: number, imagery?: string[], tone?: string, universal_scenarios?: string[]}>>([])
  const [nextLineExtractedThemes, setNextLineExtractedThemes] = useState<string[]>([])
  const [viewingNextLineSongDetails, setViewingNextLineSongDetails] = useState<string | null>(null)
  const [showingNextLineSongs, setShowingNextLineSongs] = useState(false)
  const [nextLineSuggestions, setNextLineSuggestions] = useState<Array<{line: string, syllables: number, diff: number}>>([])

  const [generatingNextLine, setGeneratingNextLine] = useState(false)
  const [nextLineFilters, setNextLineFilters] = useState({
    numSongs: 10,
    years: [] as number[],
    minRank: undefined as number | undefined,
    maxRank: undefined as number | undefined,
    genres: [] as string[],
    artists: [] as string[]
  })

  // Figurative Language Finder state
  const [figurativeKeywords, setFigurativeKeywords] = useState<string[]>([...SIMILE_KEYWORDS, ...METAPHOR_KEYWORDS])
  const [figurativeAllSimiles, setFigurativeAllSimiles] = useState(true) // Track if "All Similes" mode is on
  const [figurativeAllMetaphors, setFigurativeAllMetaphors] = useState(true) // Track if "All Metaphors" mode is on
  const [figurativeResults, setFigurativeResults] = useState<Array<{
    songId: string,
    songTitle: string,
    artist: string,
    line: string,
    lineNumber: number,
    context: string[],
    keyword: string
  }>>([])
  const [figurativeSearching, setFigurativeSearching] = useState(false)
  const [figurativeCustomKeyword, setFigurativeCustomKeyword] = useState('')
  const [figurativeGenerating, setFigurativeGenerating] = useState(false)
  const [figurativeMeaning, setFigurativeMeaning] = useState('')
  const [figurativeDesiredMeaning, setFigurativeDesiredMeaning] = useState('')
  const [figurativeFilteringByMeaning, setFigurativeFilteringByMeaning] = useState(false)
  const [figurativeResultLimit, setFigurativeResultLimit] = useState(100) // Max results to send to Claude
  const [figurativeSortOrder, setFigurativeSortOrder] = useState<Array<{id: string, field: string, direction: 'asc' | 'desc', label: string}>>([])
  const [figurativePreviewResults, setFigurativePreviewResults] = useState<Array<{songId: string, songTitle: string, artist: string, line: string, lineNumber: number, context: string[], keyword: string}>>([])
  const [figurativePreviewing, setFigurativePreviewing] = useState(false)
  const [figurativeFilters, setFigurativeFilters] = useState({
    years: [] as number[],
    minRank: undefined as number | undefined,
    maxRank: undefined as number | undefined,
    genres: [] as string[],
    artists: [] as string[]
  })
  
  // Lyrics modal
  const [showLyricsModal, setShowLyricsModal] = useState(false)
  const [modalLyrics, setModalLyrics] = useState('')
  const [modalSongTitle, setModalSongTitle] = useState('')
  const [modalHighlightWords, setModalHighlightWords] = useState<string[]>([])
  const [modalViewMode, setModalViewMode] = useState<'context' | 'full'>('full')

  // Real Talk state
  type RealTalkTab = 'browse' | 'manage'
  const [rtTab, setRtTab] = useState<RealTalkTab>('browse')
  const [rtSources, setRtSources] = useState<Array<{
    id: string,
    source_type: string,
    source_identifier: string,
    display_name: string,
    is_active: boolean,
    last_scraped_at: string | null,
    total_entries: number,
    created_at: string
  }>>([])
  const [rtNewSubreddit, setRtNewSubreddit] = useState('')
  const [rtNewYoutubeUrl, setRtNewYoutubeUrl] = useState('')
  const [rtScraping, setRtScraping] = useState<string | null>(null) // source_id being scraped
  const [rtScrapingAll, setRtScrapingAll] = useState(false)
  const [rtAddingSource, setRtAddingSource] = useState(false)
  const [rtAddingYoutube, setRtAddingYoutube] = useState(false)
  const [rtNewChannelUrl, setRtNewChannelUrl] = useState('')
  const [rtChannelLimit, setRtChannelLimit] = useState(50)
  const [rtScrapingChannel, setRtScrapingChannel] = useState(false)
  
  // Real Talk tags
  const [rtSituationTags, setRtSituationTags] = useState<Array<{id: string, tag_name: string, usage_count: number}>>([])
  const [rtEmotionTags, setRtEmotionTags] = useState<Array<{id: string, tag_name: string, usage_count: number}>>([])
  const [rtNewSituationTag, setRtNewSituationTag] = useState('')
  const [rtNewEmotionTag, setRtNewEmotionTag] = useState('')
  
  // Real Talk entries
  const [rtEntries, setRtEntries] = useState<Array<{
    id: string,
    title: string,
    raw_text: string,
    url: string,
    posted_at: string,
    poster_age: number | null,
    poster_gender: string | null,
    other_party_age: number | null,
    other_party_gender: string | null,
    situation_tags: string[],
    emotional_tags: string[],
    real_talk_sources?: { display_name: string, source_identifier: string },
    relevance_score?: number,
    relevance_reason?: string
  }>>([])
  const [rtLoading, setRtLoading] = useState(false)
  const [rtExpandedEntry, setRtExpandedEntry] = useState<string | null>(null)
  
  // Real Talk filters
  const [rtFilters, setRtFilters] = useState({
    search: '',
    situations: [] as string[],
    emotions: [] as string[],
    ageMin: undefined as number | undefined,
    ageMax: undefined as number | undefined,
    gender: '' as string,
    year: '' as string,
    sourceId: '' as string
  })
  const [rtSortOrder, setRtSortOrder] = useState<Array<{id: string, field: string, direction: 'asc' | 'desc', label: string}>>([])
  
  // Real Talk AI search
  const [rtAiQuery, setRtAiQuery] = useState('')
  const [rtAiSearching, setRtAiSearching] = useState(false)
  const [rtAiLimit, setRtAiLimit] = useState(50)

  // Melody state
  const [melodyChords, setMelodyChords] = useState('')
  const [melodyBpm, setMelodyBpm] = useState(120)
  const [melodyBpmTolerance, setMelodyBpmTolerance] = useState(15)
  const [melodyTimeSig, setMelodyTimeSig] = useState('4/4')
  const [melodyYearStart, setMelodyYearStart] = useState(2010)
  const [melodyYearEnd, setMelodyYearEnd] = useState(2024)
  const [melodyGenres, setMelodyGenres] = useState<string[]>([])
  const [melodyChart, setMelodyChart] = useState('')
  const [melodyArtistStyle, setMelodyArtistStyle] = useState('')
  const [melodySearching, setMelodySearching] = useState(false)
  const [melodyResults, setMelodyResults] = useState<any[]>([])
  const [melodyTidalAuth, setMelodyTidalAuth] = useState(false)
  const [melodySelectedTracks, setMelodySelectedTracks] = useState<Set<string>>(new Set())
  const [melodyCreatingPlaylist, setMelodyCreatingPlaylist] = useState(false)
  const [melodyPlaylistName, setMelodyPlaylistName] = useState('')

  useEffect(() => {
    getSongStats().then(setStats)
  }, [])

  // Apply filters client-side for Simple search
  const applySimpleFilters = (results: SimpleRhymeResult[]): SimpleRhymeResult[] => {
    let filtered = [...results]
    
    // Genre filter
    if (filters.genres && filters.genres.length > 0) {
      filtered = filtered.filter(r => filters.genres!.includes(r.song.genre || ''))
    }
    
    // Year filter
    if (filters.years && filters.years.length > 0) {
      filtered = filtered.filter(r => filters.years!.includes(r.song.year || 0))
    }
    
    // Billboard rank filter
    if (filters.minRank !== undefined) {
      filtered = filtered.filter(r => (r.song.billboard_rank || 999) >= filters.minRank!)
    }
    if (filters.maxRank !== undefined) {
      filtered = filtered.filter(r => (r.song.billboard_rank || 999) <= filters.maxRank!)
    }
    
    return filtered
  }

  // Apply filters client-side for Network search
  const applyNetworkFilters = (results: SortableRhymeResult[]): SortableRhymeResult[] => {
    let filtered = [...results]
    
    // Depth filter
    if (filters.depths && filters.depths.length > 0) {
      filtered = filtered.filter(r => filters.depths!.includes(r.depth))
    }
    
    // Rhyme type filter
    if (filters.rhymeTypes && filters.rhymeTypes.length > 0) {
      filtered = filtered.filter(r => filters.rhymeTypes!.includes(r.rhymeType))
    }
    
    // Genre filter
    if (filters.genres && filters.genres.length > 0) {
      filtered = filtered.filter(r => 
        r.connections.some(c => filters.genres!.includes(c.song.genre || ''))
      )
    }
    
    // Year filter
    if (filters.years && filters.years.length > 0) {
      filtered = filtered.filter(r =>
        r.connections.some(c => filters.years!.includes(c.song.year || 0))
      )
    }
    
    // Billboard rank filter
    if (filters.minRank !== undefined || filters.maxRank !== undefined) {
      filtered = filtered.filter(r =>
        r.connections.some(c => {
          const rank = c.song.billboard_rank || 999
          const minOk = filters.minRank === undefined || rank >= filters.minRank
          const maxOk = filters.maxRank === undefined || rank <= filters.maxRank
          return minOk && maxOk
        })
      )
    }
    
    return filtered
  }

  // Re-sort network results when sort order changes
  // Re-run Simple search when onePerSong changes
  useEffect(() => {
    if (searched && query.trim() && searchMode === 'simple') {
      const runSearch = async () => {
        setLoading(true)
        try {
          const showAll = !onePerSong // Invert: checked = 1 per song, unchecked = all
          const data = await searchRhymes(query.trim(), {}, showAll)
          setUnfilteredSimpleResults(data)
          const filtered = applySimpleFilters(data)
          setSimpleResults(filtered)
        } catch (err) {
          console.error('Search failed:', err)
        } finally {
          setLoading(false)
        }
      }
      runSearch()
    }
  }, [onePerSong])

  // Re-process Simple search results when filters change (client-side, fast!)
  useEffect(() => {
    if (unfilteredSimpleResults.length > 0 && searchMode === 'simple') {
      const filtered = applySimpleFilters(unfilteredSimpleResults)
      setSimpleResults(filtered)
    }
  }, [filters, unfilteredSimpleResults, searchMode])

  // Re-process Network results when filters or sort order change (client-side, fast!)
  useEffect(() => {
    if (unfilteredResults.length > 0 && searchMode === 'network') {
      const filtered = applyNetworkFilters(unfilteredResults)
      const sorted = sortOrder.length > 0 ? applySorting(filtered, sortOrder) : filtered
      setSortedResults(sorted)
    }
  }, [filters, sortOrder, unfilteredResults, searchMode])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setSearched(true)
    
    try {
      if (searchMode === 'simple') {
        // Simple search - fetch all, filter client-side
        const showAll = !onePerSong // Invert: checked = 1 per song, unchecked = all
        const data = await searchRhymes(query.trim(), {}, showAll)
        setUnfilteredSimpleResults(data)
        
        // Apply filters client-side
        const filtered = applySimpleFilters(data)
        setSimpleResults(filtered)
        setNetworkResult(null)
        setUnfilteredResults([])
      } else {
        // Network search - depth-based (no filters in query - we filter client-side!)
        const result = await searchRhymeNetworkByDepth(query.trim(), maxDepth, {})
        setNetworkResult(result)
        
        // Store unfiltered results
        const sortable = prepareResultsForSorting(result)
        setUnfilteredResults(sortable)
        
        // Apply filters and sorting client-side
        const filtered = applyFilters(sortable)
        const sorted = sortOrder.length > 0 ? applySorting(filtered, sortOrder) : filtered
        setSortedResults(sorted)
        setSimpleResults([])
      }
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleViewLyrics = async (songId: string, title: string, artist: string, highlightWords?: string[]) => {
    const lyrics = await getSongLyrics(songId)
    if (lyrics) {
      setModalLyrics(lyrics)
      setModalSongTitle(`${title} - ${artist}`)
      setModalHighlightWords(highlightWords || [])
      setModalViewMode(highlightWords && highlightWords.length > 0 ? 'context' : 'full')
      setShowLyricsModal(true)
    }
  }
  
  const getContextView = (lyrics: string, searchWords: string[]) => {
    const lines = lyrics.split('\n')
    const contexts: Array<{linesBefore: string[], matchLine: string, linesAfter: string[], lineNumber: number}> = []
    
    // Find all lines containing any of the search words
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      if (!trimmedLine) return
      
      // Check if line contains any of the search words
      const hasMatch = searchWords.some(word => 
        trimmedLine.toLowerCase().includes(word.toLowerCase())
      )
      
      if (hasMatch) {
        // Get 4 non-empty lines before and after
        const linesBefore: string[] = []
        const linesAfter: string[] = []
        
        let beforeIndex = index - 1
        while (linesBefore.length < 4 && beforeIndex >= 0) {
          const beforeLine = lines[beforeIndex].trim()
          if (beforeLine) linesBefore.unshift(beforeLine)
          beforeIndex--
        }
        
        let afterIndex = index + 1
        while (linesAfter.length < 4 && afterIndex < lines.length) {
          const afterLine = lines[afterIndex].trim()
          if (afterLine) linesAfter.push(afterLine)
          afterIndex++
        }
        
        contexts.push({
          linesBefore,
          matchLine: trimmedLine,
          linesAfter,
          lineNumber: index + 1
        })
      }
    })
    
    return contexts
  }
  
  const toggleExpanded = (word: string) => {
    setExpandedWords(prev => {
      const newSet = new Set(prev)
      if (newSet.has(word)) {
        newSet.delete(word)
      } else {
        newSet.add(word)
      }
      return newSet
    })
  }

  const activeFilterCount = 
    (filters.rhymeTypes?.length || 0) +
    (filters.genres?.length || 0) +
    (filters.years?.length || 0) +
    (filters.depths?.length || 0)

  const handleGenerateConcept = async () => {
    if (conceptMode === 'random') {
      setConceptLoading(true)
      try {
      const randomConcept = await getRandomConcept()
      if (randomConcept) {
        setConcept(randomConcept)
        setTitles(randomConcept.alternative_titles || [])
        // For random concepts, use the source song as reference
        if (randomConcept.songs) {
          setReferenceSongs([`${randomConcept.songs.title} - ${randomConcept.songs.artist}`])
        }
      }
      } catch (err) {
        console.error('Failed to generate concept:', err)
      } finally {
        setConceptLoading(false)
      }
    } else {
      // Custom concept generation
      if (!customIdea.trim()) {
        alert('Please enter your concept idea')
        return
      }
      setConceptLoading(true)
      try {
        const customConcept = await generateCustomConcept(
          customIdea,
          conceptFilters.numSongs,
          {
            years: conceptFilters.years.length > 0 ? conceptFilters.years : undefined,
            minRank: conceptFilters.minRank,
            maxRank: conceptFilters.maxRank,
            genres: conceptFilters.genres.length > 0 ? conceptFilters.genres : undefined,
            artists: conceptFilters.artists.length > 0 ? conceptFilters.artists : undefined
          },
          matchedSongs.length > 0 ? matchedSongs.map(s => s.id) : undefined
        )
        
        if (customConcept) {
          // Convert to ConceptWithSong format for display
          const conceptWithSong: ConceptWithSong = {
            ...customConcept,
            id: 'custom',
            song_id: 'custom',
            songs: {
              id: 'custom',
              title: 'Custom Concept',
              artist: 'Generated',
              year: new Date().getFullYear(),
              billboard_rank: null,
              genre: null
            }
          }
          setConcept(conceptWithSong)
          setTitles(customConcept.alternative_titles || [])
          
          // Store reference songs for generating more titles later
          if (customConcept._meta && customConcept._meta.example_songs) {
            setReferenceSongs(customConcept._meta.example_songs)
          }
        } else {
          alert('Failed to generate concept. Please try again.')
        }
      } catch (err) {
        console.error('Failed to generate custom concept:', err)
        alert('Error generating concept. Please check console for details.')
      } finally {
        setConceptLoading(false)
      }
    }
  }

  // Calculate estimated time for concept generation
  const getEstimatedTime = () => {
    if (conceptMode === 'random') return 1
    const numSongs = matchedSongs.length > 0 ? matchedSongs.length : conceptFilters.numSongs
    return 8 + (numSongs * 0.5)
  }

  // Find matching songs based on theme and filters
  const handleFindMatchingSongs = async () => {
    if (!customIdea.trim()) {
      alert('Please enter your concept idea first')
      return
    }

    setConceptLoading(true)
    try {
      // Call backend to extract themes and find matches
      const response = await fetch(`${API_URL}/api/find-matching-songs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_idea: customIdea,
          num_songs: conceptFilters.numSongs,
          filters: {
            years: conceptFilters.years.length > 0 ? conceptFilters.years : undefined,
            minRank: conceptFilters.minRank,
            maxRank: conceptFilters.maxRank,
            genres: conceptFilters.genres.length > 0 ? conceptFilters.genres : undefined,
            artists: conceptFilters.artists.length > 0 ? conceptFilters.artists : undefined
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Concepts - Received data:', data)
        setMatchedSongs(data.songs || [])
        setExtractedThemes(data.extracted_themes || [])
        setShowingSongMatches(true)
      } else {
        const errorText = await response.text()
        console.error('Server error response:', errorText)
        alert(`Failed to find matching songs: ${response.status}`)
      }
    } catch (err) {
      console.error('Error finding matching songs:', err)
      alert(`Error finding songs: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setConceptLoading(false)
    }
  }

  // Search for songs to add manually
  const handleSearchSongs = async (query: string) => {
    if (!query.trim()) {
      setSongSearchResults([])
      return
    }

    try {
      const { data } = await supabase
        .from('songs')
        .select('id, title, artist')
        .or(`title.ilike.%${query}%,artist.ilike.%${query}%`)
        .limit(10)
        .execute()

      setSongSearchResults(data || [])
    } catch (err) {
      console.error('Error searching songs:', err)
    }
  }

  // Add a song to the matched songs list
  const handleAddSong = async (songId: string) => {
    try {
      const { data } = await supabase
        .from('song_analysis')
        .select('song_id, themes, songs(id, title, artist, billboard_rank)')
        .eq('song_id', songId)
        .single()
        .execute()

      if (data && data.songs) {
        const newSong = {
          id: data.songs.id,
          title: data.songs.title,
          artist: data.songs.artist,
          rank: data.songs.billboard_rank,
          themes: data.themes || []
        }
        setMatchedSongs([...matchedSongs, newSong])
        setSongSearchQuery('')
        setSongSearchResults([])
      }
    } catch (err) {
      console.error('Error adding song:', err)
    }
  }

  // Remove a song from the matched songs list
  const handleRemoveSong = (songId: string) => {
    setMatchedSongs(matchedSongs.filter(s => s.id !== songId))
  }

  // Count syllables in a line
  const countSyllables = (text: string): number => {
    if (!text) return 0
    text = text.toLowerCase().trim()
    text = text.replace(/[^a-z\s]/g, '')
    const words = text.split(/\s+/).filter(w => w.length > 0)
    
    let syllables = 0
    words.forEach(word => {
      // Simple syllable counting (vowel groups)
      const vowelGroups = word.match(/[aeiouy]+/g)
      syllables += vowelGroups ? vowelGroups.length : 1
      // Adjust for silent e
      if (word.endsWith('e') && word.length > 2) syllables--
      if (syllables === 0) syllables = 1
    })
    
    return syllables
  }

  // Find matching songs for next line
  const handleFindNextLineSongs = async () => {
    if (!nextLineConcept.trim()) {
      alert('Please enter your song concept')
      return
    }

    setGeneratingNextLine(true)
    try {
      // Combine concept and lyrics for better context
      const combinedContext = existingLyrics.trim() 
        ? `${nextLineConcept}\n\nLyrics so far:\n${existingLyrics}`
        : nextLineConcept

      const response = await fetch(`${API_URL}/api/find-matching-songs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_idea: combinedContext,
          num_songs: nextLineFilters.numSongs,
          filters: {
            years: nextLineFilters.years.length > 0 ? nextLineFilters.years : undefined,
            minRank: nextLineFilters.minRank,
            maxRank: nextLineFilters.maxRank,
            genres: nextLineFilters.genres.length > 0 ? nextLineFilters.genres : undefined,
            artists: nextLineFilters.artists.length > 0 ? nextLineFilters.artists : undefined
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Next Line - Received data:', data)
        setNextLineMatchedSongs(data.songs || [])
        setNextLineExtractedThemes(data.extracted_themes || [])
        setShowingNextLineSongs(true)
      } else {
        const errorText = await response.text()
        console.error('Server error response:', errorText)
        alert(`Failed to find matching songs: ${response.status}`)
      }
    } catch (err) {
      console.error('Error finding songs:', err)
      alert(`Error finding songs: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setGeneratingNextLine(false)
    }
  }

  // Generate next line suggestions
  const handleGenerateNextLine = async () => {
    if (!nextLineConcept.trim() || !exampleLine.trim()) {
      alert('Please enter concept and example line')
      return
    }

    setGeneratingNextLine(true)
    try {
      const response = await fetch(`${API_URL}/api/generate-next-line`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: nextLineConcept,
          existing_lyrics: existingLyrics,
          syllable_count: countSyllables(exampleLine),
          rhyme_target: rhymeTarget,
          rhyme_position: rhymePosition,
          rhyme_type: rhymeTypeFilter !== 'any' ? rhymeTypeFilter : undefined,
          reference_song_ids: nextLineMatchedSongs.map(s => s.id),
          line_meaning: lineMeaning.trim() || undefined,
          specific_rhyme_word: specificRhymeWord.trim() || undefined,
          partial_line: partialLine.trim() || undefined,
          line_type: lineType,
          words_to_avoid: wordsToAvoid.trim() || undefined
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log(`Got ${data.total_generated} suggestions, ${data.exact_matches} match exactly`)
        setNextLineSuggestions(data.suggestions || [])
      } else {
        alert('Failed to generate suggestions')
      }
    } catch (err) {
      console.error('Error generating next line:', err)
      alert('Error generating suggestions')
    } finally {
      setGeneratingNextLine(false)
    }
  }

  // Use a suggested line
  const handleUseSuggestion = (suggestion: string) => {
    setExistingLyrics(existingLyrics + '\n' + suggestion)
    // Keep suggestions visible so user can continue selecting
  }

  // Generate more variations of a specific line
  const handleMoreLikeThis = async (baseLine: string) => {
    setGeneratingNextLine(true)
    try {
      const response = await fetch(`${API_URL}/api/generate-more-like-this`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_line: baseLine,
          concept: nextLineConcept,
          existing_lyrics: existingLyrics,
          syllable_count: countSyllables(exampleLine),
          rhyme_target: rhymeTarget,
          rhyme_position: rhymePosition,
          rhyme_type: rhymeTypeFilter !== 'any' ? rhymeTypeFilter : undefined,
          reference_song_ids: nextLineMatchedSongs.map(s => s.id),
          line_meaning: lineMeaning.trim() || undefined,
          specific_rhyme_word: specificRhymeWord.trim() || undefined,
          partial_line: partialLine.trim() || undefined,
          line_type: lineType,
          words_to_avoid: wordsToAvoid.trim() || undefined
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log(`Got ${data.total_generated} variations, ${data.exact_matches} match exactly`)
        // Append new variations below existing suggestions
        setNextLineSuggestions(prev => [...prev, ...(data.suggestions || [])])
      } else {
        alert('Failed to generate variations')
      }
    } catch (err) {
      console.error('Error generating variations:', err)
      alert('Error generating variations')
    } finally {
      setGeneratingNextLine(false)
    }
  }

  // Search for figurative language (similes, metaphors)
  const handleFigurativeSearch = async () => {
    if (figurativeKeywords.length === 0) {
      alert('Please select at least one keyword to search for')
      return
    }

    setFigurativeSearching(true)
    setFigurativeResults([])

    try {
      // Build query with filters
        let query = supabase
          .from('songs')
          .select('id, title, artist, lyrics_raw, billboard_rank, genre, year')
        
        // Apply filters at query level for better performance
        if (figurativeFilters.years.length > 0) {
          query = query.in('year', figurativeFilters.years)
        }
      if (figurativeFilters.minRank !== undefined) {
        query = query.lte('billboard_rank', figurativeFilters.minRank)
      }
      if (figurativeFilters.maxRank !== undefined) {
        query = query.gte('billboard_rank', figurativeFilters.maxRank)
      }
      
      // Limit to 500 songs max for performance
      query = query.limit(500)
      
      const { data: songs, error } = await query
      
      if (error) {
        console.error('Database error:', error)
        throw error
      }

      const results: typeof figurativeResults = []
      
        for (const song of songs || []) {
          if (!song.lyrics_raw) continue
        
        // Apply genre and artist filters (can't filter these at query level easily)
        if (figurativeFilters.genres.length > 0) {
          if (!song.genre || !figurativeFilters.genres.some(g => song.genre?.toLowerCase().includes(g.toLowerCase()))) {
            continue
          }
        }
        if (figurativeFilters.artists.length > 0) {
          if (!figurativeFilters.artists.some(a => song.artist?.toLowerCase().includes(a.toLowerCase()))) {
            continue
          }
        }

          const lines = song.lyrics_raw.split('\n')
        
        lines.forEach((line, idx) => {
          const lineLower = line.toLowerCase()
          
          for (const keyword of figurativeKeywords) {
            // Check if keyword exists in line (word boundary for single words)
            const keywordLower = keyword.toLowerCase()
            const hasKeyword = keyword.includes(' ')
              ? lineLower.includes(keywordLower)  // Multi-word: simple contains
              : new RegExp(`\\b${keywordLower}\\b`).test(lineLower)  // Single word: word boundary
            
            if (hasKeyword) {
              // Get context (4 lines before and after, ignoring blank lines)
              const contextLines: string[] = []
              let beforeCount = 0
              for (let i = idx - 1; i >= 0 && beforeCount < 4; i--) {
                if (lines[i].trim()) {
                  contextLines.unshift(lines[i])
                  beforeCount++
                }
              }
              contextLines.push(line)  // The matched line
              let afterCount = 0
              for (let i = idx + 1; i < lines.length && afterCount < 4; i++) {
                if (lines[i].trim()) {
                  contextLines.push(lines[i])
                  afterCount++
                }
              }

              results.push({
                songId: song.id,
                songTitle: song.title,
                artist: song.artist,
                line: line,
                lineNumber: idx + 1,
                context: contextLines,
                keyword: keyword
              })
              break  // Only count once per line even if multiple keywords match
            }
          }
        })
      }

      // Aggressive deduplication: Remove duplicate lines (normalize heavily)
      const seenLines = new Set<string>()
      const deduplicatedResults = results.filter(result => {
        // Normalize: lowercase, remove punctuation, collapse whitespace
        const normalizedLine = result.line
          .toLowerCase()
          .trim()
          .replace(/[.,!?;:()"']/g, '')  // Remove common punctuation
          .replace(/\s+/g, ' ')  // Collapse multiple spaces
        
        if (seenLines.has(normalizedLine)) {
          return false  // Skip duplicate
        }
        seenLines.add(normalizedLine)
        return true
      })

      console.log(`Found ${results.length} total matches, ${deduplicatedResults.length} unique lines after deduplication (${results.length - deduplicatedResults.length} duplicates removed)`)

      setFigurativeResults(deduplicatedResults)
      
      if (deduplicatedResults.length === 0) {
        alert(`No results found for ${figurativeKeywords.map(k => '"' + k + '"').join(', ')}. Try different keywords or remove filters.`)
      }
    } catch (err: any) {
      console.error('Error searching figurative language:', err)
      alert(`Error searching: ${err.message || 'Unknown error'}`)
    } finally {
      setFigurativeSearching(false)
    }
  }

  // Generate variations of a figurative line with a new meaning
  const handleGenerateFigurativeVariations = async (originalLine: string, keyword: string) => {
    if (!figurativeMeaning.trim()) {
      alert('Please enter the meaning you want to convey')
      return
    }

    setFigurativeGenerating(true)

    try {
      const response = await fetch(`${API_URL}/api/generate-figurative-variations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_line: originalLine,
          keyword: keyword,
          desired_meaning: figurativeMeaning
        })
      })

      if (response.ok) {
        const data = await response.json()
        // Display in alert for now, we can make a modal later
        alert('Generated variations:\n\n' + data.variations.join('\n\n'))
      } else {
        alert('Failed to generate variations')
      }
    } catch (err) {
      console.error('Error generating figurative variations:', err)
      alert('Error generating variations')
    } finally {
      setFigurativeGenerating(false)
    }
  }

  // Preview figurative results without sending to Claude
  const handlePreviewFigurativeResults = async () => {
    if (figurativeKeywords.length === 0) {
      alert('Please select at least one keyword to search for')
      return
    }

    setFigurativePreviewing(true)
    setFigurativePreviewResults([])

    try {
      // Step 1: Search for figurative language in the database
      let query = supabase
        .from('songs')
        .select('id, title, artist, lyrics_raw, billboard_rank, genre, year')
      
      // Apply filters at query level for better performance
      if (figurativeFilters.years.length > 0) {
        query = query.in('year', figurativeFilters.years)
      }
      if (figurativeFilters.minRank !== undefined) {
        query = query.lte('billboard_rank', figurativeFilters.minRank)
      }
      if (figurativeFilters.maxRank !== undefined) {
        query = query.gte('billboard_rank', figurativeFilters.maxRank)
      }
      
      // Limit to 500 songs max for performance
      query = query.limit(500)
      
      const { data: songs, error } = await query
      
      if (error) {
        console.error('Database error:', error)
        throw error
      }

      const searchResults: typeof figurativePreviewResults = []
      
      for (const song of songs || []) {
        if (!song.lyrics_raw) continue
        
        // Apply genre and artist filters
        if (figurativeFilters.genres.length > 0) {
          if (!song.genre || !figurativeFilters.genres.some(g => song.genre?.toLowerCase().includes(g.toLowerCase()))) {
            continue
          }
        }
        if (figurativeFilters.artists.length > 0) {
          if (!figurativeFilters.artists.some(a => song.artist?.toLowerCase().includes(a.toLowerCase()))) {
            continue
          }
        }

        const lines = song.lyrics_raw.split('\n')
        
        lines.forEach((line, idx) => {
          const lineLower = line.toLowerCase()
          
          for (const keyword of figurativeKeywords) {
            const keywordLower = keyword.toLowerCase()
            const hasKeyword = keyword.includes(' ')
              ? lineLower.includes(keywordLower)
              : new RegExp(`\\b${keywordLower}\\b`).test(lineLower)
            
            if (hasKeyword) {
              // Get context
              const contextLines: string[] = []
              let beforeCount = 0
              for (let i = idx - 1; i >= 0 && beforeCount < 4; i--) {
                if (lines[i].trim()) {
                  contextLines.unshift(lines[i])
                  beforeCount++
                }
              }
              contextLines.push(line)
              let afterCount = 0
              for (let i = idx + 1; i < lines.length && afterCount < 4; i++) {
                if (lines[i].trim()) {
                  contextLines.push(lines[i])
                  afterCount++
                }
              }

              searchResults.push({
                songId: song.id,
                songTitle: song.title,
                artist: song.artist,
                line: line,
                lineNumber: idx + 1,
                context: contextLines,
                keyword: keyword
              })
              break
            }
          }
        })
      }

      // Deduplication
      const seenLines = new Set<string>()
      const deduplicatedResults = searchResults.filter(result => {
        const normalizedLine = result.line
          .toLowerCase()
          .trim()
          .replace(/[.,!?;:()"']/g, '')
          .replace(/\s+/g, ' ')
        
        if (seenLines.has(normalizedLine)) {
          return false
        }
        seenLines.add(normalizedLine)
        return true
      })

      console.log(`Found ${searchResults.length} total matches, ${deduplicatedResults.length} unique lines after deduplication`)

      if (deduplicatedResults.length === 0) {
        alert(`No results found for ${figurativeKeywords.map(k => '"' + k + '"').join(', ')}. Try different keywords or remove filters.`)
        setFigurativePreviewing(false)
        return
      }

      // Apply sorting
      let sortedResults = [...deduplicatedResults]
      
      if (figurativeSortOrder.length > 0) {
        sortedResults.sort((a, b) => {
          for (const criterion of figurativeSortOrder) {
            let compareValue = 0
            
            if (['like', 'as', 'than', 'is_a', 'is_the', 'was_a', 'are_the', 'am_a'].includes(criterion.field)) {
              const keywordMap: Record<string, string> = {
                'like': 'like',
                'as': 'as',
                'than': 'than',
                'is_a': 'is a',
                'is_the': 'is the',
                'was_a': 'was a',
                'are_the': 'are the',
                'am_a': 'am a'
              }
              const targetKeyword = keywordMap[criterion.field]
              const aMatches = a.keyword === targetKeyword ? 1 : 0
              const bMatches = b.keyword === targetKeyword ? 1 : 0
              compareValue = bMatches - aMatches
            } else {
              switch (criterion.field) {
                case 'chart':
                  compareValue = 0
                  break
                case 'artist':
                  compareValue = a.artist.localeCompare(b.artist)
                  break
                case 'song':
                  compareValue = a.songTitle.localeCompare(b.songTitle)
                  break
                case 'random':
                  compareValue = Math.random() - 0.5
                  break
              }
            }
            
            if (compareValue !== 0) {
              return criterion.direction === 'asc' ? compareValue : -compareValue
            }
          }
          return 0
        })
        console.log(`Sorted ${sortedResults.length} results by: ${figurativeSortOrder.map(s => s.label).join(' → ')}`)
      }

      // Store all sorted results for preview
      setFigurativePreviewResults(sortedResults)
      
    } catch (err) {
      console.error('Error previewing figurative results:', err)
      alert('Error loading results')
    } finally {
      setFigurativePreviewing(false)
    }
  }

  // Search and filter figurative results by meaning using Claude (combined operation)
  const handleFilterByMeaning = async () => {
    if (!figurativeDesiredMeaning.trim()) {
      alert('Please enter what you want the figurative expression to mean')
      return
    }

    setFigurativeFilteringByMeaning(true)
    setFigurativeResults([])

    try {
      let sortedResults: typeof figurativePreviewResults = []
      
      // Use preview results if available, otherwise fetch fresh
      if (figurativePreviewResults.length > 0) {
        sortedResults = figurativePreviewResults
        console.log(`Using ${sortedResults.length} previewed results`)
      } else {
        // Fetch results if not previewed
        if (figurativeKeywords.length === 0) {
          alert('Please select at least one keyword to search for')
          return
        }
        
        // Step 1: Search for figurative language in the database
        // Build query with filters
        let query = supabase
          .from('songs')
          .select('id, title, artist, lyrics_raw, billboard_rank, genre, year')
      
      // Apply filters at query level for better performance
      if (figurativeFilters.years.length > 0) {
        query = query.in('year', figurativeFilters.years)
      }
      if (figurativeFilters.minRank !== undefined) {
        query = query.lte('billboard_rank', figurativeFilters.minRank)
      }
      if (figurativeFilters.maxRank !== undefined) {
        query = query.gte('billboard_rank', figurativeFilters.maxRank)
      }
      
      // Limit to 500 songs max for performance
      query = query.limit(500)
      
      const { data: songs, error } = await query
      
      if (error) {
        console.error('Database error:', error)
        throw error
      }

      const searchResults: typeof figurativeResults = []
      
      for (const song of songs || []) {
        if (!song.lyrics_raw) continue
        
        // Apply genre and artist filters (can't filter these at query level easily)
        if (figurativeFilters.genres.length > 0) {
          if (!song.genre || !figurativeFilters.genres.some(g => song.genre?.toLowerCase().includes(g.toLowerCase()))) {
            continue
          }
        }
        if (figurativeFilters.artists.length > 0) {
          if (!figurativeFilters.artists.some(a => song.artist?.toLowerCase().includes(a.toLowerCase()))) {
            continue
          }
        }

        const lines = song.lyrics_raw.split('\n')
        
        lines.forEach((line, idx) => {
          const lineLower = line.toLowerCase()
          
          for (const keyword of figurativeKeywords) {
            // Check if keyword exists in line (word boundary for single words)
            const keywordLower = keyword.toLowerCase()
            const hasKeyword = keyword.includes(' ')
              ? lineLower.includes(keywordLower)  // Multi-word: simple contains
              : new RegExp(`\\b${keywordLower}\\b`).test(lineLower)  // Single word: word boundary
            
            if (hasKeyword) {
              // Get context (4 lines before and after, ignoring blank lines)
              const contextLines: string[] = []
              let beforeCount = 0
              for (let i = idx - 1; i >= 0 && beforeCount < 4; i--) {
                if (lines[i].trim()) {
                  contextLines.unshift(lines[i])
                  beforeCount++
                }
              }
              contextLines.push(line)  // The matched line
              let afterCount = 0
              for (let i = idx + 1; i < lines.length && afterCount < 4; i++) {
                if (lines[i].trim()) {
                  contextLines.push(lines[i])
                  afterCount++
                }
              }

              searchResults.push({
                songId: song.id,
                songTitle: song.title,
                artist: song.artist,
                line: line,
                lineNumber: idx + 1,
                context: contextLines,
                keyword: keyword
              })
              break  // Only count once per line even if multiple keywords match
            }
          }
        })
      }

      // Aggressive deduplication: Remove duplicate lines (normalize heavily)
      const seenLines = new Set<string>()
      const deduplicatedResults = searchResults.filter(result => {
        // Normalize: lowercase, remove punctuation, collapse whitespace
        const normalizedLine = result.line
          .toLowerCase()
          .trim()
          .replace(/[.,!?;:()"']/g, '')  // Remove common punctuation
          .replace(/\s+/g, ' ')  // Collapse multiple spaces
        
        if (seenLines.has(normalizedLine)) {
          return false  // Skip duplicate
        }
        seenLines.add(normalizedLine)
        return true
      })

      console.log(`Found ${searchResults.length} total matches, ${deduplicatedResults.length} unique lines after deduplication (${searchResults.length - deduplicatedResults.length} duplicates removed)`)

      if (deduplicatedResults.length === 0) {
        alert(`No results found for ${figurativeKeywords.map(k => '"' + k + '"').join(', ')}. Try different keywords or remove filters.`)
        setFigurativeFilteringByMeaning(false)
        return
      }

      // Step 2: Apply sorting before sending to Claude
      let sortedResults = [...deduplicatedResults]
      
      // Apply each sort criterion in priority order
      if (figurativeSortOrder.length > 0) {
        sortedResults.sort((a, b) => {
          for (const criterion of figurativeSortOrder) {
            let compareValue = 0
            
            // Check if this is a keyword-specific sort
            if (['like', 'as', 'than', 'is_a', 'is_the', 'was_a', 'are_the', 'am_a'].includes(criterion.field)) {
              // Convert field name back to keyword
              const keywordMap: Record<string, string> = {
                'like': 'like',
                'as': 'as',
                'than': 'than',
                'is_a': 'is a',
                'is_the': 'is the',
                'was_a': 'was a',
                'are_the': 'are the',
                'am_a': 'am a'
              }
              const targetKeyword = keywordMap[criterion.field]
              // Prioritize results that match this keyword
              const aMatches = a.keyword === targetKeyword ? 1 : 0
              const bMatches = b.keyword === targetKeyword ? 1 : 0
              compareValue = bMatches - aMatches  // Matching ones come first
            } else {
              switch (criterion.field) {
                case 'chart':
                  // We don't have billboard_rank in results, so skip
                  compareValue = 0
                  break
                case 'artist':
                  compareValue = a.artist.localeCompare(b.artist)
                  break
                case 'song':
                  compareValue = a.songTitle.localeCompare(b.songTitle)
                  break
                case 'random':
                  compareValue = Math.random() - 0.5
                  break
              }
            }
            
            if (compareValue !== 0) {
              return criterion.direction === 'asc' ? compareValue : -compareValue
            }
          }
          return 0
        })
        console.log(`Sorted ${sortedResults.length} results by: ${figurativeSortOrder.map(s => s.label).join(' → ')}`)
        }
      }

      // Step 3: Limit results based on user preference
      const resultsToAnalyze = sortedResults.slice(0, figurativeResultLimit)
      
      if (resultsToAnalyze.length < sortedResults.length) {
        console.log(`Limiting to first ${resultsToAnalyze.length} results for Claude analysis (${sortedResults.length - resultsToAnalyze.length} not analyzed due to limit)`)
      }
      
      // Extract just the lines from results
      const lines = resultsToAnalyze.map(r => ({
        line: r.line,
        song: `${r.songTitle} - ${r.artist}`,
        keyword: r.keyword
      }))

      const response = await fetch(`${API_URL}/api/filter-figurative-by-meaning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lines: lines,
          desired_meaning: figurativeDesiredMeaning
        })
      })

      if (response.ok) {
        const data = await response.json()
        // Filter the results to only show the matches Claude selected
        const topMatchLines = new Set(data.matches.map((m: any) => m.line))
        const filteredResults = resultsToAnalyze.filter(r => topMatchLines.has(r.line))
        setFigurativeResults(filteredResults)
        console.log(`Analyzed ${resultsToAnalyze.length} unique lines, Claude selected ${filteredResults.length} that match your desired meaning`)
      } else {
        alert('Failed to filter by meaning')
      }
    } catch (err) {
      console.error('Error filtering by meaning:', err)
      alert('Error filtering by meaning')
    } finally {
      setFigurativeFilteringByMeaning(false)
    }
  }

  // Generate more titles based on the current concept
  const handleGenerateMoreTitles = async () => {
    if (!concept) return

    setGeneratingTitles(true)
    try {
      const response = await fetch(`${API_URL}/api/generate-more-titles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: {
            concept_summary: concept.concept_summary,
            themes: concept.themes,
            imagery: concept.imagery,
            tone: concept.tone
          },
          reference_songs: referenceSongs,
          existing_titles: titles
        })
      })

      if (response.ok) {
        const data = await response.json()
        setTitles([...titles, ...data.titles])
      } else {
        alert('Failed to generate more titles')
      }
    } catch (err) {
      console.error('Error generating more titles:', err)
      alert('Error generating titles. Please try again.')
    } finally {
      setGeneratingTitles(false)
    }
  }

  // ============================================
  // REAL TALK HANDLERS
  // ============================================

  // Load Real Talk sources and tags on page mount
  useEffect(() => {
    if (currentPage === 'realtalk') {
      // Fetch sources
      fetch(`${API_URL}/api/real-talk/sources`)
        .then(res => res.json())
        .then(data => setRtSources(data.sources || []))
        .catch(err => console.error('Failed to fetch sources:', err))

      // Fetch tags
      fetch(`${API_URL}/api/real-talk/tags`)
        .then(res => res.json())
        .then(data => {
          setRtSituationTags(data.situations || [])
          setRtEmotionTags(data.emotions || [])
        })
        .catch(err => console.error('Failed to fetch tags:', err))

      // Fetch initial entries
      fetch(`${API_URL}/api/real-talk/entries?limit=50`)
        .then(res => res.json())
        .then(data => setRtEntries(data.entries || []))
        .catch(err => console.error('Failed to fetch entries:', err))
    }
  }, [currentPage])

  // Add a new subreddit source
  const handleAddSource = async () => {
    if (!rtNewSubreddit.trim()) return
    
    setRtAddingSource(true)
    try {
      const res = await fetch(`${API_URL}/api/real-talk/sources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_identifier: rtNewSubreddit.trim() })
      })
      
      if (res.ok) {
        const data = await res.json()
        setRtSources(prev => [data.source, ...prev])
        setRtNewSubreddit('')
      } else {
        const error = await res.json()
        alert(error.error || 'Failed to add source')
      }
    } catch (err) {
      console.error('Failed to add source:', err)
      alert('Failed to add source')
    } finally {
      setRtAddingSource(false)
    }
  }

  // Add and scrape a YouTube video
  const handleAddYoutubeVideo = async () => {
    if (!rtNewYoutubeUrl.trim()) return
    
    setRtAddingYoutube(true)
    try {
      // First create a source for this video
      const sourceRes = await fetch(`${API_URL}/api/real-talk/sources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source_identifier: rtNewYoutubeUrl.trim(),
          source_type: 'youtube_video'
        })
      })
      
      if (!sourceRes.ok) {
        const error = await sourceRes.json()
        alert(error.error || 'Failed to add video source')
        return
      }
      
      const sourceData = await sourceRes.json()
      const sourceId = sourceData.source.id
      
      // Then scrape the video
      const scrapeRes = await fetch(`${API_URL}/api/real-talk/scrape-youtube`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_url: rtNewYoutubeUrl.trim(),
          source_id: sourceId
        })
      })
      
      if (scrapeRes.ok) {
        const scrapeData = await scrapeRes.json()
        alert(`✅ Scraped video: ${scrapeData.title}`)
        setRtNewYoutubeUrl('')
        
        // Refresh sources list
        const sourcesRes = await fetch(`${API_URL}/api/real-talk/sources`)
        const sourcesResData = await sourcesRes.json()
        setRtSources(sourcesResData.sources || [])
        
        // Refresh tags
        const tagsRes = await fetch(`${API_URL}/api/real-talk/tags`)
        const tagsData = await tagsRes.json()
        setRtSituationTags(tagsData.situations || [])
        setRtEmotionTags(tagsData.emotions || [])
      } else {
        const error = await scrapeRes.json()
        alert(error.error || 'Failed to scrape video')
      }
    } catch (err) {
      console.error('Failed to add YouTube video:', err)
      alert('Failed to add YouTube video')
    } finally {
      setRtAddingYoutube(false)
    }
  }


  // Add and scrape an entire YouTube channel
  const handleAddYoutubeChannel = async () => {
    if (!rtNewChannelUrl.trim()) return
    
    if (!confirm(`This will scrape up to ${rtChannelLimit} videos. This may take several minutes. Continue?`)) {
      return
    }
    
    setRtScrapingChannel(true)
    try {
      const sourceRes = await fetch(`${API_URL}/api/real-talk/sources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source_identifier: rtNewChannelUrl.trim(),
          source_type: 'youtube_channel'
        })
      })
      
      if (!sourceRes.ok) {
        const error = await sourceRes.json()
        alert(error.error || 'Failed to add channel')
        return
      }
      
      const sourceData = await sourceRes.json()
      
      const scrapeRes = await fetch(`${API_URL}/api/real-talk/scrape-youtube-channel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel_url: rtNewChannelUrl.trim(),
          source_id: sourceData.source.id,
          limit: rtChannelLimit
        })
      })
      
      if (scrapeRes.ok) {
        const scrapeData = await scrapeRes.json()
        alert(`✅ Channel done!\n\nTotal: ${scrapeData.total_videos}\nSaved: ${scrapeData.saved}\nFailed: ${scrapeData.failed}`)
        setRtNewChannelUrl('')
        
        const sourcesRes = await fetch(`${API_URL}/api/real-talk/sources`)
        const sourcesResData = await sourcesRes.json()
        setRtSources(sourcesResData.sources || [])
        
        const tagsRes = await fetch(`${API_URL}/api/real-talk/tags`)
        const tagsData = await tagsRes.json()
        setRtSituationTags(tagsData.situations || [])
        setRtEmotionTags(tagsData.emotions || [])
      } else {
        const error = await scrapeRes.json()
        alert(error.error || 'Failed to scrape channel')
      }
    } catch (err) {
      console.error('Failed to add YouTube channel:', err)
      alert('Failed to add YouTube channel')
    } finally {
      setRtScrapingChannel(false)
    }
  }

  // Scrape a single source
  const handleScrapeSource = async (sourceId: string, sourceType: string, sourceIdentifier: string) => {
    setRtScraping(sourceId)
    try {
      // YouTube videos are scraped on add, so just show message
      if (sourceType === 'youtube_video') {
        alert('YouTube videos are already scraped when added. This video has already been processed.')
        setRtScraping(null)
        return
      }
      
      const res = await fetch(`http://localhost:3001/api/real-talk/scrape/${sourceId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 50 })
      })
      
      if (res.ok) {
        const data = await res.json()
        alert(`Scraped ${data.scraped} posts, saved ${data.saved} new entries from r/${data.subreddit}`)
        
        // Refresh sources list
        const sourcesRes = await fetch(`${API_URL}/api/real-talk/sources`)
        const sourcesData = await sourcesRes.json()
        setRtSources(sourcesData.sources || [])
        
        // Refresh tags
        const tagsRes = await fetch(`${API_URL}/api/real-talk/tags`)
        const tagsData = await tagsRes.json()
        setRtSituationTags(tagsData.situations || [])
        setRtEmotionTags(tagsData.emotions || [])
      } else {
        const error = await res.json()
        alert(error.error || 'Failed to scrape source')
      }
    } catch (err) {
      console.error('Failed to scrape source:', err)
      alert('Failed to scrape source')
    } finally {
      setRtScraping(null)
    }
  }

  // Scrape all active sources
  const handleScrapeAll = async () => {
    setRtScrapingAll(true)
    try {
      const res = await fetch(`${API_URL}/api/real-talk/scrape-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 50 })
      })
      
      if (res.ok) {
        const data = await res.json()
        alert(`Scraped ${data.sources_scraped} sources, saved ${data.total_saved} new entries`)
        
        // Refresh sources
        const sourcesRes = await fetch(`${API_URL}/api/real-talk/sources`)
        const sourcesData = await sourcesRes.json()
        setRtSources(sourcesData.sources || [])
        
        // Refresh tags
        const tagsRes = await fetch(`${API_URL}/api/real-talk/tags`)
        const tagsData = await tagsRes.json()
        setRtSituationTags(tagsData.situations || [])
        setRtEmotionTags(tagsData.emotions || [])
      } else {
        const error = await res.json()
        alert(error.error || 'Failed to scrape sources')
      }
    } catch (err) {
      console.error('Failed to scrape all sources:', err)
      alert('Failed to scrape sources')
    } finally {
      setRtScrapingAll(false)
    }
  }

  // Add a new tag
  const handleAddTag = async (tagType: 'situation' | 'emotion', tagName: string) => {
    if (!tagName.trim()) return
    
    try {
      const res = await fetch(`${API_URL}/api/real-talk/tags`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag_type: tagType, tag_name: tagName.trim() })
      })
      
      if (res.ok) {
        const data = await res.json()
        if (tagType === 'situation') {
          setRtSituationTags(prev => [...prev, data.tag])
          setRtNewSituationTag('')
        } else {
          setRtEmotionTags(prev => [...prev, data.tag])
          setRtNewEmotionTag('')
        }
      } else {
        const error = await res.json()
        alert(error.error || 'Failed to add tag')
      }
    } catch (err) {
      console.error('Failed to add tag:', err)
    }
  }

  // Delete a tag
  const handleDeleteTag = async (tagId: string) => {
    if (!confirm('Delete this tag?')) return
    
    try {
      await fetch(`http://localhost:3001/api/real-talk/tags/${tagId}`, {
        method: 'DELETE'
      })
      setRtSituationTags(prev => prev.filter(t => t.id !== tagId))
      setRtEmotionTags(prev => prev.filter(t => t.id !== tagId))
    } catch (err) {
      console.error('Failed to delete tag:', err)
    }
  }

  // Melody handlers
  const handleMelodySearch = async () => {
    if (!melodyChords.trim()) {
      alert('Please enter a chord progression')
      return
    }

    setMelodySearching(true)
    try {
      const res = await fetch(`${API_URL}/api/melody/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chords: melodyChords,
          bpm: melodyBpm,
          bpm_tolerance: melodyBpmTolerance,
          time_signature: melodyTimeSig,
          year_start: melodyYearStart,
          year_end: melodyYearEnd,
          genres: melodyGenres,
          chart: melodyChart,
          artist_style: melodyArtistStyle
        })
      })

      if (res.ok) {
        const data = await res.json()
        setMelodyResults(data.matches || [])
        if (data.matches && data.matches.length > 0) {
          const allTrackIds = new Set(data.matches.map((m: any) => m.tidal_id))
          setMelodySelectedTracks(allTrackIds)
        }
      } else {
        const error = await res.json()
        alert(error.error || 'Search failed')
      }
    } catch (err) {
      console.error('Melody search failed:', err)
      alert('Search failed')
    } finally {
      setMelodySearching(false)
    }
  }

  const handleMelodyCreatePlaylist = async () => {
    const selectedMatches = melodyResults.filter(m => melodySelectedTracks.has(m.tidal_id))
    
    if (selectedMatches.length === 0) {
      alert('Please select at least one track')
      return
    }

    setMelodyCreatingPlaylist(true)
    try {
      const playlistName = melodyPlaylistName.trim() || `Mashup Discovery - ${new Date().toLocaleString()}`
      
      const res = await fetch(`${API_URL}/api/melody/playlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: playlistName,
          target_key: melodyResults[0]?.original_key || 'C major',
          target_bpm: melodyBpm,
          matches: selectedMatches
        })
      })

      if (res.ok) {
        const data = await res.json()
        alert(`✅ Playlist created!\n\n${data.track_count} tracks added.\n\nURL: ${data.playlist_url}`)
      } else {
        const error = await res.json()
        alert(error.error || 'Failed to create playlist')
      }
    } catch (err) {
      console.error('Failed to create playlist:', err)
      alert('Failed to create playlist')
    } finally {
      setMelodyCreatingPlaylist(false)
    }
  }

  const checkMelodyTidalStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/melody/tidal/status`)
      const data = await res.json()
      setMelodyTidalAuth(data.authenticated || false)
      return data.authenticated || false
    } catch (err) {
      console.error('Failed to check Tidal status:', err)
      return false
    }
  }

  const checkMelodyTidalAuthComplete = async () => {
    try {
      const res = await fetch(`${API_URL}/api/melody/tidal/check-complete`)
      const data = await res.json()
      setMelodyTidalAuth(data.authenticated || false)
      return data.authenticated || false
    } catch (err) {
      console.error('Failed to check Tidal auth completion:', err)
      return false
    }
  }

  const handleMelodyConnectTidal = async () => {
    try {
      const res = await fetch(`${API_URL}/api/melody/tidal/auth`)
      const data = await res.json()
      
      if (data.verification_url) {
        window.open(data.verification_url, '_blank')
        alert(`Opening Tidal authentication page...\n\nComplete the authentication in the new window.\n\nThe app will automatically detect when you're connected.`)
        
        // Start polling for auth completion
        const pollInterval = setInterval(async () => {
          const isAuth = await checkMelodyTidalAuthComplete()
          if (isAuth) {
            clearInterval(pollInterval)
            alert('✅ Successfully connected to Tidal!')
          }
        }, 2000) // Check every 2 seconds
        
        // Stop polling after 5 minutes
        setTimeout(() => clearInterval(pollInterval), 300000)
      }
    } catch (err) {
      console.error('Failed to start Tidal auth:', err)
      alert('Failed to connect to Tidal')
    }
  }

  const handleMelodyDisconnectTidal = async () => {
    if (!confirm('Disconnect from Tidal?')) return
    
    try {
      const res = await fetch(`${API_URL}/api/melody/tidal/disconnect`, {
        method: 'POST'
      })
      
      if (res.ok) {
        setMelodyTidalAuth(false)
        alert('✅ Disconnected from Tidal')
      } else {
        alert('Failed to disconnect from Tidal')
      }
    } catch (err) {
      console.error('Failed to disconnect:', err)
      alert('Failed to disconnect from Tidal')
    }
  }

  useEffect(() => {
    // Check Tidal auth status on Melody page load
    if (currentPage === 'melody') {
      checkMelodyTidalStatus()
    }
  }, [currentPage])

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo" onClick={() => sidebarCollapsed && setSidebarCollapsed(false)}>
            {sidebarCollapsed ? (
              <span className="logo-letter">L</span>
            ) : (
              <h1>LyricBox</h1>
            )}
          </div>
          {!sidebarCollapsed && (
            <button 
              className="collapse-btn"
              onClick={() => setSidebarCollapsed(true)}
              title="Collapse sidebar"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="16" height="16">
                <path d="M15 18l-6-6 6-6" />
              </svg>
            </button>
          )}
        </div>
        
        <nav className="sidebar-nav">
          <a 
            className={`nav-item ${currentPage === 'rhymes' ? 'active' : ''}`}
            onClick={() => setCurrentPage('rhymes')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18V5l12-2v13" />
              <circle cx="6" cy="18" r="3" />
              <circle cx="18" cy="16" r="3" />
            </svg>
            {!sidebarCollapsed && <span>Rhymes</span>}
          </a>

          <a 
            className={`nav-item ${currentPage === 'figurative' ? 'active' : ''}`}
            onClick={() => setCurrentPage('figurative')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
            {!sidebarCollapsed && <span>Figurative</span>}
          </a>
          
          <a 
            className={`nav-item ${currentPage === 'concepts' ? 'active' : ''}`}
            onClick={() => setCurrentPage('concepts')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21h6" />
              <path d="M12 17v4" />
              <path d="M12 3a6 6 0 0 0-6 6c0 2.22 1.21 4.16 3 5.2V16a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1.8c1.79-1.04 3-2.98 3-5.2a6 6 0 0 0-6-6z" />
            </svg>
            {!sidebarCollapsed && <span>Concepts</span>}
          </a>

          <a 
            className={`nav-item ${currentPage === 'nextline' ? 'active' : ''}`}
            onClick={() => setCurrentPage('nextline')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 19l7-7 3 3-7 7-3-3z" />
              <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
              <path d="M2 2l7.586 7.586" />
            </svg>
            {!sidebarCollapsed && <span>Next Line</span>}
          </a>

          <a 
            className={`nav-item ${currentPage === 'realtalk' ? 'active' : ''}`}
            onClick={() => setCurrentPage('realtalk')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              <path d="M8 9h8" />
              <path d="M8 13h6" />
            </svg>
            {!sidebarCollapsed && <span>Real Talk</span>}
          </a>

          <a 
            className={`nav-item ${currentPage === 'melody' ? 'active' : ''}`}
            onClick={() => setCurrentPage('melody')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18V5l12-2v13" />
              <circle cx="6" cy="18" r="3" />
              <circle cx="18" cy="16" r="3" />
            </svg>
            {!sidebarCollapsed && <span>Melody</span>}
          </a>
        </nav>

        <div className="sidebar-footer">
          {sidebarCollapsed ? (
            <button 
              className="expand-btn"
              onClick={() => setSidebarCollapsed(false)}
              title="Expand sidebar"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="16" height="16">
                <path d="M9 18l6-6-6-6" />
              </svg>
            </button>
          ) : (
            <div className="stats">
              <span>{stats.songs} songs</span>
              <span>•</span>
              <span>{stats.lines.toLocaleString()} lines</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {currentPage === 'rhymes' && (
          <>
            {/* Top Bar */}
            <div className="top-bar">
              <form onSubmit={handleSearch} className="search-container">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for a word to find rhymes..."
                  className="search-input"
                />
                <button type="submit" className="search-button" disabled={loading}>
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </form>
              
              <div className="top-bar-controls">
                {/* Search Mode Toggle */}
                <div className="mode-toggle">
                  <button
                    className={`mode-btn ${searchMode === 'simple' ? 'active' : ''}`}
                    onClick={() => setSearchMode('simple')}
                  >
                    Simple
                  </button>
                  <button
                    className={`mode-btn ${searchMode === 'network' ? 'active' : ''}`}
                    onClick={() => setSearchMode('network')}
                  >
                    Network
                  </button>
                </div>

                <button
                  className="filter-toggle"
                  onClick={() => setFilterSidebarOpen(true)}
                >
                  Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
                </button>

                {searchMode === 'network' && (
                  <label className="depth-select">
                    Max Depth:
                    <select value={maxDepth} onChange={(e) => setMaxDepth(Number(e.target.value))}>
                      <option value={1}>1</option>
                      <option value={2}>2</option>
                      <option value={3}>3</option>
                    </select>
                  </label>
                )}
              </div>
            </div>

            {/* Network Search Sort Builder */}
            {searchMode === 'network' && networkResult && (
              <div style={{ padding: '20px', paddingTop: '0' }}>
                <SortBuilder sortOrder={sortOrder} onChange={setSortOrder} />
              </div>
            )}

            {/* Results */}
            <div className="results-area">
              {loading && (
                <div className="loading-state">
                  <div className="spinner"></div>
                  <p>Searching...</p>
                </div>
              )}

              {!loading && searched && searchMode === 'simple' && simpleResults.length === 0 && (
                <div className="empty-state">
                  <p>No rhymes found for "{query}"</p>
                  <p className="empty-hint">Try a different word or adjust your filters</p>
                </div>
              )}

              {!loading && searchMode === 'simple' && simpleResults.length > 0 && (
                <div className="results-list">
                  <div className="results-header">
                    <h2>{simpleResults.length} results for "{query}"</h2>
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={onePerSong}
                        onChange={(e) => setOnePerSong(e.target.checked)}
                      />
                      <span>1 result per song</span>
                    </label>
                  </div>
                  {simpleResults.map((result, idx) => (
                    <div key={idx} className="result-card clickable" onClick={() => handleViewLyrics(result.song.id, result.song.title, result.song.artist, [])}>
                      <div className="lyric-context">
                        {result.linesBefore.map((line, i) => (
                          <div key={`before-${i}`} className="context-line">{line}</div>
                        ))}
                        <div className="match-line" dangerouslySetInnerHTML={{
                          __html: result.matchLine.replace(
                            new RegExp(`(${result.word})`, 'gi'),
                            '<strong>$1</strong>'
                          )
                        }} />
                        {result.linesAfter.map((line, i) => (
                          <div key={`after-${i}`} className="context-line">{line}</div>
                        ))}
                      </div>
                      <div className="result-meta">
                        <span className="result-song">
                          {result.song.title} - {result.song.artist}
                        </span>
                        {result.song.year && <span className="result-year">{result.song.year}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!loading && searchMode === 'network' && networkResult && sortedResults.length > 0 && (
                <div className="results-list">
                  <div className="results-header">
                    <h2>
                      {sortedResults.length} words for "{networkResult.searchWord}"
                    </h2>
                    <p className="results-meta">
                      {networkResult.totalConnections} connections • Depth 1-{networkResult.maxDepth}
                    </p>
                  </div>
                  <div className="network-results-grid">
                    {sortedResults.map((result) => (
                      <div key={result.word} className="network-result-card">
                        <div className="network-word">{result.word}</div>
                        <div className="network-meta">
                          <span className={`depth-badge depth-${result.depth}`}>
                            Depth {result.depth}
                          </span>
                          <span className="rhyme-type">{result.rhymeType}</span>
                          <span className="frequency">×{result.frequency}</span>
                        </div>
                        <div className="network-songs">
                          {(expandedWords.has(result.word) ? result.connections : result.connections.slice(0, 2)).map((conn, idx) => (
                            <div 
                              key={idx} 
                              className="network-song clickable"
                              onClick={() => {
                                // Use the full path stored in the connection
                                handleViewLyrics(conn.song.id, conn.song.title, conn.song.artist, conn.path)
                              }}
                            >
                              {conn.song.title} - {conn.song.artist}
                            </div>
                          ))}
                          {result.connections.length > 2 && (
                            <div 
                              className="more-connections clickable"
                              onClick={() => toggleExpanded(result.word)}
                            >
                              {expandedWords.has(result.word) 
                                ? 'Show less' 
                                : `+${result.connections.length - 2} more`
                              }
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {!loading && !searched && (
                <div className="empty-state">
                  <h2>🎵 Search for Rhymes</h2>
                  <p>
                    {searchMode === 'simple' 
                      ? 'Enter a word to find rhyming lines across all songs'
                      : 'Discover rhyme networks across songs at different depths'}
                  </p>
                </div>
              )}
            </div>
          </>
        )}

        {currentPage === 'concepts' && (
          <div className="concepts-page">
            {/* Mode Toggle */}
            <div className="concept-mode-toggle">
              <button 
                className={conceptMode === 'random' ? 'active' : ''}
                onClick={() => setConceptMode('random')}
              >
                Random Concept
              </button>
              <button 
                className={conceptMode === 'custom' ? 'active' : ''}
                onClick={() => setConceptMode('custom')}
              >
                Custom Concept
              </button>
            </div>

            {/* Custom Concept Input */}
            {conceptMode === 'custom' && (
              <div className="custom-concept-builder">
                <div className="concept-input-section">
                  <label>Your Concept Idea:</label>
                  <textarea
                    value={customIdea}
                    onChange={(e) => setCustomIdea(e.target.value)}
                    placeholder="Describe your song concept... (e.g., 'A song about missing your ex but pretending you're over them at a party')"
                    rows={4}
                    className="concept-textarea"
                  />
                </div>

                <div className="concept-matching-section">
                  <h3>Match Songs By Theme</h3>
                  
                  <div className="filter-group">
                    <label>Number of songs:</label>
                    <div className="button-group">
                      {[5, 10, 20].map(num => (
                        <button
                          key={num}
                          className={conceptFilters.numSongs === num ? 'active' : ''}
                          onClick={() => setConceptFilters({...conceptFilters, numSongs: num})}
                        >
                          {num}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Year:</label>
                    <div className="button-group">
                      {['2020s', '2010s', '2000s', '1990s', '1980s'].map(decade => {
                        const years = decade === '2020s' ? [2020, 2021, 2022, 2023, 2024, 2025] :
                                     decade === '2010s' ? [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019] :
                                     decade === '2000s' ? [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009] :
                                     decade === '1990s' ? [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999] :
                                     [1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989]
                        const isActive = years.some(y => conceptFilters.years.includes(y))
                        return (
                          <button
                            key={decade}
                            className={isActive ? 'active' : ''}
                            onClick={() => {
                              if (isActive) {
                                setConceptFilters({...conceptFilters, years: conceptFilters.years.filter(y => !years.includes(y))})
                              } else {
                                setConceptFilters({...conceptFilters, years: [...conceptFilters.years, ...years]})
                              }
                            }}
                          >
                            {decade}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Chart Position:</label>
                    <div className="button-group">
                      <button
                        className={conceptFilters.maxRank === 10 ? 'active' : ''}
                        onClick={() => setConceptFilters({...conceptFilters, minRank: 1, maxRank: 10})}
                      >
                        Top 10
                      </button>
                      <button
                        className={conceptFilters.maxRank === 20 ? 'active' : ''}
                        onClick={() => setConceptFilters({...conceptFilters, minRank: 1, maxRank: 20})}
                      >
                        Top 20
                      </button>
                      <button
                        className={conceptFilters.maxRank === 50 ? 'active' : ''}
                        onClick={() => setConceptFilters({...conceptFilters, minRank: 1, maxRank: 50})}
                      >
                        Top 50
                      </button>
                      <button
                        className={!conceptFilters.maxRank ? 'active' : ''}
                        onClick={() => setConceptFilters({...conceptFilters, minRank: undefined, maxRank: undefined})}
                      >
                        Any
                      </button>
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Genre:</label>
                    <div className="button-group">
                      {['pop', 'rock', 'hip hop', 'r&b', 'country', 'dance'].map(genre => (
                        <button
                          key={genre}
                          className={conceptFilters.genres.includes(genre) ? 'active' : ''}
                          onClick={() => {
                            if (conceptFilters.genres.includes(genre)) {
                              setConceptFilters({...conceptFilters, genres: conceptFilters.genres.filter(g => g !== genre)})
                            } else {
                              setConceptFilters({...conceptFilters, genres: [...conceptFilters.genres, genre]})
                            }
                          }}
                        >
                          {genre}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Artists (comma separated):</label>
                    <input
                      type="text"
                      placeholder="e.g., Taylor Swift, Ed Sheeran, Adele"
                      value={conceptFilters.artists.join(', ')}
                      onChange={(e) => {
                        const artistList = e.target.value.split(',').map(a => a.trim()).filter(a => a.length > 0)
                        setConceptFilters({...conceptFilters, artists: artistList})
                      }}
                      className="artist-input"
                    />
                  </div>

                  <div className="find-songs-section">
                    <button 
                      onClick={handleFindMatchingSongs} 
                      disabled={conceptLoading || !customIdea.trim()}
                      className="find-songs-btn"
                    >
                      {conceptLoading ? 'Finding Songs...' : '🔍 Find Matching Songs'}
                    </button>
                  </div>
                </div>

                {/* Matched Songs List */}
                {showingSongMatches && (
                  <div className="matched-songs-section">
                    <div className="matched-songs-header">
                      <h3>Matched Songs ({matchedSongs.length})</h3>
                      <p className="matched-songs-subtitle">Review and curate your inspiration songs</p>
                    </div>

                    <div className="matched-songs-list">
                      {matchedSongs.map(song => (
                        <div key={song.id} className="matched-song-card">
                          <div className="song-info">
                            <div className="song-title">{song.title}</div>
                            <div className="song-artist">{song.artist}</div>
                            {song.matchScore !== undefined && (
                              <span 
                                className="match-score clickable"
                                onClick={() => setViewingSongDetails(viewingSongDetails === song.id ? null : song.id)}
                              >
                                {song.matchScore} {song.matchScore === 1 ? 'match' : 'matches'} • Click to view
                              </span>
                            )}
                            {viewingSongDetails === song.id && (
                              <div className="song-details-popup">
                                <div className="detail-section">
                                  <strong>Themes:</strong>
                                  <div className="theme-tags">
                                    {song.themes?.map((theme, idx) => {
                                      // Check if this theme matches any extracted theme (fuzzy)
                                      const isMatch = extractedThemes.some(extracted => 
                                        theme.toLowerCase().includes(extracted.toLowerCase()) || 
                                        extracted.toLowerCase().includes(theme.toLowerCase())
                                      )
                                      return (
                                        <span key={idx} className={`theme-tag ${isMatch ? 'matched' : ''}`}>
                                          {isMatch && '✨ '}{theme}
                                        </span>
                                      )
                                    })}
                                  </div>
                                </div>
                                {song.imagery && (
                                  <div className="detail-section">
                                    <strong>Imagery:</strong>
                                    <ul>
                                      {song.imagery.map((img, idx) => <li key={idx}>{img}</li>)}
                                    </ul>
                                  </div>
                                )}
                                {song.tone && (
                                  <div className="detail-section">
                                    <strong>Tone:</strong> {song.tone}
                                  </div>
                                )}
                                {song.universal_scenarios && (
                                  <div className="detail-section">
                                    <strong>Universal Scenarios:</strong>
                                    <ul>
                                      {song.universal_scenarios.map((scenario, idx) => <li key={idx}>{scenario}</li>)}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                          <button 
                            onClick={() => handleRemoveSong(song.id)}
                            className="remove-song-btn"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>

                    <div className="manual-song-search">
                      <label>Add more songs:</label>
                      <input
                        type="text"
                        placeholder="Search by song title or artist..."
                        value={songSearchQuery}
                        onChange={(e) => {
                          setSongSearchQuery(e.target.value)
                          handleSearchSongs(e.target.value)
                        }}
                        className="song-search-input"
                      />
                      {songSearchResults.length > 0 && (
                        <div className="search-results-dropdown">
                          {songSearchResults.map(song => (
                            <div 
                              key={song.id} 
                              className="search-result-item"
                              onClick={() => handleAddSong(song.id)}
                            >
                              <span className="result-title">{song.title}</span>
                              <span className="result-artist">{song.artist}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="time-estimate">
                      ⏱️ Estimated time: ~{getEstimatedTime().toFixed(1)} seconds
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Generate Button */}
            <div className="concepts-header">
              {conceptMode === 'custom' && showingSongMatches ? (
                <button 
                  onClick={handleGenerateConcept} 
                  disabled={conceptLoading || matchedSongs.length === 0} 
                  className="search-button"
                >
                  {conceptLoading ? 'Generating...' : `Generate from ${matchedSongs.length} Songs`}
                </button>
              ) : (
                <button 
                  onClick={conceptMode === 'random' ? handleGenerateConcept : handleFindMatchingSongs} 
                  disabled={conceptLoading} 
                  className="search-button"
                >
                  {conceptLoading ? 'Loading...' : conceptMode === 'random' ? 'Generate Random Concept' : 'Find Matching Songs'}
                </button>
              )}
            </div>

            {concept && (
              <div className="concept-display">
                <div className="concept-export-section">
                  <button 
                    onClick={() => {
                      // Download concept as PDF
                      const conceptData = {
                        title: conceptMode === 'random' ? `${concept.songs.title} - ${concept.songs.artist}` : 'Custom Concept',
                        ...concept
                      }
                      
                      fetch(`${API_URL}/api/export-concept`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(conceptData)
                      })
                      .then(res => res.blob())
                      .then(blob => {
                        const url = window.URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url
                        a.download = `concept-${Date.now()}.pdf`
                        a.click()
                      })
                      .catch(err => console.error('Export failed:', err))
                    }}
                    className="export-btn"
                  >
                    📄 Export as PDF
                  </button>
                </div>
                {concept.concept_summary && (
                  <div className="concept-section">
                    <h3>Summary</h3>
                    <p className="concept-summary">{concept.concept_summary}</p>
                  </div>
                )}

                <div className="concept-section">
                  <h3>Themes</h3>
                  <div className="theme-tags">
                    {concept.themes.map((theme, idx) => (
                      <span key={idx} className="theme-tag">{theme}</span>
                    ))}
                  </div>
                </div>

                {concept.imagery && concept.imagery.length > 0 && (
                  <div className="concept-section">
                    <h3>Imagery</h3>
                    <div className="imagery-list">
                      {concept.imagery.map((img, idx) => (
                        <div key={idx} className="imagery-item">{img}</div>
                      ))}
                    </div>
                  </div>
                )}

                {concept.tone && (
                  <div className="concept-section">
                    <h3>Tone</h3>
                    <p className="tone-text">{concept.tone}</p>
                  </div>
                )}

                {concept.universal_scenarios && concept.universal_scenarios.length > 0 && (
                  <div className="concept-section">
                    <h3>Universal Scenarios</h3>
                    <div className="scenarios-list">
                      {concept.universal_scenarios.map((scenario, idx) => (
                        <div key={idx} className="scenario-item">• {scenario}</div>
                      ))}
                    </div>
                  </div>
                )}

                {titles.length > 0 && (
                  <div className="concept-section">
                    <h3>Alternative Titles</h3>
                    <div className="titles-grid">
                      {titles.map((title, idx) => (
                        <div key={idx} className="title-card">{title}</div>
                      ))}
                    </div>
                    <div className="more-titles-section">
                      <button 
                        onClick={handleGenerateMoreTitles}
                        disabled={generatingTitles}
                        className="more-titles-btn"
                      >
                        {generatingTitles ? 'Generating...' : '✨ Generate More Titles'}
                      </button>
                    </div>
                  </div>
                )}

                {concept.section_breakdown && concept.section_breakdown.length > 0 && (
                  <div className="concept-section">
                    <h3>Section Breakdown</h3>
                    <div className="section-breakdown">
                      {concept.section_breakdown.map((section, idx) => (
                        <div key={idx} className="section-item">{section}</div>
                      ))}
                    </div>
                  </div>
                )}

                {concept.thematic_vocabulary && concept.thematic_vocabulary.length > 0 && (
                  <div className="concept-section">
                    <h3>Thematic Vocabulary</h3>
                    <div className="vocab-tags">
                      {concept.thematic_vocabulary.map((word, idx) => (
                        <span key={idx} className="vocab-tag">{word}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Next Line Page */}
        {currentPage === 'nextline' && (
          <div className="nextline-page">
            <div className="nextline-header">
              <h1>AI Songwriting Assistant</h1>
              <p className="nextline-subtitle">Get AI-powered suggestions for your next line</p>
            </div>

            <div className="nextline-builder">
              <div className="nextline-inputs">
                <div className="input-section">
                  <label>Song Concept/Theme</label>
                  <textarea
                    value={nextLineConcept}
                    onChange={(e) => setNextLineConcept(e.target.value)}
                    placeholder="What's your song about? (e.g., 'A song about missing your ex but pretending you're over them')"
                    rows={3}
                    className="nextline-textarea"
                  />
                </div>

                <div className="input-section">
                  <label>Lyrics You've Written So Far</label>
                  <textarea
                    value={existingLyrics}
                    onChange={(e) => setExistingLyrics(e.target.value)}
                    placeholder="Paste your existing lyrics here (optional but recommended for better context)"
                    rows={8}
                    className="nextline-textarea"
                  />
                </div>

                <div className="input-row">
                  <div className="input-section flex-1">
                    <label>Example Line (syllable pattern)</label>
                    <input
                      type="text"
                      value={exampleLine}
                      onChange={(e) => setExampleLine(e.target.value)}
                      placeholder="e.g., 'I've been thinking about you lately'"
                      className="nextline-input"
                    />
                    {exampleLine && (
                      <div className="syllable-count">
                        Syllables: {countSyllables(exampleLine)}
                      </div>
                    )}
                  </div>
                </div>

                <div className="input-row">
                  <div className="input-section flex-1">
                    <label>Rhyme With (word/sound)</label>
                    <input
                      type="text"
                      value={rhymeTarget}
                      onChange={(e) => setRhymeTarget(e.target.value)}
                      placeholder="e.g., 'you'"
                      className="nextline-input"
                    />
                  </div>

                  <div className="input-section">
                    <label>Position</label>
                    <select 
                      value={rhymePosition} 
                      onChange={(e) => setRhymePosition(e.target.value as 'end' | 'internal')}
                      className="nextline-select"
                    >
                      <option value="end">End of line</option>
                      <option value="internal">Internal</option>
                    </select>
                  </div>

                  <div className="input-section">
                    <label>Rhyme Type</label>
                    <select 
                      value={rhymeTypeFilter} 
                      onChange={(e) => setRhymeTypeFilter(e.target.value)}
                      className="nextline-select"
                    >
                      <option value="any">Any</option>
                      <option value="perfect">Perfect</option>
                      <option value="slant">Slant</option>
                      <option value="assonance">Assonance</option>
                      <option value="consonance">Consonance</option>
                    </select>
                  </div>

                  <div className="input-section">
                    <label>Line Type</label>
                    <select 
                      value={lineType} 
                      onChange={(e) => setLineType(e.target.value as 'regular' | 'metaphor' | 'simile')}
                      className="nextline-select"
                    >
                      <option value="regular">Regular Line</option>
                      <option value="metaphor">Metaphor</option>
                      <option value="simile">Simile</option>
                    </select>
                  </div>
                </div>

                {/* Optional constraints */}
                <div className="input-section">
                  <label>What Should This Line Mean? (optional)</label>
                  <input
                    type="text"
                    value={lineMeaning}
                    onChange={(e) => setLineMeaning(e.target.value)}
                    placeholder="e.g., 'Expressing regret for mistakes made'"
                    className="nextline-input"
                  />
                </div>

                <div className="input-row">
                  <div className="input-section flex-1">
                    <label>Use This Specific Rhyme Word (optional)</label>
                    <input
                      type="text"
                      value={specificRhymeWord}
                      onChange={(e) => setSpecificRhymeWord(e.target.value)}
                      placeholder="e.g., 'blue' (will force this exact rhyme word)"
                      className="nextline-input"
                    />
                  </div>

                  <div className="input-section flex-1">
                    <label>Partial Line Already Written (optional)</label>
                    <input
                      type="text"
                      value={partialLine}
                      onChange={(e) => setPartialLine(e.target.value)}
                      placeholder="e.g., 'I know that' (AI will complete this)"
                      className="nextline-input"
                    />
                  </div>
                </div>

                <div className="input-section">
                  <label>Words to Avoid (optional)</label>
                  <input
                    type="text"
                    value={wordsToAvoid}
                    onChange={(e) => setWordsToAvoid(e.target.value)}
                    placeholder="e.g., 'me, away, day' (comma-separated words you don't want to use)"
                    className="nextline-input"
                  />
                  <div className="input-hint" style={{fontSize: '12px', color: '#888', marginTop: '4px'}}>
                    List words you've already used as rhymes and don't want to repeat
                  </div>
                </div>

                {/* Filters */}
                <div className="nextline-filters">
                  <h3>Filter Reference Songs</h3>
                  
                  <div className="filter-group">
                    <label>Number of songs:</label>
                    <div className="button-group">
                      {[5, 10, 20].map(num => (
                        <button
                          key={num}
                          className={nextLineFilters.numSongs === num ? 'active' : ''}
                          onClick={() => setNextLineFilters({...nextLineFilters, numSongs: num})}
                        >
                          {num}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Year:</label>
                    <div className="button-group">
                      {['2020s', '2010s', '2000s', '1990s', '1980s'].map(decade => {
                        const years = decade === '2020s' ? [2020, 2021, 2022, 2023, 2024, 2025] :
                                     decade === '2010s' ? [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019] :
                                     decade === '2000s' ? [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009] :
                                     decade === '1990s' ? [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999] :
                                     [1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989]
                        const isActive = years.some(y => nextLineFilters.years.includes(y))
                        return (
                          <button
                            key={decade}
                            className={isActive ? 'active' : ''}
                            onClick={() => {
                              if (isActive) {
                                setNextLineFilters({...nextLineFilters, years: nextLineFilters.years.filter(y => !years.includes(y))})
                              } else {
                                setNextLineFilters({...nextLineFilters, years: [...nextLineFilters.years, ...years]})
                              }
                            }}
                          >
                            {decade}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Chart Position:</label>
                    <div className="button-group">
                      <button
                        className={nextLineFilters.maxRank === 10 ? 'active' : ''}
                        onClick={() => setNextLineFilters({...nextLineFilters, minRank: 1, maxRank: 10})}
                      >
                        Top 10
                      </button>
                      <button
                        className={nextLineFilters.maxRank === 20 ? 'active' : ''}
                        onClick={() => setNextLineFilters({...nextLineFilters, minRank: 1, maxRank: 20})}
                      >
                        Top 20
                      </button>
                      <button
                        className={nextLineFilters.maxRank === 50 ? 'active' : ''}
                        onClick={() => setNextLineFilters({...nextLineFilters, minRank: 1, maxRank: 50})}
                      >
                        Top 50
                      </button>
                      <button
                        className={!nextLineFilters.maxRank ? 'active' : ''}
                        onClick={() => setNextLineFilters({...nextLineFilters, minRank: undefined, maxRank: undefined})}
                      >
                        Any
                      </button>
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Genre:</label>
                    <div className="button-group">
                      {['pop', 'rock', 'hip hop', 'r&b', 'country', 'dance'].map(genre => (
                        <button
                          key={genre}
                          className={nextLineFilters.genres.includes(genre) ? 'active' : ''}
                          onClick={() => {
                            if (nextLineFilters.genres.includes(genre)) {
                              setNextLineFilters({...nextLineFilters, genres: nextLineFilters.genres.filter(g => g !== genre)})
                            } else {
                              setNextLineFilters({...nextLineFilters, genres: [...nextLineFilters.genres, genre]})
                            }
                          }}
                        >
                          {genre}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Artists (comma separated):</label>
                    <input
                      type="text"
                      placeholder="e.g., Taylor Swift, Ed Sheeran"
                      value={nextLineFilters.artists.join(', ')}
                      onChange={(e) => {
                        const artistList = e.target.value.split(',').map(a => a.trim()).filter(a => a.length > 0)
                        setNextLineFilters({...nextLineFilters, artists: artistList})
                      }}
                      className="artist-input"
                    />
                  </div>
                </div>

                <div className="nextline-actions">
                  <button 
                    onClick={handleFindNextLineSongs}
                    disabled={generatingNextLine || !nextLineConcept.trim()}
                    className="search-button"
                  >
                    🔍 Find Reference Songs
                  </button>
                </div>
              </div>

              {/* Matched Songs for Next Line */}
              {showingNextLineSongs && nextLineMatchedSongs.length > 0 && (
                <div className="matched-songs-section">
                  <div className="matched-songs-header">
                    <h3>Reference Songs ({nextLineMatchedSongs.length})</h3>
                    <p className="matched-songs-subtitle">These songs will guide the AI's suggestions</p>
                  </div>

                  <div className="matched-songs-list">
                    {nextLineMatchedSongs.map(song => (
                      <div key={song.id} className="matched-song-card">
                        <div className="song-info">
                          <div className="song-title">{song.title}</div>
                          <div className="song-artist">{song.artist}</div>
                          {song.matchScore !== undefined && (
                            <span 
                              className="match-score clickable"
                              onClick={() => setViewingNextLineSongDetails(viewingNextLineSongDetails === song.id ? null : song.id)}
                            >
                              {song.matchScore} {song.matchScore === 1 ? 'match' : 'matches'} • Click to view
                            </span>
                          )}
                          {viewingNextLineSongDetails === song.id && (
                            <div className="song-details-popup">
                              <div className="detail-section">
                                <strong>Themes:</strong>
                                <div className="theme-tags">
                                  {song.themes?.map((theme, idx) => {
                                    // Check if this theme matches any extracted theme (fuzzy)
                                    const isMatch = nextLineExtractedThemes.some(extracted => 
                                      theme.toLowerCase().includes(extracted.toLowerCase()) || 
                                      extracted.toLowerCase().includes(theme.toLowerCase())
                                    )
                                    return (
                                      <span key={idx} className={`theme-tag ${isMatch ? 'matched' : ''}`}>
                                        {isMatch && '✨ '}{theme}
                                      </span>
                                    )
                                  })}
                                </div>
                              </div>
                              {song.imagery && (
                                <div className="detail-section">
                                  <strong>Imagery:</strong>
                                  <ul>
                                    {song.imagery.map((img, idx) => <li key={idx}>{img}</li>)}
                                  </ul>
                                </div>
                              )}
                              {song.tone && (
                                <div className="detail-section">
                                  <strong>Tone:</strong> {song.tone}
                                </div>
                              )}
                              {song.universal_scenarios && (
                                <div className="detail-section">
                                  <strong>Universal Scenarios:</strong>
                                  <ul>
                                    {song.universal_scenarios.map((scenario, idx) => <li key={idx}>{scenario}</li>)}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={() => setNextLineMatchedSongs(nextLineMatchedSongs.filter(s => s.id !== song.id))}
                          className="remove-song-btn"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="nextline-actions">
                    <button 
                      onClick={handleGenerateNextLine}
                      disabled={generatingNextLine || nextLineMatchedSongs.length === 0}
                      className="search-button"
                    >
                      {generatingNextLine ? 'Generating...' : '✨ Generate Line Suggestions'}
                    </button>
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {nextLineSuggestions.length > 0 && (
                <div className="suggestions-section">
                  <h3>Suggested Next Lines ({nextLineSuggestions.length})</h3>
                  <div className="suggestions-list">
                    {nextLineSuggestions.map((suggestion, idx) => (
                      <div key={idx} className={`suggestion-card ${suggestion.diff === 0 ? 'perfect-match' : ''}`}>
                        <div className="suggestion-header">
                          <div className="suggestion-text">{suggestion.line}</div>
                          <div className={`syllable-badge ${suggestion.diff === 0 ? 'exact' : suggestion.diff <= 1 ? 'close' : 'far'}`}>
                            {suggestion.syllables} syl {suggestion.diff === 0 ? '✅' : ''}
                          </div>
                        </div>
                        <div className="suggestion-actions">
                          <button 
                            onClick={() => handleMoreLikeThis(suggestion.line)}
                            disabled={generatingNextLine}
                            className="more-like-btn"
                          >
                            More Like This
                          </button>
                          <button 
                            onClick={() => handleUseSuggestion(suggestion.line)}
                            className="use-btn"
                          >
                            Use This
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="nextline-actions">
                    <button 
                      onClick={handleGenerateNextLine}
                      disabled={generatingNextLine}
                      className="more-titles-btn"
                    >
                      {generatingNextLine ? 'Generating...' : '✨ Generate More Variations'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {currentPage === 'figurative' && (
          <div className="figurative-page">
            <div className="figurative-header">
              <h1>Figurative Language Finder</h1>
              <p className="figurative-subtitle">Search for similes, metaphors, and other figurative language patterns in hit songs</p>
            </div>

            <div className="figurative-content">
              {/* Keyword Selection */}
              <div className="keyword-section">
                <h3>Step 1: Select keywords to search for</h3>
                
                <div className="keyword-presets">
                  <div className="preset-group">
                    <span className="preset-label">Similes:</span>
                    <div className="preset-buttons">
                      <button
                        className={`keyword-btn all-btn ${figurativeAllSimiles ? 'active' : ''}`}
                        onClick={() => {
                          // Toggle "All Similes"
                          if (figurativeAllSimiles) {
                            // Turn OFF all similes, keep metaphors if they're on
                            setFigurativeAllSimiles(false)
                            const nonSimiles = figurativeKeywords.filter(k => !SIMILE_KEYWORDS.includes(k))
                            setFigurativeKeywords(nonSimiles)
                          } else {
                            // Turn ON all similes, add to existing keywords
                            setFigurativeAllSimiles(true)
                            const nonSimiles = figurativeKeywords.filter(k => !SIMILE_KEYWORDS.includes(k))
                            setFigurativeKeywords([...nonSimiles, ...SIMILE_KEYWORDS])
                          }
                        }}
                      >
                        All Similes
                      </button>
                      {['like', 'as', 'than'].map(kw => (
                        <button
                          key={kw}
                          className={`keyword-btn ${!figurativeAllSimiles && figurativeKeywords.includes(kw) ? 'active' : ''}`}
                          onClick={() => {
                            // If in "All Similes" mode, clicking individual switches to just that one
                            if (figurativeAllSimiles) {
                              setFigurativeAllSimiles(false)
                              // Keep metaphor keywords if they're on
                              const nonSimiles = figurativeKeywords.filter(k => !SIMILE_KEYWORDS.includes(k))
                              setFigurativeKeywords([...nonSimiles, kw])
                            } else {
                              // In individual mode, toggle the keyword
                              if (figurativeKeywords.includes(kw)) {
                                setFigurativeKeywords(figurativeKeywords.filter(k => k !== kw))
                              } else {
                                setFigurativeKeywords([...figurativeKeywords, kw])
                              }
                            }
                          }}
                        >
                          "{kw}"
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="preset-group">
                    <span className="preset-label">Metaphors:</span>
                    <div className="preset-buttons">
                      <button
                        className={`keyword-btn all-btn ${figurativeAllMetaphors ? 'active' : ''}`}
                        onClick={() => {
                          // Toggle "All Metaphors"
                          if (figurativeAllMetaphors) {
                            // Turn OFF all metaphors, keep similes if they're on
                            setFigurativeAllMetaphors(false)
                            const nonMetaphors = figurativeKeywords.filter(k => !METAPHOR_KEYWORDS.includes(k))
                            setFigurativeKeywords(nonMetaphors)
                          } else {
                            // Turn ON all metaphors, add to existing keywords
                            setFigurativeAllMetaphors(true)
                            const nonMetaphors = figurativeKeywords.filter(k => !METAPHOR_KEYWORDS.includes(k))
                            setFigurativeKeywords([...nonMetaphors, ...METAPHOR_KEYWORDS])
                          }
                        }}
                      >
                        All Metaphors
                      </button>
                      {['is a', 'is the', 'was a', 'are the', 'am a'].map(kw => (
                        <button
                          key={kw}
                          className={`keyword-btn ${!figurativeAllMetaphors && figurativeKeywords.includes(kw) ? 'active' : ''}`}
                          onClick={() => {
                            // If in "All Metaphors" mode, clicking individual switches to just that one
                            if (figurativeAllMetaphors) {
                              setFigurativeAllMetaphors(false)
                              // Keep simile keywords if they're on
                              const nonMetaphors = figurativeKeywords.filter(k => !METAPHOR_KEYWORDS.includes(k))
                              setFigurativeKeywords([...nonMetaphors, kw])
                            } else {
                              // In individual mode, toggle the keyword
                              if (figurativeKeywords.includes(kw)) {
                                setFigurativeKeywords(figurativeKeywords.filter(k => k !== kw))
                              } else {
                                setFigurativeKeywords([...figurativeKeywords, kw])
                              }
                            }
                          }}
                        >
                          "{kw}"
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="preset-group">
                    <span className="preset-label">Custom:</span>
                    <div className="custom-keyword-input">
                      <input
                        type="text"
                        value={figurativeCustomKeyword}
                        onChange={(e) => setFigurativeCustomKeyword(e.target.value)}
                        placeholder="Enter custom keyword..."
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && figurativeCustomKeyword.trim()) {
                            setFigurativeAllSimiles(false)
                            setFigurativeAllMetaphors(false)
                            setFigurativeKeywords([...figurativeKeywords, figurativeCustomKeyword.trim()])
                            setFigurativeCustomKeyword('')
                          }
                        }}
                      />
                      <button
                        onClick={() => {
                          if (figurativeCustomKeyword.trim()) {
                            setFigurativeAllSimiles(false)
                            setFigurativeAllMetaphors(false)
                            setFigurativeKeywords([...figurativeKeywords, figurativeCustomKeyword.trim()])
                            setFigurativeCustomKeyword('')
                          }
                        }}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>

                <div className="active-keywords">
                  <span>Searching for: </span>
                  {figurativeKeywords.map(kw => (
                    <span key={kw} className="keyword-tag">
                      "{kw}"
                      <button onClick={() => {
                        // Turn off the appropriate "All" mode
                        if (SIMILE_KEYWORDS.includes(kw)) {
                          setFigurativeAllSimiles(false)
                        }
                        if (METAPHOR_KEYWORDS.includes(kw)) {
                          setFigurativeAllMetaphors(false)
                        }
                        
                        setFigurativeKeywords(figurativeKeywords.filter(k => k !== kw))
                      }}>×</button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Filters */}
              <div className="figurative-filters">
                <h3>Step 2: Song filters (optional)</h3>
                <div className="filter-row">
                  <div className="filter-group">
                    <label>Chart Position:</label>
                    <div className="button-group">
                      <button
                        className={figurativeFilters.minRank === 1 && figurativeFilters.maxRank === 10 ? 'active' : ''}
                        onClick={() => setFigurativeFilters({...figurativeFilters, minRank: 1, maxRank: 10})}
                      >
                        Top 10
                      </button>
                      <button
                        className={figurativeFilters.minRank === 1 && figurativeFilters.maxRank === 20 ? 'active' : ''}
                        onClick={() => setFigurativeFilters({...figurativeFilters, minRank: 1, maxRank: 20})}
                      >
                        Top 20
                      </button>
                      <button
                        className={figurativeFilters.minRank === undefined ? 'active' : ''}
                        onClick={() => setFigurativeFilters({...figurativeFilters, minRank: undefined, maxRank: undefined})}
                      >
                        Any
                      </button>
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Decade:</label>
                    <div className="button-group">
                      {['2020s', '2010s', '2000s'].map(decade => {
                        const years = decade === '2020s' ? [2020, 2021, 2022, 2023, 2024, 2025] :
                                     decade === '2010s' ? [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019] :
                                     [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009]
                        const isActive = years.some(y => figurativeFilters.years.includes(y))
                        return (
                          <button
                            key={decade}
                            className={isActive ? 'active' : ''}
                            onClick={() => {
                              if (isActive) {
                                setFigurativeFilters({...figurativeFilters, years: figurativeFilters.years.filter(y => !years.includes(y))})
                              } else {
                                setFigurativeFilters({...figurativeFilters, years: [...figurativeFilters.years, ...years]})
                              }
                            }}
                          >
                            {decade}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div className="filter-group">
                    <label>Genre:</label>
                    <div className="button-group">
                      {['pop', 'rock', 'hip hop', 'r&b', 'country'].map(genre => (
                        <button
                          key={genre}
                          className={figurativeFilters.genres.includes(genre) ? 'active' : ''}
                          onClick={() => {
                            if (figurativeFilters.genres.includes(genre)) {
                              setFigurativeFilters({...figurativeFilters, genres: figurativeFilters.genres.filter(g => g !== genre)})
                            } else {
                              setFigurativeFilters({...figurativeFilters, genres: [...figurativeFilters.genres, genre]})
                            }
                          }}
                        >
                          {genre}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Sort Builder */}
              <div className="figurative-filters">
                <h3>Step 3: Prioritize Results (optional)</h3>
                <p style={{color: '#888', fontSize: '13px', marginBottom: '12px'}}>
                  Order results before sending to AI - affects which {figurativeResultLimit} get analyzed
                </p>
                <div className="sort-builder-inline">
                  <div className="sort-buttons">
                    {[
                      { field: 'like', label: '"like"' },
                      { field: 'as', label: '"as"' },
                      { field: 'than', label: '"than"' },
                      { field: 'is_a', label: '"is a"' },
                      { field: 'is_the', label: '"is the"' },
                      { field: 'was_a', label: '"was a"' },
                      { field: 'are_the', label: '"are the"' },
                      { field: 'am_a', label: '"am a"' },
                      { field: 'chart', label: 'Chart Position' },
                      { field: 'artist', label: 'Artist A-Z' },
                      { field: 'song', label: 'Song A-Z' },
                      { field: 'random', label: 'Random' }
                    ].map(({ field, label }) => {
                      const isActive = figurativeSortOrder.some(s => s.field === field)
                      const criterion = figurativeSortOrder.find(s => s.field === field)
                      
                      return (
                        <button
                          key={field}
                          className={`sort-button ${isActive ? 'active' : ''}`}
                          onClick={() => {
                            if (isActive) {
                              // Toggle direction
                              setFigurativeSortOrder(figurativeSortOrder.map(s =>
                                s.field === field
                                  ? { ...s, direction: s.direction === 'asc' ? 'desc' : 'asc' as const }
                                  : s
                              ))
                            } else {
                              // Add to sort order
                              const newCriterion = {
                                id: `${Date.now()}-${field}`,
                                field,
                                direction: (field === 'chart' || field === 'random') ? 'asc' : 'desc' as const,
                                label
                              }
                              setFigurativeSortOrder([...figurativeSortOrder, newCriterion])
                            }
                          }}
                        >
                          {label}
                          {isActive && (
                            <span className="direction-indicator">
                              {criterion?.direction === 'asc' ? ' ↑' : ' ↓'}
                            </span>
                          )}
                        </button>
                      )
                    })}
                  </div>

                  {figurativeSortOrder.length > 0 && (
                    <div className="sort-chain">
                      <div className="sort-chain-label">Priority:</div>
                      <div className="sort-items">
                        {figurativeSortOrder.map((criterion, index) => (
                          <div key={criterion.id} className="sort-item">
                            <span className="sort-priority">{index + 1}</span>
                            <span className="sort-label">
                              {criterion.label} {criterion.direction === 'asc' ? '↑' : '↓'}
                            </span>
                            <button
                              onClick={() => setFigurativeSortOrder(figurativeSortOrder.filter(s => s.id !== criterion.id))}
                              className="remove-sort"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {figurativeSortOrder.length === 0 && (
                    <div className="sort-empty">
                      Click a sort option to prioritize certain results
                    </div>
                  )}
                </div>
              </div>

              {/* Result Limit */}
              <div className="figurative-filters">
                <h3>Step 4: AI Analysis Limit (optional)</h3>
                <div className="filter-row">
                  <div className="filter-group">
                    <label>Max results to analyze with AI:</label>
                    <div className="button-group">
                      {[50, 100, 200, 500].map(limit => {
                        const estimatedTime = Math.ceil(limit / 50) * 10 // ~10s per 50 lines
                        return (
                          <button
                            key={limit}
                            className={figurativeResultLimit === limit ? 'active' : ''}
                            onClick={() => setFigurativeResultLimit(limit)}
                          >
                            {limit} (~{estimatedTime}s)
                          </button>
                        )
                      })}
                    </div>
                    <p style={{color: '#888', fontSize: '12px', marginTop: '8px'}}>
                      Analyzing more results takes longer but may find better matches
                    </p>
                  </div>
                </div>
              </div>

              {/* Preview Results */}
              <div className="figurative-filters">
                <h3>Preview Results (optional)</h3>
                <p style={{color: '#888', fontSize: '13px', marginBottom: '12px'}}>
                  See which songs and lines match your filters and sort before sending to AI
                </p>
                <button
                  onClick={handlePreviewFigurativeResults}
                  disabled={figurativePreviewing || figurativeKeywords.length === 0}
                  className="preview-btn"
                  style={{
                    background: '#2a2a2a',
                    border: '1px solid #4a9eff',
                    color: '#4a9eff',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    width: '100%',
                    marginBottom: '12px'
                  }}
                >
                  {figurativePreviewing ? '🔍 Loading Preview...' : '👀 Preview Filtered & Sorted Results'}
                </button>
                
                {figurativePreviewResults.length > 0 && (
                  <div style={{
                    background: '#1e1e1e',
                    border: '1px solid #333',
                    borderRadius: '6px',
                    padding: '12px',
                    maxHeight: '400px',
                    overflowY: 'auto'
                  }}>
                    <div style={{color: '#4a9eff', fontWeight: 'bold', marginBottom: '8px'}}>
                      ✅ Found {figurativePreviewResults.length} unique lines
                    </div>
                    <div style={{color: '#888', fontSize: '12px', marginBottom: '12px'}}>
                      First {Math.min(figurativeResultLimit, figurativePreviewResults.length)} will be sent to AI for meaning analysis
                    </div>
                    <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                      {figurativePreviewResults.slice(0, 50).map((result, idx) => (
                        <div key={idx} style={{
                          background: idx < figurativeResultLimit ? '#252525' : '#1a1a1a',
                          border: `1px solid ${idx < figurativeResultLimit ? '#4a9eff' : '#333'}`,
                          borderRadius: '4px',
                          padding: '8px',
                          fontSize: '13px'
                        }}>
                          <div style={{color: '#4a9eff', fontSize: '11px', marginBottom: '4px'}}>
                            #{idx + 1} • {result.songTitle} - {result.artist} • "{result.keyword}"
                          </div>
                          <div style={{color: '#e0e0e0'}}>
                            {result.line}
                          </div>
                          {idx === figurativeResultLimit - 1 && (
                            <div style={{color: '#ff9933', fontSize: '11px', marginTop: '4px', fontWeight: 'bold'}}>
                              ⬆️ AI Limit: Results below this line won't be analyzed
                            </div>
                          )}
                        </div>
                      ))}
                      {figurativePreviewResults.length > 50 && (
                        <div style={{color: '#666', fontSize: '12px', textAlign: 'center', padding: '8px'}}>
                          ... and {figurativePreviewResults.length - 50} more results
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* AI Meaning Search */}
              <div className="meaning-filter-section">
                <h3>Step 6: What do you want the figurative expression to mean?</h3>
                <div className="meaning-filter-input">
                  <input
                    type="text"
                    value={figurativeDesiredMeaning}
                    onChange={(e) => setFigurativeDesiredMeaning(e.target.value)}
                    placeholder="e.g., 'expressing hope and optimism' or 'describing emotional pain'"
                    className="meaning-input"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && figurativeDesiredMeaning.trim() && figurativeKeywords.length > 0) {
                        handleFilterByMeaning()
                      }
                    }}
                  />
                  <button
                    onClick={handleFilterByMeaning}
                    disabled={figurativeFilteringByMeaning || !figurativeDesiredMeaning.trim() || figurativeKeywords.length === 0}
                    className="filter-meaning-btn"
                  >
                    {figurativeFilteringByMeaning ? 'Searching & Analyzing...' : '✨ Find Figurative Language with This Meaning'}
                  </button>
                </div>
                <p className="meaning-filter-hint">
                  AI will search your selected keywords and show you only the lines that match your desired meaning
                </p>
              </div>

              {/* Results */}
              {figurativeResults.length > 0 && (
                <div className="figurative-results">
                  <h3>{figurativeResults.length} results</h3>
                  <div className="results-grid">
                    {figurativeResults.map((result, idx) => (
                      <div key={idx} className="figurative-result-card">
                        <div className="result-song-info">
                          <strong>{result.songTitle}</strong> - {result.artist}
                        </div>
                        <div className="result-context">
                          {result.context.map((line, lineIdx) => {
                            const isMatchLine = line === result.line
                            if (isMatchLine) {
                              // Highlight the keyword in the matched line
                              const keywordLower = result.keyword.toLowerCase()
                              const lineLower = line.toLowerCase()
                              const keywordIdx = lineLower.indexOf(keywordLower)
                              if (keywordIdx !== -1) {
                                return (
                                  <div key={lineIdx} className="context-line matched">
                                    {line.slice(0, keywordIdx)}
                                    <span className="keyword-highlight">{line.slice(keywordIdx, keywordIdx + result.keyword.length)}</span>
                                    {line.slice(keywordIdx + result.keyword.length)}
                                  </div>
                                )
                              }
                            }
                            return <div key={lineIdx} className={`context-line ${isMatchLine ? 'matched' : ''}`}>{line}</div>
                          })}
                        </div>
                        <div className="result-actions">
                          <button 
                            className="view-song-btn"
                            onClick={() => handleViewLyrics(result.songId, result.keyword)}
                          >
                            View Full Song
                          </button>
                          <div className="generate-variation">
                            <input
                              type="text"
                              placeholder="Enter meaning..."
                              value={figurativeMeaning}
                              onChange={(e) => setFigurativeMeaning(e.target.value)}
                            />
                            <button
                              onClick={() => handleGenerateFigurativeVariations(result.line, result.keyword)}
                              disabled={figurativeGenerating}
                            >
                              {figurativeGenerating ? '...' : '✨ Generate with this meaning'}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {figurativeResults.length === 0 && !figurativeSearching && figurativeKeywords.length > 0 && (
                <div className="no-results">
                  <p>Click search to find figurative language patterns in songs</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Real Talk Page */}
        {currentPage === 'realtalk' && (
          <div className="real-talk-page">
            <div className="page-header">
              <h1>Real Talk</h1>
              <p>Authentic conversations from real people</p>
            </div>

            {/* Tab Selector */}
            <div className="rt-tabs">
              <button 
                className={`rt-tab ${rtTab === 'browse' ? 'active' : ''}`}
                onClick={() => setRtTab('browse')}
              >
                Browse
              </button>
              <button 
                className={`rt-tab ${rtTab === 'manage' ? 'active' : ''}`}
                onClick={() => setRtTab('manage')}
              >
                Manage Sources
              </button>
            </div>

            {/* Browse Tab */}
            {rtTab === 'browse' && (
              <div className="rt-browse">
                {/* Search & Filters */}
                <div className="rt-search-section">
                  <div className="rt-search-row">
                    <input
                      type="text"
                      placeholder="Search conversations (optional)..."
                      value={rtFilters.search}
                      onChange={(e) => setRtFilters({...rtFilters, search: e.target.value})}
                      className="rt-search-input"
                    />
                    <button 
                      onClick={async () => {
                        setRtLoading(true)
                        try {
                          const params = new URLSearchParams()
                          if (rtFilters.search) params.append('search', rtFilters.search)
                          if (rtFilters.situations.length) params.append('situations', rtFilters.situations.join(','))
                          if (rtFilters.emotions.length) params.append('emotions', rtFilters.emotions.join(','))
                          if (rtFilters.ageMin) params.append('age_min', rtFilters.ageMin.toString())
                          if (rtFilters.ageMax) params.append('age_max', rtFilters.ageMax.toString())
                          if (rtFilters.gender) params.append('gender', rtFilters.gender)
                          if (rtFilters.year) params.append('year', rtFilters.year)
                          if (rtFilters.sourceId) params.append('source_id', rtFilters.sourceId)
                          
                          const res = await fetch(`http://localhost:3001/api/real-talk/entries?${params}`)
                          const data = await res.json()
                          setRtEntries(data.entries || [])
                        } catch (err) {
                          console.error('Failed to fetch entries:', err)
                        } finally {
                          setRtLoading(false)
                        }
                      }}
                      className="rt-search-btn"
                      disabled={rtLoading}
                    >
                      {rtLoading ? 'Loading...' : 'Search'}
                    </button>
                  </div>

                  {/* Filter Row */}
                  <div className="rt-filters-row">
                    {/* Situations */}
                    <div className="rt-filter-group">
                      <label>Situations:</label>
                      <div className="rt-tag-buttons">
                        {rtSituationTags.map(tag => (
                          <button
                            key={tag.id}
                            className={`rt-tag-btn ${rtFilters.situations.includes(tag.tag_name) ? 'active' : ''}`}
                            onClick={() => {
                              setRtFilters(prev => ({
                                ...prev,
                                situations: prev.situations.includes(tag.tag_name)
                                  ? prev.situations.filter(t => t !== tag.tag_name)
                                  : [...prev.situations, tag.tag_name]
                              }))
                            }}
                          >
                            {tag.tag_name.replace(/_/g, ' ')} ({tag.usage_count})
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Emotions */}
                    <div className="rt-filter-group">
                      <label>Emotions:</label>
                      <div className="rt-tag-buttons">
                        {rtEmotionTags.map(tag => (
                          <button
                            key={tag.id}
                            className={`rt-tag-btn ${rtFilters.emotions.includes(tag.tag_name) ? 'active' : ''}`}
                            onClick={() => {
                              setRtFilters(prev => ({
                                ...prev,
                                emotions: prev.emotions.includes(tag.tag_name)
                                  ? prev.emotions.filter(t => t !== tag.tag_name)
                                  : [...prev.emotions, tag.tag_name]
                              }))
                            }}
                          >
                            {tag.tag_name} ({tag.usage_count})
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Demographics */}
                    <div className="rt-filter-group rt-demographics">
                      <label>Demographics:</label>
                      <div className="rt-demo-inputs">
                        <input
                          type="number"
                          placeholder="Age min"
                          value={rtFilters.ageMin || ''}
                          onChange={(e) => setRtFilters({...rtFilters, ageMin: e.target.value ? parseInt(e.target.value) : undefined})}
                          className="rt-age-input"
                        />
                        <span>-</span>
                        <input
                          type="number"
                          placeholder="Age max"
                          value={rtFilters.ageMax || ''}
                          onChange={(e) => setRtFilters({...rtFilters, ageMax: e.target.value ? parseInt(e.target.value) : undefined})}
                          className="rt-age-input"
                        />
                        <select 
                          value={rtFilters.gender}
                          onChange={(e) => setRtFilters({...rtFilters, gender: e.target.value})}
                          className="rt-gender-select"
                        >
                          <option value="">Any Gender</option>
                          <option value="M">Male</option>
                          <option value="F">Female</option>
                        </select>
                        <select 
                          value={rtFilters.year}
                          onChange={(e) => setRtFilters({...rtFilters, year: e.target.value})}
                          className="rt-year-select"
                        >
                          <option value="">Any Year</option>
                          <option value="2025">2025</option>
                          <option value="2024">2024</option>
                          <option value="2023">2023</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* AI Intelligent Search */}
                  <div className="rt-ai-search">
                    <label>AI Intelligent Search (optional):</label>
                    <div className="rt-ai-row">
                      <input
                        type="text"
                        placeholder="e.g., 'moment of realization they were wrong', 'missing someone late at night'"
                        value={rtAiQuery}
                        onChange={(e) => setRtAiQuery(e.target.value)}
                        className="rt-ai-input"
                      />
                      <select
                        value={rtAiLimit}
                        onChange={(e) => setRtAiLimit(parseInt(e.target.value))}
                        className="rt-ai-limit"
                      >
                        <option value={50}>50 (~10s)</option>
                        <option value={100}>100 (~20s)</option>
                        <option value={200}>200 (~40s)</option>
                      </select>
                      <button
                        onClick={async () => {
                          if (!rtAiQuery.trim()) return
                          setRtAiSearching(true)
                          try {
                            // First get filtered entries
                            const params = new URLSearchParams()
                            if (rtFilters.situations.length) params.append('situations', rtFilters.situations.join(','))
                            if (rtFilters.emotions.length) params.append('emotions', rtFilters.emotions.join(','))
                            if (rtFilters.ageMin) params.append('age_min', rtFilters.ageMin.toString())
                            if (rtFilters.ageMax) params.append('age_max', rtFilters.ageMax.toString())
                            if (rtFilters.gender) params.append('gender', rtFilters.gender)
                            params.append('limit', '200')
                            
                            const entriesRes = await fetch(`http://localhost:3001/api/real-talk/entries?${params}`)
                            const entriesData = await entriesRes.json()
                            
                            // Then run AI search
                            const aiRes = await fetch(`${API_URL}/api/real-talk/intelligent-search`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({
                                query: rtAiQuery,
                                entries: entriesData.entries || [],
                                limit: rtAiLimit
                              })
                            })
                            const aiData = await aiRes.json()
                            setRtEntries(aiData.results || [])
                          } catch (err) {
                            console.error('AI search failed:', err)
                          } finally {
                            setRtAiSearching(false)
                          }
                        }}
                        disabled={rtAiSearching || !rtAiQuery.trim()}
                        className="rt-ai-btn"
                      >
                        {rtAiSearching ? 'Searching...' : '✨ Find with AI'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Results */}
                <div className="rt-results">
                  {rtLoading && <div className="rt-loading">Loading conversations...</div>}
                  
                  {!rtLoading && rtEntries.length === 0 && (
                    <div className="rt-empty">
                      <p>No conversations yet. Add some subreddits in the Manage Sources tab to get started!</p>
                    </div>
                  )}

                  {!rtLoading && rtEntries.map(entry => (
                    <div 
                      key={entry.id} 
                      className={`rt-entry-card ${rtExpandedEntry === entry.id ? 'expanded' : ''}`}
                    >
                      <div className="rt-entry-header" onClick={() => setRtExpandedEntry(rtExpandedEntry === entry.id ? null : entry.id)}>
                        <div className="rt-entry-title">
                          <h3>{entry.title || 'Untitled'}</h3>
                          {entry.relevance_score && (
                            <span className="rt-relevance">AI Score: {entry.relevance_score}/10</span>
                          )}
                        </div>
                        <div className="rt-entry-meta">
                          {entry.poster_age && entry.poster_gender && (
                            <span className="rt-demo-badge">{entry.poster_age}{entry.poster_gender}</span>
                          )}
                          {entry.other_party_age && entry.other_party_gender && (
                            <span className="rt-demo-badge other">{entry.other_party_age}{entry.other_party_gender}</span>
                          )}
                          <span className="rt-source">{entry.real_talk_sources?.display_name || 'Reddit'}</span>
                          <span className="rt-date">{new Date(entry.posted_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <div className="rt-entry-tags">
                        {entry.situation_tags?.map(tag => (
                          <span key={tag} className="rt-tag situation">{tag.replace(/_/g, ' ')}</span>
                        ))}
                        {entry.emotional_tags?.map(tag => (
                          <span key={tag} className="rt-tag emotion">{tag}</span>
                        ))}
                      </div>

                      {entry.relevance_reason && (
                        <div className="rt-relevance-reason">{entry.relevance_reason}</div>
                      )}

                      <div className="rt-entry-excerpt">
                        {rtExpandedEntry === entry.id 
                          ? entry.raw_text 
                          : entry.raw_text.slice(0, 300) + (entry.raw_text.length > 300 ? '...' : '')
                        }
                      </div>

                      {entry.url && (
                        <a href={entry.url} target="_blank" rel="noopener noreferrer" className="rt-link">
                          View on Reddit →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Manage Tab */}
            {rtTab === 'manage' && (
              <div className="rt-manage">
                {/* Add Source Section */}
                <div className="rt-section">
                  <h2>Add Subreddit</h2>
                  <div className="rt-add-source">
                    <input
                      type="text"
                      placeholder="e.g., relationships, BreakUps, dating_advice"
                      value={rtNewSubreddit}
                      onChange={(e) => setRtNewSubreddit(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !rtAddingSource && handleAddSource()}
                    />
                    <button 
                      onClick={handleAddSource}
                      disabled={rtAddingSource || !rtNewSubreddit.trim()}
                    >
                      {rtAddingSource ? 'Adding...' : 'Add Subreddit'}
                    </button>
                  </div>
                </div>

                {/* Add YouTube Video Section */}
                <div className="rt-section">
                  <h2>Add YouTube Video</h2>
                  <p style={{color: '#888', fontSize: '13px', marginBottom: '12px'}}>
                    Scrapes transcripts from YouTube videos (no API key needed!)
                  </p>
                  <div className="rt-add-source">
                    <input
                      type="text"
                      placeholder="Paste YouTube video URL here..."
                      value={rtNewYoutubeUrl}
                      onChange={(e) => setRtNewYoutubeUrl(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !rtAddingYoutube && handleAddYoutubeVideo()}
                    />
                    <button 
                      onClick={handleAddYoutubeVideo}
                      disabled={rtAddingYoutube || !rtNewYoutubeUrl.trim()}
                    >
                      {rtAddingYoutube ? 'Scraping...' : 'Add & Scrape Video'}
                    </button>
                  </div>

                {/* Add YouTube Channel Section */}
                <div className="rt-section">
                  <h2>Add YouTube Channel (Bulk Import)</h2>
                  <p style={{color: '#888', fontSize: '13px', marginBottom: '12px'}}>
                    Scrapes ALL videos from a channel (no API key!)
                  </p>
                  <div className="rt-add-source">
                    <input
                      type="text"
                      placeholder="e.g., youtube.com/@podcrushed"
                      value={rtNewChannelUrl}
                      onChange={(e) => setRtNewChannelUrl(e.target.value)}
                      style={{flex: 2}}
                    />
                    <select 
                      value={rtChannelLimit}
                      onChange={(e) => setRtChannelLimit(parseInt(e.target.value))}
                      style={{
                        padding: '12px',
                        background: '#222',
                        border: '1px solid #333',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '14px'
                      }}
                    >
                      <option value={10}>10 videos</option>
                      <option value={25}>25 videos</option>
                      <option value={50}>50 videos</option>
                      <option value={100}>100 videos</option>
                    </select>
                    <button 
                      onClick={handleAddYoutubeChannel}
                      disabled={rtScrapingChannel || !rtNewChannelUrl.trim()}
                      style={{whiteSpace: 'nowrap'}}
                    >
                      {rtScrapingChannel ? 'Scraping...' : 'Scrape Channel'}
                    </button>
                  </div>
                  <p style={{color: '#666', fontSize: '12px', marginTop: '8px'}}>
                    ⚠️ Takes ~2 seconds per video. 50 videos = ~2 minutes.
                  </p>
                </div>
                </div>

                {/* Sources List */}
                <div className="rt-section">
                  <div className="rt-section-header">
                    <h2>Sources ({rtSources.length})</h2>
                    <button 
                      onClick={handleScrapeAll}
                      disabled={rtScrapingAll || rtSources.filter(s => s.is_active).length === 0}
                      className="rt-scrape-all-btn"
                    >
                      {rtScrapingAll ? 'Scraping...' : 'Scrape All Active'}
                    </button>
                  </div>

                  <div className="rt-sources-list">
                    {rtSources.map(source => (
                      <div key={source.id} className={`rt-source-card ${source.is_active ? 'active' : 'inactive'}`}>
                        <div className="rt-source-info">
                          <h3>{source.display_name}</h3>
                          <div className="rt-source-stats">
                            <span>{source.total_entries} entries</span>
                            {source.last_scraped_at && (
                              <span>Last scraped: {new Date(source.last_scraped_at).toLocaleDateString()}</span>
                            )}
                          </div>
                        </div>
                        <div className="rt-source-actions">
                          <label className="rt-toggle">
                            <input
                              type="checkbox"
                              checked={source.is_active}
                              onChange={async () => {
                                try {
                                  await fetch(`http://localhost:3001/api/real-talk/sources/${source.id}/toggle`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ is_active: !source.is_active })
                                  })
                                  setRtSources(prev => prev.map(s => 
                                    s.id === source.id ? {...s, is_active: !s.is_active} : s
                                  ))
                                } catch (err) {
                                  console.error('Failed to toggle source:', err)
                                }
                              }}
                            />
                            <span className="rt-toggle-slider"></span>
                          </label>
                          <button
                            onClick={() => handleScrapeSource(source.id, source.source_type, source.source_identifier)}
                            disabled={rtScraping === source.id || source.source_type === 'youtube_video'}
                            className="rt-scrape-btn"
                          >
                            {source.source_type === 'youtube_video' ? 'Already Scraped' : rtScraping === source.id ? 'Scraping...' : 'Scrape Now'}
                          </button>
                          <button
                            onClick={async () => {
                              if (!confirm(`Delete ${source.display_name} and all its entries?`)) return
                              try {
                                await fetch(`http://localhost:3001/api/real-talk/sources/${source.id}`, {
                                  method: 'DELETE'
                                })
                                setRtSources(prev => prev.filter(s => s.id !== source.id))
                              } catch (err) {
                                console.error('Failed to delete source:', err)
                              }
                            }}
                            className="rt-delete-btn"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                    ))}

                    {rtSources.length === 0 && (
                      <div className="rt-no-sources">
                        <p>No sources added yet. Add a subreddit above to get started!</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Tag Management */}
                <div className="rt-section">
                  <h2>Situation Tags</h2>
                  <div className="rt-tags-manage">
                    <div className="rt-add-tag">
                      <input
                        type="text"
                        placeholder="Add new situation tag..."
                        value={rtNewSituationTag}
                        onChange={(e) => setRtNewSituationTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag('situation', rtNewSituationTag)}
                      />
                      <button onClick={() => handleAddTag('situation', rtNewSituationTag)}>Add</button>
                    </div>
                    <div className="rt-tag-list">
                      {rtSituationTags.map(tag => (
                        <div key={tag.id} className="rt-tag-item">
                          <span>{tag.tag_name.replace(/_/g, ' ')}</span>
                          <span className="rt-tag-count">({tag.usage_count})</span>
                          <button onClick={() => handleDeleteTag(tag.id)} className="rt-tag-delete">×</button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rt-section">
                  <h2>Emotion Tags</h2>
                  <div className="rt-tags-manage">
                    <div className="rt-add-tag">
                      <input
                        type="text"
                        placeholder="Add new emotion tag..."
                        value={rtNewEmotionTag}
                        onChange={(e) => setRtNewEmotionTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag('emotion', rtNewEmotionTag)}
                      />
                      <button onClick={() => handleAddTag('emotion', rtNewEmotionTag)}>Add</button>
                    </div>
                    <div className="rt-tag-list">
                      {rtEmotionTags.map(tag => (
                        <div key={tag.id} className="rt-tag-item">
                          <span>{tag.tag_name}</span>
                          <span className="rt-tag-count">({tag.usage_count})</span>
                          <button onClick={() => handleDeleteTag(tag.id)} className="rt-tag-delete">×</button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Melody Page */}
        {currentPage === 'melody' && (
          <div className="content-wrapper">
            <div className="content">
              <h1>Melody</h1>
              <p className="page-description">Find mashup-compatible tracks by chord progression and tempo</p>

              {/* Tidal Connection Status */}
              {!melodyTidalAuth && (
                <div className="melody-auth-banner">
                  <p>⚠️ Connect to Tidal to search tracks and create playlists</p>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="primary-button" onClick={handleMelodyConnectTidal}>
                      Connect to Tidal
                    </button>
                    <button 
                      className="secondary-button" 
                      onClick={checkMelodyTidalStatus}
                      title="Refresh connection status"
                    >
                      🔄 Refresh
                    </button>
                  </div>
                </div>
              )}

              {melodyTidalAuth && (
                <div className="melody-auth-banner success">
                  <p>✅ Connected to Tidal</p>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button 
                      className="secondary-button" 
                      onClick={checkMelodyTidalStatus}
                      title="Refresh connection status"
                    >
                      🔄 Refresh
                    </button>
                    <button 
                      className="secondary-button" 
                      onClick={handleMelodyDisconnectTidal}
                      title="Disconnect from Tidal"
                      style={{ background: '#5a2a2a', borderColor: '#7a3a3a' }}
                    >
                      🔌 Disconnect
                    </button>
                  </div>
                </div>
              )}

              {/* Search Form */}
              <div className="melody-search-form">
                <div className="melody-form-row">
                  <div className="melody-input-group">
                    <label>Chord Progression</label>
                    <input
                      type="text"
                      placeholder="e.g., Am C F G"
                      value={melodyChords}
                      onChange={(e) => setMelodyChords(e.target.value)}
                      disabled={!melodyTidalAuth}
                    />
                    <small>Supports: Am, C, F, G or vi, I, IV, V</small>
                  </div>

                  <div className="melody-input-group">
                    <label>Target BPM</label>
                    <input
                      type="number"
                      value={melodyBpm}
                      onChange={(e) => setMelodyBpm(Number(e.target.value))}
                      disabled={!melodyTidalAuth}
                    />
                  </div>

                  <div className="melody-input-group">
                    <label>BPM Tolerance (±)</label>
                    <input
                      type="number"
                      value={melodyBpmTolerance}
                      onChange={(e) => setMelodyBpmTolerance(Number(e.target.value))}
                      disabled={!melodyTidalAuth}
                    />
                  </div>

                  <div className="melody-input-group">
                    <label>Time Signature</label>
                    <select
                      value={melodyTimeSig}
                      onChange={(e) => setMelodyTimeSig(e.target.value)}
                      disabled={!melodyTidalAuth}
                    >
                      <option value="4/4">4/4</option>
                      <option value="3/4">3/4</option>
                      <option value="6/8">6/8</option>
                    </select>
                  </div>
                </div>

                <div className="melody-form-row">
                  <div className="melody-input-group">
                    <label>Year Range</label>
                    <div className="melody-year-range">
                      <input
                        type="number"
                        placeholder="From"
                        value={melodyYearStart}
                        onChange={(e) => setMelodyYearStart(Number(e.target.value))}
                        disabled={!melodyTidalAuth}
                      />
                      <span>to</span>
                      <input
                        type="number"
                        placeholder="To"
                        value={melodyYearEnd}
                        onChange={(e) => setMelodyYearEnd(Number(e.target.value))}
                        disabled={!melodyTidalAuth}
                      />
                    </div>
                  </div>

                  <div className="melody-input-group">
                    <label>Chart (optional)</label>
                    <input
                      type="text"
                      placeholder="e.g., Billboard Hot 100"
                      value={melodyChart}
                      onChange={(e) => setMelodyChart(e.target.value)}
                      disabled={!melodyTidalAuth}
                    />
                  </div>

                  <div className="melody-input-group">
                    <label>Artist Style (optional)</label>
                    <input
                      type="text"
                      placeholder="e.g., similar to Drake"
                      value={melodyArtistStyle}
                      onChange={(e) => setMelodyArtistStyle(e.target.value)}
                      disabled={!melodyTidalAuth}
                    />
                  </div>
                </div>

                <button
                  className="primary-button melody-search-btn"
                  onClick={handleMelodySearch}
                  disabled={!melodyTidalAuth || melodySearching}
                >
                  {melodySearching ? 'Searching...' : '🔍 Find Mashups'}
                </button>
              </div>

              {/* Results */}
              {melodyResults.length > 0 && (
                <div className="melody-results">
                  <div className="melody-results-header">
                    <h2>Matches ({melodyResults.length})</h2>
                    <div className="melody-playlist-controls">
                      <input
                        type="text"
                        placeholder="Playlist name (optional)"
                        value={melodyPlaylistName}
                        onChange={(e) => setMelodyPlaylistName(e.target.value)}
                      />
                      <button
                        className="primary-button"
                        onClick={handleMelodyCreatePlaylist}
                        disabled={melodyCreatingPlaylist || melodySelectedTracks.size === 0}
                      >
                        {melodyCreatingPlaylist ? 'Creating...' : `🎵 Create Playlist (${melodySelectedTracks.size})`}
                      </button>
                    </div>
                  </div>

                  <div className="melody-matches-grid">
                    {melodyResults.map((match) => (
                      <div key={match.tidal_id} className="melody-match-card">
                        <div className="melody-match-header">
                          <input
                            type="checkbox"
                            checked={melodySelectedTracks.has(match.tidal_id)}
                            onChange={(e) => {
                              const newSet = new Set(melodySelectedTracks)
                              if (e.target.checked) {
                                newSet.add(match.tidal_id)
                              } else {
                                newSet.delete(match.tidal_id)
                              }
                              setMelodySelectedTracks(newSet)
                            }}
                          />
                          <div className="melody-match-info">
                            <h3>{match.title}</h3>
                            <p className="melody-artist">{match.artist}</p>
                          </div>
                        </div>

                        <div className="melody-match-details">
                          <div className="melody-detail">
                            <span className="label">Key:</span>
                            <span className="value">{match.original_key}</span>
                          </div>
                          <div className="melody-detail">
                            <span className="label">BPM:</span>
                            <span className="value">{match.bpm}</span>
                          </div>
                          <div className="melody-detail">
                            <span className="label">Transpose:</span>
                            <span className={`value transpose ${match.transpose_semitones === 0 ? 'perfect' : ''}`}>
                              {match.transpose_semitones === 0 ? '✓ Perfect!' : `${match.transpose_semitones > 0 ? '+' : ''}${match.transpose_semitones}`}
                            </span>
                          </div>
                          <div className="melody-detail">
                            <span className="label">Match Score:</span>
                            <span className="value">{match.match_score}/100</span>
                          </div>
                        </div>

                        <div className="melody-match-reason">
                          <small>{match.claude_reason}</small>
                        </div>

                        <a href={match.tidal_url} target="_blank" rel="noopener noreferrer" className="melody-tidal-link">
                          View on Tidal →
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {melodyResults.length === 0 && melodySearching === false && melodyTidalAuth && (
                <div className="melody-empty-state">
                  <p>Enter a chord progression and click "Find Mashups" to get started!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Filter Sidebar */}
      <FilterSidebar 
        isOpen={filterSidebarOpen}
        onClose={() => setFilterSidebarOpen(false)}
        filters={filters}
        onChange={setFilters}
        mode={searchMode}
      />

      {/* Lyrics Modal */}
      {showLyricsModal && (
        <div className="modal-overlay" onClick={() => setShowLyricsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{modalSongTitle}</h2>
              <div className="modal-actions">
                {modalHighlightWords.length > 0 && (
                  <button 
                    className="view-toggle-btn"
                    onClick={() => setModalViewMode(modalViewMode === 'context' ? 'full' : 'context')}
                  >
                    {modalViewMode === 'context' ? 'View Full Song' : 'View in Context'}
                  </button>
                )}
                <button className="modal-close" onClick={() => setShowLyricsModal(false)}>×</button>
              </div>
            </div>
            <div className="modal-body">
              {/* Show rhyme path if in context mode and we have multiple words */}
              {modalViewMode === 'context' && modalHighlightWords.length > 1 && (
                <div className="rhyme-path">
                  {modalHighlightWords.map((word, idx) => (
                    <span key={idx}>
                      {idx > 0 && <span className="path-arrow"> → </span>}
                      <span className="path-word">{word}</span>
                    </span>
                  ))}
                </div>
              )}
              
              {modalViewMode === 'full' ? (
                <pre className="lyrics-display" dangerouslySetInnerHTML={{ 
                  __html: modalHighlightWords.length > 0
                    ? modalHighlightWords.reduce((text, word) => {
                        return text.replace(
                          new RegExp(`\\b(${word})\\b`, 'gi'),
                          '<strong>$1</strong>'
                        )
                      }, modalLyrics)
                    : modalLyrics
                }} />
              ) : (
                <div className="context-view">
                  {modalHighlightWords.length > 0 && getContextView(modalLyrics, modalHighlightWords).map((ctx, idx) => {
                    // Highlight all words in the chain
                    let highlightedLine = ctx.matchLine
                    modalHighlightWords.forEach(word => {
                      highlightedLine = highlightedLine.replace(
                        new RegExp(`\\b(${word})\\b`, 'gi'),
                        '<strong>$1</strong>'
                      )
                    })
                    
                    return (
                      <div key={idx} className="context-block">
                        {ctx.linesBefore.map((line, i) => (
                          <div key={`before-${i}`} className="context-line">{line}</div>
                        ))}
                        <div className="match-line" dangerouslySetInnerHTML={{ __html: highlightedLine }} />
                        {ctx.linesAfter.map((line, i) => (
                          <div key={`after-${i}`} className="context-line">{line}</div>
                        ))}
                        <div className="context-divider" />
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
