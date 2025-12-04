"""
HUMAN BEHAVIOR: Simulate human-like interactions
Random delays, mouse movements, and scrolling to avoid bot detection.
"""

import random


def random_delay(page, min_ms=500, max_ms=2000):
    """
    Random delay between actions.
    
    Args:
        page: Playwright page instance
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    delay = random.randint(min_ms, max_ms)
    page.wait_for_timeout(delay)


def random_mouse_movement(page):
    """
    Simulate random mouse movement.
    
    Args:
        page: Playwright page instance
    """
    try:
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)
    except Exception:
        pass  # Fail silently if mouse movement fails


def random_scroll(page):
    """
    Simulate random scrolling.
    
    Args:
        page: Playwright page instance
    """
    try:
        scroll_amount = random.randint(100, 500)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        page.wait_for_timeout(random.randint(200, 800))
    except Exception:
        pass  # Fail silently if scrolling fails


def act_human(page):
    """
    Perform random human-like actions.
    Combines delay, mouse movement, and scrolling.
    
    Args:
        page: Playwright page instance
    """
    # Random delay
    random_delay(page, 1000, 2000)
    
    # Randomly choose an action
    action = random.choice(['mouse', 'scroll', 'both'])
    
    if action == 'mouse':
        random_mouse_movement(page)
    elif action == 'scroll':
        random_scroll(page)
    else:
        random_mouse_movement(page)
        random_scroll(page)
    
    # Final short delay
    random_delay(page, 500, 1000)

