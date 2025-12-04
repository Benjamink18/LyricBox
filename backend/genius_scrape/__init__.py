"""
GENIUS SCRAPE MODULE
Scrapes lyrics with section markers from Genius.com using Playwright.
"""

from .setup_browser import setup_browser
from .genius_scrape_main import scrape_lyrics
from .genius_batch import scrape_lyrics_batch

__all__ = ['setup_browser', 'scrape_lyrics', 'scrape_lyrics_batch']

