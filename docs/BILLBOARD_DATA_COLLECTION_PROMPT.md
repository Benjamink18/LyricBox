# Billboard Data Collection - Claude Prompt Template

**Purpose:** Collect Billboard Hot 100 debut songs year-by-year to avoid duplicates  
**Strategy:** Work backwards from 2025 to avoid Christmas song re-entries  
**Date:** December 5, 2024

---

## 🎯 **Claude Prompt Template:**

```
Billboard Hot 100 songs that DEBUTED in [YEAR] only. Exclude re-entries from prior years.

CSV format:
track_name,artist_name,peak_position,first_chart_date (YYYY-MM-DD)

Include header.
```

---

## 📋 **Usage Instructions:**

### **Step 1: Start with 2025**
```
Billboard Hot 100 songs that DEBUTED in 2025 only. Exclude re-entries from prior years.

CSV format:
track_name,artist_name,peak_position,first_chart_date (YYYY-MM-DD)

Include header.
```

**Save as:** `2025.csv`

---

### **Step 2: Work Backwards (2024, 2023, etc.)**
```
Billboard Hot 100 songs that DEBUTED in 2024 only. Exclude re-entries from prior years.

CSV format:
track_name,artist_name,peak_position,first_chart_date (YYYY-MM-DD)

Include header.
```

**Save as:** `2024.csv`

Repeat for each year down to 2005 (or your desired start year).

---

## 🔄 **Combining CSVs:**

### **Option 1: Manual Combine**
```bash
# In terminal
cd /Users/benkohn/Desktop/LyricBox/backend/data_enrichment

# Create header
head -1 2025.csv > songs_list.csv

# Append all years (skip headers)
tail -n +2 2025.csv >> songs_list.csv
tail -n +2 2024.csv >> songs_list.csv
tail -n +2 2023.csv >> songs_list.csv
# ... etc for all years
```

### **Option 2: Append Each Year**
After first year (2025):
- Copy output WITHOUT header
- Paste into existing `songs_list.csv`

---

## ✅ **Why This Works:**

**"DEBUTED in [YEAR]"** ensures:
- ✅ "All I Want for Christmas" only appears once (1994 debut)
- ✅ "Last Christmas" only appears once (1984 debut)
- ✅ No duplicate songs when combining years
- ✅ Each song has ONE canonical `first_chart_date`
- ✅ Clean dataset for database import

---

## 📊 **Expected Output Format:**

```csv
track_name,artist_name,peak_position,first_chart_date
Anti-Hero,Taylor Swift,1,2022-10-22
Flowers,Miley Cyrus,1,2023-01-14
Cruel Summer,Taylor Swift,1,2019-06-14
```

Each row = one unique song with its first chart appearance.

---

## 🎯 **Years to Collect:**

Recommended range: **2005-2025** (20 years of Billboard data)

- 2025 → Most recent
- 2024 → Last full year
- 2023, 2022, 2021... → Work backwards
- 2005 → Stopping point

**Estimated:** ~100-200 songs per year = ~2,000-4,000 total songs

---

## 💾 **Final File Location:**

Combined CSV should be saved to:
```
/Users/benkohn/Desktop/LyricBox/backend/data_enrichment/songs_list.csv
```

This is the file that `data_enrichment_main.py` reads from.

---

## 🚀 **Ready to Run Pipeline:**

Once you have `songs_list.csv`:
```bash
cd /Users/benkohn/Desktop/LyricBox/backend/data_enrichment
source ../venv/bin/activate
python data_enrichment_main.py
```

The pipeline will:
1. Read your CSV
2. Create normalized artists/albums/songs
3. Fetch all metadata (Musixmatch + GetSongBPM)
4. Scrape lyrics (Genius)
5. Scrape chords + update keys (Ultimate Guitar)

---

**Start with 2025 and work backwards!** 🎵

