#!/usr/bin/env python3
"""
Overbooked: A Professional Wrestling Promotion Simulator
Main application entry point
"""

import sys
import os
import logging
from src.ui.main_app_ui_pyqt import MainApp
from PyQt5.QtWidgets import QApplication, QShortcut
from PyQt5.QtGui import QIcon, QFont, QKeySequence
import datetime

# Configure logging system
def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Set up logging with both file and console handlers
    log_filename = f"{logs_dir}/overbooked_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Log file: {log_filename}")

def main():
    # Initialize logging
    setup_logging()
    logging.info("=== Overbooked: Wrestling Simulator ===")
    logging.info("Starting application...")
    
    app = QApplication(sys.argv)

    # Set paths relative to this file
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, "data", "assets", "image_assets")
    
    # Set application icon
    icon_path = os.path.join(assets_dir, "logo.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        logging.debug(f"Set application icon from {icon_path}")
    else:
        logging.warning(f"Icon file not found at {icon_path}")

    # Apply global font
    app.setFont(QFont("Fira Code", 16))
    logging.debug("Applied global font: Fira Code, 16pt")

    # Apply global stylesheet with error handling
    try:
        theme_path = os.path.join(base_dir, "src", "ui", "theme.qss")
        with open(theme_path, "r") as f:
            app.setStyleSheet(f.read())
        logging.debug(f"Applied global stylesheet from {theme_path}")
    except FileNotFoundError:
        logging.error(f"Error: Stylesheet file '{theme_path}' not found.")
        print(f"Error: Stylesheet file '{theme_path}' not found.")

    # Launch window in full screen
    window = MainApp()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.showFullScreen()  # ✅ This enables full screen at launch
    
    # Add keyboard shortcut for exiting application (ESC key)
    exit_shortcut = QShortcut(QKeySequence("Esc"), window)
    exit_shortcut.activated.connect(app.quit)
    
    logging.info("Application window launched in fullscreen mode")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 