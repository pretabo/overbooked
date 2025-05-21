# Overbooked: Wrestling Simulator

A comprehensive professional wrestling management simulation game that combines match simulation, promo generation, and storyline management.

## Overview

Overbooked lets you run your own wrestling promotion, manage wrestlers, book matches, create storylines, and watch them unfold. The game features detailed wrestler statistics, relationship dynamics, and sophisticated simulation engines for matches and promos.

## Features

- **Match Engine**: Sophisticated match simulation system with dynamic commentary
- **Promo System**: Generate realistic wrestler promos with quality ratings
- **Roster Management**: Manage a detailed roster of wrestlers with comprehensive stats
- **Storyline System**: Create and manage complex storylines between wrestlers
- **Diplomacy System**: Track relationships and backstage politics between wrestlers
- **Calendar System**: Schedule and manage events over time
- **Modern UI**: Clean, intuitive PyQt5-based interface

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the game:
   ```
   python main.py
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