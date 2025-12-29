"""
Standalone InvoiceDialog for creating/editing invoices.
Extracted from screens/invoices.py to avoid a huge single file.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QAction, QShortcut, QListWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QKeySequence
from PyQt5.QtWidgets import QCompleter
from .party_selector import PartySelector, ProductSelector

from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER
)
from database import db


class InvoiceItemWidget(QWidget):
    """Enhanced widget for invoice line items with better styling and validation"""
    
    item_changed = pyqtSignal()  # Signal for when item data changes
    add_requested = pyqtSignal()  # Signal to request adding a new item row
    
    def __init__(self, item_data=None, products=None):
        super().__init__()
        self.products = products or []
        self._product_selector_active = False
        self.setup_ui()
        if item_data:
            self.populate_data(item_data)
        self.setFixedHeight(50)  # Consistent height for all items
    
    def setup_ui(self):
        """Setup enhanced item widget UI with better styling"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(1)
        
        # Enhanced styling for all widgets
        widget_style = f"""
            QComboBox, QDoubleSpinBox, QSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
                border-color: {BORDER};
                background: #F8FAFC;
            }}
            QComboBox:hover, QDoubleSpinBox:hover, QSpinBox:hover {{
                border-color: {BORDER};
            }}
        """

        # Row number (read-only textbox) aligned with "No" header
        self.row_no_edit = QLineEdit()
        self.row_no_edit.setReadOnly(True)
        self.row_no_edit.setFixedWidth(100)
        self.row_no_edit.setFixedHeight(45)
        self.row_no_edit.setAlignment(Qt.AlignCenter)
        self.row_no_edit.setFocusPolicy(Qt.NoFocus)
        self.row_no_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 0;
                border-radius: 6px;
                padding: 0;
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(self.row_no_edit)
        
        # Product selection: QLineEdit with suggestion box (QCompleter)
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("🛍️ Type to select product…")
        self.product_input.setFixedWidth(500)
        self.product_input.setFixedHeight(40)
        self.product_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {BORDER};
                background: #F8FAFC;
            }}
        """)
        # Build completer data
        self._product_map = {}
        product_names = []
        for p in (self.products or []):
            name = p.get('name', '').strip()
            if name:
                self._product_map[name] = p
                product_names.append(name)

        layout.addWidget(self.product_input)
        layout.setSpacing(20)

        try:
            self.product_input.textEdited.connect(self.on_product_search_edited)
        except Exception:
            pass
        # Enter opens selector
        try:
            self.product_input.returnPressed.connect(self.open_product_selector)
        except Exception:
            pass

        # HSN No entry box
        self.hsn_edit = QLineEdit()
        self.hsn_edit.setPlaceholderText("HSN")
        self.hsn_edit.setFixedWidth(100)
        self.hsn_edit.setFixedHeight(40)
        self.hsn_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
        """)
        self.hsn_edit.setToolTip("HSN code for the product")
        layout.addWidget(self.hsn_edit)

        
        # Quantity with validation
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setFixedWidth(100)
        self.quantity_spin.setFixedHeight(40)
        self.quantity_spin.setStyleSheet(widget_style)
        self.quantity_spin.setToolTip("Enter quantity")
        self.quantity_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.quantity_spin)
        
        # Unit display with better styling
        self.unit_label = QLabel("Piece")
        self.unit_label.setFixedWidth(85)
        self.unit_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                font-style: italic;
                padding: 6px;
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        self.unit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.unit_label)
        
        # Rate with currency prefix
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 999999.99)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setPrefix("₹")
        self.rate_spin.setFixedWidth(110)
        self.rate_spin.setFixedHeight(40)
        self.rate_spin.setStyleSheet(widget_style)
        self.rate_spin.setToolTip("Enter rate per unit")
        self.rate_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.rate_spin)
        
        # Discount percentage
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setSuffix("%")
        self.discount_spin.setFixedWidth(110)
        self.discount_spin.setFixedHeight(40)
        self.discount_spin.setStyleSheet(widget_style)
        self.discount_spin.setToolTip("Discount percentage")
        self.discount_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.discount_spin)
        
        # Tax percentage
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 100)
        self.tax_spin.setDecimals(2)
        self.tax_spin.setValue(18)
        self.tax_spin.setSuffix("%")
        self.tax_spin.setFixedWidth(110)
        self.tax_spin.setFixedHeight(40)
        self.tax_spin.setStyleSheet(widget_style)
        self.tax_spin.setToolTip("Tax percentage (GST)")
        self.tax_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.tax_spin)        
        
        # Amount display with enhanced styling
        self.amount_label = QLabel("₹0.00")
        self.amount_label.setFixedWidth(110)
        self.amount_label.setFixedHeight(45)
        self.amount_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold; 
                color: {PRIMARY};
                font-size: 14px;
                padding: 8px;
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        self.amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.amount_label)

        # Enhanced add button
        self.add_btn = QPushButton("➕")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: {WHITE};
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: #059669;

                color: {WHITE};
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: #059669;

            }}
            QPushButton:pressed {{
                background: #B91C1C;
            }}
        """)
        self.add_btn.setToolTip("Add this item")
        # Emit signal so parent can add a new row
        self.add_btn.clicked.connect(self.add_requested.emit)
        layout.addWidget(self.add_btn)

        # Enhanced remove button
        self.remove_btn = QPushButton("✖")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER};
                color: {WHITE};
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: #DC2626;

            }}
            QPushButton:pressed {{
                background: #B91C1C;
            }}
        """)
        self.remove_btn.setToolTip("Remove this item")
        layout.addWidget(self.remove_btn)

        # layout.setAlignment(self.product_combo, Qt.AlignLeft)
        layout.setAlignment(self.hsn_edit, Qt.AlignLeft)
        layout.setAlignment(self.quantity_spin, Qt.AlignLeft)
        layout.setAlignment(self.unit_label, Qt.AlignLeft)
        layout.setAlignment(self.rate_spin, Qt.AlignLeft)
        layout.setAlignment(self.discount_spin, Qt.AlignLeft)
        layout.setAlignment(self.tax_spin, Qt.AlignLeft)
        layout.setAlignment(self.remove_btn, Qt.AlignCenter)
        layout.setAlignment(self.amount_label, Qt.AlignCenter)

    def set_row_number(self, n: int):
        """Set the display number for this row (1-based)."""
        try:
            self.row_no_edit.setText(str(n))
        except Exception:
            pass

    def on_product_search_edited(self, text: str):
        """Open ProductSelector when user types in the product search box.
        Prefill selector search with typed text and avoid opening multiple times.
        """
        try:
            if self._product_selector_active:
                return
            if not text or not text.strip():
                return
            self._product_selector_active = True
            selected = self._open_product_selector_dialog(prefill_text=text)
            if selected:
                # Set chosen product name back to the input without re-triggering textEdited
                old_state = self.product_input.blockSignals(True)
                try:
                    self.product_input.setText(selected)
                    # Immediately apply selected product data to rate/discount/tax/unit
                    try:
                        self.on_product_selected(selected)
                    except Exception as _e:
                        print(f"on_product_selected failed: {_e}")
                finally:
                    self.product_input.blockSignals(old_state)
        except Exception as e:
            print(f"Product search edit handler error: {e}")
        finally:
            self._product_selector_active = False

    # The following helper sections mirror the original dialog
    def open_product_selector(self):
        try:
            selected = self._open_product_selector_dialog()
            if selected:
                self.product_input.setText(selected)
                # Apply selected product to update dependent fields
                try:
                    self.on_product_selected(selected)
                except Exception as _e:
                    print(f"on_product_selected failed: {_e}")
        except Exception as e:
            print(f"Product selector failed: {e}")

    def _open_product_selector_dialog(self, prefill_text: str = None):
        """Create, size, position and open the ProductSelector below the input.
        Returns the selected name if accepted, else None.
        """
        dlg = ProductSelector(self.products, self)
        # Prefill search
        try:
            if prefill_text:
                dlg.search.setText(prefill_text)
                dlg.search.setCursorPosition(len(prefill_text))
        except Exception:
            pass
        # Size and position
        try:
            from PyQt5.QtWidgets import QApplication
            input_w = max(300, self.product_input.width())
            dlg_h = min(dlg.sizeHint().height(), 420)
            margin = 8  # vertical gap to avoid overlap with the input
            dlg.resize(input_w, dlg_h)
            bl = self.product_input.mapToGlobal(self.product_input.rect().bottomLeft())
            x, y = bl.x(), bl.y() + margin
            screen = QApplication.desktop().availableGeometry(self.product_input)
            if y + dlg_h > screen.bottom():
                tl = self.product_input.mapToGlobal(self.product_input.rect().topLeft())
                y = tl.y() - dlg_h - margin
            if x + input_w > screen.right():
                x = max(screen.left(), screen.right() - input_w)
            dlg.move(int(x), int(y+65))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec_() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None

    def on_product_selected(self, name: str):
        """Handle product selection from completer and update fields"""
        product_data = self._product_map.get(name)
        self.selected_product = product_data
        if product_data:
            self.rate_spin.setValue(product_data.get('sales_rate', 0))
            self.tax_spin.setValue(product_data.get('tax_rate', 18))
            self.unit_label.setText(product_data.get('unit', 'Piece'))
            
            # Auto-apply product discount if available
            if 'discount_percent' in product_data:
                self.discount_spin.setValue(product_data.get('discount_percent', 0))
            
            self.calculate_total()
            self.item_changed.emit()
    
    def calculate_total(self):
        """Calculate line item total with improved precision"""
        try:
            quantity = self.quantity_spin.value()
            rate = self.rate_spin.value()
            discount_percent = self.discount_spin.value()
            tax_percent = self.tax_spin.value()
            
            # Calculate subtotal after discount
            subtotal = quantity * rate
            discount_amount = subtotal * (discount_percent / 100)
            after_discount = subtotal - discount_amount
            
            # Calculate tax
            tax_amount = after_discount * (tax_percent / 100)
            total = after_discount + tax_amount
            
            # Update display with animation-like effect
            self.amount_label.setText(f"₹{total:,.2f}")
            
            # Change color based on amount
            if total > 10000:
                color = SUCCESS
            elif total > 5000:
                color = PRIMARY
            else:
                color = TEXT_PRIMARY
                
            self.amount_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold; 
                    color: {color};
                    font-size: 14px;
                    padding: 8px;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid {color};
                    border-radius: 6px;
                }}
            """)
            
            # Emit signal to update parent totals
            self.item_changed.emit()
            
        except Exception as e:
            print(f"Error calculating total: {e}")
            self.amount_label.setText("₹0.00")
    
    def get_item_data(self):
        """Get item data as dictionary"""
        # Use the selected product from completer or fallback to typed name lookup
        product_data = getattr(self, 'selected_product', None)
        if not product_data and hasattr(self, 'product_input'):
            name = self.product_input.text().strip()
            if name and hasattr(self, '_product_map'):
                product_data = self._product_map.get(name)
        if not product_data:
            return None
        
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()
        discount_percent = self.discount_spin.value()
        tax_percent = self.tax_spin.value()
        
        subtotal = quantity * rate
        discount_amount = subtotal * (discount_percent / 100)
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        
        return {
            'product_id': product_data.get('id'),
            'product_name': product_data.get('name') or self.product_input.text().strip(),
            'hsn_no': self.hsn_edit.text().strip(),
            'quantity': quantity,
            'unit': product_data.get('unit', 'Piece'),
            'rate': rate,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'tax_percent': tax_percent,
            'tax_amount': tax_amount,
            'amount': total
        }


class InvoiceDialog(QDialog):
    """Enhanced dialog for creating/editing invoices with modern UI"""
    def __init__(self, parent=None, invoice_data=None, invoice_number=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.products = []
        self.parties = []
        # Guard to avoid re-entrant opening of PartySelector from typing
        self._party_selector_active = False

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

        # Force maximize after everything is set up
        QTimer.singleShot(100, self.ensure_maximized)

    def load_existing_invoice(self, invoice_number):
        """Load existing invoice data by invoice number"""
        try:
            invoice_data = db.get_invoice_with_items(invoice_number)
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
                from PyQt5.QtCore import QDate
                date_obj = QDate.fromString(invoice['date'], 'yyyy-MM-dd')
                self.invoice_date.setDate(date_obj)
            
            # Set party
            if hasattr(self, 'party_search') and party:
                self.party_search.setText(party['name'])
            
            # Populate items
            if items:
                # Clear existing items first
                for i in reversed(range(self.items_layout.count() - 1)):
                    item_widget = self.items_layout.itemAt(i).widget()
                    if isinstance(item_widget, InvoiceItemWidget):
                        self.items_layout.removeWidget(item_widget)
                        item_widget.deleteLater()
                
                # Add items from database
                for item_data in items:
                    item_widget = InvoiceItemWidget(products=self.products)
                    
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
                    
                    # Connect signals
                    item_widget.add_requested.connect(self.add_item)
                    item_widget.remove_btn.clicked.connect(lambda checked, w=item_widget: self.remove_item(w))
                    item_widget.item_changed.connect(self.update_totals)
                    
                    # Add to layout
                    self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
                
                # Update row numbers and totals
                self.number_items()
                self.update_totals()
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error populating invoice data: {str(e)}")

    def ensure_maximized(self):
        """Ensure the window is properly maximized"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        self.setWindowState(Qt.WindowMaximized)
        self.showMaximized()

    def init_window(self):
        """Initialize window properties and styling"""
        title = "📄 Create Invoice" if not self.invoice_data else "📝 Edit Invoice"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1200, 900)
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {BACKGROUND}, stop:1 #F8FAFC);
                border: 2px solid {BORDER};
                border-radius: 15px;
            }}
        """)

    def load_data(self):
        """Load products and parties data with error handling"""
        try:
            self.products = db.get_products() or []
            self.parties = db.get_parties() or []
        except Exception as e:
            print(f"Database error: {e}")
            # Fallback sample data
            self.products = [
                {'id': 1, 'name': 'Dell Laptop XPS 13', 'selling_price': 75000, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 2, 'name': 'iPhone 14 Pro', 'selling_price': 120000, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 3, 'name': 'Web Development Service', 'selling_price': 50000, 'tax_rate': 18, 'unit': 'Hour', 'type': 'Service'},
                {'id': 4, 'name': 'Office Chair', 'selling_price': 8500, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 5, 'name': 'Wireless Mouse', 'selling_price': 2500, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'}
            ]
            self.parties = [
                {'id': 1, 'name': 'ABC Corporation', 'gst_number': '27AABCU9603R1Z0', 'phone': '+91 98765 43210'},
                {'id': 2, 'name': 'XYZ Limited', 'gst_number': '27AABCU9603R1Z1', 'phone': '+91 98765 43211'},
                {'id': 3, 'name': 'Tech Solutions Pvt Ltd', 'gst_number': '27AABCU9603R1Z2', 'phone': '+91 98765 43212'}
            ]

    def setup_ui(self):
        """Setup enhanced dialog UI with modern design and better organization"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30 , 30, 30, 100)
        self.setup_content_sections()
        self.setup_action_buttons()
        self.apply_final_styling()
        # Connect date changes to update due days
        try:
            if hasattr(self, 'invoice_date') and hasattr(self, 'due_date') and hasattr(self, 'due_days_spin'):
                self.invoice_date.dateChanged.connect(self.update_due_days)
                self.due_date.dateChanged.connect(self.update_due_days)
                self.update_due_days()  # Set initial value
        except Exception:
            pass
# At end of InvoiceDialog class
    def update_due_days(self):
        """Calculate and update Due Days based on invoice and due date."""
        try:
            inv_date = self.invoice_date.date()
            due_date = self.due_date.date()
            days = inv_date.daysTo(due_date)
            self.due_days_spin.setValue(max(0, days))
        except Exception:
            pass

    def setup_content_sections(self):
        """Setup the main content sections with enhanced layout"""
        self.content_splitter = QSplitter(Qt.Vertical)
        # self.content_splitter.setStyleSheet(f"""
        #     QSplitter {{ border: none; background: transparent; }}
        #     QSplitter::handle {{ background: {BORDER}; border-radius: 3px; height: 6px; margin: 2px 10px; }}
        #     QSplitter::handle:hover {{ background: {PRIMARY}; }}
        # """)
        self.header_frame = self.create_header_section()
        self.content_splitter.addWidget(self.header_frame)
        self.items_frame = self.create_items_section()
        self.content_splitter.addWidget(self.items_frame)
        self.totals_frame = self.create_totals_section()
        self.content_splitter.addWidget(self.totals_frame)
        self.content_splitter.setSizes([250, 400, 150])
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, False)
        self.content_splitter.setCollapsible(2, False)
        self.main_layout.addWidget(self.content_splitter)
        self.add_item()

    def setup_action_buttons(self):
        """Setup enhanced action buttons with better organization"""
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; padding: 8px; }}
        """)
        button_container.setFixedHeight(70)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(15, 10, 15, 10)
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(8)
        self.help_button = self.create_action_button("❓ Help", "help", WARNING, self.show_help, "Get help with invoice creation")
        utility_layout.addWidget(self.help_button)
        self.preview_button = self.create_action_button("👁️ Preview", "preview", TEXT_SECONDARY, self.preview_invoice, "Preview how the invoice will look when printed")
        utility_layout.addWidget(self.preview_button)
        button_layout.addLayout(utility_layout)
        button_layout.addStretch()
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        self.cancel_button = self.create_action_button("❌ Cancel", "cancel", DANGER, self.reject, "Cancel and close without saving")
        action_layout.addWidget(self.cancel_button)
        save_text = "💾 Update Invoice" if self.invoice_data else "💾 Save Invoice"
        self.save_button = self.create_action_button(save_text, "save", SUCCESS, self.save_invoice, "Save the invoice with all current details")
        action_layout.addWidget(self.save_button)
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container)

    def create_action_button(self, text, button_type, color, callback, tooltip):
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setMinimumWidth(120)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        hover_color = self.get_hover_color(color)
        pressed_color = self.get_pressed_color(color)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {hover_color});
                color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: bold; padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hover_color}, stop:1 {pressed_color});
            }}
            QPushButton:pressed {{ background: {pressed_color}; }}
            QPushButton:disabled {{ background: #9CA3AF; color: #6B7280; }}
        """)
        button.clicked.connect(callback)
        return button

    def get_hover_color(self, base_color):
        color_map = {SUCCESS: "#059669", DANGER: "#DC2626", WARNING: "#F59E0B", PRIMARY: PRIMARY_HOVER, TEXT_SECONDARY: "#6B7280"}
        return color_map.get(base_color, "#6B7280")

    def get_pressed_color(self, base_color):
        color_map = {SUCCESS: "#047857", DANGER: "#B91C1C", WARNING: "#D97706", PRIMARY: "#1D4ED8", TEXT_SECONDARY: "#4B5563"}
        return color_map.get(base_color, "#4B5563")

    def apply_final_styling(self):
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.showMaximized()
        self.setup_keyboard_shortcuts()
        self.setup_validation()

    def setup_keyboard_shortcuts(self):
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_invoice)
        new_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_item_shortcut.activated.connect(self.add_item)
        # Use Ctrl+Enter to add item to avoid conflicting with Enter in fields
        new_item_shortcut2 = QShortcut(QKeySequence("Ctrl+Return"), self)
        new_item_shortcut2.activated.connect(self.add_item)
        help_shortcut = QShortcut(QKeySequence.HelpContents, self)
        help_shortcut.activated.connect(self.show_help)
        cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        cancel_shortcut.activated.connect(self.reject)

    def setup_validation(self):
        pass

    def show_help(self):
        help_text = """
        <h3>📋 Invoice Creation Help</h3>
        <p><b>1. Invoice Details:</b> Fill in invoice number, date, and due date</p>
        <p><b>2. Party Selection:</b> Choose the customer/client</p>
        <p><b>3. Add Items:</b> Click 'Add Item' to add products/services</p>
        <p><b>4. Calculations:</b> Totals are calculated automatically</p>
        <p><b>5. Save:</b> Click 'Save Invoice' to create the invoice</p>
        """
        QMessageBox.information(self, "Invoice Help", help_text)

    def preview_invoice(self):
        # Collect data from the form
        party_name = getattr(self, 'party_search').text().strip() if hasattr(self, 'party_search') else ''
        inv_date = self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else ''
        due_date = self.due_date.date().toString('yyyy-MM-dd') if hasattr(self, 'due_date') else ''
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

        # Build a simple HTML preview
        rows_html = "".join([
            f"<tr>"
            f"<td style='padding:6px;border:1px solid #ddd'>{i+1}</td>"
            f"<td style='padding:6px;border:1px solid #ddd'>{it['product_name']}</td>"
            f"<td style='padding:6px;border:1px solid #ddd'>{it.get('hsn_no','')}</td>"
            f"<td style='padding:6px;border:1px solid #ddd;text-align:right'>{it['quantity']:.2f}</td>"
            f"<td style='padding:6px;border:1px solid #ddd'>{it.get('unit','')}</td>"
            f"<td style='padding:6px;border:1px solid #ddd;text-align:right'>₹{it['rate']:,.2f}</td>"
            f"<td style='padding:6px;border:1px solid #ddd;text-align:right'>{it['discount_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #ddd;text-align:right'>{it['tax_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #ddd;text-align:right'>₹{it['amount']:,.2f}</td>"
            f"</tr>"
            for i, it in enumerate(items)
        ])
        
        # Add totals rows directly in the main table
        totals_rows = f"""
            <tr style='border-top: 2px solid #666;'>
                <td colspan='8' style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>Subtotal:</td>
                <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>₹{subtotal:,.2f}</td>
            </tr>
            <tr>
                <td colspan='8' style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>Total Discount:</td>
                <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>-₹{total_discount:,.2f}</td>
            </tr>
            <tr>
                <td colspan='8' style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>Total Tax:</td>
                <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#f9fafb;'>₹{total_tax:,.2f}</td>
            </tr>
            <tr>
                <td colspan='8' style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#e5e7eb;'>Grand Total:</td>
                <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;background:#e5e7eb;'>₹{grand_total:,.2f}</td>
            </tr>
        """
        html = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; margin: 20px; }}
                h2 {{ margin: 0 0 8px 0; }}
                .meta {{ margin-bottom: 12px; font-size: 14px; color: #374151; }}
                .invoice-container {{ position: relative; }}
                .main-table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin-bottom: 15px; }}
                .main-table th {{ background:#f3f4f6; border:1px solid #ddd; padding:8px; text-align:left; }}
                .main-table td {{ padding:8px; border:1px solid #ddd; }}
                .clearfix {{ clear: both; }}
            </style>
        </head>
        <body>
            <div class='invoice-container'>
                <h2>Invoice Preview</h2>
                <div class='meta'>
                    <div><b>Party:</b> {party_name or '—'}</div>
                    <div><b>Date:</b> {inv_date or '—'} &nbsp;&nbsp; <b>Due:</b> {due_date or '—'}</div>
                </div>
                
                <table class='main-table'>
                    <thead>
                        <tr>
                            <th style='width: 40px;'>No</th>
                            <th style='width: auto;'>Product</th>
                            <th style='width: 80px;'>HSN</th>
                            <th style='width: 80px; text-align:right;'>Qty</th>
                            <th style='width: 60px;'>Unit</th>
                            <th style='width: 100px; text-align:right;'>Rate</th>
                            <th style='width: 80px; text-align:right;'>Disc%</th>
                            <th style='width: 80px; text-align:right;'>Tax%</th>
                            <th style='width: 120px; text-align:right;'>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html if rows_html else "<tr><td colspan='9' style='text-align:center;color:#6b7280'>No items added</td></tr>"}
                        {totals_rows if items else ""}
                    </tbody>
                </table>
                
                <div class='clearfix'></div>
            </div>
        </body>
        </html>
        """

        # Show in a modal dialog with a QTextBrowser and simple actions
        dlg = QDialog(self)
        dlg.setWindowTitle("Invoice Preview")
        dlg.setModal(True)
        dlg.resize(900, 600)
        container = QVBoxLayout(dlg)
        view = QTextEdit()
        view.setReadOnly(True)
        view.setHtml(html)
        container.addWidget(view)

        actions = QHBoxLayout()
        actions.addStretch()
        
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: #1d4ed8;
            }}
        """)
        print_btn.clicked.connect(lambda: self.print_invoice(html))
        actions.addWidget(print_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {TEXT_SECONDARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: #4b5563;
            }}
        """)
        close_btn.clicked.connect(dlg.reject)
        actions.addWidget(close_btn)
        container.addLayout(actions)

        dlg.exec_()

    def print_invoice(self, html_content):
        """Print the invoice using the system's print dialog"""
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtGui import QTextDocument
            from PyQt5.QtCore import QMarginsF
            
            # Create a printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(QMarginsF(15, 15, 15, 15), QPrinter.Millimeter)
            
            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Invoice")
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Create a QTextDocument and set the HTML content
                document = QTextDocument()
                document.setHtml(html_content)
                
                # Print the document
                document.print_(printer)
                
                QMessageBox.information(self, "Success", "Invoice sent to printer successfully!")
                
        except ImportError:
            # Fallback if print support is not available
            QMessageBox.warning(self, "Print Unavailable", 
                              "Print functionality requires PyQt5 print support.\n"
                              "You can copy the invoice content and print manually.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", 
                               f"An error occurred while printing:\n{str(e)}")

    # The following helper sections mirror the original dialog
    def open_party_selector(self):
        try:
            selected = self._open_party_selector_dialog()
            if selected:
                self.party_search.setText(selected)
        except Exception as e:
            print(f"Party selector failed: {e}")

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
            from PyQt5.QtWidgets import QApplication
            input_w = max(300, self.party_search.width())
            dlg_h = min(dlg.sizeHint().height(), 420)
            margin = 8  # vertical gap to avoid overlap with the input
            dlg.resize(input_w, dlg_h)
            bl = self.party_search.mapToGlobal(self.party_search.rect().bottomLeft())
            x, y = bl.x(), bl.y() + margin
            screen = QApplication.desktop().availableGeometry(self.party_search)
            if y + dlg_h > screen.bottom():
                tl = self.party_search.mapToGlobal(self.party_search.rect().topLeft())
                y = tl.y() - dlg_h - margin
            if x + input_w > screen.right():
                x = max(screen.left(), screen.right() - input_w)
            dlg.move(int(x), int(y+65))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec_() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None

    def create_header_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; }}
        """)
        frame.setFixedHeight(200)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 0, 25, 0)
        layout.setSpacing(10)

        label_style = f"""
            QLabel {{ font-weight: 600; color: {TEXT_PRIMARY}; font-size: 14px; border: none; background: transparent; }}
        """
        input_style = f"""
                QLineEdit, QDateEdit, QComboBox, QTextEdit {{
                    border: 2px solid {BORDER}; border-radius: 8px; background: {WHITE};
                    font-size: 16px; color: {TEXT_PRIMARY}; }}
            """
        # --- New header layout: VBox with two rows ---
        header_vbox = QVBoxLayout()
        header_vbox.setSpacing(5)
        header_vbox.setContentsMargins(0, 0, 0, 0)

        # Row 1: Bill Type and Invoice Type horizontally
        row1_hbox = QHBoxLayout()
        row1_hbox.setAlignment(Qt.AlignLeft)
        row1_hbox.setSpacing(12)
        row1_hbox.setContentsMargins(0, 0, 0, 0)

        # Bill Type (CASH/CREDIT)
        billtype_widget = QWidget()
        billtype_widget.setStyleSheet(f"background: {WHITE};")
        billtype_layout = QVBoxLayout(billtype_widget)
        billtype_layout.setSpacing(5)
        billtype_lbl = QLabel("💵 Bill Type:")
        billtype_lbl.setStyleSheet(f"border: none; font-weight: bold;")
        billtype_layout.addWidget(billtype_lbl)
        billtype_widget.setFixedWidth(170)
        billtype_widget.setFixedHeight(90)
        self.billtype_combo = QComboBox()
        self.billtype_combo.addItems(["CASH", "CREDIT"])
        self.billtype_combo.setFixedHeight(40)
        self.billtype_combo.setFixedWidth(120)
        # Set initial style based on selection
        def update_billtype_style():
            base_style = """
                QComboBox {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    font-size: 16px;
                    padding: 6px 12px;
                }}
                QComboBox QAbstractItemView {{
                    color: {TEXT_PRIMARY};
                    background: {WHITE};
                    selection-background-color: #e5e7eb;
                    border: 1px solid {BORDER};
                }}
            """
            if self.billtype_combo.currentText() == "CASH":
                self.billtype_combo.setStyleSheet(f"""
                    QComboBox {{
                        background: {SUCCESS};
                        color: {WHITE};
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        font-size: 16px bold;
                        padding: 6px 12px;
                    }}
                    QComboBox QAbstractItemView {{
                        color: {TEXT_PRIMARY};
                        background: #5F9EA0;
                        selection-background-color: #e5e7eb;
                        border: 1px solid {BORDER};
                    }}
                """)
            else:
                self.billtype_combo.setStyleSheet(f"""
                    QComboBox {{
                        background: {DANGER};
                        color: {WHITE};
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        font-size: 16px bold;
                        padding: 6px 12px;
                    }}
                    QComboBox QAbstractItemView {{
                        color: {TEXT_PRIMARY};
                        background: #5F9EA0;
                        selection-background-color: #e5e7eb;
                        border: 1px solid {BORDER};
                    }}
                """)
        self.billtype_combo.currentIndexChanged.connect(update_billtype_style)
        update_billtype_style()
        billtype_layout.addWidget(self.billtype_combo)
        row1_hbox.addWidget(billtype_widget)

        # Invoice Type (GST/Non-GST)
        gst_widget = QWidget()
        gst_widget.setStyleSheet(f"background: {WHITE};")
        gst_layout = QVBoxLayout(gst_widget)
        gst_layout.setSpacing(5)
        gst_lbl = QLabel("📋 Invoice Type:")
        gst_lbl.setStyleSheet(f"border: none; font-weight: bold;")
        gst_layout.addWidget(gst_lbl)
        gst_widget.setFixedWidth(170)
        gst_widget.setFixedHeight(90)
        gst_combo = QComboBox()
        gst_combo.addItems(["GST", "Non-GST"])
        gst_layout.addWidget(gst_combo)
        gst_combo.setFixedHeight(40)
        gst_combo.setFixedWidth(120)
        gst_combo.setStyleSheet(f"""
                    QComboBox {{
                        background: {PRIMARY};
                        color: {WHITE};
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        font-size: 16px bold;
                        padding: 6px 12px;
                    }}
                    QComboBox QAbstractItemView {{
                        color: {TEXT_PRIMARY};
                        background:#5F9EA0;
                        selection-background-color: #e5e7eb;
                        border: 1px solid {BORDER};
                    }}
                """)
        # gst_combo.setStyleSheet(input_style+f"background: {PRIMARY}; border: 2px solid {BORDER}; border-radius: 8px; padding: 6px 12px; font-size: 16px;")
        # gst_combo.setStyleSheet(f"background: {PRIMARY}; border: 2px solid {BORDER}; border-radius: 8px; padding: 6px 12px; font-size: 16px;")
        row1_hbox.addWidget(gst_widget)

        header_vbox.addLayout(row1_hbox)

        # Row 2: Select Party (vertical)
        party_widget = QWidget()
        party_widget.setStyleSheet(f"background: {WHITE};")
        party_layout = QVBoxLayout(party_widget)
        select_party_lbl = QLabel("🏢 Select Party:")
        select_party_lbl.setFixedHeight(20)
        party_layout.setSpacing(5)
        select_party_lbl.setStyleSheet(f"border: none; font-weight: bold;")
        party_layout.addWidget(select_party_lbl)

        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search and select customer/client...")
        # autocomplete
        self.party_data_map = {}
        for party in (self.parties or []):
            name = party.get('name', '').strip()
            if name:
                self.party_data_map[name] = party
        self.party_search.setFixedWidth(600)
        self.party_search.setFixedHeight(55)
        try:
            self.party_search.textEdited.connect(self.on_party_search_edited)
        except Exception:
            pass
        # Enter opens selector
        try:
            self.party_search.returnPressed.connect(self.open_party_selector)
        except Exception:
            pass
        self.party_search.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 18px;
                color: {TEXT_PRIMARY};
                min-height: 20px;
            }}
            QLineEdit:hover {{
                border: 2px solid {PRIMARY};
            }}
        """)
        party_layout.addWidget(self.party_search)
        header_vbox.addWidget(party_widget)

        # --- Vertical stack: Invoice Number ---
        vertical_frame = QWidget()
        vertical_frame.setStyleSheet(f"border: 2px solid {PRIMARY}; border-radius: 8px; padding: 10px;")
        vertical_layout = QVBoxLayout(vertical_frame)
        vertical_layout.setSpacing(8)
        vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Invoice number
        inv_num_widget = QWidget()
        inv_num_widget.setStyleSheet(f"background: {WHITE};")
        inv_num_layout = QVBoxLayout(inv_num_widget)
        inv_num_lbl = QLabel("📄 Invoice Number:")
        inv_num_lbl.setFixedHeight(35)
        inv_num_lbl.setStyleSheet(label_style)
        inv_num_layout.addWidget(inv_num_lbl)
        inv_num_widget.setFixedWidth(170)
        # Fetch next invoice number from database if creating new
        if not self.invoice_data:
            try:
                if hasattr(db, 'get_next_invoice_number'):
                    next_inv_no = db.get_next_invoice_number()
                else:
                    # Fallback: get max invoice_no and increment
                    invoices = db.get_invoices() or []
                    max_no = 0
                    for inv in invoices:
                        inv_no = str(inv.get('invoice_no', ''))
                        if inv_no.startswith('INV-'):
                            try:
                                num = int(inv_no.replace('INV-', '').split()[0])
                                max_no = max(max_no, num)
                            except Exception:
                                pass
                    next_inv_no = f"INV-{max_no+1:03d}"
            except Exception:
                next_inv_no = "INV-001"
        else:
            # Editing existing invoice
            if isinstance(self.invoice_data, dict):
                # New format: dict with invoice data
                if 'invoice' in self.invoice_data:
                    next_inv_no = self.invoice_data['invoice'].get('invoice_no', "INV-001")
                else:
                    next_inv_no = self.invoice_data.get('invoice_no', "INV-001")
            else:
                # Old format or unexpected data
                next_inv_no = "INV-001"
        self.invoice_number = QLineEdit(next_inv_no)
        self.invoice_number.setReadOnly(True)
        self.invoice_number.setStyleSheet(f"background: {WHITE}; color: {DANGER}; font-size: 25x bold;")
        self.invoice_number.setAlignment(Qt.AlignCenter)
        self.invoice_number.setFixedWidth(150)
        self.invoice_number.setFixedHeight(45)
        inv_num_layout.addWidget(self.invoice_number)
        vertical_layout.addWidget(inv_num_widget)


        # Add Due Days input below Due Date
        # due_days_widget = QWidget()
        # due_days_widget.setFixedWidth(300)
        # due_days_layout = QVBoxLayout(due_days_widget)
        # due_days_layout.setAlignment(Qt.AlignRight)
        # due_days_layout.setContentsMargins(0, 0, 0, 0)
        # due_days_layout.setSpacing(8)
        due_days_lbl = QLabel("📆 Due Days:")
        due_days_lbl.setFixedHeight(35)
        due_days_lbl.setStyleSheet(label_style)
        # due_days_layout.addWidget(due_days_lbl)
        inv_num_layout.addWidget(due_days_lbl)
        self.due_days_spin = QSpinBox()
        self.due_days_spin.setRange(0, 365)
        self.due_days_spin.setValue(14)
        self.due_days_spin.setFixedHeight(35)
        self.due_days_spin.setFixedWidth(150)
        # self.due_days_spin.setStyleSheet(input_style)
        self.due_days_spin.setStyleSheet(f"border: 2px solid {BORDER}; border-radius: 8px; padding: 4px; font-size: 16px bold; color: {TEXT_PRIMARY};")
        self.due_days_spin.setAlignment(Qt.AlignCenter)
        self.due_days_spin.setToolTip("Number of days until due date")
        # due_days_layout.addWidget(self.due_days_spin)
        inv_num_layout.addWidget(self.due_days_spin)
        # vertical_layout.addWidget(due_days_widget)


        # --- Add header widgets to layout ---
        invoice_layout = QHBoxLayout()
        invoice_layout.setSpacing(15)
        invoice_layout.addLayout(header_vbox)
        invoice_layout.addWidget(vertical_frame)

        # Dates stacked vertically (Invoice Date above Due Date)
        dates_container = QWidget()
        dates_container.setStyleSheet(f"background: {WHITE};")
        dates_container.setFixedWidth(300)

        dates_vlayout = QVBoxLayout(dates_container)
        dates_vlayout.setSpacing(6)
        dates_vlayout.setContentsMargins(0, 0, 0, 0)
        dates_vlayout.setAlignment(Qt.AlignRight)

        # Invoice date
        inv_date_widget = QWidget()
        # inv_date_widget.setStyleSheet(f"border: 2px solid {DANGER};")
        inv_date_widget.setFixedWidth(300)
        inv_date_layout = QVBoxLayout(inv_date_widget)
        inv_date_layout.setAlignment(Qt.AlignRight)
        inv_date_layout.setContentsMargins(0, 0, 0, 0)
        inv_date_layout.setSpacing(8)
        inv_date_lbl = QLabel("📅 Invoice Date:")
        inv_date_lbl.setFixedHeight(20)
        inv_date_lbl.setStyleSheet(label_style)
        inv_date_layout.addWidget(inv_date_lbl)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setStyleSheet(input_style + f"""
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 40px;
                    height: 30px;
                    border-left: 2px solid {BORDER};
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }}
                QDateEdit::drop-down:hover {{ background: {PRIMARY_HOVER}; }}
                QDateEdit::down-arrow {{
                    image: url(assets/icons/calendar.svg);
                    width: 30px;
                    height: 30px;
                    margin: 8px;
                }}
                QDateEdit::down-arrow:disabled {{
                    image: url(assets/icons/calendar.svg);
                }}
            """)
        self.invoice_date.setFixedHeight(35)
        self.invoice_date.setFixedWidth(150)
        inv_date_layout.addWidget(self.invoice_date)
        dates_vlayout.addWidget(inv_date_widget)

        # Due date
        due_date_widget = QWidget()
        # due_date_widget.setStyleSheet(f"border: 2px solid {DANGER};")
        due_date_widget.setFixedWidth(300)
        due_date_layout = QVBoxLayout(due_date_widget)
        due_date_layout.setAlignment(Qt.AlignRight)
        due_date_layout.setContentsMargins(0, 0, 0, 0)
        due_date_layout.setSpacing(8)
        due_date_lbl = QLabel("📆 Due Date:")
        due_date_lbl.setFixedHeight(35)
        due_date_lbl.setStyleSheet(label_style)
        due_date_layout.addWidget(due_date_lbl)
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(14))
        self.due_date.setCalendarPopup(True)
        self.due_date.setStyleSheet(input_style + f"""
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 40px;
                    height: 50px;
                    border-left: 2px solid {BORDER};
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }}
                QDateEdit::drop-down:hover {{ background: {PRIMARY_HOVER}; }}
                QDateEdit::down-arrow {{
                    image: url(assets/icons/calendar.svg);
                    width: 30px;
                    height: 30px;
                    margin: 8px;
                }}
                QDateEdit::down-arrow:disabled {{
                    image: url(assets/icons/calendar.svg);
                }}
            """)
        self.due_date.setFixedHeight(35)
        self.due_date.setFixedWidth(150)
        due_date_layout.addWidget(self.due_date)
        dates_vlayout.addWidget(due_date_widget)

        # Add header widgets to layout
        invoice_layout.addWidget(dates_container, 1)
        # invoice_layout.addWidget(gst_widget)
        invoice_layout.addWidget(inv_num_widget, 1)

        layout.addLayout(invoice_layout)
        return frame

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

    def create_items_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; margin: 5px; }}
        """)
        frame.setFixedHeight(480)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 20)

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
            label.setStyleSheet(f"""
                QLabel {{ font-weight: bold; color: {TEXT_PRIMARY}; padding: 0; margin: 0; background: {BACKGROUND}; border: 1px solid {PRIMARY}; border-radius: 6px; font-size: 13px; }}
            """)
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)
        layout.addLayout(headers_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(335)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: 1px solid {BORDER}; border-radius: 10px; background: {BACKGROUND}; }}
        """)
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(1)
        self.items_layout.setContentsMargins(1, 1, 1, 1)
        self.items_layout.addStretch()
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area)
        return frame

    def create_totals_section(self):
        frame = QFrame()
        frame.setStyleSheet(f""" QFrame {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; }} """)
        frame.setFixedHeight(230)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Notes area: lazy add via text link
        notes_container = QVBoxLayout()
        notes_header = QHBoxLayout()
        add_note_link = QLabel("<a href='add'>+Add Note</a>")
        add_note_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_note_link.setOpenExternalLinks(False)
        add_note_link.setStyleSheet("color: #2563EB; font-size: 13px; border: none;")
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
        notes_container.addStretch()

        layout.addLayout(notes_container, 2)

        # Totals on the right
        totals_layout = QFormLayout()
        totals_layout.setSpacing(15)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        self.discount_label = QLabel("₹0.00")
        self.discount_label.setStyleSheet("font-size: 16px; color: red; border: none; background: transparent;")
        totals_layout.addRow("Total Discount:", self.discount_label)
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        totals_layout.addRow("Total Tax:", self.tax_label)
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {PRIMARY}; background: {BACKGROUND}; padding: 8px; border-radius: 4px;")
        self.grand_total_label.setFixedWidth(130)
        self.grand_total_label.setFixedWidth(130)
        totals_layout.addRow("Grand Total:", self.grand_total_label)
        # Paid Amount field
        
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.paid_amount_spin = QDoubleSpinBox()
        self.paid_amount_spin.setRange(0, 999999999)
        self.paid_amount_spin.setDecimals(2)
        self.paid_amount_spin.setPrefix("₹")
        self.paid_amount_spin.setStyleSheet("font-size: 16px; border: 1px solid #ccc; border-radius: 6px; padding: 4px; background: #fff;")
        self.paid_amount_spin.setFixedWidth(130)
        self.paid_amount_spin.setFixedHeight(30)
        self.paid_amount_spin.setValue(0)
        # totals_layout.addRow("Paid Amount:", self.paid_amount_spin)
        # Balance label
        self.balance_label = QLabel("₹0.00")
        self.balance_label.setFixedWidth(130)
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #EF4444; background: #FEF2F2; padding: 6px; border-radius: 4px;")
        totals_layout.addRow("Balance Due:", self.balance_label)
        # Update balance when paid amount changes
        self.paid_amount_spin.valueChanged.connect(self.update_balance_due)
        layout.addStretch(1)
        layout.addLayout(totals_layout, 1)
        return frame

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
    def add_item(self):
        item_widget = InvoiceItemWidget(products=self.products)
        # Wire row-level ➕ to add another item row
        item_widget.add_requested.connect(self.add_item)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
        item_widget.item_changed.connect(self.update_totals)
        item_widget.setStyleSheet(f""" QWidget:hover {{ background: rgba(59, 130, 246, 0.05); border-radius: 8px; }} """)
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        # Assign row numbers after insertion
        self.number_items()
        self.update_totals()

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
            grand_total = subtotal - total_discount + total_tax
            self.subtotal_label.setText(f"₹{subtotal:,.2f}")
            self.discount_label.setText(f"-₹{total_discount:,.2f}")
            self.tax_label.setText(f"₹{total_tax:,.2f}")
            self.grand_total_label.setText(f"₹{grand_total:,.2f}")
            self.update_balance_due()
        except Exception as e:
            print(f"Error updating totals: {e}")

    def save_invoice(self):
        party_text = getattr(self, 'party_search').text().strip()
        party_data = getattr(self, 'party_data_map').get(party_text)
        if not party_data or not party_text:
            QMessageBox.warning(self, "Error", "Please select a valid party from the search!")
            return
        items = []
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                if item_data:
                    items.append(item_data)
        if not items:
            QMessageBox.warning(self, "Error", "Please add at least one item!")
            return
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        total_discount = sum(item['discount_amount'] for item in items)
        total_tax = sum(item['tax_amount'] for item in items)
        grand_total = subtotal - total_discount + total_tax
        notes_text = ''
        if hasattr(self, 'notes') and self.notes is not None:
            notes_text = self.notes.toPlainText()
        invoice_data = {
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd'),
            'due_date': getattr(self, 'due_date', self.invoice_date).date().toString('yyyy-MM-dd'),
            'notes': notes_text,
            'subtotal': subtotal,
            'total_discount': total_discount,
            'grand_total': grand_total,
            'paid_amount': self.paid_amount_spin.value(),
            'balance_due': max(0, grand_total - self.paid_amount_spin.value()),
            'status': 'Draft',
            'items': items
        }
        try:
            invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
            if not invoice_no:
                QMessageBox.warning(self, "Error", "Invoice number cannot be empty!")
                return
            # Check for duplicate invoice number only when creating new
            if not self.invoice_data and hasattr(db, 'invoice_no_exists') and db.invoice_no_exists(invoice_no):
                QMessageBox.warning(self, "Error", f"Invoice number '{invoice_no}' already exists. Please use a unique invoice number.")
                return
            invoice_data['invoice_no'] = invoice_no
            if self.invoice_data:
                invoice_data['id'] = self.invoice_data['id']
                db.update_invoice(invoice_data)
                # Update invoice items
                db.delete_invoice_items(self.invoice_data['id'])
                for item in items:
                    db.add_invoice_item(
                        self.invoice_data['id'],
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
                QMessageBox.information(self, "Success", "Invoice updated successfully!")
            else:
                # Create new invoice
                invoice_id = db.add_invoice(
                    invoice_no,
                    invoice_data.get('invoice_date', ''),
                    invoice_data.get('party_id', ''),
                    invoice_data.get('status', 'GST'),
                    invoice_data.get('subtotal', 0),
                    0, 0, 0, 0,  # cgst, sgst, igst, round_off (defaults)
                    invoice_data.get('grand_total', 0)
                )
                # Add invoice items
                for item in items:
                    db.add_invoice_item(
                        invoice_id,
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
                QMessageBox.information(self, "Success", "Invoice created successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")


