"""
Constants for Sales Invoice Dialog

This file centralizes all magic numbers used in sales_invoice_form_dialog.py
for easier maintenance and consistency.

Categories:
- Window dimensions
- Layout spacings and margins
- Widget dimensions
- Popup and completer settings
- Header dimensions (expanded/compact modes)
- Items section dimensions
- Totals section dimensions
"""

# ============================================================================
# WINDOW DIMENSIONS
# ============================================================================

DIALOG_WIDTH_DEFAULT = 1400
DIALOG_HEIGHT_DEFAULT = 900

# ============================================================================
# MAIN LAYOUT
# ============================================================================

MAIN_LAYOUT_SPACING = 12
MAIN_LAYOUT_MARGINS = (20, 20, 20, 20)  # (left, top, right, bottom)

# ============================================================================
# BUTTON CONTAINER
# ============================================================================

BUTTON_CONTAINER_MIN_HEIGHT = 60
BUTTON_LAYOUT_SPACING = 10
BUTTON_LAYOUT_MARGINS = (0, 0, 0, 0)

# ============================================================================
# ACTION LAYOUT
# ============================================================================

ACTION_LAYOUT_SPACING = 10
ACTION_LAYOUT_MARGINS = (0, 0, 0, 0)

# ============================================================================
# HEADER SECTION
# ============================================================================

HEADER_SECTION_PADDING = 15
HEADER_MIN_HEIGHT = 160  # Flexible minimum
HEADER_MAX_HEIGHT = 240  # Flexible maximum

# Compact header
HEADER_COMPACT_MIN_HEIGHT = 120
HEADER_COMPACT_MAX_HEIGHT = 140

HEADER_LAYOUT_SPACING = 12
HEADER_LAYOUT_MARGINS = (20, 15, 20, 15)  # (left, top, right, bottom)

# Row 1 (Bill Type, Tax Type, Date, Invoice No)
ROW1_SPACING = 15
ROW1_MARGINS = (0, 0, 0, 0)

# Row 2 (Party Selection)
ROW2_SPACING = 10

# ============================================================================
# BILL TYPE BUTTON
# ============================================================================

BILLTYPE_BTN_HEIGHT = 42
BILLTYPE_BTN_WIDTH = 130

# ============================================================================
# TAX TYPE SEGMENT
# ============================================================================

TAX_SEGMENT_HEIGHT = 42
TAX_SEGMENT_BTN_HEIGHT = 38
TAX_TYPE_BOX_WIDTH = 280

SEGMENT_LAYOUT_MARGINS = (2, 2, 2, 2)
SEGMENT_LAYOUT_SPACING = 0

# ============================================================================
# PARTY INFO DISPLAY
# ============================================================================

PARTY_INFO_MIN_WIDTH = 700
PARTY_INFO_MAX_WIDTH = 900

# ============================================================================
# PARTY SEARCH BOX
# ============================================================================

PARTY_SEARCH_HEIGHT = 48
PARTY_SEARCH_MIN_WIDTH = 400
PARTY_COMPLETER_MAX_VISIBLE_ITEMS = 15
PARTY_COMPLETER_POPUP_MIN_WIDTH = 500
PARTY_COMPLETER_POPUP_MAX_HEIGHT = 400
PARTY_COMPLETER_POPUP_GAP_FROM_INPUT = 10

# ============================================================================
# INVOICE DATE BOX
# ============================================================================

INVOICE_DATE_BOX_HEIGHT = 42
INVOICE_DATE_BOX_WIDTH = 170

INVOICE_DATE_BOX_LAYOUT_MARGINS = (0, 0, 0, 0)
INVOICE_DATE_BOX_LAYOUT_SPACING = 4

# ============================================================================
# INVOICE NUMBER BOX
# ============================================================================

INVOICE_NUMBER_BOX_HEIGHT = 42
INVOICE_NUMBER_BOX_WIDTH = 150

INVOICE_NUMBER_BOX_LAYOUT_MARGINS = (0, 0, 0, 0)
INVOICE_NUMBER_BOX_LAYOUT_SPACING = 4

# ============================================================================
# ITEMS SECTION
# ============================================================================

ITEMS_SECTION_PADDING = 15
ITEMS_LAYOUT_SPACING = 8
ITEMS_LAYOUT_MARGINS = (10, 10, 10, 10)

# Quick Products Section
QUICK_PRODUCTS_LAYOUT_SPACING = 8
QUICK_PRODUCTS_LAYOUT_MARGINS = (8, 8, 8, 8)
QUICK_PRODUCTS_LABEL_SIZE = 12

QUICK_PRODUCTS_SHOW_COUNT = 5  # Show top 5 products
QUICK_PRODUCTS_RECENT_COUNT = 3  # Show 3 recent products
QUICK_PRODUCTS_POPULAR_COUNT = 2  # Show 2 popular products

QUICK_PRODUCT_CHIP_HEIGHT = 32
QUICK_PRODUCT_CHIP_MIN_WIDTH = 100

# Column Headers
HEADERS_LAYOUT_SPACING = 2
HEADERS_LAYOUT_MARGINS = (8, 4, 8, 4)
HEADER_LABEL_HEIGHT = 32

# Header column widths for table items
HEADER_COLUMN_NO_WIDTH = 40
HEADER_COLUMN_PRODUCT_WIDTH = 520
HEADER_COLUMN_HSN_WIDTH = 100
HEADER_COLUMN_QTY_WIDTH = 70
HEADER_COLUMN_UNIT_WIDTH = 60
HEADER_COLUMN_RATE_WIDTH = 100
HEADER_COLUMN_DISC_WIDTH = 75
HEADER_COLUMN_TAX_WIDTH = 85
HEADER_COLUMN_AMOUNT_WIDTH = 110
HEADER_COLUMN_ACTION_WIDTH = 60

# Empty State
EMPTY_STATE_MIN_HEIGHT = 120

# Items Container
ITEMS_CONTAINER_SPACING = 0
ITEMS_CONTAINER_MARGINS = (0, 0, 0, 0)

# ============================================================================
# TOTALS SECTION
# ============================================================================

TOTALS_SECTION_PADDING = 12
TOTALS_SECTION_MIN_HEIGHT = 250

TOTALS_LAYOUT_MARGINS = (15, 12, 15, 12)
TOTALS_LAYOUT_SPACING = 20

LEFT_CONTAINER_SPACING = 10

NOTES_FIELD_HEIGHT = 70

# Amount in Words
AMOUNT_WORDS_CONTAINER_SPACING = 6
AMOUNT_WORDS_LABEL_MIN_WIDTH = 400
AMOUNT_WORDS_LABEL_MIN_HEIGHT = 50

# Totals Grid
TOTALS_GRID_SPACING = 6
TOTALS_GRID_MARGINS = (0, 0, 0, 0)

# Totals Row Heights
TOTALS_ROW_HEIGHT = 32
TOTALS_LABEL_WIDTH = 200

# ============================================================================
# PREVIEW DIALOGS
# ============================================================================

# HTML Preview Dialog
HTML_PREVIEW_DIALOG_WIDTH = 900
HTML_PREVIEW_DIALOG_HEIGHT = 850
HTML_PREVIEW_DIALOG_MIN_WIDTH = 800
HTML_PREVIEW_DIALOG_MIN_HEIGHT = 600

HTML_PREVIEW_HEADER_HEIGHT = 60
HTML_PREVIEW_LAYOUT_MARGINS = (10, 10, 10, 10)
HTML_PREVIEW_LAYOUT_SPACING = 10
HTML_PREVIEW_HEADER_MARGINS = (15, 5, 15, 5)
HTML_PREVIEW_TITLE_FONT_SIZE = 16

# PDF Preview Dialog
PDF_PREVIEW_DIALOG_WIDTH = 900
PDF_PREVIEW_DIALOG_HEIGHT = 800

PDF_PREVIEW_HEADER_HEIGHT = 60
PDF_PREVIEW_LAYOUT_MARGINS = (10, 10, 10, 10)
PDF_PREVIEW_LAYOUT_SPACING = 10
PDF_PREVIEW_HEADER_MARGINS = (15, 5, 15, 5)

# ============================================================================
# POPUP POSITIONING
# ============================================================================

COMPLETER_POPUP_POSITIONING_DELAY_MS = 0  # QTimer.singleShot delay for positioning
PARTY_TEXT_VALIDATION_DEBOUNCE_MS = 300  # Debounce time for validation

# ============================================================================
# PARTY BOX STYLING
# ============================================================================

PARTY_BOX_LAYOUT_MARGINS = (0, 0, 0, 0)
PARTY_BOX_LAYOUT_SPACING = 4
PARTY_HEADER_SPACING = 10
PARTY_SEARCH_LAYOUT_MARGINS = (0, 0, 0, 0)
PARTY_SEARCH_LAYOUT_SPACING = 5

# ============================================================================
# BILL TYPE BOX
# ============================================================================

BILLTYPE_BOX_LAYOUT_MARGINS = (0, 0, 0, 0)
BILLTYPE_BOX_LAYOUT_SPACING = 4

# ============================================================================
# TAX TYPE BOX
# ============================================================================

TAX_BOX_LAYOUT_MARGINS = (0, 0, 0, 0)
TAX_BOX_LAYOUT_SPACING = 4

# ============================================================================
# COMMON SPACING VALUES
# ============================================================================

# Used across multiple components for consistency
SPACING_XS = 2
SPACING_SM = 4
SPACING_MD = 6
SPACING_LG = 8
SPACING_XL = 10
SPACING_2XL = 12
SPACING_3XL = 15
SPACING_4XL = 20

# Common margin tuples (left, top, right, bottom)
MARGINS_NONE = (0, 0, 0, 0)
MARGINS_COMPACT = (8, 4, 8, 4)
MARGINS_NORMAL = (10, 10, 10, 10)
MARGINS_LOOSE = (15, 12, 15, 12)
MARGINS_EXTRA = (20, 15, 20, 15)

# ============================================================================
# NUMERIC CONSTANTS
# ============================================================================

# Numeric limits and counts
MIN_PARTY_NAME_LENGTH = 2  # Minimum characters for party name search
MIN_INVOICE_NUMBER_LENGTH = 1
QUICK_ADD_DIALOG_WIDTH = 900
QUICK_ADD_DIALOG_HEIGHT = 900

# Minimum item count thresholds
MIN_ITEMS_FOR_DISCOUNT = 1  # Items required before allowing discount

# ============================================================================
# STYLE CONSTANTS
# ============================================================================

# Border radius values (in pixels)
BORDER_RADIUS_SM = 4
BORDER_RADIUS_MD = 6
BORDER_RADIUS_LG = 8
