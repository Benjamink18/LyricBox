#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Test if 'love' exists in rhyme pairs
query_str = "word.ilike.love,rhymes_with.ilike.love"
result = supabase.table('rhyme_pairs').select('word, rhymes_with, song_id').or_(query_str).limit(5).execute()
print(f'Found {len(result.data)} rhyme pairs with "love"')
for pair in result.data[:3]:
    print(f'  {pair["word"]} -> {pair["rhymes_with"]} (song_id: {pair["song_id"]})')

