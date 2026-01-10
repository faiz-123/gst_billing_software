"""
Sales Invoice Form Dialog
UI for creating/editing sales invoices.

Architecture: UI → Controller → Service → DB
This file contains ONLY UI code - layouts, widgets, signal-slot connections.
All business logic is delegated to InvoiceFormController.
"""

import os
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QKeySequence, QAction, QShortcut
from PySide6.QtWidgets import QCompleter
from widgets import (
    CustomButton, CustomTable, CustomInput, FormField, PartySelector, ProductSelector,
    InvoiceItemWidget, highlight_error, highlight_success, show_validation_error
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
    get_pdf_toolbar_button_style, get_pdf_page_info_style
)
from controllers.invoice_controller import invoice_form_controller


class InvoiceDialog(QDialog):

    """Enhanced dialog for creating/editing invoices with modern UI"""
    def __init__(self, parent=None, invoice_data=None, invoice_number=None, read_only=False):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.products = []
        self.parties = []
        self.read_only = read_only  # Read-only mode flag
        # Guard to avoid re-entrant opening of PartySelector from typing
        self._party_selector_active = False
        # Auto-save timer
        self._autosave_timer = None
        self._has_unsaved_changes = False

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
            QTimer.singleShot(150, self.set_initial_focus)
            # Start auto-save for new invoices
            QTimer.singleShot(200, self.setup_autosave)

    def load_existing_invoice(self, invoice_number):
        """Load existing invoice data by invoice number via controller."""
        try:
            invoice_data = invoice_form_controller.get_invoice_by_number(invoice_number)
            if invoice_data:
                self.invoice_data = invoice_data
            else:
                QMessageBox.warning(self, "Error", f"Invoice '{invoice_number}' not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoice: {str(e)}")

    def populate_invoice_data(self):
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
                self.party_search.setText(party['name'])
            
            # Set bill type if available
            if hasattr(self, 'billtype_combo') and invoice.get('bill_type'):
                index = self.billtype_combo.findText(invoice['bill_type'])
                if index >= 0:
                    self.billtype_combo.setCurrentIndex(index)
            
            # Set invoice type (GST/Non-GST) if available
            if hasattr(self, 'gst_combo') and invoice.get('tax_type'):
                index = self.gst_combo.findText(invoice['tax_type'])
                if index >= 0:
                    self.gst_combo.setCurrentIndex(index)
            
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
                
                # Add items from database
                for item_data in items:
                    item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                    
                    # Set product name
                    item_widget.product_input.setText(item_data['product_name'])
                    
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
                    item_widget.item_changed.connect(self.update_totals)
                    
                    # Add to layout (before the stretch)
                    self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
                
                # Update row numbers and totals
                self.number_items()
                self.update_totals()
            
            # Check if invoice is FINAL and disable editing if so
            if invoice.get('status') == 'FINAL':
                self.disable_editing_after_final_save(show_message=False)
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error populating invoice data: {str(e)}")

    def apply_read_only_mode(self):
        """Apply read-only mode to the entire dialog - disable all editing"""
        try:
            # Update window title to indicate view mode
            invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else 'Invoice'
            self.setWindowTitle(f"📄 View Invoice - {invoice_no} (Read Only)")
            
            # Disable header inputs
            if hasattr(self, 'billtype_combo'):
                self.billtype_combo.setEnabled(False)
            if hasattr(self, 'party_search'):
                self.party_search.setReadOnly(True)
                self.party_search.setStyleSheet(self.party_search.styleSheet() + f"background: {BACKGROUND};")
            if hasattr(self, 'gst_combo'):
                self.gst_combo.setEnabled(False)
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
                            item_widget.product_input.setReadOnly(True)
                            item_widget.product_input.setStyleSheet(item_widget.product_input.styleSheet() + f"background: {BACKGROUND};")
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

    def ensure_maximized(self):
        """Ensure the window is properly maximized"""
        from PySide6.QtGui import QGuiApplication
        # Use availableGeometry to account for menu bar and dock
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setWindowState(Qt.WindowMaximized)
        self.showMaximized()

    def set_initial_focus(self):
        """Set initial focus on the party search box for new invoices"""
        try:
            if hasattr(self, 'party_search'):
                self.party_search.setFocus()
                # Optional: clear any existing text and position cursor at start
                self.party_search.selectAll()
        except Exception as e:
            print(f"Error setting initial focus: {e}")

    def setup_autosave(self):
        """Setup auto-save timer to save draft every 30 seconds"""
        try:
            self._autosave_timer = QTimer(self)
            self._autosave_timer.timeout.connect(self.autosave_draft)
            self._autosave_timer.start(30000)  # 30 seconds
            print("Auto-save enabled: Draft will be saved every 30 seconds")
        except Exception as e:
            print(f"Failed to setup auto-save: {e}")

    def autosave_draft(self):
        """Auto-save current invoice data as draft"""
        try:
            # Only save if there's meaningful data
            party_text = self.party_search.text().strip() if hasattr(self, 'party_search') else ''
            
            # Check if any items have been added
            item_count = 0
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    if item_widget.get_item_data():
                        item_count += 1
            
            # Only save if there's party or items
            if party_text or item_count > 0:
                draft_data = self.collect_draft_data()
                # Save to config
                try:
                    from config import config
                    config.set('invoice_draft', draft_data)
                    self._has_unsaved_changes = False
                    print(f"Draft auto-saved: {party_text or 'No party'}, {item_count} items")
                except Exception as config_error:
                    print(f"Could not save draft to config: {config_error}")
        except Exception as e:
            print(f"Auto-save draft failed: {e}")

    def collect_draft_data(self):
        """Collect current form data for draft saving"""
        try:
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            return {
                'party_name': self.party_search.text().strip() if hasattr(self, 'party_search') else '',
                'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else '',
                'bill_type': self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH',
                'invoice_type': self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST',
                'internal_invoice_type': invoice_form_controller.map_invoice_type_to_internal(
                    self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST'
                ),
                'items': items,
                'notes': self.notes.toPlainText() if hasattr(self, 'notes') and self.notes else '',
                'saved_at': QDate.currentDate().toString('yyyy-MM-dd')
            }
        except Exception as e:
            print(f"Error collecting draft data: {e}")
            return {}

    def closeEvent(self, event):
        """Handle dialog close - stop auto-save timer"""
        try:
            if self._autosave_timer:
                self._autosave_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)

    def init_window(self):
        """Initialize window properties and styling"""
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

    def load_data(self):
        """Load products and parties data via controller."""
        try:
            self.products = invoice_form_controller.get_products()
            self.parties = invoice_form_controller.get_parties()
        except Exception as e:
            print(f"[InvoiceDialog] Error loading data: {e}")
            self.products = []
            self.parties = []

    def setup_ui(self):
        """Setup enhanced dialog UI with modern design and better organization"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(30, 30, 30, 30)  # Reduced bottom margin
        self.setup_content_sections()
        self.setup_action_buttons()
        self.apply_final_styling()

    def setup_content_sections(self):
        """Setup the main content sections with enhanced layout"""
        self.content_splitter = QSplitter(Qt.Vertical)
        self.header_frame = self.create_header_section()
        self.content_splitter.addWidget(self.header_frame)
        self.items_frame = self.create_items_section()
        self.content_splitter.addWidget(self.items_frame)
        self.totals_frame = self.create_totals_section()
        self.content_splitter.addWidget(self.totals_frame)
        self.content_splitter.setSizes([180, 450, 150])
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, False)
        self.content_splitter.setCollapsible(2, False)
        self.main_layout.addWidget(self.content_splitter, 1)  # Stretch factor 1 for splitter
        # Only add empty item row for new invoices (not in read-only mode or editing existing)
        if not self.read_only and not self.invoice_data:
            self.add_item()

    def setup_action_buttons(self):
        """Setup enhanced action buttons using CustomButton from common_widgets"""
        button_container = QFrame()
        button_container.setObjectName("buttonContainer")
        button_container.setStyleSheet(f"""
            QFrame#buttonContainer {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; }}
        """)
        button_container.setMinimumHeight(70)
        button_container.setMaximumHeight(80)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(20, 15, 20, 15)
        
        # Utility buttons (left side)
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(8)
        
        self.help_button = CustomButton("❓ Help", "secondary")
        self.help_button.setToolTip("Get help with invoice creation")
        self.help_button.clicked.connect(self.show_help)
        utility_layout.addWidget(self.help_button)
        
        button_layout.addLayout(utility_layout)
        button_layout.addStretch()
        
        # Action buttons (right side)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        # Cancel button
        self.cancel_button = CustomButton("❌ Cancel", "danger")
        self.cancel_button.setToolTip("Cancel and close without saving")
        self.cancel_button.clicked.connect(self.reject)
        action_layout.addWidget(self.cancel_button)
        
        # Reset button
        self.reset_button = CustomButton("🔄 Reset", "secondary")
        self.reset_button.setToolTip("Clear all values and reset to defaults")
        self.reset_button.clicked.connect(self.reset_form)
        action_layout.addWidget(self.reset_button)
        
        # Save Print button
        save_text = "💾 Update & Print" if self.invoice_data else "💾 Save Print"
        self.save_print_button = CustomButton(save_text, "primary")
        self.save_print_button.setToolTip("Save invoice and open print preview")
        self.save_print_button.clicked.connect(self.save_and_print)
        action_layout.addWidget(self.save_print_button)
        
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container, 0)  # Stretch factor 0 - don't expand

    def apply_final_styling(self):
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.showMaximized()
        self.setup_keyboard_shortcuts()
        self.setup_validation()

    def setup_keyboard_shortcuts(self):
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

    def setup_validation(self):
        # Set initial balance due visibility based on default bill type
        if hasattr(self, 'billtype_combo'):
            self.on_bill_type_changed(self.billtype_combo.currentText())

    def show_help(self):
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
        bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else ''
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

        dlg.exec()

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

    def save_and_print(self):
        """Save invoice and open print preview"""
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

    def validate_invoice_for_final_save(self):
        """Validate that invoice has all required data for final save"""
        # Check invoice number
        invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
        if not invoice_no:
            show_validation_error(
                self,
                self.invoice_number if hasattr(self, 'invoice_number') else None,
                "Validation Error",
                "Invoice number is required!"
            )
            return False
        
        # Check date
        if not hasattr(self, 'invoice_date') or not self.invoice_date.date():
            show_validation_error(
                self,
                self.invoice_date if hasattr(self, 'invoice_date') else None,
                "Validation Error",
                "Invoice date is required!"
            )
            return False
        
        # Check party selection
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
        
        # Check at least one item
        items = []
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                if item_data:
                    items.append(item_data)
        
        if not items:
            # Highlight item count badge
            if hasattr(self, 'item_count_badge'):
                highlight_error(self.item_count_badge, "Add at least one item")
            QMessageBox.warning(self, "Validation Error", "⚠️ Please add at least one item!")
            return False
        
        # Check for duplicate invoice number via controller
        if not self.invoice_data and invoice_form_controller.invoice_number_exists(invoice_no):
            show_validation_error(
                self,
                self.invoice_number if hasattr(self, 'invoice_number') else None,
                "Validation Error",
                f"Invoice number '{invoice_no}' already exists. Please use a unique invoice number."
            )
            return False
        
        return True

    def save_final_invoice(self):
        """Save invoice with FINAL status via controller and return invoice ID."""
        try:
            # Collect party data
            party_text = getattr(self, 'party_search').text().strip()
            party_data = getattr(self, 'party_data_map', {}).get(party_text)
            
            if not party_data or 'id' not in party_data:
                raise Exception(f"Invalid party selected: {party_text}")
            
            # Collect items
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            invoice_no = self.invoice_number.text().strip()
            invoice_date = self.invoice_date.date().toString('yyyy-MM-dd')
            invoice_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST - Same State'
            bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH'
            round_off = getattr(self, 'roundoff_amount', 0.0)
            notes = self.notes.toPlainText().strip() if hasattr(self, 'notes') and self.notes else None
            
            # Ensure unique invoice number for new invoices
            if not self.invoice_data:
                invoice_no = invoice_form_controller.ensure_unique_invoice_number(invoice_no)
                if hasattr(self, 'invoice_number'):
                    self.invoice_number.setText(invoice_no)
            
            # Prepare data for controller
            invoice_data_dict = {
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
            result = invoice_form_controller.save_invoice(
                invoice_data_dict,
                items,
                is_update=bool(self.invoice_data),
                status='FINAL'
            )
            
            if result.success:
                # Update invoice number display
                if result.invoice_no and hasattr(self, 'invoice_number'):
                    self.invoice_number.setText(result.invoice_no)
                
                # Disable editing after final save
                self.disable_editing_after_final_save()
                
                return result.invoice_id
            else:
                QMessageBox.critical(self, "Save Error", result.message)
                return None
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save invoice: {str(e)}")
            return None

    def disable_editing_after_final_save(self, show_message=True):
        """Disable all editing controls after invoice is saved as FINAL"""
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

    def show_print_preview(self, invoice_id):
        """Show HTML preview dialog - uses common utility"""
        from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
        show_invoice_preview(self, invoice_id)

    def generate_invoice_html(self, invoice_id):
        """Generate HTML content for the invoice"""
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
            
            # Create a hidden webview for rendering
            webview = QWebEngineView()
            webview.setMinimumSize(800, 600)
            
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
        try:
            # Check if typed text exactly matches a party name
            typed_text = self.party_search.text().strip()
            exact_match = None
            
            # Check for exact match (case-insensitive)
            for party_name in self.party_data_map.keys():
                if party_name.upper() == typed_text.upper():
                    exact_match = party_name
                    break
            
            if exact_match:
                # Direct match found, no need to open selector
                selected = exact_match
                self.party_search.setText(selected)
                
                # Focus on Date field after party selection
                if hasattr(self, 'invoice_date'):
                    self.invoice_date.setFocus()
            else:
                # No exact match, open selector
                selected = self._open_party_selector_dialog()
                if selected:
                    self.party_search.setText(selected)
                    
                    # Focus on Date field after party selection
                    if hasattr(self, 'invoice_date'):
                        self.invoice_date.setFocus()
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

    def _open_party_selector_dialog(self, prefill_text: str = None):
        """Create, size, position and open the PartySelector below the input.
        Returns the selected name if accepted, else None.
        """
        dlg = PartySelector(self.parties, self)
        # Prefill search
        try:
            if prefill_text:
                dlg.search.setText(prefill_text)
                dlg.search.setCursorPosition(len(prefill_text))
        except Exception:
            pass
        # Size and position
        try:
            from PySide6.QtGui import QGuiApplication
            input_w = max(300, self.party_search.width())
            dlg_h = min(dlg.sizeHint().height(), 420)
            margin = 8  # vertical gap to avoid overlap with the input
            dlg.resize(input_w, dlg_h)
            bl = self.party_search.mapToGlobal(self.party_search.rect().bottomLeft())
            x, y = bl.x(), bl.y() + margin
            screen = QGuiApplication.primaryScreen().availableGeometry()
            if y + dlg_h > screen.bottom():
                tl = self.party_search.mapToGlobal(self.party_search.rect().topLeft())
                y = tl.y() - dlg_h - margin
            if x + input_w > screen.right():
                x = max(screen.left(), screen.right() - input_w)
            dlg.move(int(x), int(y+65))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None

    def create_header_section(self):
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 15))
        # Two row header
        frame.setFixedHeight(200)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        label_style = get_form_label_style(14, "600")

        # ========== ROW 1: Bill Type, Tax Type, (stretch), Date, Invoice No ==========
        row1 = QHBoxLayout()
        row1.setSpacing(15)

        # Bill Type
        bill_box = QWidget()
        bill_box.setStyleSheet(get_transparent_container_style())
        bill_box_layout = QVBoxLayout(bill_box)
        bill_box_layout.setContentsMargins(0, 0, 0, 0)
        bill_box_layout.setSpacing(2)
        bill_lbl = QLabel("💵 Bill Type")
        bill_lbl.setStyleSheet(label_style)
        bill_box_layout.addWidget(bill_lbl)
        try:
            self.billtype_combo
        except Exception:
            self.billtype_combo = QComboBox()
            self.billtype_combo.addItems(["CASH", "CREDIT"])
        self.billtype_combo.setFixedHeight(40)
        # Dynamic background for bill type: green for CASH, red for CREDIT
        def update_billtype_style(text):
            t = (text or '').strip().upper()
            if 'CASH' in t:
                bg = '#10B981'  # green-500
                fg = WHITE
            elif 'CREDIT' in t:
                bg = '#EF4444'  # red-500
                fg = WHITE
            else:
                bg = WHITE
                fg = TEXT_PRIMARY
            try:
                self.billtype_combo.setStyleSheet(f"""
                    QComboBox {{ background: {bg}; color: {fg}; border-radius: 6px; padding: 6px; font-size: 14px; }}
                    QComboBox QAbstractItemView {{
                        background: {bg};
                        color: {TEXT_PRIMARY};
                        selection-background-color: {PRIMARY};
                        selection-color: {WHITE};
                    }}
                """)
            except Exception:
                pass
        update_billtype_style(self.billtype_combo.currentText())
        self.billtype_combo.currentTextChanged.connect(update_billtype_style)
        # Update totals when bill type changes (for Balance Due visibility)
        self.billtype_combo.currentTextChanged.connect(lambda: self.update_totals() if hasattr(self, 'items_layout') else None)
        bill_box_layout.addWidget(self.billtype_combo)
        bill_box.setFixedWidth(140)
        row1.addWidget(bill_box)

        # Tax Type
        gst_box = QWidget()
        gst_box.setStyleSheet(get_transparent_container_style())
        gst_box_layout = QVBoxLayout(gst_box)
        gst_box_layout.setContentsMargins(0, 0, 0, 0)
        gst_box_layout.setSpacing(2)
        gst_lbl = QLabel("📋 Tax Type")
        gst_lbl.setStyleSheet(label_style)
        gst_box_layout.addWidget(gst_lbl)
        try:
            self.gst_combo
        except Exception:
            self.gst_combo = QComboBox()
            self.gst_combo.addItems(["GST - Same State", "GST - Other State", "Non-GST"])
        self.gst_combo.setFixedHeight(40)
        # Add tooltip explaining GST tax types
        self.gst_combo.setToolTip(
            "<b>GST Tax Types:</b><br><br>"
            "<b>GST - Same State:</b><br>"
            "• CGST (Central GST) - Tax paid to Central Govt<br>"
            "• SGST (State GST) - Tax paid to State Govt<br>"
            "• Used when buyer & seller are in same state<br><br>"
            "<b>GST - Other State:</b><br>"
            "• IGST (Integrated GST) - Tax on interstate sales<br>"
            "• Used when buyer & seller are in different states<br><br>"
            "<b>Non-GST:</b><br>"
            "• No GST applicable (exempt goods/services)"
        )
        try:
            self.gst_combo.setStyleSheet(f"""
                QComboBox {{ background: {PRIMARY}; color: {WHITE}; border-radius: 6px; padding: 6px; font-size: 14px; }}
                QComboBox QAbstractItemView {{
                    background: {PRIMARY};
                    color: {TEXT_PRIMARY};
                    selection-background-color: {PRIMARY};
                    selection-color: {WHITE};
                }}
            """)
        except Exception:
            pass
        # Update totals when tax type changes (for CGST/SGST/IGST visibility)
        self.gst_combo.currentTextChanged.connect(lambda: self.update_totals() if hasattr(self, 'items_layout') else None)
        gst_box_layout.addWidget(self.gst_combo)
        gst_box.setFixedWidth(160)
        row1.addWidget(gst_box)

        # Stretch to push Date and Invoice No to the right
        row1.addStretch()

        # Invoice Date (right corner)
        inv_date_box = QWidget()
        inv_date_box.setStyleSheet(get_transparent_container_style())
        inv_date_box_layout = QVBoxLayout(inv_date_box)
        inv_date_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_date_box_layout.setSpacing(2)
        inv_date_lbl = QLabel("📅 Date")
        inv_date_lbl.setStyleSheet(label_style)
        inv_date_box_layout.addWidget(inv_date_lbl)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setFixedHeight(40)
        self.invoice_date.setStyleSheet(get_date_edit_style() + get_calendar_stylesheet())
        # Connect editingFinished to focus on product input after date
        self.invoice_date.editingFinished.connect(self._focus_first_product_input)
        inv_date_box_layout.addWidget(self.invoice_date)
        inv_date_box.setFixedWidth(140)
        row1.addWidget(inv_date_box)

        # Invoice Number (right corner)
        inv_num_box = QWidget()
        inv_num_box.setStyleSheet(get_transparent_container_style())
        inv_num_box_layout = QVBoxLayout(inv_num_box)
        inv_num_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_num_box_layout.setSpacing(2)
        inv_num_lbl = QLabel("📄 Invoice No")
        inv_num_lbl.setStyleSheet(label_style)
        inv_num_box_layout.addWidget(inv_num_lbl)
        # Determine next invoice number via controller
        next_inv_no = invoice_form_controller.generate_next_invoice_number()
        self.invoice_number = QLineEdit(next_inv_no)
        self.invoice_number.setReadOnly(True)
        self.invoice_number.setFixedHeight(40)
        self.invoice_number.setAlignment(Qt.AlignCenter)
        self.invoice_number.setStyleSheet(get_invoice_number_input_style())
        inv_num_box_layout.addWidget(self.invoice_number)
        inv_num_box.setFixedWidth(140)
        row1.addWidget(inv_num_box)

        layout.addLayout(row1)

        # ========== ROW 2: Select Party (full width) ==========
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        party_box = QWidget()
        party_box.setStyleSheet(get_transparent_container_style())
        party_box_layout = QVBoxLayout(party_box)
        party_box_layout.setContentsMargins(0, 0, 0, 0)
        party_box_layout.setSpacing(2)
        party_header = QHBoxLayout()
        party_header.setSpacing(5)
        party_label = QLabel("🏢 Select Party")
        party_label.setStyleSheet(label_style)
        party_header.addWidget(party_label)
        add_party_link = QLabel("<a href='#'>+Add New</a>")
        add_party_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_party_link.setOpenExternalLinks(False)
        add_party_link.setStyleSheet(get_add_party_link_style())
        add_party_link.setCursor(Qt.PointingHandCursor)
        add_party_link.linkActivated.connect(self.open_quick_add_party_dialog)
        party_header.addWidget(add_party_link)
        party_header.addStretch()
        party_box_layout.addLayout(party_header)

        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search customer...")
        self.party_search.setFixedHeight(50)
        self.party_search.setFixedWidth(500)
        self.party_search.setStyleSheet(get_party_search_input_style())
        # populate party_data_map
        self.party_data_map = {}
        for p in (self.parties or []):
            name = p.get('name', '').strip()
            if name:
                self.party_data_map[name] = p
        self.party_search.textEdited.connect(self.on_party_search_edited)
        self.party_search.returnPressed.connect(self.open_party_selector)
        party_box_layout.addWidget(self.party_search)
        row2.addWidget(party_box, 1)  # Stretch to fill full width

        layout.addLayout(row2)

        return frame

    def open_quick_add_party_dialog(self, link=None):
        """Open a quick dialog to add a new party without leaving the invoice."""
        try:
            from ui.parties.party_form_dialog import PartyDialog
            dialog = PartyDialog(self)
            if dialog.exec() == QDialog.Accepted:
                # Refresh parties list via controller
                self.parties = invoice_form_controller.get_parties()
                # Update party_data_map
                self.party_data_map = {}
                for party in self.parties:
                    name = party.get('name', '').strip()
                    if name:
                        self.party_data_map[name] = party
                
                # If a new party was created, select it automatically
                if hasattr(dialog, 'saved_party_name') and dialog.saved_party_name:
                    self.party_search.setText(dialog.saved_party_name)
                    highlight_success(self.party_search)
                    QMessageBox.information(self, "Success", f"✅ Party '{dialog.saved_party_name}' added and selected!")
                else:
                    QMessageBox.information(self, "Success", "✅ New party added! You can now search and select it.")
        except ImportError:
            QMessageBox.warning(self, "Feature Unavailable", "Party dialog module not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open party dialog: {str(e)}")

    def on_party_search_edited(self, text: str):
        """Open PartySelector when user types in the party search box.
        Prefill selector search with typed text and avoid opening multiple times.
        """
        try:
            if self._party_selector_active:
                return
            if not text or not text.strip():
                return
            self._party_selector_active = True
            selected = self._open_party_selector_dialog(prefill_text=text)
            if selected:
                # Set chosen party name back to the input without re-triggering textEdited
                old_state = self.party_search.blockSignals(True)
                try:
                    self.party_search.setText(selected)
                finally:
                    self.party_search.blockSignals(old_state)
        except Exception as e:
            print(f"Party search edit handler error: {e}")
        finally:
            self._party_selector_active = False

    def on_invoice_type_changed(self, invoice_type: str):
        """Update tax rates for all items when invoice type changes"""
        try:
            for i in range(self.items_layout.count() - 1):  # exclude the stretch at the end
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    widget.update_tax_rate_for_invoice_type(invoice_type)
            
            # Update overall totals
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

    def create_items_section(self):
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 15))
        # frame.setFixedHeight(420)  # Reduced height
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 10)

        # Quick Products Section - Show recently used products as clickable chips
        quick_products_layout = QHBoxLayout()
        quick_products_layout.setSpacing(8)
        quick_products_layout.setContentsMargins(5, 5, 5, 5)
        
        quick_label = QLabel("⚡ Quick Add:")
        quick_label.setStyleSheet(get_form_label_style(12, "bold", TEXT_SECONDARY))
        quick_products_layout.addWidget(quick_label)
        
        # Get top 5 most used products (sorted by sales_rate as proxy for popularity)
        top_products = sorted(self.products[:8], key=lambda x: x.get('sales_rate', 0), reverse=True)[:5]
        
        for product in top_products:
            chip = QPushButton(product.get('name', '')[:20])  # Truncate long names
            chip.setFixedHeight(28)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setFocusPolicy(Qt.NoFocus)  # Prevent keyboard focus - only mouse clicks
            chip.setToolTip(f"Add {product.get('name', '')} - ₹{product.get('sales_rate', 0):,.2f}")
            chip.setStyleSheet(get_quick_chip_style())
            # Store product data in the button
            chip.product_data = product
            chip.clicked.connect(lambda checked, p=product: self.quick_add_product(p))
            quick_products_layout.addWidget(chip)
        
        quick_products_layout.addStretch()

        # Items count badge at right corner of Quick Add row
        items_label = QLabel("📦 Items:")
        items_label.setStyleSheet(get_form_label_style(12, "bold", TEXT_SECONDARY))
        quick_products_layout.addWidget(items_label)
        self.item_count_badge = QLabel("0")
        self.item_count_badge.setFixedSize(56, 46)
        self.item_count_badge.setStyleSheet(get_item_count_badge_style(0))
        quick_products_layout.addWidget(self.item_count_badge)

        layout.addLayout(quick_products_layout)

        headers_layout = QHBoxLayout()
        headers_layout.setSpacing(0)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        # Add leading No column for row numbering and HSN No after Product
        headers = [
            "No", "🛍️ Product", "📦 HSN No", "Qty", "📏 Unit",
            "💰 Rate", "🏷️ Disc%", "📋 Tax%", "💵 Amount", "❌ Action"
        ]
        widths = [100, 500, 100, 100, 85, 110, 110, 110, 110, 110]
        for header, width in zip(headers, widths):
            label = QLabel(header)
            label.setFixedWidth(width)
            label.setFixedHeight(35)
            label.setStyleSheet(get_items_header_label_style())
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)
        layout.addLayout(headers_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # scroll_area.setFixedHeight(380)  # Reduced scroll area height
        scroll_area.setStyleSheet(get_transparent_scroll_area_style())
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(1)
        self.items_layout.setContentsMargins(1, 1, 1, 1)
        self.items_layout.addStretch()
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area)
        
        # Subtotal row at bottom, aligned with Amount column
        subtotal_row = QHBoxLayout()
        subtotal_row.setSpacing(0)
        subtotal_row.setContentsMargins(0, 5, 0, 0)
        
        # Add spacers to align with Amount column (No:100 + Product:500 + HSN:100 + Qty:100 + Unit:85 + Rate:110 + Disc:110 + Tax:110 = 1215)
        spacer_widget = QWidget()
        spacer_widget.setFixedWidth(1215)
        subtotal_row.addWidget(spacer_widget)
        
        # Subtotal label aligned with Amount header
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setFixedWidth(110)
        subtotal_label.setFixedHeight(25)
        subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        subtotal_label.setStyleSheet(get_summary_label_style())
        subtotal_row.addWidget(subtotal_label)
        
        # Subtotal value - simple style like totals section
        self.items_subtotal_label = QLabel("₹0.00")
        self.items_subtotal_label.setFixedWidth(110)
        self.items_subtotal_label.setFixedHeight(25)
        self.items_subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_subtotal_label.setStyleSheet(get_summary_value_style())
        subtotal_row.addWidget(self.items_subtotal_label)
        
        # Action column spacer
        action_spacer = QWidget()
        action_spacer.setFixedWidth(110)
        subtotal_row.addWidget(action_spacer)
        
        layout.addLayout(subtotal_row)
        
        return frame

    def create_totals_section(self):
        frame = QFrame()
        frame.setStyleSheet(get_section_frame_style(WHITE, 12))
        frame.setMinimumHeight(150)  # Minimum height instead of fixed
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)

        # Notes area: lazy add via text link
        notes_container = QVBoxLayout()
        notes_header = QHBoxLayout()
        add_note_link = QLabel("<a href='add'>+Add Note</a>")
        add_note_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_note_link.setOpenExternalLinks(False)
        add_note_link.setStyleSheet(get_add_party_link_style())
        # Handler to create/show notes editor lazily
        def _handle_add_note_link(_):
            try:
                if not hasattr(self, 'notes') or self.notes is None:
                    self.notes = QTextEdit()
                    self.notes.setPlaceholderText("Add any additional information or terms...")
                    self.notes.setStyleSheet(f"border: 2px solid {BORDER}; border-radius: 8px; padding: 10px; background: {WHITE}; font-size: 13px;")
                    self.notes.setFixedHeight(80)
                    notes_container.insertWidget(1, self.notes)
                else:
                    self.notes.setVisible(True)
            except Exception as e:
                print(f"Failed to add notes editor: {e}")
        add_note_link.linkActivated.connect(_handle_add_note_link)
        # Place the link at the left; stretch goes after to push remaining content to the right
        notes_header.addWidget(add_note_link)
        notes_header.addStretch()
        notes_container.addLayout(notes_header)
        # Initially, no notes editor is shown; created on demand via link
        if not hasattr(self, 'notes'):
            self.notes = None
        
        # Amount in words label - positioned below notes
        amount_words_container = QVBoxLayout()
        amount_words_container.setSpacing(2)
        
        amount_words_title = QLabel("💰 In Words:")
        amount_words_title.setStyleSheet(get_form_label_style(11, "bold", TEXT_SECONDARY))
        amount_words_container.addWidget(amount_words_title)
        
        self.amount_in_words_label = QLabel("Zero Rupees Only")
        self.amount_in_words_label.setWordWrap(True)
        self.amount_in_words_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-style: italic;
                color: {PRIMARY};
                background: #EFF6FF;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 10px;
            }}
        """)
        self.amount_in_words_label.setMinimumWidth(280)
        self.amount_in_words_label.setMaximumWidth(400)
        self.amount_in_words_label.setMaximumHeight(50)
        amount_words_container.addWidget(self.amount_in_words_label)
        
        notes_container.addLayout(amount_words_container)
        notes_container.addStretch()

        layout.addLayout(notes_container, 2)

        # Totals on the right
        self.totals_layout = QFormLayout()  # Store reference for show/hide functionality
        self.totals_layout.setSpacing(8)  # Better spacing between rows
        
        # Hidden subtotal label for backward compatibility (not displayed - shown in items section)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setVisible(False)
        
        # Discount label (visible only when discount > 0)
        self.discount_label = QLabel("-₹0.00")
        self.discount_label.setStyleSheet("font-size: 14px; color: red; border: none; background: transparent;")
        self.totals_layout.addRow("Discount:", self.discount_label)
        
        # Tax row with breakdown box beside it
        # Create a container for Tax amount + breakdown box
        tax_container = QWidget()
        tax_container.setStyleSheet("background: transparent; border: none;")
        tax_container_layout = QHBoxLayout(tax_container)
        tax_container_layout.setContentsMargins(0, 0, 0, 0)
        tax_container_layout.setSpacing(8)
        
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        self.tax_label.setFixedWidth(80)
        tax_container_layout.addWidget(self.tax_label)
        
        # Tax breakdown box (shows CGST+SGST or IGST)
        self.tax_breakdown_box = QLabel("")
        self.tax_breakdown_box.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {TEXT_PRIMARY};
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 3px 8px;
            }}
        """)
        self.tax_breakdown_box.setVisible(False)
        tax_container_layout.addWidget(self.tax_breakdown_box)
        tax_container_layout.addStretch()
        
        # Store reference to tax container row
        self.tax_row_label = QLabel("Tax:")
        self.tax_row_label.setStyleSheet("font-size: 14px; border-radius: 6px;; background: transparent;")
        self.totals_layout.addRow(self.tax_row_label, tax_container)
        
        # Hidden GST breakdown labels (for backward compatibility - values still calculated)
        self.cgst_label = QLabel("₹0.00")
        self.cgst_label.setVisible(False)
        self.sgst_label = QLabel("₹0.00")
        self.sgst_label.setVisible(False)
        self.igst_label = QLabel("₹0.00")
        self.igst_label.setVisible(False)
        
        # Round-off row (hidden by default, shown when grand total has decimal)
        self.roundoff_container = QWidget()
        roundoff_layout = QHBoxLayout(self.roundoff_container)
        roundoff_layout.setContentsMargins(0, 0, 0, 0)
        roundoff_layout.setSpacing(5)
        
        self.roundoff_link = QLabel("<a href='roundoff'>Round Off</a>")
        self.roundoff_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.roundoff_link.setOpenExternalLinks(False)
        self.roundoff_link.setStyleSheet("color: #2563EB; font-size: 12px; border: none;")
        self.roundoff_link.linkActivated.connect(self.show_roundoff_options)
        roundoff_layout.addWidget(self.roundoff_link)
        
        self.roundoff_value_label = QLabel("₹0.00")
        self.roundoff_value_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        roundoff_layout.addWidget(self.roundoff_value_label)
        
        self.roundoff_container.setVisible(False)
        
        # Store round-off amount
        self.roundoff_amount = 0.0
        
        # Grand Total row with roundoff beside it
        grand_total_container = QWidget()
        grand_total_container.setStyleSheet("background: transparent; border: none;")
        grand_total_container_layout = QHBoxLayout(grand_total_container)
        grand_total_container_layout.setContentsMargins(0, 0, 0, 0)
        grand_total_container_layout.setSpacing(8)
        
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY}; background: {BACKGROUND}; padding: 6px 10px; border-radius: 6px;")
        self.grand_total_label.setMinimumWidth(120)
        grand_total_container_layout.addWidget(self.grand_total_label)
        
        # Add roundoff container beside grand total
        grand_total_container_layout.addWidget(self.roundoff_container)
        grand_total_container_layout.addStretch()
        
        self.totals_layout.addRow("Grand Total:", grand_total_container)
        
        from PySide6.QtWidgets import QDoubleSpinBox
        self.paid_amount_spin = QDoubleSpinBox()
        self.paid_amount_spin.setRange(0, 999999999)
        self.paid_amount_spin.setDecimals(2)
        self.paid_amount_spin.setPrefix("₹")
        self.paid_amount_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                font-size: 14px;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px;
                background: {WHITE};
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid {PRIMARY};
            }}
        """)
        self.paid_amount_spin.setFixedWidth(140)
        self.paid_amount_spin.setFixedHeight(30)
        self.paid_amount_spin.setValue(0)
        # totals_layout.addRow("Paid Amount:", self.paid_amount_spin)
        # Balance label - same size as Grand Total
        self.balance_label = QLabel("₹0.00")
        self.balance_label.setMinimumWidth(120)
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #EF4444; background: #FEF2F2; padding: 6px 10px; border-radius: 6px;")
        # Store reference to balance due row for show/hide functionality
        self.balance_due_row = self.totals_layout.rowCount()
        self.totals_layout.addRow("Balance Due:", self.balance_label)
        # Update balance when paid amount changes
        self.paid_amount_spin.valueChanged.connect(self.update_balance_due)
        layout.addStretch(1)
        layout.addLayout(self.totals_layout, 1)
        return frame

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
            self.roundoff_amount = roundoff_amount
            
            if roundoff_amount > 0:
                self.roundoff_value_label.setText(f"+₹{roundoff_amount:.2f}")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style(roundoff_amount))
            elif roundoff_amount < 0:
                self.roundoff_value_label.setText(f"-₹{abs(roundoff_amount):.2f}")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style(roundoff_amount))
            else:
                self.roundoff_value_label.setText("₹0.00")
                self.roundoff_value_label.setStyleSheet(get_roundoff_value_style(roundoff_amount))
            
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
            try:
                grand_total = 0.0
                try:
                    grand_total = float(self.grand_total_label.text().replace('₹','').replace(',',''))
                except Exception:
                    pass
                paid = self.paid_amount_spin.value()
                balance = max(0, grand_total - paid)
                self.balance_label.setText(f"₹{balance:,.2f}")
            except Exception:
                self.balance_label.setText("₹0.00")
            
    # Items management
    def quick_add_product(self, product_data):
        """Quickly add a product to the invoice from the quick-select chips"""
        try:
            # Check if party is selected first
            if hasattr(self, 'party_search'):
                party_text = self.party_search.text().strip()
                if not party_text:
                    highlight_error(self.party_search, "Please select a party first")
                    self.party_search.setFocus()
                    return
            
            # Check if there's an empty first row that we can fill instead of creating new
            first_item_widget = None
            for i in range(self.items_layout.count()):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    first_item_widget = widget
                    break
            
            # If first row exists and has no product selected, fill it instead of creating new row
            if first_item_widget and not first_item_widget.product_input.text().strip():
                item_widget = first_item_widget
            else:
                # Create a new item widget with the product pre-selected
                item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                item_widget.add_requested.connect(self.add_item)
                item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
                item_widget.item_changed.connect(self.update_totals)
                item_widget.setStyleSheet(get_item_widget_normal_style())
                # Add to layout
                self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
            
            # Pre-fill with the product data
            item_widget.product_input.setText(product_data.get('name', ''))
            item_widget.selected_product = product_data
            item_widget.rate_spin.setValue(product_data.get('sales_rate', 0))
            item_widget.unit_label.setText(product_data.get('unit', 'Piece'))
            item_widget.hsn_edit.setText(product_data.get('hsn_code', ''))
            
            # Set tax based on invoice type
            if hasattr(self, 'gst_combo') and self.gst_combo.currentText() == "Non-GST":
                item_widget.tax_spin.setValue(0)
            else:
                item_widget.tax_spin.setValue(product_data.get('tax_rate', 18))
            
            # Calculate total for the item
            item_widget.calculate_total()
            
            self.number_items()
            self.update_totals()
            
            # Focus on quantity field for quick entry
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.setFocus())
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.selectAll())
            
            # Brief success highlight
            highlight_success(item_widget.product_input, duration_ms=1000)
            
        except Exception as e:
            print(f"Quick add product error: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

    def add_item(self):
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
                product_text = last_item_widget.product_input.text().strip()
                if not product_text:
                    # Highlight the empty product field and show message
                    highlight_error(last_item_widget.product_input, "Please select a product first")
                    last_item_widget.product_input.setFocus()
                    return  # Don't add new row
        
        item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
        # Wire row-level ➕ to add another item row
        item_widget.add_requested.connect(self.add_item)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
        item_widget.item_changed.connect(self.update_totals)
        item_widget.setStyleSheet(get_item_widget_normal_style())
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        # Assign row numbers after insertion
        self.number_items()
        self.update_totals()
        
        # Auto-scroll to show the new row and set focus
        QTimer.singleShot(50, lambda: self.scroll_to_new_item(item_widget))

    def remove_item(self, item_widget):
        if self.items_layout.count() <= 2:
            QMessageBox.warning(self, "Cannot Remove", "🚫 At least one item is required for the invoice!")
            return
        reply = QMessageBox.question(self, "Remove Item", "❓ Are you sure you want to remove this item?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.items_layout.removeWidget(item_widget)
            item_widget.deleteLater()
            # Re-number items after removal
            self.number_items()
            self.update_totals()

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
        """Update the read-only row number textbox in each item row (1-based)."""
        try:
            row = 1
            for i in range(self.items_layout.count() - 1):  # exclude the stretch at the end
                w = self.items_layout.itemAt(i).widget()
                if isinstance(w, InvoiceItemWidget) and hasattr(w, 'set_row_number'):
                    w.set_row_number(row)
                    row += 1
        except Exception as e:
            print(f"Error numbering items: {e}")

    def update_totals(self):
        try:
            subtotal, total_discount, total_tax, item_count = 0, 0, 0, 0
            total_cgst, total_sgst, total_igst = 0, 0, 0
            
            # Get current tax type selection
            tax_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST - Same State'
            
            # Determine state based on tax type selection
            is_interstate = (tax_type == 'GST - Other State')
            is_non_gst = (tax_type == 'Non-GST')
            
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        quantity = item_data['quantity']
                        rate = item_data['rate']
                        item_subtotal = quantity * rate
                        subtotal += item_subtotal
                        total_discount += item_data['discount_amount']
                        total_tax += item_data['tax_amount']
                        item_count += 1
                        
                        # Calculate GST breakdown for this item
                        tax_amount = item_data['tax_amount']
                        if tax_amount > 0 and not is_non_gst:  # Only calculate GST breakdown if there's tax and not Non-GST
                            if is_interstate:
                                # Inter-state: All tax goes to IGST
                                total_igst += tax_amount
                            else:
                                # Intra-state: Split between CGST and SGST
                                cgst_amount = tax_amount / 2
                                sgst_amount = tax_amount / 2
                                total_cgst += cgst_amount
                                total_sgst += sgst_amount
            
            grand_total = subtotal - total_discount + total_tax
            
            # Update items section subtotal label
            if hasattr(self, 'items_subtotal_label'):
                self.items_subtotal_label.setText(f"₹{subtotal:,.2f}")
            
            # Update all totals labels
            self.subtotal_label.setText(f"₹{subtotal:,.2f}")
            self.discount_label.setText(f"-₹{total_discount:,.2f}")
            self.cgst_label.setText(f"₹{total_cgst:,.2f}")
            self.sgst_label.setText(f"₹{total_sgst:,.2f}")
            self.igst_label.setText(f"₹{total_igst:,.2f}")
            self.tax_label.setText(f"₹{total_tax:,.2f}")
            self.grand_total_label.setText(f"₹{grand_total:,.2f}")
            
            # Update tax breakdown box beside Tax amount
            if hasattr(self, 'tax_breakdown_box'):
                if not is_non_gst and total_tax > 0:
                    if is_interstate:
                        # Show IGST breakdown with HTML formatting (secondary text for label, primary text for price)
                        self.tax_breakdown_box.setText(f"<span style='color: {TEXT_SECONDARY};'>IGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_igst:,.2f}</span>")
                    else:
                        # Show CGST + SGST breakdown with HTML formatting
                        self.tax_breakdown_box.setText(f"<span style='color: {TEXT_SECONDARY};'>CGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_cgst:,.2f}</span> + <span style='color: {TEXT_SECONDARY};'>SGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_sgst:,.2f}</span>")
                    self.tax_breakdown_box.setVisible(True)
                else:
                    self.tax_breakdown_box.setVisible(False)
            
            # Update amount in words via controller
            if hasattr(self, 'amount_in_words_label'):
                self.amount_in_words_label.setText(
                    invoice_form_controller.number_to_words_indian(grand_total)
                )
            
            # Check if grand total has decimal (for round-off)
            has_decimal = (grand_total % 1) != 0
            if hasattr(self, 'roundoff_container'):
                self.roundoff_container.setVisible(has_decimal and grand_total > 0)
            
            # Get bill type for Balance Due visibility
            bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH'
            is_credit = (bill_type == 'CREDIT')
            
            # ========== VISIBILITY LOGIC ==========
            # 1) CASH, No Tax, No Disc → Grand Total only
            # 2) CREDIT, No Tax, No Disc → Grand Total + Balance Due
            # 3) CREDIT, Tax, No Disc → Tax (with breakdown) + Grand Total + Balance Due
            # 4) CREDIT, Tax, Disc → Disc + Tax (with breakdown) + Grand Total + Balance Due
            
            has_tax = (total_tax > 0 and not is_non_gst)
            has_discount = (total_discount > 0)
            
            # Show/hide Discount row
            if hasattr(self, 'discount_label'):
                # Find and hide discount row in form layout
                for i in range(self.totals_layout.rowCount()):
                    label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                    if label_item and label_item.widget():
                        label_text = label_item.widget().text()
                        if label_text == "Discount:":
                            label_item.widget().setVisible(has_discount)
                            if field_item and field_item.widget():
                                field_item.widget().setVisible(has_discount)
            
            # Show/hide Tax row (with breakdown box)
            if hasattr(self, 'tax_row_label'):
                self.tax_row_label.setVisible(has_tax)
                # Find tax container in form layout
                for i in range(self.totals_layout.rowCount()):
                    label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                    if label_item and label_item.widget() == self.tax_row_label:
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(has_tax)
            
            # Show/hide Balance Due row (only for CREDIT)
            for i in range(self.totals_layout.rowCount()):
                label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                if label_item and label_item.widget():
                    label_text = label_item.widget().text()
                    if label_text == "Balance Due:":
                        label_item.widget().setVisible(is_credit)
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(is_credit)
            
            # Update item count badge
            if hasattr(self, 'item_count_badge'):
                self.item_count_badge.setText(str(item_count))
                # Change badge color based on item count
                if item_count == 0:
                    badge_color = TEXT_SECONDARY
                elif item_count >= 5:
                    badge_color = SUCCESS
                else:
                    badge_color = PRIMARY
                self.item_count_badge.setStyleSheet(get_item_count_badge_style(item_count))
            
            self.update_balance_due()
        except Exception as e:
            print(f"Error updating totals: {e}")

    def save_invoice(self):
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
                if item_data:
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
        
        # Validate via controller
        is_new = not self.invoice_data
        is_valid, error_msg, field_name = invoice_form_controller.validate_invoice_data(
            invoice_no, party_data.get('id'), items, is_new
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
            'invoice_type': self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST - Same State',
            'bill_type': self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH',
            'notes': notes_text,
            'round_off': getattr(self, 'roundoff_amount', 0.0),
        }
        
        if self.invoice_data:
            invoice_data_dict['id'] = self.invoice_data.get('id') or self.invoice_data.get('invoice', {}).get('id')
        
        # Save via controller
        result = invoice_form_controller.save_invoice(
            invoice_data_dict,
            items,
            is_update=not is_new,
            status='Draft'
        )
        
        if result.success:
            # Update invoice number display if it was changed
            if result.invoice_no and hasattr(self, 'invoice_number'):
                self.invoice_number.setText(result.invoice_no)
            
            highlight_success(self.invoice_number)
            QMessageBox.information(self, "Success", f"✅ {result.message}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"❌ {result.message}")

    def reset_form(self):
        """Reset all form fields to defaults and update date to today"""
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
            
            # Clear party search
            if hasattr(self, 'party_search') and self.party_search is not None:
                self.party_search.clear()
                # Repopulate party data map from parties list (don't clear it completely)
                if hasattr(self, 'party_data_map'):
                    self.party_data_map = {}
                    # Repopulate from self.parties
                    for party in self.parties:
                        name = party.get('name', '').upper()
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
                
                # Add one new empty item
                self.add_item()
            
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


