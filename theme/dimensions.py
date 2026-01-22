"""
Dimension constants for dialogs, windows, and UI components.
Centralizes all size-related configuration for consistency.
"""

# ============================================================
# DIALOG SIZES
# ============================================================

# Standard Form Dialog (Product, Party, etc.)
DIALOG_FORM_DEFAULT_WIDTH = 1300
DIALOG_FORM_DEFAULT_HEIGHT = 1000
DIALOG_FORM_MIN_WIDTH = 800
DIALOG_FORM_MIN_HEIGHT = 600

# Large Dialog (Invoice, Reports)
DIALOG_LARGE_DEFAULT_WIDTH = 1400
DIALOG_LARGE_DEFAULT_HEIGHT = 900
DIALOG_LARGE_MIN_WIDTH = 1000
DIALOG_LARGE_MIN_HEIGHT = 700

# Small Dialog (Confirmation, Simple Forms)
DIALOG_SMALL_DEFAULT_WIDTH = 500
DIALOG_SMALL_DEFAULT_HEIGHT = 400
DIALOG_SMALL_MIN_WIDTH = 400
DIALOG_SMALL_MIN_HEIGHT = 300

# ============================================================
# BUTTON SIZES
# ============================================================

BUTTON_PRIMARY_WIDTH = 140
BUTTON_PRIMARY_HEIGHT = 44
BUTTON_SECONDARY_WIDTH = 120
BUTTON_SECONDARY_HEIGHT = 44
BUTTON_ICON_SIZE = 36

# Quick Action Chips
CHIP_HEIGHT = 32
CHIP_MIN_WIDTH = 50

# ============================================================
# FOOTER & HEADER
# ============================================================

DIALOG_HEADER_HEIGHT = 72
DIALOG_FOOTER_HEIGHT = 80

# ============================================================
# SPACING & MARGINS
# ============================================================

SECTION_MARGIN = 24
SECTION_SPACING = 16
FIELD_SPACING = 20
GRID_SPACING = 20

# ============================================================
# INPUT FIELD SIZES
# ============================================================

INPUT_HEIGHT = 44
INPUT_MIN_WIDTH = 200
TEXTAREA_MIN_HEIGHT = 80

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_form_dialog_size():
    """Returns (default_width, default_height, min_width, min_height) for form dialogs"""
    return (
        DIALOG_FORM_DEFAULT_WIDTH,
        DIALOG_FORM_DEFAULT_HEIGHT,
        DIALOG_FORM_MIN_WIDTH,
        DIALOG_FORM_MIN_HEIGHT
    )

def get_large_dialog_size():
    """Returns (default_width, default_height, min_width, min_height) for large dialogs"""
    return (
        DIALOG_LARGE_DEFAULT_WIDTH,
        DIALOG_LARGE_DEFAULT_HEIGHT,
        DIALOG_LARGE_MIN_WIDTH,
        DIALOG_LARGE_MIN_HEIGHT
    )

def get_small_dialog_size():
    """Returns (default_width, default_height, min_width, min_height) for small dialogs"""
    return (
        DIALOG_SMALL_DEFAULT_WIDTH,
        DIALOG_SMALL_DEFAULT_HEIGHT,
        DIALOG_SMALL_MIN_WIDTH,
        DIALOG_SMALL_MIN_HEIGHT
    )
