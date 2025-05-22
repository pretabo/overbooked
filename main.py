from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
import sys
import os
import logging
import datetime
from ui.main_app_ui_pyqt import MainApp

# Configure logging system
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up logging with both file and console handlers
    log_filename = f"logs/overbooked_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
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


if __name__ == '__main__':
    # Initialize logging
    setup_logging()
    logging.info("=== Overbooked: Wrestling Simulator ===")
    logging.info("Starting application...")
    
    app = QApplication(sys.argv)

    # Set application icon
    app_icon = QIcon("image_assets/logo.png")
    app.setWindowIcon(app_icon)
    logging.debug("Set application icon from image_assets/logo.png")

    # Apply global font
    app.setFont(QFont("Fira Code", 16))
    logging.debug("Applied global font: Fira Code, 16pt")

    # Apply global stylesheet with error handling
    try:
        with open("ui/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
        logging.debug("Applied global stylesheet from ui/theme.qss")
    except FileNotFoundError:
        logging.error("Error: Stylesheet file 'ui/theme.qss' not found.")
        print("Error: Stylesheet file 'ui/theme.qss' not found.")

    # Launch window in full screen
    window = MainApp()
    window.setWindowIcon(QIcon("image_assets/logo.png"))  # Ensure the path is correct
    window.showFullScreen()  # ✅ This enables full screen at launch
    logging.info("Application window launched in fullscreen mode")
    sys.exit(app.exec_())
