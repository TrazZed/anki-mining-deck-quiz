"""
Utility modules for the Japanese Vocabulary Game.
"""

from .anki_api import anki_request, get_deck_names, get_card_ids, get_cards_info
from .jisho_api import get_jisho_info
from .text_utils import strip_html, contains_kanji, katakana_to_hiragana, convert_romaji_to_hiragana
from .sound_utils import generate_sound

__all__ = [
    'anki_request',
    'get_deck_names',
    'get_card_ids',
    'get_cards_info',
    'get_jisho_info',
    'strip_html',
    'contains_kanji',
    'katakana_to_hiragana',
    'convert_romaji_to_hiragana',
    'generate_sound',
]
