"""
Stylesheet definitions for GST Billing Software
Contains all style strings and style helper functions
"""

from .colors import (
    PRIMARY, PRIMARY_HOVER, SUCCESS, DANGER, WARNING,
    BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, WHITE,
    PRIMARY_LIGHT, PRIMARY_DARK, DANGER_LIGHT, SUCCESS_LIGHT, TEXT_MUTED
)
from .fonts import FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, FONT_SIZE_TITLE

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
    """Get button stylesheet by type with PySide6 compatibility
    
    Args:
        button_type: Type of button (primary, secondary, danger, success, warning)
        
    Returns:
        str: CSS stylesheet string with all states (normal, hover, pressed, disabled)
    """
    styles = {
        "primary": f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 25px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #1D4ED8;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
                border: none;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """,
        "secondary": f"""
            QPushButton {{
                background-color: {WHITE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 25px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {BACKGROUND};
                border: 1px solid {PRIMARY};
                color: {PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: #E8F0FF;
            }}
            QPushButton:disabled {{
                background-color: #FAFAFA;
                color: #BDBDBD;
                border: 1px solid #E0E0E0;
            }}
            QPushButton:focus {{
                outline: none;
                border: 1px solid {PRIMARY};
            }}
        """,
        "danger": f"""
            QPushButton {{
                background-color: {DANGER};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 25px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #991B1B;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
                border: none;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """,
        "success": f"""
            QPushButton {{
                background-color: {SUCCESS};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 25px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #059669;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #065F46;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
                border: none;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """,
        "warning": f"""
            QPushButton {{
                background-color: #F59E0B;
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 25px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: #D97706;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #B45309;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
                border: none;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
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
            min-width: 300px;
            min-height: 280px;
        }}
        
        /* Navigation bar styling */
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {PRIMARY};
            color: {WHITE};
            border-radius: 8px 8px 0 0;
            min-height: 45px;
            padding: 4px;
        }}
        
        /* Navigation buttons */
        QCalendarWidget QToolButton {{
            background-color: {PRIMARY};
            color: {WHITE};
            border: none;
            border-radius: 5px;
            padding: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 40px;
            min-height: 35px;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        QCalendarWidget QToolButton#qt_calendar_prevmonth,
        QCalendarWidget QToolButton#qt_calendar_nextmonth {{
            min-width: 35px;
            max-width: 35px;
            qproperty-icon: none;
        }}
        QCalendarWidget QToolButton#qt_calendar_prevmonth {{
            qproperty-text: "<";
        }}
        QCalendarWidget QToolButton#qt_calendar_nextmonth {{
            qproperty-text: ">";
        }}
        
        /* Month/Year menu button */
        QCalendarWidget QToolButton::menu-indicator {{
            image: none;
            width: 0px;
        }}
        
        /* Month/Year spinboxes */
        QCalendarWidget QSpinBox {{
            background-color: {WHITE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 5px;
            padding: 4px;
            font-size: 14px;
            min-width: 60px;
        }}
        
        /* Main calendar view container */
        QCalendarWidget QWidget {{
            alternate-background-color: {WHITE};
        }}
        
        /* Main calendar grid */
        QCalendarWidget QTableView {{
            background-color: {WHITE};
            alternate-background-color: {WHITE};
            color: {TEXT_PRIMARY};
            gridline-color: #E5E7EB;
            selection-background-color: {PRIMARY};
            selection-color: {WHITE};
            font-size: 14px;
            outline: none;
            border: none;
        }}
        
        /* Individual date cells - explicit styling */
        QCalendarWidget QAbstractItemView:enabled {{
            color: #111827;
            background-color: {WHITE};
            font-size: 14px;
            font-weight: 500;
        }}
        
        QCalendarWidget QAbstractItemView:disabled {{
            color: #9CA3AF;
        }}
        
        /* Selected date */
        QCalendarWidget QTableView::item:selected {{
            background-color: {PRIMARY};
            color: {WHITE};
            border-radius: 4px;
            font-weight: bold;
        }}
        
        /* Hover state */
        QCalendarWidget QTableView::item:hover {{
            background-color: #DBEAFE;
            color: #111827;
            border-radius: 4px;
        }}
        
        /* Header for days of week (Mon, Tue, etc.) */
        QCalendarWidget QHeaderView {{
            background-color: #F3F4F6;
        }}
        QCalendarWidget QHeaderView::section {{
            background-color: #F3F4F6;
            color: #374151;
            border: none;
            padding: 6px;
            font-weight: 600;
            font-size: 12px;
        }}
        
        /* Weekend days - slightly different color */
        QCalendarWidget QHeaderView::section:first,
        QCalendarWidget QHeaderView::section:last {{
            color: #6B7280;
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


def get_dialog_input_style():
    """Get dialog input field stylesheet (line edits, combos, spinboxes)
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 0 12px;
            color: {TEXT_PRIMARY};
            background: {WHITE};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {TEXT_SECONDARY};
            margin-right: 10px;
        }}
    """


def get_readonly_input_style():
    """Get read-only input field stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 0 12px;
            color: {TEXT_SECONDARY};
            background: {BACKGROUND};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {TEXT_SECONDARY};
            margin-right: 10px;
        }}
    """


def get_error_input_style():
    """Get error state input field stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit, QDoubleSpinBox, QSpinBox {{
            border: 2px solid {DANGER};
            border-radius: 8px;
            padding: 0 12px;
            background: #fff5f5;
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
    """


def get_textarea_style():
    """Get text area/text edit stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QTextEdit {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 10px 12px;
            color: {TEXT_PRIMARY};
            background: {WHITE};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QTextEdit:focus {{
            border-color: {PRIMARY};
        }}
    """


def get_checkbox_style():
    """Get checkbox stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QCheckBox {{
            color: {TEXT_PRIMARY};
            font-weight: 600;
            background: transparent;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {BORDER};
            border-radius: 4px;
            background: {WHITE};
        }}
        QCheckBox::indicator:checked {{
            background: {PRIMARY};
            border-color: {PRIMARY};
            image: none;
        }}
        QCheckBox::indicator:hover {{
            border-color: {PRIMARY};
        }}
    """


def get_section_frame_style(bg_color: str = None, border_radius: int = 12):
    """Get section/card frame stylesheet
    
    Args:
        bg_color: Background color (default: WHITE)
        border_radius: Border radius in pixels (default: 12)
    
    Returns:
        str: CSS stylesheet string
    """
    bg = bg_color if bg_color else WHITE
    return f"""
        QFrame#sectionFrame {{
            background: {bg};
            border: 1px solid {BORDER};
            border-radius: {border_radius}px;
            padding: 8px;
        }}
        QFrame {{
            background: {bg};
            border: 1px solid {BORDER};
            border-radius: {border_radius}px;
        }}
    """


def get_dialog_footer_style():
    """Get dialog footer stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame {{
            background: {WHITE};
            border-top: 1px solid {BORDER};
        }}
    """


def get_cancel_button_style():
    """Get cancel button stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: transparent;
            color: {TEXT_SECONDARY};
            border: 2px solid {BORDER};
            border-radius: 8px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {BACKGROUND};
            border-color: {TEXT_SECONDARY};
        }}
    """


def get_save_button_style():
    """Get save/primary action button stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: {PRIMARY};
            color: {WHITE};
            border: none;
            border-radius: 8px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {PRIMARY_HOVER};
        }}
    """


def get_link_label_style(color=None):
    """Get clickable link label stylesheet
    
    Args:
        color: Custom color (default: PRIMARY)
        
    Returns:
        str: CSS stylesheet string
    """
    link_color = color or PRIMARY
    return f"""
        QLabel {{
            color: {link_color};
            background: transparent;
            padding: 8px 0;
        }}
        QLabel:hover {{
            color: {PRIMARY_HOVER};
        }}
    """


def get_scroll_area_style():
    """Get scroll area stylesheet with transparent background
    
    Returns:
        str: CSS stylesheet string
    """
    return f"background: {BACKGROUND}; border: none;"


# ============================================================================
# Screen/List specific styles
# ============================================================================

def get_action_frame_style():
    """Get action bar frame stylesheet for list screens
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame#actionFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 8px;
        }}
    """


def get_search_container_style():
    """Get search container frame stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame#searchContainer {{
            border: 2px solid {BORDER};
            border-radius: 10px;
            background: {WHITE};
        }}
        QFrame#searchContainer:hover {{
            border-color: {PRIMARY};
        }}
    """


def get_search_input_style():
    """Get search input stylesheet (borderless for inside search container)
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit {{
            border: none;
            font-size: {FONT_SIZE_NORMAL}px;
            background: transparent;
            color: {TEXT_PRIMARY};
            padding: 8px 0;
        }}
        QLineEdit::placeholder {{
            color: {TEXT_SECONDARY};
        }}
    """


def get_primary_action_button_style():
    """Get primary action button stylesheet (gradient style)
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {PRIMARY}, stop:1 #1D4ED8);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
            padding: 10px 24px;
            min-width: 140px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3B82F6, stop:1 #1E40AF);
        }}
        QPushButton:pressed {{
            background: #1D4ED8;
        }}
    """


def get_secondary_action_button_style():
    """Get secondary action button stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: {WHITE};
            color: {TEXT_PRIMARY};
            border: 2px solid {BORDER};
            border-radius: 10px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 500;
            padding: 10px 20px;
            min-width: 110px;
        }}
        QPushButton:hover {{
            border-color: {PRIMARY};
            background: #F8FAFC;
            color: {PRIMARY};
        }}
        QPushButton:pressed {{
            background: #EEF2FF;
        }}
    """


def get_stat_card_style(accent_color):
    """Get statistics card stylesheet with accent color
    
    Args:
        accent_color: Color for left border and hover accent
        
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 12px;
            border-left: 4px solid {accent_color};
        }}
        QFrame:hover {{
            border-color: {accent_color};
            background: #FAFBFC;
        }}
    """


def get_filter_frame_style():
    """Get filter section frame stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 12px;
        }}
    """


def get_filter_combo_style():
    """Get filter combo box stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QComboBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 6px 12px;
            padding-right: 30px;
            background: {BACKGROUND};
            font-size: {FONT_SIZE_NORMAL - 1}px;
            color: {TEXT_PRIMARY};
            min-width: 100px;
        }}
        QComboBox:hover {{
            border-color: {PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {TEXT_SECONDARY};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {BORDER};
            background: {WHITE};
            selection-background-color: {PRIMARY};
            selection-color: white;
            outline: none;
        }}
    """


def get_icon_button_style():
    """Get small icon button stylesheet (refresh, etc.)
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 6px;
            font-size: {FONT_SIZE_NORMAL}px;
            padding: 0px;
        }}
        QPushButton:hover {{
            background: {PRIMARY};
            color: white;
            border-color: {PRIMARY};
        }}
    """


def get_clear_button_style():
    """Get clear/reset button stylesheet (text-only)
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background: transparent;
            color: {TEXT_SECONDARY};
            border: none;
            font-size: {FONT_SIZE_NORMAL - 1}px;
            padding: 0 8px;
        }}
        QPushButton:hover {{
            color: {DANGER};
        }}
    """


def get_table_frame_style():
    """Get table container frame stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame#tableFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 12px;
        }}
    """


def get_enhanced_table_style():
    """Get enhanced table widget stylesheet with modern styling
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QTableWidget {{
            gridline-color: #F3F4F6;
            background-color: {WHITE};
            border: none;
            font-size: {FONT_SIZE_NORMAL}px;
            selection-background-color: #EEF2FF;
            alternate-background-color: #FAFBFC;
        }}
        QTableWidget::item {{
            border-bottom: 1px solid #F3F4F6;
        }}
        QTableWidget::item:selected {{
            background-color: #EEF2FF;
            color: {TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background-color: #F8FAFC;
            color: {TEXT_SECONDARY};
            font-weight: 600;
            border: none;
            border-bottom: 2px solid #E5E7EB;
            font-size: {FONT_SIZE_NORMAL - 1}px;
            text-transform: uppercase;
        }}
        QHeaderView::section:hover {{
            background-color: #F1F5F9;
        }}
    """


def get_count_badge_style():
    """Get count/info badge stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_NORMAL - 1}px;
            background: {BACKGROUND};
            padding: 6px 14px;
            border-radius: 16px;
            border: none;
        }}
    """


def get_status_badge_style(color, bg_color):
    """Get status badge stylesheet with custom colors
    
    Args:
        color: Text color
        bg_color: Background color
        
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLabel {{
            color: {color};
            background: {bg_color};
            padding: 6px 12px;
            border-radius: 12px;
            font-size: {FONT_SIZE_SMALL - 1}px;
            font-weight: 600;
        }}
    """


def get_row_action_button_style(bg_color, hover_color):
    """Get table row action button stylesheet
    
    Args:
        bg_color: Background color
        hover_color: Hover background color
        
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            border: 1px solid {BORDER};
            border-radius: 4px;
            background: {bg_color};
            font-size: {FONT_SIZE_SMALL - 1}px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            padding: 0px;
        }}
        QPushButton:hover {{
            background: {hover_color};
            border-color: {hover_color};
            color: white;
        }}
    """


def get_filter_label_style():
    """Get filter label stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_SMALL - 1}px;
        font-weight: 500;
        border: none;
    """


def get_stat_label_style():
    """Get stat card label stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_SMALL}px;
        font-weight: 500;
        border: none;
    """


def get_stat_value_style():
    """Get stat card value stylesheet
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        color: {TEXT_PRIMARY};
        font-size: {FONT_SIZE_TITLE - 2}px;
        font-weight: 700;
        border: none;
    """


def get_stat_icon_container_style(color: str):
    """Get stat card icon container stylesheet
    
    Args:
        color: The accent color for the icon background
        
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QFrame {{
            background: {color}20;
            border-radius: 10px;
            border: none;
        }}
    """


# ============================================================================
# Invoice Form Dialog Styles
# ============================================================================

def get_row_number_style():
    """Get row number label style for invoice items"""
    return f"""
        QLineEdit {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            color: {TEXT_SECONDARY};
            font-weight: 600;
            font-size: {FONT_SIZE_NORMAL}px;
            padding: 4px;
            min-width: 30px;
            max-width: 35px;
        }}
    """


def get_product_input_style():
    """Get product name input style for invoice items"""
    return f"""
        QLineEdit {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QLineEdit:focus {{
            border-color: {PRIMARY};
        }}
    """


def get_hsn_readonly_style():
    """Get HSN code readonly input style"""
    return f"""
        QLineEdit {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_SMALL}px;
            padding: 6px;
        }}
    """


def get_unit_label_style():
    """Get unit label style"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_SMALL}px;
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 6px 10px;
        }}
    """


def get_readonly_spinbox_style():
    """Get readonly spinbox style"""
    return f"""
        QDoubleSpinBox, QSpinBox {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_NORMAL}px;
            padding: 4px;
        }}
    """


def get_amount_display_style():
    """Get amount display label style"""
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 8px 12px;
        }}
    """


def get_circle_button_style(color: str, hover_color: str = None):
    """Get circular button style (add/remove buttons)"""
    if hover_color is None:
        hover_color = color
    return f"""
        QPushButton {{
            background: {color};
            color: {WHITE};
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: bold;
            min-width: 28px;
            max-width: 28px;
            min-height: 28px;
            max-height: 28px;
        }}
        QPushButton:hover {{
            background: {hover_color};
        }}
    """


def get_invoice_dialog_style():
    """Get main invoice dialog style"""
    return f"""
        QDialog {{
            background: {BACKGROUND};
        }}
        QToolTip {{
            background-color: #FFFFFF;
            color: #1F2937;
            border: 2px solid #3B82F6;
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 13px;
            font-weight: normal;
        }}
    """


def get_dialog_header_style():
    """Get dialog header section style"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 16px;
        }}
    """


def get_preview_header_style():
    """Get preview dialog header style"""
    return f"""
        QFrame {{
            background: {PRIMARY};
            border-radius: 8px 8px 0 0;
            padding: 12px;
        }}
    """


def get_preview_close_button_style():
    """Get preview close button style"""
    return f"""
        QPushButton {{
            background: transparent;
            color: {WHITE};
            border: none;
            font-size: 20px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            color: {DANGER};
        }}
    """


def get_html_viewer_style():
    """Get HTML viewer widget style"""
    return f"""
        QTextBrowser {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
        }}
    """


def get_pdf_viewer_style():
    """Get PDF viewer widget style"""
    return f"""
        QScrollArea {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
        }}
    """


def get_form_label_style(font_size: int = None, font_weight: str = "600", color: str = None):
    """Get form field label style
    
    Args:
        font_size: Font size in pixels (default: FONT_SIZE_SMALL)
        font_weight: Font weight (default: "600")
        color: Text color (default: TEXT_PRIMARY)
    """
    size = font_size if font_size else FONT_SIZE_SMALL
    text_color = color if color else TEXT_PRIMARY
    return f"""
        QLabel {{
            color: {text_color};
            font-size: {size}px;
            font-weight: {font_weight};
        }}
    """


def get_form_combo_style():
    """Get form combo box style"""
    return f"""
        QComboBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
            min-height: 20px;
        }}
        QComboBox:focus {{
            border-color: {PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
    """


def get_date_edit_style():
    """Get date edit widget style with calendar icon and proper dropdown"""
    return f"""
        QDateEdit {{
            border: 2px solid {BORDER};
            border-bottom: 2px solid {BORDER};
            border-radius: 6px;
            padding: 6px 8px;
            padding-right: 30px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 500;
            min-height: 24px;
            margin-bottom: 2px;
        }}
        QDateEdit:focus {{
            border: 2px solid {PRIMARY};
            border-bottom: 2px solid {PRIMARY};
        }}
        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 28px;
            border: none;
            background: transparent;
            margin-right: 2px;
        }}
        QDateEdit::down-arrow {{
            image: url(assets/icons/calendar.png);
            width: 18px;
            height: 18px;
        }}
        QDateEdit QAbstractItemView {{
            background: {WHITE};
            color: {TEXT_PRIMARY};
            selection-background-color: {PRIMARY};
            selection-color: {WHITE};
            border: 1px solid {BORDER};
        }}
    """


def get_invoice_number_input_style():
    """Get invoice number input style - Red color for visibility"""
    return f"""
        QLineEdit {{
            background: #FEF2F2;
            border: 2px solid #EF4444;
            border-radius: 6px;
            padding: 8px 12px;
            color: #DC2626;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 700;
        }}
    """


def get_party_search_input_style():
    """Get party search input style"""
    return f"""
        QLineEdit {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QLineEdit:focus {{
            border-color: {PRIMARY};
        }}
    """


def get_section_header_style():
    """Get section header label style"""
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_LARGE}px;
            font-weight: 700;
            border: none;
            background: transparent;
        }}
    """


def get_quick_chip_style(is_active: bool = False):
    """Get quick action chip button style"""
    bg = PRIMARY if is_active else WHITE
    text = WHITE if is_active else TEXT_PRIMARY
    return f"""
        QPushButton {{
            background: {bg};
            color: {text};
            border: 1px solid {BORDER if not is_active else PRIMARY};
            border-radius: 16px;
            padding: 6px 14px;
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {PRIMARY_HOVER if is_active else BACKGROUND};
            border-color: {PRIMARY};
        }}
    """


def get_item_count_badge_style(count: int = 0):
    """Get item count badge style
    
    Args:
        count: Item count (unused, for compatibility)
    """
    return f"""
        QLabel {{
            background: {PRIMARY_LIGHT};
            color: {PRIMARY};
            border-radius: 12px;
            padding: 4px 10px;
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: 600;
        }}
    """


def get_transparent_scroll_area_style():
    """Get transparent scroll area style"""
    return f"""
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: {BACKGROUND};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def get_items_scroll_container_style():
    """Get items scroll container style"""
    return f"""
        QWidget {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 8px;
        }}
    """


def get_summary_label_style():
    """Get summary section label style"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_NORMAL}px;
            border: none;
            background: transparent;
        }}
    """


def get_summary_value_style():
    """Get summary section value style"""
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
            border: none;
            background: transparent;
        }}
    """


def get_total_row_style():
    """Get total row container style"""
    return f"""
        QFrame {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px;
        }}
    """


def get_grand_total_label_style():
    """Get grand total label style"""
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_LARGE}px;
            font-weight: 700;
            border: none;
            background: transparent;
        }}
    """


def get_grand_total_value_style():
    """Get grand total value style"""
    return f"""
        QLabel {{
            color: {PRIMARY};
            font-size: {FONT_SIZE_TITLE}px;
            font-weight: 700;
            border: none;
            background: transparent;
        }}
    """


def get_balance_due_style():
    """Get balance due value style"""
    return f"""
        QLabel {{
            color: {DANGER};
            font-size: {FONT_SIZE_LARGE}px;
            font-weight: 700;
            border: none;
            background: transparent;
        }}
    """


def get_roundoff_input_style():
    """Get round-off input style"""
    return f"""
        QDoubleSpinBox {{
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            background: {WHITE};
            color: {TEXT_PRIMARY};
            font-size: {FONT_SIZE_NORMAL}px;
            max-width: 80px;
        }}
    """


def get_roundoff_value_style():
    """Get round-off value label style"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_NORMAL}px;
            border: none;
            background: transparent;
        }}
    """


def get_add_party_link_style():
    """Get add party link button style"""
    return f"""
        QPushButton {{
            color: {PRIMARY};
            background: transparent;
            border: none;
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: 500;
            text-decoration: underline;
        }}
        QPushButton:hover {{
            color: {PRIMARY_HOVER};
        }}
    """


def get_context_menu_style():
    """Get context menu style"""
    return f"""
        QMenu {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background: {PRIMARY_LIGHT};
            color: {PRIMARY};
        }}
    """


def get_party_suggestion_menu_style():
    """Get party suggestion dropdown menu style"""
    return f"""
        QListWidget {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QListWidget::item {{
            padding: 10px 12px;
            border-bottom: 1px solid {BACKGROUND};
        }}
        QListWidget::item:hover {{
            background: {PRIMARY_LIGHT};
        }}
        QListWidget::item:selected {{
            background: {PRIMARY};
            color: {WHITE};
        }}
    """


def get_item_widget_normal_style():
    """Get normal state style for invoice item widget"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 8px;
            margin: 2px 0;
        }}
    """


def get_item_widget_hover_style():
    """Get hover state style for invoice item widget"""
    return f"""
        QFrame {{
            background: {PRIMARY_LIGHT};
            border: 1px solid {PRIMARY};
            border-radius: 8px;
            margin: 2px 0;
        }}
    """


def get_error_highlight_style():
    """Get error highlight style for validation"""
    return f"""
        border: 2px solid {DANGER} !important;
        background: {DANGER_LIGHT} !important;
    """


def get_success_highlight_style():
    """Get success highlight style for validation"""
    return f"""
        border: 2px solid {SUCCESS} !important;
        background: {SUCCESS_LIGHT} !important;
    """


def get_print_button_style():
    """Get print button style"""
    return f"""
        QPushButton {{
            background: {SUCCESS};
            color: {WHITE};
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: #059669;
        }}
    """


def get_secondary_button_style():
    """Get secondary button style"""
    return f"""
        QPushButton {{
            background: {WHITE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 10px 20px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {BACKGROUND};
            border-color: {TEXT_SECONDARY};
        }}
    """


def get_transparent_container_style():
    """Get transparent container style"""
    return """
        QWidget {
            background: transparent;
            border: none;
        }
    """


def get_transparent_frame_style():
    """Get transparent frame style"""
    return """
        QFrame {
            background: transparent;
            border: none;
        }
    """


def get_header_column_style():
    """Get header column container style"""
    return f"""
        QFrame {{
            background: transparent;
            border: none;
        }}
    """


def get_items_header_style():
    """Get items section header style"""
    return f"""
        QFrame {{
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 6px 6px 0 0;
            padding: 8px 12px;
        }}
    """


def get_items_header_label_style():
    """Get items header label style - clean uppercase without emojis"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: {BACKGROUND};
            border: none;
            padding: 8px 4px;
        }}
    """


def get_item_row_even_style():
    """Get style for even-numbered item rows with hover highlight"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            margin: 1px 0;
        }}
        QFrame:hover {{
            background: #F3F4F6;
            border: 2px solid {PRIMARY};
            padding: 0px;
            margin: 0px;
        }}
    """


def get_item_row_odd_style():
    """Get style for odd-numbered item rows with hover highlight"""
    return f"""
        QFrame {{
            background: #F9FAFB;
            border: 1px solid {BORDER};
            border-radius: 6px;
            margin: 1px 0;
        }}
        QFrame:hover {{
            background: #F3F4F6;
            border: 2px solid {PRIMARY};
            padding: 0px;
            margin: 0px;
        }}
    """


def get_item_row_error_style():
    """Get style for item row with validation error - with hover highlight"""
    return f"""
        QFrame {{
            background: #FEF2F2;
            border: 2px solid {DANGER};
            border-radius: 6px;
            margin: 1px 0;
        }}
        QFrame:hover {{
            background: #FEE2E2;
            border: 2px solid {DANGER};
        }}
    """


def get_empty_state_style():
    """Get style for empty state message in items section"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: 14px;
            font-style: italic;
            padding: 40px 20px;
            background: {BACKGROUND};
            border: 2px dashed {BORDER};
            border-radius: 8px;
        }}
    """


def get_quick_chip_recent_style():
    """Get style for recently used product chips (highlighted)"""
    return f"""
        QPushButton {{
            background: #EFF6FF;
            color: {PRIMARY};
            border: 1px solid {PRIMARY};
            border-radius: 16px;
            padding: 6px 14px;
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {PRIMARY};
            color: {WHITE};
        }}
    """


def get_stock_indicator_style(in_stock: bool = True):
    """Get style for stock availability indicator"""
    if in_stock:
        return f"""
            QLabel {{
                color: {SUCCESS};
                font-size: 10px;
                font-weight: 500;
                background: {SUCCESS_LIGHT};
                border-radius: 3px;
                padding: 2px 6px;
            }}
        """
    else:
        return f"""
            QLabel {{
                color: {DANGER};
                font-size: 10px;
                font-weight: 500;
                background: {DANGER_LIGHT};
                border-radius: 3px;
                padding: 2px 6px;
            }}
        """


def get_action_icon_button_style(color: str = None):
    """Get style for small action icon buttons with enhanced hover, pressed, disabled, and focus states"""
    bg_color = color or SUCCESS
    # Calculate hover and shadow colors based on button color
    hover_color = PRIMARY_HOVER if bg_color == SUCCESS else '#DC2626'
    # Calculate shadow color (with reduced opacity for subtle effect)
    if bg_color == SUCCESS:
        shadow_color = '16, 185, 129'  # SUCCESS RGB
        border_color = '#059669'  # Darker green
        focus_color = PRIMARY  # Blue focus ring for visibility
    else:  # DANGER color
        shadow_color = '239, 68, 68'  # DANGER RGB
        border_color = '#B91C1C'  # Darker red
        focus_color = PRIMARY  # Blue focus ring for visibility
    
    return f"""
        QPushButton {{
            background: {bg_color};
            color: {WHITE};
            border: 2px solid transparent;
            border-radius: 4px;
            padding: 3px;
            font-size: 14px;
            font-weight: bold;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            outline: none;
        }}
        QPushButton:hover {{
            background: {hover_color};
            border: 2px solid {border_color};
        }}
        QPushButton:pressed {{
            background: {border_color};
            border: 2px solid {border_color};
            padding: 4px 2px 2px 4px;
        }}
        QPushButton:focus {{
            border: 2px solid {focus_color};
            outline: none;
        }}
        QPushButton:focus:hover {{
            border: 2px solid {border_color};
        }}
        QPushButton:disabled {{
            background: #CCCCCC;
            color: #999999;
            border: 2px solid #DDDDDD;
            outline: none;
            opacity: 0.6;
        }}
    """


def get_pdf_preview_dialog_style():
    """Get PDF preview dialog style"""
    return f"""
        QDialog {{
            background: {BACKGROUND};
        }}
    """


def get_pdf_page_container_style():
    """Get PDF page container style"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 4px;
        }}
    """


def get_pdf_page_label_style():
    """Get PDF page label style"""
    return f"""
        QLabel {{
            background: {WHITE};
        }}
    """


def get_pdf_toolbar_style():
    """Get PDF toolbar style"""
    return f"""
        QFrame {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 8px;
        }}
    """


def get_pdf_toolbar_button_style():
    """Get PDF toolbar button style"""
    return f"""
        QPushButton {{
            background: {BACKGROUND};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: {FONT_SIZE_SMALL}px;
        }}
        QPushButton:hover {{
            background: {PRIMARY_LIGHT};
            border-color: {PRIMARY};
        }}
    """


def get_pdf_page_info_style():
    """Get PDF page info label style"""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_SMALL}px;
            background: transparent;
        }}
    """


# ============== INVOICE TOTALS SECTION STYLES ==============

def get_totals_row_label_style():
    """Get style for totals section row labels (right-aligned)"""
    return f"""
        QLabel {{
            font-size: 13px;
            font-weight: 500;
            color: {TEXT_SECONDARY};
            background: transparent;
            border: none;
            padding: 4px 0;
        }}
    """


def get_totals_row_value_style():
    """Get style for totals section row values"""
    return f"""
        QLabel {{
            font-size: 14px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            background: transparent;
            border: none;
            padding: 4px 8px;
            min-width: 100px;
        }}
    """


def get_subtotal_value_style():
    """Get style for subtotal value"""
    return f"""
        QLabel {{
            font-size: 14px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 6px 10px;
            min-width: 100px;
        }}
    """


def get_discount_value_style():
    """Get style for discount value (red/negative)"""
    return f"""
        QLabel {{
            font-size: 13px;
            font-weight: 600;
            color: #DC2626;
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 80px;
            max-width: 120px;
        }}
    """


def get_tax_value_style():
    """Get style for tax value"""
    return f"""
        QLabel {{
            font-size: 14px;
            font-weight: 600;
            color: #059669;
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 4px;
            padding: 6px 10px;
            min-width: 100px;
        }}
    """


def get_tax_breakdown_style():
    """Get style for tax breakdown box (CGST/SGST or IGST)"""
    return f"""
        QLabel {{
            font-size: 11px;
            color: {TEXT_SECONDARY};
            background: #F9FAFB;
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 4px 8px;
        }}
    """


def get_other_charges_input_style():
    """Get style for other charges input field"""
    return f"""
        QDoubleSpinBox {{
            font-size: 13px;
            font-weight: 500;
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            background: {WHITE};
            min-width: 100px;
        }}
        QDoubleSpinBox:focus {{
            border: 2px solid {PRIMARY};
        }}
        QDoubleSpinBox:hover {{
            border: 1px solid {PRIMARY_HOVER};
        }}
    """


def get_grand_total_row_style():
    """Get style for grand total row container with top border"""
    return f"""
        QWidget {{
            background: transparent;
            border: none;
            border-top: 2px solid {BORDER};
            padding-top: 8px;
            margin-top: 4px;
        }}
    """


def get_grand_total_label_enhanced_style():
    """Get enhanced style for grand total label"""
    return f"""
        QLabel {{
            font-size: 13px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
            background: transparent;
            border: none;
            padding: 4px 0;
        }}
    """


def get_grand_total_value_enhanced_style():
    """Get enhanced style for grand total value"""
    return f"""
        QLabel {{
            font-size: 20px;
            font-weight: bold;
            color: {PRIMARY};
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border: 2px solid {PRIMARY};
            border-radius: 8px;
            padding: 10px 16px;
            min-width: 140px;
        }}
    """


def get_paid_amount_input_style():
    """Get style for paid amount input"""
    return f"""
        QDoubleSpinBox {{
            font-size: 14px;
            font-weight: 600;
            border: 2px solid #10B981;
            border-radius: 6px;
            padding: 6px 10px;
            background: #ECFDF5;
            color: #059669;
            min-width: 120px;
        }}
        QDoubleSpinBox:focus {{
            border: 2px solid #059669;
            background: {WHITE};
        }}
        QDoubleSpinBox:hover {{
            border: 2px solid #059669;
        }}
    """


def get_balance_due_style_dynamic(balance: float):
    """Get dynamic style for balance due based on amount"""
    if balance <= 0:
        # Fully paid - green with checkmark style
        return f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: #059669;
                background: #ECFDF5;
                border: 1px solid #10B981;
                border-radius: 6px;
                padding: 6px 12px;
            }}
        """
    elif balance > 10000:
        # High balance - warning style with animation hint
        return f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: #DC2626;
                background: #FEF2F2;
                border: 1px solid #EF4444;
                border-radius: 6px;
                padding: 6px 12px;
            }}
        """
    else:
        # Normal balance
        return f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: #F59E0B;
                background: #FFFBEB;
                border: 1px solid #FBBF24;
                border-radius: 6px;
                padding: 6px 12px;
            }}
        """


def get_roundoff_row_style():
    """Get style for round-off row"""
    return f"""
        QWidget {{
            background: transparent;
            border: none;
        }}
    """


def get_invoice_discount_input_style():
    """Get style for invoice-level discount input"""
    return f"""
        QWidget {{
            background: transparent;
        }}
        QDoubleSpinBox {{
            font-size: 13px;
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 4px;
            background: {WHITE};
            min-width: 70px;
        }}
        QDoubleSpinBox:focus {{
            border: 2px solid {PRIMARY};
        }}
        QComboBox {{
            font-size: 12px;
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 4px;
            background: {WHITE};
            min-width: 50px;
        }}
    """


def get_totals_separator_style():
    """Get style for separator line in totals section"""
    return f"""
        QFrame {{
            background-color: {BORDER};
            max-height: 1px;
            margin: 8px 0;
        }}
    """


def get_previous_balance_style():
    """Get style for previous outstanding balance display"""
    return f"""
        QLabel {{
            font-size: 12px;
            color: #9333EA;
            background: #FAF5FF;
            border: 1px solid #E9D5FF;
            border-radius: 4px;
            padding: 4px 8px;
        }}
    """
