# theme.py
# 🎨 Colours
GUNMETAL       = "#42494a"
DARK_GREY      = "#1e1e1e"
NEAR_BLACK     = "#111"
SILVER         = "#c0c0c0"
CRIMSON        = "#c44b4f"
BLUEGRAY       = "#607d86"
BONE           = "#e0e0e0"
SKY_HIGHLIGHT  = "#5b9bd5"
GOLDENROD      = "#ffd700"

# 🔤 Fonts (optional to apply globally in main.py)
FONT_MONO      = ("Fira Code", 10)
FONT_SANS      = ("Fira Code", 10)
FONT_SANS_BOLD = ("Fira Code", 11, "bold")
FONT_HEADER    = ("Futura", 14, "bold")

# 🎛️ Centralised style dictionary
STYLES = {
    "app_background": {
        "background-color": GUNMETAL,
    },

    "label": {
        "background-color": GUNMETAL,
        "color": BONE,
        "font-family": "Fira Code",
        "font-size": "10pt",
    },

    "label_header": {
        "background-color": GUNMETAL,
        "color": BONE,
        "font-family": "Futura",
        "font-size": "18pt",
        "font-weight": "bold",
    },

    "momentum_label": {
        "background-color": GUNMETAL,
        "color": CRIMSON,
        "font-family": "Futura",
        "font-size": "13pt",
        "font-weight": "bold"
    },

    "commentary_box": {
        "background-color": DARK_GREY,
        "color": BONE,
        "font-family": "Fira Code",
        "font-size": "13pt",
        "border": "1px solid #444",
        "padding": "8px"
    },

    "stat_label": {
        "color": SILVER,
        "font-family": "Fira Code",
        "font-size": "10pt",
        "padding": "6px"
    },

    "summary_box": {
        "background-color": "#333333",
        "color": BONE,
        "font-family": "Fira Code",
        "font-size": "10pt",
        "padding": "10px",
        "border-top": "1px solid #555",
        "margin-top": "10px"
    },

    "warning": {
        "color": "orange",
        "font-size": "10pt",
        "padding": "4px"
    },

    "input_text": {
        "background-color": "#222",
        "color": "#f0f0f0",
        "font-family": "Fira Code",
        "font-size": "16pt",
        "padding": "6px"
    },

    "button_nav": """
        QPushButton {
            background-color: #444;
            color: #e0e0e0;
            font-size: 13pt;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #666;
        }
    """,

    "button_blue": """
        QPushButton {
            background-color: #4682b4;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #5b9bd5;
        }
    """,

    "button_red": """
        QPushButton {
            background-color: #f57f7f;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #8b0000;
        }
    """,

    "button_yellow": """
        QPushButton {
            background-color: #ffd700;
            color: black;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #ffcf33;
        }
    """,

    "button_flat": """
        QPushButton {
            background-color: #444;
            color: #ccc;
            border: 1px solid #666;
            padding: 2px;
        }
        QPushButton:hover {
            background-color: #666;
        }
    """,

    "dropdown": """
        QComboBox {
            background-color: #333;
            color: white;
            padding: 4px;
            font-size: 11pt;
        }
    """,

    "list_wrestlers": """
        QListWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-size: 14pt;
            font-family: Fira Code;
            border: 1px solid #444;
        }
    """,

    "list_matches": """
        QListWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-size: 11pt;
            font-family: Fira Code;
            border: 1px solid #444;
        }
    """
}

# 🧩 Utility
def apply_styles(widget, style_key):
    """
    Apply a stylesheet to a PyQt widget from STYLES dict.
    If the style is a dict, convert it to CSS. If it's already a string, apply it directly.
    """
    style = STYLES.get(style_key)
    if not style:
        print(f"⚠️ Style '{style_key}' not found.")
        return

    if isinstance(style, str):
        widget.setStyleSheet(style)
    elif isinstance(style, dict):
        css = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in style.items())
        widget.setStyleSheet(css)


from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class ShadowTextLabel(QLabel):
    def __init__(self, text="", shadow_offset=(2, 2), shadow_color=QColor(0, 0, 0), parent=None):
        super().__init__(text, parent)
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        text = self.text()
        rect = self.rect()

        # Shadow
        shadow_rect = rect.translated(self.shadow_offset[0], self.shadow_offset[1])
        painter.setPen(self.shadow_color)
        painter.drawText(shadow_rect, Qt.AlignCenter, text)

        # Main text
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(rect, Qt.AlignCenter, text)
