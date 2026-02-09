# Japanese Vocabulary Game

An interactive Japanese vocabulary quiz game with a beautiful GUI that connects to your Anki deck via AnkiConnect. Test your kanji reading skills with time-based scoring, streak multipliers, and visual effects!

## Project Structure

The project is now organized into a modular structure for better maintainability:

```
jp_vocab_game/
├── main.py                      # Entry point - run this to start the game
├── config.py                    # Game configuration and constants
├── requirements.txt             # Python package dependencies
├── README.md                    # This file
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── anki_api.py             # AnkiConnect API integration
│   ├── jisho_api.py            # Jisho.org API integration
│   ├── text_utils.py           # Text processing (romaji, HTML, etc.)
│   └── sound_utils.py          # Sound generation
│
├── game/                        # Game logic
│   ├── __init__.py
│   └── scoring.py              # Scoring system and leaderboards
│
└── ui/                          # User interface components
    ├── __init__.py
    ├── particles.py            # Particle effects
    ├── game_gui.py             # Main game GUI class
    └── screens/                # Screen renderers
        ├── __init__.py
        ├── loading_screen.py   # Loading/saving screens
        ├── menu_screen.py      # Menu and mode selection
        ├── game_screen.py      # Main gameplay screen
        ├── leaderboard_screen.py # Leaderboard display
        └── review_screen.py    # Incorrect answers review
```

## ⚠️ Migration from Old Version

The project has been refactored from a single `anki_kanji_game.py` file into the modular structure above. The old file is still present as a backup, but **you should now use `main.py` to run the game**.

You can safely delete `anki_kanji_game.py` once you've confirmed the new version works correctly.

## Features

### Core Gameplay
- **Anki Integration**: Automatically loads kanji cards from your Anki deck (default: "日本語::Mining")
- **Pronunciation Quiz**: Type hiragana readings for displayed kanji words
- **Multiple Valid Readings**: Accepts all valid readings for each word via Jisho.org API
- **Romaji Input**: Automatic romaji to hiragana conversion - type in romaji and it converts to hiragana
- **IME Support**: Full support for Japanese Input Method Editors

### Scoring System
- **Time-Based Points**: Faster answers earn more points (100 points for <2s, decreasing to 10 points for >10s)
- **Streak Multiplier**: Build streaks for up to 3x point multiplier (increases by 0.1x per streak)
- **High Score Tracking**: Scores automatically saved to CSV file with date, percentage, and points

### Game Modes
- **Normal Mode**: Full animations and feedback with answer review
- **Fast Mode**: Skip animations for rapid-fire practice

### Visual Effects
- **Particle Systems**: Dynamic particle effects for correct/incorrect answers
- **Streak Effects**: More particles and screen shake with higher streaks
- **Smooth Animations**: Animated feedback, word zoom, and background effects
- **Sound Effects**: Audio feedback for correct answers and streaks

### Additional Features
- **Pause/Resume**: Pause the game at any time without losing progress
- **Save/Load**: Save your progress mid-game and continue later
- **Review Mode**: Review all incorrect answers at the end with meanings from Jisho.org
- **Leaderboard**: View your top 5 high scores
- **Resizable Window**: Responsive design adapts to any window size
- **Retry Button**: Easy retry if Anki connection fails (press R or click Retry button)

## Requirements
- **Anki** (desktop app)
- **AnkiConnect** (Anki add-on #2055492159)
- **Python 3.7+**
- **Python Packages**:
  - `pygame` (for GUI and game engine)
  - `requests` (for AnkiConnect and Jisho.org API)

## Setup Instructions

### 1. Install Anki
Download and install Anki from: https://apps.ankiweb.net/

### 2. Install AnkiConnect
1. Open Anki
2. Go to `Tools > Add-ons > Get Add-ons...`
3. Enter code: `2055492159`
4. Click OK and restart Anki

More info: https://ankiweb.net/shared/info/2055492159

### 3. Install Python and Dependencies
1. Install Python 3.7 or newer: https://www.python.org/downloads/
2. Open a terminal in the project folder
3. Install required packages:

```bash
pip install pygame requests
```

### 4. Configure Your Deck
By default, the game loads the deck named "日本語::Mining". To use a different deck:
1. Open `config.py`
2. Find the line: `DEFAULT_DECK_NAME = "日本語::Mining"`
3. Change it to your deck name (e.g., `DEFAULT_DECK_NAME = "Japanese::Core 2000"`)

### 5. Run the Game
1. Start Anki (keep it running in the background)
2. Run the game:

```bash
python main.py
```

3. Wait for the deck to load, then select your game mode and start playing!

## How to Play

1. **Launch**: The game loads your Anki deck and filters for kanji cards
2. **Mode Selection**: Choose Normal or Fast mode
3. **Quiz**: A kanji word appears - type its hiragana reading
4. **Input**: 
   - Type romaji (e.g., "konnichiha" → "こんにちは")
   - Or use Japanese IME for direct hiragana input
   - Press Enter to submit
5. **Scoring**: Faster answers = more points, build streaks for multipliers!
6. **Review**: At game end, review all incorrect answers with meanings

### Controls
- **Enter**: Submit answer / Skip animation / Start game
- **Backspace**: Delete last character
- **ESC**: Pause game / Quit
- **R**: Retry connection (when connection error occurs)
- **Mouse Wheel**: Scroll through incorrect answers review

## Game Files
- `anki_kanji_game.py`: Main game file
- `vocab_game_scores.csv`: High score history (auto-created)
- `vocab_game_save.json`: Save file for continuing games (auto-created)

## Troubleshooting

### Connection Errors
- **"Cannot connect to Anki"**: Make sure Anki is running and AnkiConnect is installed
- Use the **Retry button** or press **R** to retry the connection

### No Cards Found
- The game only includes cards with kanji that aren't marked as "new"
- Study some cards in Anki first to make them available

## License
MIT
