"""
Font definitions for GST Billing Software
Contains font family and size constants
"""

from PySide6.QtGui import QFont

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


def get_label_font(size=FONT_SIZE_SMALL):
    """Get label font with specified size (bold)
    
    Args:
        size: Font size (default: FONT_SIZE_SMALL)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font


def get_section_title_font(size=14):
    """Get section title font
    
    Args:
        size: Font size (default: 14)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    return font


def get_link_font(size=13):
    """Get font for link/hyperlink text
    
    Args:
        size: Font size (default: 13)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    return font


def get_checkbox_font(size=FONT_SIZE_SMALL):
    """Get font for checkboxes
    
    Args:
        size: Font size (default: FONT_SIZE_SMALL)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(FONT_FAMILY, size)
    return font
