"""
UTILS: Shared utilities for scrapers
Contains human behavior simulation and other common functions.
"""

from .human_behavior import act_human, random_delay, random_mouse_movement, random_scroll

__all__ = ['act_human', 'random_delay', 'random_mouse_movement', 'random_scroll']

