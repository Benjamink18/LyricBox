#!/usr/bin/env python3
"""
Test script to fetch 5 songs from each backup source and compare quality.
"""

from lyrics_client import MultiSourceLyricsClient
import json


def test_backup_sources():
    """Test Lyrics.ovh and LRCLIB with 5 popular songs."""
    
    client = MultiSourceLyricsClient()
    
    # 5 diverse test songs
    test_songs = [
        ("Hozier", "Too Sweet"),
        ("Taylor Swift", "Anti-Hero"),
        ("The Weeknd", "Blinding Lights"),
        ("Billie Eilish", "Bad Guy"),
        ("Ed Sheeran", "Shape of You")
    ]
    
    results = {
        "lyrics_ovh": [],
        "lrclib": []
    }
    
    print("🔍 Testing Lyrics.ovh...\n")
    for artist, title in test_songs:
        print(f"   Fetching: {artist} - {title}")
        result = client._fetch_lyrics_ovh(artist, title)
        results["lyrics_ovh"].append({
            "artist": artist,
            "title": title,
            "success": result.success,
            "lyrics": result.lyrics if result.success else None,
            "error": result.error if not result.success else None
        })
    
    print("\n🔍 Testing LRCLIB...\n")
    for artist, title in test_songs:
        print(f"   Fetching: {artist} - {title}")
        result = client._fetch_lrclib(artist, title)
        results["lrclib"].append({
            "artist": artist,
            "title": title,
            "success": result.success,
            "lyrics": result.lyrics if result.success else None,
            "error": result.error if not result.success else None
        })
    
    return results


def generate_markdown(results):
    """Generate markdown file comparing both sources."""
    
    md = "# Backup Lyrics Sources Comparison\n\n"
    md += "Testing 5 songs from each backup source to verify data quality.\n\n"
    md += "---\n\n"
    
    # Summary table
    md += "## Summary\n\n"
    md += "| Song | Lyrics.ovh | LRCLIB |\n"
    md += "|------|------------|--------|\n"
    
    for i, song in enumerate(results["lyrics_ovh"]):
        ovh_status = "✅" if song["success"] else "❌"
        lrc_status = "✅" if results["lrclib"][i]["success"] else "❌"
        md += f"| {song['artist']} - {song['title']} | {ovh_status} | {lrc_status} |\n"
    
    md += "\n---\n\n"
    
    # Detailed results for each song
    for i, song in enumerate(results["lyrics_ovh"]):
        md += f"## {i+1}. {song['artist']} - {song['title']}\n\n"
        
        # Lyrics.ovh
        md += "### Lyrics.ovh\n\n"
        if song["success"]:
            lyrics = song["lyrics"]
            md += f"**Status:** ✅ Success\n\n"
            md += f"**Length:** {len(lyrics)} characters\n\n"
            md += "**First 500 characters:**\n\n"
            md += "```\n"
            md += lyrics[:500]
            if len(lyrics) > 500:
                md += "\n... (truncated)"
            md += "\n```\n\n"
            
            # Show last 200 characters too
            if len(lyrics) > 500:
                md += "**Last 200 characters:**\n\n"
                md += "```\n"
                md += lyrics[-200:]
                md += "\n```\n\n"
        else:
            md += f"**Status:** ❌ Failed\n\n"
            md += f"**Error:** {song['error']}\n\n"
        
        # LRCLIB
        lrc_song = results["lrclib"][i]
        md += "### LRCLIB\n\n"
        if lrc_song["success"]:
            lyrics = lrc_song["lyrics"]
            md += f"**Status:** ✅ Success\n\n"
            md += f"**Length:** {len(lyrics)} characters\n\n"
            md += "**First 500 characters:**\n\n"
            md += "```\n"
            md += lyrics[:500]
            if len(lyrics) > 500:
                md += "\n... (truncated)"
            md += "\n```\n\n"
            
            # Show last 200 characters too
            if len(lyrics) > 500:
                md += "**Last 200 characters:**\n\n"
                md += "```\n"
                md += lyrics[-200:]
                md += "\n```\n\n"
        else:
            md += f"**Status:** ❌ Failed\n\n"
            md += f"**Error:** {lrc_song['error']}\n\n"
        
        md += "---\n\n"
    
    # Final assessment
    md += "## Assessment\n\n"
    
    ovh_success = sum(1 for s in results["lyrics_ovh"] if s["success"])
    lrc_success = sum(1 for s in results["lrclib"] if s["success"])
    
    md += f"**Lyrics.ovh:** {ovh_success}/5 songs successfully fetched\n\n"
    md += f"**LRCLIB:** {lrc_success}/5 songs successfully fetched\n\n"
    
    if ovh_success >= 4 or lrc_success >= 4:
        md += "✅ **Conclusion:** Backup sources are reliable for the full import!\n\n"
    elif ovh_success + lrc_success >= 6:
        md += "⚠️ **Conclusion:** Between both sources, good coverage. Automatic fallback will work well.\n\n"
    else:
        md += "❌ **Conclusion:** May need to wait for Musixmatch to reset.\n\n"
    
    return md


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING BACKUP LYRICS SOURCES")
    print("=" * 60)
    print()
    
    results = test_backup_sources()
    
    print("\n" + "=" * 60)
    print("GENERATING MARKDOWN REPORT")
    print("=" * 60)
    
    md_content = generate_markdown(results)
    
    with open("BACKUP_SOURCES_TEST.md", "w") as f:
        f.write(md_content)
    
    print("\n✅ Report saved to: BACKUP_SOURCES_TEST.md")
    print()


