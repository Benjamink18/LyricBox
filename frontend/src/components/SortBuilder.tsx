import { useState } from 'react'
import type { SortCriterion, SortField } from '../lib/supabase'

interface SortBuilderProps {
  sortOrder: SortCriterion[]
  onChange: (newOrder: SortCriterion[]) => void
}

const SORT_FIELDS: { field: SortField; label: string }[] = [
  { field: 'depth', label: 'Depth' },
  { field: 'rhyme_type', label: 'Rhyme Type' },
  { field: 'frequency', label: 'Frequency' },
  { field: 'alphabetical', label: 'A-Z' }
]

export function SortBuilder({ sortOrder, onChange }: SortBuilderProps) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)

  const getLabel = (criterion: SortCriterion): string => {
    const field = SORT_FIELDS.find(f => f.field === criterion.field)
    const direction = criterion.direction === 'asc' ? '↑' : '↓'
    return `${field?.label} ${direction}`
  }

  const addSort = (field: SortField) => {
    // Check if already exists
    const existing = sortOrder.find(s => s.field === field)
    if (existing) {
      // Toggle direction
      const newOrder = sortOrder.map(s =>
        s.field === field
          ? { ...s, direction: s.direction === 'asc' ? 'desc' : 'asc' as const }
          : s
      )
      onChange(newOrder)
    } else {
      // Add new criterion
      const fieldInfo = SORT_FIELDS.find(f => f.field === field)!
      const newCriterion: SortCriterion = {
        id: `${Date.now()}-${field}`,
        field,
        direction: field === 'depth' || field === 'frequency' ? 'desc' : 'asc',
        label: fieldInfo.label
      }
      onChange([...sortOrder, newCriterion])
    }
  }

  const removeSort = (id: string) => {
    onChange(sortOrder.filter(s => s.id !== id))
  }

  const handleDragStart = (index: number) => {
    setDraggedIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggedIndex === null || draggedIndex === index) return

    const newOrder = [...sortOrder]
    const draggedItem = newOrder[draggedIndex]
    newOrder.splice(draggedIndex, 1)
    newOrder.splice(index, 0, draggedItem)
    
    onChange(newOrder)
    setDraggedIndex(index)
  }

  const handleDragEnd = () => {
    setDraggedIndex(null)
  }

  const isActive = (field: SortField): boolean => {
    return sortOrder.some(s => s.field === field)
  }

  return (
    <div className="sort-builder">
      <div className="sort-controls">
        <div className="sort-buttons">
          {SORT_FIELDS.map(({ field, label }) => (
            <button
              key={field}
              onClick={() => addSort(field)}
              className={`sort-button ${isActive(field) ? 'active' : ''}`}
              title={isActive(field) ? 'Click to toggle direction' : 'Click to add'}
            >
              {label}
              {isActive(field) && (
                <span className="direction-indicator">
                  {sortOrder.find(s => s.field === field)?.direction === 'asc' ? ' ↑' : ' ↓'}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {sortOrder.length > 0 && (
        <div className="sort-chain">
          <div className="sort-chain-label">Sort Priority:</div>
          <div className="sort-items">
            {sortOrder.map((criterion, index) => (
              <div
                key={criterion.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
                className={`sort-item ${draggedIndex === index ? 'dragging' : ''}`}
              >
                <span className="sort-priority">{index + 1}</span>
                <span className="sort-label">{getLabel(criterion)}</span>
                <button
                  onClick={() => removeSort(criterion.id)}
                  className="remove-sort"
                  title="Remove"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {sortOrder.length === 0 && (
        <div className="sort-empty">
          Click a sort option to begin
        </div>
      )}

      <style>{`
        .sort-builder {
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 8px;
          padding: 16px;
          margin: 16px 0;
        }

        .sort-buttons {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          margin-bottom: 12px;
        }

        .sort-button {
          background: #2a2a2a;
          border: 1px solid #444;
          border-radius: 6px;
          color: #e0e0e0;
          padding: 8px 16px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .sort-button:hover {
          background: #333;
          border-color: #666;
        }

        .sort-button.active {
          background: #4a9eff;
          border-color: #4a9eff;
          color: white;
          font-weight: 500;
        }

        .sort-chain {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #333;
        }

        .sort-chain-label {
          font-size: 12px;
          color: #888;
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .sort-items {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .sort-item {
          display: flex;
          align-items: center;
          gap: 10px;
          background: #252525;
          border: 1px solid #3a3a3a;
          border-radius: 6px;
          padding: 10px 12px;
          cursor: move;
          transition: all 0.2s;
        }

        .sort-item:hover {
          background: #2d2d2d;
          border-color: #4a9eff;
        }

        .sort-item.dragging {
          opacity: 0.5;
          transform: scale(0.98);
        }

        .sort-priority {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background: #4a9eff;
          color: white;
          border-radius: 50%;
          font-size: 12px;
          font-weight: 600;
          flex-shrink: 0;
        }

        .sort-label {
          flex: 1;
          color: #e0e0e0;
          font-size: 14px;
        }

        .remove-sort {
          background: transparent;
          border: none;
          color: #888;
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: all 0.2s;
        }

        .remove-sort:hover {
          background: #ff4444;
          color: white;
        }

        .sort-empty {
          text-align: center;
          color: #666;
          padding: 20px;
          font-size: 14px;
        }

        .direction-indicator {
          font-weight: bold;
        }
      `}</style>
    </div>
  )
}

