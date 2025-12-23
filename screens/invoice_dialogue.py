"""
Standalone InvoiceDialog for creating/editing invoices.
Extracted from screens/invoices.py to avoid a huge single file.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QAction, QShortcut, 
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QKeySequence
from PyQt5.QtWidgets import QCompleter
from .party_selector import PartySelector

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
        
        # Product selection with enhanced styling
        self.product_combo = QComboBox()
        self.product_combo.addItem("🛍️ Select Product", None)
        for product in self.products:
            icon = "📦" if product.get('type') == 'Goods' else "🔧"
            display_text = f"{icon} {product['name']} - ₹{product.get('selling_price', 0):,.0f}"
            self.product_combo.addItem(display_text, product)
        # Align with header width (Product ~300px when preceded by No=60px and HSN=100px)
        self.product_combo.setFixedWidth(500)
        self.product_combo.setFixedHeight(40)
        self.product_combo.setStyleSheet(widget_style)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        layout.addWidget(self.product_combo)
        layout.setSpacing(20)

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

        # Enhanced remove button
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

            }}
            QPushButton:pressed {{
                background: #B91C1C;
            }}
        """)
        self.add_btn.setToolTip("Add this item")
        # Emit signal so parent can add a new row
        self.add_btn.clicked.connect(self.add_requested.emit)
        layout.addWidget(self.add_btn)
        layout.setAlignment(self.product_combo, Qt.AlignLeft)
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


    def on_product_changed(self):
        """Handle product selection change with validation"""
        product_data = self.product_combo.currentData()
        if product_data:
            self.rate_spin.setValue(product_data.get('selling_price', 0))
            self.tax_spin.setValue(product_data.get('tax_rate', 18))
            self.unit_label.setText(product_data.get('unit', 'Piece'))
            
            # Auto-apply product discount if available
            if 'discount' in product_data:
                self.discount_spin.setValue(product_data.get('discount', 0))
            
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
        product_data = self.product_combo.currentData()
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
            'product_id': product_data['id'],
            'product_name': product_data['name'],
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
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.products = []
        self.parties = []

        # Initialize window properties
        self.init_window()

        # Load required data
        self.load_data()

        # Setup the complete UI
        self.setup_ui()

        # Force maximize after everything is set up
        QTimer.singleShot(100, self.ensure_maximized)

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

    def setup_content_sections(self):
        """Setup the main content sections with enhanced layout"""
        self.content_splitter = QSplitter(Qt.Vertical)
        self.content_splitter.setStyleSheet(f"""
            QSplitter {{ border: none; background: transparent; }}
            QSplitter::handle {{ background: {BORDER}; border-radius: 3px; height: 6px; margin: 2px 10px; }}
            QSplitter::handle:hover {{ background: {PRIMARY}; }}
        """)
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
        html = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; }}
                h2 {{ margin: 0 0 8px 0; }}
                .meta {{ margin-bottom: 12px; font-size: 14px; color: #374151; }}
                table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
                th {{ background:#f3f4f6; border:1px solid #ddd; padding:8px; text-align:left; }}
                td {{ padding:8px; border:1px solid #ddd; }}
                .totals-box {{ margin: 12px 0 0 0; width: 180px; float: right; border: 1px solid #ddd; border-radius: 6px; }}
                .totals-box table {{ width: 100%; border-collapse: collapse; }}
                .totals-box td {{ border: none; padding: 6px 8px; font-size: 14px; }}
                .totals-box td.label {{ text-align: left; width: 60%; }}
                .totals-box td.value {{ text-align: right; width: 40%; }}
            </style>
        </head>
        <body>
            <h2>Invoice Preview</h2>
            <div class='meta'>
                <div><b>Party:</b> {party_name or '—'}</div>
                <div><b>Date:</b> {inv_date or '—'} &nbsp;&nbsp; <b>Due:</b> {due_date or '—'}</div>
            </div>
            <table>
                <colgroup>
                    <col span="8" />
                    <col style="width: 180px" />
                </colgroup>
                <thead>
                    <tr>
                        <th>No</th><th>Product</th><th>HSN</th><th style='text-align:right'>Qty</th>
                        <th>Unit</th><th style='text-align:right'>Rate</th><th style='text-align:right'>Disc%</th>
                        <th style='text-align:right'>Tax%</th><th style='text-align:right'>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else "<tr><td colspan='9' style='text-align:center;color:#6b7280'>No items added</td></tr>"}
                </tbody>
            </table>
                        <div class='totals-box'>
                            <table>
                                <tr><td class='label'><b>Subtotal</b></td><td class='value'>₹{subtotal:,.2f}</td></tr>
                                <tr><td class='label'><b>Total Discount</b></td><td class='value'>-₹{total_discount:,.2f}</td></tr>
                                <tr><td class='label'><b>Total Tax</b></td><td class='value'>₹{total_tax:,.2f}</td></tr>
                                <tr><td class='label'><b>Grand Total</b></td><td class='value'><b>₹{grand_total:,.2f}</b></td></tr>
                            </table>
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
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.reject)
        actions.addWidget(close_btn)
        container.addLayout(actions)

        dlg.exec_()

    # The following helper sections mirror the original dialog
    def open_party_selector(self):
        try:
            dlg = PartySelector(self.parties, self)
            if dlg.exec_() == QDialog.Accepted and dlg.selected_name:
                self.party_search.setText(dlg.selected_name)
        except Exception as e:
            print(f"Party selector failed: {e}")

    def create_header_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; }}
        """)
        frame.setFixedHeight(120)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 0, 25, 0)
        layout.setSpacing(10)

        label_style = f"""
            QLabel {{ font-weight: 600; color: {TEXT_PRIMARY}; font-size: 14px; border: none; background: transparent; }}
        """

        invoice_layout = QHBoxLayout()
        invoice_layout.setSpacing(15)

        # Party selection
        party_widget = QWidget()
        party_layout = QVBoxLayout(party_widget)
        party_layout.setSpacing(1)
        select_party_lbl = QLabel("🏢 Select Party:")
        select_party_lbl.setFixedHeight(30)
        select_party_lbl.setFixedWidth(150)
        select_party_lbl.setStyleSheet(label_style)
        party_layout.addWidget(select_party_lbl)

        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search and select customer/client...")
        # autocomplete
        party_names = []
        self.party_data_map = {}
        parties_to_use = self.parties or []
        if not parties_to_use:
            parties_to_use = [
                {'id': 1, 'name': 'ABC Corporation'},
            ]
        for party in parties_to_use:
            name = party.get('name', '').strip()
            if not name:
                continue
            party_names.append(name)
            self.party_data_map[name] = party
            completer = QCompleter(party_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        # completer.setMaxVisibleItems(4)
        popup = completer.popup()
        try:
            popup.setMinimumWidth(self.party_search.width())
            popup.setFixedHeight(140)
        except Exception:
            pass
        popup.setStyleSheet(f"""
            QAbstractItemView {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                outline: none;
                selection-background-color: {PRIMARY};
                selection-color: white;
                padding: 8px;
                font-size: 18px;
            }}
        """)
        self.party_search.setCompleter(completer)
        input_style = f"""
            QLineEdit, QDateEdit, QComboBox, QTextEdit {{
                border: 2px solid {BORDER}; border-radius: 8px; padding: 10px 12px; background: {WHITE};
                font-size: 14px; color: {TEXT_PRIMARY}; min-height: 20px; }}
        """
        self.party_search.setStyleSheet(input_style)
        party_input_row = QHBoxLayout()
        party_input_row.setSpacing(8)
        party_input_row.addWidget(self.party_search)
        select_btn = QPushButton("Select")
        select_btn.setFixedHeight(35)
        select_btn.clicked.connect(self.open_party_selector)
        party_input_row.addWidget(select_btn)
        party_layout.addLayout(party_input_row)
        self.party_search.setFixedWidth(600)
        self.party_search.setFixedHeight(35)
        # Enter opens selector
        try:
            self.party_search.returnPressed.connect(self.open_party_selector)
        except Exception:
            pass
        invoice_layout.addWidget(party_widget)
        # layout.addSpacing(200)

        # GST/Non-GST
        gst_widget = QWidget()
        gst_layout = QVBoxLayout(gst_widget)
        gst_layout.setSpacing(1)
        gst_lbl = QLabel("📋 Invoice Type:")
        gst_lbl.setFixedHeight(35)
        gst_lbl.setStyleSheet(label_style)
        gst_layout.addWidget(gst_lbl)
        gst_widget.setFixedWidth(150)
        gst_combo = QComboBox()
        gst_combo.addItems(["GST", "Non-GST"])
        gst_combo.setStyleSheet(input_style)
        gst_layout.addWidget(gst_combo)
        gst_combo.setFixedHeight(35)
        invoice_layout.addWidget(gst_widget)

        # Invoice number and date
        inv_num_widget = QWidget()
        inv_num_layout = QVBoxLayout(inv_num_widget)
        inv_num_lbl = QLabel("📄 Invoice Number:")
        inv_num_lbl.setFixedHeight(35)
        inv_num_lbl.setStyleSheet(label_style)
        inv_num_layout.addWidget(inv_num_lbl)
        inv_num_widget.setFixedWidth(170)
        invoice_number = QLineEdit("Auto-generated")
        invoice_number.setReadOnly(True)
        invoice_number.setStyleSheet(input_style + f"background: {BACKGROUND};")
        invoice_number.setFixedWidth(150)
        inv_num_layout.addWidget(invoice_number)

        # Invoice date
        inv_date_widget = QWidget()
        inv_date_layout = QVBoxLayout(inv_date_widget)
        inv_date_lbl = QLabel("📅 Invoice Date:")
        inv_date_lbl.setFixedHeight(35)
        inv_date_lbl.setStyleSheet(label_style)
        inv_date_layout.addWidget(inv_date_lbl)
        inv_date_widget.setFixedWidth(160)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setStyleSheet(input_style + f"""
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 35px;
                    height: 45px;
                    border-left: 2px solid {BORDER};
                    background: {PRIMARY};
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }}
                QDateEdit::drop-down:hover {{ background: {PRIMARY_HOVER}; }}
                QDateEdit::down-arrow {{
                    width: 18px;
                    height: 18px;
                    margin: 6px;
                }}
            """)
        inv_date_layout.addWidget(self.invoice_date)

        # Due date
        due_date_widget = QWidget()
        due_date_layout = QVBoxLayout(due_date_widget)
        due_date_lbl = QLabel("⏰ Due Date:")
        due_date_lbl.setFixedHeight(35)
        due_date_lbl.setStyleSheet(label_style)
        due_date_layout.addWidget(due_date_lbl)
        due_date_widget.setFixedWidth(160)
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(14))
        self.due_date.setCalendarPopup(True)
        self.due_date.setStyleSheet(input_style + f"""
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 35px;
                    height: 45px;
                    border-left: 2px solid {BORDER};
                    background: {PRIMARY};
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }}
                QDateEdit::drop-down:hover {{ background: {PRIMARY_HOVER}; }}
                QDateEdit::down-arrow {{
                    width: 18px;
                    height: 18px;
                    margin: 6px;
                }}
            """)
        due_date_layout.addWidget(self.due_date)

        # Add header widgets to layout
        invoice_layout.addWidget(inv_num_widget, 1)
        invoice_layout.addWidget(inv_date_widget, 1)
        invoice_layout.addWidget(due_date_widget, 1)

        layout.addLayout(invoice_layout)
        return frame

    def create_items_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; margin: 5px; }}
        """)
        frame.setFixedHeight(500)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 20)
        # layout.setSpacing(20)
        # # Toolbar
        # toolbar = QHBoxLayout()
        # add_btn = QPushButton("➕ Add Item")
        # add_btn.setCursor(Qt.PointingHandCursor)
        # add_btn.setFixedHeight(34)
        # add_btn.setStyleSheet(f"""
        #     QPushButton {{
        #         background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 6px 12px; font-weight: 600;
        #     }}
        #     QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        # """)
        # add_btn.clicked.connect(self.add_item)
        # toolbar.addWidget(add_btn)
        # toolbar.addStretch()
        # layout.addLayout(toolbar)

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
                QLabel {{ font-weight: bold; color: {TEXT_PRIMARY}; padding: 0; margin: 0; background: {BACKGROUND}; border: 1px solid {BORDER}; border-radius: 0px; font-size: 13px; }}
            """)
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)
        layout.addLayout(headers_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(435)
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
        frame.setFixedHeight(200)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Notes area
        notes_container = QVBoxLayout()
        notes_label = QLabel("📝 Notes")
        notes_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY};")
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Add any additional information or terms...")
        self.notes.setStyleSheet(f"border: 2px solid {BORDER}; border-radius: 8px; padding: 10px; background: {WHITE}; font-size: 13px;")
        self.notes.setFixedHeight(80)
        notes_container.addWidget(notes_label)
        notes_container.addWidget(self.notes)
        notes_container.addStretch()

        layout.addLayout(notes_container, 2)

        # Totals on the right
        totals_layout = QFormLayout()
        totals_layout.setSpacing(8)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-size: 14px;")
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        self.discount_label = QLabel("₹0.00")
        self.discount_label.setStyleSheet("font-size: 14px; color: red;")
        totals_layout.addRow("Total Discount:", self.discount_label)
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet("font-size: 14px;")
        totals_layout.addRow("Total Tax:", self.tax_label)
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY}; background: {BACKGROUND}; padding: 8px; border-radius: 4px;")
        totals_layout.addRow("Grand Total:", self.grand_total_label)
        layout.addStretch(1)
        layout.addLayout(totals_layout, 1)
        return frame

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
        notes_text = getattr(self, 'notes').toPlainText() if hasattr(self, 'notes') else ''
        invoice_data = {
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd'),
            'due_date': getattr(self, 'due_date', self.invoice_date).date().toString('yyyy-MM-dd'),
            'notes': notes_text,
            'subtotal': subtotal,
            'total_discount': total_discount,
            'grand_total': grand_total,
            'status': 'Draft',
            'items': items
        }
        try:
            if self.invoice_data:
                invoice_data['id'] = self.invoice_data['id']
                db.update_invoice(invoice_data)
                QMessageBox.information(self, "Success", "Invoice updated successfully!")
            else:
                db.add_invoice(invoice_data)
                QMessageBox.information(self, "Success", "Invoice created successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")


