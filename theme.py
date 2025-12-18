"""
Theme and styling configuration for GST Billing Software
Contains colors, fonts, and common stylesheets
"""

from PyQt5.QtGui import QFont

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1E40AF"
SUCCESS = "#10B981" 
SUCCESS_BG = "#8ACBB5"
DANGER = "#EF4444"
WARNING = "#F59E0B"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
WHITE = "#FFFFFF"
PURPLE = "#9333EA"

# ---------------- Fonts ----------------
FONT_FAMILY = "Arial"
FONT_SIZE_SMALL = 12
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_TITLE = 24
FONT_SIZE_HEADER = 32

# ---------------- Common Stylesheets ----------------
APP_STYLESHEET = f"""
QWidget {{
    background: {BACKGROUND};
    color: {TEXT_PRIMARY};
    font-family: "{FONT_FAMILY}";
    font-size: {FONT_SIZE_NORMAL}px;
}}

QGroupBox {{
    border: 2px solid {BORDER};
    border-radius: 6px;
    margin-top: 7px;
    font-weight: bold;
    padding: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding-left: 20px;
    color: {TEXT_PRIMARY};
}}

QLineEdit, QDateEdit, QComboBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px;
    background: {WHITE};
    color: {TEXT_PRIMARY};
    height: 28px;
    font-size: {FONT_SIZE_LARGE}px;
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    height: 20px;
    width: 20px;
    subcontrol-position: center right;
    border-color: transparent;
}}

QTextEdit {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px;
    background: {WHITE};
    color: {TEXT_PRIMARY};
    font-size: {FONT_SIZE_NORMAL}px;
}}

QTableWidget {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
}}

QHeaderView::section {{
    background-color: {BACKGROUND};
    color: {TEXT_SECONDARY};
    padding: 8px;
    border: none;
    font-weight: bold;
}}

QPushButton {{
    border-radius: 6px;
    font-weight: bold;
    padding: 8px 16px;
}}
"""

def get_button_style(button_type="primary"):
    """Get button stylesheet by type"""
    styles = {
        "primary": f"""
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
            }}
            QPushButton:hover {{
                background: {PRIMARY_HOVER};
            }}
        """,
        "secondary": f"""
            QPushButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
            }}
        """,
        "danger": f"""
            QPushButton {{
                background: {DANGER};
                color: {WHITE};
                border: none;
            }}
            QPushButton:hover {{
                background: #DC2626;
            }}
        """,
        "success": f"""
            QPushButton {{
                background: {SUCCESS};
                color: {WHITE};
                border: none;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """
    }
    return styles.get(button_type, styles["primary"])

def get_sidebar_style():
    """Get sidebar stylesheet"""
    return """
        QFrame {
            background-color: #0A2E5C;
        }
        QLabel {
            color: white;
            font-weight: bold;
        }
        QPushButton {
            text-align: left;
            padding: 12px 16px;
            border: none;
            color: white;
            background: transparent;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        QPushButton:pressed {
            background: rgba(255, 255, 255, 0.2);
        }
    """

def get_card_style():
    """Get card/frame stylesheet"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 16px;
        }}
    """

def get_title_font(size=FONT_SIZE_TITLE):
    """Get title font"""
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font

def get_header_font(size=FONT_SIZE_HEADER):
    """Get header font"""
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font
