import requests
import random
import re
import time
from html.parser import HTMLParser

ANKI_CONNECT_URL = "http://localhost:8765"

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
    score = 0
    total = 0
    random.shuffle(kanji_cards)
    
    for card in kanji_cards:
        word = strip_html(card['question'])
        
        # Look up word in Jisho
        print("\nLooking up word in dictionary...")
        info = get_jisho_info(word)
        
        if not info or not info['reading']:
            print(f"Could not find '{word}' in dictionary. Skipping...")
            time.sleep(0.5)
            continue
        
        total += 1
        print("\n" + "="*50)
        print(f"Word: {info['word']}")
        
        # Ask for reading
        answer = input("\nEnter reading (hiragana): ").strip()
        
        if answer == info['reading']:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Incorrect. The reading is: {info['reading']}")
        
        # Show meanings
        if info['meanings']:
            print(f"\nMeaning(s): {', '.join(info['meanings'])}")
        
        time.sleep(1)  # Avoid hammering Jisho.org
    
    print("\n" + "="*50)
    print(f"Game over! Your score: {score}/{total}")

if __name__ == "__main__":
    main()
