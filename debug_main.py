#!/usr/bin/env python3
"""Debug wrapper for main.py"""

import traceback

try:
    import main
    main.main()
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc() 