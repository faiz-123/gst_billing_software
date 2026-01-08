"""
Font definitions for GST Billing Software
Contains font family and size constants
"""

from PyQt5.QtGui import QFont

# ---------------- Font Family ----------------
FONT_FAMILY = "Arial"

# ---------------- Font Sizes ----------------
FONT_SIZE_SMALL = 12
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_TITLE = 24
FONT_SIZE_HEADER = 32

# ---------------- Font Helpers ----------------
def get_title_font(size=FONT_SIZE_TITLE):
    """Get title font with specified size
    
    Args:
        size: Font size (default: FONT_SIZE_TITLE)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font


def get_header_font(size=FONT_SIZE_HEADER):
    """Get header font with specified size
    
    Args:
        size: Font size (default: FONT_SIZE_HEADER)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font


def get_normal_font(size=FONT_SIZE_NORMAL):
    """Get normal font with specified size
    
    Args:
        size: Font size (default: FONT_SIZE_NORMAL)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    return font


def get_bold_font(size=FONT_SIZE_NORMAL):
    """Get bold font with specified size
    
    Args:
        size: Font size (default: FONT_SIZE_NORMAL)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font
