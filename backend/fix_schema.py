#!/usr/bin/env python3
"""
Add missing lyrics_source column to songs table.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def fix_schema():
    """Add lyrics_source column to songs table."""
    
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    print("🔧 Adding lyrics_source column to songs table...")
    print()
    
    try:
        # Execute SQL to add column
        result = supabase.rpc('exec_sql', {
            'query': 'ALTER TABLE songs ADD COLUMN IF NOT EXISTS lyrics_source TEXT;'
        }).execute()
        
        print("✅ Column added successfully!")
        
    except Exception as e:
        # If RPC doesn't work, we'll need to do it via Supabase UI
        print("⚠️  Cannot add column via Python client")
        print()
        print("Please run this SQL in Supabase SQL Editor:")
        print()
        print("=" * 60)
        print("ALTER TABLE songs")
        print("ADD COLUMN IF NOT EXISTS lyrics_source TEXT;")
        print("=" * 60)
        print()
        print("Steps:")
        print("1. Go to Supabase Dashboard")
        print("2. Click 'SQL Editor' in left sidebar")
        print("3. Click 'New Query'")
        print("4. Paste the SQL above")
        print("5. Click 'Run' or press Cmd+Enter")
        print()


if __name__ == "__main__":
    fix_schema()

