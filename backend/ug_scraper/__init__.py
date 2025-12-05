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
from .extract_capo_and_tuning import extract_capo_and_tuning
from .check_tuning import is_standard_tuning, get_tuning_name
from .extract_chords import extract_chords
from .transpose_by_capo import transpose_by_capo, transpose_chord_list
from .transpose_to_c import transpose_to_c
from .convert_to_roman import convert_to_roman
from .simplify_chord import simplify_chord
from .process_chords import process_chords
from .log_missing_chords import log_missing_chords
from .log_alternate_tuning import log_alternate_tuning
from .chords_to_supabase import save_chords_to_supabase
from .scrape_song import scrape_song

__all__ = [
    'setup_browser',
    'search_song',
    'find_official_tabs',
    'click_tab',
    'click_chords',
    'extract_tonality',
    'extract_capo_and_tuning',
    'check_tuning',
    'is_standard_tuning',
    'get_tuning_name',
    'extract_chords',
    'transpose_by_capo',
    'transpose_chord_list',
    'transpose_to_c',
    'convert_to_roman',
    'simplify_chord',
    'process_chords',
    'log_missing_chords',
    'log_alternate_tuning',
    'save_chords_to_supabase',
    'scrape_song'
]

