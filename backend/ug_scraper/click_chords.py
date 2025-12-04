"""
CLICK CHORDS: Click the CHORDS button on the tab page
Switches the view to show chords instead of just tabs.
"""


def click_chords(page):
    """
    Click the CHORDS button on a tab page.
    
    Args:
        page: Playwright page instance (on a tab page)
    
    Returns:
        None (switches to chords view)
    """
    print("Clicking CHORDS button...")
    
    try:
        # Use Playwright's smart text matching with force click
        chords_button = page.get_by_text("Chords", exact=True)
        if chords_button.count() > 0:
            chords_button.first.click(force=True)
            print("Clicked using get_by_text!")
        else:
            print("CHORDS button not found with get_by_text.")
            # Fallback to JavaScript if Playwright's locator fails
            js_code = """
            const elements = document.querySelectorAll('button, div, span, a');
            let clicked = false;
            for (const el of elements) {
                if (el.textContent.toLowerCase().includes('chords')) {
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    clicked = true;
                    return 'Clicked: ' + el.tagName + ' - ' + el.textContent;
                }
            }
            return 'Not found';
            """
            result = page.evaluate(js_code)
            print(f"Result: {result}")
            if result.startswith('Clicked'):
                print("Clicked using JavaScript fallback!")
            else:
                print("CHORDS button not found with JavaScript fallback.")
    except Exception as e:
        print(f"Error clicking CHORDS button: {e}")
    
    page.wait_for_timeout(2000)  # Wait for chords to render
    print("Done!")

