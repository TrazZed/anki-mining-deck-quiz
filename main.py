"""
Japanese Vocabulary Quiz Game

An interactive vocabulary quiz that connects to your Anki deck and tests
your Japanese kanji reading skills with visual effects, multiple game modes,
and comprehensive scoring.

Author: Tristan Hayes
"""

import pygame
from config import DEFAULT_DECK_NAME
from ui.game_gui import VocabGameGUI


def main():
    """Main entry point for the game."""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create and run the game
    # Pass None for cards to trigger deck loading on startup
    deck_name = DEFAULT_DECK_NAME
    app = VocabGameGUI(None, deck_name)
    app.run()


if __name__ == "__main__":
    main()
