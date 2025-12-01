import { useState, useEffect } from 'react'
import { getDistinctGenres, getDistinctYears } from '../lib/supabase'
import type { RhymeNetworkFilters as RhymeNetworkFiltersType } from '../lib/supabase'

interface FilterSidebarProps {
  isOpen: boolean
  onClose: () => void
  filters: RhymeNetworkFiltersType
  onChange: (filters: RhymeNetworkFiltersType) => void
  mode: 'simple' | 'network'
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

export function FilterSidebar({ isOpen, onClose, filters, onChange, mode }: FilterSidebarProps) {
  const [allGenres, setAllGenres] = useState<string[]>([])
  const [allYears, setAllYears] = useState<number[]>([])
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['genres', 'years', 'rhymeTypes', 'depths', 'billboard'])
  )

  useEffect(() => {
    Promise.all([getDistinctGenres(), getDistinctYears()]).then(([genres, years]) => {
      const validGenres = genres.filter(g => g && g !== 'Unknown').sort()
      setAllGenres(validGenres)
      setAllYears(years)
    })
  }, [])

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(section)) {
        newSet.delete(section)
      } else {
        newSet.add(section)
      }
      return newSet
    })
  }

  const toggleRhymeType = (type: string) => {
    const current = filters.rhymeTypes || []
    const updated = current.includes(type)
      ? current.filter(t => t !== type)
      : [...current, type]
    onChange({ ...filters, rhymeTypes: updated.length > 0 ? updated : undefined })
  }

  const toggleGenre = (genre: string) => {
    const current = filters.genres || []
    const updated = current.includes(genre)
      ? current.filter(g => g !== genre)
      : [...current, genre]
    onChange({ ...filters, genres: updated.length > 0 ? updated : undefined })
  }

  const toggleYear = (year: number) => {
    const current = filters.years || []
    const updated = current.includes(year)
      ? current.filter(y => y !== year)
      : [...current, year]
    onChange({ ...filters, years: updated.length > 0 ? updated : undefined })
  }

  const toggleDepth = (depth: number) => {
    const current = filters.depths || []
    const updated = current.includes(depth)
      ? current.filter(d => d !== depth)
      : [...current, depth]
    onChange({ ...filters, depths: updated.length > 0 ? updated : undefined })
  }

  const updateRankRange = (min: number, max: number) => {
    onChange({ 
      ...filters, 
      minRank: min > 1 ? min : undefined,
      maxRank: max < 40 ? max : undefined
    })
  }

  const clearAll = () => {
    onChange({})
  }

  // Build list of active filters for display
  const getActiveFilters = (): Array<{ label: string; onRemove: () => void }> => {
    const active: Array<{ label: string; onRemove: () => void }> = []
    
    // Rhyme types
    filters.rhymeTypes?.forEach(type => {
      const rhyme = RHYME_TYPES.find(r => r.value === type)
      active.push({
        label: rhyme?.label || type,
        onRemove: () => toggleRhymeType(type)
      })
    })
    
    // Depths
    filters.depths?.forEach(depth => {
      active.push({
        label: `Depth ${depth}`,
        onRemove: () => toggleDepth(depth)
      })
    })
    
    // Genres
    filters.genres?.forEach(genre => {
      active.push({
        label: genre,
        onRemove: () => toggleGenre(genre)
      })
    })
    
    // Years
    filters.years?.forEach(year => {
      active.push({
        label: `${year}`,
        onRemove: () => toggleYear(year)
      })
    })
    
    // Billboard rank
    if (filters.minRank || filters.maxRank) {
      const min = filters.minRank || 1
      const max = filters.maxRank || 40
      if (min === 1 && max === 10) {
        active.push({ label: 'Top 10', onRemove: () => updateRankRange(1, 40) })
      } else if (min === 1 && max === 20) {
        active.push({ label: 'Top 20', onRemove: () => updateRankRange(1, 40) })
      } else {
        active.push({ label: `Rank ${min}-${max}`, onRemove: () => updateRankRange(1, 40) })
      }
    }
    
    return active
  }

  const activeFilters = getActiveFilters()

  return (
    <>
      {/* Overlay */}
      {isOpen && <div className="filter-overlay" onClick={onClose} />}
      
      {/* Sidebar */}
      <div className={`filter-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="filter-sidebar-header">
          <div className="header-content">
            <div className="header-top">
              <h2>Filters</h2>
              <button onClick={onClose} className="close-btn">×</button>
            </div>
            {activeFilters.length > 0 && (
              <div className="active-filters">
                {activeFilters.map((filter, idx) => (
                  <div key={idx} className="filter-tag" onClick={filter.onRemove}>
                    <span>{filter.label}</span>
                    <span className="filter-tag-x">×</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="filter-sidebar-content">
          {/* Rhyme Types - Network mode only */}
          {mode === 'network' && (
            <div className="filter-section">
              <h3 
                className="collapseable-header"
                onClick={() => toggleSection('rhymeTypes')}
              >
                <span>Rhyme Types</span>
                <span className="collapse-icon">{expandedSections.has('rhymeTypes') ? '−' : '+'}</span>
              </h3>
              {expandedSections.has('rhymeTypes') && (
                <div className="filter-grid">
                  {RHYME_TYPES.map(({ value, label, emoji }) => (
                    <button
                      key={value}
                      onClick={() => toggleRhymeType(value)}
                      className={`filter-btn ${filters.rhymeTypes?.includes(value) ? 'active' : ''}`}
                    >
                      <span className="filter-emoji">{emoji}</span>
                      <span>{label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Depth Layers - Network mode only */}
          {mode === 'network' && (
            <div className="filter-section">
              <h3 
                className="collapseable-header"
                onClick={() => toggleSection('depths')}
              >
                <span>Depth Layers</span>
                <span className="collapse-icon">{expandedSections.has('depths') ? '−' : '+'}</span>
              </h3>
              {expandedSections.has('depths') && (
                <div className="filter-grid">
                  {[1, 2, 3].map(depth => (
                    <button
                      key={depth}
                      onClick={() => toggleDepth(depth)}
                      className={`filter-btn ${filters.depths?.includes(depth) ? 'active' : ''}`}
                    >
                      Depth {depth}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Billboard Placement - Both modes */}
          <div className="filter-section">
            <h3 
              className="collapseable-header"
              onClick={() => toggleSection('billboard')}
            >
              <span>Billboard Rank</span>
              <span className="collapse-icon">{expandedSections.has('billboard') ? '−' : '+'}</span>
            </h3>
            {expandedSections.has('billboard') && (
              <div className="rank-slider-container">
                <div className="rank-labels">
                  <span>Best (1)</span>
                  <span>Worst (40)</span>
                </div>
                <div className="rank-inputs">
                  <div>
                    <label>Min Rank:</label>
                    <input
                      type="number"
                      min="1"
                      max="40"
                      value={filters.minRank || 1}
                      onChange={(e) => updateRankRange(parseInt(e.target.value), filters.maxRank || 40)}
                      className="rank-input"
                    />
                  </div>
                  <div>
                    <label>Max Rank:</label>
                    <input
                      type="number"
                      min="1"
                      max="40"
                      value={filters.maxRank || 40}
                      onChange={(e) => updateRankRange(filters.minRank || 1, parseInt(e.target.value))}
                      className="rank-input"
                    />
                  </div>
                </div>
                <div className="quick-ranks">
                  <button 
                    className="quick-rank-btn"
                    onClick={() => updateRankRange(1, 10)}
                  >
                    Top 10
                  </button>
                  <button 
                    className="quick-rank-btn"
                    onClick={() => updateRankRange(1, 20)}
                  >
                    Top 20
                  </button>
                  <button 
                    className="quick-rank-btn"
                    onClick={() => updateRankRange(1, 40)}
                  >
                    All
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Genres - Both modes */}
          <div className="filter-section">
            <h3 
              className="collapseable-header"
              onClick={() => toggleSection('genres')}
            >
              <span>Genres</span>
              <span className="collapse-icon">{expandedSections.has('genres') ? '−' : '+'}</span>
            </h3>
            {expandedSections.has('genres') && (
              <div className="filter-grid">
                {allGenres.map(genre => (
                  <button
                    key={genre}
                    onClick={() => toggleGenre(genre)}
                    className={`filter-btn ${filters.genres?.includes(genre) ? 'active' : ''}`}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Years - Both modes */}
          <div className="filter-section">
            <h3 
              className="collapseable-header"
              onClick={() => toggleSection('years')}
            >
              <span>Years</span>
              <span className="collapse-icon">{expandedSections.has('years') ? '−' : '+'}</span>
            </h3>
            {expandedSections.has('years') && (
              <div className="filter-grid year-grid">
                {allYears.map(year => (
                  <button
                    key={year}
                    onClick={() => toggleYear(year)}
                    className={`filter-btn ${filters.years?.includes(year) ? 'active' : ''}`}
                  >
                    {year}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="filter-sidebar-footer">
          <button onClick={clearAll} className="clear-all-btn">
            Clear All Filters
          </button>
        </div>

        <style>{`
          .filter-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            z-index: 998;
            animation: fadeIn 0.2s;
          }

          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }

          .filter-sidebar {
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100vh;
            background: #111;
            border-left: 1px solid #222;
            z-index: 999;
            display: flex;
            flex-direction: column;
            transition: right 0.3s ease;
          }

          .filter-sidebar.open {
            right: 0;
          }

          .filter-sidebar-header {
            padding: 24px;
            border-bottom: 1px solid #222;
          }

          .header-content {
            width: 100%;
          }

          .header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
          }

          .filter-sidebar-header h2 {
            font-size: 24px;
            margin: 0;
          }

          .active-filters {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 12px;
          }

          .filter-tag {
            background: #4a9eff;
            color: white;
            padding: 4px 8px 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 0.2s;
          }

          .filter-tag:hover {
            background: #3a8eef;
          }

          .filter-tag-x {
            font-size: 16px;
            font-weight: bold;
            opacity: 0.8;
          }

          .filter-tag:hover .filter-tag-x {
            opacity: 1;
          }

          .close-btn {
            background: transparent;
            border: none;
            color: #888;
            font-size: 36px;
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
          }

          .close-btn:hover {
            color: #e0e0e0;
          }

          .filter-sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
          }

          .filter-section {
            margin-bottom: 24px;
          }

          .collapseable-header {
            font-size: 13px;
            color: #e0e0e0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            transition: color 0.2s;
          }

          .collapseable-header:hover {
            color: #4a9eff;
          }

          .collapse-icon {
            font-size: 20px;
            font-weight: bold;
            color: #666;
          }

          .filter-section h3 {
            font-size: 13px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
          }

          .filter-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
          }

          .year-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .filter-btn {
            background: #1a1a1a;
            border: 1px solid #333;
            color: #e0e0e0;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
          }

          .filter-btn:hover {
            border-color: #4a9eff;
          }

          .filter-btn.active {
            background: #4a9eff;
            border-color: #4a9eff;
            color: white;
          }

          .filter-emoji {
            font-size: 16px;
          }

          .rank-slider-container {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 16px;
          }

          .rank-labels {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #666;
            margin-bottom: 12px;
          }

          .rank-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
          }

          .rank-inputs > div {
            display: flex;
            flex-direction: column;
            gap: 4px;
          }

          .rank-inputs label {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
          }

          .rank-input {
            background: #0a0a0a;
            border: 1px solid #333;
            color: #e0e0e0;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
            width: 100%;
          }

          .rank-input:focus {
            outline: none;
            border-color: #4a9eff;
          }

          .quick-ranks {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
          }

          .quick-rank-btn {
            background: #0a0a0a;
            border: 1px solid #333;
            color: #888;
            padding: 6px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s;
          }

          .quick-rank-btn:hover {
            border-color: #4a9eff;
            color: #4a9eff;
          }

          .filter-sidebar-footer {
            padding: 20px;
            border-top: 1px solid #222;
          }

          .clear-all-btn {
            width: 100%;
            background: transparent;
            border: 1px solid #ff4444;
            color: #ff4444;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
          }

          .clear-all-btn:hover {
            background: #ff4444;
            color: white;
          }
        `}</style>
      </div>
    </>
  )
}
