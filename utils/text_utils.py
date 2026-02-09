"""
Text processing utilities for Japanese text.
"""

import re
from html.parser import HTMLParser
from config import ROMAJI_TO_HIRAGANA


class HTMLStripper(HTMLParser):
    """HTML parser that strips all tags and returns plain text."""
    
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
    """
    Remove HTML tags and return plain text.
    
    Args:
        html: HTML string to strip
        
    Returns:
        Plain text string
    """
    s = HTMLStripper()
    s.feed(html)
    return s.get_data().strip()


def contains_kanji(text):
    """
    Check if a string contains kanji (CJK Unified Ideographs).
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains kanji, False otherwise
    """
    return re.search(r"[\u4e00-\u9fff]", text) is not None


def katakana_to_hiragana(text):
    """
    Convert katakana characters to hiragana.
    
    Args:
        text: Text containing katakana
        
    Returns:
        Text with katakana converted to hiragana
    """
    result = ""
    for char in text:
        # Check if character is katakana (ァ-ヶ)
        if '\u30a1' <= char <= '\u30f6':
            # Convert to hiragana by subtracting 0x60
            result += chr(ord(char) - 0x60)
        else:
            result += char
    return result


def convert_romaji_to_hiragana(romaji):
    """
    Convert romaji text to hiragana.
    
    Args:
        romaji: Romaji string to convert
        
    Returns:
        Hiragana string
    """
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
