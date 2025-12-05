# Log Files - Centralized in backend/logs/

**Location:** `/Users/benkohn/Desktop/LyricBox/backend/logs/`

All log files are centralized in the `backend/logs/` folder for easy access and review.

---

## 📝 Active Log Files

### 1. **metadata_not_found.txt**
**Created by:** `backend/data_enrichment/log_metadata_failures.py`  
**Purpose:** Logs songs where metadata fetch failed (no genres or no BPM)  
**Format:** `YYYY-MM-DD HH:MM:SS - Artist - Track (reason: no_genres|no_bpm)`

**Example:**
```
2024-12-05 14:30:15 - Unknown Artist - Test Song (reason: no_genres)
2024-12-05 14:30:20 - Another Artist - Song Title (reason: no_bpm)
```

**When to review:** After enrichment pipeline runs, to see which songs were skipped

---

### 2. **chords_not_found.txt**
**Created by:** `backend/ug_scraper/log_missing_chords.py`  
**Purpose:** Logs songs where Ultimate Guitar chords weren't found  
**Format:** `YYYY-MM-DD HH:MM:SS - Artist - Track`

**Example:**
```
2024-12-05 14:35:10 - D'Angelo - Spanish Joint
2024-12-05 14:35:15 - Obscure Band - Rare Song
```

**When to review:** 
- After chord scraping completes
- To identify songs that exist in DB but have no chords
- These songs won't have `musical_key` populated

---

## 🗑️ Removed/Unused Log Files

### ~~musicbrainz_partial_metadata.txt~~
**Status:** ❌ Removed (no longer used)  
**Why:** We removed MusicBrainz fallback logic  
**Old file:** Moved to `backend/unused/log_musicbrainz_partial.py`

---

## 📊 Log File Paths (Technical)

All log files use **relative paths** from where scripts run:

| Script Location | Log Path Used | Actual File Location |
|-----------------|---------------|---------------------|
| `backend/data_enrichment/*.py` | `../logs/*.txt` | `backend/logs/*.txt` |
| `backend/ug_scraper/*.py` | `../logs/*.txt` | `backend/logs/*.txt` |

**Why relative paths?** Scripts run from their own directories, so `../logs/` goes up one level to `backend/` then into `logs/`.

---

## 🔍 How to Review Logs

### View all logs:
```bash
cd /Users/benkohn/Desktop/LyricBox/backend/logs
ls -la *.txt
```

### View recent failures:
```bash
# Last 10 metadata failures
tail -10 metadata_not_found.txt

# Last 10 missing chords
tail -10 chords_not_found.txt
```

### Count failures by reason:
```bash
# Count genres failures
grep "no_genres" metadata_not_found.txt | wc -l

# Count BPM failures
grep "no_bpm" metadata_not_found.txt | wc -l
```

### Clear logs (before new test):
```bash
# Clear all logs
rm backend/logs/*.txt

# Or clear specific log
rm backend/logs/metadata_not_found.txt
```

---

## ✅ Log File Standards

All log files follow these standards:

1. **Location:** `backend/logs/` (centralized)
2. **Naming:** `descriptive_name.txt` (lowercase, underscores)
3. **Format:** Timestamp + Artist + Track + (optional reason)
4. **Append-only:** Never overwrite, always append
5. **UTF-8 encoding:** Support international characters

---

## 📋 Future Log Files (Planned)

If you add more data sources, create logs in the same location:

- `lyrics_not_found.txt` - If Genius scraping fails (not currently logged)
- `bpm_not_found.txt` - If GetSongBPM fails (when implemented)

**Pattern:** `{data_type}_not_found.txt`

---

## 🧹 Log Maintenance

### When to clear logs:
- Before running a fresh enrichment test
- After fixing data source issues
- When starting a new batch of songs

### When to keep logs:
- During active debugging
- To track recurring failures
- For historical analysis

### Backup important logs:
```bash
# Backup before clearing
cp backend/logs/metadata_not_found.txt backend/logs/metadata_not_found_backup_$(date +%Y%m%d).txt
```

---

## 🎯 Quick Reference

| Log File | Purpose | When Created |
|----------|---------|--------------|
| `metadata_not_found.txt` | Missing genres or BPM | Step 2 of enrichment |
| `chords_not_found.txt` | Missing UG chords | Step 4 of enrichment |

**All logs:**
- ✅ Centralized in `backend/logs/`
- ✅ Timestamped entries
- ✅ Easy to review
- ✅ Safe to delete between runs

