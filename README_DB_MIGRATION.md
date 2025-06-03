# Database Migration Guide for Overbooked

## Overview

This document outlines the process for consolidating the database locations in the Overbooked project. Previously, database files were scattered across multiple directories (`/db` and `/data/db`), leading to confusion and potential data inconsistency.

## The Problem

- Database files exist in both `/db` and `/data/db` directories
- Multiple `db_path` utilities with different logic across the codebase
- Code references both locations, causing confusion and bugs
- Data could become out of sync between copies

## The Solution

We've chosen to standardize on a single location for all database files: `/db`

Reasons for this choice:
- It's at the project root, making paths simpler and less ambiguous
- Most code already prioritizes this location
- It's a common convention for single-app projects

## Migration Process

The migration is handled by the `db_migration.py` script, which performs the following tasks:

1. **Compare database files** between `/data/db` and `/db`
2. **Create a migration plan** based on file existence, modification dates, and sizes
3. **Execute the migration plan** by copying or merging files into `/db`
4. **Update the central `db_path` function** in `src/db/utils.py`
5. **Create a symlink** from `/data/db` to `/db` for backward compatibility

## How to Use

1. Run the migration script:
   ```
   python db_migration.py
   ```

2. Review the migration log file (`db_migration.log`) to ensure everything worked correctly

3. Test your application to ensure it works with the new database setup

4. Review the files with `db_path` references (listed in the log) and update them as needed

5. Once all code is updated and tested, the symlink can be removed for a cleaner structure

## Future Development

For all future development:

1. Always use the central `db_path` function from `src/db/utils.py`
2. All database files should be placed in the `/db` directory
3. Never hardcode database paths in your code

## Troubleshooting

If you encounter issues after migration:

1. Check the migration log for any errors or warnings
2. Verify that the symlink from `/data/db` to `/db` exists and is working correctly
3. Look for any code that might be using absolute paths or bypassing the `db_path` function
4. Database backups are created during migration with timestamps if you need to recover data 