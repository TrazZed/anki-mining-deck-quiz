"""
Card filtering system for practice modes.
"""

# Maturity level constants
MATURITY_NEW = 'new'           # Never studied (type=0)
MATURITY_LEARNING = 'learning' # In learning phase (type=1)
MATURITY_YOUNG = 'young'       # Review cards, interval < 21 days
MATURITY_MATURE = 'mature'     # Review cards, interval >= 21 days

# Display names for UI
MATURITY_DISPLAY_NAMES = {
    MATURITY_NEW: 'New Cards',
    MATURITY_LEARNING: 'Learning Cards',
    MATURITY_YOUNG: 'Young Cards (<21 days)',
    MATURITY_MATURE: 'Mature Cards (≥21 days)'
}


class CardFilter:
    """Manages card filtering settings."""
    
    def __init__(self):
        self.maturity_levels = []  # List of maturity levels to include
        self.enabled = False       # Whether filtering is active
    
    def set_maturity_levels(self, levels):
        """
        Set which maturity levels to include.
        
        Args:
            levels: List of maturity constants (e.g., ['young', 'mature'])
        """
        self.maturity_levels = levels
        self.enabled = len(levels) > 0
    
    def add_maturity_level(self, level):
        """Add a maturity level to the filter."""
        if level not in self.maturity_levels:
            self.maturity_levels.append(level)
            self.enabled = True
    
    def remove_maturity_level(self, level):
        """Remove a maturity level from the filter."""
        if level in self.maturity_levels:
            self.maturity_levels.remove(level)
            self.enabled = len(self.maturity_levels) > 0
    
    def toggle_maturity_level(self, level):
        """Toggle a maturity level on/off."""
        if level in self.maturity_levels:
            self.remove_maturity_level(level)
        else:
            self.add_maturity_level(level)
    
    def clear(self):
        """Clear all filters."""
        self.maturity_levels = []
        self.enabled = False
    
    def is_active(self):
        """Check if any filters are active."""
        return self.enabled and len(self.maturity_levels) > 0
    
    def get_summary(self):
        """Get a human-readable summary of active filters."""
        if not self.is_active():
            return "All Cards"
        
        names = [MATURITY_DISPLAY_NAMES.get(level, level) for level in self.maturity_levels]
        return ", ".join(names)


def get_card_maturity(card):
    """
    Determine the maturity level of a card.
    
    Args:
        card: Card info dict from AnkiConnect with 'type' and 'interval' keys
        
    Returns:
        One of the MATURITY_* constants
    """
    card_type = card.get('type', 0)
    interval = card.get('interval', 0)
    
    if card_type == 0:
        return MATURITY_NEW
    elif card_type == 1:
        return MATURITY_LEARNING
    elif card_type == 2:
        # Review card - check interval
        if interval < 21:
            return MATURITY_YOUNG
        else:
            return MATURITY_MATURE
    else:
        # Unknown type, treat as new
        return MATURITY_NEW


def filter_cards_by_maturity(cards, maturity_levels):
    """
    Filter cards by maturity level.
    
    Args:
        cards: List of card info dicts from AnkiConnect
        maturity_levels: List of maturity constants to include
        
    Returns:
        Filtered list of cards
    """
    if not maturity_levels:
        return cards
    
    filtered = []
    for card in cards:
        maturity = get_card_maturity(card)
        if maturity in maturity_levels:
            filtered.append(card)
    
    return filtered


def analyze_deck_maturity(cards):
    """
    Analyze a deck to show maturity distribution.
    
    Args:
        cards: List of card info dicts
        
    Returns:
        Dict with counts for each maturity level
    """
    counts = {
        MATURITY_NEW: 0,
        MATURITY_LEARNING: 0,
        MATURITY_YOUNG: 0,
        MATURITY_MATURE: 0
    }
    
    for card in cards:
        maturity = get_card_maturity(card)
        counts[maturity] = counts.get(maturity, 0) + 1
    
    return counts


def get_available_maturity_levels(cards):
    """
    Get list of maturity levels that have cards in this deck.
    
    Args:
        cards: List of card info dicts
        
    Returns:
        List of maturity constants that have at least one card
    """
    counts = analyze_deck_maturity(cards)
    return [level for level, count in counts.items() if count > 0]
