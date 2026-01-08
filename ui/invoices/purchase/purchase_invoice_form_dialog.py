"""
Purchase Invoice Dialog - Dialog for creating/editing purchase invoices.
Uses separate purchase_invoices table instead of the invoices table.
Extends the base InvoiceDialog functionality with purchase-specific behavior.
"""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer

from ui.invoices.sales.sales_invoice_form_dialog import InvoiceDialog, InvoiceItemWidget
from core.db.sqlite_db import db
from theme import BACKGROUND


class PurchaseInvoiceDialog(QDialog):
    """Dialog for creating/editing purchase invoices - wraps InvoiceDialog with purchase-specific settings"""
    
    def __init__(self, parent=None, invoice_data=None, invoice_number=None, read_only=False):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.read_only = read_only
        self.invoice_number = invoice_number
        
        # Create the underlying invoice dialog with purchase settings
        self._inner_dialog = PurchaseInvoiceDialogInner(
            parent=self,
            invoice_data=invoice_data,
            invoice_number=invoice_number,
            read_only=read_only
        )
        
    def exec_(self):
        """Execute the inner dialog"""
        result = self._inner_dialog.exec_()
        # Mirror the result to this dialog
        if result == QDialog.Accepted:
            self.accept()
        else:
            self.reject()
        return result


class PurchaseInvoiceDialogInner(InvoiceDialog):
    """Inner dialog that extends InvoiceDialog with purchase-specific behavior"""
    
    def __init__(self, parent=None, invoice_data=None, invoice_number=None, read_only=False):
        # Mark this as a purchase invoice dialog
        self._is_purchase = True
        
        # Call parent constructor
        super().__init__(parent, invoice_data, invoice_number, read_only)
        
        # Set purchase invoice number AFTER parent init completes (only for new invoices)
        if not invoice_data and hasattr(self, 'invoice_number'):
            self.invoice_number.setText(self.generate_invoice_number())
        
        # Apply purchase-specific styling after UI is setup
        QTimer.singleShot(100, self.apply_purchase_styling)
    
    def init_window(self):
        """Initialize window properties with purchase-specific styling"""
        title = "🛒 Create Purchase Invoice" if not self.invoice_data else "🛒 Edit Purchase Invoice"
        if self.read_only:
            title = "🛒 View Purchase Invoice"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1200, 900)
        # Use amber/orange theme for purchases
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFBEB, stop:1 #FEF3C7);
                border: 2px solid #FCD34D;
                border-radius: 15px;
            }}
        """)
    
    def apply_purchase_styling(self):
        """Apply purchase-specific styling to differentiate from sales invoices"""
        try:
            # Update window title if in read-only mode
            if self.read_only and hasattr(self, 'invoice_number'):
                invoice_no = self.invoice_number.text() if hasattr(self.invoice_number, 'text') else 'Invoice'
                self.setWindowTitle(f"🛒 View Purchase Invoice - {invoice_no} (Read Only)")
        except Exception as e:
            print(f"Error applying purchase styling: {e}")
    
    def setup_action_buttons(self):
        """Setup action buttons - only Save Print for purchase invoices"""
        from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton
        from PyQt5.QtCore import Qt
        from theme import WHITE, BORDER, WARNING, DANGER, PRIMARY
        
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; padding: 8px; }}
        """)
        button_container.setFixedHeight(70)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(15, 10, 15, 10)
        
        # Utility buttons (left side)
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(8)
        self.help_button = self.create_action_button("❓ Help", "help", WARNING, self.show_help, "Get help with invoice creation")
        utility_layout.addWidget(self.help_button)
        button_layout.addLayout(utility_layout)
        button_layout.addStretch()
        
        # Action buttons (right side)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.cancel_button = self.create_action_button("❌ Cancel", "cancel", DANGER, self.reject, "Cancel and close without saving")
        action_layout.addWidget(self.cancel_button)
        
        # Reset button
        self.reset_button = self.create_action_button("🔄 Reset", "reset", WARNING, self.reset_form, "Clear all values and reset to defaults")
        action_layout.addWidget(self.reset_button)
        
        # Only Save Print button (no separate Save Invoice button)
        save_text = "💾 Save Print" if not self.invoice_data else "💾 Update & Print"
        self.save_print_button = self.create_action_button(save_text, "save_print", PRIMARY, self.save_and_print, "Save purchase invoice and open print preview")
        action_layout.addWidget(self.save_print_button)
        
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container)

    def load_data(self):
        """Load products and suppliers data"""
        try:
            self.products = db.get_products() or []
            # For purchase invoices, filter parties to show only Suppliers
            all_parties = db.get_parties() or []
            self.parties = [p for p in all_parties if p.get('party_type', '').lower() == 'supplier']
            
            # If no suppliers found, show all parties as fallback
            if not self.parties:
                self.parties = all_parties
                
        except Exception as e:
            print(f"Database error: {e}")
            self.products = []
            self.parties = []
    
    def generate_invoice_number(self):
        """Generate purchase invoice number with PUR prefix from purchase_invoices table"""
        try:
            # Get the last purchase invoice number from the separate table (filtered by company)
            company_id = db.get_current_company_id()
            if hasattr(db, '_query'):
                if company_id:
                    result = db._query(
                        "SELECT invoice_no FROM purchase_invoices WHERE company_id = ? ORDER BY id DESC LIMIT 1",
                        (company_id,)
                    )
                else:
                    result = db._query(
                        "SELECT invoice_no FROM purchase_invoices ORDER BY id DESC LIMIT 1"
                    )
                if result and result[0].get('invoice_no'):
                    last_no = result[0]['invoice_no']
                    # Extract number from format like PUR-001
                    if last_no.startswith('PUR-'):
                        try:
                            num = int(last_no.split('-')[1]) + 1
                            return f"PUR-{num:03d}"
                        except (ValueError, IndexError):
                            pass
            
            # Get count of purchase invoices + 1 (filtered by company)
            if hasattr(db, '_query'):
                if company_id:
                    result = db._query("SELECT COUNT(*) as count FROM purchase_invoices WHERE company_id = ?", (company_id,))
                else:
                    result = db._query("SELECT COUNT(*) as count FROM purchase_invoices")
                count = result[0]['count'] if result else 0
                return f"PUR-{count + 1:03d}"
            
            return "PUR-001"
            
        except Exception as e:
            print(f"Error generating purchase number: {e}")
            return "PUR-001"
    
    def get_selected_party_label(self):
        """Override to show 'Supplier' instead of 'Customer/Party'"""
        return "Supplier"
    
    def save_invoice(self, final=False):
        """Save purchase invoice to separate purchase_invoices table"""
        print("DEBUG: save_invoice called")
        try:
            # Validate required fields
            if not self.validate_invoice():
                print("DEBUG: validate_invoice returned False")
                return
            
            print("DEBUG: validation passed")
            # Get supplier
            party_name = self.party_search.text().strip() if hasattr(self, 'party_search') else ''
            print(f"DEBUG: party_name = '{party_name}'")
            supplier_id = None
            if party_name:
                for party in self.parties:
                    if party['name'].upper() == party_name.upper():
                        supplier_id = party['id']
                        break
            
            print(f"DEBUG: supplier_id = {supplier_id}")
            if not supplier_id:
                QMessageBox.warning(self, "Validation Error", "Please select a valid supplier.")
                return
            
            # Collect item data
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            if not items:
                QMessageBox.warning(self, "Validation Error", "Please add at least one item to the purchase invoice.")
                return
            
            # Calculate totals
            grand_total = sum(item['amount'] for item in items)
            
            # Get invoice details
            invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else self.generate_invoice_number()
            invoice_date = self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else ''
            invoice_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST'
            status = 'Paid' if final else 'Unpaid'
            
            # Check if editing existing purchase invoice
            if self.invoice_data and self.invoice_data.get('invoice', {}).get('id'):
                purchase_id = self.invoice_data['invoice']['id']
                
                # Update existing purchase invoice in purchase_invoices table
                db.update_purchase_invoice({
                    'id': purchase_id,
                    'invoice_no': invoice_no,
                    'date': invoice_date,
                    'supplier_id': supplier_id,
                    'grand_total': grand_total,
                    'status': status,
                    'type': invoice_type
                })
                
                # Delete old items and add new ones
                db.delete_purchase_invoice_items(purchase_id)
                for item in items:
                    db.add_purchase_invoice_item(
                        purchase_invoice_id=purchase_id,
                        product_id=item['product_id'],
                        product_name=item['product_name'],
                        hsn_code=item.get('hsn_no', ''),
                        quantity=item['quantity'],
                        unit=item.get('unit', 'Piece'),
                        rate=item['rate'],
                        discount_percent=item['discount_percent'],
                        discount_amount=item['discount_amount'],
                        tax_percent=item['tax_percent'],
                        tax_amount=item['tax_amount'],
                        amount=item['amount']
                    )
                
                # Update stock for purchase items (only for products with track_stock enabled)
                db.update_stock_for_purchase_items(items)
                
                QMessageBox.information(self, "Success", f"Purchase invoice {invoice_no} updated successfully!")
            else:
                # Create new purchase invoice in purchase_invoices table
                print(f"DEBUG: Saving new purchase invoice: {invoice_no}, supplier_id: {supplier_id}, grand_total: {grand_total}")
                purchase_id = db.add_purchase_invoice(
                    invoice_no=invoice_no,
                    date=invoice_date,
                    supplier_id=supplier_id,
                    invoice_type=invoice_type,
                    grand_total=grand_total,
                    status=status
                )
                print(f"DEBUG: Purchase invoice saved with ID: {purchase_id}")
                
                # Add purchase invoice items to purchase_invoice_items table
                for item in items:
                    db.add_purchase_invoice_item(
                        purchase_invoice_id=purchase_id,
                        product_id=item['product_id'],
                        product_name=item['product_name'],
                        hsn_code=item.get('hsn_no', ''),
                        quantity=item['quantity'],
                        unit=item.get('unit', 'Piece'),
                        rate=item['rate'],
                        discount_percent=item['discount_percent'],
                        discount_amount=item['discount_amount'],
                        tax_percent=item['tax_percent'],
                        tax_amount=item['tax_amount'],
                        amount=item['amount']
                    )
                
                # Update stock for purchase items (only for products with track_stock enabled)
                db.update_stock_for_purchase_items(items)
                
                QMessageBox.information(self, "Success", f"Purchase invoice {invoice_no} saved successfully!")
            
            # Disable editing if final
            if final:
                self.disable_editing_after_final_save()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save purchase invoice: {str(e)}")
            print(f"Error saving purchase invoice: {e}")
    
    def save_and_print(self):
        """Save purchase invoice and open print preview"""
        try:
            # Validate invoice
            if not self.validate_invoice():
                return
            
            # Get supplier
            party_name = self.party_search.text().strip() if hasattr(self, 'party_search') else ''
            supplier_id = None
            if party_name:
                for party in self.parties:
                    if party['name'].upper() == party_name.upper():
                        supplier_id = party['id']
                        break
            
            if not supplier_id:
                QMessageBox.warning(self, "Validation Error", "Please select a valid supplier.")
                return
            
            # Collect item data
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            if not items:
                QMessageBox.warning(self, "Validation Error", "Please add at least one item to the purchase invoice.")
                return
            
            # Calculate totals
            grand_total = sum(item['amount'] for item in items)
            
            # Get invoice details
            invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else self.generate_invoice_number()
            invoice_date = self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else ''
            invoice_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST'
            status = 'Paid'  # Final invoices are marked as Paid
            
            # Check if editing existing purchase invoice
            if self.invoice_data and self.invoice_data.get('invoice', {}).get('id'):
                purchase_id = self.invoice_data['invoice']['id']
                
                # Update existing purchase invoice
                db.update_purchase_invoice({
                    'id': purchase_id,
                    'invoice_no': invoice_no,
                    'date': invoice_date,
                    'supplier_id': supplier_id,
                    'grand_total': grand_total,
                    'status': status,
                    'type': invoice_type
                })
                
                # Delete old items and add new ones
                db.delete_purchase_invoice_items(purchase_id)
                for item in items:
                    db.add_purchase_invoice_item(
                        purchase_invoice_id=purchase_id,
                        product_id=item['product_id'],
                        product_name=item['product_name'],
                        hsn_code=item.get('hsn_no', ''),
                        quantity=item['quantity'],
                        unit=item.get('unit', 'Piece'),
                        rate=item['rate'],
                        discount_percent=item['discount_percent'],
                        discount_amount=item['discount_amount'],
                        tax_percent=item['tax_percent'],
                        tax_amount=item['tax_amount'],
                        amount=item['amount']
                    )
                
                # Update stock
                db.update_stock_for_purchase_items(items)
                
            else:
                # Create new purchase invoice
                purchase_id = db.add_purchase_invoice(
                    invoice_no=invoice_no,
                    date=invoice_date,
                    supplier_id=supplier_id,
                    invoice_type=invoice_type,
                    grand_total=grand_total,
                    status=status
                )
                
                # Add purchase invoice items
                for item in items:
                    db.add_purchase_invoice_item(
                        purchase_invoice_id=purchase_id,
                        product_id=item['product_id'],
                        product_name=item['product_name'],
                        hsn_code=item.get('hsn_no', ''),
                        quantity=item['quantity'],
                        unit=item.get('unit', 'Piece'),
                        rate=item['rate'],
                        discount_percent=item['discount_percent'],
                        discount_amount=item['discount_amount'],
                        tax_percent=item['tax_percent'],
                        tax_amount=item['tax_amount'],
                        amount=item['amount']
                    )
                
                # Update stock
                db.update_stock_for_purchase_items(items)
            
            # Show print preview
            try:
                from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
                show_invoice_preview(self, purchase_id, is_purchase=True)
            except Exception as print_error:
                print(f"Print preview error: {print_error}")
                QMessageBox.information(self, "Success", f"Purchase invoice {invoice_no} saved successfully!\n\n(Print preview not available)")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save and print purchase invoice: {str(e)}")
            print(f"Error in save_and_print: {e}")

    def validate_invoice(self):
        """Validate invoice data before saving"""
        # Check party
        party_name = self.party_search.text().strip() if hasattr(self, 'party_search') else ''
        if not party_name:
            QMessageBox.warning(self, "Validation Error", "Please select a supplier.")
            if hasattr(self, 'party_search'):
                self.party_search.setFocus()
            return False
        
        # Check at least one valid item
        has_items = False
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                if item_data:
                    has_items = True
                    break
        
        if not has_items:
            QMessageBox.warning(self, "Validation Error", "Please add at least one item.")
            return False
        
        return True
    
    def populate_invoice_data(self):
        """Populate form fields with existing purchase invoice data"""
        if not self.invoice_data:
            return
        
        try:
            invoice = self.invoice_data['invoice']
            party = self.invoice_data.get('party')
            items = self.invoice_data.get('items', [])
            
            # Set invoice number
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setText(invoice.get('invoice_no', ''))
            
            # Set dates
            if hasattr(self, 'invoice_date'):
                from PyQt5.QtCore import QDate
                date_str = invoice.get('date', '')
                if date_str:
                    date_obj = QDate.fromString(date_str, 'yyyy-MM-dd')
                    self.invoice_date.setDate(date_obj)
            
            # Set supplier
            if hasattr(self, 'party_search') and party:
                self.party_search.setText(party.get('name', ''))
            
            # Set invoice type (GST/Non-GST) if available
            if hasattr(self, 'gst_combo') and invoice.get('tax_type'):
                index = self.gst_combo.findText(invoice['tax_type'])
                if index >= 0:
                    self.gst_combo.setCurrentIndex(index)
            
            # Populate items
            if items:
                # Clear ALL existing item widgets
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
                    item_widget.product_input.setText(item_data.get('product_name', ''))
                    
                    # Set HSN code
                    item_widget.hsn_edit.setText(item_data.get('hsn_code', ''))
                    
                    # Set values
                    item_widget.quantity_spin.setValue(item_data.get('quantity', 0))
                    item_widget.rate_spin.setValue(item_data.get('rate', 0))
                    item_widget.discount_spin.setValue(item_data.get('discount_percent', 0))
                    item_widget.tax_spin.setValue(item_data.get('tax_percent', 0))
                    
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
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error populating purchase invoice data: {str(e)}")
            print(f"Error populating purchase invoice data: {e}")
