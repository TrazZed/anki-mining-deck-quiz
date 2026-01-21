import requests
import random
import re
import time
import pygame
from html.parser import HTMLParser
import threading
from queue import Queue
import csv
import os
from datetime import datetime
import math
import json

ANKI_CONNECT_URL = "http://localhost:8765"
SAVE_FILE = "vocab_game_save.json"

# Game states
STATE_LOADING = 'loading'
STATE_LOADING_SAVE = 'loading_save'
STATE_SAVING = 'saving'
STATE_MENU = 'menu'
STATE_MODE_SELECT = 'mode_select'
STATE_COUNTDOWN = 'countdown'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_LEADERBOARD = 'leaderboard'
STATE_GAME_OVER = 'game_over'
STATE_REVIEW_INCORRECT = 'review_incorrect'

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

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Particle classes for visual effects
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=1.0, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += 200 * dt  # Gravity
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], self.alpha)
            pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class FireParticle(Particle):
    def __init__(self, x, y):
        colors = [(255, 100, 0), (255, 200, 0), (255, 150, 0), (255, 69, 0)]
        color = random.choice(colors)
        velocity_x = random.uniform(-30, 30)
        velocity_y = random.uniform(-100, -50)
        lifetime = random.uniform(0.5, 1.0)
        size = random.uniform(3, 6)
        super().__init__(x, y, color, velocity_x, velocity_y, lifetime, size)
    
    def update(self, dt):
        self.velocity_y -= 50 * dt  # Rise up instead of fall
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0

class StarParticle(Particle):
    """Star-shaped particle for burst effects."""
    def __init__(self, x, y, velocity_x, velocity_y):
        colors = [(255, 255, 0), (255, 255, 255), (255, 215, 0), (255, 250, 150)]
        color = random.choice(colors)
        lifetime = random.uniform(0.8, 1.5)
        size = random.uniform(4, 8)
        super().__init__(x, y, color, velocity_x, velocity_y, lifetime, size)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-360, 360)
    
    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += 150 * dt  # Gravity
        self.velocity_x *= 0.98  # Air resistance
        self.velocity_y *= 0.98
        self.lifetime -= dt
        self.rotation += self.rotation_speed * dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.alpha > 0:
            # Draw a 5-pointed star
            points = []
            for i in range(10):
                angle = math.radians(self.rotation + i * 36)
                radius = self.size if i % 2 == 0 else self.size * 0.4
                px = self.x + radius * math.cos(angle)
                py = self.y + radius * math.sin(angle)
                points.append((px, py))
            
            if len(points) >= 3:
                s = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
                offset_x = self.size * 1.5
                offset_y = self.size * 1.5
                adjusted_points = [(px - self.x + offset_x, py - self.y + offset_y) for px, py in points]
                color_with_alpha = (*self.color[:3], self.alpha)
                pygame.draw.polygon(s, color_with_alpha, adjusted_points)
                surface.blit(s, (int(self.x - offset_x), int(self.y - offset_y)))

# Utility to call AnkiConnect

def anki_request(action, params=None):
    return requests.post(ANKI_CONNECT_URL, json={
        "action": action,
        "version": 6,
        "params": params or {}
    }).json()

# Get all deck names

def get_deck_names():
    resp = anki_request("deckNames")
    return resp.get("result", [])

# Get all card IDs in a deck

def get_card_ids(deck_name):
    resp = anki_request("findCards", {"query": f"deck:{deck_name}"})
    return resp.get("result", [])

# Get card info for a list of card IDs

def get_cards_info(card_ids):
    resp = anki_request("cardsInfo", {"cards": card_ids})
    return resp.get("result", [])

# Strip HTML tags from text
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        self.skip_tags = set()  # Track tags to skip content from
    
    def handle_starttag(self, tag, attrs):
        # Skip content in style and script tags
        if tag.lower() in ('style', 'script'):
            self.skip_tags.add(tag.lower())
    
    def handle_endtag(self, tag):
        # Resume processing after style/script tags
        if tag.lower() in self.skip_tags:
            self.skip_tags.discard(tag.lower())
    
    def handle_data(self, data):
        # Only add data if we're not inside a skip tag
        if not self.skip_tags:
            self.text.append(data)
    
    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    """Remove HTML tags and return plain text."""
    s = HTMLStripper()
    s.feed(html)
    return s.get_data().strip()

# Check if a string contains kanji (CJK Unified Ideographs)
def contains_kanji(text):
    return re.search(r"[\u4e00-\u9fff]", text) is not None

# Sound generation functions
def generate_sound(frequency, duration=0.1):
    """Generate a simple beep sound."""
    try:
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = []
        for i in range(n_samples):
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            buf.append([value, value])
        sound = pygame.sndarray.make_sound(buf)
        return sound
    except:
        return None

def save_score_to_csv(score, total, points, percentage, avg_points):
    """Save the game score to a CSV file."""
    filename = "vocab_game_scores.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'time', 'score', 'total', 'percentage', 'points', 'avg_points']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        now = datetime.now()
        writer.writerow({
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'score': score,
            'total': total,
            'percentage': percentage,
            'points': points,
            'avg_points': avg_points
        })

def get_high_scores():
    """Get the top 5 high scores from CSV."""
    filename = "vocab_game_scores.csv"
    if not os.path.isfile(filename):
        return []
    
    scores = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            scores.append({
                'date': row['date'],
                'points': int(row['points']),
                'percentage': int(row['percentage'])
            })
    
    # Sort by points descending
    scores.sort(key=lambda x: x['points'], reverse=True)
    return scores[:5]

def get_jisho_info(word):
    """
    Query Jisho.org for word information.
    Returns a dict with 'word', 'readings' (list), and 'meanings', or None if not found.
    """
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Find all matching entries for this word
        entries = data.get('data', [])
        if not entries:
            return None
        
        word_text = word
        readings = []
        all_meanings = []
        
        # Collect all readings from all entries that match the word
        for entry in entries:
            japanese = entry.get('japanese', [])
            for jp in japanese:
                if jp.get('word') == word or not jp.get('word'):
                    word_text = jp.get('word', word)
                    reading = jp.get('reading', '')
                    if reading and reading not in readings:
                        readings.append(reading)
            
            # Get English meanings from first entry only
            if not all_meanings:
                senses = entry.get('senses', [])
                for sense in senses:
                    eng_defs = sense.get('english_definitions', [])
                    all_meanings.extend(eng_defs)
        
        if not readings:
            return None
        
        return {
            'word': word_text,
            'readings': readings,  # Now a list of all valid readings
            'meanings': all_meanings[:3]  # Limit to first 3 meanings
        }
    except Exception as e:
        print(f"Error fetching from Jisho: {e}")
        return None

def main():
    # Launch GUI first with loading screen
    deck_name = "日本語::Mining"
    app = VocabGameGUI(None, deck_name)
    app.run()

class VocabGameGUI:
    def __init__(self, cards, deck_name=None):
        self.cards = cards
        self.deck_name = deck_name
        self.current_index = 0
        self.score = 0
        self.points = 0  # Total points earned
        self.total = 0
        self.streak = 0  # Current correct answer streak
        self.current_info = None
        self.animating = False
        self.game_over = False
        self.can_skip = False  # Can skip animation with Enter
        self.question_start_time = None  # Track when question was displayed
        self.paused_time_elapsed = 0  # Time elapsed before pausing
        self.last_points_earned = 0  # Points earned on last answer
        self.incorrect_answers = []  # Track incorrect answers
        
        # Loading state
        self.loading_deck = (cards is None)
        self.loading_status = "Initializing..."
        self.loading_error = None
        self.save_load_status = ""  # For save/load operations
        self.save_load_error = None
        
        # Game state
        self.state = STATE_LOADING if self.loading_deck else STATE_MENU
        self.high_scores = []
        self.countdown_start = 0
        self.countdown_number = 3
        self.game_mode = 'normal'  # 'normal' or 'fast'
        
        # Word zoom animation
        self.word_zoom = 0.2  # 0.0 to 1.0
        self.word_distance = 1.0  # How far away the word is
        
        # Particle system
        self.particles = []
        self.background_time = 0
        
        # Screen shake
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        self.screen_shake_intensity = 0
        
        # Sound effects
        try:
            self.sound_correct = generate_sound(523, 0.1)  # C note
            self.sound_incorrect = generate_sound(200, 0.15)  # Low note
            self.sound_streak = generate_sound(659, 0.08)  # E note
        except:
            self.sound_correct = None
            self.sound_incorrect = None
            self.sound_streak = None
        
        # Card preloading queue
        self.ready_cards = Queue()
        self.preload_count = 10  # Number of cards to keep preloaded
        self.loading = True
        self.fetch_thread = None
        
        # Create window
        self.width = 800
        self.height = 650
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Japanese Vocabulary Quiz")
        
        # Colors
        self.bg_color = (44, 62, 80)  # #2C3E50
        self.text_color = (236, 240, 241)  # #ECF0F1
        self.correct_color = (46, 204, 113)  # #2ECC71
        self.incorrect_color = (231, 76, 60)  # #E74C3C
        self.button_color = (52, 152, 219)  # #3498DB
        self.button_hover_color = (41, 128, 185)  # #2980B9
        self.gray_color = (189, 195, 199)  # #BDC3C7
        self.status_color = (149, 165, 166)  # #95A5A6
        
        # Fonts - try multiple Japanese fonts
        japanese_fonts = ['msgothic', 'meiryo', 'yugothic', 'msgothic', 'msmincho', 'Arial Unicode MS']
        
        self.word_font = None
        for font_name in japanese_fonts:
            try:
                self.word_font = pygame.font.SysFont(font_name, 72)
                # Test if it can render hiragana
                test = self.word_font.render('あ', True, (255, 255, 255))
                if test.get_width() > 0:
                    break
            except:
                continue
        
        if not self.word_font:
            self.word_font = pygame.font.Font(None, 72)
        
        self.reading_font = None
        for font_name in japanese_fonts:
            try:
                self.reading_font = pygame.font.SysFont(font_name, 32)
                # Test if it can render hiragana
                test = self.reading_font.render('あ', True, (0, 0, 0))
                if test.get_width() > 0:
                    break
            except:
                continue
        
        if not self.reading_font:
            self.reading_font = pygame.font.Font(None, 32)
        
        self.meaning_font = pygame.font.Font(None, 24)
        self.score_font = pygame.font.Font(None, 20)
        
        # Input state
        self.input_text = ""
        self.input_active = False
        self.composition = ""  # For IME composition text
        self.romaji_buffer = ""  # Buffer for romaji to hiragana conversion
        
        # Enable text input for IME support
        pygame.key.start_text_input()
        
        # Buttons
        self.button_rect = pygame.Rect(self.width // 2 - 100, 330, 200, 50)
        self.button_hover = False
        
        # Menu buttons
        self.play_button = pygame.Rect(self.width // 2 - 100, 250, 200, 60)
        self.resume_game_button = pygame.Rect(self.width // 2 - 100, 330, 200, 60)
        self.leaderboard_button = pygame.Rect(self.width // 2 - 100, 410, 200, 60)
        self.back_button = pygame.Rect(self.width // 2 - 100, 500, 200, 50)
        self.leave_button = pygame.Rect(self.width - 80, 10, 70, 30)
        self.pause_button = pygame.Rect(self.width - 160, 10, 70, 30)
        self.play_button_hover = False
        self.resume_game_button_hover = False
        self.leaderboard_button_hover = False
        self.back_button_hover = False
        self.leave_button_hover = False
        self.pause_button_hover = False
        
        # Pause menu buttons
        self.resume_button = pygame.Rect(self.width // 2 - 100, 250, 200, 60)
        self.save_quit_button = pygame.Rect(self.width // 2 - 100, 330, 200, 60)
        self.quit_button = pygame.Rect(self.width // 2 - 100, 410, 200, 60)
        self.resume_button_hover = False
        self.save_quit_button_hover = False
        self.quit_button_hover = False
        
        # Retry button for connection errors
        self.retry_button = pygame.Rect(self.width // 2 - 100, self.height // 2 + 80, 200, 50)
        self.retry_button_hover = False
        
        # Mode selection buttons
        self.normal_mode_button = pygame.Rect(self.width // 2 - 220, 250, 200, 80)
        self.fast_mode_button = pygame.Rect(self.width // 2 + 20, 250, 200, 80)
        self.normal_mode_hover = False
        self.fast_mode_hover = False
        
        # Review screen scroll
        self.review_scroll = 0
        self.review_cache = None  # Cache rendered review items
        self.review_cache_scroll = -1  # Track scroll position for cache invalidation
        
        # Animation state
        self.feedback_text = ""
        self.feedback_color = self.text_color
        self.word_color = self.text_color
        self.meaning_text = ""
        self.meaning_color = self.gray_color
        self.status_text = ""
        self.animation_start = 0
        self.animation_type = None  # 'correct', 'incorrect', or None
        self.shake_offset = 0
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Start deck loading if needed
        if self.loading_deck:
            loading_thread = threading.Thread(target=self._load_deck, daemon=True)
            loading_thread.start()
        else:
            # Start background card loading
            self.fetch_thread = threading.Thread(target=self._preload_cards, daemon=True)
            self.fetch_thread.start()
    
    def _preload_cards(self):
        """Background thread to preload cards from Jisho."""
        while self.current_index < len(self.cards) and self.loading:
            # Keep queue filled with preloaded cards
            if self.ready_cards.qsize() < self.preload_count:
                card = self.cards[self.current_index]
                word = strip_html(card['question'])
                info = get_jisho_info(word)
                
                if info and info['readings']:
                    self.ready_cards.put(info)
                    print(f"Preloaded card {self.current_index + 1}/{len(self.cards)}: {info['word']}")
                
                self.current_index += 1
            else:
                # Queue is full, wait a bit before checking again
                time.sleep(0.1)
        
        self.loading = False
    
    def _load_deck(self):
        """Background thread to load the Anki deck."""
        try:
            self.loading_status = "Connecting to Anki..."
            print("Connecting to Anki...")
            
            # Test connection to AnkiConnect
            try:
                deck_names = get_deck_names()
            except requests.exceptions.ConnectionError:
                self.loading_error = "Cannot connect to Anki. Please make sure Anki is running and AnkiConnect is installed."
                print(self.loading_error)
                return
            except Exception as conn_err:
                self.loading_error = f"Connection error: {str(conn_err)}"
                print(self.loading_error)
                return
            
            self.loading_status = f"Loading deck: {self.deck_name}..."
            print(f"Using deck: {self.deck_name}")
            card_ids = get_card_ids(self.deck_name)
            
            if not card_ids:
                self.loading_error = f"Deck '{self.deck_name}' not found or is empty. Please check the deck name in the code."
                print(self.loading_error)
                return
            
            self.loading_status = f"Loading {len(card_ids)} cards..."
            cards = get_cards_info(card_ids)
            
            self.loading_status = "Filtering cards..."
            # Filter for cards with kanji and exclude new cards
            kanji_cards = [card for card in cards if contains_kanji(card['question']) and card.get('type', 0) != 0]
            
            if not kanji_cards:
                self.loading_error = "No cards with kanji found in this deck. Try studying some cards first!"
                print(self.loading_error)
                return
            
            print(f"Loaded {len(kanji_cards)} kanji cards (excluding new cards).")
            random.shuffle(kanji_cards)
            
            # Set the cards and update state
            self.cards = kanji_cards
            self.loading_status = "Ready!"
            
            # Wait a moment to show "Ready!" message
            time.sleep(0.5)
            
            self.loading_deck = False
            self.state = STATE_MENU
            
            # Start background card preloading
            self.fetch_thread = threading.Thread(target=self._preload_cards, daemon=True)
            self.fetch_thread.start()
            
        except Exception as e:
            self.loading_error = f"Unexpected error: {str(e)}"
            print(self.loading_error)
    
    def update_button_positions(self):
        """Update button positions based on current window size."""
        self.play_button = pygame.Rect(self.width // 2 - 100, 250, 200, 60)
        self.resume_game_button = pygame.Rect(self.width // 2 - 100, 330, 200, 60)
        self.leaderboard_button = pygame.Rect(self.width // 2 - 100, 410, 200, 60)
        self.back_button = pygame.Rect(self.width // 2 - 100, 500, 200, 50)
        self.leave_button = pygame.Rect(self.width - 80, 10, 70, 30)
        self.pause_button = pygame.Rect(self.width - 160, 10, 70, 30)
        self.resume_button = pygame.Rect(self.width // 2 - 100, 250, 200, 60)
        self.save_quit_button = pygame.Rect(self.width // 2 - 100, 330, 200, 60)
        self.quit_button = pygame.Rect(self.width // 2 - 100, 410, 200, 60)
        self.normal_mode_button = pygame.Rect(self.width // 2 - 220, 250, 200, 80)
        self.fast_mode_button = pygame.Rect(self.width // 2 + 20, 250, 200, 80)
        self.retry_button = pygame.Rect(self.width // 2 - 100, self.height // 2 + 80, 200, 50)
    
    def start_game(self):
        """Go to mode selection."""
        self.state = STATE_MODE_SELECT
    
    def start_game_with_mode(self, mode):
        """Start a new game with the selected mode."""
        self.game_mode = mode
        self.state = STATE_COUNTDOWN
        self.countdown_start = pygame.time.get_ticks()
        self.countdown_number = 3
        self.score = 0
        self.points = 0
        self.total = 0
        self.streak = 0
        self.incorrect_answers = []
        self.animating = False
        self.game_over = False
    
    def retry_connection(self):
        """Retry connecting to Anki deck."""
        self.loading_error = None
        self.loading_status = "Initializing..."
        self.loading_deck = True
        self.state = STATE_LOADING
        loading_thread = threading.Thread(target=self._load_deck, daemon=True)
        loading_thread.start()
    
    def pause_game(self):
        """Pause the current game."""
        if self.question_start_time:
            # Save elapsed time before pausing
            self.paused_time_elapsed = time.time() - self.question_start_time
        self.state = STATE_PAUSED
    
    def resume_game(self):
        """Resume the paused game."""
        if self.question_start_time:
            # Restore the timer by adjusting start time
            self.question_start_time = time.time() - self.paused_time_elapsed
        self.state = STATE_PLAYING
    
    def save_game(self):
        """Initiate save game in background thread."""
        self.state = STATE_SAVING
        self.save_load_status = "Saving game..."
        self.save_load_error = None
        save_thread = threading.Thread(target=self._save_game_thread, daemon=True)
        save_thread.start()
    
    def _save_game_thread(self):
        """Save the current game state to a file (runs in background thread)."""
        try:
            # Stop loading thread
            self.loading = False
            
            # Convert Queue to list
            ready_cards_list = []
            temp_queue = Queue()
            while not self.ready_cards.empty():
                card = self.ready_cards.get()
                ready_cards_list.append(card)
                temp_queue.put(card)
            self.ready_cards = temp_queue  # Restore queue
            
            # Calculate elapsed time for current question
            elapsed_time = 0
            if self.question_start_time:
                elapsed_time = time.time() - self.question_start_time
            
            save_data = {
                'deck_name': self.deck_name,
                'game_mode': self.game_mode,
                'current_index': self.current_index,
                'score': self.score,
                'points': self.points,
                'total': self.total,
                'streak': self.streak,
                'incorrect_answers': self.incorrect_answers,
                'cards': self.cards,  # Shuffled card list
                'ready_cards': ready_cards_list,  # Preloaded cards
                'current_info': self.current_info,
                'elapsed_time': elapsed_time,
                'word_text': self.word_text if hasattr(self, 'word_text') else '',
                'timestamp': datetime.now().isoformat()
            }
            
            self.save_load_status = "Writing to file..."
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"Game saved to {SAVE_FILE}")
            self.save_load_status = "Game saved!"
            time.sleep(0.5)  # Brief pause to show success message
            self.state = STATE_MENU
        except Exception as e:
            print(f"Error saving game: {e}")
            self.save_load_error = f"Failed to save: {str(e)}"
            time.sleep(2)  # Show error longer
            self.state = STATE_MENU
    
    def load_game(self):
        """Initiate load game in background thread."""
        self.state = STATE_LOADING_SAVE
        self.save_load_status = "Loading saved game..."
        self.save_load_error = None
        load_thread = threading.Thread(target=self._load_game_thread, daemon=True)
        load_thread.start()
    
    def _load_game_thread(self):
        """Load game state from file (runs in background thread)."""
        try:
            self.save_load_status = "Reading save file..."
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.save_load_status = "Restoring game state..."
            # Restore game state
            self.deck_name = save_data['deck_name']
            self.game_mode = save_data['game_mode']
            self.current_index = save_data['current_index']
            self.score = save_data['score']
            self.points = save_data['points']
            self.total = save_data['total']
            self.streak = save_data['streak']
            self.incorrect_answers = save_data['incorrect_answers']
            self.cards = save_data['cards']
            self.current_info = save_data['current_info']
            self.word_text = save_data.get('word_text', '')
            
            # Restore ready cards queue
            self.ready_cards = Queue()
            for card_info in save_data['ready_cards']:
                self.ready_cards.put(card_info)
            
            # Restore timer
            elapsed = save_data.get('elapsed_time', 0)
            self.question_start_time = time.time() - elapsed
            self.paused_time_elapsed = elapsed
            
            # Reset UI state
            self.input_text = ""
            self.composition = ""
            self.romaji_buffer = ""
            self.input_active = True
            self.word_color = self.text_color
            self.animating = False
            self.game_over = False
            
            self.save_load_status = "Starting game..."
            # Restart background loading thread
            self.loading = True
            self.fetch_thread = threading.Thread(target=self._preload_cards, daemon=True)
            self.fetch_thread.start()
            
            time.sleep(0.3)  # Brief pause for smooth transition
            # Go directly to playing state
            self.state = STATE_PLAYING
            
            print(f"Game loaded from {SAVE_FILE}")
        except FileNotFoundError:
            print("No save file found")
            self.save_load_error = "No save file found"
            time.sleep(1.5)
            self.state = STATE_MENU
        except Exception as e:
            print(f"Error loading game: {e}")
            self.save_load_error = f"Failed to load: {str(e)}"
            time.sleep(2)
            self.state = STATE_MENU
    
    @staticmethod
    def has_save_file():
        """Check if a save file exists."""
        return os.path.isfile(SAVE_FILE)
    
    @staticmethod
    def delete_save_file():
        """Delete the save file."""
        try:
            if os.path.isfile(SAVE_FILE):
                os.remove(SAVE_FILE)
                print(f"Deleted {SAVE_FILE}")
        except Exception as e:
            print(f"Error deleting save file: {e}")
    
    def leave_game(self):
        """Leave the current game and save score."""
        if self.total > 0:  # Only save if at least one question was answered
            percentage = int(self.score / self.total * 100)
            avg_points = int(self.points / self.total)
            save_score_to_csv(self.score, self.total, self.points, percentage, avg_points)
        
        # Delete save file when leaving
        self.delete_save_file()
        
        # Show incorrect answers if there are any
        if self.incorrect_answers:
            self.state = STATE_REVIEW_INCORRECT
            self.review_scroll = 0  # Reset scroll
            self.review_cache = None  # Clear cache for fresh rendering
            self.review_cache_scroll = -1
        else:
            self.state = STATE_MENU
        self.animating = False
        self.game_over = False
    
    def load_next_word(self):
        """Load the next word from the preloaded queue."""
        # Reset UI state
        self.feedback_text = ""
        self.meaning_text = ""
        self.input_text = ""
        self.composition = ""
        self.romaji_buffer = ""
        self.input_active = False
        self.word_color = self.text_color
        self.word_zoom = 0.2
        self.word_distance = 1.0
        
        # Try to get a preloaded card
        if not self.ready_cards.empty():
            self.current_info = self.ready_cards.get()
            self._display_word()
        elif not self.loading:
            # No more cards available and loading is done
            self.show_final_score()
        else:
            # Still loading, show loading message
            self.status_text = "Loading cards..."
            self.word_text = "Please wait..."
            # Check again in a moment
            threading.Timer(0.5, self.load_next_word).start()
    
    def _display_word(self):
        """Display the word in the UI."""
        self.word_text = self.current_info['word']
        self.status_text = ""
        self.input_active = True
        self.question_start_time = time.time()  # Start timing the question
    
    def katakana_to_hiragana(self, text):
        """Convert katakana characters to hiragana."""
        result = ""
        for char in text:
            # Check if character is katakana (ァ-ヶ)
            if '\u30a1' <= char <= '\u30f6':
                # Convert to hiragana by subtracting 0x60
                result += chr(ord(char) - 0x60)
            else:
                result += char
        return result
    
    def convert_romaji_to_hiragana(self, romaji):
        """Convert romaji text to hiragana."""
        result = ""
        i = 0
        while i < len(romaji):
            # Check for double consonants (small っ)
            # If we have two identical consonants (except 'n'), convert first to っ
            if i + 2 <= len(romaji):
                current = romaji[i]
                next_char = romaji[i+1]
                # Check if it's a double consonant (not vowel, not 'n')
                if (current == next_char and 
                    current not in 'aeioun' and 
                    current.isalpha()):
                    result += 'っ'
                    i += 1
                    continue
            
            # Try 3-character combinations first
            if i + 3 <= len(romaji):
                three_char = romaji[i:i+3]
                if three_char in ROMAJI_TO_HIRAGANA:
                    result += ROMAJI_TO_HIRAGANA[three_char]
                    i += 3
                    continue
            
            # Try 2-character combinations
            if i + 2 <= len(romaji):
                two_char = romaji[i:i+2]
                if two_char in ROMAJI_TO_HIRAGANA:
                    result += ROMAJI_TO_HIRAGANA[two_char]
                    i += 2
                    continue
            
            # Try single character
            if i + 1 <= len(romaji):
                one_char = romaji[i:i+1]
                if one_char in ROMAJI_TO_HIRAGANA:
                    result += ROMAJI_TO_HIRAGANA[one_char]
                    i += 1
                    continue
            
            # If no match, keep the character as is
            result += romaji[i]
            i += 1
        
        return result
    
    def check_answer(self):
        """Check if the user's answer is correct."""
        if self.animating or not self.current_info or not self.input_text.strip():
            return
        
        # Validate that answer only contains hiragana characters
        answer = self.input_text.strip()
        if not all('\u3040' <= c <= '\u309f' for c in answer):
            # Flash the input to indicate invalid characters
            return
        
        self.animating = True
        self.input_active = False
        self.can_skip = True  # Allow skipping to next card
        
        correct_readings = self.current_info['readings']
        self.total += 1
        
        # Calculate time taken
        time_taken = time.time() - self.question_start_time
        
        # Normalize answer to hiragana for comparison (accept hiragana for katakana)
        normalized_answer = self.katakana_to_hiragana(answer)
        
        # Check if answer matches any of the valid readings
        is_correct = any(normalized_answer == self.katakana_to_hiragana(reading) for reading in correct_readings)
        
        if is_correct:
            self.score += 1
            self.streak += 1
            
            # Calculate points based on speed (max 100 points for <2s, decreasing to 10 points)
            if time_taken < 2:
                base_points = 100
            elif time_taken < 4:
                base_points = 75
            elif time_taken < 6:
                base_points = 50
            elif time_taken < 10:
                base_points = 25
            else:
                base_points = 10
            
            # Apply streak multiplier (1.0x to 3.0x based on streak)
            streak_multiplier = min(1.0 + (self.streak - 1) * 0.1, 3.0)
            points_earned = int(base_points * streak_multiplier)
            
            self.points += points_earned
            self.last_points_earned = points_earned
            
            self.animate_correct()
        else:
            self.streak = 0  # Reset streak on wrong answer
            self.last_points_earned = 0
            self.animate_incorrect(correct_readings)
    
    def animate_correct(self):
        """Animate correct answer."""
        self.animation_type = 'correct'
        self.animation_start = pygame.time.get_ticks()
        self.feedback_color = self.correct_color
        self.word_color = self.correct_color
        
        # Screen shake on high streaks (10+)
        if self.streak >= 10:
            self.screen_shake_intensity = min(5 + (self.streak - 10) * 2, 40)  # 5-40
        
        # Play sound
        if self.sound_correct:
            self.sound_correct.play()
        if self.streak >= 5 and self.sound_streak:
            pygame.time.set_timer(pygame.USEREVENT + 1, 100, 1)
        
        # Create success particles - MORE with higher streak
        particle_count = int(50 * pow(max(1, self.streak), 0.5))  # Square root scaling
        particle_count = min(particle_count, 300)  # Cap at 300
        for _ in range(particle_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            vx = random.uniform(-150, 150)
            vy = random.uniform(-200, -50)
            color = self.correct_color
            particle = Particle(x, y, color, vx, vy, random.uniform(0.5, 1.5), random.uniform(3, 8))
            self.particles.append(particle)
        
        # Star burst effects from corners at 10+ streak
        if self.streak >= 10:
            corners = [
                (0, 0),  # Top-left
                (self.width, 0),  # Top-right
                (0, self.height),  # Bottom-left
                (self.width, self.height)  # Bottom-right
            ]
            star_count = min(15 + self.streak, 40)  # More stars with higher streak
            for corner_x, corner_y in corners:
                for _ in range(star_count // 4):
                    # Stars burst outward from corner
                    angle = random.uniform(0, math.pi / 2)  # Quarter circle
                    if corner_x == 0 and corner_y == 0:  # Top-left
                        angle = random.uniform(0, math.pi / 2)
                    elif corner_x == self.width and corner_y == 0:  # Top-right
                        angle = random.uniform(math.pi / 2, math.pi)
                    elif corner_x == 0 and corner_y == self.height:  # Bottom-left
                        angle = random.uniform(-math.pi / 2, 0)
                    else:  # Bottom-right
                        angle = random.uniform(math.pi, 3 * math.pi / 2)
                    
                    speed = random.uniform(100, 300)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    self.particles.append(StarParticle(corner_x, corner_y, vx, vy))
        
        # Show meanings
        if self.current_info['meanings']:
            self.meaning_text = "Meanings: " + ", ".join(self.current_info['meanings'])
            self.meaning_color = self.correct_color
    
    def animate_incorrect(self, correct_readings):
        """Animate incorrect answer."""
        self.animation_type = 'incorrect'
        self.animation_start = pygame.time.get_ticks()
        # Display all valid readings separated by ' / '
        self.correct_answer_text = ' / '.join(correct_readings)
        self.feedback_color = self.incorrect_color
        self.word_color = self.incorrect_color
        
        # Track incorrect answer
        self.incorrect_answers.append({
            'word': self.current_info['word'],
            'correct_reading': ' / '.join(correct_readings),
            'your_answer': self.input_text.strip()
        })
        
        # Play sound
        if self.sound_incorrect:
            self.sound_incorrect.play()
        
        # Create failure particles
        for _ in range(40):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            vx = random.uniform(-100, 100)
            vy = random.uniform(-150, -30)
            color = self.incorrect_color
            particle = Particle(x, y, color, vx, vy, random.uniform(0.4, 1.2), random.uniform(3, 6))
            self.particles.append(particle)
        
        # Show meanings
        if self.current_info['meanings']:
            self.meaning_text = "Meanings: " + ", ".join(self.current_info['meanings'])
            self.meaning_color = self.incorrect_color
    
    def update_animation(self):
        """Update animation state."""
        if not self.animating:
            return
        
        # Fast mode: skip all animations and go straight to next word
        if self.game_mode == 'fast':
            self.next_word()
            return
        
        elapsed = pygame.time.get_ticks() - self.animation_start
        
        if self.animation_type == 'correct':
            # Flash animation
            if elapsed < 200:
                self.word_color = self.correct_color
            elif elapsed < 400:
                self.word_color = self.text_color
            elif elapsed < 600:
                self.word_color = self.correct_color
            else:
                self.word_color = self.text_color
            
            # End animation and move to next word
            if elapsed > 2000:
                self.next_word()
        
        elif self.animation_type == 'incorrect':
            # Shake animation
            if elapsed < 400:
                shake_sequence = [10, -10, 8, -8, 5, -5, 0]
                index = min(int(elapsed / 50), len(shake_sequence) - 1)
                self.shake_offset = shake_sequence[index]
            else:
                self.shake_offset = 0
                self.word_color = self.text_color
            
            # End animation and move to next word
            if elapsed > 3000:
                self.next_word()
    
    def next_word(self):
        """Move to the next word."""
        self.animating = False
        self.animation_type = None
        self.shake_offset = 0
        self.can_skip = False
        self.load_next_word()
    
    def show_final_score(self):
        """Show the final score."""
        self.state = STATE_GAME_OVER
        self.game_over = True
        self.word_text = "Game Over!"
        self.word_color = self.text_color
        self.feedback_text = ""
        self.meaning_text = ""
        percentage = int(self.score / self.total * 100) if self.total > 0 else 0
        avg_points = int(self.points / self.total) if self.total > 0 else 0
        
        # Save score to CSV
        save_score_to_csv(self.score, self.total, self.points, percentage, avg_points)
        
        # Delete save file when game completes naturally
        self.delete_save_file()
        
        # Get high scores
        self.high_scores = get_high_scores()
        
        self.status_text = f"Score: {self.score}/{self.total} ({percentage}%) | Points: {self.points} | Avg: {avg_points} pts/card"
        self.input_active = False
    
    def draw_text_wrapped(self, text, font, color, y_pos, max_width=500, draw_target=None):
        """Draw text with word wrapping."""
        if draw_target is None:
            draw_target = self.screen
        
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(self.width // 2, y_pos + i * 25))
            draw_target.blit(text_surface, text_rect)
    
    def draw(self):
        """Draw the UI based on current state."""
        if self.state == STATE_LOADING:
            self.draw_loading()
        elif self.state == STATE_LOADING_SAVE:
            self.draw_loading_save()
        elif self.state == STATE_SAVING:
            self.draw_saving()
        elif self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_MODE_SELECT:
            self.draw_mode_select()
        elif self.state == STATE_COUNTDOWN:
            self.draw_countdown()
        elif self.state == STATE_LEADERBOARD:
            self.draw_leaderboard()
        elif self.state == STATE_PLAYING:
            self.draw_game()
        elif self.state == STATE_PAUSED:
            self.draw_paused()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == STATE_REVIEW_INCORRECT:
            self.draw_review_incorrect()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu."""
        # Animated background
        base_color = self.bg_color
        wave = int(10 * math.sin(self.background_time * 0.5))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw background particles
        for i in range(12):
            # Create pseudo-random but deterministic positions
            base_x = (self.background_time * 25 + i * 137) % (self.width + 50)
            base_y = (i * 83) % self.height
            # Add pseudo-random offset using sine/cosine
            offset_x = 40 * math.sin(i * 3.14)
            offset_y = 35 * math.cos(i * 2.71)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(50 + 30 * math.sin(self.background_time + i))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.text_color[:3], alpha), (2, 2), 2)
            self.screen.blit(s, (int(x), int(y)))
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Japanese Vocab Quiz", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle (using Japanese-capable font)
        subtitle_font = pygame.font.SysFont(self.reading_font.get_name() if hasattr(self.reading_font, 'get_name') else 'msgothic', 20)
        subtitle = subtitle_font.render("日本語語彙クイズ", True, self.gray_color)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Play button
        play_color = self.button_hover_color if self.play_button_hover else self.button_color
        pygame.draw.rect(self.screen, play_color, self.play_button, border_radius=10)
        play_text = self.meaning_font.render("Play", True, (255, 255, 255))
        play_text_rect = play_text.get_rect(center=self.play_button.center)
        self.screen.blit(play_text, play_text_rect)
        
        # Resume Game button (only if save file exists)
        if self.has_save_file():
            resume_color = self.button_hover_color if self.resume_game_button_hover else self.correct_color
            pygame.draw.rect(self.screen, resume_color, self.resume_game_button, border_radius=10)
            resume_text = self.meaning_font.render("▶ Resume Game", True, (255, 255, 255))
            resume_text_rect = resume_text.get_rect(center=self.resume_game_button.center)
            self.screen.blit(resume_text, resume_text_rect)
        
        # Leaderboard button
        lb_color = self.button_hover_color if self.leaderboard_button_hover else self.button_color
        pygame.draw.rect(self.screen, lb_color, self.leaderboard_button, border_radius=10)
        lb_text = self.meaning_font.render("🏆 Leaderboard", True, (255, 255, 255))
        lb_text_rect = lb_text.get_rect(center=self.leaderboard_button.center)
        self.screen.blit(lb_text, lb_text_rect)
    
    def draw_mode_select(self):
        """Draw the mode selection screen."""
        # Animated background
        base_color = self.bg_color
        wave = int(10 * math.sin(self.background_time * 0.5))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw background particles
        for i in range(12):
            base_x = (self.background_time * 25 + i * 137) % (self.width + 50)
            base_y = (i * 83) % self.height
            offset_x = 40 * math.sin(i * 3.14)
            offset_y = 35 * math.cos(i * 2.71)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(50 + 30 * math.sin(self.background_time + i))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.text_color[:3], alpha), (2, 2), 2)
            self.screen.blit(s, (int(x), int(y)))
        
        # Title
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("Select Game Mode", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Normal mode button
        normal_color = self.button_hover_color if self.normal_mode_hover else self.button_color
        pygame.draw.rect(self.screen, normal_color, self.normal_mode_button, border_radius=10)
        normal_title = pygame.font.Font(None, 36).render("Normal", True, (255, 255, 255))
        normal_title_rect = normal_title.get_rect(center=(self.normal_mode_button.centerx, self.normal_mode_button.centery - 15))
        self.screen.blit(normal_title, normal_title_rect)
        normal_desc = self.score_font.render("Full animations", True, (255, 255, 255))
        normal_desc_rect = normal_desc.get_rect(center=(self.normal_mode_button.centerx, self.normal_mode_button.centery + 10))
        self.screen.blit(normal_desc, normal_desc_rect)
        normal_desc2 = self.score_font.render("& feedback", True, (255, 255, 255))
        normal_desc2_rect = normal_desc2.get_rect(center=(self.normal_mode_button.centerx, self.normal_mode_button.centery + 28))
        self.screen.blit(normal_desc2, normal_desc2_rect)
        
        # Fast mode button
        fast_color = self.button_hover_color if self.fast_mode_hover else self.correct_color
        pygame.draw.rect(self.screen, fast_color, self.fast_mode_button, border_radius=10)
        fast_title = pygame.font.Font(None, 36).render("Fast", True, (255, 255, 255))
        fast_title_rect = fast_title.get_rect(center=(self.fast_mode_button.centerx, self.fast_mode_button.centery - 15))
        self.screen.blit(fast_title, fast_title_rect)
        fast_desc = self.score_font.render("No animations", True, (255, 255, 255))
        fast_desc_rect = fast_desc.get_rect(center=(self.fast_mode_button.centerx, self.fast_mode_button.centery + 10))
        self.screen.blit(fast_desc, fast_desc_rect)
        fast_desc2 = self.score_font.render("Instant next word", True, (255, 255, 255))
        fast_desc2_rect = fast_desc2.get_rect(center=(self.fast_mode_button.centerx, self.fast_mode_button.centery + 28))
        self.screen.blit(fast_desc2, fast_desc2_rect)
        
        # Back button
        back_color = self.button_hover_color if self.back_button_hover else self.status_color
        pygame.draw.rect(self.screen, back_color, self.back_button, border_radius=10)
        back_text = self.meaning_font.render("← Back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
    
    def draw_loading(self):
        """Draw the loading screen."""
        # Animated background
        base_color = self.bg_color
        wave = int(15 * math.sin(self.background_time * 2))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw animated particles
        for i in range(15):
            # Create pseudo-random but deterministic positions
            base_x = (self.background_time * 45 + i * 119) % (self.width + 50)
            base_y = (i * 71) % self.height
            # Add pseudo-random offset using sine/cosine
            offset_x = 35 * math.sin(i * 2.97)
            offset_y = 30 * math.cos(i * 3.33)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(100 + 50 * math.sin(self.background_time * 2 + i))
            size = 3 + int(2 * math.sin(self.background_time * 3 + i * 0.5))
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.button_color[:3], alpha), (int(size), int(size)), int(size))
            self.screen.blit(s, (int(x), int(y)))
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Loading...", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Loading status
        if self.loading_error:
            status_color = self.incorrect_color
            status = self.loading_error
            # Use wrapped text for errors (they can be long)
            status_font = pygame.font.Font(None, 24)
            self.draw_text_wrapped(status, status_font, status_color, self.height // 2 + 20, max_width=700)
        else:
            status_color = self.button_color
            status = self.loading_status
            status_font = pygame.font.Font(None, 28)
            status_surface = status_font.render(status, True, status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
            self.screen.blit(status_surface, status_rect)
        
        # Animated loading bar
        if not self.loading_error:
            bar_width = 400
            bar_height = 20
            bar_x = (self.width - bar_width) // 2
            bar_y = self.height // 2 + 70
            
            # Background bar
            pygame.draw.rect(self.screen, self.gray_color, 
                           (bar_x, bar_y, bar_width, bar_height), 
                           border_radius=10)
            
            # Animated progress (indeterminate)
            progress_width = 100
            progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(self.background_time * 3)))
            pygame.draw.rect(self.screen, self.button_color,
                           (progress_x, bar_y, progress_width, bar_height),
                           border_radius=10)
        else:
            # Show retry button and quit hint
            button_color = self.button_hover_color if self.retry_button_hover else self.button_color
            pygame.draw.rect(self.screen, button_color, self.retry_button, border_radius=8)
            
            retry_text = "Retry"
            retry_font = pygame.font.Font(None, 32)
            retry_surface = retry_font.render(retry_text, True, self.text_color)
            retry_rect = retry_surface.get_rect(center=self.retry_button.center)
            self.screen.blit(retry_surface, retry_rect)
            
            hint_text = "Press ESC to quit or R to retry"
            hint_surface = self.meaning_font.render(hint_text, True, self.gray_color)
            hint_rect = hint_surface.get_rect(center=(self.width // 2, self.height // 2 + 150))
            self.screen.blit(hint_surface, hint_rect)
    
    def draw_loading_save(self):
        """Draw the loading save screen."""
        # Animated background
        base_color = self.bg_color
        wave = int(15 * math.sin(self.background_time * 2))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw animated particles
        for i in range(15):
            base_x = (self.background_time * 45 + i * 119) % (self.width + 50)
            base_y = (i * 71) % self.height
            offset_x = 35 * math.sin(i * 2.97)
            offset_y = 30 * math.cos(i * 3.33)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(100 + 50 * math.sin(self.background_time * 2 + i))
            size = 3 + int(2 * math.sin(self.background_time * 3 + i * 0.5))
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.correct_color[:3], alpha), (int(size), int(size)), int(size))
            self.screen.blit(s, (int(x), int(y)))
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Loading Game...", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Status
        if self.save_load_error:
            status_color = self.incorrect_color
            status = self.save_load_error
        else:
            status_color = self.correct_color
            status = self.save_load_status
        
        status_font = pygame.font.Font(None, 28)
        status_surface = status_font.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(status_surface, status_rect)
        
        # Animated loading bar
        if not self.save_load_error:
            bar_width = 400
            bar_height = 20
            bar_x = (self.width - bar_width) // 2
            bar_y = self.height // 2 + 70
            
            pygame.draw.rect(self.screen, self.gray_color, 
                           (bar_x, bar_y, bar_width, bar_height), 
                           border_radius=10)
            
            progress_width = 100
            progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(self.background_time * 3)))
            pygame.draw.rect(self.screen, self.correct_color,
                           (progress_x, bar_y, progress_width, bar_height),
                           border_radius=10)
    
    def draw_saving(self):
        """Draw the saving screen."""
        # Animated background
        base_color = self.bg_color
        wave = int(15 * math.sin(self.background_time * 2))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw animated particles
        for i in range(15):
            base_x = (self.background_time * 45 + i * 119) % (self.width + 50)
            base_y = (i * 71) % self.height
            offset_x = 35 * math.sin(i * 2.97)
            offset_y = 30 * math.cos(i * 3.33)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(100 + 50 * math.sin(self.background_time * 2 + i))
            size = 3 + int(2 * math.sin(self.background_time * 3 + i * 0.5))
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.correct_color[:3], alpha), (int(size), int(size)), int(size))
            self.screen.blit(s, (int(x), int(y)))
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Saving Game...", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Status
        if self.save_load_error:
            status_color = self.incorrect_color
            status = self.save_load_error
        else:
            status_color = self.correct_color
            status = self.save_load_status
        
        status_font = pygame.font.Font(None, 28)
        status_surface = status_font.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(status_surface, status_rect)
        
        # Animated loading bar
        if not self.save_load_error:
            bar_width = 400
            bar_height = 20
            bar_x = (self.width - bar_width) // 2
            bar_y = self.height // 2 + 70
            
            pygame.draw.rect(self.screen, self.gray_color, 
                           (bar_x, bar_y, bar_width, bar_height), 
                           border_radius=10)
            
            progress_width = 100
            progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(self.background_time * 3)))
            pygame.draw.rect(self.screen, self.correct_color,
                           (progress_x, bar_y, progress_width, bar_height),
                           border_radius=10)
    
    def draw_countdown(self):
        """Draw the countdown screen."""
        # Animated background
        base_color = self.bg_color
        wave = int(15 * math.sin(self.background_time * 2))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Calculate countdown
        elapsed = pygame.time.get_ticks() - self.countdown_start
        self.countdown_number = 3 - (elapsed // 1000)
        
        if self.countdown_number <= 0:
            self.state = STATE_PLAYING
            self.load_next_word()
            return
        
        # Draw countdown number with pulsing effect
        pulse = 0.7 + 0.3 * math.sin(elapsed / 150)
        countdown_font = pygame.font.Font(None, int(200 * pulse))
        countdown_text = countdown_font.render(str(self.countdown_number), True, self.text_color)
        countdown_rect = countdown_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(countdown_text, countdown_rect)
        
        # Draw "Get Ready!" text
        ready_font = pygame.font.Font(None, 36)
        ready_text = ready_font.render("Get Ready!", True, self.gray_color)
        ready_rect = ready_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
        self.screen.blit(ready_text, ready_rect)
    
    def draw_leaderboard(self):
        """Draw the leaderboard screen."""
        self.screen.fill(self.bg_color)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Leaderboard", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Get and display high scores
        if not self.high_scores:
            self.high_scores = get_high_scores()
        
        if self.high_scores:
            y_start = 120
            for i, hs in enumerate(self.high_scores[:10], 1):
                # Rank
                rank_color = self.correct_color if i <= 3 else self.text_color
                rank_text = f"{i}."
                rank_surface = self.meaning_font.render(rank_text, True, rank_color)
                self.screen.blit(rank_surface, (100, y_start + i * 35))
                
                # Score details
                score_text = f"{hs['points']} pts  |  {hs['percentage']}%  |  {hs['date']}"
                score_surface = self.meaning_font.render(score_text, True, self.text_color)
                self.screen.blit(score_surface, (140, y_start + i * 35))
        else:
            no_scores = self.meaning_font.render("No scores yet. Play to set a record!", True, self.gray_color)
            no_scores_rect = no_scores.get_rect(center=(self.width // 2, 200))
            self.screen.blit(no_scores, no_scores_rect)
        
        # Back button
        back_color = self.button_hover_color if self.back_button_hover else self.button_color
        pygame.draw.rect(self.screen, back_color, self.back_button, border_radius=10)
        back_text = self.meaning_font.render("← Back to Menu", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
    
    def draw_game(self):
        """Draw the main game screen."""
        # Streak-based background animation with rainbow effect at high streaks
        base_color = self.bg_color
        speed_multiplier = 1.0 + (self.streak * 0.6)
        wave_intensity = 10 + (self.streak * 3)
        wave = int(wave_intensity * math.sin(self.background_time * 0.5 * speed_multiplier))
        
        # Rainbow color shift for 15+ streak
        if self.streak >= 15:
            # Calculate RGB values using sine waves with phase offsets for rainbow
            time_factor = self.background_time * 2
            r = int(127 + 127 * math.sin(time_factor))
            g = int(127 + 127 * math.sin(time_factor + 2.094))  # 120 degrees
            b = int(127 + 127 * math.sin(time_factor + 4.189))  # 240 degrees
            # Blend with base color
            blend = 0.3  # 30% rainbow, 70% base
            bg_color = (
                max(0, min(255, int(base_color[0] * (1 - blend) + r * blend + wave))),
                max(0, min(255, int(base_color[1] * (1 - blend) + g * blend + wave))),
                max(0, min(255, int(base_color[2] * (1 - blend) + b * blend + wave)))
            )
        # Add color shift for high streaks
        elif self.streak >= 10:
            bg_color = (
                max(0, min(255, base_color[0] + wave + 20)),
                max(0, min(255, base_color[1] + wave + 10)),
                max(0, min(255, base_color[2] + wave))
            )
        elif self.streak >= 5:
            bg_color = (
                max(0, min(255, base_color[0] + wave + 10)),
                max(0, min(255, base_color[1] + wave + 5)),
                max(0, min(255, base_color[2] + wave))
            )
        else:
            bg_color = (
                max(0, min(255, base_color[0] + wave)),
                max(0, min(255, base_color[1] + wave)),
                max(0, min(255, base_color[2] + wave))
            )
        self.screen.fill(bg_color)
        
        # Create a surface for screen shake effect
        if self.screen_shake_intensity > 0:
            game_surface = pygame.Surface((self.width, self.height))
            game_surface.fill(bg_color)
            draw_target = game_surface
        else:
            draw_target = self.screen
        
        # Draw background particles (more with higher streak)
        particle_count = 5 + (self.streak * 4)  # More dramatic increase
        for i in range(min(particle_count, 80)):  # 80 max
            # Distribute particles across the screen with deterministic offset
            base_x = (self.background_time * (30 + self.streak * 5) + i * 150) % (self.width + 100)
            base_y = (i * 47) % self.height
            # Add consistent pseudo-random offset using sine/cosine based on particle index
            offset_x = 30 * math.sin(i * 2.7)  # Deterministic but looks random
            offset_y = 25 * math.cos(i * 3.1)
            x = base_x + offset_x
            y = base_y + offset_y
            alpha = int(50 + 30 * math.sin(self.background_time * speed_multiplier + i))
            size = 3 + (self.streak * 0.2)  # Particles grow with streak
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.text_color[:3], alpha), (int(size), int(size)), int(size))
            self.screen.blit(s, (int(x), int(y)))
        
        # Draw active particles
        for particle in self.particles:
            particle.draw(draw_target)
        
        # Draw pause button
        pause_color = self.button_hover_color if self.pause_button_hover else self.button_color
        pygame.draw.rect(draw_target, pause_color, self.pause_button, border_radius=5)
        pause_text = self.score_font.render("Pause", True, (255, 255, 255))
        pause_text_rect = pause_text.get_rect(center=self.pause_button.center)
        draw_target.blit(pause_text, pause_text_rect)
        
        # Draw leave button
        leave_color = self.incorrect_color if self.leave_button_hover else self.status_color
        pygame.draw.rect(draw_target, leave_color, self.leave_button, border_radius=5)
        leave_text = self.score_font.render("Leave", True, (255, 255, 255))
        leave_text_rect = leave_text.get_rect(center=self.leave_button.center)
        draw_target.blit(leave_text, leave_text_rect)
        
        # Draw score and points - PROMINENT
        score_bg = pygame.Surface((250, 45), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 100))
        draw_target.blit(score_bg, (10, 5))
        
        score_font_large = pygame.font.Font(None, 32)
        score_text = f"{self.score}/{self.total}"
        score_surface = score_font_large.render(score_text, True, self.text_color)
        draw_target.blit(score_surface, (20, 10))
        
        points_text = f"+{self.points} pts"
        points_surface = self.score_font.render(points_text, True, (255, 215, 0))
        draw_target.blit(points_surface, (20, 35))
        
        # Draw streak with fire particles
        if self.streak > 0:
            streak_bg = pygame.Surface((150, 35), pygame.SRCALPHA)
            streak_bg.fill((0, 0, 0, 120))
            streak_rect_bg = streak_bg.get_rect(center=(self.width // 2, 45))
            draw_target.blit(streak_bg, streak_rect_bg)
            
            streak_font_large = pygame.font.Font(None, 36)
            streak_text = f"{self.streak}x Streak"
            streak_color = self.correct_color if self.streak >= 5 else self.text_color
            streak_surface = streak_font_large.render(streak_text, True, streak_color)
            streak_rect = streak_surface.get_rect(center=(self.width // 2, 45))
            draw_target.blit(streak_surface, streak_rect)
            
            # Add fire particles around screen border for high streaks
            if self.streak >= 5:
                # More particles as streak increases
                particle_chance = min(0.3 + (self.streak * 0.05), 0.95)
                if random.random() < particle_chance:
                    # Choose a random edge of the screen
                    edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
                    if edge == 0:  # Top
                        fire_x = random.randint(0, self.width)
                        fire_y = 0
                    elif edge == 1:  # Right
                        fire_x = self.width
                        fire_y = random.randint(0, self.height)
                    elif edge == 2:  # Bottom
                        fire_x = random.randint(0, self.width)
                        fire_y = self.height
                    else:  # Left
                        fire_x = 0
                        fire_y = random.randint(0, self.height)
                    self.particles.append(FireParticle(fire_x, fire_y))
        
        # Update word zoom animation with smooth easing
        if not self.animating and self.input_active:
            self.word_zoom = min(1.0, self.word_zoom + 0.001)
            # Ease-out effect for smoother animation
            eased_zoom = 1.0 - math.pow(1.0 - self.word_zoom, 3)
            self.word_distance = 1.0 - (eased_zoom * 0.5)
        
        # Draw word with zoom effect
        base_size = 90
        # Apply ease-out for smoother zoom
        eased_zoom = 1.0 - math.pow(1.0 - self.word_zoom, 3)
        zoom_factor = 0.2 + (eased_zoom * 0.8)  # Start at 20% size
        word_size = int(base_size * zoom_factor)
        word_font_zoom = pygame.font.SysFont(self.word_font.get_name() if hasattr(self.word_font, 'get_name') else 'msgothic', word_size)
        word_surface = word_font_zoom.render(self.word_text, True, self.word_color)
        word_y = 120 + int(40 * self.word_distance)
        word_rect = word_surface.get_rect(center=(self.width // 2 + self.shake_offset, word_y))
        draw_target.blit(word_surface, word_rect)
        
        if not self.game_over:
            # Draw "Reading:" label
            label_surface = self.meaning_font.render("Reading:", True, self.text_color)
            label_rect = label_surface.get_rect(center=(self.width // 2, 280))
            draw_target.blit(label_surface, label_rect)
            
            # Draw input box
            input_rect = pygame.Rect(self.width // 2 - 150, 310, 300, 45)
            pygame.draw.rect(draw_target, (255, 255, 255), input_rect)
            pygame.draw.rect(draw_target, (0, 0, 0), input_rect, 2)
            
            # Draw input text with composition overlay
            display_text = self.input_text + self.composition
            input_surface = self.reading_font.render(display_text, True, (0, 0, 0))
            input_text_rect = input_surface.get_rect(center=input_rect.center)
            draw_target.blit(input_surface, input_text_rect)
            
            # Draw button
            self.button_rect = pygame.Rect(self.width // 2 - 150, 380, 300, 50)
            button_color = self.button_hover_color if self.button_hover else self.button_color
            pygame.draw.rect(draw_target, button_color, self.button_rect, border_radius=5)
            button_text = "Submit"
            button_surface = self.meaning_font.render(button_text, True, (255, 255, 255))
            button_text_rect = button_surface.get_rect(center=self.button_rect.center)
            draw_target.blit(button_surface, button_text_rect)
        
        # Draw meanings
        if self.meaning_text:
            self.draw_text_wrapped(self.meaning_text, self.meaning_font, self.meaning_color, 480, draw_target=draw_target)
        
        # Draw status
        if self.status_text:
            status_surface = self.meaning_font.render(self.status_text, True, self.status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, 600))
            draw_target.blit(status_surface, status_rect)
        
        # Show correct answer when incorrect (drawn late so it's on top)
        if self.animating and self.animation_type == 'incorrect':
            if hasattr(self, 'correct_answer_text'):
                correct_label_font = pygame.font.Font(None, 32)
                correct_label = correct_label_font.render("Correct:", True, self.text_color)
                correct_label_rect = correct_label.get_rect(center=(self.width // 2, 520))
                draw_target.blit(correct_label, correct_label_rect)
                
                correct_font = pygame.font.SysFont(self.reading_font.get_name() if hasattr(self.reading_font, 'get_name') else 'msgothic', 56)
                correct_surface = correct_font.render(self.correct_answer_text, True, self.incorrect_color)
                correct_rect = correct_surface.get_rect(center=(self.width // 2, 565))
                draw_target.blit(correct_surface, correct_rect)
        
        # Full-screen flash animation on answer (drawn LAST to cover everything)
        if self.animating and self.animation_type:
            elapsed = pygame.time.get_ticks() - self.animation_start
            if elapsed < 400:  # Flash for 400ms
                # Create a brighter, more visible flash
                flash_alpha = int(180 * (1.0 - elapsed / 400))
                flash_surface = pygame.Surface((self.width, self.height))
                if self.animation_type == 'correct':
                    flash_surface.fill(self.correct_color)
                else:
                    flash_surface.fill(self.incorrect_color)
                flash_surface.set_alpha(flash_alpha)
                draw_target.blit(flash_surface, (0, 0))
        
        # Apply screen shake by blitting the game surface with offset
        if self.screen_shake_intensity > 0:
            self.screen.blit(game_surface, (int(self.screen_shake_x), int(self.screen_shake_y)))
    
    def draw_game_over(self):
        """Draw the game over screen."""
        self.screen.fill(self.bg_color)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Game Over!", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Final score
        if self.status_text:
            status_surface = self.meaning_font.render(self.status_text, True, self.status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, 140))
            self.screen.blit(status_surface, status_rect)
        
        # High scores
        if hasattr(self, 'high_scores') and self.high_scores:
            hs_y = 180
            hs_title = self.meaning_font.render("🏆 High Scores 🏆", True, (255, 215, 0))
            self.screen.blit(hs_title, hs_title.get_rect(center=(self.width // 2, hs_y)))
            
            for i, hs in enumerate(self.high_scores[:3], 1):
                hs_text = f"{i}. {hs['points']} pts ({hs['percentage']}%) - {hs['date']}"
                hs_surface = self.meaning_font.render(hs_text, True, self.text_color)
                hs_rect = hs_surface.get_rect(center=(self.width // 2, hs_y + 25 + i * 25))
                self.screen.blit(hs_surface, hs_rect)
        
        # Back to menu button
        self.button_rect = pygame.Rect(self.width // 2 - 100, 380, 200, 50)
        button_color = self.button_hover_color if self.button_hover else self.button_color
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=10)
        button_surface = self.meaning_font.render("← Back to Menu", True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(button_surface, button_text_rect)
    
    def draw_paused(self):
        """Draw the pause screen."""
        # Semi-transparent overlay over game
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((20, 30, 40))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("PAUSED", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Current score
        score_text = f"Score: {self.score}/{self.total}  |  Points: {self.points}"
        if self.streak > 0:
            score_text += f"  |  Streak: {self.streak}x"
        score_surface = self.meaning_font.render(score_text, True, self.gray_color)
        score_rect = score_surface.get_rect(center=(self.width // 2, 180))
        self.screen.blit(score_surface, score_rect)
        
        # Resume button
        resume_color = self.button_hover_color if self.resume_button_hover else self.button_color
        pygame.draw.rect(self.screen, resume_color, self.resume_button, border_radius=10)
        resume_text = self.meaning_font.render("▶ Resume", True, (255, 255, 255))
        resume_text_rect = resume_text.get_rect(center=self.resume_button.center)
        self.screen.blit(resume_text, resume_text_rect)
        
        # Save & Quit button
        save_quit_color = self.button_hover_color if self.save_quit_button_hover else self.correct_color
        pygame.draw.rect(self.screen, save_quit_color, self.save_quit_button, border_radius=10)
        save_quit_text = self.meaning_font.render("💾 Save & Quit", True, (255, 255, 255))
        save_quit_text_rect = save_quit_text.get_rect(center=self.save_quit_button.center)
        self.screen.blit(save_quit_text, save_quit_text_rect)
        
        # Quit button
        quit_color = self.button_hover_color if self.quit_button_hover else self.incorrect_color
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=10)
        quit_text = self.meaning_font.render("← Quit to Menu", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
    
    def draw_review_incorrect(self):
        """Draw the review incorrect answers screen."""
        # Static background (no animation for better performance)
        self.screen.fill(self.bg_color)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Review Incorrect Answers", True, self.incorrect_color)
        title_rect = title.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Count
        count_text = f"{len(self.incorrect_answers)} incorrect answer(s)"
        count_surface = self.meaning_font.render(count_text, True, self.gray_color)
        count_rect = count_surface.get_rect(center=(self.width // 2, 80))
        self.screen.blit(count_surface, count_rect)
        
        # Scrolling hint if there are many items
        if len(self.incorrect_answers) > 7:
            hint_text = "(Scroll to see all)"
            hint_surface = self.score_font.render(hint_text, True, self.gray_color)
            hint_rect = hint_surface.get_rect(center=(self.width // 2, 100))
            self.screen.blit(hint_surface, hint_rect)
        
        # Create a scrollable area
        scroll_area_top = 120
        scroll_area_bottom = 560
        scroll_area_height = scroll_area_bottom - scroll_area_top
        
        # Calculate total content height
        item_height = 60
        total_content_height = len(self.incorrect_answers) * item_height
        
        # Clamp scroll position
        max_scroll = max(0, total_content_height - scroll_area_height)
        self.review_scroll = max(0, min(self.review_scroll, max_scroll))
        
        # Cache rendered content to avoid re-rendering text every frame
        # Only regenerate if cache is invalid or scroll position changed significantly
        if (self.review_cache is None or 
            abs(self.review_cache_scroll - self.review_scroll) > 1):
            
            self.review_cache_scroll = self.review_scroll
            
            # Create a clipping surface for the scrollable area
            scroll_surface = pygame.Surface((self.width, scroll_area_height))
            scroll_surface.fill(self.bg_color)
            
            # Pre-render fonts (cached for the session)
            if not hasattr(self, '_review_fonts_cached'):
                self._review_word_font = pygame.font.SysFont(
                    self.reading_font.get_name() if hasattr(self.reading_font, 'get_name') else 'msgothic', 36)
                self._review_reading_font = pygame.font.SysFont(
                    self.reading_font.get_name() if hasattr(self.reading_font, 'get_name') else 'msgothic', 24)
                self._review_fonts_cached = True
            
            # Draw items onto the scroll surface
            for i, ans in enumerate(self.incorrect_answers):
                y_pos = i * item_height - self.review_scroll
                
                # Only draw if visible in scroll area (with margin)
                if -item_height < y_pos < scroll_area_height + item_height:
                    # Word
                    word_surface = self._review_word_font.render(ans['word'], True, self.text_color)
                    word_rect = word_surface.get_rect(center=(self.width // 2, y_pos + 20))
                    scroll_surface.blit(word_surface, word_rect)
                    
                    # Correct reading (in green)
                    correct_surface = self._review_reading_font.render(f"✓ {ans['correct_reading']}", True, self.correct_color)
                    correct_rect = correct_surface.get_rect(center=(self.width // 2, y_pos + 45))
                    scroll_surface.blit(correct_surface, correct_rect)
                    
                    # Your answer (in red) if different
                    if ans['your_answer']:
                        your_surface = self._review_reading_font.render(f"✗ {ans['your_answer']}", True, self.incorrect_color)
                        your_rect = your_surface.get_rect(center=(self.width // 2 + 150, y_pos + 45))
                        scroll_surface.blit(your_surface, your_rect)
            
            self.review_cache = scroll_surface
        
        # Blit the cached scroll surface to the main screen
        self.screen.blit(self.review_cache, (0, scroll_area_top))
        
        # Draw scrollbar if needed
        if total_content_height > scroll_area_height:
            scrollbar_x = self.width - 15
            scrollbar_height = max(30, int((scroll_area_height / total_content_height) * scroll_area_height))
            scrollbar_y = scroll_area_top + int((self.review_scroll / max_scroll) * (scroll_area_height - scrollbar_height))
            
            pygame.draw.rect(self.screen, self.gray_color, 
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height), 
                           border_radius=5)
        
        # Back to menu button
        self.button_rect = pygame.Rect(self.width // 2 - 100, 580, 200, 50)
        button_color = self.button_hover_color if self.button_hover else self.button_color
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=10)
        button_surface = self.meaning_font.render("← Back to Menu", True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(button_surface, button_text_rect)
    
    def run(self):
        """Start the game loop."""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            self.background_time += dt
            
            # Update particles
            self.particles = [p for p in self.particles if p.update(dt)]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle window resize
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    # Update all button positions
                    self.update_button_positions()
                
                # Streak sound event
                elif event.type == pygame.USEREVENT + 1:
                    if self.sound_streak:
                        self.sound_streak.play()
                
                # Handle text input with romaji conversion
                elif event.type == pygame.TEXTINPUT:
                    if self.state == STATE_PLAYING and self.input_active and not self.animating:
                        # Check if it's already hiragana/katakana (from IME)
                        if any('\u3040' <= c <= '\u30ff' for c in event.text):
                            self.input_text += event.text
                        else:
                            # Add to romaji buffer
                            self.romaji_buffer += event.text.lower()
                            # Convert to hiragana
                            self.input_text = self.convert_romaji_to_hiragana(self.romaji_buffer)
                        print(f"Input: {self.input_text} (romaji: {self.romaji_buffer})")  # Debug output
                
                # Handle IME composition (in-progress text)
                elif event.type == pygame.TEXTEDITING:
                    if self.state == STATE_PLAYING:
                        self.composition = event.text
                        print(f"Composing: {self.composition}")  # Debug output
                
                elif event.type == pygame.KEYDOWN:
                    if self.state == STATE_LOADING and self.loading_error:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_r:
                            self.retry_connection()
                    elif self.state == STATE_PAUSED:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                            self.resume_game()
                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_ESCAPE:
                            self.pause_game()
                        elif event.key == pygame.K_RETURN:
                            if self.input_active and not self.animating:
                                self.check_answer()
                            elif self.can_skip and self.animating:
                                # Skip animation and go to next word
                                self.next_word()
                        elif self.input_active and not self.animating:
                            if event.key == pygame.K_BACKSPACE:
                                if len(self.input_text) > 0:
                                    # Remove last hiragana character
                                    self.input_text = self.input_text[:-1]
                                    # Rebuild romaji buffer to match the remaining hiragana
                                    # Keep removing from romaji buffer until conversion matches
                                    while len(self.romaji_buffer) > 0:
                                        test_conversion = self.convert_romaji_to_hiragana(self.romaji_buffer)
                                        if test_conversion == self.input_text:
                                            break
                                        self.romaji_buffer = self.romaji_buffer[:-1]
                                print(f"Input: {self.input_text} (romaji: {self.romaji_buffer})")  # Debug output
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle mouse wheel for scrolling in review screen
                    if self.state == STATE_REVIEW_INCORRECT:
                        if event.button == 4:  # Scroll up
                            self.review_scroll -= 30
                        elif event.button == 5:  # Scroll down
                            self.review_scroll += 30
                    
                    self.handle_mouse_click(event.pos)
                
                elif event.type == pygame.MOUSEMOTION:
                    self.update_button_hover(event.pos)
            
            # Update animations
            self.update_animation()
            
            # Update screen shake
            if self.screen_shake_intensity > 0:
                self.screen_shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_intensity *= 0.9  # Decay shake
                if self.screen_shake_intensity < 0.5:
                    self.screen_shake_intensity = 0
                    self.screen_shake_x = 0
                    self.screen_shake_y = 0
            
            # Draw everything
            self.draw()
        
        pygame.quit()
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks based on current state."""
        if self.state == STATE_LOADING and self.loading_error:
            if self.retry_button.collidepoint(pos):
                self.retry_connection()
        elif self.state == STATE_MENU:
            if self.play_button.collidepoint(pos):
                self.start_game()
            elif self.has_save_file() and self.resume_game_button.collidepoint(pos):
                self.load_game()
            elif self.leaderboard_button.collidepoint(pos):
                self.state = STATE_LEADERBOARD
                self.high_scores = get_high_scores()
        
        elif self.state == STATE_MODE_SELECT:
            if self.normal_mode_button.collidepoint(pos):
                self.start_game_with_mode('normal')
            elif self.fast_mode_button.collidepoint(pos):
                self.start_game_with_mode('fast')
            elif self.back_button.collidepoint(pos):
                self.state = STATE_MENU
        
        elif self.state == STATE_LEADERBOARD:
            if self.back_button.collidepoint(pos):
                self.state = STATE_MENU
        
        elif self.state == STATE_PLAYING:
            if self.button_rect.collidepoint(pos) and not self.animating:
                self.check_answer()
            elif self.pause_button.collidepoint(pos):
                self.pause_game()
            elif self.leave_button.collidepoint(pos):
                self.leave_game()
        
        elif self.state == STATE_PAUSED:
            if self.resume_button.collidepoint(pos):
                self.resume_game()
            elif self.save_quit_button.collidepoint(pos):
                self.save_game()
            elif self.quit_button.collidepoint(pos):
                self.leave_game()
        
        elif self.state == STATE_GAME_OVER:
            if self.button_rect.collidepoint(pos):
                self.state = STATE_MENU
        
        elif self.state == STATE_REVIEW_INCORRECT:
            if self.button_rect.collidepoint(pos):
                self.state = STATE_MENU
    
    def update_button_hover(self, pos):
        """Update button hover states based on mouse position."""
        if self.state == STATE_LOADING and self.loading_error:
            self.retry_button_hover = self.retry_button.collidepoint(pos)
        
        elif self.state == STATE_MENU:
            self.play_button_hover = self.play_button.collidepoint(pos)
            self.resume_game_button_hover = self.resume_game_button.collidepoint(pos)
            self.leaderboard_button_hover = self.leaderboard_button.collidepoint(pos)
        
        elif self.state == STATE_MODE_SELECT:
            self.normal_mode_hover = self.normal_mode_button.collidepoint(pos)
            self.fast_mode_hover = self.fast_mode_button.collidepoint(pos)
            self.back_button_hover = self.back_button.collidepoint(pos)
        
        elif self.state == STATE_LEADERBOARD:
            self.back_button_hover = self.back_button.collidepoint(pos)
        
        elif self.state == STATE_PLAYING:
            self.button_hover = self.button_rect.collidepoint(pos)
            self.pause_button_hover = self.pause_button.collidepoint(pos)
            self.leave_button_hover = self.leave_button.collidepoint(pos)
        
        elif self.state == STATE_PAUSED:
            self.resume_button_hover = self.resume_button.collidepoint(pos)
            self.save_quit_button_hover = self.save_quit_button.collidepoint(pos)
            self.quit_button_hover = self.quit_button.collidepoint(pos)
        
        elif self.state == STATE_GAME_OVER:
            self.button_hover = self.button_rect.collidepoint(pos)
        
        elif self.state == STATE_REVIEW_INCORRECT:
            self.button_hover = self.button_rect.collidepoint(pos)

if __name__ == "__main__":
    main()
