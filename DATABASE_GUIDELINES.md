# Database Guidelines for Overbooked

## Overview

This document outlines the standards and best practices for database access in the Overbooked project after the consolidation of database locations.

## Database Location

All databases are now located in the `/db` directory at the project root. 

- **DO NOT** create or reference databases in `/data/db` or any other location
- **DO NOT** hardcode database paths in your code
- **DO NOT** create custom `db_path` functions

## Accessing Databases

### Recommended Approach

Use the centralized database utilities in `src/core/db_utils.py`:

```python
from src.core.db_utils import get_db_path, execute_query, execute_update

# Get a database path
db_path = get_db_path("wrestlers.db")

# Execute a query
results = execute_query("wrestlers.db", "SELECT * FROM wrestlers WHERE id = ?", (wrestler_id,))

# Execute an update
affected_rows = execute_update("wrestlers.db", "UPDATE wrestlers SET name = ? WHERE id = ?", (new_name, wrestler_id))
```

### Available Utility Functions

- `get_db_path(db_name)`: Get the path to a database file
- `get_connection(db_name)`: Get a connection to a database
- `execute_query(db_name, query, params=None)`: Execute a query and return results
- `execute_update(db_name, query, params=None)`: Execute an update and return affected rows
- `execute_script(db_name, script)`: Execute a SQL script
- `table_exists(db_name, table_name)`: Check if a table exists
- `column_exists(db_name, table_name, column_name)`: Check if a column exists
- `create_database_if_not_exists(db_name)`: Create a database if it doesn't exist

## Primary Databases

The following databases should be used for their respective data:

- `wrestlers.db`: Wrestler data, attributes, and relationships
- `events.db`: Events, matches, and related data
- `matches.db`: Match history and statistics
- `buffs.db`: Buffs, buff types, and wrestler buffs
- `manoeuvres.db`: Wrestling moves and maneuvers
- `relationships.db`: Relationships between wrestlers
- `business.db`: Business data, finances, and statistics
- `save_state.db`: Game state and save data

## Migration Status

- All databases have been consolidated into `/db`
- A symlink from `/data/db` to `/db` exists for backward compatibility
- Custom `db_path` functions and hardcoded paths should be updated to use the central utilities

## Next Steps for Developers

1. Update any code that references hardcoded database paths
2. Replace custom `db_path` functions with imports from `src.core.db_utils`
3. Fix any bugs related to database access
4. Use consistent database and table naming conventions

## Database Schema Management

For schema changes:

1. Document the changes in a comment or documentation
2. Check if columns exist before using them
3. Handle migration gracefully if a column doesn't exist

Example:

```python
from src.core.db_utils import column_exists, execute_update

# Check if column exists and add it if it doesn't
if not column_exists("wrestlers.db", "wrestlers", "created_at"):
    execute_update("wrestlers.db", "ALTER TABLE wrestlers ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
```

## Questions or Issues

If you encounter any issues with database access or have questions about the database structure, please update the README or contact the team. 