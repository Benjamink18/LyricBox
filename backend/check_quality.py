"""Check if analysis quality has degraded over time."""
from supabase import create_client
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("🔍 QUALITY ANALYSIS: Early vs Recent Imports\n")
print("=" * 60)

# Get first 50 songs (original batch)
early_songs = supabase.table('song_analysis').select(
    'song_id, themes, imagery, thematic_vocabulary, alternative_titles, section_breakdown, concept_summary, songs(title, artist)'
).limit(50).execute()

# Get most recent 50 songs (from adaptive testing)
total = supabase.table('song_analysis').select('id', count='exact').execute()
offset = total.count - 50

recent_songs = supabase.table('song_analysis').select(
    'song_id, themes, imagery, thematic_vocabulary, alternative_titles, section_breakdown, concept_summary, songs(title, artist)'
).range(offset, offset + 49).execute()

def analyze_quality(songs, label):
    print(f"\n📊 {label} ({len(songs.data)} songs)")
    print("-" * 60)
    
    themes_count = []
    imagery_count = []
    vocab_count = []
    titles_count = []
    has_section_breakdown = 0
    has_concept = 0
    concept_lengths = []
    
    for song in songs.data:
        themes = song.get('themes') or []
        imagery = song.get('imagery') or []
        vocab = song.get('thematic_vocabulary') or []
        titles = song.get('alternative_titles') or []
        section = song.get('section_breakdown')
        concept = song.get('concept_summary') or ""
        
        themes_count.append(len(themes) if isinstance(themes, list) else 0)
        imagery_count.append(len(imagery) if isinstance(imagery, list) else 0)
        vocab_count.append(len(vocab) if isinstance(vocab, list) else 0)
        titles_count.append(len(titles) if isinstance(titles, list) else 0)
        
        if section and isinstance(section, (dict, list)):
            has_section_breakdown += 1
        
        if concept and len(concept.strip()) > 0:
            has_concept += 1
            concept_lengths.append(len(concept))
    
    avg_themes = sum(themes_count) / len(themes_count) if themes_count else 0
    avg_imagery = sum(imagery_count) / len(imagery_count) if imagery_count else 0
    avg_vocab = sum(vocab_count) / len(vocab_count) if vocab_count else 0
    avg_titles = sum(titles_count) / len(titles_count) if titles_count else 0
    avg_concept_len = sum(concept_lengths) / len(concept_lengths) if concept_lengths else 0
    
    print(f"  Themes per song:         {avg_themes:.1f}")
    print(f"  Imagery items per song:  {avg_imagery:.1f}")
    print(f"  Vocabulary per song:     {avg_vocab:.1f}")
    print(f"  Alternative titles:      {avg_titles:.1f}")
    print(f"  Section breakdowns:      {has_section_breakdown}/{len(songs.data)} ({has_section_breakdown/len(songs.data)*100:.1f}%)")
    print(f"  Has concept summary:     {has_concept}/{len(songs.data)} ({has_concept/len(songs.data)*100:.1f}%)")
    print(f"  Avg concept length:      {avg_concept_len:.0f} chars")
    
    # Show a sample
    if songs.data:
        sample = songs.data[0]
        song_title = sample.get('songs', {}).get('title', 'Unknown') if sample.get('songs') else 'Unknown'
        song_artist = sample.get('songs', {}).get('artist', 'Unknown') if sample.get('songs') else 'Unknown'
        print(f"\n  📝 Sample: {song_title} - {song_artist}")
        themes = sample.get('themes', [])
        if isinstance(themes, list):
            print(f"     Themes ({len(themes)}): {themes[:3]}")
        vocab = sample.get('thematic_vocabulary', [])
        if isinstance(vocab, list):
            print(f"     Vocab words: {len(vocab)}")
        concept = sample.get('concept_summary', '')
        if concept:
            print(f"     Concept: {concept[:100]}...")

analyze_quality(early_songs, "EARLY BATCH (First 50 songs)")
analyze_quality(recent_songs, "RECENT BATCH (Last 50 songs)")

# Check rhyme pairs
print("\n\n🎯 RHYME PAIRS ANALYSIS")
print("=" * 60)

# Early songs rhyme pairs
early_song_ids = [s['song_id'] for s in early_songs.data[:20]]
early_rhymes = supabase.table('rhyme_pairs').select('song_id, rhyme_type').in_('song_id', early_song_ids).execute()

# Recent songs rhyme pairs  
recent_song_ids = [s['song_id'] for s in recent_songs.data[:20]]
recent_rhymes = supabase.table('rhyme_pairs').select('song_id, rhyme_type').in_('song_id', recent_song_ids).execute()

def analyze_rhymes(rhymes, label, num_songs):
    print(f"\n📊 {label} (20 songs)")
    print("-" * 60)
    
    total_pairs = len(rhymes.data)
    avg_per_song = total_pairs / num_songs if num_songs > 0 else 0
    
    rhyme_types = Counter([r['rhyme_type'] for r in rhymes.data])
    
    print(f"  Total rhyme pairs:       {total_pairs}")
    print(f"  Avg per song:            {avg_per_song:.1f}")
    print(f"  Rhyme type breakdown:")
    for rtype, count in rhyme_types.most_common():
        print(f"    {rtype:12s}: {count:4d} ({count/total_pairs*100:.1f}%)")

analyze_rhymes(early_rhymes, "EARLY BATCH", 20)
analyze_rhymes(recent_rhymes, "RECENT BATCH", 20)

print("\n" + "=" * 60)
print("✅ QUALITY CHECK COMPLETE")
print("=" * 60)
