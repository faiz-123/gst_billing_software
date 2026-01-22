"""
Theme module - Contains colors, fonts, styles, and dimensions for the application
"""

from .colors import (
    PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_BG, DANGER, WARNING,
    BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, WHITE, PURPLE, PURPLE_LIGHT,
    TEXT_DARK, TEXT_MUTED, PRIMARY_LIGHT, PRIMARY_DARK, DANGER_LIGHT, SUCCESS_LIGHT,
    # Purchase theme colors (amber/orange)
    PURCHASE_PRIMARY, PURCHASE_PRIMARY_HOVER, PURCHASE_BG_LIGHT,
    PURCHASE_BORDER_ACCENT, PURCHASE_TEXT_DARK, WARNING_LIGHT,
    # Gray scale
    GRAY_50, GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500,
    GRAY_600, GRAY_700, GRAY_800, GRAY_900,
    # Sidebar
    SIDEBAR_BG, SIDEBAR_TEXT, SIDEBAR_ACCENT
)
from .fonts import (
    FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
    FONT_SIZE_TITLE, FONT_SIZE_HEADER, get_title_font, get_header_font,
    get_normal_font, get_bold_font, get_label_font, get_section_title_font,
    get_link_font, get_checkbox_font
)
from .dimensions import (
    # Dialog sizes
    DIALOG_FORM_DEFAULT_WIDTH, DIALOG_FORM_DEFAULT_HEIGHT,
    DIALOG_FORM_MIN_WIDTH, DIALOG_FORM_MIN_HEIGHT,
    DIALOG_LARGE_DEFAULT_WIDTH, DIALOG_LARGE_DEFAULT_HEIGHT,
    DIALOG_LARGE_MIN_WIDTH, DIALOG_LARGE_MIN_HEIGHT,
    DIALOG_SMALL_DEFAULT_WIDTH, DIALOG_SMALL_DEFAULT_HEIGHT,
    DIALOG_SMALL_MIN_WIDTH, DIALOG_SMALL_MIN_HEIGHT,
    # Button sizes
    BUTTON_PRIMARY_WIDTH, BUTTON_PRIMARY_HEIGHT,
    BUTTON_SECONDARY_WIDTH, BUTTON_SECONDARY_HEIGHT, BUTTON_ICON_SIZE,
    CHIP_HEIGHT, CHIP_MIN_WIDTH,
    # Header/Footer
    DIALOG_HEADER_HEIGHT, DIALOG_FOOTER_HEIGHT,
    # Spacing
    SECTION_MARGIN, SECTION_SPACING, FIELD_SPACING, GRID_SPACING,
    # Input sizes
    INPUT_HEIGHT, INPUT_MIN_WIDTH, TEXTAREA_MIN_HEIGHT,
    # Helper functions
    get_form_dialog_size, get_large_dialog_size, get_small_dialog_size
)
from .styles import (
    APP_STYLESHEET, get_button_style, get_sidebar_style, get_card_style,
    get_calendar_stylesheet, get_input_style, get_table_style,
    get_dialog_input_style, get_readonly_input_style, get_error_input_style,
    get_textarea_style, get_checkbox_style, get_section_frame_style,
    get_dialog_footer_style, get_cancel_button_style, get_save_button_style,
    get_link_label_style, get_scroll_area_style,
    # Screen/List specific styles
    get_action_frame_style, get_search_container_style, get_search_input_style,
    get_primary_action_button_style, get_secondary_action_button_style,
    get_stat_card_style, get_filter_frame_style, get_filter_combo_style,
    get_icon_button_style, get_clear_button_style, get_table_frame_style,
    get_enhanced_table_style, get_count_badge_style, get_status_badge_style,
    get_row_action_button_style, get_filter_label_style, get_stat_label_style,
    get_stat_value_style, get_stat_icon_container_style,
    # Invoice form specific styles
    get_row_number_style, get_product_input_style, get_hsn_readonly_style,
    get_unit_label_style, get_readonly_spinbox_style, get_amount_display_style,
    get_circle_button_style, get_invoice_dialog_style, get_dialog_header_style,
    get_preview_header_style, get_preview_close_button_style,
    get_html_viewer_style, get_pdf_viewer_style,
    # Form field styles
    get_form_label_style, get_form_combo_style, get_date_edit_style,
    get_invoice_number_input_style, get_party_search_input_style,
    get_section_header_style,
    # Quick action chips
    get_quick_chip_style, get_item_count_badge_style,
    # Scroll area styles
    get_transparent_scroll_area_style, get_items_scroll_container_style,
    # Summary section styles
    get_summary_label_style, get_summary_value_style, get_total_row_style,
    get_grand_total_label_style, get_grand_total_value_style,
    get_balance_due_style, get_roundoff_input_style, get_roundoff_value_style,
    # Link and action styles
    get_add_party_link_style,
    # Menu and popup styles
    get_context_menu_style, get_party_suggestion_menu_style,
    # Item widget styles
    get_item_widget_hover_style, get_item_widget_normal_style,
    # Validation/highlight styles
    get_error_highlight_style, get_success_highlight_style,
    # Print dialog styles
    get_print_button_style, get_secondary_button_style,
    # Transparent container styles
    get_transparent_container_style, get_transparent_frame_style,
    # Header section styles
    get_header_column_style, get_items_header_style, get_items_header_label_style,
    # PDF preview styles
    get_pdf_preview_dialog_style, get_pdf_page_container_style,
    get_pdf_page_label_style, get_pdf_toolbar_style,
    get_pdf_toolbar_button_style, get_pdf_page_info_style,
    # Items section improvements
    get_item_row_even_style, get_item_row_odd_style, get_item_row_error_style,
    get_empty_state_style, get_quick_chip_recent_style, get_stock_indicator_style,
    get_action_icon_button_style,
    # Invoice totals section styles (NEW)
    get_totals_row_label_style, get_totals_row_value_style,
    get_subtotal_value_style, get_discount_value_style, get_tax_value_style,
    get_tax_breakdown_style, get_other_charges_input_style,
    get_grand_total_row_style, get_grand_total_label_enhanced_style,
    get_grand_total_value_enhanced_style, get_paid_amount_input_style,
    get_balance_due_style_dynamic, get_roundoff_row_style,
    get_invoice_discount_input_style, get_totals_separator_style,
    get_previous_balance_style
)

__all__ = [
    # Colors
    'PRIMARY', 'PRIMARY_HOVER', 'SUCCESS', 'SUCCESS_BG', 'DANGER', 'WARNING',
    'BACKGROUND', 'TEXT_PRIMARY', 'TEXT_SECONDARY', 'BORDER', 'WHITE', 'PURPLE',
    'TEXT_DARK', 'TEXT_MUTED', 'PRIMARY_LIGHT', 'PRIMARY_DARK', 'DANGER_LIGHT', 'SUCCESS_LIGHT',
    # Fonts
    'FONT_FAMILY', 'FONT_SIZE_SMALL', 'FONT_SIZE_NORMAL', 'FONT_SIZE_LARGE',
    'FONT_SIZE_TITLE', 'FONT_SIZE_HEADER', 'get_title_font', 'get_header_font',
    'get_normal_font', 'get_bold_font', 'get_label_font', 'get_section_title_font',
    'get_link_font', 'get_checkbox_font',
    # Dimensions - Dialog sizes
    'DIALOG_FORM_DEFAULT_WIDTH', 'DIALOG_FORM_DEFAULT_HEIGHT',
    'DIALOG_FORM_MIN_WIDTH', 'DIALOG_FORM_MIN_HEIGHT',
    'DIALOG_LARGE_DEFAULT_WIDTH', 'DIALOG_LARGE_DEFAULT_HEIGHT',
    'DIALOG_LARGE_MIN_WIDTH', 'DIALOG_LARGE_MIN_HEIGHT',
    'DIALOG_SMALL_DEFAULT_WIDTH', 'DIALOG_SMALL_DEFAULT_HEIGHT',
    'DIALOG_SMALL_MIN_WIDTH', 'DIALOG_SMALL_MIN_HEIGHT',
    # Dimensions - Button sizes
    'BUTTON_PRIMARY_WIDTH', 'BUTTON_PRIMARY_HEIGHT',
    'BUTTON_SECONDARY_WIDTH', 'BUTTON_SECONDARY_HEIGHT', 'BUTTON_ICON_SIZE',
    'CHIP_HEIGHT', 'CHIP_MIN_WIDTH',
    # Dimensions - Header/Footer
    'DIALOG_HEADER_HEIGHT', 'DIALOG_FOOTER_HEIGHT',
    # Dimensions - Spacing
    'SECTION_MARGIN', 'SECTION_SPACING', 'FIELD_SPACING', 'GRID_SPACING',
    # Dimensions - Input sizes
    'INPUT_HEIGHT', 'INPUT_MIN_WIDTH', 'TEXTAREA_MIN_HEIGHT',
    # Dimensions - Helper functions
    'get_form_dialog_size', 'get_large_dialog_size', 'get_small_dialog_size',
    # Styles - Dialog/General
    'APP_STYLESHEET', 'get_button_style', 'get_sidebar_style', 'get_card_style',
    'get_calendar_stylesheet', 'get_input_style', 'get_table_style',
    'get_dialog_input_style', 'get_readonly_input_style', 'get_error_input_style',
    'get_textarea_style', 'get_checkbox_style', 'get_section_frame_style',
    'get_dialog_footer_style', 'get_cancel_button_style', 'get_save_button_style',
    'get_link_label_style', 'get_scroll_area_style',
    # Styles - Screen/List specific
    'get_action_frame_style', 'get_search_container_style', 'get_search_input_style',
    'get_primary_action_button_style', 'get_secondary_action_button_style',
    'get_stat_card_style', 'get_filter_frame_style', 'get_filter_combo_style',
    'get_icon_button_style', 'get_clear_button_style', 'get_table_frame_style',
    'get_enhanced_table_style', 'get_count_badge_style', 'get_status_badge_style',
    'get_row_action_button_style', 'get_filter_label_style', 'get_stat_label_style',
    'get_stat_value_style', 'get_stat_icon_container_style',
    # Invoice form specific styles
    'get_row_number_style', 'get_product_input_style', 'get_hsn_readonly_style',
    'get_unit_label_style', 'get_readonly_spinbox_style', 'get_amount_display_style',
    'get_circle_button_style', 'get_invoice_dialog_style', 'get_dialog_header_style',
    'get_preview_header_style', 'get_preview_close_button_style',
    'get_html_viewer_style', 'get_pdf_viewer_style',
    # Form field styles
    'get_form_label_style', 'get_form_combo_style', 'get_date_edit_style',
    'get_invoice_number_input_style', 'get_party_search_input_style',
    'get_section_header_style',
    # Quick action chips
    'get_quick_chip_style', 'get_item_count_badge_style',
    # Scroll area styles
    'get_transparent_scroll_area_style', 'get_items_scroll_container_style',
    # Summary section styles
    'get_summary_label_style', 'get_summary_value_style', 'get_total_row_style',
    'get_grand_total_label_style', 'get_grand_total_value_style',
    'get_balance_due_style', 'get_roundoff_input_style', 'get_roundoff_value_style',
    # Link and action styles
    'get_add_party_link_style',
    # Menu and popup styles
    'get_context_menu_style', 'get_party_suggestion_menu_style',
    # Item widget styles
    'get_item_widget_hover_style', 'get_item_widget_normal_style',
    # Validation/highlight styles
    'get_error_highlight_style', 'get_success_highlight_style',
    # Print dialog styles
    'get_print_button_style', 'get_secondary_button_style',
    # Transparent container styles
    'get_transparent_container_style', 'get_transparent_frame_style',
    # Header section styles
    'get_header_column_style', 'get_items_header_style', 'get_items_header_label_style',
    # PDF preview styles
    'get_pdf_preview_dialog_style', 'get_pdf_page_container_style',
    'get_pdf_page_label_style', 'get_pdf_toolbar_style',
    'get_pdf_toolbar_button_style', 'get_pdf_page_info_style',
    # Items section improvements
    'get_item_row_even_style', 'get_item_row_odd_style', 'get_item_row_error_style',
    'get_empty_state_style', 'get_quick_chip_recent_style', 'get_stock_indicator_style',
    'get_action_icon_button_style',
    # Invoice totals section styles (NEW)
    'get_totals_row_label_style', 'get_totals_row_value_style',
    'get_subtotal_value_style', 'get_discount_value_style', 'get_tax_value_style',
    'get_tax_breakdown_style', 'get_other_charges_input_style',
    'get_grand_total_row_style', 'get_grand_total_label_enhanced_style',
    'get_grand_total_value_enhanced_style', 'get_paid_amount_input_style',
    'get_balance_due_style_dynamic', 'get_roundoff_row_style',
    'get_invoice_discount_input_style', 'get_totals_separator_style',
    'get_previous_balance_style'
]
