from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
import sys
import os
import logging
import datetime

# Fix Python module import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add both project root and src to path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# This allows both 'from src.module' and 'from module' style imports to work
sys.path.append(os.path.join(project_root, "src"))

from ui.main_app_ui_pyqt import MainApp

# Configure logging system
def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
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
    base_dir = os.path.dirname(os.path.dirname(__file__))
    assets_dir = os.path.join(base_dir, "data", "assets", "image_assets")
    
    # Set application icon
    app_icon = QIcon(os.path.join(assets_dir, "logo.png"))
    app.setWindowIcon(app_icon)
    logging.debug(f"Set application icon from {os.path.join(assets_dir, 'logo.png')}")

    # Apply global font
    app.setFont(QFont("Fira Code", 16))
    logging.debug("Applied global font: Fira Code, 16pt")

    # Apply global stylesheet with error handling
    try:
        theme_path = os.path.join(os.path.dirname(__file__), "ui", "theme.qss")
        with open(theme_path, "r") as f:
            app.setStyleSheet(f.read())
        logging.debug(f"Applied global stylesheet from {theme_path}")
    except FileNotFoundError:
        logging.error(f"Error: Stylesheet file '{theme_path}' not found.")
        print(f"Error: Stylesheet file '{theme_path}' not found.")

    # Launch window in full screen
    window = MainApp()
    window.setWindowIcon(QIcon(os.path.join(assets_dir, "logo.png")))
    window.showFullScreen()  # ✅ This enables full screen at launch
    logging.info("Application window launched in fullscreen mode")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
