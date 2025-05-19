from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
import sys
from ui.main_app_ui_pyqt import MainApp



if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply global font
    app.setFont(QFont("Fira Code", 16))

    # Apply global stylesheet with error handling
    try:
        with open("ui/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Error: Stylesheet file 'ui/theme.qss' not found.")

    # Launch window in full screen
    window = MainApp()
    window.setWindowIcon(QIcon("image_assets/logo.png"))  # Ensure the path is correct
    window.showFullScreen()  # ✅ This enables full screen at launch
    sys.exit(app.exec_())
