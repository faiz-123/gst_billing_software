"""
Invoices screen - Create and manage invoices with enhanced UI and functionality
"""

import sys
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from database import db

class InvoiceItemWidget(QWidget):
    """Enhanced widget for invoice line items with better styling and validation"""
    
    item_changed = pyqtSignal()  # Signal for when item data changes
    
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
        
        # Product selection with enhanced styling
        self.product_combo = QComboBox()
        self.product_combo.addItem("🛍️ Select Product", None)
        for product in self.products:
            icon = "📦" if product.get('type') == 'Goods' else "🔧"
            display_text = f"{icon} {product['name']} - ₹{product.get('selling_price', 0):,.0f}"
            self.product_combo.addItem(display_text, product)
        self.product_combo.setFixedWidth(430)
        self.product_combo.setStyleSheet(widget_style)
        layout.addWidget(self.product_combo)
        layout.setSpacing(35)

        
        # Quantity with validation
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setFixedWidth(110)
        self.quantity_spin.setStyleSheet(widget_style)
        self.quantity_spin.setToolTip("Enter quantity")
        self.quantity_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.quantity_spin)
        layout.addWidget(self.quantity_spin)
        
        # Unit display with better styling
        self.unit_label = QLabel("Piece")
        self.unit_label.setFixedWidth(65)
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
        # self.add_btn.clicked.connect(self.add_item)
        layout.addWidget(self.add_btn)


        layout.setAlignment(self.product_combo, Qt.AlignLeft)
        layout.setAlignment(self.quantity_spin, Qt.AlignLeft)
        layout.setAlignment(self.unit_label, Qt.AlignLeft)
        layout.setAlignment(self.rate_spin, Qt.AlignLeft)
        layout.setAlignment(self.discount_spin, Qt.AlignLeft)
        layout.setAlignment(self.tax_spin, Qt.AlignLeft)
        layout.setAlignment(self.remove_btn, Qt.AlignCenter)
        layout.setAlignment(self.amount_label, Qt.AlignCenter)


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
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.ensure_maximized)
    
    def ensure_maximized(self):
        """Ensure the window is properly maximized"""
        from PyQt5.QtWidgets import QApplication
        
        # Get screen geometry and set window to full screen
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        
        # Set window state to maximized
        self.setWindowState(Qt.WindowMaximized)
        self.showMaximized()
        
    def init_window(self):
        """Initialize window properties and styling"""
        # Set window title with icons
        title = "📄 Create Invoice" if not self.invoice_data else "📝 Edit Invoice"
        self.setWindowTitle(title)
        
        # Window configuration
        self.setModal(True)
        
        # Set window flags for better control
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set to full screen size
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        
        # Also set minimum size for usability
        self.setMinimumSize(1200, 900)
        
        # Enhanced window styling
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
            # Enhanced sample data for demonstration
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
        # Create main layout with enhanced spacing and margins
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Setup individual UI components
        # self.setup_title_section()
        self.setup_content_sections()
        self.setup_action_buttons()
        
        # Apply final styling and animations
        self.apply_final_styling()
    
    def setup_title_section(self):
        """Setup the enhanced title section with status indicators"""
        title_container = QFrame()
        title_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
                border-radius: 15px;
                margin: 5px;
                padding: 10px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(20, 15, 20, 15)
        title_layout.setSpacing(20)
        
        # Main title with enhanced styling
        title_text = "📄 Create New Invoice" if not self.invoice_data else "📝 Edit Invoice"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Arial", 22, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                border: none;
                background: transparent;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Status indicator for editing mode
        if self.invoice_data:
            status = self.invoice_data.get('status', 'Draft')
            status_color = SUCCESS if status == 'Paid' else WARNING if status == 'Sent' else TEXT_SECONDARY
            
            self.status_indicator = QLabel(f"📊 {status}")
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    background: {status_color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }}
            """)
            title_layout.addWidget(self.status_indicator)
        
        # Invoice number display
        invoice_num = self.invoice_data.get('invoice_no', 'Auto-generated') if self.invoice_data else 'Auto-generated'
        self.invoice_num_label = QLabel(f"#{invoice_num}")
        self.invoice_num_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)
        title_layout.addWidget(self.invoice_num_label)
        
        self.main_layout.addWidget(title_container)
    
    def setup_content_sections(self):
        """Setup the main content sections with enhanced layout"""
        # Create splitter for responsive layout management
        self.content_splitter = QSplitter(Qt.Vertical)
        self.content_splitter.setStyleSheet(f"""
            QSplitter {{
                border: none;
                background: transparent;
            }}
            QSplitter::handle {{
                background: {BORDER};
                border-radius: 3px;
                height: 6px;
                margin: 2px 10px;
            }}
            QSplitter::handle:hover {{
                background: {PRIMARY};
            }}
        """)
        
        # Header section (Invoice details)
        self.header_frame = self.create_header_section()
        self.content_splitter.addWidget(self.header_frame)
        
        # Items section (Products/Services)
        self.items_frame = self.create_items_section()
        self.content_splitter.addWidget(self.items_frame)
        
        # Totals section (Calculations)
        self.totals_frame = self.create_totals_section()
        self.content_splitter.addWidget(self.totals_frame)
        
        # Set optimal proportions for each section
        self.content_splitter.setSizes([250, 400, 150])
        self.content_splitter.setCollapsible(0, False)  # Header always visible
        self.content_splitter.setCollapsible(1, False)  # Items always visible
        self.content_splitter.setCollapsible(2, False)  # Totals always visible
        
        self.main_layout.addWidget(self.content_splitter)
        
        # Add first item after all sections are created
        self.add_item()
    
    def setup_action_buttons(self):
        """Setup enhanced action buttons with better organization"""
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(15, 10, 15, 10)
        
        # Left side - utility buttons
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(8)
        
        # Help button
        self.help_button = self.create_action_button(
            "❓ Help", "help", WARNING, self.show_help,
            "Get help with invoice creation"
        )
        utility_layout.addWidget(self.help_button)
        
        # Preview button
        self.preview_button = self.create_action_button(
            "👁️ Preview", "preview", TEXT_SECONDARY, self.preview_invoice,
            "Preview how the invoice will look when printed"
        )
        utility_layout.addWidget(self.preview_button)
        
        button_layout.addLayout(utility_layout)
        button_layout.addStretch()
        
        # Right side - primary actions
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        # Cancel button
        self.cancel_button = self.create_action_button(
            "❌ Cancel", "cancel", DANGER, self.reject,
            "Cancel and close without saving"
        )
        action_layout.addWidget(self.cancel_button)
        
        # Save button
        save_text = "💾 Update Invoice" if self.invoice_data else "💾 Save Invoice"
        self.save_button = self.create_action_button(
            save_text, "save", SUCCESS, self.save_invoice,
            "Save the invoice with all current details"
        )
        action_layout.addWidget(self.save_button)
        
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container)
    
    def create_action_button(self, text, button_type, color, callback, tooltip):
        """Create a standardized action button with enhanced styling"""
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setMinimumWidth(120)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        
        # Enhanced button styling based on type
        hover_color = self.get_hover_color(color)
        pressed_color = self.get_pressed_color(color)
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {color}, stop:1 {hover_color});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {hover_color}, stop:1 {pressed_color});
            }}
            QPushButton:pressed {{
                background: {pressed_color};
            }}
            QPushButton:disabled {{
                background: #9CA3AF;
                color: #6B7280;
            }}
        """)
        
        button.clicked.connect(callback)
        return button
    
    def get_hover_color(self, base_color):
        """Get appropriate hover color for button styling"""
        color_map = {
            SUCCESS: "#059669",
            DANGER: "#DC2626", 
            WARNING: "#F59E0B",
            PRIMARY: PRIMARY_HOVER,
            TEXT_SECONDARY: "#6B7280"
        }
        return color_map.get(base_color, "#6B7280")
    
    def get_pressed_color(self, base_color):
        """Get appropriate pressed color for button styling"""
        color_map = {
            SUCCESS: "#047857",
            DANGER: "#B91C1C",
            WARNING: "#D97706", 
            PRIMARY: "#1D4ED8",
            TEXT_SECONDARY: "#4B5563"
        }
        return color_map.get(base_color, "#4B5563")
    
    def apply_final_styling(self):
        """Apply final styling and setup window behavior"""
        # Add subtle shadow effect to the dialog
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Ensure window is maximized after setup
        self.showMaximized()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Setup validation and auto-save
        self.setup_validation()
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better user experience"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+S to save
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_invoice)
        
        # Ctrl+N to add new item
        new_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_item_shortcut.activated.connect(self.add_item)
        
        # Ctrl+N to add new item
        new_item_shortcut2 = QShortcut(QKeySequence("Return"), self)
        new_item_shortcut2.activated.connect(self.add_item)
        
        # F1 for help
        help_shortcut = QShortcut(QKeySequence.HelpContents, self)
        help_shortcut.activated.connect(self.show_help)
        
        # Escape to cancel
        cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        cancel_shortcut.activated.connect(self.reject)
    
    def setup_validation(self):
        """Setup form validation and auto-save functionality"""
        # This will be implemented to validate form fields in real-time
        pass
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>📋 Invoice Creation Help</h3>
        <p><b>1. Invoice Details:</b> Fill in invoice number, date, and due date</p>
        <p><b>2. Party Selection:</b> Choose the customer/client</p>
        <p><b>3. Add Items:</b> Click 'Add Item' to add products/services</p>
        <p><b>4. Calculations:</b> Totals are calculated automatically</p>
        <p><b>5. Save:</b> Click 'Save Invoice' to create the invoice</p>
        
        <h4>💡 Tips:</h4>
        <ul>
        <li>Use Tab key to navigate between fields quickly</li>
        <li>Discount and tax are calculated per line item</li>
        <li>Click the red ✖ button to remove items</li>
        <li>Preview before saving to review the invoice</li>
        </ul>
        """
        QMessageBox.information(self, "Invoice Help", help_text)
    
    def preview_invoice(self):
        """Show invoice preview"""
        QMessageBox.information(self, "Preview", "📋 Invoice preview functionality will be implemented soon!\n\nThis will show how the printed invoice will look.")
    
    def create_header_section(self):
        """Create enhanced invoice header section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {DANGER};
                border-radius: 15px;
            }}
        """)
        frame.setFixedHeight(130)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 0, 25, 0)
        layout.setSpacing(1)
        
        # Enhanced title with icon
        header_title = QLabel("📋 Invoice Details")
        header_title.setFont(QFont("Arial", 18, QFont.Bold))
        header_title.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY}; 
                border: none;
                padding: 10px;
                background: rgba(59, 130, 246, 0.1);
            }}
        """)
        # layout.addWidget(header_title)
        
        # Enhanced form layout with grid
        # form_widget = QWidget()
        # form_layout = QFormLayout(form_widget)
        # form_layout.setSpacing(1)
        # form_layout.setHorizontalSpacing(20)
        
        # Enhanced input styling
        input_style = f"""
            QLineEdit, QDateEdit, QComboBox, QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 10px 12px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
                min-height: 20px;
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: {BORDER};
                background: #F8FAFC;
            }}
            QLineEdit:hover, QDateEdit:hover, QComboBox:hover, QTextEdit:hover {{
                border-color: {BORDER};
            }}
        """
        
        label_style = f"""
            QLabel {{
                font-weight: 600;
                color: {TEXT_PRIMARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """
        
        # Invoice number and date row
        # invoice_row = QWidget()
        invoice_layout = QHBoxLayout()
        # invoice_row.setFixedHeight(150)
        invoice_layout.setSpacing(15)

        # invoice_row.setStyleSheet(f"""
        #     QWidget {{
        #         border: 2px solid {DANGER};
        #         border-radius: 8px;
        #         background: {WHITE};
        #     }}
        # """)

        # Party selection with enhanced styling
        party_widget = QWidget()
        party_layout = QVBoxLayout(party_widget)
        party_layout.setSpacing(1)
        select_party_lbl = QLabel("🏢 Select Party:")
        select_party_lbl.setFixedHeight(35)
        select_party_lbl.setFixedWidth(150)
        select_party_lbl.setStyleSheet(label_style)
        party_layout.addWidget(select_party_lbl) 
        
        # Create searchable party input with autocomplete
        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search and select customer/client...")
        
        # Setup autocomplete
        from PyQt5.QtWidgets import QCompleter
        from PyQt5.QtCore import QStringListModel
        
        party_names = []
        self.party_data_map = {}  # Map display names to party data
        
        # Add dummy data if no parties available
        if not self.parties:
            dummy_parties = [
                {'id': 1, 'name': 'ABC Corporation', 'gst_number': '27AABCU9603R1Z0', 'phone': '+91 98765 43210'},
                {'id': 2, 'name': 'XYZ Limited', 'gst_number': '27AABCU9603R1Z1', 'phone': '+91 98765 43211'},
                {'id': 3, 'name': 'Tech Solutions Pvt Ltd', 'gst_number': '27AABCU9603R1Z2', 'phone': '+91 98765 43212'},
                {'id': 4, 'name': 'Global Industries Inc', 'gst_number': '27AABCU9603R1Z3', 'phone': '+91 98765 43213'},
                {'id': 5, 'name': 'Digital Marketing Co', 'gst_number': '27AABCU9603R1Z4', 'phone': '+91 98765 43214'},
                {'id': 6, 'name': 'Smart Solutions LLC', 'gst_number': '27AABCU9603R1Z5', 'phone': '+91 98765 43215'},
                {'id': 7, 'name': 'Future Enterprises', 'gst_number': '27AABCU9603R1Z6', 'phone': '+91 98765 43216'},
                {'id': 8, 'name': 'Innovation Hub Pvt Ltd', 'gst_number': '27AABCU9603R1Z7', 'phone': '+91 98765 43217'}
            ]
            parties_to_use = dummy_parties
        else:
            parties_to_use = self.parties
        
        for party in parties_to_use:
            gst_info = f" | GST: {party.get('gst_number', 'Not Provided')}"
            phone_info = f" | 📞 {party.get('phone', 'No Phone')}"
            display_text = f"🏢 {party['name']}{gst_info}{phone_info}"
            party_names.append(display_text)
            self.party_data_map[display_text] = party

        completer = QCompleter(party_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.party_search.setCompleter(completer)

        self.party_search.setStyleSheet(input_style)
        party_layout.addWidget(self.party_search)
        self.party_search.setFixedWidth(600)
        self.party_search.setFixedHeight(35)
        
        invoice_layout.addWidget(party_widget)

        # GST/Non-GST selection
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
        
        # Invoice number
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
        inv_date_widget.setFixedWidth(150)
        
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setStyleSheet(input_style)
        inv_date_layout.addWidget(self.invoice_date)
        
        invoice_layout.addWidget(inv_num_widget, 1)
        invoice_layout.addWidget(inv_date_widget, 1)
                        
        # Due date and payment terms
        # due_payment_row = QWidget()
        due_payment_layout = QHBoxLayout()
        # due_payment_row.setFixedHeight(150)
        # due_payment_row.setStyleSheet(f"""
        #     QWidget {{
        #         border: 2px solid {DANGER};
        #         border-radius: 8px;
        #         background: {WHITE};
        #         margin: 1px;
        #     }}
        # """)
        due_payment_layout.setSpacing(1)
        
        # Mobile number
        mobile_widget = QWidget()
        mobile_layout = QVBoxLayout(mobile_widget)
        mobile_lbl = QLabel("📱 Mobile Number:")
        mobile_lbl.setFixedHeight(35)
        mobile_widget.setFixedWidth(1000)
        mobile_lbl.setStyleSheet(label_style)
        # mobile_layout.addWidget(mobile_lbl)
        mobile_layout.setAlignment(Qt.AlignLeft)

        mobile_number = QLineEdit()
        mobile_number.setPlaceholderText("Enter mobile number...")
        mobile_number.setStyleSheet(input_style)
        mobile_number.setFixedWidth(600)
        # mobile_layout.addWidget(mobile_number)


        
        # Due date
        due_date_widget = QWidget()
        due_date_layout = QVBoxLayout(due_date_widget)
        due_date_lbl = QLabel("⏳ Due Date:")
        due_date_lbl.setFixedHeight(35)
        due_date_lbl.setStyleSheet(label_style)
        due_date_layout.addWidget(due_date_lbl)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        self.due_date.setStyleSheet(input_style)
        due_date_layout.addWidget(self.due_date)
        due_date_widget.setFixedWidth(150)
        
        # Payment terms
        terms_widget = QWidget()
        terms_layout = QVBoxLayout(terms_widget)
        terms_lbl = QLabel("💼 Payment Terms:")
        terms_lbl.setFixedHeight(35)
        terms_lbl.setStyleSheet(label_style)
        terms_layout.addWidget(terms_lbl)
        
        self.payment_terms = QComboBox()
        self.payment_terms.addItems([
            "Net 30 Days", "Net 15 Days", "Net 7 Days", 
            "Due on Receipt", "Cash on Delivery", "Custom"
        ])
        self.payment_terms.setStyleSheet(input_style)
        self.payment_terms.currentTextChanged.connect(self.update_due_date)
        terms_layout.addWidget(self.payment_terms)
        terms_widget.setFixedWidth(200)
        
        # due_payment_layout.addWidget(mobile_widget, 1)        
        # due_payment_layout.addWidget(due_date_widget, 1)
        # due_payment_layout.addWidget(terms_widget, 1)

        # layout.addWidget(invoice_row)
        layout.addLayout(invoice_layout)
        layout.setSpacing(10)
        layout.addLayout(due_payment_layout)
        # layout.addWidget(due_payment_row)
        
        # # Notes with enhanced styling
        # notes_widget = QWidget()
        # notes_layout = QVBoxLayout(notes_widget)
        # notes_layout.setContentsMargins(0, 0, 0, 0)
        # notes_layout.addWidget(QLabel("📝 Notes/Terms & Conditions:"))
        
        # self.notes = QTextEdit()
        # self.notes.setPlaceholderText("Add payment terms, delivery instructions, or other notes...")
        # self.notes.setFixedHeight(80)
        # self.notes.setStyleSheet(input_style)
        # notes_layout.addWidget(self.notes)
        
        # layout.addWidget(notes_widget)
        
        return frame
    
    def update_due_date(self):
        """Update due date based on payment terms"""
        terms = self.payment_terms.currentText()
        current_date = self.invoice_date.date()
        
        if "30 Days" in terms:
            self.due_date.setDate(current_date.addDays(30))
        elif "15 Days" in terms:
            self.due_date.setDate(current_date.addDays(15))
        elif "7 Days" in terms:
            self.due_date.setDate(current_date.addDays(7))
        elif "Due on Receipt" in terms:
            self.due_date.setDate(current_date)
    
    def create_items_section(self):
        """Create enhanced invoice items section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {DANGER};
                border-radius: 15px;
                margin: 5px;
            }}
        """)
        frame.setFixedHeight(500)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 20)
        layout.setSpacing(20)
        
        # Enhanced title and add button
        header_layout = QHBoxLayout()
        
        items_title = QLabel("🛒 Invoice Items")
        items_title.setFont(QFont("Arial", 18, QFont.Bold))
        items_title.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY}; 
                border: none;
                padding: 10px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 8px;
            }}
        """)
        # header_layout.addWidget(items_title)
        
        header_layout.addStretch()
        
        # Enhanced add item button
        add_item_btn = QPushButton("➕ Add Item")
        add_item_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #059669;

            }}
        """)
        # add_item_btn.clicked.connect(self.add_item)
        # header_layout.addWidget(add_item_btn)
        
        layout.addLayout(header_layout)
        
        # Enhanced items header with better styling
        headers_layout = QHBoxLayout()
        # headers_layout.setAlignment(Qt.AlignRight)
        headers = ["🛍️ Product", "📊 Qty", "📏 Unit", "💰 Rate", "🏷️ Disc%", "📋 Tax%", "💵 Amount", "❌ Action"]
        widths = [400, 110, 85, 110, 110, 110, 110, 110]
        space = [250, 50, 30, 30, 30, 30, 30, 30]
        
        # headers = ["🛍️ Product", "📊 Qty", "📏 Unit"]
        # widths = [450, 110, 85]
        # space = [230, 30, 30]


        for header, width in zip(headers, widths):
            label = QLabel(header)
            label.setFixedWidth(width)
            label.setFixedHeight(45)
            label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold; 
                    color: {TEXT_PRIMARY}; 
                    padding: 10px 5px;
                    background: {BACKGROUND};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    font-size: 13px;
                }}
            """)
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)



        
        layout.addLayout(headers_layout)
        
        # Enhanced scrollable items container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 2px solid {DANGER};
                border-radius: 10px;
                background: {BACKGROUND};
            }}
            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {PRIMARY};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PRIMARY_HOVER};
            }}
        """)
        
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(1)
        self.items_layout.setContentsMargins(1, 1, 1, 1)
        self.items_layout.addStretch()
        
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area)
        
        # Note: First item will be added after all sections are created
        
        return frame
    
    def create_totals_section(self):
        """Create totals section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        frame.setFixedHeight(250)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addStretch()
        
        # Totals layout
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
        
        # Grand total with emphasis
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"""
            font-size: 18px; 
            font-weight: bold; 
            color: {PRIMARY};
            background: {BACKGROUND};
            padding: 8px;
            border-radius: 4px;
        """)
        totals_layout.addRow("Grand Total:", self.grand_total_label)
        
        layout.addLayout(totals_layout)
        
        return frame
    
    def add_item(self):
        """Add new enhanced invoice item"""
        item_widget = InvoiceItemWidget(products=self.products)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
        item_widget.item_changed.connect(self.update_totals)
        
        # Add hover effect to items
        item_widget.setStyleSheet(f"""
            QWidget:hover {{
                background: rgba(59, 130, 246, 0.05);
                border-radius: 8px;
            }}
        """)
        
        # Insert before the stretch
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        self.update_totals()
    
    def remove_item(self, item_widget):
        """Remove invoice item with confirmation"""
        if self.items_layout.count() <= 2:  # Only stretch and one item
            QMessageBox.warning(self, "Cannot Remove", "🚫 At least one item is required for the invoice!")
            return
            
        reply = QMessageBox.question(
            self, "Remove Item", 
            "❓ Are you sure you want to remove this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.items_layout.removeWidget(item_widget)
            item_widget.deleteLater()
            self.update_totals()
    
    def update_totals(self):
        """Update invoice totals with enhanced calculations and animations"""
        try:
            subtotal = 0
            total_discount = 0
            total_tax = 0
            item_count = 0
            
            # Calculate totals from all items
            for i in range(self.items_layout.count() - 1):  # Exclude stretch
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
            
            # Update labels with enhanced formatting
            self.subtotal_label.setText(f"₹{subtotal:,.2f}")
            self.discount_label.setText(f"-₹{total_discount:,.2f}")
            self.tax_label.setText(f"₹{total_tax:,.2f}")
            self.grand_total_label.setText(f"₹{grand_total:,.2f}")
            
            # Update item count display
            if hasattr(self, 'item_count_label'):
                self.item_count_label.setText(f"📦 {item_count} item{'s' if item_count != 1 else ''}")
            
            # Add visual feedback for large amounts
            if grand_total > 100000:
                self.grand_total_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 20px; 
                        font-weight: bold; 
                        color: {SUCCESS};
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 rgba(34, 197, 94, 0.1), stop:1 rgba(34, 197, 94, 0.2));
                        padding: 12px;
                        border: 2px solid {SUCCESS};
                        border-radius: 8px;
                    }}
                """)
            else:
                self.grand_total_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 18px; 
                        font-weight: bold; 
                        color: {PRIMARY};
                        background: {BACKGROUND};
                        padding: 10px;
                        border-radius: 6px;
                        border: 1px solid {BORDER};
                    }}
                """)
                
        except Exception as e:
            print(f"Error updating totals: {e}")
            # Set default values on error - create labels if they don't exist
            if not hasattr(self, 'subtotal_label'):
                self.subtotal_label = QLabel("₹0.00")
            if not hasattr(self, 'discount_label'):
                self.discount_label = QLabel("₹0.00")
            if not hasattr(self, 'tax_label'):
                self.tax_label = QLabel("₹0.00")
            if not hasattr(self, 'grand_total_label'):
                self.grand_total_label = QLabel("₹0.00")
            
            self.subtotal_label.setText("₹0.00")
            self.discount_label.setText("₹0.00")
            self.tax_label.setText("₹0.00")
            self.grand_total_label.setText("₹0.00")
    
    def save_invoice(self):
        """Save invoice data"""
        # Validate required fields - get party data from search input
        party_text = self.party_search.text().strip()
        party_data = self.party_data_map.get(party_text)
        
        if not party_data or not party_text:
            QMessageBox.warning(self, "Error", "Please select a valid party from the search!")
            return
        
        # Collect items data
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
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        total_discount = sum(item['discount_amount'] for item in items)
        total_tax = sum(item['tax_amount'] for item in items)
        grand_total = subtotal - total_discount + total_tax
        
        invoice_data = {
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd'),
            'due_date': self.due_date.date().toString('yyyy-MM-dd'),
            'notes': self.notes.toPlainText(),
            'subtotal': subtotal,
            'total_discount': total_discount,
            'total_tax': total_tax,
            'grand_total': grand_total,
            'status': 'Draft',
            'items': items
        }
        
        try:
            if self.invoice_data:  # Editing
                invoice_data['id'] = self.invoice_data['id']
                db.update_invoice(invoice_data)
                QMessageBox.information(self, "Success", "Invoice updated successfully!")
            else:  # Creating new
                db.add_invoice(invoice_data)
                QMessageBox.information(self, "Success", "Invoice created successfully!")
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")

class InvoicesScreen(BaseScreen):
    """Enhanced Invoices screen with modern UI and advanced functionality"""
    
    def __init__(self):
        super().__init__("💼 Invoices & Billing")
        self.all_invoices_data = []
        self.setup_invoices_screen()
        self.load_invoices_data()
    
    def setup_invoices_screen(self):
        """Setup enhanced invoices screen content"""
        # Enhanced top action bar with modern design
        self.setup_action_bar()
        
        # Modern invoices table with advanced features
        self.setup_invoices_table()
    
    def setup_action_bar(self):
        """Setup enhanced top action bar with modern design"""
        # Main container with enhanced styling
        action_frame = QFrame()
        action_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {WHITE}, stop:1 #F8FAFC);
                border: 2px solid {BORDER};
                border-radius: 15px;
                margin: 1px;
                padding: 10px;
            }}
        """)
        
        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(15)
        action_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced search with icon
        search_container = QFrame()
        search_container.setFixedWidth(350)
        search_container.setFixedHeight(65)
        search_container.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                background: {WHITE};
            }}
            QFrame:focus-within {{
                border-color: {PRIMARY};
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 0, 0, 0)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; padding: 1px;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search invoices by number, party name, or amount...")
        self.search_input.setAlignment(Qt.AlignLeft)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.search_input.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.search_input)
        
        action_layout.addWidget(search_container)
        action_layout.addStretch()
        
        # Enhanced action buttons with icons
        buttons_data = [
            (" Export", "secondary", self.export_invoices),
            ("📋 Templates", "warning", self.manage_templates),
            ("➕ Create Invoice", "primary", self.create_invoice)
        ]
        
        for text, style, callback in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setMinimumWidth(130)
            btn.clicked.connect(callback)
            btn.setCursor(Qt.PointingHandCursor)
            
            if style == "primary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
                        color: white;
                        border: none;
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {PRIMARY_HOVER}, stop:1 #1D4ED8);

                    }}
                    QPushButton:pressed {{

                    }}
                """)
            elif style == "secondary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {WHITE};
                        color: {TEXT_PRIMARY};
                        border: 2px solid {BORDER};
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        border-color: {BORDER};
                        background: #F8FAFC;
                        color: {PRIMARY};
                    }}
                """)
            elif style == "warning":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {WARNING};
                        color: white;
                        border: none;
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: #F59E0B;
                    }}
                """)
            elif style == "info":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #3B82F6;
                        color: white;
                        border: none;
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: #2563EB;
                    }}
                """)
            
            action_layout.addWidget(btn)
        
        self.add_content(action_frame)

    def setup_filters_and_stats(self):
        """Setup enhanced filters and invoice statistics"""
        # Main container with modern styling
        container_frame = QFrame()
        container_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 15px;
                margin: 1px;
            }}
        """)
        
        main_layout = QVBoxLayout(container_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(20)
        
        # Statistics cards row
        stats_container = QHBoxLayout()
        # stats_container.setSpacing(15)
        
        # Enhanced statistics cards
        stats_data = [
            ("📋", "Total Invoices", "0", PRIMARY, "total_invoices_label"),
            ("💰", "Total Amount", "₹0", SUCCESS, "total_amount_label"),
            ("⏰", "Overdue", "0", DANGER, "overdue_label"),
            ("✅", "Paid", "0", "#10B981", "paid_label")
        ]
        
        for icon, label_text, value, color, attr_name in stats_data:
            card = self.create_enhanced_stat_card(icon, label_text, value, color)
            setattr(self, attr_name, card.findChild(QLabel, "value_label"))
            stats_container.addWidget(card)
        
        main_layout.addLayout(stats_container)
        
        self.add_content(container_frame)
    
    def create_enhanced_stat_card(self, icon, label_text, value, color):
        """Create enhanced statistics card with animations"""
        card = QFrame()
        card.setFixedSize(200, 50)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {WHITE}, stop:1 #F8FAFC);
                border: 2px solid {BORDER};
                border-radius: 12px;
                margin: 2px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FEFEFE, stop:1 #F0F4F8);

            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # # Icon and value row
        # top_layout = QHBoxLayout()
        # top_layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(28, 28)
        # icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
        """)
        layout.addWidget(icon_label)

        # Label
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(f"color: #6B7280; font-size: 12px; border: none; font-weight: 500;")
        # label_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_widget)
        layout.addStretch()

  
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value_label")  # For finding later
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        # value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(value_label)        
        
        return card

    def setup_filters_layout(self, parent_layout):
        """Setup the filters layout with all filter controls"""
        
        # Filters section
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(1)
        
        # # Filter title
        # filter_title = QLabel("🎯 Smart Filters")
        # filter_title.setFont(QFont("Arial", 14, QFont.Bold))
        # filter_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        # filters_layout.addWidget(filter_title)
        
        # Enhanced filter controls
        filter_controls = [
            ("📊 Status:", ["All", "Paid", "Overdue", "Cancelled"], "status_filter"),
            ("📅 Period:", ["All Time", "Today", "This Week", "This Month", "Last Month", "This Quarter", "This Year", "Custom"], "period_filter"),
            ("💵 Amount:", ["All Amounts", "Under ₹10K", "₹10K - ₹50K", "₹50K - ₹1L", "Above ₹1L"], "amount_filter"),
            ("👥 Party:", ["All Parties"], "party_filter")
        ]
        
        for label_text, items, attr_name in filter_controls:
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY}; 
                    font-weight: 600; 
                    border: none;
                    font-size: 13px;
                }}
            """)
            filters_layout.addWidget(label)
            
            # Enhanced ComboBox
            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedWidth(140)
            combo.setFixedHeight(35)
            combo.setStyleSheet(f"""
                QComboBox {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    padding: 6px 12px;
                    background: {WHITE};
                    font-size: 13px;
                    color: {TEXT_PRIMARY};
                    font-weight: 500;
                }}
                QComboBox:hover {{
                    border-color: {BORDER};
                    background: #F8FAFC;
                }}
                QComboBox:focus {{
                    border-color: {BORDER};
                    background: {WHITE};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 30px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid {TEXT_PRIMARY};
                    margin-right: 8px;
                }}
                QComboBox QAbstractItemView {{
                    border: 2px solid {BORDER};
                    background: {WHITE};
                    selection-background-color: {PRIMARY};
                    selection-color: white;
                    border-radius: 8px;
                    outline: none;
                }}
            """)
            combo.currentTextChanged.connect(self.filter_invoices)
            setattr(self, attr_name, combo)
            filters_layout.addWidget(combo)
            filters_layout.addSpacing(30)

        
        filters_layout.addStretch()
        
        # Enhanced action buttons
        action_buttons = [
            ("🔄", "Refresh Data", self.load_invoices_data),
            # ("🗑️", "Clear Filters", self.clear_filters)
        ]
        
        for icon, tooltip, callback in action_buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(35, 35)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {BORDER};
                    border-radius: 17px;
                    background: {WHITE};
                    font-size: 16px;
                    color: {TEXT_PRIMARY};
                    padding: 6px;
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: white;
                    border-color: {BORDER};
                }}
                QPushButton:pressed {{

                }}
            """)
            btn.clicked.connect(callback)
            filters_layout.addWidget(btn)
        
        # Add the filters frame to the parent layout
        parent_layout.addWidget(filters_frame)

    def setup_invoices_table(self):
        """Setup enhanced invoices table with modern design"""
        # First setup the filters and statistics
        self.setup_filters_and_stats()
        
        # Main container with enhanced styling
        container_frame = QFrame()
        container_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(container_frame)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)
        
        # Add filters layout at the top of the table section
        self.setup_filters_layout(layout)
        
        
        # Enhanced table headers and setup
        headers = ["Select", "Invoice No.", "Date", "Party", "Due Date", "Amount", "Status", "Actions", "Priority"]
        self.invoices_table = CustomTable(0, len(headers), headers)
        
        # Enhanced table styling
        self.invoices_table.setStyleSheet(f"""
            QTableWidget {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                gridline-color: {BORDER};
                font-size: 13px;
                selection-background-color: rgba(59, 130, 246, 0.2);
            }}
            QTableWidget::hover {{
                border: 2px solid {PRIMARY};
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {BORDER};
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item:hover {{
                background: #F8FAFC;
            }}
            QTableWidget::item:selected {{
                background: rgba(59, 130, 246, 0.3);
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {PRIMARY}, stop:1 #2563EB);
                color: white;
                padding: 12px;
                border: none;
                font-weight: 600;
                font-size: 13px;
            }}
            QHeaderView::section:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }}
            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PRIMARY};
            }}
        """)
        
        # Enhanced table configuration
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.invoices_table.setSortingEnabled(True)
        self.invoices_table.setShowGrid(True)
        
        # Enhanced column widths
        self.invoices_table.setColumnWidth(0, 60)   # Select
        self.invoices_table.setColumnWidth(1, 120)  # Invoice No
        self.invoices_table.setColumnWidth(2, 100)  # Date
        self.invoices_table.setColumnWidth(3, 200)  # Party
        self.invoices_table.setColumnWidth(4, 100)  # Due Date
        self.invoices_table.setColumnWidth(5, 120)  # Amount
        self.invoices_table.setColumnWidth(6, 100)  # Status
        self.invoices_table.setColumnWidth(7, 150)  # Actions
        self.invoices_table.setColumnWidth(8, 80)   # Priority
        
        # Enhanced context menu
        self.invoices_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.invoices_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enhanced double-click handling
        self.invoices_table.itemDoubleClicked.connect(self.edit_invoice)
        
        layout.addWidget(self.invoices_table)
        
        # Enhanced pagination and info bar
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setSpacing(15)
        
        # Enhanced items per page
        items_layout = QHBoxLayout()
        items_layout.addWidget(QLabel("Items per page:"))
        
        self.items_per_page = QComboBox()
        self.items_per_page.addItems(["25", "50", "100", "200"])
        self.items_per_page.setCurrentText("50")
        self.items_per_page.setFixedWidth(80)
        self.items_per_page.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px;
                background: {WHITE};
            }}
        """)
        self.items_per_page.currentTextChanged.connect(self.load_invoices_data)
        items_layout.addWidget(self.items_per_page)
        
        pagination_layout.addLayout(items_layout)
        pagination_layout.addStretch()
        
        # Enhanced pagination info
        self.pagination_info = QLabel("Showing 0 - 0 of 0 items")
        self.pagination_info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 500;")
        pagination_layout.addWidget(self.pagination_info)
        
        # Enhanced pagination controls
        pagination_controls = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("◀ Previous")
        self.prev_page_btn.setFixedHeight(35)
        self.prev_page_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                background: {WHITE};
                color: {TEXT_PRIMARY};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
                border-color: {BORDER};
            }}
            QPushButton:disabled {{
                color: #9CA3AF;
                background: #F3F4F6;
            }}
        """)
        self.prev_page_btn.clicked.connect(self.previous_page)
        pagination_controls.addWidget(self.prev_page_btn)
        
        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; padding: 0 15px;")
        pagination_controls.addWidget(self.page_info)
        
        self.next_page_btn = QPushButton("Next ▶")
        self.next_page_btn.setFixedHeight(35)
        self.next_page_btn.setStyleSheet(self.prev_page_btn.styleSheet())
        self.next_page_btn.clicked.connect(self.next_page)
        pagination_controls.addWidget(self.next_page_btn)
        
        pagination_layout.addLayout(pagination_controls)
        layout.addWidget(pagination_frame)
        
        self.add_content(container_frame)
        
        # Store original data for filtering
        self.all_invoices_data = []
    
    def load_invoices_data(self):
        """Load invoices data into table"""
        try:
            invoices = db.get_invoices()
            self.all_invoices_data = invoices
            self.populate_table(invoices)
            self.update_stats(invoices)
        except Exception as e:
            # Show sample data if database not available
            sample_data = [
                {
                    'id': 1, 'invoice_no': 'INV-001', 'date': '2024-01-01', 
                    'party_name': 'ABC Corp', 'due_date': '2024-01-31',
                    'grand_total': 54000, 'status': 'Paid'
                },
                {
                    'id': 2, 'invoice_no': 'INV-002', 'date': '2024-01-02',
                    'party_name': 'XYZ Ltd', 'due_date': '2024-02-01',
                    'grand_total': 25000, 'status': 'Sent'
                }
            ]
            self.all_invoices_data = sample_data
            self.populate_table(sample_data)
            self.update_stats(sample_data)
    
    def populate_table(self, invoices_data):
        """Populate table with invoices data with enhanced features"""
        self.invoices_table.setRowCount(len(invoices_data))
        
        for row, invoice in enumerate(invoices_data):
            # Select checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {BORDER};
                    border-radius: 3px;
                    background: {WHITE};
                }}
                QCheckBox::indicator:checked {{
                    background: {PRIMARY};
                    border-color: {BORDER};
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0IDcuNUwxMSAxLjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                }}
            """)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.invoices_table.setCellWidget(row, 0, checkbox_widget)
            
            # Invoice number with enhanced styling
            invoice_item = QTableWidgetItem(str(invoice.get('invoice_no', f'INV-{invoice["id"]:03d}')))
            invoice_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.invoices_table.setItem(row, 1, invoice_item)
            
            # Date with color coding
            date_item = QTableWidgetItem(str(invoice.get('date', '2024-01-01')))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.invoices_table.setItem(row, 2, date_item)
            
            # Party name
            party_item = QTableWidgetItem(str(invoice.get('party_name', 'Sample Party')))
            self.invoices_table.setItem(row, 3, party_item)
            
            # Due date with overdue indicator
            due_date_item = QTableWidgetItem(str(invoice.get('due_date', '2024-01-31')))
            due_date_item.setTextAlignment(Qt.AlignCenter)
            # Add overdue styling if needed
            if invoice.get('status') == 'Overdue':
                due_date_item.setBackground(QColor("#FEE2E2"))
            self.invoices_table.setItem(row, 4, due_date_item)
            
            # Amount with currency formatting
            amount = invoice.get('grand_total', 0)
            amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.invoices_table.setItem(row, 5, amount_item)
            
            # Enhanced status with color coding
            status = invoice.get('status', 'Draft')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code status
            status_colors = {
                'Draft': ("#6B7280", "#F3F4F6"),
                'Sent': ("#3B82F6", "#EBF8FF"),
                'Paid': ("#10B981", "#D1FAE5"),
                'Overdue': ("#EF4444", "#FEE2E2"),
                'Cancelled': ("#6B7280", "#F3F4F6")
            }
            
            if status in status_colors:
                color, bg_color = status_colors[status]
                status_item.setForeground(QColor(color))
                status_item.setBackground(QColor(bg_color))
            
            self.invoices_table.setItem(row, 6, status_item)
            
            # Enhanced action buttons
            actions_widget = self.create_action_buttons(invoice)
            self.invoices_table.setCellWidget(row, 7, actions_widget)
            
            # Priority indicator
            priority = self.get_invoice_priority(invoice)
            priority_item = QTableWidgetItem(priority)
            priority_item.setTextAlignment(Qt.AlignCenter)
            
            priority_colors = {
                "🔴": "#EF4444",  # High
                "🟡": "#F59E0B",  # Medium
                "🟢": "#10B981"   # Low
            }
            
            if priority in priority_colors:
                priority_item.setForeground(QColor(priority_colors[priority]))
            
            self.invoices_table.setItem(row, 8, priority_item)
        
        self.update_pagination_info()
    
    def create_action_buttons(self, invoice):
        """Create enhanced action buttons for each invoice row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Action buttons with enhanced styling
        actions = [
            ("👁️", "View", lambda: self.view_invoice(invoice['id'])),
            ("✏️", "Edit", lambda: self.edit_invoice(invoice['id'])),
            ("📤", "Send", lambda: self.send_invoice(invoice['id'])),
            ("💰", "Payment", lambda: self.record_payment(invoice['id']))
        ]
        
        for icon, tooltip, callback in actions:
            btn = QPushButton(icon)
            btn.setFixedSize(28, 28)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 14px;
                    background: {WHITE};
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: white;
                    border-color: {BORDER};
                }}
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        return widget
    
    def get_invoice_priority(self, invoice):
        """Determine invoice priority based on amount and due date"""
        amount = invoice.get('grand_total', 0)
        status = invoice.get('status', 'Draft')
        
        if status == 'Overdue':
            return "🔴"  # High priority
        elif amount > 50000:
            return "🔴"  # High priority for large amounts
        elif amount > 20000:
            return "🟡"  # Medium priority
        else:
            return "🟢"  # Low priority
    
    def update_pagination_info(self):
        """Update pagination information"""
        total_items = len(self.all_invoices_data)
        items_per_page = int(self.items_per_page.currentText())
        current_page = getattr(self, 'current_page', 1)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        
        start_item = (current_page - 1) * items_per_page + 1
        end_item = min(current_page * items_per_page, total_items)
        
        self.pagination_info.setText(f"Showing {start_item} - {end_item} of {total_items} items")
        self.page_info.setText(f"Page {current_page} of {total_pages}")
        
        # Update button states
        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)
    
    def handle_table_action(self, action):
        """Handle table action buttons"""
        if action == "search":
            self.show_advanced_search()
        elif action == "import":
            self.import_invoices()
        elif action == "export":
            self.export_selected_invoices()
        elif action == "delete":
            self.delete_selected_invoices()
        elif action == "bulk":
            self.show_bulk_actions_menu()
    
    def clear_filters(self):
        """Clear all applied filters"""
        self.status_filter.setCurrentIndex(0)
        self.period_filter.setCurrentIndex(0)
        self.amount_filter.setCurrentIndex(0)
        self.party_filter.setCurrentIndex(0)
        self.filter_invoices()
    
    def manage_templates(self):
        """Manage invoice templates"""
        QMessageBox.information(self, "Templates", "Template management coming soon!")
    
    def previous_page(self):
        """Go to previous page"""
        current_page = getattr(self, 'current_page', 1)
        if current_page > 1:
            self.current_page = current_page - 1
            self.load_invoices_data()
    
    def next_page(self):
        """Go to next page"""
        total_items = len(self.all_invoices_data)
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        current_page = getattr(self, 'current_page', 1)
        
        if current_page < total_pages:
            self.current_page = current_page + 1
            self.load_invoices_data()
    
    # Placeholder methods for future implementation
    def show_advanced_search(self): pass
    def import_invoices(self): pass
    def export_selected_invoices(self): pass
    def delete_selected_invoices(self): pass
    def show_bulk_actions_menu(self): pass
    def view_invoice(self, invoice_id): pass
    def send_invoice(self, invoice_id): pass
    def record_payment(self, invoice_id): pass
    def show_context_menu(self, position): pass
    
    def create_action_buttons(self, invoice):
        """Create action buttons for each row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(25, 25)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 12px;
                background: {WHITE};
                color: {PRIMARY};
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_invoice(invoice))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setStyleSheet(view_btn.styleSheet())
        edit_btn.clicked.connect(lambda: self.edit_invoice(invoice))
        layout.addWidget(edit_btn)
        
        # Print/PDF button
        print_btn = QPushButton("🖨️")
        print_btn.setFixedSize(25, 25)
        print_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {SUCCESS};
                border-radius: 12px;
                background: {WHITE};
                color: {SUCCESS};
            }}
            QPushButton:hover {{
                background: {SUCCESS};
                color: {WHITE};
            }}
        """)
        print_btn.clicked.connect(lambda: self.print_invoice(invoice))
        layout.addWidget(print_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(25, 25)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {DANGER};
                border-radius: 12px;
                background: {WHITE};
                color: {DANGER};
            }}
            QPushButton:hover {{
                background: {DANGER};
                color: {WHITE};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_invoice(invoice))
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_stats(self, invoices):
        """Update enhanced statistics with all metrics"""
        total_count = len(invoices)
        total_amount = sum(inv['grand_total'] for inv in invoices)
        
        # Calculate various statuses
        overdue_count = sum(1 for inv in invoices if inv.get('status') == 'Overdue')
        paid_count = sum(1 for inv in invoices if inv.get('status') == 'Paid')
        
        # Update all statistics labels
        self.total_invoices_label.setText(str(total_count))
        self.total_amount_label.setText(f"₹{total_amount:,.0f}")
        self.overdue_label.setText(str(overdue_count))
        self.paid_label.setText(str(paid_count))
    
    def filter_invoices(self):
        """Enhanced filter invoices based on multiple criteria"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        period_filter = self.period_filter.currentText()
        amount_filter = self.amount_filter.currentText()
        party_filter = self.party_filter.currentText()
        
        filtered_data = []
        for invoice in self.all_invoices_data:
            # Search filter
            if search_text:
                searchable_text = f"{invoice.get('invoice_no', '')} {invoice.get('party_name', '')}".lower()
                if search_text not in searchable_text:
                    continue
            
            # Status filter
            if status_filter != "All" and invoice.get('status', 'Draft') != status_filter:
                continue
            
            # Amount filter
            amount = invoice.get('grand_total', 0)
            if amount_filter == "Under ₹10K" and amount >= 10000:
                continue
            elif amount_filter == "₹10K - ₹50K" and not (10000 <= amount < 50000):
                continue
            elif amount_filter == "₹50K - ₹1L" and not (50000 <= amount < 100000):
                continue
            elif amount_filter == "Above ₹1L" and amount < 100000:
                continue
            
            # Party filter
            if party_filter != "All Parties" and invoice.get('party_name', '') != party_filter:
                continue
            
            # Period filter (simplified implementation)
            # In a real application, you would parse dates and filter by actual date ranges
            
            filtered_data.append(invoice)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
    
    def create_invoice(self):
        """Open create invoice dialog"""
        dialog = InvoiceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_invoices_data()
    
    def edit_invoice(self, invoice):
        """Open edit invoice dialog"""
        dialog = InvoiceDialog(self, invoice)
        if dialog.exec_() == QDialog.Accepted:
            self.load_invoices_data()
    
    def view_invoice(self, invoice):
        """View invoice details"""
        invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
        QMessageBox.information(self, "View Invoice", f"Viewing invoice {invoice_no}")
    
    def print_invoice(self, invoice):
        """Print/export invoice as PDF"""
        QMessageBox.information(self, "Print Invoice", "Print/PDF functionality will be implemented soon!")
    
    def delete_invoice(self, invoice):
        """Delete invoice with confirmation"""
        invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete invoice {invoice_no}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_invoice(invoice['id'])
                QMessageBox.information(self, "Success", "Invoice deleted successfully!")
                self.load_invoices_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")
    
    def export_invoices(self):
        """Export invoices data"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")
    
    
    def refresh_data(self):
        """Refresh invoices data"""
        self.load_invoices_data()
