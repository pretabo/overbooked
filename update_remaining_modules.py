#!/usr/bin/env python3
"""
Update Remaining Modules to Use Centralized Database Utilities

This script updates the modules that still use hardcoded database paths to
use the centralized database utilities in src/core/db_utils.py.
"""

import os
import logging
import glob
import re
import fileinput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_modules.log"),
        logging.StreamHandler()
    ]
)

def get_project_root():
    """Get the absolute path to the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def find_modules_to_update():
    """Find modules that need to be updated to use the centralized utilities."""
    root = get_project_root()
    modules_to_update = []
    
    # Look for specific modules we know need updating
    modules_to_check = [
        os.path.join(root, "src", "core", "match_statistics.py"),
        os.path.join(root, "src", "storyline", "storyline_manager.py"),
        os.path.join(root, "src", "storyline", "enhanced_storyline_manager.py"),
    ]
    
    for module_path in modules_to_check:
        if os.path.exists(module_path):
            try:
                with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Check if the module uses hardcoded database paths
                    if 'self.db_path = "data/' in content or 'self.rivalry_db_path = "data/' in content:
                        modules_to_update.append(module_path)
            except Exception as e:
                logging.warning(f"Error reading {module_path}: {e}")
    
    return modules_to_update

def update_module(module_path):
    """Update a module to use the centralized database utilities."""
    try:
        # Flag to track if we need to add the import
        needs_import = True
        
        # First, read the file to check if db_utils is already imported
        with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'from src.core.db_utils import' in content:
                needs_import = False
        
        # Now, update the file
        with fileinput.FileInput(module_path, inplace=True) as file:
            in_init_method = False
            init_indent = ""
            
            for line in file:
                # Add import if needed
                if needs_import and line.startswith('import ') and not 'import os' in line:
                    print(f'import os\nimport sqlite3\nfrom src.core.db_utils import get_db_path, get_connection\n{line}', end='')
                    needs_import = False
                    continue
                elif needs_import and line.strip() == 'import os':
                    print(f'import os\nimport sqlite3\nfrom src.core.db_utils import get_db_path, get_connection', end='')
                    needs_import = False
                    continue
                
                # Detect if we're in the __init__ method
                if re.match(r'^\s*def\s+__init__\s*\(', line):
                    in_init_method = True
                    init_indent = re.match(r'^(\s*)', line).group(1)
                
                # Replace hardcoded database path in init method
                if in_init_method and ('self.db_path = "data/' in line or 'self.rivalry_db_path = "data/' in line):
                    if 'self.db_path = "data/' in line:
                        db_name = line.split('/')[-1].strip('")\n')
                        indent = re.match(r'^(\s*)', line).group(1)
                        print(f'{indent}self.db_name = "{db_name}"', end='')
                        print(f'\n{indent}self.db_path = get_db_path(self.db_name)')
                    elif 'self.rivalry_db_path = "data/' in line:
                        db_name = line.split('/')[-1].strip('")\n')
                        indent = re.match(r'^(\s*)', line).group(1)
                        print(f'{indent}self.rivalry_db_name = "{db_name}"', end='')
                        print(f'\n{indent}self.rivalry_db_path = get_db_path(self.rivalry_db_name)')
                # Exit init method detection
                elif in_init_method and re.match(r'^\s*def\s+', line):
                    in_init_method = False
                    print(line, end='')
                # Replace direct connection calls
                elif 'sqlite3.connect(self.db_path)' in line:
                    indent = re.match(r'^(\s*)', line).group(1)
                    print(f'{indent}get_connection(self.db_name)', end='')
                elif 'sqlite3.connect(self.rivalry_db_path)' in line:
                    indent = re.match(r'^(\s*)', line).group(1)
                    print(f'{indent}get_connection(self.rivalry_db_name)', end='')
                # Keep the line unchanged
                else:
                    print(line, end='')
        
        logging.info(f"Updated module: {module_path}")
        return True
    except Exception as e:
        logging.error(f"Error updating module {module_path}: {e}")
        return False

def main():
    """Main function."""
    logging.info("Starting module updates")
    
    # Find modules to update
    modules_to_update = find_modules_to_update()
    
    if not modules_to_update:
        logging.info("No modules need updating")
        return
    
    logging.info(f"Found {len(modules_to_update)} modules to update")
    
    # Update each module
    for module_path in modules_to_update:
        if update_module(module_path):
            logging.info(f"Successfully updated {module_path}")
        else:
            logging.error(f"Failed to update {module_path}")
    
    logging.info("Completed module updates")

if __name__ == "__main__":
    main() 