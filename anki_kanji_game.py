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

ANKI_CONNECT_URL = "http://localhost:8765"

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
    Returns a dict with 'word', 'reading', and 'meanings', or None if not found.
    """
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Find the first matching entry
        entries = data.get('data', [])
        if not entries:
            return None
        
        entry = entries[0]
        japanese = entry.get('japanese', [])
        if not japanese:
            return None
        
        # Get the word and reading
        word_text = japanese[0].get('word', word)
        reading = japanese[0].get('reading', '')
        
        # Get English meanings
        senses = entry.get('senses', [])
        meanings = []
        for sense in senses:
            eng_defs = sense.get('english_definitions', [])
            meanings.extend(eng_defs)
        
        return {
            'word': word_text,
            'reading': reading,
            'meanings': meanings[:3]  # Limit to first 3 meanings
        }
    except Exception as e:
        print(f"Error fetching from Jisho: {e}")
        return None

def main():
    print("Connecting to Anki...")
    deck_name = "日本語::Mining"
    print(f"Using deck: {deck_name}")
    card_ids = get_card_ids(deck_name)
    cards = get_cards_info(card_ids)
    kanji_cards = [card for card in cards if contains_kanji(card['question'])]
    if not kanji_cards:
        print("No cards with kanji found in this deck.")
        return
    print(f"Loaded {len(kanji_cards)} kanji cards.")
    random.shuffle(kanji_cards)
    
    # Launch GUI
    app = VocabGameGUI(kanji_cards)
    app.run()

class VocabGameGUI:
    def __init__(self, cards):
        self.cards = cards
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
        self.last_points_earned = 0  # Points earned on last answer
        
        # Particle system
        self.particles = []
        self.background_time = 0
        
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
        self.width = 600
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height))
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
        
        # Enable text input for IME support
        pygame.key.start_text_input()
        
        # Button
        self.button_rect = pygame.Rect(200, 330, 200, 50)
        self.button_hover = False
        
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
        
        # Start background card loading
        self.fetch_thread = threading.Thread(target=self._preload_cards, daemon=True)
        self.fetch_thread.start()
        
        # Load first word
        self.load_next_word()
    
    def _preload_cards(self):
        """Background thread to preload cards from Jisho."""
        while self.current_index < len(self.cards) and self.loading:
            # Keep queue filled with preloaded cards
            if self.ready_cards.qsize() < self.preload_count:
                card = self.cards[self.current_index]
                word = strip_html(card['question'])
                info = get_jisho_info(word)
                
                if info and info['reading']:
                    self.ready_cards.put(info)
                    print(f"Preloaded card {self.current_index + 1}/{len(self.cards)}: {info['word']}")
                
                self.current_index += 1
            else:
                # Queue is full, wait a bit before checking again
                time.sleep(0.1)
        
        self.loading = False
    
    def load_next_word(self):
        """Load the next word from the preloaded queue."""
        # Reset UI state
        self.feedback_text = ""
        self.meaning_text = ""
        self.input_text = ""
        self.composition = ""
        self.input_active = False
        self.word_color = self.text_color
        
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
    
    def check_answer(self):
        """Check if the user's answer is correct."""
        if self.animating or not self.current_info or not self.input_text.strip():
            return
        
        self.animating = True
        self.input_active = False
        self.can_skip = True  # Allow skipping to next card
        
        correct_reading = self.current_info['reading']
        self.total += 1
        
        # Calculate time taken
        time_taken = time.time() - self.question_start_time
        
        if self.input_text.strip() == correct_reading:
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
            self.animate_incorrect(correct_reading)
    
    def animate_correct(self):
        """Animate correct answer."""
        self.animation_type = 'correct'
        self.animation_start = pygame.time.get_ticks()
        self.feedback_text = f"✓ Correct! +{self.last_points_earned} pts"
        self.feedback_color = self.correct_color
        self.word_color = self.correct_color
        
        # Play sound
        if self.sound_correct:
            self.sound_correct.play()
        if self.streak >= 5 and self.sound_streak:
            pygame.time.set_timer(pygame.USEREVENT + 1, 100, 1)
        
        # Create success particles
        for _ in range(30):
            x = random.randint(100, 500)
            y = random.randint(100, 200)
            vx = random.uniform(-100, 100)
            vy = random.uniform(-150, -50)
            color = self.correct_color
            particle = Particle(x, y, color, vx, vy, random.uniform(0.5, 1.0), random.uniform(2, 5))
            self.particles.append(particle)
        
        # Show meanings
        if self.current_info['meanings']:
            self.meaning_text = "Meanings: " + ", ".join(self.current_info['meanings'])
            self.meaning_color = self.correct_color
    
    def animate_incorrect(self, correct_reading):
        """Animate incorrect answer."""
        self.animation_type = 'incorrect'
        self.animation_start = pygame.time.get_ticks()
        self.feedback_text = f"✗ Incorrect: {correct_reading}"
        self.feedback_color = self.incorrect_color
        self.word_color = self.incorrect_color
        
        # Play sound
        if self.sound_incorrect:
            self.sound_incorrect.play()
        
        # Create failure particles
        for _ in range(20):
            x = random.randint(150, 450)
            y = random.randint(100, 200)
            vx = random.uniform(-50, 50)
            vy = random.uniform(-100, -30)
            color = self.incorrect_color
            particle = Particle(x, y, color, vx, vy, random.uniform(0.4, 0.8), random.uniform(2, 4))
            self.particles.append(particle)
        
        # Show meanings
        if self.current_info['meanings']:
            self.meaning_text = "Meanings: " + ", ".join(self.current_info['meanings'])
            self.meaning_color = self.incorrect_color
    
    def update_animation(self):
        """Update animation state."""
        if not self.animating:
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
        self.game_over = True
        self.word_text = "Game Over!"
        self.word_color = self.text_color
        self.feedback_text = ""
        self.meaning_text = ""
        percentage = int(self.score / self.total * 100) if self.total > 0 else 0
        avg_points = int(self.points / self.total) if self.total > 0 else 0
        
        # Save score to CSV
        save_score_to_csv(self.score, self.total, self.points, percentage, avg_points)
        
        # Get high scores
        self.high_scores = get_high_scores()
        
        self.status_text = f"Score: {self.score}/{self.total} ({percentage}%) | Points: {self.points} | Avg: {avg_points} pts/card"
        self.input_active = False
    
    def draw_text_wrapped(self, text, font, color, y_pos, max_width=500):
        """Draw text with word wrapping."""
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
            self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        """Draw the UI."""
        # Animated background
        base_color = self.bg_color
        wave = int(10 * math.sin(self.background_time * 0.5))
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
        self.screen.fill(bg_color)
        
        # Draw background particles (subtle)
        for i in range(5):
            x = (self.background_time * 20 + i * 120) % self.width
            y = 50 + i * 80
            alpha = int(50 + 30 * math.sin(self.background_time + i))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.text_color[:3], alpha), (2, 2), 2)
            self.screen.blit(s, (x, y))
        
        # Draw active particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw score and points
        score_text = f"Score: {self.score}/{self.total}  |  Points: {self.points}"
        score_surface = self.score_font.render(score_text, True, self.text_color)
        score_rect = score_surface.get_rect(center=(self.width // 2, 20))
        self.screen.blit(score_surface, score_rect)
        
        # Draw streak with fire particles
        if self.streak > 0:
            streak_text = f"🔥 Streak: {self.streak}x"
            streak_color = self.correct_color if self.streak >= 5 else self.text_color
            streak_surface = self.score_font.render(streak_text, True, streak_color)
            streak_rect = streak_surface.get_rect(center=(self.width // 2, 45))
            self.screen.blit(streak_surface, streak_rect)
            
            # Add fire particles for high streaks
            if self.streak >= 5 and random.random() < 0.3:
                fire_x = streak_rect.left + random.randint(-10, 10)
                fire_y = streak_rect.centery + random.randint(-5, 5)
                self.particles.append(FireParticle(fire_x, fire_y))
        
        # Draw word (with shake offset)
        word_surface = self.word_font.render(self.word_text, True, self.word_color)
        word_y = 115 if self.streak > 0 else 100
        word_rect = word_surface.get_rect(center=(self.width // 2 + self.shake_offset, word_y))
        self.screen.blit(word_surface, word_rect)
        
        # Draw feedback
        if self.feedback_text:
            feedback_surface = self.reading_font.render(self.feedback_text, True, self.feedback_color)
            feedback_rect = feedback_surface.get_rect(center=(self.width // 2, 170))
            self.screen.blit(feedback_surface, feedback_rect)
        
        if not self.game_over:
            # Draw "Reading:" label
            label_surface = self.meaning_font.render("Reading:", True, self.text_color)
            label_rect = label_surface.get_rect(center=(self.width // 2, 220))
            self.screen.blit(label_surface, label_rect)
            
            # Draw input box
            input_rect = pygame.Rect(150, 240, 300, 40)
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), input_rect, 2)
            
            # Draw input text with composition overlay
            display_text = self.input_text + self.composition
            input_surface = self.reading_font.render(display_text, True, (0, 0, 0))
            input_text_rect = input_surface.get_rect(center=input_rect.center)
            self.screen.blit(input_surface, input_text_rect)
            
            # Draw button
            button_color = self.button_hover_color if self.button_hover else self.button_color
            pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=5)
            button_text = "Submit"
            button_surface = self.meaning_font.render(button_text, True, (255, 255, 255))
            button_text_rect = button_surface.get_rect(center=self.button_rect.center)
            self.screen.blit(button_surface, button_text_rect)
        else:
            # Draw close button
            close_button = pygame.Rect(200, 330, 200, 50)
            button_color = self.button_hover_color if self.button_hover else self.button_color
            pygame.draw.rect(self.screen, button_color, close_button, border_radius=5)
            button_surface = self.meaning_font.render("Close", True, (255, 255, 255))
            button_text_rect = button_surface.get_rect(center=close_button.center)
            self.screen.blit(button_surface, button_text_rect)
            
            # Draw high scores
            if hasattr(self, 'high_scores') and self.high_scores:
                hs_y = 250
                hs_title = self.meaning_font.render("🏆 High Scores 🏆", True, (255, 215, 0))
                self.screen.blit(hs_title, hs_title.get_rect(center=(self.width // 2, hs_y)))
                
                for i, hs in enumerate(self.high_scores[:3], 1):
                    hs_text = f"{i}. {hs['points']} pts ({hs['percentage']}%) - {hs['date']}"
                    hs_surface = self.meaning_font.render(hs_text, True, self.text_color)
                    hs_rect = hs_surface.get_rect(center=(self.width // 2, hs_y + 25 + i * 25))
                    self.screen.blit(hs_surface, hs_rect)
        
        # Draw meanings
        if self.meaning_text:
            self.draw_text_wrapped(self.meaning_text, self.meaning_font, self.meaning_color, 400)
        
        # Draw status
        if self.status_text:
            status_surface = self.meaning_font.render(self.status_text, True, self.status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, 460))
            self.screen.blit(status_surface, status_rect)
        
        pygame.display.flip()
    
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
                
                # Streak sound event
                elif event.type == pygame.USEREVENT + 1:
                    if self.sound_streak:
                        self.sound_streak.play()
                
                # Handle IME text input (for Japanese/other languages)
                elif event.type == pygame.TEXTINPUT:
                    if self.input_active and not self.animating:
                        self.input_text += event.text
                        print(f"Input: {self.input_text}")  # Debug output
                
                # Handle IME composition (in-progress text)
                elif event.type == pygame.TEXTEDITING:
                    self.composition = event.text
                    print(f"Composing: {self.composition}")  # Debug output
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        continue
                    
                    if event.key == pygame.K_RETURN:
                        if self.input_active and not self.animating:
                            self.check_answer()
                        elif self.can_skip and self.animating:
                            # Skip animation and go to next word
                            self.next_word()
                    elif self.input_active and not self.animating:
                        if event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                            print(f"Input: {self.input_text}")  # Debug output
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        if self.game_over:
                            running = False
                        else:
                            self.check_answer()
                
                elif event.type == pygame.MOUSEMOTION:
                    self.button_hover = self.button_rect.collidepoint(event.pos)
            
            # Update animations
            self.update_animation()
            
            # Draw everything
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    main()
