"""
Main game GUI class.
"""

import pygame
import random
import time
import threading
import math
import json
import os
from queue import Queue
from datetime import datetime

from config import *
from utils import (
    get_deck_names, get_card_ids, get_cards_info, get_jisho_info,
    strip_html, contains_kanji, katakana_to_hiragana, 
    convert_romaji_to_hiragana, generate_sound
)
from game import save_score_to_csv, get_high_scores, calculate_points
from ui.particles import Particle, FireParticle, StarParticle


class VocabGameGUI:
    """Main GUI class for the vocabulary game."""
    
    def __init__(self, cards, deck_name=None):
        self.cards = cards
        self.deck_name = deck_name or DEFAULT_DECK_NAME
        self.current_index = 0
        self.score = 0
        self.points = 0
        self.total = 0
        self.streak = 0
        self.current_info = None
        self.animating = False
        self.game_over = False
        self.can_skip = False
        self.question_start_time = None
        self.paused_time_elapsed = 0
        self.last_points_earned = 0
        self.incorrect_answers = []
        
        # Loading state
        self.loading_deck = (cards is None)
        self.loading_status = "Initializing..."
        self.loading_error = None
        self.save_load_status = ""
        self.save_load_error = None
        
        # Game state
        self.state = STATE_LOADING if self.loading_deck else STATE_MENU
        self.high_scores = []
        self.countdown_start = 0
        self.countdown_number = 3
        self.game_mode = 'normal'
        
        # Time attack mode variables
        self.time_attack_duration = TIME_ATTACK_DURATION
        self.time_attack_start_time = 0
        self.time_attack_paused_elapsed = 0
        
        # Word zoom animation
        self.word_zoom = 0.2
        self.word_distance = 1.0
        
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
        self.preload_count = PRELOAD_COUNT
        self.loading = True
        self.fetch_thread = None
        
        # Create window
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Colors
        self.bg_color = COLOR_BG
        self.text_color = COLOR_TEXT
        self.correct_color = COLOR_CORRECT
        self.incorrect_color = COLOR_INCORRECT
        self.button_color = COLOR_BUTTON
        self.button_hover_color = COLOR_BUTTON_HOVER
        self.gray_color = COLOR_GRAY
        self.status_color = COLOR_STATUS
        
        # Initialize fonts
        self._initialize_fonts()
        
        # Input state
        self.input_text = ""
        self.input_active = False
        self.composition = ""
        self.romaji_buffer = ""
        
        # Enable text input for IME support
        pygame.key.start_text_input()
        
        # Initialize buttons
        self._initialize_buttons()
        
        # Animation state
        self.feedback_text = ""
        self.feedback_color = self.text_color
        self.word_color = self.text_color
        self.meaning_text = ""
        self.meaning_color = self.gray_color
        self.status_text = ""
        self.animation_start = 0
        self.animation_type = None
        self.shake_offset = 0
        
        # Review screen scroll
        self.review_scroll = 0
        self.review_cache = None
        self.review_cache_scroll = -1
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Start deck loading if needed
        if self.loading_deck:
            loading_thread = threading.Thread(target=self._load_deck, daemon=True)
            loading_thread.start()
    
    def _initialize_fonts(self):
        """Initialize fonts with Japanese support."""
        self.word_font = None
        for font_name in JAPANESE_FONTS:
            try:
                self.word_font = pygame.font.SysFont(font_name, 72)
                test = self.word_font.render('あ', True, (255, 255, 255))
                if test.get_width() > 0:
                    break
            except:
                continue
        
        if not self.word_font:
            self.word_font = pygame.font.Font(None, 72)
        
        self.reading_font = None
        for font_name in JAPANESE_FONTS:
            try:
                self.reading_font = pygame.font.SysFont(font_name, 32)
                test = self.reading_font.render('あ', True, (0, 0, 0))
                if test.get_width() > 0:
                    break
            except:
                continue
        
        if not self.reading_font:
            self.reading_font = pygame.font.Font(None, 32)
        
        self.meaning_font = pygame.font.Font(None, 24)
        self.score_font = pygame.font.Font(None, 20)
    
    def _initialize_buttons(self):
        """Initialize all button rectangles."""
        self.button_rect = pygame.Rect(self.width // 2 - 100, 330, 200, 50)
        self.button_hover = False
        
        # Menu buttons
        self.play_button = pygame.Rect(self.width // 2 - 100, 250, 200, 60)
        self.resume_game_button = pygame.Rect(self.width // 2 - 100, 330, 200, 60)
        self.leaderboard_button = pygame.Rect(self.width // 2 - 100, 410, 200, 60)
        self.back_button = pygame.Rect(self.width // 2 - 100, 500, 200, 50)
        self.pause_button = pygame.Rect(self.width - 80, 10, 70, 30)
        self.play_button_hover = False
        self.resume_game_button_hover = False
        self.leaderboard_button_hover = False
        self.back_button_hover = False
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
        self.time_attack_button = pygame.Rect(self.width // 2 - 100, 360, 200, 80)
        self.normal_mode_hover = False
        self.fast_mode_hover = False
        self.time_attack_hover = False
    
    def update_button_positions(self):
        """Update button positions based on current window size."""
        self._initialize_buttons()
    
    def _preload_cards(self):
        """Background thread to preload cards from Jisho."""
        while self.current_index < len(self.cards) and self.loading:
            if self.ready_cards.qsize() < self.preload_count:
                card = self.cards[self.current_index]
                word = strip_html(card['question'])
                info = get_jisho_info(word)
                
                if info and info['readings']:
                    self.ready_cards.put(info)
                    print(f"Preloaded card {self.current_index + 1}/{len(self.cards)}: {info['word']}")
                
                self.current_index += 1
            else:
                time.sleep(0.1)
        
        self.loading = False
    
    def _load_deck(self):
        """Background thread to load the Anki deck."""
        try:
            self.loading_status = "Connecting to Anki..."
            print("Connecting to Anki...")
            
            try:
                deck_names = get_deck_names()
            except Exception as conn_err:
                self.loading_error = f"Cannot connect to Anki. Please make sure Anki is running and AnkiConnect is installed."
                print(self.loading_error)
                return
            
            self.loading_status = f"Loading deck: {self.deck_name}..."
            print(f"Using deck: {self.deck_name}")
            card_ids = get_card_ids(self.deck_name)
            
            if not card_ids:
                self.loading_error = f"Deck '{self.deck_name}' not found or is empty."
                print(self.loading_error)
                return
            
            self.loading_status = f"Loading {len(card_ids)} cards..."
            cards = get_cards_info(card_ids)
            
            self.loading_status = "Filtering cards..."
            kanji_cards = [card for card in cards if contains_kanji(card['question']) and card.get('type', 0) != 0]
            
            if not kanji_cards:
                self.loading_error = "No cards with kanji found in this deck."
                print(self.loading_error)
                return
            
            print(f"Loaded {len(kanji_cards)} kanji cards.")
            random.shuffle(kanji_cards)
            
            self.cards = kanji_cards
            self.loading_status = "Ready!"
            time.sleep(0.5)
            
            self.loading_deck = False
            self.state = STATE_MENU
            
        except Exception as e:
            self.loading_error = f"Unexpected error: {str(e)}"
            print(self.loading_error)
    
    def start_game(self):
        """Go to mode selection."""
        self.state = STATE_MODE_SELECT
    
    def _reset_card_state(self):
        """Reset card loading state for a fresh game."""
        self.loading = False
        if self.fetch_thread and self.fetch_thread.is_alive():
            time.sleep(0.1)
        
        self.ready_cards = Queue()
        self.current_index = 0
        random.shuffle(self.cards)
        self.current_info = None
    
    def start_game_with_mode(self, mode):
        """Start a new game with the selected mode."""
        self.game_mode = mode
        self.state = STATE_COUNTDOWN
        self.countdown_start = pygame.time.get_ticks()
        self.countdown_number = 3
        self.score = 0
        self.points = 0
        
        if mode == 'time_attack':
            self.time_attack_start_time = 0
            self.time_attack_paused_elapsed = 0
        self.total = 0
        self.streak = 0
        self.incorrect_answers = []
        self.animating = False
        self.game_over = False
        
        self._reset_card_state()
    
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
            self.paused_time_elapsed = time.time() - self.question_start_time
        
        if self.game_mode == 'time_attack' and self.time_attack_start_time > 0:
            self.time_attack_paused_elapsed = (pygame.time.get_ticks() - self.time_attack_start_time) / 1000.0
        
        self.state = STATE_PAUSED
    
    def resume_game(self):
        """Resume the paused game."""
        if self.question_start_time:
            self.question_start_time = time.time() - self.paused_time_elapsed
        
        if self.game_mode == 'time_attack' and self.time_attack_paused_elapsed > 0:
            self.time_attack_start_time = pygame.time.get_ticks() - int(self.time_attack_paused_elapsed * 1000)
            self.time_attack_paused_elapsed = 0
        
        self.state = STATE_PLAYING
    
    def save_game(self):
        """Initiate save game in background thread."""
        self.state = STATE_SAVING
        self.save_load_status = "Saving game..."
        self.save_load_error = None
        save_thread = threading.Thread(target=self._save_game_thread, daemon=True)
        save_thread.start()
    
    def _save_game_thread(self):
        """Save the current game state to a file."""
        try:
            self.loading = False
            
            ready_cards_list = []
            temp_queue = Queue()
            while not self.ready_cards.empty():
                card = self.ready_cards.get()
                ready_cards_list.append(card)
                temp_queue.put(card)
            self.ready_cards = temp_queue
            
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
                'cards': self.cards,
                'ready_cards': ready_cards_list,
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
            time.sleep(0.5)
            self.state = STATE_MENU
        except Exception as e:
            print(f"Error saving game: {e}")
            self.save_load_error = f"Failed to save: {str(e)}"
            time.sleep(2)
            self.state = STATE_MENU
    
    def load_game(self):
        """Initiate load game in background thread."""
        self.state = STATE_LOADING_SAVE
        self.save_load_status = "Loading saved game..."
        self.save_load_error = None
        load_thread = threading.Thread(target=self._load_game_thread, daemon=True)
        load_thread.start()
    
    def _load_game_thread(self):
        """Load game state from file."""
        try:
            self.save_load_status = "Reading save file..."
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.save_load_status = "Restoring game state..."
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
            
            self.ready_cards = Queue()
            for card_info in save_data['ready_cards']:
                self.ready_cards.put(card_info)
            
            elapsed = save_data.get('elapsed_time', 0)
            self.question_start_time = time.time() - elapsed
            self.paused_time_elapsed = elapsed
            
            self.input_text = ""
            self.composition = ""
            self.romaji_buffer = ""
            self.input_active = True
            self.word_color = self.text_color
            self.animating = False
            self.game_over = False
            
            self.save_load_status = "Starting game..."
            self.loading = True
            self.fetch_thread = threading.Thread(target=self._preload_cards, daemon=True)
            self.fetch_thread.start()
            
            time.sleep(0.3)
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
        if self.total > 0:
            percentage = int(self.score / self.total * 100)
            avg_points = int(self.points / self.total)
            save_score_to_csv(self.score, self.total, self.points, percentage, avg_points, self.game_mode)
        
        self.delete_save_file()
        
        if self.incorrect_answers:
            self.state = STATE_REVIEW_INCORRECT
            self.review_scroll = 0
            self.review_cache = None
            self.review_cache_scroll = -1
        else:
            self.state = STATE_MENU
        self.animating = False
        self.game_over = False
    
    def load_next_word(self):
        """Load the next word from the preloaded queue."""
        self.feedback_text = ""
        self.meaning_text = ""
        self.input_text = ""
        self.composition = ""
        self.romaji_buffer = ""
        self.input_active = False
        self.word_color = self.text_color
        self.word_zoom = 0.2
        self.word_distance = 1.0
        
        if not self.ready_cards.empty():
            self.current_info = self.ready_cards.get()
            self._display_word()
        elif not self.loading:
            self.show_final_score()
        else:
            self.status_text = "Loading cards..."
            self.word_text = "Please wait..."
            threading.Timer(0.5, self.load_next_word).start()
    
    def _display_word(self):
        """Display the word in the UI."""
        self.word_text = self.current_info['word']
        self.status_text = ""
        self.input_active = True
        self.question_start_time = time.time()
    
    def check_answer(self):
        """Check if the user's answer is correct."""
        if self.animating or not self.current_info or not self.input_text.strip():
            return
        
        answer = self.input_text.strip()
        if not all('\u3040' <= c <= '\u309f' for c in answer):
            return
        
        self.animating = True
        self.input_active = False
        self.can_skip = True
        
        correct_readings = self.current_info['readings']
        self.total += 1
        
        time_taken = time.time() - self.question_start_time
        
        normalized_answer = katakana_to_hiragana(answer)
        is_correct = any(normalized_answer == katakana_to_hiragana(reading) for reading in correct_readings)
        
        if is_correct:
            self.score += 1
            self.streak += 1
            
            points_earned, _, _ = calculate_points(time_taken, self.streak)
            self.points += points_earned
            self.last_points_earned = points_earned
            
            self.animate_correct()
        else:
            self.streak = 0
            self.last_points_earned = 0
            self.animate_incorrect(correct_readings)
    
    def animate_correct(self):
        """Animate correct answer."""
        self.animation_type = 'correct'
        self.animation_start = pygame.time.get_ticks()
        self.feedback_color = self.correct_color
        self.word_color = self.correct_color
        
        if self.streak >= 10:
            self.screen_shake_intensity = min(5 + (self.streak - 10) * 2, 40)
        
        if self.sound_correct:
            self.sound_correct.play()
        if self.streak >= 5 and self.sound_streak:
            pygame.time.set_timer(pygame.USEREVENT + 1, 100, 1)
        
        # Create particles
        particle_count = int(50 * pow(max(1, self.streak), 0.5))
        particle_count = min(particle_count, 300)
        for _ in range(particle_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            vx = random.uniform(-150, 150)
            vy = random.uniform(-200, -50)
            color = self.correct_color
            particle = Particle(x, y, color, vx, vy, random.uniform(0.5, 1.5), random.uniform(3, 8))
            self.particles.append(particle)
        
        # Star burst effects at 10+ streak
        if self.streak >= 10:
            corners = [(0, 0), (self.width, 0), (0, self.height), (self.width, self.height)]
            star_count = min(15 + self.streak, 40)
            for corner_x, corner_y in corners:
                for _ in range(star_count // 4):
                    angle = random.uniform(0, math.pi / 2)
                    if corner_x == 0 and corner_y == 0:
                        angle = random.uniform(0, math.pi / 2)
                    elif corner_x == self.width and corner_y == 0:
                        angle = random.uniform(math.pi / 2, math.pi)
                    elif corner_x == 0 and corner_y == self.height:
                        angle = random.uniform(-math.pi / 2, 0)
                    else:
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
        self.correct_answer_text = ' / '.join(correct_readings)
        self.feedback_color = self.incorrect_color
        self.word_color = self.incorrect_color
        
        self.incorrect_answers.append({
            'word': self.current_info['word'],
            'correct_reading': ' / '.join(correct_readings),
            'your_answer': self.input_text.strip()
        })
        
        if self.sound_incorrect:
            self.sound_incorrect.play()
        
        # Create particles
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
        
        if self.game_mode == 'fast' or self.game_mode == 'time_attack':
            self.next_word()
            return
        
        elapsed = pygame.time.get_ticks() - self.animation_start
        
        if self.animation_type == 'correct':
            if elapsed < 200:
                self.word_color = self.correct_color
            elif elapsed < 400:
                self.word_color = self.text_color
            elif elapsed < 600:
                self.word_color = self.correct_color
            else:
                self.word_color = self.text_color
            
            if elapsed > 2000:
                self.next_word()
        
        elif self.animation_type == 'incorrect':
            if elapsed < 400:
                shake_sequence = [10, -10, 8, -8, 5, -5, 0]
                index = min(int(elapsed / 50), len(shake_sequence) - 1)
                self.shake_offset = shake_sequence[index]
            else:
                self.shake_offset = 0
                self.word_color = self.text_color
            
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
        
        save_score_to_csv(self.score, self.total, self.points, percentage, avg_points, self.game_mode)
        self.delete_save_file()
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
        # Import screen drawing methods here to avoid circular imports
        from ui.screens.menu_screen import draw_menu, draw_mode_select
        from ui.screens.game_screen import draw_game, draw_countdown, draw_paused, draw_game_over
        from ui.screens.leaderboard_screen import draw_leaderboard
        from ui.screens.review_screen import draw_review_incorrect
        from ui.screens.loading_screen import draw_loading, draw_loading_save, draw_saving
        
        if self.state == STATE_LOADING:
            draw_loading(self)
        elif self.state == STATE_LOADING_SAVE:
            draw_loading_save(self)
        elif self.state == STATE_SAVING:
            draw_saving(self)
        elif self.state == STATE_MENU:
            draw_menu(self)
        elif self.state == STATE_MODE_SELECT:
            draw_mode_select(self)
        elif self.state == STATE_COUNTDOWN:
            draw_countdown(self)
        elif self.state == STATE_LEADERBOARD:
            draw_leaderboard(self)
        elif self.state == STATE_PLAYING:
            draw_game(self)
        elif self.state == STATE_PAUSED:
            draw_paused(self)
        elif self.state == STATE_GAME_OVER:
            draw_game_over(self)
        elif self.state == STATE_REVIEW_INCORRECT:
            draw_review_incorrect(self)
        
        pygame.display.flip()
    
    def run(self):
        """Start the game loop."""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.background_time += dt
            
            # Update particles
            self.particles = [p for p in self.particles if p.update(dt)]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.update_button_positions()
                
                elif event.type == pygame.USEREVENT + 1:
                    if self.sound_streak:
                        self.sound_streak.play()
                
                elif event.type == pygame.TEXTINPUT:
                    if self.state == STATE_PLAYING and self.input_active and not self.animating:
                        if any('\u3040' <= c <= '\u30ff' for c in event.text):
                            self.input_text += event.text
                        else:
                            self.romaji_buffer += event.text.lower()
                            self.input_text = convert_romaji_to_hiragana(self.romaji_buffer)
                        print(f"Input: {self.input_text} (romaji: {self.romaji_buffer})")
                
                elif event.type == pygame.TEXTEDITING:
                    if self.state == STATE_PLAYING:
                        self.composition = event.text
                        print(f"Composing: {self.composition}")
                
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event, running)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == STATE_REVIEW_INCORRECT:
                        if event.button == 4:
                            self.review_scroll -= 30
                        elif event.button == 5:
                            self.review_scroll += 30
                    
                    self.handle_mouse_click(event.pos)
                
                elif event.type == pygame.MOUSEMOTION:
                    self.update_button_hover(event.pos)
            
            # Check time attack expiration
            if self.state == STATE_PLAYING and self.game_mode == 'time_attack' and self.time_attack_start_time > 0:
                elapsed_time = (pygame.time.get_ticks() - self.time_attack_start_time) / 1000.0
                if elapsed_time >= self.time_attack_duration:
                    self.show_final_score()
            
            # Update animations
            self.update_animation()
            
            # Update screen shake
            if self.screen_shake_intensity > 0:
                self.screen_shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_intensity *= 0.9
                if self.screen_shake_intensity < 0.5:
                    self.screen_shake_intensity = 0
                    self.screen_shake_x = 0
                    self.screen_shake_y = 0
            
            # Draw everything
            self.draw()
        
        pygame.quit()
    
    def _handle_keydown(self, event, running):
        """Handle keyboard input."""
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
                    self.next_word()
            elif self.input_active and not self.animating:
                if event.key == pygame.K_BACKSPACE:
                    if len(self.input_text) > 0:
                        self.input_text = self.input_text[:-1]
                        while len(self.romaji_buffer) > 0:
                            test_conversion = convert_romaji_to_hiragana(self.romaji_buffer)
                            if test_conversion == self.input_text:
                                break
                            self.romaji_buffer = self.romaji_buffer[:-1]
                    print(f"Input: {self.input_text} (romaji: {self.romaji_buffer})")
    
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
            elif self.time_attack_button.collidepoint(pos):
                self.start_game_with_mode('time_attack')
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
            self.time_attack_hover = self.time_attack_button.collidepoint(pos)
            self.back_button_hover = self.back_button.collidepoint(pos)
        
        elif self.state == STATE_LEADERBOARD:
            self.back_button_hover = self.back_button.collidepoint(pos)
        
        elif self.state == STATE_PLAYING:
            self.button_hover = self.button_rect.collidepoint(pos)
            self.pause_button_hover = self.pause_button.collidepoint(pos)
        
        elif self.state == STATE_PAUSED:
            self.resume_button_hover = self.resume_button.collidepoint(pos)
            self.save_quit_button_hover = self.save_quit_button.collidepoint(pos)
            self.quit_button_hover = self.quit_button.collidepoint(pos)
        
        elif self.state == STATE_GAME_OVER:
            self.button_hover = self.button_rect.collidepoint(pos)
        
        elif self.state == STATE_REVIEW_INCORRECT:
            self.button_hover = self.button_rect.collidepoint(pos)
