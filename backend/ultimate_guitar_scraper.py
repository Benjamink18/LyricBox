#!/usr/bin/env python3
"""
Ultimate Guitar scraper for fetching real chord data.
Based on https://github.com/joncardasis/ultimate-api
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import re
import json


class UltimateGuitarScraper:
    """Scrapes Ultimate Guitar for chord tabs."""
    
    BASE_URL = "https://www.ultimate-guitar.com"
    SEARCH_URL = f"{BASE_URL}/search.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def search_song(self, artist: str, title: str) -> Optional[str]:
        """
        Search for a song and return the first Chords tab URL.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            Tab URL if found, None otherwise
        """
        try:
            query = f"{artist} {title}"
            params = {
                'search_type': 'title',
                'value': query
            }
            
            response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️  UG search failed with status {response.status_code}")
                return None
            
            # Parse the search results page to find tab data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the data store in the page (UG embeds search results in JS)
            script_tags = soup.find_all('script')
            for script in script_tags:
                if 'window.UGAPP.store.page' in str(script.string):
                    # Extract the JSON data
                    match = re.search(r'window\.UGAPP\.store\.page\s*=\s*({.*?});', str(script.string))
                    if match:
                        data = json.loads(match.group(1))
                        results = data.get('data', {}).get('results', [])
                        
                        # Find first "Chords" tab (type: 'Chords')
                        for result in results:
                            if result.get('type') == 'Chords':
                                tab_url = result.get('tab_url')
                                if tab_url:
                                    print(f"✅ Found UG tab: {tab_url}")
                                    return tab_url
            
            print(f"⚠️  No chord tab found for: {artist} - {title}")
            return None
            
        except Exception as e:
            print(f"⚠️  UG search error: {e}")
            return None
    
    def scrape_tab(self, tab_url: str) -> Optional[Dict[str, any]]:
        """
        Scrape a tab page for chord data.
        
        Args:
            tab_url: Full URL to the tab page
            
        Returns:
            Dict with tab data including chorus chords, or None
        """
        try:
            response = self.session.get(tab_url, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️  Failed to fetch tab: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the tab data in the page (UG stores it in JS)
            script_tags = soup.find_all('script')
            for script in script_tags:
                if 'window.UGAPP.store.page' in str(script.string):
                    match = re.search(r'window\.UGAPP\.store\.page\s*=\s*({.*?});', str(script.string))
                    if match:
                        data = json.loads(match.group(1))
                        tab_data = data.get('data', {}).get('tab_view', {}).get('wiki_tab', {})
                        
                        content = tab_data.get('content', '')
                        song_name = tab_data.get('song_name', '')
                        artist_name = tab_data.get('artist_name', '')
                        
                        # Extract chorus section
                        chorus_chords = self._extract_chorus_chords(content)
                        
                        return {
                            'song_name': song_name,
                            'artist_name': artist_name,
                            'content': content,
                            'chorus_chords': chorus_chords,
                            'tab_url': tab_url
                        }
            
            print(f"⚠️  Could not extract tab data from page")
            return None
            
        except Exception as e:
            print(f"⚠️  Error scraping tab: {e}")
            return None
    
    def _extract_chorus_chords(self, content: str) -> Optional[str]:
        """
        Extract chords from the chorus section of tab content.
        
        Args:
            content: Raw tab content
            
        Returns:
            Chord progression string or None
        """
        try:
            # Look for [Chorus] section
            chorus_match = re.search(r'\[Chorus[^\]]*\](.*?)(?:\[|$)', content, re.IGNORECASE | re.DOTALL)
            
            if not chorus_match:
                print("⚠️  No [Chorus] section found in tab")
                return None
            
            chorus_text = chorus_match.group(1)
            
            # Extract all chords (uppercase letters with optional modifiers)
            # Matches: C, Cm, C7, Cmaj7, C#m, etc.
            chord_pattern = r'\b([A-G][#b]?(?:m|maj|min|dim|aug|sus|add)?[0-9]*)\b'
            chords = re.findall(chord_pattern, chorus_text)
            
            if not chords:
                print("⚠️  No chords found in chorus section")
                return None
            
            # Remove duplicates while preserving order
            unique_chords = []
            seen = set()
            for chord in chords:
                if chord not in seen:
                    unique_chords.append(chord)
                    seen.add(chord)
            
            chord_progression = ' '.join(unique_chords)
            print(f"✅ Extracted chorus chords: {chord_progression}")
            return chord_progression
            
        except Exception as e:
            print(f"⚠️  Error extracting chorus chords: {e}")
            return None
    
    def get_verified_chords(self, artist: str, title: str) -> Optional[str]:
        """
        Complete workflow: search for song and extract chorus chords.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            Chorus chord progression string or None
        """
        print(f"🔍 Searching Ultimate Guitar for: {artist} - {title}")
        
        # Step 1: Search for the tab
        tab_url = self.search_song(artist, title)
        if not tab_url:
            return None
        
        # Step 2: Scrape the tab
        tab_data = self.scrape_tab(tab_url)
        if not tab_data:
            return None
        
        return tab_data.get('chorus_chords')


# CLI for testing
if __name__ == "__main__":
    scraper = UltimateGuitarScraper()
    
    # Test with a popular song
    chords = scraper.get_verified_chords("Taylor Swift", "Love Story")
    print(f"\nResult: {chords}")

