#!/bin/bash
# Overbooked wrestling promotion simulator launcher

# Determine the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Run the application
python main.py 