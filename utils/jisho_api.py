"""
Jisho.org API integration.
"""

import requests


def get_jisho_info(word):
    """
    Query Jisho.org for word information.
    
    Args:
        word: Japanese word to look up
        
    Returns:
        Dict with 'word', 'readings' (list), and 'meanings', or None if not found
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
