"""
GENIUS SCRAPE MODULE
Scrapes lyrics with section markers from Genius.com using Playwright.
"""

from .setup_browser import setup_browser
from .genius_main import scrape_lyrics

__all__ = ['setup_browser', 'scrape_lyrics']

