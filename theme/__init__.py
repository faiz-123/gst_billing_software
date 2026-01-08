"""
Theme module - Contains colors, fonts, and styles for the application
"""

from .colors import (
    PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_BG, DANGER, WARNING,
    BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, WHITE, PURPLE
)
from .fonts import (
    FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
    FONT_SIZE_TITLE, FONT_SIZE_HEADER, get_title_font, get_header_font
)
from .styles import (
    APP_STYLESHEET, get_button_style, get_sidebar_style, get_card_style,
    get_calendar_stylesheet
)

__all__ = [
    # Colors
    'PRIMARY', 'PRIMARY_HOVER', 'SUCCESS', 'SUCCESS_BG', 'DANGER', 'WARNING',
    'BACKGROUND', 'TEXT_PRIMARY', 'TEXT_SECONDARY', 'BORDER', 'WHITE', 'PURPLE',
    # Fonts
    'FONT_FAMILY', 'FONT_SIZE_SMALL', 'FONT_SIZE_NORMAL', 'FONT_SIZE_LARGE',
    'FONT_SIZE_TITLE', 'FONT_SIZE_HEADER', 'get_title_font', 'get_header_font',
    # Styles
    'APP_STYLESHEET', 'get_button_style', 'get_sidebar_style', 'get_card_style',
    'get_calendar_stylesheet'
]
