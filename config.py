"""
Configuration and constants for the Japanese Vocabulary Game.
"""

# AnkiConnect settings
ANKI_CONNECT_URL = "http://localhost:8765"
SAVE_FILE = "vocab_game_save.json"
SCORES_FILE = "vocab_game_scores.csv"

# Game states
STATE_LOADING = 'loading'
STATE_LOADING_SAVE = 'loading_save'
STATE_SAVING = 'saving'
STATE_MENU = 'menu'
STATE_FILTER_SELECT = 'filter_select'
STATE_MODE_SELECT = 'mode_select'
STATE_COUNTDOWN = 'countdown'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_LEADERBOARD = 'leaderboard'
STATE_GAME_OVER = 'game_over'
STATE_REVIEW_INCORRECT = 'review_incorrect'

# Game settings
DEFAULT_DECK_NAME = "日本語::Mining"
PRELOAD_COUNT = 10  # Number of cards to keep preloaded
TIME_ATTACK_DURATION = 60  # seconds
COUNTDOWN_DURATION = 3  # seconds

# Scoring settings
POINTS_UNDER_2_SEC = 100
POINTS_UNDER_4_SEC = 75
POINTS_UNDER_6_SEC = 50
POINTS_UNDER_10_SEC = 25
POINTS_OVER_10_SEC = 10
MAX_STREAK_MULTIPLIER = 3.0
STREAK_MULTIPLIER_STEP = 0.1

# UI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
WINDOW_TITLE = "Japanese Vocabulary Quiz"

# Colors (RGB)
COLOR_BG = (44, 62, 80)  # #2C3E50
COLOR_TEXT = (236, 240, 241)  # #ECF0F1
COLOR_CORRECT = (46, 204, 113)  # #2ECC71
COLOR_INCORRECT = (231, 76, 60)  # #E74C3C
COLOR_BUTTON = (52, 152, 219)  # #3498DB
COLOR_BUTTON_HOVER = (41, 128, 185)  # #2980B9
COLOR_GRAY = (189, 195, 199)  # #BDC3C7
COLOR_STATUS = (149, 165, 166)  # #95A5A6
COLOR_GOLD = (255, 215, 0)
COLOR_ORANGE = (255, 140, 0)

# Font settings
JAPANESE_FONTS = ['msgothic', 'meiryo', 'yugothic', 'msmincho', 'Arial Unicode MS']

# Romaji to Hiragana conversion map
ROMAJI_TO_HIRAGANA = {
    # Vowels
    'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
    # K-series
    'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
    'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
    # G-series
    'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
    'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',
    # S-series
    'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
    'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
    # Z-series
    'za': 'ざ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
    'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
    # T-series
    'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'tu': 'つ', 'te': 'て', 'to': 'と',
    'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',
    # D-series
    'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
    # N-series
    'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
    'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',
    # H-series
    'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
    'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
    # B-series
    'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
    'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',
    # P-series
    'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
    'pya': 'ぴゃ', 'pyu': 'ぴゅ', 'pyo': 'ぴょ',
    # M-series
    'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
    'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',
    # Y-series
    'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
    # R-series
    'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
    'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',
    # W-series
    'wa': 'わ', 'wo': 'を',
    # Special
    'nn': 'ん',
    '-': 'ー',  # Long vowel mark
}
