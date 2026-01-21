"""
Sales Invoice Form Dialog
UI for creating/editing sales invoices.

Architecture: UI → Controller → Service → DB
This file contains ONLY UI code - layouts, widgets, signal-slot connections.
All business logic is delegated to InvoiceFormController.
"""

import os
import tempfile
import webbrowser
from typing import Optional, Dict, List, Any

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QListWidget, QFileDialog, QCompleter,
    QStyledItemDelegate, QStyle, QApplication, QPlainTextEdit
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QRect, QSize, QStringListModel
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QKeySequence, QAction, QShortcut, QPainter, QTextDocument, QAbstractTextDocumentLayout, QKeyEvent

from widgets import (
    CustomButton, CustomTable, CustomInput, FormField, PartySelector, ProductSelector,
    InvoiceItemWidget, highlight_error, highlight_success, show_validation_error,
    DialogEditableComboBox
)
from .sales_invoice_dialog_constants import (
    # Window dimensions
    DIALOG_WIDTH_DEFAULT, DIALOG_HEIGHT_DEFAULT,
    # Layout spacings and margins
    MAIN_LAYOUT_SPACING, MAIN_LAYOUT_MARGINS,
    BUTTON_CONTAINER_MIN_HEIGHT, BUTTON_LAYOUT_SPACING, BUTTON_LAYOUT_MARGINS,
    ACTION_LAYOUT_SPACING, ACTION_LAYOUT_MARGINS,
    # Header
    HEADER_MIN_HEIGHT, HEADER_MAX_HEIGHT, HEADER_COMPACT_MIN_HEIGHT, HEADER_COMPACT_MAX_HEIGHT,
    HEADER_LAYOUT_SPACING, HEADER_LAYOUT_MARGINS,
    ROW1_SPACING, ROW1_MARGINS, ROW2_SPACING,
    # Bill type
    BILLTYPE_BTN_HEIGHT, BILLTYPE_BTN_WIDTH, BILLTYPE_BOX_LAYOUT_SPACING,
    # Tax type
    TAX_SEGMENT_HEIGHT, TAX_SEGMENT_BTN_HEIGHT, TAX_TYPE_BOX_WIDTH,
    TAX_BOX_LAYOUT_SPACING, SEGMENT_LAYOUT_MARGINS, SEGMENT_LAYOUT_SPACING,
    # Party
    PARTY_INFO_MIN_WIDTH, PARTY_INFO_MAX_WIDTH,
    PARTY_SEARCH_HEIGHT, PARTY_SEARCH_MIN_WIDTH, PARTY_COMPLETER_MAX_VISIBLE_ITEMS,
    PARTY_COMPLETER_POPUP_MIN_WIDTH, PARTY_COMPLETER_POPUP_MAX_HEIGHT, PARTY_COMPLETER_POPUP_GAP_FROM_INPUT,
    # Invoice fields
    INVOICE_DATE_BOX_HEIGHT, INVOICE_DATE_BOX_WIDTH, INVOICE_DATE_BOX_LAYOUT_SPACING,
    INVOICE_NUMBER_BOX_HEIGHT, INVOICE_NUMBER_BOX_WIDTH, INVOICE_NUMBER_BOX_LAYOUT_SPACING,
    # Items section
    ITEMS_LAYOUT_SPACING, ITEMS_LAYOUT_MARGINS,
    QUICK_PRODUCTS_LAYOUT_SPACING, QUICK_PRODUCTS_LAYOUT_MARGINS, QUICK_PRODUCTS_LABEL_SIZE,
    QUICK_PRODUCTS_SHOW_COUNT, QUICK_PRODUCTS_RECENT_COUNT, QUICK_PRODUCTS_POPULAR_COUNT,
    QUICK_PRODUCT_CHIP_HEIGHT, QUICK_PRODUCT_CHIP_MIN_WIDTH,
    HEADERS_LAYOUT_SPACING, HEADERS_LAYOUT_MARGINS, HEADER_LABEL_HEIGHT,
    HEADER_COLUMN_NO_WIDTH, HEADER_COLUMN_PRODUCT_WIDTH, HEADER_COLUMN_HSN_WIDTH,
    HEADER_COLUMN_QTY_WIDTH, HEADER_COLUMN_UNIT_WIDTH, HEADER_COLUMN_RATE_WIDTH,
    HEADER_COLUMN_DISC_WIDTH, HEADER_COLUMN_TAX_WIDTH, HEADER_COLUMN_AMOUNT_WIDTH, HEADER_COLUMN_ACTION_WIDTH,
    EMPTY_STATE_MIN_HEIGHT, ITEMS_CONTAINER_SPACING, ITEMS_CONTAINER_MARGINS,
    # Totals section
    TOTALS_SECTION_MIN_HEIGHT, TOTALS_LAYOUT_MARGINS, TOTALS_LAYOUT_SPACING,
    LEFT_CONTAINER_SPACING, NOTES_FIELD_HEIGHT,
    AMOUNT_WORDS_CONTAINER_SPACING, AMOUNT_WORDS_LABEL_MIN_WIDTH, AMOUNT_WORDS_LABEL_MIN_HEIGHT,
    TOTALS_GRID_SPACING, TOTALS_GRID_MARGINS, TOTALS_ROW_HEIGHT, TOTALS_LABEL_WIDTH,
    # Previews
    HTML_PREVIEW_DIALOG_WIDTH, HTML_PREVIEW_DIALOG_HEIGHT, HTML_PREVIEW_DIALOG_MIN_WIDTH, HTML_PREVIEW_DIALOG_MIN_HEIGHT,
    HTML_PREVIEW_HEADER_HEIGHT, HTML_PREVIEW_LAYOUT_MARGINS, HTML_PREVIEW_LAYOUT_SPACING, HTML_PREVIEW_HEADER_MARGINS,
    PDF_PREVIEW_DIALOG_WIDTH, PDF_PREVIEW_DIALOG_HEIGHT, PDF_PREVIEW_HEADER_HEIGHT,
    PDF_PREVIEW_LAYOUT_MARGINS, PDF_PREVIEW_LAYOUT_SPACING, PDF_PREVIEW_HEADER_MARGINS,
    # Timing
    PARTY_TEXT_VALIDATION_DEBOUNCE_MS, COMPLETER_POPUP_POSITIONING_DELAY_MS,
    # Limits
    QUICK_ADD_DIALOG_WIDTH, QUICK_ADD_DIALOG_HEIGHT, MIN_PARTY_NAME_LENGTH,
)
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_DARK, TEXT_MUTED,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, PRIMARY_LIGHT, PRIMARY_DARK,
    DANGER_LIGHT, SUCCESS_LIGHT,
    get_calendar_stylesheet, get_dialog_input_style, get_error_input_style,
    # Invoice form specific styles
    get_row_number_style, get_product_input_style, get_hsn_readonly_style,
    get_unit_label_style, get_readonly_spinbox_style, get_amount_display_style,
    get_circle_button_style, get_invoice_dialog_style, get_dialog_header_style,
    get_preview_header_style, get_preview_close_button_style,
    get_html_viewer_style, get_pdf_viewer_style,
    # Form field styles
    get_form_label_style, get_form_combo_style, get_date_edit_style,
    get_invoice_number_input_style, get_party_search_input_style,
    get_section_frame_style, get_section_header_style,
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
    # New styles for items section improvements
    get_empty_state_style, get_item_row_even_style, get_item_row_odd_style,
    get_item_row_error_style, get_quick_chip_recent_style, get_stock_indicator_style,
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
from controllers.invoice_controller import invoice_form_controller


class HighlightDelegate(QStyledItemDelegate):
    """
    Custom delegate that highlights matching text in the party dropdown.
    Shows matched characters in bold with different background color.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.highlight_color = "#FEF3C7"  # Warm yellow highlight
        self.highlight_text_color = "#92400E"  # Dark amber text
        
    def set_search_text(self, text: str):
        """Set the text to highlight in dropdown items."""
        self.search_text = text.strip().upper() if text else ""
    
    def paint(self, painter, option, index):
        """Paint the item with highlighted matching text."""
        painter.save()
        
        # Get the text to display
        text = index.data(Qt.DisplayRole) or ""
        
        # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(PRIMARY))
            text_color = QColor(WHITE)
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor(PRIMARY_LIGHT))
            text_color = QColor(TEXT_PRIMARY)
        else:
            painter.fillRect(option.rect, QColor(WHITE))
            text_color = QColor(TEXT_PRIMARY)
        
        # Draw text with highlighting
        if self.search_text and self.search_text in text.upper():
            # Create HTML with highlighted text
            html_text = self._create_highlighted_html(text, text_color, option.state & QStyle.State_Selected)
            
            doc = QTextDocument()
            doc.setHtml(html_text)
            doc.setDefaultFont(option.font)
            doc.setTextWidth(option.rect.width() - 24)  # Account for padding
            
            painter.translate(option.rect.left() + 12, option.rect.top() + 8)
            doc.drawContents(painter)
        else:
            # Draw plain text
            painter.setPen(text_color)
            painter.setFont(option.font)
            text_rect = option.rect.adjusted(12, 8, -12, -8)
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)
        
        painter.restore()
    
    def _create_highlighted_html(self, text: str, text_color: QColor, is_selected: bool) -> str:
        """Create HTML string with matching text highlighted."""
        if not self.search_text:
            return f'<span style="color: {text_color.name()};">{text}</span>'
        
        # Find all occurrences (case-insensitive)
        text_upper = text.upper()
        search_upper = self.search_text
        
        result = []
        last_end = 0
        pos = 0
        
        while True:
            idx = text_upper.find(search_upper, pos)
            if idx == -1:
                break
            
            # Add text before match
            if idx > last_end:
                result.append(f'<span style="color: {text_color.name()};">{text[last_end:idx]}</span>')
            
            # Add highlighted match
            if is_selected:
                # For selected items, use white text with underline
                result.append(f'<span style="color: white; font-weight: bold; text-decoration: underline;">{text[idx:idx+len(search_upper)]}</span>')
            else:
                # For non-selected, use amber highlight
                result.append(f'<span style="background-color: {self.highlight_color}; color: {self.highlight_text_color}; font-weight: bold; padding: 1px 2px; border-radius: 2px;">{text[idx:idx+len(search_upper)]}</span>')
            
            last_end = idx + len(search_upper)
            pos = last_end
        
        # Add remaining text
        if last_end < len(text):
            result.append(f'<span style="color: {text_color.name()};">{text[last_end:]}</span>')
        
        return ''.join(result)
    
    def sizeHint(self, option, index):
        """Return larger size for touch-friendly items."""
        return QSize(option.rect.width(), 48)  # 48px height for touch support


class InvoiceDialog(QDialog):
    """
    Enhanced dialog for creating/editing sales invoices with modern UI.
    
    This dialog handles:
    - Creating new sales invoices
    - Editing existing invoices
    - Read-only viewing of invoices
    - Invoice preview and printing
    
    Architecture: UI → Controller → Service → DB
    All business logic is delegated to invoice_form_controller.
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        invoice_data: Optional[Dict[str, Any]] = None,
        invoice_number: Optional[str] = None,
        read_only: bool = False
    ) -> None:
        """
        Initialize the invoice dialog.
        
        Args:
            parent: Parent widget
            invoice_data: Existing invoice data for editing
            invoice_number: Invoice number to load
            read_only: Whether the dialog is in read-only mode
        """
        super().__init__(parent)
        self.invoice_data: Optional[Dict[str, Any]] = invoice_data
        self.products: List[Dict[str, Any]] = []
        self.parties: List[Dict[str, Any]] = []
        self.read_only: bool = read_only

        # Load existing invoice if invoice_number is provided
        if invoice_number and not invoice_data:
            self.load_existing_invoice(invoice_number)

        # Initialize window properties
        self.init_window()

        # Load required data
        self.load_data()

        # Setup the complete UI
        self.setup_ui()

        # Populate data if editing
        if self.invoice_data:
            self.populate_invoice_data()

        # Apply read-only mode if enabled
        if self.read_only:
            QTimer.singleShot(200, self.apply_read_only_mode)

        # Force maximize after everything is set up
        QTimer.singleShot(100, self.ensure_maximized)
        
        # Set initial focus on party search box for new invoices
        if not self.invoice_data and not self.read_only:
            QTimer.singleShot(200, self.set_initial_focus)

    def load_existing_invoice(self, invoice_number: str) -> None:
        """
        Load existing invoice data by invoice number via controller.
        
        Args:
            invoice_number: The invoice number to load
        """
        try:
            invoice_data = invoice_form_controller.get_invoice_by_number(invoice_number)
            if invoice_data:
                self.invoice_data = invoice_data
            else:
                QMessageBox.warning(self, "Error", f"Invoice '{invoice_number}' not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoice: {str(e)}")

    def populate_invoice_data(self) -> None:
        """Populate form fields with existing invoice data"""
        if not self.invoice_data:
            return
        
        try:
            invoice = self.invoice_data['invoice']
            party = self.invoice_data['party']
            items = self.invoice_data.get('items', [])
            
            # Set invoice number
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setText(invoice['invoice_no'])
            
            # Set dates
            if hasattr(self, 'invoice_date'):
                from PySide6.QtCore import QDate
                date_obj = QDate.fromString(invoice['date'], 'yyyy-MM-dd')
                self.invoice_date.setDate(date_obj)
            
            # Set party
            if hasattr(self, 'party_search') and party:
                party_name = party['name'].strip() if party.get('name') else ''
                if party_name:
                    # Set the lineEdit text directly (don't use setCurrentText since items aren't in combobox)
                    self.party_search.lineEdit().blockSignals(True)
                    self.party_search.lineEdit().setText(party_name)
                    self.party_search.lineEdit().blockSignals(False)
                    
                    # Ensure party_search lineEdit is visible by clearing placeholder
                    self.party_search.lineEdit().setPlaceholderText("")
                    
                    # Show party info card using the party data directly from invoice
                    self._show_party_info(party)
            
            # Set bill type if available
            if invoice.get('bill_type'):
                self._bill_type = invoice['bill_type'].upper()
                if hasattr(self, 'billtype_btn'):
                    self._update_billtype_style()
            
            # Set invoice type (GST/Non-GST) if available - using segmented buttons
            if invoice.get('tax_type'):
                # Convert stored format to internal state
                stored_type = invoice['tax_type']
                if 'Same State' in stored_type:
                    self._tax_type = 'SAME_STATE'
                elif 'Other State' in stored_type:
                    self._tax_type = 'OTHER_STATE'
                elif 'Non-GST' in stored_type:
                    self._tax_type = 'NON_GST'
                
                # Update button styles
                if hasattr(self, '_tax_buttons'):
                    self._apply_tax_type_styles()
            
            # Populate items
            if items:
                # Clear ALL existing item widgets (not just count-1)
                widgets_to_remove = []
                for i in range(self.items_layout.count()):
                    item_widget = self.items_layout.itemAt(i).widget()
                    if isinstance(item_widget, InvoiceItemWidget):
                        widgets_to_remove.append(item_widget)
                
                for widget in widgets_to_remove:
                    self.items_layout.removeWidget(widget)
                    widget.deleteLater()
                
                # Add items from database (skip empty items)
                for item_data in items:
                    # Skip empty items (no product selected)
                    if not item_data.get('product_name', '').strip():
                        continue
                    
                    item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                    
                    # Set product name
                    item_widget.product_input.setCurrentText(item_data['product_name'])
                    
                    # Set HSN code
                    item_widget.hsn_edit.setText(item_data.get('hsn_code', ''))
                    
                    # Set values
                    item_widget.quantity_spin.setValue(item_data['quantity'])
                    item_widget.rate_spin.setValue(item_data['rate'])
                    item_widget.discount_spin.setValue(item_data['discount_percent'])
                    item_widget.tax_spin.setValue(item_data['tax_percent'])
                    
                    # Set unit
                    item_widget.unit_label.setText(item_data.get('unit', 'Piece'))
                    
                    # Connect signals (only if not in read-only mode)
                    if not self.read_only:
                        item_widget.add_requested.connect(self.add_item)
                        item_widget.remove_btn.clicked.connect(lambda checked, w=item_widget: self.remove_item(w))
                        item_widget.remove_requested.connect(self._handle_remove_request)  # Ctrl+Delete support
                    item_widget.item_changed.connect(self.update_totals)
                    
                    # Add to layout (before the stretch)
                    self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
                
                # Update row numbers and totals
                self.number_items()
                self.update_totals()
                
                # Add one empty row for adding more items (only in edit mode, not read-only)
                if not self.read_only:
                    self.add_item()
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error populating invoice data: {str(e)}")

    def apply_read_only_mode(self) -> None:
        """Apply read-only mode to the entire dialog - disable all editing."""
        try:
            # Update window title to indicate view mode
            invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else 'Invoice'
            self.setWindowTitle(f"📄 View Invoice - {invoice_no} (Read Only)")
            
            # Disable header inputs
            if hasattr(self, 'billtype_btn'):
                self.billtype_btn.setEnabled(False)
            if hasattr(self, 'party_search'):
                # Make lineEdit read-only instead of disabling the entire combobox
                # This ensures text is visible even in read-only mode
                self.party_search.lineEdit().setReadOnly(True)
                self.party_search.setEnabled(False)  # Still disable dropdown button
            # Disable tax type segmented buttons
            if hasattr(self, '_tax_buttons'):
                for btn in self._tax_buttons.values():
                    btn.setEnabled(False)
            if hasattr(self, 'invoice_date'):
                self.invoice_date.setEnabled(False)
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setReadOnly(True)
            
            # Disable all item widgets - keep buttons visible but disabled to maintain layout
            if hasattr(self, 'items_layout'):
                for i in range(self.items_layout.count()):
                    item_widget = self.items_layout.itemAt(i).widget()
                    if item_widget and hasattr(item_widget, 'product_input'):
                        # Disable all inputs in item widget
                        if hasattr(item_widget, 'product_input'):
                            item_widget.product_input.setEnabled(False)  # QComboBox - use setEnabled
                        if hasattr(item_widget, 'hsn_edit'):
                            item_widget.hsn_edit.setReadOnly(True)
                        if hasattr(item_widget, 'quantity_spin'):
                            item_widget.quantity_spin.setEnabled(False)
                        if hasattr(item_widget, 'rate_spin'):
                            item_widget.rate_spin.setEnabled(False)
                        if hasattr(item_widget, 'discount_spin'):
                            item_widget.discount_spin.setEnabled(False)
                        if hasattr(item_widget, 'tax_spin'):
                            item_widget.tax_spin.setEnabled(False)
                        # Keep buttons visible but make them invisible (maintain space)
                        if hasattr(item_widget, 'remove_btn'):
                            item_widget.remove_btn.setEnabled(False)
                            item_widget.remove_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
                        if hasattr(item_widget, 'add_btn'):
                            item_widget.add_btn.setEnabled(False)
                            item_widget.add_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
            
            # Disable action buttons (Save, Save & Print) but keep Close
            if hasattr(self, 'save_button'):
                self.save_button.setEnabled(False)
                self.save_button.hide()
            if hasattr(self, 'save_print_button'):
                self.save_print_button.setEnabled(False)
                self.save_print_button.hide()
            
            # Add a "Print Preview" button for viewing
            if hasattr(self, 'preview_button'):
                self.preview_button.setEnabled(True)
            
            # Disable notes/terms if they exist
            if hasattr(self, 'notes_edit'):
                self.notes_edit.setReadOnly(True)
            if hasattr(self, 'terms_edit'):
                self.terms_edit.setReadOnly(True)
            
            print(f"✅ Read-only mode applied for invoice: {invoice_no}")
            
        except Exception as e:
            print(f"Error applying read-only mode: {e}")

    def ensure_maximized(self) -> None:
        """Ensure the window is properly maximized."""
        from PySide6.QtGui import QGuiApplication
        # Use availableGeometry to account for menu bar and dock
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setWindowState(Qt.WindowMaximized)
        self.showMaximized()

    def set_initial_focus(self) -> None:
        """Set initial focus on the party search box for new invoices."""
        try:
            if hasattr(self, 'party_search'):
                self.party_search.setFocus()
                # For combo box, select all text in the line edit
                if hasattr(self.party_search, 'lineEdit') and self.party_search.lineEdit():
                    self.party_search.lineEdit().selectAll()
        except Exception as e:
            print(f"Error setting initial focus: {e}")

    def setup_autosave(self) -> None:
        """Setup auto-save timer to save draft every 30 seconds."""
        try:
            self._autosave_timer = QTimer(self)
            self._autosave_timer.timeout.connect(self.autosave_draft)
            self._autosave_timer.start(30000)  # 30 seconds
            print("Auto-save enabled: Draft will be saved every 30 seconds")
        except Exception as e:
            print(f"Failed to setup auto-save: {e}")

    def closeEvent(self, event) -> None:
        """Handle dialog close - cleanup."""
        try:
            # Cleanup any orphan webviews
            if hasattr(self, '_pdf_webview') and self._pdf_webview:
                self._pdf_webview.close()
                self._pdf_webview.deleteLater()
                self._pdf_webview = None
            
            # Hide all orphan floating widgets (GST labels that aren't in layout)
            for widget_name in ['cgst_label', 'sgst_label', 'igst_label', 'tax_breakdown_box']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget:
                        widget.setVisible(False)
            
            # Close any open child dialogs (preview, print, etc.)
            for child in self.children():
                if isinstance(child, QDialog) and child.isVisible():
                    child.close()
        except Exception:
            pass
        super().closeEvent(event)

    def reject(self) -> None:
        """Handle dialog rejection (Cancel button or Escape key) - cleanup orphan widgets."""
        try:
            # Hide all orphan floating widgets to prevent them from appearing
            for widget_name in ['cgst_label', 'sgst_label', 'igst_label', 'tax_breakdown_box']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget:
                        widget.setVisible(False)
        except Exception:
            pass
        super().reject()

    def init_window(self) -> None:
        """Initialize window properties and styling."""
        title = "📄 Create Invoice" if not self.invoice_data else "📝 Edit Invoice"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        from PySide6.QtGui import QGuiApplication
        # Use availableGeometry to account for menu bar and dock
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1200, 900)
        self.setStyleSheet(get_invoice_dialog_style())

    def load_data(self) -> None:
        """Load products and parties data via controller."""
        try:
            self.products = invoice_form_controller.get_products()
            self.parties = invoice_form_controller.get_parties()
        except Exception as e:
            print(f"[InvoiceDialog] Error loading data: {e}")
            self.products = []
            self.parties = []

    def setup_ui(self) -> None:
        """Setup enhanced dialog UI with modern design and better organization."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(MAIN_LAYOUT_SPACING)
        self.main_layout.setContentsMargins(*MAIN_LAYOUT_MARGINS)
        
        # Setup content sections directly without scroll area
        self.setup_content_sections(self.main_layout)
        
        # Add action buttons at the bottom (fixed)
        self.setup_action_buttons()
        
        # Setup Tab navigation order for better UX flow
        self.setup_tab_order()
        
        self.apply_final_styling()

    def setup_content_sections(self, layout) -> None:
        """Setup the main content sections with enhanced layout (scrollable)."""
        # Create header section
        self.header_frame = self.create_header_section()
        layout.addWidget(self.header_frame, 0)  # No stretch
        
        # Create items section
        self.items_frame = self.create_items_section()
        layout.addWidget(self.items_frame, 1)  # Stretch factor 1 - expand to fill space
        
        # Create totals section
        self.totals_frame = self.create_totals_section()
        layout.addWidget(self.totals_frame, 0)  # No stretch
        
        # Only add empty item row for new invoices (not in read-only mode or editing existing)
        if not self.read_only and not self.invoice_data:
            self.add_item()

    def _apply_button_styling(self, button: CustomButton, height: int = 42, min_width: int = 110) -> None:
        """Apply consistent button styling (Improvement #1: Reduce duplication)."""
        button.setFixedHeight(height)
        button.setMinimumWidth(min_width)

    def setup_action_buttons(self) -> None:
        """Setup enhanced action buttons with improved styling and alignment.
        
        Improvements implemented:
        1. Helper method to reduce style duplication
        2. Read-only mode button visibility control
        3. State management based on dialog mode
        4. Consistent button widths via data-driven approach
        5. Visual keyboard shortcut indicators in tooltips
        6. Form validation state management
        7. Context-aware help button
        8. Loading/processing state feedback
        9. Reset confirmation dialog
        10. Button focus order for keyboard navigation
        """
        button_container = QFrame()
        button_container.setObjectName("buttonContainer")
        button_container.setStyleSheet(f"""
            QFrame#buttonContainer {{
                background: {WHITE};
                border-top: 2px solid {BORDER};
                border-radius: 0px;
                padding: 15px 20px;
            }}
        """)
        button_container.setMinimumHeight(BUTTON_CONTAINER_MIN_HEIGHT)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(BUTTON_LAYOUT_SPACING)
        button_layout.setContentsMargins(*BUTTON_LAYOUT_MARGINS)
        
        # Improvement #4: Data-driven button widths (Consistent sizing)
        button_widths = {
            'help': 100,
            'cancel': 110,
            'reset': 110,
            'save': 110,
            'save_print': 140
        }
        height=35
        
        # Help button (left side)
        self.help_button = CustomButton("❓ Help", "secondary", heigth=25)
        # self._apply_button_styling(self.help_button, height=35, min_width=button_widths['help'])
        # Improvement #5: Enhanced tooltip with keyboard shortcut (visual indicator)
        self.help_button.setToolTip("Get help with invoice creation\n⌨️ Shortcut: F1")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)
        
        # Separator stretch
        button_layout.addStretch()

        # Action buttons (right side) - aligned consistently
        action_layout = QHBoxLayout()
        action_layout.setSpacing(ACTION_LAYOUT_SPACING)
        action_layout.setContentsMargins(*ACTION_LAYOUT_MARGINS)

        # Cancel button - Improvement #3: State management
        self.cancel_button = CustomButton("✕ Cancel", "danger")
        self._apply_button_styling(self.cancel_button, height=42, min_width=button_widths['cancel'])
        # Improvement #5: Enhanced tooltip
        cancel_tooltip = "Close without saving\n⌨️ Shortcut: Esc"
        if self.read_only:
            cancel_tooltip = "Close invoice view\n⌨️ Shortcut: Esc"
        self.cancel_button.setToolTip(cancel_tooltip)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        action_layout.addWidget(self.cancel_button)
        
        # Reset button - Improvement #9: Add confirmation for destructive action
        # Color-coded as "warning" (orange) to indicate destructive action
        self.reset_button = CustomButton("↻ Reset", "warning")
        self._apply_button_styling(self.reset_button, height=42, min_width=button_widths['reset'])
        self.reset_button.setToolTip("Clear all fields and start over\n⌨️ Shortcut: Ctrl+R")
        self.reset_button.clicked.connect(self.reset_form)
        # Improvement #2: Hide in read-only mode
        if self.read_only:
            self.reset_button.hide()
        action_layout.addWidget(self.reset_button)
        
        # Save button - Improvement #6: Form validation state management
        self.save_button = CustomButton("💾 Save", "primary")
        self._apply_button_styling(self.save_button, height=42, min_width=button_widths['save'])
        self.save_button.setToolTip("Save invoice as draft\n⌨️ Shortcut: Ctrl+S")
        self.save_button.clicked.connect(self.on_save_clicked)
        # Improvement #2: Hide in read-only mode
        if self.read_only:
            self.save_button.hide()
        action_layout.addWidget(self.save_button)
        
        # Save Print button - Improvement #3: Dynamic text based on mode
        save_text = "🖨️ Update & Print" if self.invoice_data else "💾 Save & Print"
        self.save_print_button = CustomButton(save_text, "success")
        self._apply_button_styling(self.save_print_button, height=42, min_width=button_widths['save_print'])
        save_print_tooltip = ("Save and print invoice\n⌨️ Shortcut: Ctrl+P" 
                             if not self.invoice_data 
                             else "Update and print invoice\n⌨️ Shortcut: Ctrl+P")
        self.save_print_button.setToolTip(save_print_tooltip)
        self.save_print_button.clicked.connect(self.save_and_print)
        # Improvement #2: Hide in read-only mode
        if self.read_only:
            self.save_print_button.hide()
        action_layout.addWidget(self.save_print_button)
        
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container, 0)  # Stretch factor 0 - don't expand
        
        # Improvement #10: Setup button focus order for keyboard navigation
        self.setup_button_focus_order()
    
    def setup_button_focus_order(self) -> None:
        """Setup Tab navigation order for action buttons (Improvement #10)."""
        try:
            # Tab order: Cancel → Reset → Save → Save & Print → Help
            if hasattr(self, 'cancel_button') and hasattr(self, 'reset_button'):
                self.setTabOrder(self.cancel_button, self.reset_button)
            if hasattr(self, 'reset_button') and hasattr(self, 'save_button'):
                self.setTabOrder(self.reset_button, self.save_button)
            if hasattr(self, 'save_button') and hasattr(self, 'save_print_button'):
                self.setTabOrder(self.save_button, self.save_print_button)
            if hasattr(self, 'save_print_button') and hasattr(self, 'help_button'):
                self.setTabOrder(self.save_print_button, self.help_button)
        except Exception as e:
            print(f"Error setting button focus order: {e}")
    
    def on_cancel_clicked(self) -> None:
        """Handle Cancel button click with proper label context (Improvement #3)."""
        self.reject()
    
    def on_save_clicked(self) -> None:
        """Handle Save button with loading state (Improvement #8)."""
        # Improvement #8: Show loading state
        self.save_button.setEnabled(False)
        original_text = self.save_button.text()
        self.save_button.setText("⏳ Saving...")
        
        try:
            self.save_invoice()
        finally:
            # Restore button state
            self.save_button.setEnabled(True)
            self.save_button.setText(original_text)

    def apply_final_styling(self) -> None:
        """Apply final styling and setup additional features."""
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Set dynamic window size (70% of screen)
        screen = self.screen()
        if screen:
            screen_rect = screen.geometry()
            width = int(screen_rect.width() * 0.75)  # 75% of screen width
            height = int(screen_rect.height() * 0.80)  # 80% of screen height
            self.resize(width, height)
        else:
            # Fallback size if screen not available
            self.resize(DIALOG_WIDTH_DEFAULT, DIALOG_HEIGHT_DEFAULT)
        
        # Center window on screen
        self.move(
            (screen_rect.width() - self.width()) // 2,
            (screen_rect.height() - self.height()) // 2
        )
        
        self.setup_keyboard_shortcuts()
        self.setup_validation()

    def setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for common actions."""
        # Save shortcuts
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_invoice)
        
        # Add new item shortcuts
        new_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_item_shortcut.activated.connect(self.add_item)
        new_item_shortcut2 = QShortcut(QKeySequence("Ctrl+Return"), self)
        new_item_shortcut2.activated.connect(self.add_item)
        
        # Quick navigation shortcuts
        party_shortcut = QShortcut(QKeySequence("Alt+P"), self)
        party_shortcut.activated.connect(lambda: self.party_search.setFocus() if hasattr(self, 'party_search') else None)
        
        date_shortcut = QShortcut(QKeySequence("Alt+D"), self)
        date_shortcut.activated.connect(lambda: self.invoice_date.setFocus() if hasattr(self, 'invoice_date') else None)
        
        # Print shortcut
        print_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        print_shortcut.activated.connect(self.save_and_print)
        
        # Reset shortcut
        reset_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reset_shortcut.activated.connect(self.reset_form)
        
        # Help and cancel
        help_shortcut = QShortcut(QKeySequence.HelpContents, self)
        help_shortcut.activated.connect(self.show_help)
        cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        cancel_shortcut.activated.connect(self.reject)

    def setup_validation(self) -> None:
        """Setup initial form validation state."""
        # Set initial balance due visibility based on default bill type
        if hasattr(self, '_bill_type'):
            self.on_bill_type_changed(self._bill_type)

    def setup_tab_order(self) -> None:
        """Setup Tab navigation order: Bill Type → Tax Type → Date → Party → Items.
        
        Creates a clear visual flow for users to navigate through invoice form.
        Tab order: Bill Type → Tax Type → Date → Invoice Number → Party Search → First Item
        """
        try:
            if not hasattr(self, 'billtype_btn'):
                return
            
            # Build Tab order list starting with header fields
            tab_order = []
            
            # 1. Bill Type button (first in order)
            tab_order.append(self.billtype_btn)
            
            # 2. Tax Type buttons (if they exist)
            if hasattr(self, 'tax_btn_same'):
                tab_order.append(self.tax_btn_same)
            if hasattr(self, 'tax_btn_other'):
                tab_order.append(self.tax_btn_other)
            if hasattr(self, 'tax_btn_nongst'):
                tab_order.append(self.tax_btn_nongst)
            
            # 3. Invoice Date
            if hasattr(self, 'invoice_date'):
                tab_order.append(self.invoice_date)
            
            # 4. Invoice Number
            if hasattr(self, 'invoice_number'):
                tab_order.append(self.invoice_number)
            
            # 5. Party Search (main selection field)
            if hasattr(self, 'party_search'):
                tab_order.append(self.party_search)
            
            # 6. First item product field (if items exist)
            if hasattr(self, 'items_layout'):
                for i in range(self.items_layout.count() - 1):
                    w = self.items_layout.itemAt(i).widget()
                    if isinstance(w, InvoiceItemWidget):
                        if hasattr(w, 'product_input'):
                            tab_order.append(w.product_input)
                            break  # Just add first item's product field
            
            # Set Tab order for the widgets
            for i in range(len(tab_order) - 1):
                self.setTabOrder(tab_order[i], tab_order[i + 1])
            
            # Add helpful Tab order guide in status or tooltips
            if hasattr(self, 'billtype_btn'):
                self.billtype_btn.setToolTip(
                    self.billtype_btn.toolTip() + 
                    "<br><br><b style='color: #3B82F6;'>📍 Tab Navigation:</b>" +
                    "<br><span style='color: #6B7280;'>1️⃣ Bill Type (current)</span>" +
                    "<br><span style='color: #6B7280;'>2️⃣ Tax Type → 3️⃣ Date → 4️⃣ Invoice No</span>" +
                    "<br><span style='color: #6B7280;'>5️⃣ Party Selection → 6️⃣ Items</span>"
                )
        except Exception as e:
            print(f"Setup Tab order error: {e}")

    def show_help(self) -> None:
        """Show help dialog with instructions and keyboard shortcuts."""
        help_text = """
        <h3>📋 Invoice Creation Help</h3>
        
        <h4>📝 Steps:</h4>
        <p><b>1. Invoice Details:</b> Fill in invoice number, date, and due date</p>
        <p><b>2. Party Selection:</b> Choose the customer/client</p>
        <p><b>3. Add Items:</b> Click 'Add Item' to add products/services</p>
        <p><b>4. Calculations:</b> Totals are calculated automatically</p>
        <p><b>5. Save:</b> Click 'Save Invoice' to create the invoice</p>
        
        <h4>⌨️ Keyboard Shortcuts:</h4>
        <table style='margin-left: 10px;'>
            <tr><td><b>Ctrl+S</b></td><td>Save Invoice</td></tr>
            <tr><td><b>Ctrl+P</b></td><td>Save & Print</td></tr>
            <tr><td><b>Ctrl+N</b></td><td>Add New Item</td></tr>
            <tr><td><b>Ctrl+R</b></td><td>Reset Form</td></tr>
            <tr><td><b>Alt+P</b></td><td>Focus Party Search</td></tr>
            <tr><td><b>Alt+D</b></td><td>Focus Invoice Date</td></tr>
            <tr><td><b>Enter</b></td><td>Next field / Add row</td></tr>
            <tr><td><b>Esc</b></td><td>Cancel & Close</td></tr>
        </table>
        """
        QMessageBox.information(self, "Invoice Help", help_text)

    def preview_invoice(self):
        # Collect data from the form
        party_name = getattr(self, 'party_search').text().strip() if hasattr(self, 'party_search') else ''
        inv_date = self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else ''
        invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else ''
        bill_type = self._bill_type if hasattr(self, '_bill_type') else 'CASH'
        items = []
        for i in range(self.items_layout.count() - 1):
            w = self.items_layout.itemAt(i).widget()
            if isinstance(w, InvoiceItemWidget):
                d = w.get_item_data()
                if d:
                    items.append(d)
        subtotal = sum((it['quantity'] * it['rate']) for it in items) if items else 0
        total_discount = sum(it['discount_amount'] for it in items) if items else 0
        total_tax = sum(it['tax_amount'] for it in items) if items else 0
        grand_total = subtotal - total_discount + total_tax
        cgst = sum(it['tax_amount']/2 for it in items if it['tax_amount'] > 0) if items else 0
        sgst = cgst
        igst = 0  # For now, assuming intra-state
        # GST summary row (assuming all items same rate for demo)
        gst_rate = items[0]['tax_percent'] if items else 0
        gst_summary = f"""
            <tr>
                <td style='border:1px solid #bbb;padding:4px;'>GST%</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{gst_rate:.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{subtotal-total_discount:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{cgst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{sgst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{igst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{total_tax:,.2f}</td>
            </tr>
        """
        # Build item rows
        rows_html = "".join([
            f"<tr>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:center'>{i+1}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it['product_name']}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it.get('hsn_no','')}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['quantity']:.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it.get('unit','')}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['rate']:,.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['discount_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['tax_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['amount']:,.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['tax_amount']/2:,.2f}</td>"  # CGST
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['tax_amount']/2:,.2f}</td>"  # SGST
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹0.00</td>"  # IGST
            f"</tr>"
            for i, it in enumerate(items)
        ])
        # In Words
        def num2words(n):
            # Simple number to words for demo (Indian style)
            import math
            units = ["", "Thousand", "Lakh", "Crore"]
            s = ""
            if n == 0:
                return "Zero"
            if n < 0:
                return "Minus " + num2words(-n)
            i = 0
            while n > 0:
                rem = n % 1000 if i == 0 else n % 100
                if rem != 0:
                    s = f"{rem} {units[i]} " + s
                n = n // 1000 if i == 0 else n // 100
                i += 1
            return s.strip()
        in_words = num2words(int(round(grand_total))) + " Only"
        # HTML
        html = f"""
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
        body {{ font-family: Arial, sans-serif; color: #222; margin: 0; background: #fff; }}
        .invoice-box {{ max-width: 900px; margin: 20px auto; border: 1px solid #bbb; padding: 24px 32px 32px 32px; background: #fff; }}
        .header {{ text-align: center; border-bottom: 2px solid #222; padding-bottom: 8px; margin-bottom: 8px; }}
        .header h1 {{ font-size: 24px; margin: 0; letter-spacing: 2px; }}
        .header .subtitle {{ font-size: 13px; color: #444; margin-top: 2px; }}
        .meta-table, .meta-table td {{ font-size: 13px; }}
        .meta-table {{ width: 100%; margin-bottom: 8px; }}
        .meta-table td {{ padding: 2px 6px; }}
        .section-title {{ background: #e5e7eb; font-weight: bold; padding: 4px 8px; border: 1px solid #bbb; }}
        .items-table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin-bottom: 0; }}
        .items-table th, .items-table td {{ border: 1px solid #bbb; padding: 5px 4px; }}
        .items-table th {{ background: #f3f4f6; font-size: 13px; }}
        .totals-table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin-top: 0; }}
        .totals-table td {{ border: 1px solid #bbb; padding: 4px 6px; }}
        .totals-table .label {{ text-align: right; font-weight: bold; background: #f9fafb; }}
        .totals-table .value {{ text-align: right; font-weight: bold; background: #f9fafb; }}
        .gst-summary-table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin-top: 0; }}
        .gst-summary-table td {{ border: 1px solid #bbb; padding: 4px 6px; }}
        .footer-box {{ background: #e0f2fe; border: 1px solid #bbb; padding: 10px 16px; margin-top: 18px; font-size: 15px; font-weight: bold; text-align: right; }}
        .footer-details {{ font-size: 12px; color: #444; margin-top: 8px; }}
        </style>
        </head>
        <body>
        <div class='invoice-box'>
            <div class='header'>
                <div style='font-size:11px; text-align:right; float:right;'>TAX INVOICE</div>
                <h1>SUPER POWER BATTERIES (INDIA)</h1>
                <div class='subtitle'>A-1/2, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat<br>ph. (0265-2427631, 8815991781 | mail : )</div>
                <div class='subtitle' style='font-weight:bold;'>Terms : {bill_type}</div>
            </div>
            <table class='meta-table'>
                <tr>
                    <td><b>Buyer's Name and Address</b><br>{party_name or '—'}<br>GSTIN: —</td>
                    <td>
                        <table style='width:100%; font-size:13px;'>
                            <tr><td>Invoice No.:</td><td>{invoice_no}</td></tr>
                            <tr><td>Date:</td><td>{inv_date}</td></tr>
                            <tr><td>Ref No. & Dt.:</td><td> </td></tr>
                            <tr><td>Vehicle No.:</td><td> </td></tr>
                            <tr><td>Transport:</td><td> </td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            <div class='section-title'>Item Details</div>
            <table class='items-table'>
                <tr>
                    <th>No</th><th>Description</th><th>HSN Code</th><th>MRP</th><th>Qty</th><th>Unit</th><th>Rate</th><th>Discount</th><th>Tax%</th><th>CGST</th><th>SGST</th><th>IGST</th><th>Total</th>
                </tr>
                {rows_html if rows_html else "<tr><td colspan='13' style='text-align:center;color:#6b7280'>No items added</td></tr>"}
            </table>
            <table class='totals-table'>
                <tr><td class='label' colspan='12'>Total Amount Before Tax</td><td class='value'>₹{subtotal:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Discount</td><td class='value'>₹{total_discount:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Add: CGST/SGST</td><td class='value'>₹{cgst+sgst:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Add: IGST</td><td class='value'>₹{igst:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Tax Amount</td><td class='value'>₹{total_tax:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Invoice After Tax</td><td class='value'>₹{grand_total:,.2f}</td></tr>
            </table>
            <div class='section-title'>GST SUMMARY</div>
            <table class='gst-summary-table'>
                <tr style='background:#f3f4f6;'><td>GST%</td><td>Taxable Amt</td><td>CGST Amt</td><td>SGST Amt</td><td>IGST Amt</td><td>Tax Amt</td></tr>
                {gst_summary}
            </table>
            <div class='footer-box'>Net Amount<br><span style='font-size:22px;'>₹{grand_total:,.2f}</span></div>
            <div class='footer-details'>In Words : {in_words}<br>GSTIN : 24AADPF6173E1ZT<br>Bank Details :<br>BANK OF INDIA, A/C NO: 230327100001287<br>IFSC CODE: BKID0002303<br>Terms & Conditions: Subject to Vadodara - 390001 jurisdiction E.&O.E.<br><br><b>For SUPER POWER BATTERIES (INDIA)</b></div>
        </div>
        </body>
        </html>
        """
        # Show in a modal dialog with a QTextBrowser and simple actions
        dlg = QDialog(self)
        dlg.setWindowTitle("Invoice Preview")
        dlg.setModal(True)
        dlg.resize(900, 900)
        container = QVBoxLayout(dlg)
        view = QTextEdit()
        view.setReadOnly(True)
        view.setHtml(html)
        container.addWidget(view)
        actions = QHBoxLayout()
        actions.addStretch()
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(get_print_button_style())
        print_btn.clicked.connect(lambda: self.print_invoice(html))
        actions.addWidget(print_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_secondary_button_style())
        close_btn.clicked.connect(dlg.reject)
        actions.addWidget(close_btn)
        container.addLayout(actions)

        dlg.show()

    def print_invoice(self, html_content):
        """Print the invoice using the system's print dialog"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QTextDocument
            
            # Create a printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            
            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Invoice")
            
            if print_dialog.exec() == QPrintDialog.Accepted:
                # Create a QTextDocument and set the HTML content
                document = QTextDocument()
                document.setHtml(html_content)
                
                # Print the document
                document.print_(printer)
                
                QMessageBox.information(self, "Success", "Invoice sent to printer successfully!")
                
        except ImportError:
            # Fallback if print support is not available
            QMessageBox.warning(self, "Print Unavailable", 
                              "Print functionality requires PySide6 print support.\n"
                              "You can copy the invoice content and print manually.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", 
                               f"An error occurred while printing:\n{str(e)}")

    def save_and_print(self) -> None:
        """Save invoice and open print preview."""
        try:
            # Show confirmation dialog first
            reply = QMessageBox.question(
                self, 
                "Confirm Save & Print", 
                "Do you want to save this invoice and print it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return  # User cancelled
            
            # Step 1: Validate invoice data
            if not self.validate_invoice_for_final_save():
                return
            
            # Step 2: Save invoice as FINAL
            saved_invoice_id = self.save_final_invoice()
            if not saved_invoice_id:
                return
                
            # Step 3: Generate PDF and show print preview
            self.show_print_preview(saved_invoice_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Save & Print Error", 
                               f"An error occurred during save & print:\n{str(e)}")

    def validate_invoice_for_final_save(self) -> bool:
        """
        Validate that invoice has all required data for final save.
        
        Uses invoice_form_controller for centralized validation logic.
        
        Returns:
            True if validation passes, False otherwise.
        """
        try:
            # Get invoice number
            invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
            if not invoice_no:
                show_validation_error(
                    self,
                    self.invoice_number if hasattr(self, 'invoice_number') else None,
                    "Validation Error",
                    "Invoice number is required!"
                )
                return False
            
            # Get party selection
            party_text = getattr(self, 'party_search').text().strip() if hasattr(self, 'party_search') else ''
            party_data = getattr(self, 'party_data_map', {}).get(party_text)
            if not party_data or not party_text:
                show_validation_error(
                    self,
                    self.party_search if hasattr(self, 'party_search') else None,
                    "Validation Error",
                    "Please select a valid customer!"
                )
                return False
            
            # Collect items
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data and item_data.get('product_name', '').strip():
                        items.append(item_data)
            
            # Validate via controller (centralized validation logic)
            is_new = not self.invoice_data
            is_valid, error_msg, field_name = invoice_form_controller.validate_invoice_data(
                invoice_no, party_data.get('id'), items, is_new, skip_duplicate_check=True
            )
            
            if not is_valid:
                # Highlight the appropriate field
                field_widget = None
                if field_name == 'invoice_no' and hasattr(self, 'invoice_number'):
                    field_widget = self.invoice_number
                elif field_name == 'party' and hasattr(self, 'party_search'):
                    field_widget = self.party_search
                elif field_name == 'items' and hasattr(self, 'item_count_badge'):
                    field_widget = self.item_count_badge
                
                show_validation_error(self, field_widget, "Validation Error", error_msg)
                return False
            
            return True
            
        except Exception as e:
            print(f"Validation error: {e}")
            QMessageBox.critical(self, "Error", f"Validation failed: {str(e)}")
            return False

    def save_final_invoice(self) -> Optional[int]:
        """
        Save invoice with FINAL status via controller.
        
        Returns:
            The invoice ID if save was successful, None otherwise.
        """
        try:
            # Collect party data
            party_text = getattr(self, 'party_search').text().strip()
            party_data = getattr(self, 'party_data_map', {}).get(party_text)
            
            if not party_data or 'id' not in party_data:
                raise Exception(f"Invalid party selected: {party_text}")
            
            # Collect items
            items: List[Dict[str, Any]] = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            invoice_no = self.invoice_number.text().strip()
            invoice_date = self.invoice_date.date().toString('yyyy-MM-dd')
            invoice_type = self._get_tax_type()
            bill_type = self._bill_type if hasattr(self, '_bill_type') else 'CASH'
            # Round roundoff_amount to 2 decimal places to avoid floating point precision issues
            round_off = round(getattr(self, 'roundoff_amount', 0.0), 2)
            notes = self.notes.toPlainText().strip() if hasattr(self, 'notes') and self.notes else None
            
            # Ensure unique invoice number for new invoices
            if not self.invoice_data:
                invoice_no = invoice_form_controller.ensure_unique_invoice_number(invoice_no)
                if hasattr(self, 'invoice_number'):
                    self.invoice_number.setText(invoice_no)
            
            # Prepare data for controller
            invoice_data_dict: Dict[str, Any] = {
                'invoice_no': invoice_no,
                'date': invoice_date,
                'party_id': party_data['id'],
                'invoice_type': invoice_type,
                'bill_type': bill_type,
                'notes': notes,
                'round_off': round_off,
            }
            
            if self.invoice_data:
                invoice_data_dict['id'] = self.invoice_data.get('id') or self.invoice_data.get('invoice', {}).get('id')
            
            # Save via controller with FINAL status
            success, message, invoice_id = invoice_form_controller.save_invoice(
                invoice_data_dict,
                items,
                is_final=True
            )
            
            if success:
                return invoice_id
            else:
                QMessageBox.critical(self, "Save Error", message)
                return None
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save invoice: {str(e)}")
            return None

    def disable_editing_after_final_save(self, show_message: bool = True) -> None:
        """
        Disable all editing controls after invoice is saved as FINAL.
        
        Args:
            show_message: Whether to show a confirmation message to the user.
        """
        # Disable the Save & Print button itself
        if hasattr(self, 'save_print_button'):
            self.save_print_button.setEnabled(False)
            self.save_print_button.setText("✓ Saved & Final")
        
        # Disable regular save button
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(False)
            self.save_button.setText("✓ Finalized")
        
        # Show final status message only if requested
        if show_message:
            QMessageBox.information(self, "Invoice Finalized", 
                                  "Invoice has been saved as FINAL and cannot be edited further.")

    def show_print_preview(self, invoice_id: int) -> None:
        """
        Show HTML preview dialog for the invoice.
        
        Args:
            invoice_id: The ID of the invoice to preview.
        """
        from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
        show_invoice_preview(self, invoice_id)

    def generate_invoice_html(self, invoice_id: int) -> Optional[str]:
        """
        Generate HTML content for the invoice.
        
        Args:
            invoice_id: The ID of the invoice to generate HTML for.
            
        Returns:
            HTML string if successful, None otherwise.
        """
        try:
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            
            # Get invoice data
            invoice_data = generator.get_invoice_data(invoice_id)
            if not invoice_data:
                return None
            
            # Get invoice type and set appropriate template
            invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
            generator.template_path = generator.get_template_path(invoice_type)
            
            # Prepare template data based on invoice type
            if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
                template_data = generator.prepare_non_gst_template_data(invoice_data)
            else:
                template_data = generator.prepare_template_data(invoice_data)
            
            html_content = generator.render_html_template(template_data, invoice_type)
            
            return html_content
                
        except Exception as e:
            QMessageBox.critical(self, "HTML Generation Error", 
                               f"Failed to generate HTML: {str(e)}")
            return None

    def show_html_preview_dialog(self, html_content, invoice_id):
        """Show HTML preview directly in QWebEngineView - renders exactly like browser"""
        import tempfile
        import os
        from PySide6.QtCore import QUrl
        
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
        except ImportError:
            QMessageBox.critical(self, "Error", "PyQtWebEngine not installed.\n\nRun: pip3 install PyQtWebEngine")
            return
        
        try:
            # Get invoice number for filename
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            invoice_data = generator.get_invoice_data(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            invoice_no = invoice_data['invoice']['invoice_no']
            
            # Create preview dialog
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle(f"📄 Invoice Preview - {invoice_no}")
            preview_dialog.setModal(True)
            preview_dialog.resize(900, 850)
            preview_dialog.setMinimumSize(800, 600)
            
            # Main layout
            layout = QVBoxLayout(preview_dialog)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # Header bar with title and buttons
            header_frame = QFrame()
            header_frame.setFixedHeight(60)
            header_frame.setStyleSheet(get_preview_header_style())
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(15, 5, 15, 5)
            
            # Title
            title_label = QLabel(f"📄 Invoice: {invoice_no}")
            title_label.setStyleSheet(f"color: {WHITE}; font-size: 16px; font-weight: bold;")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # Button style
            btn_style = f"""
                QPushButton {{
                    background: {WHITE};
                    color: {PRIMARY};
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 15px;
                    min-width: 100px;
                }}
                QPushButton:hover {{ background: #e0e7ff; }}
                QPushButton:pressed {{ background: #c7d2fe; }}
            """
            
            # Create temp PDF path for later use
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"Invoice_{invoice_no}.pdf")
            
            # Store references in dialog for callbacks
            preview_dialog.html_content = html_content
            preview_dialog.pdf_path = pdf_path
            preview_dialog.invoice_no = invoice_no
            
            # Save PDF button
            save_btn = QPushButton("💾 Save PDF")
            save_btn.setStyleSheet(btn_style)
            save_btn.clicked.connect(lambda: self.save_invoice_as_pdf(preview_dialog))
            header_layout.addWidget(save_btn)
            
            # Print button
            print_btn = QPushButton("🖨️ Print")
            print_btn.setStyleSheet(btn_style)
            print_btn.clicked.connect(lambda: self.print_invoice_preview(preview_dialog))
            header_layout.addWidget(print_btn)
            
            # Open in Browser button
            browser_btn = QPushButton("🌐 Open in Browser")
            browser_btn.setStyleSheet(btn_style)
            browser_btn.clicked.connect(lambda: self.open_html_in_browser(html_content, invoice_no))
            header_layout.addWidget(browser_btn)
            
            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.setStyleSheet(get_preview_close_button_style())
            close_btn.clicked.connect(preview_dialog.close)
            header_layout.addWidget(close_btn)
            
            layout.addWidget(header_frame)
            
            # HTML Viewer using QWebEngineView - renders exactly like browser!
            html_viewer = QWebEngineView()
            html_viewer.setStyleSheet(get_html_viewer_style())
            
            # Configure settings
            settings = html_viewer.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            
            # Load HTML content directly - this renders exactly like in Chrome!
            html_viewer.setHtml(html_content)
            
            layout.addWidget(html_viewer, 1)  # Stretch factor 1 to fill space
            
            # Store reference to prevent garbage collection
            preview_dialog.html_viewer = html_viewer
            
            # Show dialog
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to show preview: {str(e)}")
            print(f"❌ Preview failed: {e}")

    def save_invoice_as_pdf(self, preview_dialog):
        """Save the invoice as PDF using WebEngine's printToPdf"""
        from PySide6.QtCore import QMarginsF
        from PySide6.QtGui import QPageLayout, QPageSize
        
        # Get save path from user
        default_filename = f"Invoice_{preview_dialog.invoice_no}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Invoice as PDF",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not save_path:
            return
        
        # Store save path for callback
        preview_dialog.save_path = save_path
        
        # Setup page layout for PDF (A4 size with margins)
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(10, 10, 10, 10)
        )
        
        # Generate PDF from the rendered HTML
        def on_pdf_saved(file_path, success):
            if success:
                QMessageBox.information(self, "Saved", f"PDF saved successfully:\n{file_path}")
                # Ask to open
                reply = QMessageBox.question(self, "Open PDF?", "Would you like to open the saved PDF?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.open_pdf_file(file_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to save PDF")
        
        preview_dialog.html_viewer.page().pdfPrintingFinished.connect(on_pdf_saved)
        preview_dialog.html_viewer.page().printToPdf(save_path, page_layout)

    def print_invoice_preview(self, preview_dialog):
        """Print the invoice using system print dialog"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec() == QPrintDialog.Accepted:
            preview_dialog.html_viewer.page().print(printer, lambda ok: None)

    def open_html_in_browser(self, html_content, invoice_no):
        """Open the HTML invoice in the default browser"""
        import tempfile
        import webbrowser
        import os
        
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, f"Invoice_{invoice_no}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        webbrowser.open(f'file://{html_path}')

    def generate_pdf_with_webengine(self, html_content, pdf_path, invoice_no, invoice_id):
        """Use QWebEngineView to render HTML and export to PDF"""
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
            from PySide6.QtCore import QUrl, QMarginsF, QSizeF
            from PySide6.QtGui import QPageLayout, QPageSize
            
            # Create a hidden webview for rendering (with parent to prevent orphan window)
            webview = QWebEngineView(self)
            webview.setMinimumSize(800, 600)
            webview.hide()  # Keep hidden - only used for PDF generation
            
            # Configure settings for better rendering
            settings = webview.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            
            # Store references for the callback
            self._pdf_webview = webview
            self._pdf_path = pdf_path
            self._pdf_invoice_no = invoice_no
            self._pdf_invoice_id = invoice_id
            self._pdf_html_content = html_content
            
            # Connect to loadFinished signal
            webview.loadFinished.connect(self._on_webview_load_finished)
            
            # Load HTML content
            webview.setHtml(html_content)
            
            print(f"📄 Loading HTML into WebEngine for PDF generation...")
            
        except ImportError as e:
            QMessageBox.critical(self, "WebEngine Error", 
                f"PyQtWebEngine is not installed.\n\nPlease run:\npip3 install PyQtWebEngine\n\nError: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Generation Error", f"Failed to initialize WebEngine: {str(e)}")
            print(f"❌ WebEngine initialization failed: {e}")

    def _on_webview_load_finished(self, ok):
        """Called when HTML is loaded in WebEngine, now generate PDF"""
        from PySide6.QtCore import QMarginsF
        from PySide6.QtGui import QPageLayout, QPageSize
        
        if not ok:
            QMessageBox.warning(self, "Load Error", "Failed to load HTML content")
            return
        
        print(f"✅ HTML loaded, generating PDF...")
        
        # Setup page layout for PDF (A4 size with margins)
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(10, 10, 10, 10)  # Small margins (left, top, right, bottom)
        )
        
        # Generate PDF
        self._pdf_webview.page().printToPdf(
            self._pdf_path,
            page_layout
        )
        
        # Connect to pdfPrintingFinished signal
        self._pdf_webview.page().pdfPrintingFinished.connect(self._on_pdf_generated)

    def _on_pdf_generated(self, file_path, success):
        """Called when PDF generation is complete"""
        if success:
            print(f"✅ PDF generated successfully: {file_path}")
            # Show the PDF preview dialog
            self.show_pdf_preview_dialog(
                file_path, 
                self._pdf_invoice_no, 
                self._pdf_html_content, 
                self._pdf_invoice_id
            )
        else:
            QMessageBox.critical(self, "PDF Error", "Failed to generate PDF file")
            print(f"❌ PDF generation failed")
        
        # Cleanup
        if hasattr(self, '_pdf_webview'):
            self._pdf_webview.deleteLater()
            del self._pdf_webview

    def show_pdf_preview_dialog(self, pdf_path, invoice_no, html_content, invoice_id):
        """Show PDF preview inside PyQt dialog with embedded viewer"""
        import os
        import shutil
        from PySide6.QtCore import QUrl
        
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
        except ImportError:
            QMessageBox.critical(self, "Error", "PyQtWebEngine not installed")
            return
        
        # Create preview dialog - larger to show PDF properly
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"📄 Invoice Preview - {invoice_no}")
        preview_dialog.setModal(True)
        preview_dialog.resize(900, 800)
        preview_dialog.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(preview_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header bar with title and buttons
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet(get_preview_header_style())
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Title
        title_label = QLabel(f"📄 Invoice: {invoice_no}")
        title_label.setStyleSheet(get_pdf_page_info_style())
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Button style
        btn_style = get_pdf_toolbar_button_style()
        
        # Save As button
        save_btn = QPushButton("💾 Save As")
        save_btn.setStyleSheet(btn_style)
        save_btn.clicked.connect(lambda: self.save_pdf_as(pdf_path, invoice_no))
        header_layout.addWidget(save_btn)
        
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(btn_style)
        print_btn.clicked.connect(lambda: self.print_pdf(pdf_path))
        header_layout.addWidget(print_btn)
        
        # Open External button
        open_btn = QPushButton("📖 Open External")
        open_btn.setStyleSheet(btn_style)
        open_btn.clicked.connect(lambda: self.open_pdf_file(pdf_path))
        header_layout.addWidget(open_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(get_preview_close_button_style())
        close_btn.clicked.connect(preview_dialog.close)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_frame)
        
        # PDF Viewer using QWebEngineView
        pdf_viewer = QWebEngineView()
        pdf_viewer.setStyleSheet(get_pdf_viewer_style())
        
        # Configure settings
        settings = pdf_viewer.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        
        # Load PDF file directly in WebEngineView (Chrome's built-in PDF viewer)
        pdf_url = QUrl.fromLocalFile(pdf_path)
        pdf_viewer.setUrl(pdf_url)
        
        layout.addWidget(pdf_viewer, 1)  # Stretch factor 1 to fill space
        
        # Store reference to prevent garbage collection
        preview_dialog.pdf_viewer = pdf_viewer
        
        # Show dialog
        preview_dialog.exec() 

    def open_pdf_file(self, pdf_path):
        """Open PDF file with system default viewer"""
        import subprocess
        import os
        
        try:
            if os.path.exists(pdf_path):
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':
                    if os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', pdf_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', pdf_path])
                print(f"📖 Opened PDF: {pdf_path}")
            else:
                QMessageBox.warning(self, "File Not Found", f"PDF file not found: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open PDF: {str(e)}")

    def save_pdf_as(self, pdf_path, invoice_no):
        """Save PDF to user-chosen location"""
        import shutil
        
        try:
            default_filename = f"Invoice_{invoice_no}.pdf"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                default_filename,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if save_path:
                shutil.copy2(pdf_path, save_path)
                QMessageBox.information(self, "Saved", f"PDF saved to:\n{save_path}")
                
                # Ask to open
                reply = QMessageBox.question(self, "Open PDF?", "Would you like to open the saved PDF?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.open_pdf_file(save_path)
                    
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")

    def print_pdf(self, pdf_path):
        """Print PDF using system print dialog"""
        import subprocess
        import os
        
        try:
            if os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
                # Use lpr command for printing on macOS
                subprocess.run(['lpr', pdf_path])
                QMessageBox.information(self, "Print", "PDF sent to default printer!")
            else:
                # Open PDF and let user print from viewer
                self.open_pdf_file(pdf_path)
                QMessageBox.information(self, "Print", "PDF opened. Use Ctrl+P to print.")
        except Exception as e:
            # Fallback: open PDF for manual printing
            self.open_pdf_file(pdf_path)
            QMessageBox.information(self, "Print", f"PDF opened. Please print from the viewer.\n\nError: {str(e)}")

    def open_invoice_in_browser(self, invoice_id, dialog):
        """Open the invoice HTML in browser and close preview dialog"""
        try:
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            import tempfile
            import webbrowser
            
            generator = InvoicePDFGenerator()
            
            # Get invoice data
            invoice_data = generator.get_invoice_data(invoice_id)
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            # Get invoice type and set appropriate template
            invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
            generator.template_path = generator.get_template_path(invoice_type)
            
            # Prepare template data based on invoice type
            if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
                template_data = generator.prepare_non_gst_template_data(invoice_data)
            else:
                template_data = generator.prepare_template_data(invoice_data)
            
            html_content = generator.render_html_template(template_data, invoice_type)
            
            # Create temporary HTML file
            temp_dir = tempfile.gettempdir()
            html_filename = f"invoice_{invoice_data['invoice']['invoice_no']}.html"
            html_path = os.path.join(temp_dir, html_filename)
            
            # Save HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open('file://' + html_path)
            print(f"Invoice HTML opened in browser: {html_path}")
            print("To save as PDF: Press Ctrl+P (or Cmd+P on Mac) and save as PDF")
            
            # Close the preview dialog
            dialog.close()
            
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"Invoice opened in browser!\n\nTo save as PDF:\n• Press Ctrl+P (or Cmd+P on Mac)\n• Choose 'Save as PDF' option")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open invoice in browser: {str(e)}")

    def download_invoice_pdf(self, invoice_id, html_content):
        """Download invoice as PDF file using browser's print-to-PDF functionality"""
        try:
            # Get invoice data for filename
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            invoice_data = generator.get_invoice_data(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            invoice_no = invoice_data['invoice']['invoice_no']
            
            # Try native PDF generation using QPrinter
            try:
                from PySide6.QtPrintSupport import QPrinter
                from PySide6.QtGui import QTextDocument
                
                # Get save location from user
                default_filename = f"Invoice_{invoice_no}.pdf"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Invoice PDF",
                    default_filename,
                    "PDF Files (*.pdf);;All Files (*)"
                )
                
                if not file_path:
                    return  # User cancelled
                
                # Create QTextDocument and set HTML content
                document = QTextDocument()
                document.setHtml(html_content)
                
                # Set up printer for PDF output
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
                
                # Print document to PDF
                document.print(printer)
                
                # Show success message
                QMessageBox.information(
                    self, 
                    "PDF Saved", 
                    f"Invoice PDF saved successfully!\n\nLocation: {file_path}"
                )
                
                # Ask if user wants to open the PDF
                reply = QMessageBox.question(
                    self,
                    "Open PDF?",
                    "Would you like to open the PDF file now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # Open the PDF file with system default application
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS and Linux
                        os.system(f'open "{file_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{file_path}"')
                
            except ImportError as print_error:
                print(f"QPrinter not available: {print_error}")
                
                # Fallback: Generate HTML file and give instructions
                QMessageBox.information(
                    self,
                    "PDF Download Instructions",
                    f"Direct PDF generation is not available.\n\n"
                    f"Alternative method:\n"
                    f"1. Click 'Open in Browser' button\n"
                    f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                    f"3. Choose 'Save as PDF' option\n"
                    f"4. Save as '{invoice_no}.pdf'"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "PDF Download Error", f"Failed to download PDF: {str(e)}")

    def generate_invoice_pdf(self, invoice_id):
        """Generate PDF for the invoice using the PDF generator module"""
        try:
            from ui.print.invoice_pdf_generator import generate_invoice_pdf
            pdf_path = generate_invoice_pdf(invoice_id)
            
            if pdf_path and os.path.exists(pdf_path):
                return pdf_path
            else:
                QMessageBox.critical(self, "PDF Generation Error", 
                                   "Failed to generate PDF. Please check your data and try again.")
                return None
                
        except ImportError:
            QMessageBox.critical(self, "PDF Generation Error", 
                               "PDF generation requires ReportLab library.\nPlease install it using: pip install reportlab")
            return None
        except Exception as e:
            QMessageBox.critical(self, "PDF Generation Error", 
                               f"Failed to generate PDF: {str(e)}")
            return None

    # The following helper sections mirror the original dialog
    def open_party_selector(self):
        """Open the party combo box dropdown when Enter is pressed or selector is triggered."""
        try:
            # Simply show the dropdown - the combo box handles search/selection
            self.party_search.showPopup()
        except Exception as e:
            print(f"Party selector failed: {e}")

    def _focus_first_product_input(self):
        """Focus on the first item row's product input field"""
        try:
            if hasattr(self, 'items_layout'):
                for i in range(self.items_layout.count()):
                    widget = self.items_layout.itemAt(i).widget()
                    if isinstance(widget, InvoiceItemWidget) and hasattr(widget, 'product_input'):
                        widget.product_input.setFocus()
                        return
        except Exception as e:
            print(f"Focus first product input failed: {e}")

    def create_header_section(self):
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 15))
        frame.setMinimumHeight(HEADER_MIN_HEIGHT)  # Flexible instead of fixed 210px
        frame.setMaximumHeight(HEADER_MAX_HEIGHT)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*HEADER_LAYOUT_MARGINS)
        layout.setSpacing(HEADER_LAYOUT_SPACING)

        # Clean label style with emojis for visual distinction
        label_style = f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """

        # ========== HEADER COMPACT/EXPANDED TOGGLE ==========
        self._header_expanded = True  # Track expanded state
        
        # ========== ROW 1: Bill Type, Tax Type, (stretch), Date, Invoice No ==========
        row1 = QHBoxLayout()
        row1.setSpacing(ROW1_SPACING)
        row1.setContentsMargins(*ROW1_MARGINS)

        # Bill Type - Toggle Button (CASH ↔ CREDIT)
        bill_box = QWidget()
        bill_box.setStyleSheet(get_transparent_container_style())
        bill_box.setObjectName("billTypeBox")  # For toggle visibility
        bill_box_layout = QVBoxLayout(bill_box)
        bill_box_layout.setContentsMargins(*BUTTON_LAYOUT_MARGINS)
        bill_box_layout.setSpacing(BILLTYPE_BOX_LAYOUT_SPACING)
        bill_lbl = QLabel("💵 BILL TYPE")
        bill_lbl.setStyleSheet(label_style)
        bill_lbl.setToolTip("Select payment type\n\n⌨️  Shortcut: Alt+B to toggle CASH/CREDIT")
        bill_box_layout.addWidget(bill_lbl)
        
        # Create toggle button instead of combo box
        self.billtype_btn = QPushButton("💵 CASH")
        self.billtype_btn.setFixedHeight(BILLTYPE_BTN_HEIGHT)
        self.billtype_btn.setCursor(Qt.PointingHandCursor)
        self.billtype_btn.setToolTip(
            "<b style='color: #3B82F6;'>💵 Bill Type Toggle</b><br><br>"
            "<span style='color: #059669;'>✓ 💵 <b>CASH</b>: Payment received immediately</span><br>"
            "<span style='color: #059669;'>✓ 📝 <b>CREDIT</b>: Payment due later (shows Balance Due)</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Shortcut: Alt+B</i></span>"
        )
        self.billtype_btn.setAutoDefault(False)  # Prevent Enter key from triggering
        self.billtype_btn.setDefault(False)  # Not the default button
        self._bill_type = "CASH"  # Internal state
        
        # Store reference to update function for external access
        self._update_billtype_style = lambda: self._apply_billtype_style()
        
        self.billtype_btn.clicked.connect(self._toggle_bill_type)
        self._apply_billtype_style()  # Set initial style
        bill_box_layout.addWidget(self.billtype_btn)
        bill_box.setFixedWidth(BILLTYPE_BTN_WIDTH)
        row1.addWidget(bill_box)

        # Tax Type with Segmented Button Group
        gst_box = QWidget()
        gst_box.setStyleSheet(get_transparent_container_style())
        gst_box.setObjectName("taxTypeBox")  # For toggle visibility
        gst_box_layout = QVBoxLayout(gst_box)
        gst_box_layout.setContentsMargins(*BUTTON_LAYOUT_MARGINS)
        gst_box_layout.setSpacing(TAX_BOX_LAYOUT_SPACING)
        gst_lbl = QLabel("📊 TAX TYPE")
        gst_lbl.setStyleSheet(label_style)
        gst_lbl.setToolTip("<b>Tax Classification</b><br><br>Select based on buyer location:<br>⌨️  Use arrow keys or number keys (1/2/3) to select")
        gst_box_layout.addWidget(gst_lbl)
        
        # Create segmented button container with proper styling
        self._tax_type = "SAME_STATE"  # Internal state: SAME_STATE, OTHER_STATE, NON_GST
        segment_container = QFrame()
        segment_container.setObjectName("taxTypeSegment")
        segment_container.setFixedHeight(TAX_SEGMENT_HEIGHT)
        segment_container.setStyleSheet(f"""
            QFrame#taxTypeSegment {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 0px;
                margin: 0px;
            }}
        """)
        segment_layout = QHBoxLayout(segment_container)
        segment_layout.setContentsMargins(*SEGMENT_LAYOUT_MARGINS)
        segment_layout.setSpacing(SEGMENT_LAYOUT_SPACING)
        
        # Create three segment buttons
        self.tax_btn_same = QPushButton("Same State")
        self.tax_btn_other = QPushButton("Other State")
        self.tax_btn_nongst = QPushButton("Non-GST")
        
        # Store buttons for easy access
        self._tax_buttons = {
            "SAME_STATE": self.tax_btn_same,
            "OTHER_STATE": self.tax_btn_other,
            "NON_GST": self.tax_btn_nongst
        }
        
        # Configure buttons with proper segmented styling
        buttons_config = [
            (self.tax_btn_same, "SAME_STATE", "🏠", "6px 0 0 6px"),
            (self.tax_btn_other, "OTHER_STATE", "🚚", "0"),
            (self.tax_btn_nongst, "NON_GST", "❌", "0 6px 6px 0")
        ]
        
        for btn, key, emoji, border_radius in buttons_config:
            btn.setFixedHeight(TAX_SEGMENT_BTN_HEIGHT)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setAutoDefault(False)
            btn.setDefault(False)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {WHITE};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER};
                    border-radius: {border_radius};
                    padding: 6px 12px;
                    font-size: 11px;
                    font-weight: 600;
                    outline: none;
                }}
                QPushButton:hover {{
                    background: {PRIMARY_LIGHT};
                    border: 1px solid {PRIMARY};
                }}
                QPushButton:pressed {{
                    background: {PRIMARY};
                    color: {WHITE};
                    border: 1px solid {PRIMARY};
                }}
            """)
        
        # Set tooltips with proper HTML formatting for visibility
        self.tax_btn_same.setToolTip(
            "<b style='color: #3B82F6;'>🏠 Same State (Intra-State GST)</b><br><br>"
            "<span style='color: #059669;'>✓ CGST + SGST applies</span><br>"
            "<span style='color: #6B7280;'>• Buyer & seller in same state</span><br>"
            "<span style='color: #6B7280;'>• Tax split between Central & State</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Press 1 to select</i></span>"
        )
        self.tax_btn_other.setToolTip(
            "<b style='color: #F59E0B;'>🚚 Other State (Inter-State GST)</b><br><br>"
            "<span style='color: #059669;'>✓ IGST applies</span><br>"
            "<span style='color: #6B7280;'>• Buyer & seller in different states</span><br>"
            "<span style='color: #6B7280;'>• Single integrated tax</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Press 2 to select</i></span>"
        )
        self.tax_btn_nongst.setToolTip(
            "<b style='color: #6B7280;'>❌ Non-GST</b><br><br>"
            "<span style='color: #059669;'>✓ No GST applicable</span><br>"
            "<span style='color: #6B7280;'>• Exempt goods/services</span><br>"
            "<span style='color: #6B7280;'>• Tax = 0%</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Press 3 to select</i></span>"
        )
        
        # Connect click handlers
        self.tax_btn_same.clicked.connect(lambda: self._set_tax_type("SAME_STATE"))
        self.tax_btn_other.clicked.connect(lambda: self._set_tax_type("OTHER_STATE"))
        self.tax_btn_nongst.clicked.connect(lambda: self._set_tax_type("NON_GST"))
        
        # Add buttons to layout
        segment_layout.addWidget(self.tax_btn_same, 1)
        segment_layout.addWidget(self.tax_btn_other, 1)
        segment_layout.addWidget(self.tax_btn_nongst, 1)
        
        # Apply initial styling
        self._apply_tax_type_styles()
        
        gst_box_layout.addWidget(segment_container)
        gst_box.setFixedWidth(TAX_TYPE_BOX_WIDTH)  # Optimized width for better Row 1 spacing
        row1.addWidget(gst_box)

        # Stretch to push Date and Invoice No to the right
        row1.addStretch()

 # ========== ROW 1.5: Party Info Display (centered) ==========
        party_info_container = QWidget()
        party_info_container.setStyleSheet(get_transparent_container_style())
        party_info_container_layout = QHBoxLayout(party_info_container)
        party_info_container_layout.setContentsMargins(0, 0, 0, 0)
        party_info_container_layout.setSpacing(0)
        
        # Add stretch on left side
        party_info_container_layout.addStretch()
        
        # Party info display (shows details after selection) - Enhanced card style in center
        self.party_info_label = QLabel("")
        self.party_info_label.setTextFormat(Qt.RichText)  # Enable HTML rendering
        self.party_info_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {TEXT_PRIMARY};
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F0FDF4, stop:1 #ECFDF5);
                border: 1px solid #86EFAC;
                border-radius: 6px;
                border-left: 4px solid #10B981;
            }}
        """)
        self.party_info_label.setVisible(False)
        self.party_info_label.setMinimumWidth(PARTY_INFO_MIN_WIDTH)  # Increased for 2-line display
        self.party_info_label.setMaximumWidth(PARTY_INFO_MAX_WIDTH)  # Wider to accommodate phone + GSTIN + address on line 1
        self.party_info_label.setWordWrap(True)  # Still allow wrapping but won't need it with wider width
        party_info_container_layout.addWidget(self.party_info_label, 0)  # No stretch - keep centered
        
        # Add stretch on right side
        party_info_container_layout.addStretch()
        row1.addWidget(party_info_container)
        # layout.addWidget(party_info_container)

        # Stretch to push Date and Invoice No to the right
        row1.addStretch()

        # Invoice Date (right corner)
        inv_date_box = QWidget()
        inv_date_box.setStyleSheet(get_transparent_container_style())
        inv_date_box.setObjectName("invoiceDateBox")  # For toggle visibility
        inv_date_box_layout = QVBoxLayout(inv_date_box)
        inv_date_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_date_box_layout.setSpacing(4)
        inv_date_lbl = QLabel("📅 DATE")
        inv_date_lbl.setStyleSheet(label_style)
        inv_date_lbl.setToolTip(
            "<b style='color: #3B82F6;'>📅 Invoice Date</b><br><br>"
            "<span style='color: #6B7280;'>Date when invoice is created</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Shortcut: Alt+D</i></span>"
        )
        inv_date_box_layout.addWidget(inv_date_lbl)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setFixedHeight(INVOICE_DATE_BOX_HEIGHT)
        self.invoice_date.setDisplayFormat("dd-MM-yyyy")
        self.invoice_date.setStyleSheet(get_date_edit_style() + get_calendar_stylesheet())
        
        # Get the calendar widget and configure it
        calendar = self.invoice_date.calendarWidget()
        if calendar:
            calendar.setGridVisible(True)
            calendar.setVerticalHeaderFormat(calendar.VerticalHeaderFormat.NoVerticalHeader)
            calendar.setStyleSheet(get_calendar_stylesheet())
        
        # Connect editingFinished to focus on product input after date
        self.invoice_date.editingFinished.connect(self._focus_first_product_input)
        inv_date_box_layout.addWidget(self.invoice_date)
        inv_date_box.setFixedWidth(INVOICE_DATE_BOX_WIDTH)  # Increased from 150 to accommodate full date "dd-MM-yyyy"
        row1.addWidget(inv_date_box)

        # Invoice Number (right corner) - editable for new invoices, read-only for existing
        inv_num_box = QWidget()
        inv_num_box.setStyleSheet(get_transparent_container_style())
        inv_num_box.setObjectName("invoiceNumberBox")  # For toggle visibility
        inv_num_box_layout = QVBoxLayout(inv_num_box)
        inv_num_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_num_box_layout.setSpacing(4)
        inv_num_lbl = QLabel("📄 INVOICE NO")
        inv_num_lbl.setStyleSheet(label_style)
        inv_num_lbl.setToolTip(
            "<b style='color: #3B82F6;'>📄 Invoice Number</b><br><br>"
            "<span style='color: #059669;'>🔵 NEW:</span> <span style='color: #6B7280;'>Editable - auto-generated</span><br>"
            "<span style='color: #6B7280;'>🔴 EXISTING:</span> <span style='color: #6B7280;'>Read-only - locked</span><br><br>"
            "<span style='color: #6B7280;'><i>Unique identifier for this invoice</i></span>"
        )
        inv_num_box_layout.addWidget(inv_num_lbl)
        
        # Determine next invoice number via controller
        next_inv_no = invoice_form_controller.generate_next_invoice_number()
        self.invoice_number = QLineEdit(next_inv_no)
        
        # Make editable for new invoices, read-only for existing ones
        if self.invoice_data:
            self.invoice_number.setReadOnly(True)
            self.invoice_number.setStyleSheet(get_invoice_number_input_style().replace("QLineEdit", "QLineEdit:read-only"))
        else:
            # For new invoices, allow editing
            self.invoice_number.setReadOnly(False)
            self.invoice_number.setStyleSheet(get_invoice_number_input_style())
        
        self.invoice_number.setFixedHeight(INVOICE_NUMBER_BOX_HEIGHT)
        self.invoice_number.setAlignment(Qt.AlignCenter)
        inv_num_box_layout.addWidget(self.invoice_number)
        inv_num_box.setFixedWidth(INVOICE_NUMBER_BOX_WIDTH)
        row1.addWidget(inv_num_box)

        layout.addLayout(row1)

        # # ========== SEPARATOR LINE between Row 1 and Row 2 ==========
        # separator = QFrame()
        # separator.setFrameShape(QFrame.HLine)
        # separator.setStyleSheet(f"background-color: {BORDER}; max-height: 1px; margin: 4px 0px;")
        # layout.addWidget(separator)


        # ========== ROW 2: Select Party (full width) ==========
        row2 = QHBoxLayout()
        row2.setSpacing(ROW2_SPACING)

        party_box = QWidget()
        party_box.setStyleSheet(get_transparent_container_style())
        party_box_layout = QVBoxLayout(party_box)
        party_box_layout.setContentsMargins(0, 0, 0, 0)
        party_box_layout.setSpacing(4)
        party_header = QHBoxLayout()
        party_header.setSpacing(10)
        party_label = QLabel("👥 SELECT PARTY / CUSTOMER")
        party_label.setStyleSheet(label_style)
        party_label.setToolTip(
            "<b style='color: #3B82F6;'>👥 Party Selection</b><br><br>"
            "<span style='color: #6B7280;'><i>⏱️ Recent:</i> Recently used parties shown first</span><br>"
            "<span style='color: #6B7280;'><i>🔍 Search:</i> Type name, GSTIN, or phone</span><br><br>"
            "<span style='color: #6B7280;'><i>⌨️  Press Enter to select<br>Esc to clear</i></span>"
        )
        party_header.addWidget(party_label)
        add_party_link = QLabel("<a href='#' style='text-decoration: none;'>+ Add New Party</a>")
        add_party_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_party_link.setOpenExternalLinks(False)
        add_party_link.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel:hover {{
                color: {PRIMARY_HOVER};
            }}
        """)
        add_party_link.setCursor(Qt.PointingHandCursor)
        add_party_link.setToolTip(
            "<b style='color: #3B82F6;'>➕ Add New Party</b><br><br>"
            "<span style='color: #6B7280;'>Quick dialog to create new party</span><br>"
            "<span style='color: #6B7280;'>without leaving the invoice form</span><br><br>"
            "<span style='color: #059669;'>✓ Automatically selected after creation</span><br>"
            "<span style='color: #6B7280;'><i>Returns to invoice immediately</i></span>"
        )
        add_party_link.linkActivated.connect(self.open_quick_add_party_dialog)
        party_header.addWidget(add_party_link)
        party_header.addStretch()
        party_box_layout.addLayout(party_header)

        # Create party search container with combobox and clear button
        party_search_container = QWidget()
        party_search_container.setStyleSheet("background: transparent;")
        party_search_layout = QHBoxLayout(party_search_container)
        party_search_layout.setContentsMargins(0, 0, 0, 0)
        party_search_layout.setSpacing(5)

        # Create party combo box with search functionality
        party_names = [p.get('name', '').strip() for p in (self.parties or []) if p.get('name', '').strip()]
        self.party_search = DialogEditableComboBox(
            items=[],  # Don't add items - we'll use QCompleter only
            placeholder="🔍 Type to search party name, GSTIN, or phone...",
            auto_upper=True
        )
        self.party_search.setFixedHeight(PARTY_SEARCH_HEIGHT)
        self.party_search.setMinimumWidth(PARTY_SEARCH_MIN_WIDTH)  # Minimum width, will expand
        
        # Disable native completer - we'll use our custom QCompleter
        self.party_search.setCompleter(None)
        
        # Simple styling for the input box only (no dropdown styling needed)
        # We use QCompleter popup for ALL selections (typing AND button click)
        self.party_search.setStyleSheet(f"""
            QComboBox {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                padding-right: 45px;
                font-size: 15px;
                color: {TEXT_PRIMARY};
            }}
            QComboBox:focus {{
                border: 2px solid {PRIMARY};
            }}
            QComboBox:hover {{
                border: 2px solid {PRIMARY_HOVER};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 40px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: url(assets/icons/down-arrow.png);
                width: 16px;
                height: 16px;
            }}
        """)
        
        # Populate party_data_map with balance info
        self.party_data_map = {}
        self.party_display_map = {}  # Maps display text to party name
        all_display_names = []  # All parties in alphabetical order
        
        for p in (self.parties or []):
            name = p.get('name', '').strip()
            if name:
                self.party_data_map[name] = p
                
                # Calculate balance from opening_balance and balance_type
                # 'dr' (debit) = money owed to us (Due)
                # 'cr' (credit) = advance payment (Advance)
                opening_balance = p.get('opening_balance', 0) or 0
                balance_type = p.get('balance_type', 'dr') or 'dr'
                
                # Convert to signed balance: positive = Due, negative = Advance
                if balance_type.lower() == 'cr':
                    balance = -abs(opening_balance)  # Negative = Advance
                else:
                    balance = abs(opening_balance)   # Positive = Due
                
                # Store calculated balance in party data for later use
                p['_calculated_balance'] = balance
                
                # Display party name in search dropdown (balance shown in party info after selection)
                display_text = name
                self.party_display_map[display_text] = name
                all_display_names.append(display_text)
        
        # Sort all parties alphabetically
        all_display_names.sort()
        
        # DON'T add items to combo box - we use QCompleter only for all selections
        # This ensures ONE consistent popup style for both typing and button click
        
        # Create custom completer - this is the ONLY popup we use
        self.party_completer = QCompleter(all_display_names, self)
        self.party_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.party_completer.setFilterMode(Qt.MatchContains)
        self.party_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.party_completer.setMaxVisibleItems(PARTY_COMPLETER_MAX_VISIBLE_ITEMS)
        
        # Create highlight delegate for matched text
        self.party_highlight_delegate = HighlightDelegate(self.party_completer.popup())
        self.party_completer.popup().setItemDelegate(self.party_highlight_delegate)
        
        # Style the completer popup (this is the ONLY popup style we need)
        self.party_completer.popup().setStyleSheet(f"""
            QListView {{
                background: {WHITE};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                padding: 4px;
                font-size: 14px;
                outline: none;
            }}
            QListView::item {{
                padding: 14px 16px;
                min-height: 44px;
                border: none;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListView::item:hover {{
                background: {PRIMARY_LIGHT};
            }}
            QListView::item:selected {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        
        # Set completer on the line edit
        self.party_search.lineEdit().setCompleter(self.party_completer)
        
        # Pre-position completer popup before it shows (to avoid flickering)
        self._setup_completer_positioning()
        
        # Connect completer activation to selection handler
        self.party_completer.activated.connect(self._on_party_completer_activated)

        def custom_show_popup():
            # Show all items by completing with empty prefix
            self.party_completer.setCompletionPrefix("")
            self.party_completer.complete()
            # Position the popup
            self._position_completer_popup()

        # Connect to handle text changes
        self.party_search.lineEdit().textEdited.connect(self._on_party_text_edited)

        self.party_search.showPopup = custom_show_popup

        # Override showPopup to show QCompleter popup instead of native combo dropdown
        # This makes button click use the SAME popup as typing        
        # Connect only to actual selection events (completer activation), NOT text changes
        # This ensures on_party_selected is called only when user confirms selection
        
        # Install event filter for keyboard navigation (Tab to confirm, Escape to clear, Down to open)
        # Install on BOTH lineEdit and the combobox itself to catch all key events
        self.party_search.lineEdit().installEventFilter(self)
        self.party_search.installEventFilter(self)
        
        party_search_layout.addWidget(self.party_search, 1)  # Stretch factor 1 to expand
        
        # Add party search container with full width (no side-by-side layout)
        party_box_layout.addWidget(party_search_container)
        
        # Validation error label (hidden by default)
        self.party_error_label = QLabel("")
        self.party_error_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: #EF4444;
                padding: 2px 4px;
            }}
        """)
        self.party_error_label.setVisible(False)
        party_box_layout.addWidget(self.party_error_label)
        
        row2.addWidget(party_box, 1)  # Stretch to fill full width

        layout.addLayout(row2)

        return frame

    def open_quick_add_party_dialog(self, link=None):
        """Open a quick dialog to add a new party without leaving the invoice."""
        try:
            from ui.parties.party_form_dialog import PartyDialog
            
            # Get the text user typed in the search box
            search_text = self.party_search.lineEdit().text().strip() if hasattr(self, 'party_search') else ""
            
            # Create and open the party dialog
            dialog = PartyDialog(self)
            
            # Pre-fill the party name field if user typed something
            if search_text and hasattr(dialog, 'name_input'):
                dialog.name_input.setText(search_text)
                dialog.name_input.selectAll()  # Select all for easy editing
                dialog.name_input.setFocus()  # Focus on the field
            
            if dialog.exec() == QDialog.Accepted:
                # Refresh parties list via controller
                self.parties = invoice_form_controller.get_parties()
                
                # Update party_data_map, display_map, and combo box items
                self.party_data_map = {}
                self.party_display_map = {}
                party_display_names = []
                
                for party in self.parties:
                    name = party.get('name', '').strip()
                    if name:
                        self.party_data_map[name] = party
                        
                        # Calculate balance from opening_balance and balance_type
                        opening_balance = party.get('opening_balance', 0) or 0
                        balance_type = party.get('balance_type', 'dr') or 'dr'
                        if balance_type.lower() == 'cr':
                            balance = -abs(opening_balance)
                        else:
                            balance = abs(opening_balance)
                        party['_calculated_balance'] = balance
                        
                        # Create display text with balance
                        if balance > 0:
                            display_text = f"{name}  [₹{balance:,.2f} Due]"
                        elif balance < 0:
                            display_text = f"{name}  [₹{abs(balance):,.2f} Advance]"
                        else:
                            display_text = name
                        self.party_display_map[display_text] = name
                        party_display_names.append(display_text)
                
                # Update combo box items
                self.party_search.blockSignals(True)
                self.party_search.clear()
                self.party_search.addItems(party_display_names)
                self.party_search.setCurrentIndex(-1)
                self.party_search.blockSignals(False)
                
                # Update the completer with new party names
                if hasattr(self, 'party_completer'):
                    from PySide6.QtCore import QStringListModel
                    self.party_completer.setModel(QStringListModel(party_display_names))
                
                # If a new party was created, select it automatically
                if hasattr(dialog, 'saved_party_name') and dialog.saved_party_name:
                    self.party_search.setCurrentText(dialog.saved_party_name)
                    # Show party info
                    party_data = self.party_data_map.get(dialog.saved_party_name)
                    if party_data:
                        self._show_party_info(party_data)
                    highlight_success(self.party_search)
                    QMessageBox.information(self, "Success", f"✅ Party '{dialog.saved_party_name}' added and selected!")
                else:
                    QMessageBox.information(self, "Success", "✅ New party added! You can now search and select it.")
        except ImportError:
            QMessageBox.warning(self, "Feature Unavailable", "Party dialog module not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open party dialog: {str(e)}")

    def on_party_selected(self, text: str):
        """Handle party selection from the combo box.
        Shows party info, updates UI, and automatically adds first item row.
        """
        try:
            if not text or not text.strip():
                self._hide_party_info()
                return
            
            # Skip section separators
            if text.startswith("──"):
                self.party_search.setCurrentIndex(-1)
                return
            
            # Remove recent party prefix if present
            clean_text = text.strip()
            if clean_text.startswith("⏱️ "):
                clean_text = clean_text[3:]  # Remove "⏱️ " prefix
            
            # Extract party name from display text (remove balance info)
            party_name = self.party_display_map.get(clean_text, clean_text)
            # Also check with prefix
            if party_name == clean_text:
                party_name = self.party_display_map.get(text.strip(), clean_text)
            
            # If party name still has balance info, extract just the name
            if "  [" in party_name:
                party_name = party_name.split("  [")[0]
            
            # Check if the selected party exists in our data map
            party_data = self.party_data_map.get(party_name)
            if party_data:
                # Valid party selected
                self._show_party_info(party_data)
                self._clear_party_error()
                
                # Update combobox border to success color
                self.party_search.setStyleSheet(self.party_search.styleSheet().replace(
                    f"border: 2px solid {BORDER}",
                    f"border: 2px solid #10B981"
                ))
                
                # Set clean party name (without balance info) in the input
                self.party_search.blockSignals(True)
                self.party_search.setCurrentText(party_name)
                self.party_search.blockSignals(False)
                
                # Auto-add first item row if no items exist
                item_count = 0
                for i in range(self.items_layout.count()):
                    widget = self.items_layout.itemAt(i).widget()
                    if isinstance(widget, InvoiceItemWidget):
                        item_count += 1
                
                if item_count == 0:
                    # Automatically add first item row
                    QTimer.singleShot(200, self.add_item)
                else:
                    # Keep focus on party search so user can easily delete/clear if needed
                    if hasattr(self, 'party_search'):
                        QTimer.singleShot(150, lambda: self.party_search.lineEdit().setFocus())
            else:
                # Check if it's a partial match (user is still typing)
                matching_parties = [n for n in self.party_data_map.keys() 
                                   if clean_text.upper() in n.upper()]
                if not matching_parties and len(clean_text) > 2:
                    self._show_party_error(f"No party found matching '{clean_text}'")
                    self._hide_party_info()
        except Exception as e:
            print(f"Party selection handler error: {e}")

    def _on_party_completer_activated(self, text: str):
        """Handle party selection from the completer dropdown.
        Sets the text, shows party info, and automatically adds first empty item row.
        Focus stays in party search field - user presses Enter to move to product search.
        """
        try:
            if text and text.strip():
                # Skip section separators
                if text.startswith("──"):
                    return
                
                # Extract party name from display text
                clean_text = text.strip()
                party_name = self.party_display_map.get(clean_text, clean_text)
                
                # If party name still has balance info, extract just the name
                if "  [" in party_name:
                    party_name = party_name.split("  [")[0]
                
                # Set just the party name in the combo box (not the display text with balance)
                self.party_search.blockSignals(True)
                self.party_search.lineEdit().setText(party_name)  # Set text directly
                self.party_search.blockSignals(False)
                
                # Show party info
                party_data = self.party_data_map.get(party_name)
                if party_data:
                    self._show_party_info(party_data)
                    self._clear_party_error()
                    
                    # Update border to success
                    self.party_search.setStyleSheet(self.party_search.styleSheet().replace(
                        f"border: 2px solid {BORDER}",
                        f"border: 2px solid #10B981"
                    ))
                    
                    # ✅ AUTO-ADD FIRST ITEM ROW if no items exist
                    item_count = 0
                    for i in range(self.items_layout.count()):
                        widget = self.items_layout.itemAt(i).widget()
                        if isinstance(widget, InvoiceItemWidget):
                            item_count += 1
                    
                    if item_count == 0:
                        # Automatically add first empty item row
                        QTimer.singleShot(200, self.add_item)
                    
                    # Keep focus on party search field - user presses Enter to move to product search
                    QTimer.singleShot(150, lambda: self.party_search.lineEdit().setFocus())
        except Exception as e:
            print(f"Party completer activation error: {e}")

    def _focus_on_product_search(self):
        """Focus on the first item's product search field."""
        try:
            # Find the first InvoiceItemWidget
            for i in range(self.items_layout.count()):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    # Focus on the product_input field
                    if hasattr(widget, 'product_input'):
                        widget.product_input.lineEdit().setFocus()
                        widget.product_input.lineEdit().selectAll()
                    break
        except Exception as e:
            print(f"Error focusing on product search: {e}")

    def _on_party_text_edited(self, text: str):
        """Handle text editing in party search - position dropdown, validate, highlight matches, and show suggestions."""
        try:
            # Reset styling when editing
            if hasattr(self, 'party_search'):
                current_style = self.party_search.styleSheet()
                if "#10B981" in current_style or "#EF4444" in current_style:
                    self.party_search.setStyleSheet(current_style.replace(
                        "border: 2px solid #10B981", f"border: 2px solid {BORDER}"
                    ).replace(
                        "border: 2px solid #EF4444", f"border: 2px solid {BORDER}"
                    ))
            
            if text and len(text) >= 1:
                # Update highlight delegate with search text
                if hasattr(self, 'party_highlight_delegate'):
                    self.party_highlight_delegate.set_search_text(text)

                # Position popup after QCompleter finishes its internal positioning
                # Use QTimer to ensure our positioning happens LAST
                QTimer.singleShot(COMPLETER_POPUP_POSITIONING_DELAY_MS, self._position_completer_popup)
                
                # Clear error while typing
                self._clear_party_error()
                
                # Check for matches (debounced validation)
                if hasattr(self, '_party_validation_timer'):
                    self._party_validation_timer.stop()
                self._party_validation_timer = QTimer()
                self._party_validation_timer.setSingleShot(True)
                self._party_validation_timer.timeout.connect(lambda: self._validate_party_input(text))
                self._party_validation_timer.start(PARTY_TEXT_VALIDATION_DEBOUNCE_MS)  # 300ms debounce
            else:
                self._hide_party_info()
                self._clear_party_error()
                # Clear highlight when no text
                if hasattr(self, 'party_highlight_delegate'):
                    self.party_highlight_delegate.set_search_text("")
        except Exception as e:
            print(f"Party text edited error: {e}")

    def _validate_party_input(self, text: str):
        """Validate party input after debounce delay."""
        try:
            if not text or len(text) < 2:
                return
            
            # Check for matches
            matching = [n for n in self.party_data_map.keys() 
                       if text.strip().upper() in n.upper()]
            
            if not matching and len(text) >= 3:
                self._show_party_error(f"No party found. Click '+Add New' to create.")
        except Exception as e:
            print(f"Party validation error: {e}")

    def _show_party_info(self, party_data: dict):
        """Display party information below the search box in a card format with hover tooltip."""
        try:
            if not hasattr(self, 'party_info_label'):
                return
            
            name = party_data.get('name', '')
            party_id = party_data.get('id', '')
            phone = party_data.get('phone', '') or party_data.get('mobile', '')
            address = party_data.get('address', '')
            gstin = party_data.get('gstin', '') or party_data.get('gst_number', '') or party_data.get('gst_no', '')
            city = party_data.get('city', '')
            state = party_data.get('state', '')
            
            # Get total balance (opening + pending from invoices)
            balance_info = invoice_form_controller.get_party_total_balance(party_id, party_data)
            total_balance = balance_info['total']
            opening_balance = balance_info['opening']
            pending_balance = balance_info['pending']            

            # Build rich info HTML for better display
            info_html = []
            
            # Line 1: Phone | GSTIN | Address (all in one line with separators)
            line1_parts = []
            if phone:
                line1_parts.append(f"📞 {phone}")
            if gstin:
                line1_parts.append(f"🏷️ {gstin}")
            
            # Add address to line 1
            if address or city or state:
                addr_parts = []
                if address:
                    addr_short = address[:30] + "..." if len(address) > 30 else address
                    addr_parts.append(addr_short)
                if city:
                    addr_parts.append(city)
                if state:
                    addr_parts.append(state)
                if addr_parts:
                    line1_parts.append(f"📍 {', '.join(addr_parts)}")
            
            if line1_parts:
                info_html.append(f"<span style='color: #059669;'>{' | '.join(line1_parts)}</span>")
            
            # Line 2: Total Balance Due (with color coding based on type)
            if total_balance > 0:
                info_html.append(f"<span style='color: #DC2626;'>� Total Due: <b>₹{total_balance:,.2f}</b></span>")
            elif total_balance < 0:
                info_html.append(f"<span style='color: #059669;'>💚 Advance Credit: <b>₹{abs(total_balance):,.2f}</b></span>")
            else:
                info_html.append(f"<span style='color: #059669;'>✓ No outstanding balance</span>")
            
            if info_html:
                self.party_info_label.setText("<br>".join(info_html))
                # Create detailed tooltip for hover
                tooltip_parts = [f"<b style='color: #3B82F6; font-size: 14px;'>👥 {name}</b>"]
                if phone:
                    tooltip_parts.append(f"<br><b>📞 Phone:</b> <span style='color: #059669;'>{phone}</span>")
                if gstin:
                    tooltip_parts.append(f"<br><b>🏷️  GSTIN:</b> <span style='color: #059669;'>{gstin}</span>")
                if address:
                    tooltip_parts.append(f"<br><b>📍 Address:</b> <span style='color: #059669;'>{address}</span>")
                if city:
                    tooltip_parts.append(f"<br><b>🏘️  City:</b> <span style='color: #059669;'>{city}</span>")
                if state:
                    tooltip_parts.append(f"<br><b>🗺️  State:</b> <span style='color: #059669;'>{state}</span>")
                # Show balance breakdown in tooltip
                tooltip_parts.append(f"<br><br><b style='color: #3B82F6;'>💰 Balance Breakdown:</b>")
                tooltip_parts.append(f"<br>• Opening Balance: <span style='color: #666666;'>₹{opening_balance:,.2f}</span>")
                tooltip_parts.append(f"<br>• Pending Invoices: <span style='color: #666666;'>₹{pending_balance:,.2f}</span>")
                
                if total_balance >= 0:
                    tooltip_parts.append(f"<br><br><b style='color: #DC2626;'>� TOTAL DUE: ₹{total_balance:,.2f}</b>")
                else:
                    tooltip_parts.append(f"<br><br><b style='color: #059669;'>💚 TOTAL CREDIT: ₹{abs(total_balance):,.2f}</b>")
                self.party_info_label.setToolTip("".join(tooltip_parts))
                self.party_info_label.setVisible(True)
            else:
                self.party_info_label.setVisible(False)
            
            # Auto-detect tax type based on party state
            self._auto_detect_tax_type(party_data)
        except Exception as e:
            print(f"Show party info error: {e}")

    def _auto_detect_tax_type(self, party_data: dict):
        """Auto-detect and set tax type based on party's state vs company's state.
        
        Delegates to invoice_form_controller which uses PartyService for business logic.
        """
        try:
            if not hasattr(self, '_tax_type'):
                return
            
            # Get company info from controller
            company_data = invoice_form_controller.get_current_company()
            if not company_data:
                return
            
            # Use controller to detect tax type (delegates to PartyService)
            tax_type = invoice_form_controller.detect_tax_type_for_party(party_data, company_data)
            
            # Map tax type to UI selection
            if tax_type == 'GST':
                # Check GSTIN state codes to determine if same/different state
                party_gstin = party_data.get('gstin', '') or party_data.get('gst_number', '') or ''
                company_gstin = company_data.get('gstin', '') or ''
                
                party_state_code = party_gstin[:2] if len(party_gstin) >= 2 and party_gstin[:2].isdigit() else None
                company_state_code = company_gstin[:2] if len(company_gstin) >= 2 and company_gstin[:2].isdigit() else None
                
                if party_state_code and company_state_code:
                    if party_state_code == company_state_code:
                        self._set_tax_type("SAME_STATE")
                    else:
                        self._set_tax_type("OTHER_STATE")
            else:
                # Non-GST transaction
                self._set_tax_type("NON_GST")
            
        except Exception as e:
            print(f"Auto-detect tax type error: {e}")

    def _hide_party_info(self):
        """Hide the party info label."""
        try:
            if hasattr(self, 'party_info_label'):
                self.party_info_label.setVisible(False)
        except Exception as e:
            print(f"Hide party info error: {e}")

    def _show_party_error(self, message: str):
        """Display validation error for party selection."""
        try:
            if hasattr(self, 'party_error_label'):
                self.party_error_label.setText(f"⚠️ {message}")
                self.party_error_label.setVisible(True)
            
            # Update combobox border to error color
            if hasattr(self, 'party_search'):
                current_style = self.party_search.styleSheet()
                self.party_search.setStyleSheet(current_style.replace(
                    f"border: 2px solid {BORDER}", "border: 2px solid #EF4444"
                ).replace(
                    "border: 2px solid #10B981", "border: 2px solid #EF4444"
                ))
        except Exception as e:
            print(f"Show party error error: {e}")

    def _clear_party_error(self):
        """Clear the party validation error."""
        try:
            if hasattr(self, 'party_error_label'):
                self.party_error_label.setVisible(False)
                self.party_error_label.setText("")
        except Exception as e:
            print(f"Clear party error error: {e}")

    def _clear_party_selection(self):
        """Clear the selected party and reset the search box. Triggered by Escape key."""
        try:
            self.party_search.setCurrentIndex(-1)
            self.party_search.lineEdit().clear()
            self.party_search.lineEdit().setPlaceholderText("🔍 Search or select customer...")
            self._hide_party_info()
            self._clear_party_error()
            
            # Reset border color
            current_style = self.party_search.styleSheet()
            self.party_search.setStyleSheet(current_style.replace(
                "border: 2px solid #10B981", f"border: 2px solid {BORDER}"
            ).replace(
                "border: 2px solid #EF4444", f"border: 2px solid {BORDER}"
            ))
            
            # Focus back on search and show all options
            self.party_search.setFocus()
            # Show dropdown with all options after clearing
            QTimer.singleShot(100, lambda: self.party_search.showPopup())
        except Exception as e:
            print(f"Clear party selection error: {e}")

    def eventFilter(self, obj, event):
        """Handle keyboard events for party search - Tab/Enter to confirm, Escape to clear, Down to open dropdown."""
        try:
            from PySide6.QtCore import QEvent
            
            # Check if event is from party search (either combobox or its lineEdit)
            if hasattr(self, 'party_search'):
                is_party_search = (obj == self.party_search or obj == self.party_search.lineEdit())
                
                if is_party_search and event.type() == QEvent.KeyPress:
                    # Down arrow key: open dropdown menu
                    if event.key() == Qt.Key_Down:
                        print(f"[DEBUG] Down arrow pressed in party search Sales")
                        if not self.party_completer.popup().isVisible():
                            # Show all items in dropdown
                            self.party_search.showPopup()
                            return True
                        # If popup is visible, let default behavior navigate the list
                    
                    # Tab or Enter key: confirm current selection and move to product search
                    elif event.key() in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
                        # If completer popup is visible and Enter is pressed, 
                        # let QCompleter handle it - it will select the highlighted item and emit activated signal
                        if self.party_completer.popup().isVisible() and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                            # Return False to let QCompleter process the Enter key
                            # This will select the highlighted item and emit the activated signal
                            # which calls _on_party_completer_activated automatically
                            return False
                        
                        # For Tab key or when popup is not visible, validate and move to product search
                        text = self.party_search.lineEdit().text().strip()  # Use lineEdit().text() for read-only compatibility
                        if text:
                            # Check if it's a valid party
                            party_name = self.party_display_map.get(text, text)
                            if party_name in self.party_data_map:
                                # If party not yet processed, process it now
                                if not hasattr(self, '_party_selection_processed'):
                                    self._on_party_completer_activated(text)
                                    self._party_selection_processed = True
                                else:
                                    # Clear flag for next selection
                                    self._party_selection_processed = False
                                
                                # Move focus to first item's product search
                                self._focus_on_product_search()
                                return True  # Block default behavior
                            else:
                                # Show error for invalid party
                                self._show_party_error("Please select a valid party from the list")
                                return True  # Block key
                        return False  # Allow event to propagate if text is empty
                    
                    # Escape key: close dropdown first, then clear selection
                    elif event.key() == Qt.Key_Escape:
                        if self.party_completer.popup().isVisible():
                            self.party_completer.popup().hide()
                            return True
                        else:
                            # Clear selection and show all options
                            self._clear_party_selection()
                            return True
        except Exception as e:
            print(f"Event filter error: {e}")
        
        return super().eventFilter(obj, event)

    def _setup_completer_positioning(self):
        """Setup completer to position correctly when showing (prevents flickering)."""
        try:
            if hasattr(self, 'party_completer'):
                popup = self.party_completer.popup()
                dialog_ref = self  # Reference to use in closure
                
                # Override setVisible because QCompleter uses this internally (not show())
                original_setVisible = popup.setVisible
                def custom_setVisible(visible):
                    original_setVisible(visible)
                    if visible:
                        # Position AFTER showing so geometry is correct
                        dialog_ref._position_completer_popup()
                popup.setVisible = custom_setVisible
        except Exception as e:
            print(f"Setup completer positioning error: {e}")

    def _position_completer_popup(self):
        """Position the completer popup with dynamic screen-aware positioning.
        This is the SINGLE positioning method used for all popup displays.
        """
        try:
            if not hasattr(self, 'party_completer'):
                return
                
            popup = self.party_completer.popup()
            
            # Get the combobox position in global coordinates
            combo_rect = self.party_search.rect()
            global_pos = self.party_search.mapToGlobal(combo_rect.bottomLeft())
            
            # Set popup width (wider to show balance info)
            popup_width = max(self.party_search.width(), PARTY_COMPLETER_POPUP_MIN_WIDTH)
            popup.setFixedWidth(popup_width)
            
            # Calculate position - use bottomLeft() so we start BELOW the search box
            gap = PARTY_COMPLETER_POPUP_GAP_FROM_INPUT  # Small gap between search box and popup
            y_pos = global_pos.y() + gap
            x_pos = global_pos.x()
            
            # Get screen geometry for bounds checking
            screen = QApplication.screenAt(global_pos)
            if screen:
                screen_geometry = screen.availableGeometry()
                popup_height = min(popup.sizeHint().height(), PARTY_COMPLETER_POPUP_MAX_HEIGHT)  # Max 400px height
                
                # Check if popup would go below screen - position above instead
                if y_pos + popup_height > screen_geometry.bottom():
                    # Position above the search box
                    top_pos = self.party_search.mapToGlobal(combo_rect.topLeft())
                    y_pos = top_pos.y() - popup_height - gap
                
                # Check if popup would go off right edge
                if x_pos + popup_width > screen_geometry.right():
                    x_pos = screen_geometry.right() - popup_width - 10
            
            # Move popup to calculated position
            popup.move(x_pos, y_pos)
        except Exception as e:
            print(f"Position completer popup error: {e}")

    def _get_recent_party_ids(self) -> list:
        """Get IDs of recently used parties from invoices (last 5 unique parties).
        
        Delegates to invoice_form_controller which uses InvoiceService for database access.
        """
        try:
            return invoice_form_controller.get_recent_party_ids(limit=5)
        except Exception as e:
            print(f"Error getting recent party IDs: {e}")
            return []

    def _get_recent_product_ids(self) -> list:
        """Get IDs of recently used products from invoice items (last 10 unique products).
        
        Delegates to invoice_form_controller which uses InvoiceService for database access.
        """
        try:
            return invoice_form_controller.get_recent_product_ids(limit=10)
        except Exception as e:
            print(f"Error getting recent product IDs: {e}")
            return []

    def _get_tax_type(self) -> str:
        """Get the normalized tax type from the segmented button state.
        
        Converts internal state to format expected by database:
        - 'SAME_STATE' -> 'GST - Same State'
        - 'OTHER_STATE' -> 'GST - Other State'  
        - 'NON_GST' -> 'Non-GST'
        """
        if not hasattr(self, '_tax_type'):
            return 'GST - Same State'
        
        tax_type_map = {
            'SAME_STATE': 'GST - Same State',
            'OTHER_STATE': 'GST - Other State',
            'NON_GST': 'Non-GST'
        }
        return tax_type_map.get(self._tax_type, 'GST - Same State')

    def on_invoice_type_changed(self, invoice_type: str):
        """Update tax display and totals when invoice type changes.
        
        For Non-GST invoices, tax is shown as 0 in totals.
        For GST invoices, tax splits into CGST/SGST (Same State) or IGST (Other State).
        """
        try:
            # Update overall totals (which handles tax display based on invoice type)
            self.update_totals()
        except Exception as e:
            print(f"Invoice type change handler error: {e}")

    def on_bill_type_changed(self, bill_type: str):
        """Show/hide Balance Due based on bill type"""
        try:
            # Update totals to reflect bill type visibility changes
            self.update_totals()
        except Exception as e:
            print(f"Bill type change handler error: {e}")

    def _apply_billtype_style(self):
        """Apply the correct style to bill type toggle button based on current state with improved styling."""
        try:
            if not hasattr(self, 'billtype_btn'):
                return
            if self._bill_type == "CASH":
                self.billtype_btn.setText("💵 CASH")
                self.billtype_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10B981, stop:1 #059669);
                        color: {WHITE};
                        border: 2px solid #059669;
                        border-radius: 6px;
                        padding: 8px 14px;
                        font-size: 13px;
                        font-weight: bold;
                        outline: none;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #047857);
                    }}
                    QPushButton:pressed {{
                        background: #047857;
                    }}
                    QPushButton:disabled {{
                        background: #6EE7B7;
                        color: #D1FAE5;
                        border: 2px solid #A7F3D0;
                    }}
                """)
            else:
                self.billtype_btn.setText("📝 CREDIT")
                self.billtype_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EF4444, stop:1 #DC2626);
                        color: {WHITE};
                        border: 2px solid #DC2626;
                        border-radius: 6px;
                        padding: 8px 14px;
                        font-size: 13px;
                        font-weight: bold;
                        outline: none;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #DC2626, stop:1 #B91C1C);
                    }}
                    QPushButton:pressed {{
                        background: #B91C1C;
                    }}
                    QPushButton:disabled {{
                        background: #FCA5A5;
                        color: #FEE2E2;
                        border: 2px solid #FECACA;
                    }}
                """)
        except Exception as e:
            print(f"Bill type style error: {e}")

    def _toggle_bill_type(self):
        """Toggle between CASH and CREDIT bill types."""
        try:
            self._bill_type = "CREDIT" if self._bill_type == "CASH" else "CASH"
            self._apply_billtype_style()
            # Update totals when bill type changes (for Balance Due visibility)
            if hasattr(self, 'items_layout'):
                self.update_totals()
        except Exception as e:
            print(f"Bill type toggle error: {e}")

    def _set_tax_type(self, tax_type: str):
        """Set the tax type and update button styles.
        
        Args:
            tax_type: One of 'SAME_STATE', 'OTHER_STATE', 'NON_GST'
        """
        try:
            self._tax_type = tax_type
            self._apply_tax_type_styles()
            
            # Update all item rows - set tax field read-only for Non-GST
            # and recalculate tax amounts based on new tax type
            if hasattr(self, 'items_layout'):
                is_non_gst = (tax_type == "NON_GST")
                for i in range(self.items_layout.count()):
                    widget = self.items_layout.itemAt(i).widget()
                    if widget and hasattr(widget, 'set_tax_readonly'):
                        widget.set_tax_readonly(is_non_gst, set_to_zero=is_non_gst)
                    
                    # Update tax rate for each item based on new tax type
                    if isinstance(widget, InvoiceItemWidget):
                        widget.update_tax_for_type_change(tax_type)
                
                # Update totals when tax type changes
                self.update_totals()
                            
            # Trigger invoice type change handler for item tax rates
            self.on_invoice_type_changed(self._get_tax_type())
        except Exception as e:
            print(f"Set tax type error: {e}")

    def _apply_tax_type_styles(self):
        """Apply styles to tax type segment buttons based on current selection with proper segmentation."""
        try:
            if not hasattr(self, '_tax_buttons'):
                return
            
            # Define colors for each type - all as tuples (bg_color, hover_color)
            colors = {
                "SAME_STATE": ("#3B82F6", "#2563EB"),   # Blue
                "OTHER_STATE": ("#F59E0B", "#D97706"),  # Orange
                "NON_GST": ("#6B7280", "#4B5563")       # Gray
            }
            
            for btn_type, btn in self._tax_buttons.items():
                if btn_type == self._tax_type:
                    # Selected style - use the appropriate color with gradient
                    bg_color, hover_color = colors.get(btn_type, ("#3B82F6", "#2563EB"))
                    
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {bg_color}, stop:1 {hover_color});
                            color: {WHITE};
                            border: none;
                            padding: 6px 12px;
                            font-size: 12px;
                            font-weight: bold;
                            outline: none;
                        }}
                        QPushButton:hover {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {hover_color}, stop:1 {hover_color});
                        }}
                        QPushButton:pressed {{
                            background: {hover_color};
                        }}
                    """)
                else:
                    # Unselected style - light gray with border
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: {WHITE};
                            color: {TEXT_PRIMARY};
                            border: 1px solid {BORDER};
                            padding: 6px 12px;
                            font-size: 12px;
                            font-weight: 500;
                            outline: none;
                        }}
                        QPushButton:hover {{
                            background: {PRIMARY_LIGHT};
                            border: 1px solid {PRIMARY};
                            color: {PRIMARY};
                        }}
                        QPushButton:pressed {{
                            background: {PRIMARY_LIGHT};
                        }}
                    """)
        except Exception as e:
            print(f"Tax type style error: {e}")

    def toggle_header_compact(self) -> None:
        """Toggle between compact and expanded header modes."""
        try:
            self._header_expanded = not self._header_expanded
            
            # Get all box containers in header
            boxes_to_toggle = [
                'billTypeBox',
                'taxTypeBox', 
                'invoiceDateBox',
                'invoiceNumberBox'
            ]
            
            for box_name in boxes_to_toggle:
                if hasattr(self, 'header_frame'):
                    # Find widget by object name
                    box_widget = self.header_frame.findChild(QWidget, box_name)
                    if box_widget:
                        box_widget.setVisible(self._header_expanded)
            
            # Adjust header height based on mode
            if hasattr(self, 'header_frame'):
                if self._header_expanded:
                    self.header_frame.setMinimumHeight(160)
                    self.header_frame.setMaximumHeight(240)
                else:
                    # Compact mode: only show party selection
                    self.header_frame.setMinimumHeight(120)
                    self.header_frame.setMaximumHeight(140)
            
        except Exception as e:
            print(f"Error toggling header compact mode: {e}")

    def create_items_section(self):
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 15))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*ITEMS_LAYOUT_MARGINS)
        layout.setSpacing(ITEMS_LAYOUT_SPACING)

        # Quick Products Section - Show recently used products as clickable chips
        quick_products_layout = QHBoxLayout()
        quick_products_layout.setSpacing(QUICK_PRODUCTS_LAYOUT_SPACING)
        quick_products_layout.setContentsMargins(*QUICK_PRODUCTS_LAYOUT_MARGINS)
        quick_products_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        quick_label = QLabel("⚡ Quick Add Products:")
        quick_label.setStyleSheet(get_form_label_style(QUICK_PRODUCTS_LABEL_SIZE, "bold", TEXT_SECONDARY))
        quick_products_layout.addWidget(quick_label)
        
        # Get recently used products from invoices
        recent_product_ids = self._get_recent_product_ids()
        
        # Get top 5 products - prioritize recently used, then by popularity
        recent_products = [p for p in self.products if p.get('id') in recent_product_ids][:QUICK_PRODUCTS_RECENT_COUNT]
        other_products = [p for p in self.products if p.get('id') not in recent_product_ids]
        other_products = sorted(other_products[:8], key=lambda x: x.get('sales_rate', 0), reverse=True)[:QUICK_PRODUCTS_POPULAR_COUNT]
        top_products = recent_products + other_products
        
        for i, product in enumerate(top_products):
            chip = QPushButton(product.get('name', '')[:20])  # Truncate long names
            chip.setFixedHeight(QUICK_PRODUCT_CHIP_HEIGHT)
            chip.setMinimumWidth(QUICK_PRODUCT_CHIP_MIN_WIDTH)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setFocusPolicy(Qt.NoFocus)  # Prevent keyboard focus - only mouse clicks
            
            # Show stock in tooltip
            stock = product.get('opening_stock', 0) or 0
            price = product.get('sales_rate', 0) or 0
            stock_text = f"Stock: {stock}" if stock > 0 else "Out of Stock"
            chip.setToolTip(f"Add {product.get('name', '')}\n₹{price:,.2f} | {stock_text}")
            
            # Use different style for recently used products
            is_recent = product.get('id') in recent_product_ids
            chip.setStyleSheet(get_quick_chip_recent_style() if is_recent else get_quick_chip_style())
            
            # Store product data in the button
            chip.product_data = product
            chip.clicked.connect(lambda checked, p=product: self.quick_add_product(p))
            quick_products_layout.addWidget(chip)
        
        quick_products_layout.addStretch()

        # Items count badge at right corner of Quick Add row
        items_label = QLabel("📦")
        items_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        quick_products_layout.addWidget(items_label)
        
        self.item_count_badge = QLabel("0")
        self.item_count_badge.setFixedSize(48, 32)
        self.item_count_badge.setAlignment(Qt.AlignCenter)
        self.item_count_badge.setStyleSheet(get_item_count_badge_style(0))
        quick_products_layout.addWidget(self.item_count_badge)

        layout.addLayout(quick_products_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        layout.addWidget(separator)

        # Column Headers - Clean design without emojis
        headers_layout = QHBoxLayout()
        headers_layout.setSpacing(HEADERS_LAYOUT_SPACING)
        headers_layout.setContentsMargins(*HEADERS_LAYOUT_MARGINS)
        
        # Clean uppercase headers
        # Widths match InvoiceItemWidget exactly
        headers = [
            "NO", "PRODUCT", "HSN", "QTY", "UNIT",
            "RATE", "DISC%", "TAX%", "AMOUNT", ""
        ]
        widths = [HEADER_COLUMN_NO_WIDTH, HEADER_COLUMN_PRODUCT_WIDTH, HEADER_COLUMN_HSN_WIDTH,
                  HEADER_COLUMN_QTY_WIDTH, HEADER_COLUMN_UNIT_WIDTH, HEADER_COLUMN_RATE_WIDTH,
                  HEADER_COLUMN_DISC_WIDTH, HEADER_COLUMN_TAX_WIDTH, HEADER_COLUMN_AMOUNT_WIDTH, HEADER_COLUMN_ACTION_WIDTH]
        for header, width in zip(headers, widths):
            label = QLabel(header)
            label.setFixedWidth(width)
            label.setFixedHeight(HEADER_LABEL_HEIGHT)
            label.setStyleSheet(get_items_header_label_style())
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)
        layout.addLayout(headers_layout)
        
        # Empty state message (shown when no items) - Improved UX
        self.empty_state_label = QLabel(
            "📦 No items added yet\n"
            "Click on a quick product above or search for products below to get started."
        )
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 13px;
                padding: 40px 20px;
                background: {BACKGROUND};
                border: 2px dashed {BORDER};
                border-radius: 8px;
                font-weight: 500;
            }}
        """)
        self.empty_state_label.setMinimumHeight(EMPTY_STATE_MIN_HEIGHT)
        layout.addWidget(self.empty_state_label)

        # Items scroll area with improved styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                background: {WHITE};
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: {BACKGROUND};
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {TEXT_SECONDARY};
            }}
        """)
        
        self.items_widget = QWidget()
        self.items_widget.setStyleSheet(f"background: {WHITE};")
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(ITEMS_CONTAINER_SPACING)
        self.items_layout.setContentsMargins(*ITEMS_CONTAINER_MARGINS)
        self.items_layout.addStretch()
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area, 1)  # Stretch to fill
        
        return frame

    def create_totals_section(self):
        """Create enhanced totals section with improved layout and features.
        
        Features:
        - Visible subtotal row
        - Invoice-level discount (% or flat)
        - Other charges (shipping, packaging, etc.)
        - Tax with expandable breakdown (CGST/SGST or IGST)
        - Round-off as separate row
        - Grand Total with visual separation
        - Paid Amount field for CREDIT invoices
        - Dynamic Balance Due with color-coded styling
        - Amount in words
        - Notes section
        """
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 12))
        frame.setMinimumHeight(TOTALS_SECTION_MIN_HEIGHT)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(*TOTALS_LAYOUT_MARGINS)
        layout.setSpacing(TOTALS_LAYOUT_SPACING)


        # ========== LEFT SIDE: Notes & Amount in Words ==========
        left_container = QVBoxLayout()
        left_container.setSpacing(LEFT_CONTAINER_SPACING)
        
        # Notes area with icon
        add_note_link = QLabel("📝 <a href='add' style='text-decoration: none;'>Add Note</a>")
        add_note_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_note_link.setOpenExternalLinks(False)
        add_note_link.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                font-size: 13px;
                font-weight: 600;
                border: none;
                outline: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }}
            QLabel:hover {{
                color: {PRIMARY_HOVER};
            }}
        """)
        add_note_link.setCursor(Qt.PointingHandCursor)
        
        # Handler to create/show notes editor lazily
        def _handle_add_note_link(_):
            try:
                if not hasattr(self, 'notes') or self.notes is None:
                    self.notes = QTextEdit()
                    self.notes.setPlaceholderText("Add any additional information, terms, or special instructions...")
                    self.notes.setStyleSheet(f"""
                        QTextEdit {{
                            border: 2px solid {BORDER}; 
                            border-radius: 8px; 
                            padding: 10px; 
                            background: {WHITE}; 
                            font-size: 13px;
                            color: {TEXT_PRIMARY};
                        }}
                        QTextEdit:focus {{
                            border: 2px solid {PRIMARY};
                        }}
                    """)
                    self.notes.setFixedHeight(NOTES_FIELD_HEIGHT)
                    self.notes.setMaximumWidth(400)
                    left_container.insertWidget(1, self.notes)
                    add_note_link.setText("📝 <a href='hide' style='text-decoration: none;'>Hide Note</a>")
                else:
                    if self.notes.isVisible():
                        self.notes.setVisible(False)
                        add_note_link.setText("📝 <a href='add' style='text-decoration: none;'>Add Note</a>")
                    else:
                        self.notes.setVisible(True)
                        add_note_link.setText("📝 <a href='hide' style='text-decoration: none;'>Hide Note</a>")
            except Exception as e:
                print(f"Failed to toggle notes editor: {e}")
        
        add_note_link.linkActivated.connect(_handle_add_note_link)
        left_container.addWidget(add_note_link)

        # Initialize notes as None
        if not hasattr(self, 'notes'):
            self.notes = None
        
        # Amount in words section - more prominent with better styling
        amount_words_container = QVBoxLayout()
        amount_words_container.setSpacing(AMOUNT_WORDS_CONTAINER_SPACING)
        
        amount_words_title = QLabel("💰 Amount in Words:")
        amount_words_title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: bold;
                border: none;
                outline: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }}
        """)
        amount_words_container.addWidget(amount_words_title)
        
        self.amount_in_words_label = QLabel("Zero Rupees Only")
        self.amount_in_words_label.setWordWrap(True)
        self.amount_in_words_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-style: italic;
                font-weight: 500;
                color: {PRIMARY_DARK};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EFF6FF, stop:1 #DBEAFE);
                border-radius: 6px;
                padding: 12px 14px;
            }}
        """)
        self.amount_in_words_label.setMinimumWidth(AMOUNT_WORDS_LABEL_MIN_WIDTH)
        self.amount_in_words_label.setMaximumWidth(600)
        self.amount_in_words_label.setMinimumHeight(AMOUNT_WORDS_LABEL_MIN_HEIGHT)
        amount_words_container.addWidget(self.amount_in_words_label)
        
        left_container.addLayout(amount_words_container)
        left_container.addStretch()
        layout.addLayout(left_container)

        layout.addStretch()
        # ========== RIGHT SIDE: Totals Grid ==========
        totals_container = QVBoxLayout()
        # totals_container.setAlignment(Qt.AlignRight)
        totals_container.setSpacing(AMOUNT_WORDS_CONTAINER_SPACING)
        
        # Use Grid Layout for better alignment
        from PySide6.QtWidgets import QGridLayout
        self.totals_grid = QGridLayout()
        self.totals_grid.setSpacing(TOTALS_GRID_SPACING)
        self.totals_grid.setContentsMargins(*TOTALS_GRID_MARGINS)
        self.totals_grid.setAlignment(Qt.AlignRight)

        # Fixed widths for alignment
        LABEL_WIDTH = 120
        VALUE_WIDTH = 140
        ROW_HEIGHT = 32
        
        row_idx = 0
        
        # ---- ROW 1: Subtotal ----
        self.subtotal_row_label = QLabel("Subtotal:")
        self.subtotal_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.subtotal_row_label.setFixedWidth(TOTALS_LABEL_WIDTH)
        self.subtotal_row_label.setFixedHeight(TOTALS_ROW_HEIGHT)
        self.subtotal_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.subtotal_row_label, row_idx, 0)
        
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                background: transparent;
                padding: 4px 8px;
            }}
        """)
        self.subtotal_label.setFixedWidth(VALUE_WIDTH)
        self.subtotal_label.setFixedHeight(ROW_HEIGHT)
        self.subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.subtotal_label, row_idx, 1)
        row_idx += 1
        
        # ---- ROW 2: Discount (visible when there's discount) ----
        self.invoice_discount_row_label = QLabel("Discount:")
        self.invoice_discount_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.invoice_discount_row_label.setFixedWidth(LABEL_WIDTH)
        self.invoice_discount_row_label.setFixedHeight(ROW_HEIGHT)
        self.invoice_discount_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.invoice_discount_row_label, row_idx, 0)
        
        # Discount value display
        self.discount_label = QLabel("-₹0.00")
        self.discount_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {DANGER};
                background: transparent;
                padding: 4px 8px;
            }}
        """)
        self.discount_label.setFixedWidth(VALUE_WIDTH)
        self.discount_label.setFixedHeight(ROW_HEIGHT)
        self.discount_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.discount_label, row_idx, 1)
        
        # Initially hide discount row (shown when there's discount)
        self.invoice_discount_row_label.setVisible(False)
        self.discount_label.setVisible(False)
        row_idx += 1
        
        # ---- ROW 4: Tax ----
        self.tax_row_label = QLabel("Tax:")
        self.tax_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.tax_row_label.setFixedWidth(LABEL_WIDTH)
        self.tax_row_label.setFixedHeight(ROW_HEIGHT)
        self.tax_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.tax_row_label, row_idx, 0)
        
        # Tax container with horizontal layout showing all tax info
        tax_container = QWidget()
        tax_container.setStyleSheet("background: transparent;")
        tax_layout = QHBoxLayout(tax_container)
        tax_layout.setContentsMargins(0, 0, 0, 0)
        tax_layout.setSpacing(12)
        
        # Tax amount box
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: #059669;
                background: #ECFDF5;
                border: 1px solid #A7F3D0;
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)
        self.tax_label.setFixedWidth(VALUE_WIDTH)
        self.tax_label.setFixedHeight(ROW_HEIGHT)
        self.tax_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.tax_label.setWordWrap(False)
        tax_layout.addWidget(self.tax_label)
        
        # Tax breakdown label (CGST + SGST or IGST)
        self.tax_breakdown_label = QLabel("")
        self.tax_breakdown_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
                padding: 2px 0px;
            }}
        """)
        self.tax_breakdown_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.tax_breakdown_label.setMinimumWidth(200)
        tax_layout.addWidget(self.tax_breakdown_label)
        # tax_layout.addStretch()
        
        self.totals_grid.addWidget(tax_container, row_idx, 1)
        row_idx += 1
        
        # Hidden GST breakdown labels (for backward compatibility - values still calculated)
        self.cgst_label = QLabel("₹0.00")
        self.cgst_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 500;
                color: {DANGER};
                background: transparent;
                padding: 2px 0px;
            }}
        """)
        self.cgst_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.cgst_label.setMinimumWidth(120)
        self.cgst_label.setVisible(False)
        self.sgst_label = QLabel("₹0.00")
        self.sgst_label.setVisible(False)
        self.igst_label = QLabel("₹0.00")
        self.igst_label.setVisible(False)
        self.tax_breakdown_box = QLabel("")
        self.tax_breakdown_box.setVisible(False)
        
        # ---- SEPARATOR before Grand Total ----
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        # self.totals_grid.addWidget(separator, row_idx, 0, 1, 2)
        row_idx += 1
        
        # ---- ROW 5: Grand Total (PROMINENT) ----
        self.grand_total_row_label = QLabel("GRAND TOTAL:")
        self.grand_total_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {PRIMARY};
                background: transparent;
            }}
        """)
        self.grand_total_row_label.setFixedWidth(LABEL_WIDTH)
        self.grand_total_row_label.setFixedHeight(ROW_HEIGHT + 8)
        self.grand_total_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.grand_total_row_label, row_idx, 0)
        
        # Grand total with prominent styling - blue gradient box
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {WHITE};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {PRIMARY}, stop:1 {PRIMARY_DARK});
                border: 2px solid {PRIMARY_DARK};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)
        self.grand_total_label.setFixedWidth(VALUE_WIDTH)
        self.grand_total_label.setFixedHeight(ROW_HEIGHT + 8)
        self.grand_total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.grand_total_label, row_idx, 1)
        row_idx += 1
        
        # ---- ROW 6: Balance Due (with dynamic color) ----
        self.balance_row_label = QLabel("BALANCE DUE:")
        self.balance_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: bold;
                color: #F59E0B;
                background: transparent;
            }}
        """)
        self.balance_row_label.setFixedWidth(LABEL_WIDTH)
        self.balance_row_label.setFixedHeight(ROW_HEIGHT + 4)
        self.balance_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.balance_row_label, row_idx, 0)
        
        # Balance due with dynamic styling (changes color based on amount)
        self.balance_label = QLabel("₹0.00")
        self.balance_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                background: #F59E0B;
                border: 1px solid #D97706;
                border-radius: 4px;
                padding: 6px 10px;
            }}
        """)
        self.balance_label.setFixedWidth(VALUE_WIDTH)
        self.balance_label.setFixedHeight(ROW_HEIGHT + 4)
        self.balance_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.balance_label, row_idx, 1)
        
        # Initially hide balance due row (shown for CREDIT)
        self.balance_row_label.setVisible(False)
        self.balance_label.setVisible(False)
        row_idx += 1
        
        # ---- ROW 7: Roundoff (visible when grand_total has decimals) ----
        self.roundoff_row_label = QLabel("Roundoff:")
        self.roundoff_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.roundoff_row_label.setFixedWidth(LABEL_WIDTH)
        self.roundoff_row_label.setFixedHeight(ROW_HEIGHT)
        self.roundoff_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.roundoff_row_label, row_idx, 0)
        
        # Roundoff value display with clickable link for options
        self.roundoff_link = QLabel("<a href='options' style='text-decoration: none; color: #3B82F6;'>₹0.00 ▼</a>")
        self.roundoff_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.roundoff_link.setOpenExternalLinks(False)
        self.roundoff_link.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: #3B82F6;
                background: transparent;
                padding: 4px 8px;
            }}
            QLabel:hover {{
                color: #2563EB;
            }}
        """)
        self.roundoff_link.setFixedWidth(VALUE_WIDTH)
        self.roundoff_link.setFixedHeight(ROW_HEIGHT)
        self.roundoff_link.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.roundoff_link.setCursor(Qt.PointingHandCursor)
        self.roundoff_link.setToolTip("Click to round up/down")
        self.roundoff_link.linkActivated.connect(self.show_roundoff_options)
        self.totals_grid.addWidget(self.roundoff_link, row_idx, 1)
        
        # Initially hide roundoff row (shown when decimal exists)
        self.roundoff_row_label.setVisible(False)
        self.roundoff_link.setVisible(False)
        self.roundoff_amount = 0.0
        row_idx += 1
        
        # ---- ROW 8: Paid Amount (visible only for CREDIT invoices) ----
        self.paid_row_label = QLabel("Paid Amount:")
        self.paid_row_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {TEXT_SECONDARY};
                background: transparent;
            }}
        """)
        self.paid_row_label.setFixedWidth(LABEL_WIDTH)
        self.paid_row_label.setFixedHeight(ROW_HEIGHT)
        self.paid_row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.totals_grid.addWidget(self.paid_row_label, row_idx, 0)
        
        # Paid amount input field with currency prefix
        self.paid_amount_spin = QDoubleSpinBox()
        self.paid_amount_spin.setRange(0, 999999999)
        self.paid_amount_spin.setDecimals(2)
        self.paid_amount_spin.setPrefix("₹")
        self.paid_amount_spin.setValue(0)
        self.paid_amount_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 2px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                background: {WHITE};
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid {PRIMARY};
            }}
        """)
        self.paid_amount_spin.setFixedWidth(VALUE_WIDTH)
        self.paid_amount_spin.setFixedHeight(ROW_HEIGHT)
        self.paid_amount_spin.valueChanged.connect(self.update_balance_due)
        self.totals_grid.addWidget(self.paid_amount_spin, row_idx, 1)
        
        # Initially hide paid amount row (shown only for CREDIT)
        self.paid_row_label.setVisible(False)
        self.paid_amount_spin.setVisible(False)
        row_idx += 1
        
        # Note: Discount row and other charge rows are already properly added to the grid above.
        # These old container variables are kept only for backward compatibility.
        # They should NOT be set to visible() as they're orphan widgets.
        
        # Backward compatibility: Create invoice discount spin (not used in new grid layout)
        self.invoice_discount_spin = QDoubleSpinBox()
        self.invoice_discount_spin.setVisible(False)
        self.invoice_discount_type = QComboBox()
        self.invoice_discount_type.setVisible(False)
        
        # Backward compatibility: Other charges fields
        self.other_charges_row_label = QLabel("")
        self.other_charges_row_label.setVisible(False)
        self.other_charges_spin = QDoubleSpinBox()
        self.other_charges_spin.setVisible(False)
        self.other_charges_type_label = QLabel("")
        self.other_charges_type_label.setVisible(False)
        
        # Backward compatibility: Roundoff value label
        self.roundoff_value_label = QLabel("₹0.00")
        self.roundoff_value_label.setVisible(False)
        
        # Also create items_subtotal_label for backward compatibility
        self.items_subtotal_label = QLabel("₹0.00")
        self.items_subtotal_label.setVisible(False)
        
        totals_container.addLayout(self.totals_grid)
        totals_container.addStretch()
        
        layout.addLayout(totals_container, 1)
        
        return frame

    def _toggle_discount_row(self, link=None):
        """Toggle visibility of invoice-level discount row - disabled in simplified mode"""
        pass

    def _toggle_charges_row(self, link=None):
        """Toggle visibility of other charges row - disabled in simplified mode"""
        pass

    def _show_charge_label_popup(self, link=None):
        """Show popup to select charge type label"""
        try:
            menu = QMenu(self)
            menu.setStyleSheet(get_context_menu_style())
            
            charge_types = ["Shipping", "Packaging", "Handling", "Delivery", "Service Charge", "Other"]
            for charge_type in charge_types:
                action = QAction(charge_type, self)
                action.triggered.connect(lambda checked, ct=charge_type: self._set_charge_label(ct))
                menu.addAction(action)
            
            # Show at cursor position
            menu.exec_(QApplication.instance().activeWindow().cursor().pos())
        except Exception as e:
            print(f"Show charge label popup error: {e}")

    def _set_charge_label(self, label: str):
        """Set the label for other charges"""
        try:
            self.other_charges_type_label.setText(f"({label})")
            self.other_charges_type_label.setVisible(True)
            self.other_charges_row_label.setText(f"(+) {label}:")
        except Exception as e:
            print(f"Set charge label error: {e}")

    def _on_invoice_discount_changed(self):
        """Handle invoice-level discount changes"""
        try:
            self.update_totals()
        except Exception as e:
            print(f"Invoice discount change error: {e}")

    def show_roundoff_options(self, link=None):
        """Show popup with round-off options (up/down)"""
        try:
            grand_total = float(self.grand_total_label.text().replace('₹','').replace(',',''))
            
            # Calculate round down and round up values
            round_down = int(grand_total)
            round_up = round_down + 1 if grand_total > round_down else round_down
            
            diff_down = grand_total - round_down
            diff_up = round_up - grand_total
            
            # Create popup menu with minimum width
            menu = QMenu(self)
            menu.setMinimumWidth(180)
            menu.setStyleSheet(get_context_menu_style())
            
            # Round down option - shorter text
            down_action = QAction(f"⬇ Down (-₹{diff_down:.2f})", self)
            down_action.triggered.connect(lambda: self.apply_roundoff(-diff_down, round_down))
            menu.addAction(down_action)
            
            # Round up option - shorter text
            up_action = QAction(f"⬆ Up (+₹{diff_up:.2f})", self)
            up_action.triggered.connect(lambda: self.apply_roundoff(diff_up, round_up))
            menu.addAction(up_action)
            
            # No rounding option
            no_round_action = QAction("✕ No Rounding", self)
            no_round_action.triggered.connect(lambda: self.apply_roundoff(0, grand_total))
            menu.addAction(no_round_action)
            
            # Show menu at link position
            menu.exec_(self.roundoff_link.mapToGlobal(self.roundoff_link.rect().bottomLeft()))
            
        except Exception as e:
            print(f"Error showing roundoff options: {e}")

    def apply_roundoff(self, roundoff_amount, final_total):
        """Apply the selected round-off amount"""
        try:
            # Round to 2 decimal places to avoid floating point precision issues
            self.roundoff_amount = round(roundoff_amount, 2)
            
            if self.roundoff_amount > 0:
                self.roundoff_value_label.setText(f"+₹{self.roundoff_amount:.2f}")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style())
            elif self.roundoff_amount < 0:
                self.roundoff_value_label.setText(f"-₹{abs(self.roundoff_amount):.2f}")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style())
            else:
                self.roundoff_value_label.setText("₹0.00")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style())
            
            # Update grand total with rounded value
            self.grand_total_label.setText(f"₹{final_total:,.2f}")
            
            # Update amount in words via controller
            if hasattr(self, 'amount_in_words_label'):
                self.amount_in_words_label.setText(
                    invoice_form_controller.number_to_words_indian(final_total)
                )
            
            # Update balance due
            self.update_balance_due()
            
        except Exception as e:
            print(f"Error applying roundoff: {e}")

    def update_balance_due(self):
        """Update balance due with dynamic color-coded styling based on amount."""
        try:
            grand_total = 0.0
            try:
                grand_total = float(self.grand_total_label.text().replace('₹', '').replace(',', ''))
            except Exception:
                pass
            
            paid = self.paid_amount_spin.value()
            balance = max(0, grand_total - paid)
            
            # Update balance label text
            if balance <= 0:
                balance_text = "✓ PAID"
                balance_color_bg = "#10B981"  # Green - Paid
                balance_color_border = "#059669"
                balance_color_text = WHITE
                label_color = "#059669"
            elif balance < 100:
                # Small balance - Light orange
                balance_text = f"₹{balance:,.2f}"
                balance_color_bg = "#FCD34D"
                balance_color_border = "#F59E0B"
                balance_color_text = "#78350F"
                label_color = "#D97706"
            elif balance < 1000:
                # Medium balance - Orange
                balance_text = f"₹{balance:,.2f}"
                balance_color_bg = "#F59E0B"
                balance_color_border = "#D97706"
                balance_color_text = WHITE
                label_color = "#D97706"
            else:
                # Large balance - Red
                balance_text = f"₹{balance:,.2f}"
                balance_color_bg = "#EF4444"
                balance_color_border = "#DC2626"
                balance_color_text = WHITE
                label_color = "#DC2626"
            
            # Update balance label with dynamic styling
            self.balance_label.setText(balance_text)
            self.balance_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    font-weight: bold;
                    color: {balance_color_text};
                    background: {balance_color_bg};
                    border: 1px solid {balance_color_border};
                    border-radius: 4px;
                    padding: 6px 10px;
                }}
            """)
            
            # Update balance row label color to match
            self.balance_row_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    font-weight: bold;
                    color: {label_color};
                    background: transparent;
                    padding: 4px 0;
                }}
            """)
                
        except Exception as e:
            print(f"Update balance due error: {e}")
            self.balance_label.setText("₹0.00")

    # Items management
    def quick_add_product(self, product_data):
        """Quickly add a product to the invoice from the quick-select chips with duplicate detection."""
        try:
            # Check if party is selected first
            if hasattr(self, 'party_search'):
                party_text = self.party_search.text().strip()
                if not party_text:
                    highlight_error(self.party_search, "Please select a party first")
                    self.party_search.setFocus()
                    return
            
            product_id = product_data.get('id')
            product_name = product_data.get('name', '')
            
            # Check if this product already exists in any row
            existing_item_widget = None
            for i in range(self.items_layout.count() - 1):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    if hasattr(widget, 'product_input') and widget.product_input.currentText().strip() == product_name:
                        existing_item_widget = widget
                        break
            
            # If product exists, increment quantity instead of adding new row
            if existing_item_widget:
                # Increment quantity by 1
                current_qty = existing_item_widget.quantity_spin.value()
                existing_item_widget.quantity_spin.setValue(current_qty + 1)
                
                # Show brief highlight with feedback
                highlight_success(existing_item_widget, f"📌 Qty increased to {current_qty + 1}")
                return
            
            # Check if there's an empty first row that we can fill instead of creating new
            first_item_widget = None
            for i in range(self.items_layout.count()):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    first_item_widget = widget
                    break
            
            # If first row exists and has no product selected, fill it instead of creating new row
            if first_item_widget and not first_item_widget.product_input.currentText().strip():
                item_widget = first_item_widget
            else:
                # Create a new item widget with the product pre-selected
                item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                item_widget.add_requested.connect(self.add_item)
                item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
                item_widget.remove_requested.connect(self._handle_remove_request)  # Ctrl+Delete support
                item_widget.item_changed.connect(self.update_totals)
                item_widget.setStyleSheet(get_item_widget_normal_style())
                # Add to layout
                self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
            
            # Pre-fill with the product data using set_product_by_data method
            item_widget.set_product_by_data(product_data)
            
            # Set tax based on invoice type
            if hasattr(self, '_tax_type') and self._tax_type == "NON_GST":
                item_widget.tax_spin.setValue(0)
                item_widget.set_tax_readonly(True, set_to_zero=False)  # Already set to 0 above
            else:
                item_widget.tax_spin.setValue(product_data.get('tax_rate', 18))
                item_widget.set_tax_readonly(False)  # Make editable for GST invoices
            
            # Calculate total for the item
            item_widget.calculate_total()
            
            self.number_items()
            self.update_totals()
            self._update_empty_state()
            
            # Focus on quantity field for quick entry
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.setFocus())
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.selectAll())
            
            # Brief success highlight
            highlight_success(item_widget.product_input, duration_ms=1000)
            
        except Exception as e:
            print(f"Quick add product error: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

    def add_item(self) -> None:
        """Add a new invoice item row with validation."""
        # Check if party is selected first
        if hasattr(self, 'party_search'):
            party_text = self.party_search.text().strip()
            if not party_text:
                highlight_error(self.party_search, "Please select a party first")
                self.party_search.setFocus()
                return
        
        # Check if the last item row has a product selected before adding new row
        if self.items_layout.count() > 1:  # There's at least one item row (plus stretch)
            last_item_widget = None
            # Find the last InvoiceItemWidget
            for i in range(self.items_layout.count() - 2, -1, -1):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    last_item_widget = widget
                    break
            
            if last_item_widget:
                # Check if product is selected (not empty)
                product_text = last_item_widget.product_input.currentText().strip()
                if not product_text:
                    # Highlight the empty product field and show message
                    highlight_error(last_item_widget.product_input, "Please select a product first")
                    last_item_widget.product_input.setFocus()
                    return  # Don't add new row
        
        item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
        # Wire row-level ➕ to add another item row
        item_widget.add_requested.connect(self.add_item)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
        item_widget.remove_requested.connect(self._handle_remove_request)  # Ctrl+Delete support
        item_widget.item_changed.connect(self.update_totals)
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        
        # Apply tax readonly state based on current tax type
        if hasattr(self, '_tax_type') and self._tax_type == "NON_GST":
            item_widget.set_tax_readonly(True, set_to_zero=True)
        else:
            item_widget.set_tax_readonly(False)
        
        # Assign row numbers after insertion (this also sets alternating colors)
        self.number_items()
        self.update_totals()
        self._update_empty_state()
        
        # Auto-scroll to show the new row and set focus
        QTimer.singleShot(50, lambda: self.scroll_to_new_item(item_widget))

    def _handle_remove_request(self, item_widget: InvoiceItemWidget, skip_confirm: bool = False) -> None:
        """Handle remove request from item widget (supports Ctrl+Delete instant delete).
        
        Args:
            item_widget: The InvoiceItemWidget to remove.
            skip_confirm: If True, skip confirmation dialog (Ctrl+Delete).
        """
        self.remove_item(item_widget, skip_confirm=skip_confirm)

    def remove_item(self, item_widget: InvoiceItemWidget, skip_confirm: bool = False) -> None:
        """
        Remove an invoice item row.
        
        Args:
            item_widget: The InvoiceItemWidget to remove.
            skip_confirm: If True, skip confirmation dialog (for Ctrl+Delete instant delete).
        """
        if self.items_layout.count() <= 2:
            QMessageBox.warning(self, "Cannot Remove", "🚫 At least one item is required for the invoice!")
            return
        
        # Skip confirmation if Ctrl+Delete was used
        if not skip_confirm:
            reply = QMessageBox.question(self, "Remove Item", "❓ Are you sure you want to remove this item?\n\n💡 Tip: Use Ctrl+Delete for instant delete.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        
        self.items_layout.removeWidget(item_widget)
        item_widget.deleteLater()
        # Re-number items after removal (also updates alternating colors)
        self.number_items()
        self.update_totals()
        self._update_empty_state()

    def _update_empty_state(self):
        """Show/hide empty state message based on whether items exist."""
        try:
            if not hasattr(self, 'empty_state_label'):
                return
            
            # Count actual item widgets (not the stretch at the end)
            item_count = 0
            for i in range(self.items_layout.count()):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    item_count += 1
            
            # Show empty state if no items
            self.empty_state_label.setVisible(item_count == 0)
        except Exception as e:
            print(f"Update empty state error: {e}")

    def scroll_to_new_item(self, item_widget):
        """Auto-scroll to show the newly added item and set focus on its product input"""
        try:
            # Find the scroll area that contains the items
            scroll_area = None
            for i in range(self.items_frame.layout().count()):
                widget = self.items_frame.layout().itemAt(i).widget()
                if isinstance(widget, QScrollArea):
                    scroll_area = widget
                    break
            
            if scroll_area and item_widget:
                # Ensure the widget is visible by scrolling to it
                scroll_area.ensureWidgetVisible(item_widget)
                
                # Set focus on the product input field
                item_widget.product_input.setFocus()
                
        except Exception as e:
            print(f"Error scrolling to new item: {e}")
            # Fallback: just set focus without scrolling
            try:
                item_widget.product_input.setFocus()
            except Exception:
                pass

    def number_items(self):
        """Update the read-only row number textbox in each item row (1-based) with alternating row colors."""
        try:
            row = 1
            for i in range(self.items_layout.count() - 1):  # exclude the stretch at the end
                w = self.items_layout.itemAt(i).widget()
                if isinstance(w, InvoiceItemWidget) and hasattr(w, 'set_row_number'):
                    w.set_row_number(row)
                    
                    # Apply alternating row colors for better readability
                    if row % 2 == 0:
                        # Even row - light background
                        w.setStyleSheet(get_item_row_even_style())
                    else:
                        # Odd row - white background
                        w.setStyleSheet(get_item_row_odd_style())
                    
                    row += 1
        except Exception as e:
            print(f"Error numbering items: {e}")

    def update_totals(self) -> None:
        """Update all totals, tax breakdowns, and balance due calculations.
        
        Delegates all calculation logic to invoice_form_controller (which uses InvoiceService).
        UI only handles data collection and display updates.
        
        Enhanced to handle:
        - Invoice-level discount (% or flat amount)
        - Other charges (shipping, packaging, etc.)
        - Round-off visibility
        - Dynamic row visibility based on bill type
        """
        try:
            # ========== COLLECT ITEM DATA ==========
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            # ========== COLLECT SETTINGS ==========
            # Get current tax type selection (normalized)
            tax_type = self._get_tax_type()
            
            # Get invoice-level discount
            invoice_discount = 0.0
            invoice_discount_type = "%"
            if hasattr(self, 'invoice_discount_spin') and hasattr(self, 'invoice_discount_type'):
                invoice_discount = self.invoice_discount_spin.value()
                invoice_discount_type = self.invoice_discount_type.currentText()
            
            # Get other charges
            other_charges = 0.0
            if hasattr(self, 'other_charges_spin'):
                other_charges = self.other_charges_spin.value()
            
            # ========== DELEGATE CALCULATIONS TO CONTROLLER ==========
            totals = invoice_form_controller.calculate_invoice_totals(
                items, tax_type, invoice_discount, invoice_discount_type, other_charges
            )
            
            # Extract calculated values
            subtotal = totals['subtotal']
            total_discount = totals['total_discount']
            total_cgst = totals['cgst']
            total_sgst = totals['sgst']
            total_igst = totals['igst']
            total_tax = totals['total_tax']
            roundoff_amount = totals['roundoff_amount']
            grand_total = totals['grand_total']
            is_interstate = totals['is_interstate']
            is_non_gst = totals['is_non_gst']
            item_count = totals['item_count']
            has_decimal = totals['has_decimal']
            
            # Store roundoff for later use
            self.roundoff_amount = roundoff_amount
            
            # ========== UPDATE UI LABELS ==========
            
            # Update items section subtotal label
            if hasattr(self, 'items_subtotal_label'):
                self.items_subtotal_label.setText(f"₹{subtotal:,.2f}")
            
            # Update subtotal in totals section (now visible!)
            self.subtotal_label.setText(f"₹{subtotal:,.2f}")
            
            # Update discount label (shows total discount)
            self.discount_label.setText(f"-₹{total_discount:,.2f}")
            
            # Show/hide discount row (visible when there's any discount)
            has_discount = (total_discount > 0)
            if hasattr(self, 'invoice_discount_row_label'):
                self.invoice_discount_row_label.setVisible(has_discount)
            if hasattr(self, 'discount_label'):
                self.discount_label.setVisible(has_discount)
            
            # Update GST breakdown labels
            self.cgst_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 500;
                color: {DANGER};
                background: transparent;
                padding: 2px 0px;
            }}
                """)
            self.cgst_label.setText(f"₹{total_cgst:,.2f}")
            self.sgst_label.setText(f"₹{total_sgst:,.2f}")
            self.igst_label.setText(f"₹{total_igst:,.2f}")
            self.tax_label.setText(f"₹{total_tax:,.2f}")
            
            # Update tax row label based on invoice type
            if hasattr(self, 'tax_row_label'):
                if is_interstate and not is_non_gst:
                    self.tax_row_label.setText("Tax/IGST:")
                else:
                    self.tax_row_label.setText("Tax:")
            
            # Update tax breakdown label beside tax value
            if hasattr(self, 'tax_breakdown_label'):
                if not is_non_gst and total_tax > 0:
                    if is_interstate:
                        self.tax_breakdown_label.setText("")
                    else:
                        # HTML format with colors: CGST: ₹X.XX + SGST: ₹Y.YY (with colored amounts)
                        cgst_colored = f"<span style='color: #059669; font-weight: 600;'>₹{total_cgst:,.2f}</span>"
                        sgst_colored = f"<span style='color: #059669; font-weight: 600;'>₹{total_sgst:,.2f}</span>"
                        label_text = f"CGST: {cgst_colored}<br>SGST: {sgst_colored}"
                        self.tax_breakdown_label.setText(label_text)
                    self.tax_breakdown_label.setTextFormat(Qt.RichText)
                else:
                    self.tax_breakdown_label.setText("")
            
            # Update grand total
            self.grand_total_label.setText(f"₹{grand_total:,.2f}")
            
            # Update amount in words
            if hasattr(self, 'amount_in_words_label'):
                self.amount_in_words_label.setText(
                    invoice_form_controller.number_to_words_indian(grand_total)
                )
            
            # ========== VISIBILITY LOGIC ==========
            
            # Get bill type for Balance Due visibility
            bill_type = self._bill_type if hasattr(self, '_bill_type') else 'CASH'
            is_credit = (bill_type == 'CREDIT')
            
            # Determine if Tax row should be visible:
            # - For Non-GST invoices: ALWAYS HIDE (regardless of products or tax)
            # - For GST invoices: show if there's tax
            has_products = (item_count > 0)
            has_tax = (total_tax > 0 and not is_non_gst)
            
            # Show/hide Tax row (hide completely for Non-GST, or for GST with no tax)
            if hasattr(self, 'tax_row_label'):
                self.tax_row_label.setVisible(has_tax)
            if hasattr(self, 'tax_label'):
                self.tax_label.setVisible(has_tax)
            if hasattr(self, 'tax_breakdown_label'):
                self.tax_breakdown_label.setVisible(has_tax)
            
            # Show/hide CGST/SGST/IGST breakdown rows
            if has_tax and not is_non_gst:
                if is_interstate:
                    # Show IGST only
                    if hasattr(self, 'cgst_row_label'):
                        self.cgst_row_label.setVisible(False)
                        self.cgst_label.setVisible(False)
                    if hasattr(self, 'sgst_row_label'):
                        self.sgst_row_label.setVisible(False)
                        self.sgst_label.setVisible(False)
                    if hasattr(self, 'igst_row_label'):
                        self.igst_row_label.setVisible(True)
                        self.igst_label.setVisible(True)
                else:
                    # Show CGST and SGST
                    if hasattr(self, 'cgst_row_label'):
                        self.cgst_row_label.setVisible(True)
                        self.cgst_label.setVisible(True)
                    if hasattr(self, 'sgst_row_label'):
                        self.sgst_row_label.setVisible(True)
                        self.sgst_label.setVisible(True)
                    if hasattr(self, 'igst_row_label'):
                        self.igst_row_label.setVisible(False)
                        self.igst_label.setVisible(False)
            else:
                # Hide all GST breakdown rows
                if hasattr(self, 'cgst_row_label'):
                    self.cgst_row_label.setVisible(False)
                    self.cgst_label.setVisible(False)
                if hasattr(self, 'sgst_row_label'):
                    self.sgst_row_label.setVisible(False)
                    self.sgst_label.setVisible(False)
                if hasattr(self, 'igst_row_label'):
                    self.igst_row_label.setVisible(False)
                    self.igst_label.setVisible(False)
            
            # Show/hide Round-off row (when grand total has decimal)
            if hasattr(self, 'roundoff_row_label') and hasattr(self, 'roundoff_link'):
                show_roundoff = has_decimal and grand_total > 0
                self.roundoff_row_label.setVisible(show_roundoff)
                self.roundoff_link.setVisible(show_roundoff)
                
                # Update roundoff value if visible
                if show_roundoff:
                    if roundoff_amount >= 0:
                        roundoff_display = f"<a href='options' style='text-decoration: none; color: #10B981;'>+₹{roundoff_amount:.2f} ▼</a>"
                    else:
                        roundoff_display = f"<a href='options' style='text-decoration: none; color: #EF4444;'>-₹{abs(roundoff_amount):.2f} ▼</a>"
                    self.roundoff_link.setText(roundoff_display)
            
            # Show/hide Paid Amount and Balance Due rows (only for CREDIT)
            if hasattr(self, 'paid_row_label'):
                self.paid_row_label.setVisible(is_credit)
                self.paid_amount_spin.setVisible(is_credit)
            
            if hasattr(self, 'balance_row_label'):
                self.balance_row_label.setVisible(is_credit)
                self.balance_label.setVisible(is_credit)
            
            # Update item count badge
            if hasattr(self, 'item_count_badge'):
                self.item_count_badge.setText(str(item_count))
                self.item_count_badge.setStyleSheet(get_item_count_badge_style(item_count))
            
            # Show/hide empty state label (hide when there are items, show when no items)
            if hasattr(self, 'empty_state_label'):
                actual_item_count = 0
                for i in range(self.items_layout.count()):
                    widget = self.items_layout.itemAt(i).widget()
                    if isinstance(widget, InvoiceItemWidget):
                        actual_item_count += 1
                self.empty_state_label.setVisible(actual_item_count == 0)

            
        except Exception as e:
            print(f"Error updating totals: {e}")

    def save_invoice(self) -> None:
        """Save the invoice with validation and user confirmation."""
        # Show confirmation dialog first
        action_text = "update" if self.invoice_data else "save"
        reply = QMessageBox.question(
            self, 
            "Confirm Save", 
            f"Do you want to {action_text} this invoice?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return  # User cancelled
        
        # Validate party selection with visual feedback
        party_text = getattr(self, 'party_search').text().strip()
        party_data = getattr(self, 'party_data_map', {}).get(party_text)
        if not party_data or not party_text:
            show_validation_error(
                self, 
                self.party_search if hasattr(self, 'party_search') else None,
                "Validation Error", 
                "Please select a valid party from the search!"
            )
            return
        
        # Validate items with visual feedback
        items = []
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                # Only include items with valid product data (skip empty rows)
                if item_data and item_data.get('product_name', '').strip():
                    items.append(item_data)
        
        if not items:
            # Highlight the item count badge to draw attention
            if hasattr(self, 'item_count_badge'):
                highlight_error(self.item_count_badge, "Add at least one item")
            QMessageBox.warning(self, "Validation Error", "⚠️ Please add at least one item with a valid product!")
            return
        
        # Collect invoice header data for controller
        notes_text = ''
        if hasattr(self, 'notes') and self.notes is not None:
            notes_text = self.notes.toPlainText()
        
        invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
        if not invoice_no:
            QMessageBox.warning(self, "Error", "Invoice number cannot be empty!")
            return
        
        # For new invoices, ensure the invoice number is unique
        is_new = not self.invoice_data
        if is_new:
            invoice_no = invoice_form_controller.ensure_unique_invoice_number(invoice_no)
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setText(invoice_no)
        
        # Validate via controller (skip duplicate check since we already ensured uniqueness)
        is_valid, error_msg, field_name = invoice_form_controller.validate_invoice_data(
            invoice_no, party_data.get('id'), items, is_new, skip_duplicate_check=is_new
        )
        
        if not is_valid:
            # Show validation error with field highlighting
            field_widget = None
            if field_name == 'invoice_no' and hasattr(self, 'invoice_number'):
                field_widget = self.invoice_number
            elif field_name == 'party' and hasattr(self, 'party_search'):
                field_widget = self.party_search
            elif field_name == 'items' and hasattr(self, 'item_count_badge'):
                field_widget = self.item_count_badge
            
            show_validation_error(self, field_widget, "Validation Error", error_msg)
            return
        
        # Prepare data for controller
        invoice_data_dict = {
            'invoice_no': invoice_no,
            'date': self.invoice_date.date().toString('yyyy-MM-dd'),
            'party_id': party_data['id'],
            'invoice_type': self._get_tax_type(),
            'bill_type': self._bill_type if hasattr(self, '_bill_type') else 'CASH',
            'notes': notes_text,
            'round_off': round(getattr(self, 'roundoff_amount', 0.0), 2),
        }
        
        if self.invoice_data:
            invoice_data_dict['id'] = self.invoice_data.get('id') or self.invoice_data.get('invoice', {}).get('id')
        
        # Save via controller
        success, message, invoice_id = invoice_form_controller.save_invoice(
            invoice_data_dict,
            items,
            is_final=False
        )
        
        if success:
            highlight_success(self.invoice_number)
            QMessageBox.information(self, "Success", f"✅ {message}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"❌ {message}")

    def reset_form(self) -> None:
        """Reset all form fields to defaults and update date to today."""
        try:
            # Show confirmation dialog first
            reply = QMessageBox.question(
                self, 
                "Confirm Reset", 
                "Are you sure you want to reset all fields? This will clear all entered data.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default to No for safety
            )
            
            if reply != QMessageBox.Yes:
                return  # User cancelled
            
            # Reset date to today
            if hasattr(self, 'invoice_date') and self.invoice_date is not None:
                self.invoice_date.setDate(QDate.currentDate())
            
            # Reset invoice number to next available via controller
            if hasattr(self, 'invoice_number') and self.invoice_number is not None:
                next_inv_no = invoice_form_controller.generate_next_invoice_number()
                self.invoice_number.setText(next_inv_no)
            
            # Clear party search (combo box)
            if hasattr(self, 'party_search') and self.party_search is not None:
                self.party_search.setCurrentIndex(-1)
                self.party_search.lineEdit().clear()
                # Repopulate party data map from parties list (don't clear it completely)
                if hasattr(self, 'party_data_map'):
                    self.party_data_map = {}
                    # Repopulate from self.parties
                    for party in self.parties:
                        name = party.get('name', '').strip()
                        if name:
                            self.party_data_map[name] = party
            
            # Clear notes if it exists
            if hasattr(self, 'notes') and self.notes is not None:
                self.notes.clear()
            
            # Reset paid amount
            if hasattr(self, 'paid_amount_spin') and self.paid_amount_spin is not None:
                self.paid_amount_spin.setValue(0.0)
            
            # Remove all item widgets except the stretch at the end
            if hasattr(self, 'items_layout') and self.items_layout is not None:
                # Remove all items in reverse order (preserve stretch at end)
                for i in reversed(range(self.items_layout.count() - 1)):
                    item = self.items_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, InvoiceItemWidget):
                            self.items_layout.removeWidget(widget)
                            widget.deleteLater()
                
                # Don't add a new item - wait for party selection
                # The empty state will be shown automatically
                self._update_empty_state()
            
            # Update totals display
            self.update_totals()
            
            # Re-enable save buttons (in case they were disabled after a FINAL save)
            if hasattr(self, 'save_button'):
                self.save_button.setEnabled(True)
                self.save_button.setText("💾 Save Invoice")
            
            if hasattr(self, 'save_print_button'):
                self.save_print_button.setEnabled(True)
                self.save_print_button.setText("� Save Print")
            
            # Clear invoice_data so this is treated as a new invoice
            self.invoice_data = None
            
            # Show success message
            QMessageBox.information(self, "Reset Complete", "Invoice has been reset. You can now create a new invoice.")
            
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Failed to reset invoice: {str(e)}")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Override keyPressEvent to prevent Enter from closing the dialog.
        Enter/Return should only trigger actions if explicitly handled by focused widget.
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Check if focused widget is a button - if not, ignore the key
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox)):
                # These widgets should handle Enter normally, don't pass to parent
                event.accept()
                return
            # For other widgets, consume the event to prevent dialog closing
            event.accept()
            return
        
        # Let other keys pass through normally
        super().keyPressEvent(event)



