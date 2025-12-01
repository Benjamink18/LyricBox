#!/usr/bin/env python3
"""
Test script to verify all lyrics sources are working.
"""

from lyrics_client import MultiSourceLyricsClient
import sys


def test_all_sources():
    """Test each lyrics source individually."""
    
    client = MultiSourceLyricsClient()
    
    # Test song
    artist = "Hozier"
    title = "Too Sweet"
    
    print(f"Testing all lyrics sources for: {artist} - {title}\n")
    print("=" * 60)
    
    # Test each source individually
    sources_to_test = [
        ("Musixmatch", client._fetch_musixmatch),
        ("Lyrics.ovh", client._fetch_lyrics_ovh),
        ("LRCLIB", client._fetch_lrclib),
    ]
    
    results = []
    
    for source_name, fetch_func in sources_to_test:
        print(f"\n🧪 Testing {source_name}...")
        try:
            result = fetch_func(artist, title)
            if result.success:
                preview = result.lyrics[:100].replace("\n", " ")
                print(f"   ✅ SUCCESS")
                print(f"   📝 Preview: {preview}...")
                print(f"   📊 Length: {len(result.lyrics)} characters")
                results.append((source_name, "✅", None))
            else:
                print(f"   ❌ FAILED: {result.error}")
                results.append((source_name, "❌", result.error))
        except Exception as e:
            print(f"   💥 ERROR: {str(e)}")
            results.append((source_name, "💥", str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    working_sources = sum(1 for _, status, _ in results if status == "✅")
    
    for source, status, error in results:
        print(f"{status} {source:15} ", end="")
        if error:
            print(f"({error[:40]}...)" if len(error) > 40 else f"({error})")
        else:
            print()
    
    print("\n" + "=" * 60)
    print(f"✅ {working_sources}/3 sources working")
    
    if working_sources == 0:
        print("\n⚠️  WARNING: No sources are working!")
        print("   Please check your Musixmatch API key in .env file")
        return False
    elif working_sources < 2:
        print("\n⚠️  WARNING: Only 1 source working")
        print("   Should be fine but less redundancy")
        return True
    else:
        print("\n🎉 Great! Multiple sources working - you have solid fallback!")
        return True


def test_automatic_fallback():
    """Test the automatic fallback system."""
    
    print("\n" + "=" * 60)
    print("TESTING AUTOMATIC FALLBACK")
    print("=" * 60)
    
    client = MultiSourceLyricsClient()
    
    test_songs = [
        ("Taylor Swift", "Anti-Hero"),
        ("The Weeknd", "Blinding Lights"),
        ("Kendrick Lamar", "HUMBLE.")
    ]
    
    for artist, title in test_songs:
        print(f"\n🎵 {artist} - {title}")
        result = client.get_lyrics(artist, title)
        
        if result.success:
            preview = result.lyrics[:80].replace("\n", " ")
            print(f"   ✅ Success via {result.source.upper()}")
            print(f"   📝 {preview}...")
        else:
            print(f"   ❌ All sources failed")
            print(f"   📝 Errors: {result.error}")


if __name__ == "__main__":
    print("🔍 LYRICS SOURCE TESTING")
    print("=" * 60)
    
    # Test individual sources
    success = test_all_sources()
    
    # Test automatic fallback
    test_automatic_fallback()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE!")
    print("=" * 60)
    
    if not success:
        print("\n💡 Next step: Check your Musixmatch API key")
        print("   Visit: https://developer.musixmatch.com/")
        print("   Resets at midnight UTC if you hit the daily limit")
        sys.exit(1)
    else:
        print("\n✅ You're all set! Ready for the full import.")
        sys.exit(0)

