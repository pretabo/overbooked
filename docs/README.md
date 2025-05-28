# Overbooked: A Wrestling Promotion Simulator

Overbooked is a professional wrestling promotion simulator where you can create wrestlers, book matches, and run promotions. It features a match engine, a promo system, and a diplomacy system for managing wrestler relationships.

## Directory Structure

The project has been reorganized for better maintainability and clarity:

```
overbooked/
├── src/                  # Main source code
│   ├── core/             # Core game engines and mechanics
│   │   ├── match_engine.py
│   │   ├── diplomacy_system.py
│   │   └── game_state.py
│   ├── promo/            # Promo system for wrestler interviews
│   │   ├── promo_engine.py
│   │   └── versus_promo_engine.py
│   ├── ui/               # User interface components
│   │   ├── main_app_ui_pyqt.py
│   │   └── promo_test_ui.py
│   └── models/           # Data models and schemas
│       └── wrestler_creator_model.py
├── data/                 # Game data and assets
│   ├── db/               # Database files
│   ├── assets/           # Visual assets and resources
│   │   └── image_assets/
│   └── config/           # Configuration files
├── tests/                # Test files
│   ├── match_tests/
│   ├── promo_tests/
│   └── integration_tests/
├── scripts/              # Utility scripts
│   └── utility_scripts/
├── logs/                 # Application logs
└── docs/                 # Documentation
```

## Features

### Match Engine
The match engine simulates professional wrestling matches with:
- Turn-based action system
- Dynamic momentum shifts
- Realistic wrestling moves and damage
- Special finisher moves
- Match ratings based on quality and flow

### Promo System
The promo system allows wrestlers to cut promos and engage in verbal confrontations:
- Solo and versus promo modes
- Momentum and confidence mechanics
- Cash-in system for special moments
- Rating system based on delivery and content

### Diplomacy System
The diplomacy system manages relationships between wrestlers:
- Alliances and rivalries
- Stable formations
- Reputation management
- Dynamic relationship changes based on actions

## Getting Started

1. Ensure you have Python 3.8+ installed
2. Install required packages:
```
pip install -r requirements.txt
```
3. Run the application:
```
python main.py
```

## Development

### Setting up a development environment

1. Clone the repository
2. Create a virtual environment:
```
python -m venv venv
```
3. Activate the virtual environment:
```
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```
4. Install development dependencies:
```
pip install -r requirements.txt
```

### Running Tests

```
python -m pytest tests/
```

## Development and Debugging

### Logging

The game uses a comprehensive logging system that logs to both the console and log files. Log files are stored in the `logs` directory with timestamps in their filenames.

Log levels:
- `DEBUG`: Detailed development information
- `INFO`: General information about game operations
- `WARNING`: Warnings about potential issues
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors that require immediate attention

### Debug Menu

The game includes a debug menu accessible from the main UI. This menu provides various tools for testing and debugging:

1. **Game State**: View and export game state, check wrestler details
2. **Performance**: Run tests on match and promo engines, view performance statistics
3. **Console Capture**: View real-time console output within the UI

To use the debug menu, click on the "[DEBUG] Debug Menu" button in the main navigation.

### Game State Debugging

For more detailed game state information, you can use functions provided in the `game_state_debug.py` module:

```python
import game_state_debug

# Print a summary of the current game state
game_state_debug.print_game_summary()

# Print detailed information about a specific wrestler
game_state_debug.print_wrestler_details(wrestler_id)

# Export the entire game state for debugging
game_state_debug.export_debug_state()
```

## Testing

The game includes extensive test suites for the match engine, promo system, and other components. You can run specific tests using the scripts in the `scripts` directory.

For example:
```
./scripts/promo-test     # Test the promo system
./scripts/overbooked     # Run the main game
```

## Architecture

The codebase is organized into several key components:

- **Match Engine**: `match_engine.py`, `match_engine_utils.py`
- **Promo System**: `promo/` directory
- **UI Components**: `ui/` directory
- **Game State**: `game_state.py`
- **Diplomacy System**: `diplomacy_system.py`, `diplomacy_hooks.py`
- **Database Utilities**: `db/` directory
- **Debugging Tools**: `game_state_debug.py`

## Database Structure

The game uses SQLite databases for data persistence:

- `wrestlers.db`: Wrestler profiles, attributes, and stats
- `relationships.db`: Relationships between wrestlers
- `save_state.db`: Game state information like current date
- `manoeuvres.db`: Wrestling moves and finishers

## License

This project is copyright © 2023. All rights reserved. 