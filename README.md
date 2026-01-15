# JP Vocab Kanji Game

This is a Python game that connects to your Anki account using AnkiConnect, lets you select a deck, and quizzes you on kanji vocabulary by asking for their pronunciation.

## Features
- Connects to your local Anki via AnkiConnect
- Lets you select any deck
- Filters cards containing kanji
- Prompts you to enter the pronunciation for each kanji card
- Keeps score

## Requirements
- Anki (desktop app)
- AnkiConnect (Anki add-on)
- Python 3.7+
- `requests` Python package

## Setup Instructions

### 1. Install Anki
Download and install Anki from the official website: https://apps.ankiweb.net/

### 2. Install AnkiConnect
1. Open Anki.
2. Go to `Tools > Add-ons > Get Add-ons...`
3. Enter the code: `2055492159` and click OK.
4. Restart Anki.
5. Make sure Anki is running whenever you use the game.

More info: https://ankiweb.net/shared/info/2055492159

### 3. Install Python and Dependencies
1. Make sure Python 3.7 or newer is installed: https://www.python.org/downloads/
2. Open a terminal in the project folder.
3. Install the required package:

```
pip install requests
```

### 4. Run the Game
1. Start Anki and ensure AnkiConnect is enabled.
2. Open a terminal in the project folder.
3. Run the game:

```
python anki_kanji_game.py
```

4. Follow the prompts to select a deck and play!

## Troubleshooting
- If you get connection errors, make sure Anki is running and AnkiConnect is installed.
- The game only works with decks containing cards with kanji (Japanese characters).
- You can customize your decks in Anki to include more kanji cards.

## Customization
- You can modify the game logic in `anki_kanji_game.py` to add more features, such as hints, GUI, or support for other languages.

## License
MIT
