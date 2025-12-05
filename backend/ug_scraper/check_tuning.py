"""
CHECK TUNING: Determine if a tuning is standard or alternate
============================================================
Standard guitar tuning is E A D G B E (low to high).
"""


def is_standard_tuning(tuning):
    """
    Check if a tuning string represents standard guitar tuning.
    
    Args:
        tuning: Tuning string (e.g., "E A D G B E", "EADGBE", "D A D G A D")
    
    Returns:
        Boolean: True if standard, False if alternate
    """
    if not tuning:
        return True  # If no tuning specified, assume standard
    
    # Normalize the tuning string (remove spaces, convert to uppercase)
    normalized = tuning.replace(" ", "").upper()
    
    # Standard tuning variations
    standard_variations = [
        "EADGBE",      # Compact format
        "E A D G B E", # Spaced format
        "STANDARD",    # Text label
    ]
    
    # Check if it matches any standard variation
    for standard in standard_variations:
        if normalized == standard.replace(" ", ""):
            return True
    
    return False


def get_tuning_name(tuning):
    """
    Get a clean tuning name for logging.
    
    Args:
        tuning: Raw tuning string from UG
    
    Returns:
        Cleaned tuning name (e.g., "DADGAD", "Drop D")
    """
    if not tuning:
        return "Unknown"
    
    # Remove extra spaces and normalize
    cleaned = " ".join(tuning.split())
    
    return cleaned

