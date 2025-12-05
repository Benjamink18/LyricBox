"""
UG SCRAPER MODULE
Scrapes chord data from Ultimate Guitar using Playwright.
"""

from .setup import setup_browser
from .search import search_song
from .find_official import find_official_tabs
from .click_tab import click_tab
from .click_chords import click_chords
from .extract_tonality import extract_tonality
from .extract_chords import extract_chords
from .transpose_to_c import transpose_to_c
from .convert_to_roman import convert_to_roman
from .simplify_chord import simplify_chord
from .process_chords import process_chords
from .log_missing_chords import log_missing_chords
from .chords_to_supabase import save_chords_to_supabase
from .scrape_song import scrape_song

__all__ = [
    'setup_browser',
    'search_song',
    'find_official_tabs',
    'click_tab',
    'click_chords',
    'extract_tonality',
    'extract_chords',
    'transpose_to_c',
    'convert_to_roman',
    'simplify_chord',
    'process_chords',
    'log_missing_chords',
    'save_chords_to_supabase',
    'scrape_song'
]

