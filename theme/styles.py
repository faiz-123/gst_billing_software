"""
Stylesheet definitions for GST Billing Software
Contains all style strings and style helper functions
"""

from .colors import (
    PRIMARY, PRIMARY_HOVER, SUCCESS, DANGER, WARNING,
    BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, WHITE
)
from .fonts import FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_LARGE

# ---------------- Main Application Stylesheet ----------------
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
    """Get button stylesheet by type
    
    Args:
        button_type: Type of button (primary, secondary, danger, success)
        
    Returns:
        str: CSS stylesheet string
    """
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
    """Get sidebar stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
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
    """Get card/frame stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 16px;
        }}
    """


def get_calendar_stylesheet():
    """Get consistent calendar popup styling for QDateEdit widgets
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QCalendarWidget {{
            background-color: {WHITE};
            color: {TEXT_PRIMARY};
            border: 2px solid {BORDER};
            border-radius: 10px;
            font-size: 14px;
        }}
        
        /* Navigation bar styling */
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {PRIMARY};
            color: {WHITE};
            border-radius: 8px;
            height: 40px;
        }}
        
        /* Navigation buttons */
        QCalendarWidget QToolButton {{
            background-color: {PRIMARY};
            color: {WHITE};
            border: none;
            border-radius: 5px;
            padding: 1px;
            font-weight: bold;
            font-size: 14px;
            min-width: 50px;
            height: 40px;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        
        /* Month/Year spinboxes */
        QCalendarWidget QSpinBox {{
            background-color: {WHITE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 5px;
            padding: 1px;
            font-size: 14px;
        }}
        
        /* Day header (Mon, Tue, etc.) */
        QCalendarWidget QWidget {{ 
            alternate-background-color: {BACKGROUND};
            padding: 0px;
        }}
        
        /* Main calendar grid */
        QCalendarWidget QTableView {{
            background-color: {WHITE};
            alternate-background-color: {WHITE};
            color: {TEXT_PRIMARY};
            gridline-color: {BORDER};
            selection-background-color: {PRIMARY};
            selection-color: {WHITE};
            font-size: 15px;
            font-weight: bold;
            outline: none;
        }}
        
        /* Individual date cells */
        QCalendarWidget QTableView::item {{
            color: #111827;
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            padding: 8px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        }}
        
        QCalendarWidget QTableView::item:selected {{
            background-color: {PRIMARY};
            color: {WHITE};
            border: 2px solid {PRIMARY_HOVER};
            font-weight: bold;
        }}
        
        QCalendarWidget QTableView::item:hover {{
            background-color: #F3F4F6;
            color: #111827;
            border: 2px solid {PRIMARY};
        }}
        
        /* Header for days of week */
        QCalendarWidget QHeaderView::section {{
            background-color: {BACKGROUND};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
        }}
    """


def get_input_style():
    """Get input field stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_LARGE}px;
            min-height: 16px;
        }}
        QLineEdit:focus {{
            border: 2px solid {PRIMARY};
        }}
    """


def get_table_style():
    """Get table widget stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QTableWidget {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            gridline-color: {BORDER};
        }}
        QTableWidget::item {{
            padding: 8px;
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QTableWidget::item:selected {{
            background: {BACKGROUND};
        }}
    """
