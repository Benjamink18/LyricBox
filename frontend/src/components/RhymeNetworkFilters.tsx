import { useState, useEffect } from 'react'
import type { RhymeNetworkFilters } from '../lib/supabase'
import { getDistinctGenres, getDistinctYears, getDistinctArtists } from '../lib/supabase'

interface RhymeNetworkFiltersProps {
  filters: RhymeNetworkFilters
  onChange: (filters: RhymeNetworkFilters) => void
}

const RHYME_TYPES = [
  { value: 'perfect', label: 'Perfect', emoji: '🎯' },
  { value: 'multi', label: 'Multi', emoji: '🎼' },
  { value: 'compound', label: 'Compound', emoji: '🔗' },
  { value: 'assonance', label: 'Assonance', emoji: '🎵' },
  { value: 'consonance', label: 'Consonance', emoji: '🎶' },
  { value: 'slant', label: 'Slant', emoji: '〰️' },
  { value: 'embedded', label: 'Embedded', emoji: '📦' }
]

const MAIN_GENRES = [
  'Hip-Hop',
  'Pop',
  'R&B',
  'Rock',
  'Country',
  'Electronic',
  'Alternative'
]

const DEPTH_OPTIONS = [
  { value: 1, label: 'Depth 1 (Obvious)' },
  { value: 2, label: 'Depth 2 (Creative)' },
  { value: 3, label: 'Depth 3 (Rare)' }
]

export function RhymeNetworkFilters({ filters, onChange }: RhymeNetworkFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [allGenres, setAllGenres] = useState<string[]>([])
  const [allYears, setAllYears] = useState<number[]>([])
  const [allArtists, setAllArtists] = useState<string[]>([])
  const [genreSearch, setGenreSearch] = useState('')
  const [artistSearch, setArtistSearch] = useState('')

  useEffect(() => {
    // Load available options from database
    Promise.all([
      getDistinctGenres(),
      getDistinctYears(),
      getDistinctArtists()
    ]).then(([genres, years, artists]) => {
      setAllGenres(genres)
      setAllYears(years)
      setAllArtists(artists)
    })
  }, [])

  const toggleRhymeType = (type: string) => {
    const current = filters.rhymeTypes || []
    const updated = current.includes(type)
      ? current.filter(t => t !== type)
      : [...current, type]
    onChange({ ...filters, rhymeTypes: updated.length > 0 ? updated : undefined })
  }

  const toggleMainGenre = (genre: string) => {
    const current = filters.genres || []
    const updated = current.includes(genre)
      ? current.filter(g => g !== genre)
      : [...current, genre]
    onChange({ ...filters, genres: updated.length > 0 ? updated : undefined })
  }

  const addGenre = (genre: string) => {
    const current = filters.genres || []
    if (!current.includes(genre)) {
      onChange({ ...filters, genres: [...current, genre] })
    }
    setGenreSearch('')
  }

  const removeGenre = (genre: string) => {
    const current = filters.genres || []
    const updated = current.filter(g => g !== genre)
    onChange({ ...filters, genres: updated.length > 0 ? updated : undefined })
  }

  const toggleYear = (year: number) => {
    const current = filters.years || []
    const updated = current.includes(year)
      ? current.filter(y => y !== year)
      : [...current, year]
    onChange({ ...filters, years: updated.length > 0 ? updated : undefined })
  }

  const addArtist = (artist: string) => {
    const current = filters.artists || []
    if (!current.includes(artist)) {
      onChange({ ...filters, artists: [...current, artist] })
    }
    setArtistSearch('')
  }

  const removeArtist = (artist: string) => {
    const current = filters.artists || []
    const updated = current.filter(a => a !== artist)
    onChange({ ...filters, artists: updated.length > 0 ? updated : undefined })
  }

  const toggleDepth = (depth: number) => {
    const current = filters.depths || []
    const updated = current.includes(depth)
      ? current.filter(d => d !== depth)
      : [...current, depth]
    onChange({ ...filters, depths: updated.length > 0 ? updated : undefined })
  }

  const setRankRange = (min: number, max: number) => {
    onChange({
      ...filters,
      minRank: min > 1 ? min : undefined,
      maxRank: max < 100 ? max : undefined
    })
  }

  const clearAllFilters = () => {
    onChange({})
  }

  const activeFilterCount = 
    (filters.rhymeTypes?.length || 0) +
    (filters.genres?.length || 0) +
    (filters.years?.length || 0) +
    (filters.artists?.length || 0) +
    (filters.depths?.length || 0) +
    (filters.minRank ? 1 : 0) +
    (filters.maxRank ? 1 : 0) +
    (filters.minFrequency ? 1 : 0)

  const filteredGenres = allGenres.filter(g => 
    g.toLowerCase().includes(genreSearch.toLowerCase())
  )

  const filteredArtists = allArtists.filter(a =>
    a.toLowerCase().includes(artistSearch.toLowerCase())
  )

  return (
    <div className="rhyme-network-filters">
      <div className="filter-header">
        <h3>Filters</h3>
        {activeFilterCount > 0 && (
          <div className="filter-actions">
            <span className="active-count">{activeFilterCount} active</span>
            <button onClick={clearAllFilters} className="clear-btn">Clear All</button>
          </div>
        )}
      </div>

      {/* Rhyme Types */}
      <div className="filter-section">
        <label>Rhyme Types</label>
        <div className="rhyme-type-buttons">
          {RHYME_TYPES.map(({ value, label, emoji }) => (
            <button
              key={value}
              onClick={() => toggleRhymeType(value)}
              className={`rhyme-type-btn ${filters.rhymeTypes?.includes(value) ? 'active' : ''}`}
              title={label}
            >
              <span className="emoji">{emoji}</span>
              <span className="label">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Depth Layers */}
      <div className="filter-section">
        <label>Depth Layers</label>
        <div className="depth-buttons">
          {DEPTH_OPTIONS.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => toggleDepth(value)}
              className={`depth-btn ${filters.depths?.includes(value) ? 'active' : ''}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Billboard Rank */}
      <div className="filter-section">
        <label>Billboard Rank</label>
        <div className="rank-slider">
          <input
            type="range"
            min="1"
            max="100"
            value={filters.minRank || 1}
            onChange={(e) => setRankRange(Number(e.target.value), filters.maxRank || 100)}
          />
          <input
            type="range"
            min="1"
            max="100"
            value={filters.maxRank || 100}
            onChange={(e) => setRankRange(filters.minRank || 1, Number(e.target.value))}
          />
          <div className="rank-display">
            #{filters.minRank || 1} - #{filters.maxRank || 100}
          </div>
        </div>
      </div>

      {/* Main Genres */}
      <div className="filter-section">
        <label>Main Genres</label>
        <div className="genre-buttons">
          {MAIN_GENRES.map(genre => (
            <button
              key={genre}
              onClick={() => toggleMainGenre(genre)}
              className={`genre-btn ${filters.genres?.includes(genre) ? 'active' : ''}`}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Filters */}
      <button
        className="advanced-toggle"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? '▼' : '▶'} Advanced Filters
      </button>

      {showAdvanced && (
        <div className="advanced-filters">
          {/* Detailed Genre Search */}
          <div className="filter-section">
            <label>Search Genres</label>
            <input
              type="text"
              placeholder="Type to search genres..."
              value={genreSearch}
              onChange={(e) => setGenreSearch(e.target.value)}
              className="search-input"
            />
            {genreSearch && filteredGenres.length > 0 && (
              <div className="autocomplete-results">
                {filteredGenres.slice(0, 10).map(genre => (
                  <div
                    key={genre}
                    onClick={() => addGenre(genre)}
                    className="autocomplete-item"
                  >
                    {genre}
                  </div>
                ))}
              </div>
            )}
            {filters.genres && filters.genres.length > 0 && (
              <div className="selected-tags">
                {filters.genres.map(genre => (
                  <span key={genre} className="tag">
                    {genre}
                    <button onClick={() => removeGenre(genre)}>×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Year Selection */}
          <div className="filter-section">
            <label>Years</label>
            <div className="year-checkboxes">
              {allYears.map(year => (
                <label key={year} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.years?.includes(year) || false}
                    onChange={() => toggleYear(year)}
                  />
                  {year}
                </label>
              ))}
            </div>
          </div>

          {/* Artist Search */}
          <div className="filter-section">
            <label>Artists</label>
            <input
              type="text"
              placeholder="Type to search artists..."
              value={artistSearch}
              onChange={(e) => setArtistSearch(e.target.value)}
              className="search-input"
            />
            {artistSearch && filteredArtists.length > 0 && (
              <div className="autocomplete-results">
                {filteredArtists.slice(0, 10).map(artist => (
                  <div
                    key={artist}
                    onClick={() => addArtist(artist)}
                    className="autocomplete-item"
                  >
                    {artist}
                  </div>
                ))}
              </div>
            )}
            {filters.artists && filters.artists.length > 0 && (
              <div className="selected-tags">
                {filters.artists.map(artist => (
                  <span key={artist} className="tag">
                    {artist}
                    <button onClick={() => removeArtist(artist)}>×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Frequency Filter */}
          <div className="filter-section">
            <label>Minimum Frequency</label>
            <input
              type="range"
              min="1"
              max="20"
              value={filters.minFrequency || 1}
              onChange={(e) => onChange({ ...filters, minFrequency: Number(e.target.value) > 1 ? Number(e.target.value) : undefined })}
            />
            <div className="frequency-display">
              {filters.minFrequency || 1}+ occurrences
            </div>
          </div>
        </div>
      )}

      <style>{`
        .rhyme-network-filters {
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 8px;
          padding: 20px;
          margin: 16px 0;
        }

        .filter-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .filter-header h3 {
          margin: 0;
          font-size: 18px;
          color: #e0e0e0;
        }

        .filter-actions {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .active-count {
          background: #4a9eff;
          color: white;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .clear-btn {
          background: transparent;
          border: 1px solid #666;
          color: #e0e0e0;
          padding: 6px 12px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.2s;
        }

        .clear-btn:hover {
          background: #ff4444;
          border-color: #ff4444;
          color: white;
        }

        .filter-section {
          margin-bottom: 24px;
        }

        .filter-section label {
          display: block;
          color: #888;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 10px;
        }

        .rhyme-type-buttons,
        .genre-buttons,
        .depth-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .rhyme-type-btn,
        .genre-btn,
        .depth-btn {
          background: #2a2a2a;
          border: 1px solid #444;
          color: #e0e0e0;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .rhyme-type-btn:hover,
        .genre-btn:hover,
        .depth-btn:hover {
          background: #333;
          border-color: #666;
        }

        .rhyme-type-btn.active,
        .genre-btn.active,
        .depth-btn.active {
          background: #4a9eff;
          border-color: #4a9eff;
          color: white;
        }

        .rhyme-type-btn .emoji {
          font-size: 16px;
        }

        .rank-slider {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .rank-slider input[type="range"] {
          width: 100%;
        }

        .rank-display,
        .frequency-display {
          text-align: center;
          color: #4a9eff;
          font-size: 14px;
          font-weight: 600;
        }

        .advanced-toggle {
          background: transparent;
          border: none;
          color: #4a9eff;
          cursor: pointer;
          font-size: 14px;
          padding: 8px 0;
          width: 100%;
          text-align: left;
          transition: all 0.2s;
        }

        .advanced-toggle:hover {
          color: #6ab7ff;
        }

        .advanced-filters {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #333;
        }

        .search-input {
          width: 100%;
          background: #252525;
          border: 1px solid #3a3a3a;
          color: #e0e0e0;
          padding: 10px 12px;
          border-radius: 6px;
          font-size: 14px;
        }

        .search-input:focus {
          outline: none;
          border-color: #4a9eff;
        }

        .autocomplete-results {
          background: #252525;
          border: 1px solid #3a3a3a;
          border-radius: 6px;
          margin-top: 4px;
          max-height: 200px;
          overflow-y: auto;
        }

        .autocomplete-item {
          padding: 10px 12px;
          cursor: pointer;
          color: #e0e0e0;
          transition: background 0.2s;
        }

        .autocomplete-item:hover {
          background: #2d2d2d;
        }

        .selected-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 10px;
        }

        .tag {
          background: #4a9eff;
          color: white;
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 13px;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .tag button {
          background: transparent;
          border: none;
          color: white;
          cursor: pointer;
          font-size: 18px;
          padding: 0;
          width: 16px;
          height: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .tag button:hover {
          color: #ff4444;
        }

        .year-checkboxes {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #e0e0e0;
          font-size: 14px;
          cursor: pointer;
        }

        .checkbox-label input {
          cursor: pointer;
        }
      `}</style>
    </div>
  )
}





