"""
Payments screen - Record and manage payments with enhanced UI and functionality
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSplitter, QGroupBox,
    QAbstractItemView, QMenu, QAction, QCompleter, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QCursor

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER, get_title_font
)
from database import db

class PaymentDialog(QDialog):
    """Enhanced dialog for recording payments with modern UI"""
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.parties = []
        self.invoices = []
        
        # Initialize window properties
        self.init_window()
        
        # Load required data
        self.load_data()
        
        # Setup the complete UI
        self.setup_ui()
        
        # Auto-populate if editing
        if self.payment_data:
            self.populate_form()
    
    def init_window(self):
        """Initialize window properties and styling"""
        title = "💳 Record Payment" if not self.payment_data else "📝 Edit Payment"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(900, 750)  # Increased size to accommodate all elements
        
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
        """Load parties and invoices data with error handling"""
        try:
            self.parties = db.get_parties() or []
            self.invoices = db.get_invoices() or []
        except Exception as e:
            print(f"Database error: {e}")
            # Enhanced sample data for demonstration
            self.parties = [
                {'id': 1, 'name': 'ABC Corporation', 'type': 'Customer', 'opening_balance': 5000, 'phone': '+91 98765 43210'},
                {'id': 2, 'name': 'XYZ Limited', 'type': 'Supplier', 'opening_balance': -2000, 'phone': '+91 98765 43211'},
                {'id': 3, 'name': 'Tech Solutions Pvt Ltd', 'type': 'Both', 'opening_balance': 0, 'phone': '+91 98765 43212'}
            ]
            self.invoices = [
                {'id': 1, 'invoice_no': 'INV-001', 'party_id': 1, 'grand_total': 54000, 'status': 'Sent', 'due_amount': 54000},
                {'id': 2, 'invoice_no': 'INV-002', 'party_id': 2, 'grand_total': 25000, 'status': 'Sent', 'due_amount': 25000},
                {'id': 3, 'invoice_no': 'INV-003', 'party_id': 1, 'grand_total': 18000, 'status': 'Paid', 'due_amount': 0}
            ]
    
    def setup_ui(self):
        """Setup enhanced dialog UI with modern design"""
        # Create main layout with optimized spacing
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)  # Reduced spacing
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins
        
        # Enhanced title section
        self.setup_title_section()
        
        # Main content sections
        self.setup_content_sections()
        
        # Action buttons
        self.setup_action_buttons()
    
    def setup_title_section(self):
        """Setup enhanced title section with compact layout"""
        title_container = QFrame()
        title_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
                border-radius: 12px;
                margin: 2px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        
        # Main title
        title_text = "💳 Record New Payment" if not self.payment_data else "📝 Edit Payment"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))  # Slightly smaller font
        self.title_label.setStyleSheet("color: white; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Payment ID for editing
        if self.payment_data:
            payment_id = self.payment_data.get('id', 'N/A')
            id_label = QLabel(f"Payment #{payment_id}")
            id_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; border: none;")
            title_layout.addWidget(id_label)
        
        self.main_layout.addWidget(title_container)
    
    def setup_content_sections(self):
        """Setup main content sections"""
        # Create splitter for better layout management
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet(f"""
            QSplitter {{
                border: none;
                background: transparent;
            }}
            QSplitter::handle {{
                background: {BORDER};
                border-radius: 3px;
                width: 6px;
                margin: 2px 5px;
            }}
        """)
        
        # Left section - Payment details
        self.payment_details_frame = self.create_payment_details_section()
        content_splitter.addWidget(self.payment_details_frame)
        
        # Right section - Summary and info
        self.summary_frame = self.create_summary_section()
        content_splitter.addWidget(self.summary_frame)
        
        # Set proportions - give more space to the payment details form
        content_splitter.setSizes([500, 350])
        
        self.main_layout.addWidget(content_splitter)
    
    def create_payment_details_section(self):
        """Create enhanced payment details section with scrollable content"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 15px;
                margin: 2px;
            }}
        """)
        
        # Main layout for the frame
        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
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
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PRIMARY};
            }}
        """)
        
        # Content widget for scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Section header
        header = QLabel("💼 Payment Information")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                border: none;
                padding: 10px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 8px;
            }}
        """)
        layout.addWidget(header)
        
        # Enhanced form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)  # Reduced spacing to fit more content
        form_layout.setHorizontalSpacing(15)
        
        # Enhanced input styling with compact dimensions
        input_style = f"""
            QComboBox, QDoubleSpinBox, QLineEdit, QDateEdit, QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
                min-height: 16px;
                max-height: 32px;
            }}
            QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {PRIMARY};
                background: #F8FAFC;
            }}
            QComboBox:hover, QDoubleSpinBox:hover, QLineEdit:hover, QDateEdit:hover, QTextEdit:hover {{
                border-color: {PRIMARY_HOVER};
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
        
        # Payment type with radio buttons for better UX
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setSpacing(20)
        
        self.payment_type_group = QButtonGroup()
        
        self.received_radio = QRadioButton("💰 Payment Received")
        self.received_radio.setChecked(True)
        self.received_radio.setStyleSheet(f"""
            QRadioButton {{
                font-size: 14px;
                color: {TEXT_PRIMARY};
                font-weight: 500;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:checked {{
                background: {SUCCESS};
                border: 2px solid {SUCCESS};
                border-radius: 9px;
            }}
        """)
        
        self.made_radio = QRadioButton("💸 Payment Made")
        self.made_radio.setStyleSheet(f"""
            QRadioButton {{
                font-size: 14px;
                color: {TEXT_PRIMARY};
                font-weight: 500;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:checked {{
                background: {DANGER};
                border: 2px solid {DANGER};
                border-radius: 9px;
            }}
        """)
        
        self.payment_type_group.addButton(self.received_radio, 0)
        self.payment_type_group.addButton(self.made_radio, 1)
        self.payment_type_group.buttonClicked.connect(self.on_payment_type_changed)
        
        type_layout.addWidget(self.received_radio)
        type_layout.addWidget(self.made_radio)
        type_layout.addStretch()
        
        form_layout.addRow("📋 Payment Type:", type_widget)
    
        # Party selection with searchable combo
        self.party_combo = QComboBox()
        self.party_combo.setEditable(True)
        self.party_combo.addItem("🏢 Select Party", None)
        self.update_party_combo()
        self.party_combo.setStyleSheet(input_style)
        self.party_combo.currentTextChanged.connect(self.on_party_changed)
        form_layout.addRow("🏢 Select Party:", self.party_combo)
        
        # Invoice reference with enhanced selection
        self.invoice_combo = QComboBox()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        self.invoice_combo.setStyleSheet(input_style)
        self.invoice_combo.currentTextChanged.connect(self.on_invoice_changed)
        form_layout.addRow("📄 Invoice Reference:", self.invoice_combo)
        
        # Amount with currency and validation
        amount_container = QWidget()
        amount_layout = QHBoxLayout(amount_container)
        amount_layout.setSpacing(10)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 9999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setStyleSheet(input_style)
        self.amount_input.valueChanged.connect(self.validate_amount)
        amount_layout.addWidget(self.amount_input)
        
        # Outstanding amount indicator
        self.outstanding_label = QLabel("💡 Outstanding: ₹0.00")
        self.outstanding_label.setStyleSheet(f"""
            QLabel {{
                color: {SUCCESS};
                font-weight: bold;
                font-size: 13px;
                border: 1px solid {SUCCESS};
                border-radius: 6px;
                padding: 6px 10px;
                background: rgba(34, 197, 94, 0.1);
            }}
        """)
        amount_layout.addWidget(self.outstanding_label)
        
        form_layout.addRow("💰 Amount:", amount_container)
        
        # Payment date with calendar
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setStyleSheet(input_style)
        form_layout.addRow("📅 Payment Date:", self.payment_date)
        
        # Payment method with icons
        self.payment_method = QComboBox()
        payment_methods = [
            ("💵 Cash", "Cash"),
            ("🏦 Bank Transfer", "Bank Transfer"),
            ("📝 Cheque", "Cheque"),
            ("📱 UPI", "UPI"),
            ("💳 Credit Card", "Credit Card"),
            ("💳 Debit Card", "Debit Card"),
            ("💻 Net Banking", "Net Banking"),
            ("📋 Other", "Other")
        ]
        
        for display_text, value in payment_methods:
            self.payment_method.addItem(display_text, value)
        
        self.payment_method.setStyleSheet(input_style)
        form_layout.addRow("💳 Payment Method:", self.payment_method)
        
        # Reference number with validation
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Enter transaction/reference number...")
        self.reference_input.setStyleSheet(input_style)
        form_layout.addRow("🔗 Reference Number:", self.reference_input)
        
        # Notes section
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add payment notes, remarks, or additional details...")
        self.notes_input.setFixedHeight(70)  # Reduced height to save space
        self.notes_input.setStyleSheet(input_style)
        form_layout.addRow("📝 Notes:", self.notes_input)
        
        layout.addWidget(form_widget)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        return frame
    
    def create_summary_section(self):
        """Create payment summary and info section with optimized layout"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 15px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins
        layout.setSpacing(12)  # Reduced spacing
        
        # Summary header
        summary_header = QLabel("📊 Payment Summary")
        summary_header.setFont(QFont("Arial", 14, QFont.Bold))  # Slightly smaller font
        summary_header.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                border: none;
                padding: 8px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 8px;
            }}
        """)
        layout.addWidget(summary_header)
        
        # Summary content with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
                min-height: 15px;
            }}
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(10)
        
        # Summary content
        self.summary_content = QLabel("Select party and invoice to see payment summary")
        self.summary_content.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 12px;
                background: {BACKGROUND};
                line-height: 1.4;
            }}
        """)
        self.summary_content.setWordWrap(True)
        self.summary_content.setAlignment(Qt.AlignTop)
        content_layout.addWidget(self.summary_content)
        
        # Quick tips with compact formatting
        tips_header = QLabel("💡 Quick Tips")
        tips_header.setFont(QFont("Arial", 12, QFont.Bold))
        tips_header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; margin-top: 8px;")
        content_layout.addWidget(tips_header)
        
        tips_content = QLabel("""
• Payment Received: Money coming in
• Payment Made: Money going out  
• Link to invoice for reconciliation
• Use reference numbers for tracking
        """)
        tips_content.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px;
                background: #F0F9FF;
                line-height: 1.3;
            }}
        """)
        tips_content.setWordWrap(True)
        content_layout.addWidget(tips_content)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return frame
    
    def setup_action_buttons(self):
        """Setup enhanced action buttons with compact layout"""
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 5px;
            }}
        """)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(12, 8, 12, 8)  # Reduced margins
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setFixedHeight(35)  # Reduced height
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WARNING};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                background: #F59E0B;
            }}
        """)
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFixedHeight(35)  # Reduced height
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background: #DC2626;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        save_text = "💾 Update Payment" if self.payment_data else "💾 Record Payment"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setFixedHeight(35)  # Reduced height
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
                min-width: 110px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """)
        self.save_btn.clicked.connect(self.save_payment)
        button_layout.addWidget(self.save_btn)
        
        self.main_layout.addWidget(button_container)
    
    def update_party_combo(self):
        """Update party combo based on payment type"""
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        self.party_combo.clear()
        self.party_combo.addItem("🏢 Select Party", None)
        
        # Filter parties based on payment type with enhanced display
        for party in self.parties:
            party_type = party.get('type', 'Both')
            opening_balance = party.get('opening_balance', 0)
            phone = party.get('phone', '')
            
            show_party = False
            if payment_type == "Payment Received":
                # Show customers and parties with positive balance
                show_party = party_type in ['Customer', 'Both'] or opening_balance > 0
                icon = "👤"
            else:  # Payment Made
                # Show suppliers and parties with negative balance
                show_party = party_type in ['Supplier', 'Both'] or opening_balance < 0
                icon = "🏭"
            
            if show_party:
                balance_info = f" | Balance: ₹{opening_balance:,.0f}" if opening_balance != 0 else ""
                phone_info = f" | 📞 {phone}" if phone else ""
                display_text = f"{icon} {party['name']}{balance_info}{phone_info}"
                self.party_combo.addItem(display_text, party)
    
    def on_payment_type_changed(self):
        """Handle payment type change with visual feedback"""
        self.update_party_combo()
        self.update_invoice_combo()
        self.update_summary()
        
        # Update UI colors based on type
        if self.received_radio.isChecked():
            self.title_label.setText("💰 Record Payment Received")
        else:
            self.title_label.setText("💸 Record Payment Made")
    
    def on_party_changed(self):
        """Handle party selection change with enhanced feedback"""
        self.update_invoice_combo()
        self.update_outstanding_display()
        self.update_summary()
    
    def update_invoice_combo(self):
        """Update invoice combo with enhanced filtering and display"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        
        party_data = self.party_combo.currentData()
        if party_data:
            party_id = party_data['id']
            payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
            
            # Filter invoices for selected party
            relevant_invoices = [inv for inv in self.invoices if inv.get('party_id') == party_id]
            
            for invoice in relevant_invoices:
                # Show unpaid or partially paid invoices
                due_amount = invoice.get('due_amount', invoice.get('grand_total', 0))
                if due_amount > 0:
                    status = invoice.get('status', 'Sent')
                    status_icon = "📄" if status == 'Sent' else "⏰" if status == 'Overdue' else "📋"
                    
                    invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
                    display_text = f"{status_icon} {invoice_no} - ₹{due_amount:,.0f} due"
                    self.invoice_combo.addItem(display_text, invoice)
    
    def on_invoice_changed(self):
        """Handle invoice selection change"""
        self.update_outstanding_display()
        self.update_summary()
        
        # Auto-fill amount with outstanding amount
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            self.amount_input.setValue(due_amount)
    
    def update_outstanding_display(self):
        """Update outstanding amount display with enhanced info"""
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            self.outstanding_label.setText(f"💡 Due: ₹{due_amount:,.2f}")
            self.outstanding_label.setStyleSheet(f"""
                QLabel {{
                    color: {DANGER if due_amount > 0 else SUCCESS};
                    font-weight: bold;
                    font-size: 13px;
                    border: 1px solid {DANGER if due_amount > 0 else SUCCESS};
                    border-radius: 6px;
                    padding: 6px 10px;
                    background: rgba({("220, 38, 38" if due_amount > 0 else "34, 197, 94")}, 0.1);
                }}
            """)
        elif party_data:
            balance = party_data.get('opening_balance', 0)
            if balance != 0:
                self.outstanding_label.setText(f"💰 Balance: ₹{balance:,.2f}")
                self.outstanding_label.setStyleSheet(f"""
                    QLabel {{
                        color: {SUCCESS if balance > 0 else DANGER};
                        font-weight: bold;
                        font-size: 13px;
                        border: 1px solid {SUCCESS if balance > 0 else DANGER};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background: rgba({("34, 197, 94" if balance > 0 else "220, 38, 38")}, 0.1);
                    }}
                """)
            else:
                self.outstanding_label.setText("💡 No outstanding amount")
                self.outstanding_label.setStyleSheet(f"""
                    QLabel {{
                        color: {TEXT_SECONDARY};
                        font-weight: normal;
                        font-size: 13px;
                        border: 1px solid {BORDER};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background: {BACKGROUND};
                    }}
                """)
        else:
            self.outstanding_label.setText("💡 Select party to see balance")
            self.outstanding_label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-weight: normal;
                    font-size: 13px;
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    padding: 6px 10px;
                    background: {BACKGROUND};
                }}
            """)
    
    def validate_amount(self):
        """Validate payment amount with visual feedback"""
        amount = self.amount_input.value()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            if amount > due_amount:
                # Show warning for overpayment
                self.amount_input.setStyleSheet(f"""
                    QDoubleSpinBox {{
                        border: 2px solid {WARNING};
                        border-radius: 8px;
                        padding: 10px 12px;
                        background: rgba(245, 158, 11, 0.1);
                        font-size: 14px;
                        color: {TEXT_PRIMARY};
                    }}
                """)
            else:
                # Reset to normal style
                self.amount_input.setStyleSheet(f"""
                    QDoubleSpinBox {{
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        padding: 10px 12px;
                        background: {WHITE};
                        font-size: 14px;
                        color: {TEXT_PRIMARY};
                    }}
                """)
        
        self.update_summary()
    
    def update_summary(self):
        """Update payment summary with detailed information"""
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        amount = self.amount_input.value()
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        
        if not party_data:
            self.summary_content.setText("Select party and invoice to see payment summary")
            return
        
        summary_text = f"""
<b>📊 Payment Summary</b><br><br>
<b>Type:</b> {payment_type}<br>
<b>Party:</b> {party_data.get('name', 'N/A')}<br>
<b>Amount:</b> ₹{amount:,.2f}<br>
"""
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            remaining = due_amount - amount
            
            summary_text += f"""
<b>Invoice:</b> {invoice_data.get('invoice_no', 'N/A')}<br>
<b>Due Amount:</b> ₹{due_amount:,.2f}<br>
<b>Payment Amount:</b> ₹{amount:,.2f}<br>
<b>Remaining:</b> ₹{remaining:,.2f}<br>
"""
            
            if remaining < 0:
                summary_text += f"<br><span style='color: {WARNING};'><b>⚠️ Overpayment by ₹{abs(remaining):,.2f}</b></span>"
            elif remaining == 0:
                summary_text += f"<br><span style='color: {SUCCESS};'><b>✅ Invoice will be fully paid</b></span>"
        else:
            summary_text += "<br><b>Invoice:</b> Direct Payment (No Invoice)<br>"
        
        # Add balance impact
        current_balance = party_data.get('opening_balance', 0)
        if payment_type == "Payment Received":
            new_balance = current_balance - amount
        else:
            new_balance = current_balance + amount
        
        summary_text += f"""
<br><b>💰 Balance Impact:</b><br>
Current Balance: ₹{current_balance:,.2f}<br>
New Balance: ₹{new_balance:,.2f}
"""
        
        self.summary_content.setText(summary_text)
    
    def show_help(self):
        """Show payment help dialog"""
        help_text = """
        <h3>💳 Payment Recording Help</h3>
        
        <h4>📋 Payment Types:</h4>
        <p><b>Payment Received:</b> Money coming into your business from customers</p>
        <p><b>Payment Made:</b> Money going out of your business to suppliers</p>
        
        <h4>🏢 Party Selection:</h4>
        <p>Choose the customer or supplier for this payment</p>
        
        <h4>📄 Invoice Linking:</h4>
        <p><b>With Invoice:</b> Links payment to specific invoice for automatic reconciliation</p>
        <p><b>Direct Payment:</b> General payment not linked to any specific invoice</p>
        
        <h4>💰 Amount Guidelines:</h4>
        <p>• Enter the exact amount received or paid</p>
        <p>• System warns about overpayments</p>
        <p>• Partial payments are allowed</p>
        
        <h4>💡 Best Practices:</h4>
        <ul>
        <li>Always enter reference numbers for bank transactions</li>
        <li>Add notes for cash payments</li>
        <li>Link payments to invoices when possible</li>
        <li>Double-check amount before saving</li>
        </ul>
        """
        QMessageBox.information(self, "Payment Help", help_text)
    
    def populate_form(self):
        """Populate form with existing payment data"""
        if not self.payment_data:
            return
        
        # Set payment type
        payment_type = self.payment_data.get('type', 'Payment Received')
        if payment_type == 'Payment Received':
            self.received_radio.setChecked(True)
        else:
            self.made_radio.setChecked(True)
        
        # Update combos based on type
        self.on_payment_type_changed()
        
        # Set party
        party_id = self.payment_data.get('party_id')
        if party_id:
            for i in range(self.party_combo.count()):
                party_data = self.party_combo.itemData(i)
                if party_data and party_data.get('id') == party_id:
                    self.party_combo.setCurrentIndex(i)
                    break
        
        # Set invoice if applicable
        invoice_id = self.payment_data.get('invoice_id')
        if invoice_id:
            for i in range(self.invoice_combo.count()):
                invoice_data = self.invoice_combo.itemData(i)
                if invoice_data and invoice_data.get('id') == invoice_id:
                    self.invoice_combo.setCurrentIndex(i)
                    break
        
        # Set other fields
        self.amount_input.setValue(self.payment_data.get('amount', 0))
        
        payment_date = self.payment_data.get('date', '')
        if payment_date:
            date_obj = QDate.fromString(payment_date, 'yyyy-MM-dd')
            self.payment_date.setDate(date_obj)
        
        # Set payment method
        method = self.payment_data.get('method', 'Cash')
        for i in range(self.payment_method.count()):
            if self.payment_method.itemData(i) == method:
                self.payment_method.setCurrentIndex(i)
                break
        
        self.reference_input.setText(self.payment_data.get('reference', ''))
        self.notes_input.setPlainText(self.payment_data.get('notes', ''))
    
    def on_invoice_changed(self):
        """Handle invoice selection change"""
        self.update_outstanding_display()
        
        # Auto-fill amount with invoice total
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            self.amount_input.setValue(invoice_data['grand_total'])
    
    def update_outstanding_display(self):
        """Update outstanding amount display"""
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            # Show invoice outstanding
            outstanding = invoice_data['grand_total']
            self.outstanding_label.setText(f"Outstanding: ₹{outstanding:,.2f}")
        elif party_data:
            # Show party balance
            balance = party_data.get('opening_balance', 0)
            if balance > 0:
                self.outstanding_label.setText(f"Receivable: ₹{balance:,.2f}")
            elif balance < 0:
                self.outstanding_label.setText(f"Payable: ₹{abs(balance):,.2f}")
            else:
                self.outstanding_label.setText("No outstanding amount")
        else:
            self.outstanding_label.setText("")
    
    def populate_form(self):
        """Populate form with existing payment data"""
        data = self.payment_data
        
        # Payment type
        type_index = self.payment_type.findText(data.get('type', 'Payment Received'))
        if type_index >= 0:
            self.payment_type.setCurrentIndex(type_index)
        
        # Find and select party
        for i in range(self.party_combo.count()):
            party_data = self.party_combo.itemData(i)
            if party_data and party_data['id'] == data.get('party_id'):
                self.party_combo.setCurrentIndex(i)
                break
        
        # Amount and other fields
        self.amount_input.setValue(data.get('amount', 0))
        
        # Payment date
        from PyQt5.QtCore import QDate
        date_str = data.get('date', QDate.currentDate().toString('yyyy-MM-dd'))
        payment_date = QDate.fromString(date_str, 'yyyy-MM-dd')
        self.payment_date.setDate(payment_date)
        
        # Payment method
        method_index = self.payment_method.findText(data.get('method', 'Cash'))
        if method_index >= 0:
            self.payment_method.setCurrentIndex(method_index)
        
        self.reference_input.setText(data.get('reference', ''))
        self.notes_input.setPlainText(data.get('notes', ''))
    
    def save_payment(self):
        """Save payment data with enhanced validation and feedback"""
        # Comprehensive validation
        party_data = self.party_combo.currentData()
        if not party_data:
            QMessageBox.warning(self, "Validation Error", "🏢 Please select a party!")
            self.party_combo.setFocus()
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "💰 Please enter a valid amount!")
            self.amount_input.setFocus()
            return
        
        # Validate reference for non-cash payments
        payment_method = self.payment_method.currentData()
        reference = self.reference_input.text().strip()
        if payment_method != "Cash" and not reference:
            reply = QMessageBox.question(
                self, "Missing Reference", 
                f"💳 No reference number entered for {payment_method} payment.\n\nDo you want to continue without reference?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.reference_input.setFocus()
                return
        
        # Check for overpayment warning
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            if amount > due_amount:
                overpay = amount - due_amount
                reply = QMessageBox.question(
                    self, "Overpayment Warning",
                    f"⚠️ Payment amount (₹{amount:,.2f}) exceeds due amount (₹{due_amount:,.2f}).\n\n"
                    f"Overpayment: ₹{overpay:,.2f}\n\nDo you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
        
        # Prepare payment data
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        
        payment_data = {
            'type': payment_type,
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'amount': amount,
            'date': self.payment_date.date().toString('yyyy-MM-dd'),
            'method': payment_method,
            'reference': reference,
            'notes': self.notes_input.toPlainText().strip(),
            'status': 'Completed'
        }
        
        # Add invoice reference if selected
        if invoice_data:
            payment_data['invoice_id'] = invoice_data['id']
            invoice_no = invoice_data.get('invoice_no', f"INV-{invoice_data['id']:03d}")
            payment_data['invoice_no'] = invoice_no
        
        # Save with progress indication
        try:
            # Disable save button to prevent double-clicking
            self.save_btn.setEnabled(False)
            self.save_btn.setText("💾 Saving...")
            
            if self.payment_data:  # Editing
                payment_data['id'] = self.payment_data['id']
                db.update_payment(payment_data)
                success_msg = "✅ Payment updated successfully!"
            else:  # Recording new
                db.add_payment(payment_data)
                success_msg = "✅ Payment recorded successfully!"
            
            # Show success with summary
            summary = f"""
{success_msg}

Payment Details:
• Type: {payment_type}
• Party: {party_data['name']}
• Amount: ₹{amount:,.2f}
• Method: {payment_method}
• Date: {self.payment_date.date().toString('dd-MM-yyyy')}
            """
            
            if invoice_data:
                summary += f"\n• Invoice: {payment_data.get('invoice_no', 'N/A')}"
            
            QMessageBox.information(self, "Success", summary.strip())
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save payment:\n\n{str(e)}")
        finally:
            # Re-enable save button
            self.save_btn.setEnabled(True)
            save_text = "💾 Update Payment" if self.payment_data else "💾 Record Payment"
            self.save_btn.setText(save_text)

class PaymentsScreen(BaseScreen):
    """Enhanced Payments screen with modern UI and advanced functionality"""
    
    def __init__(self):
        super().__init__("💳 Payments & Transactions")
        self.all_payments_data = []
        self.setup_payments_screen()
        self.load_payments_data()
    
    def setup_payments_screen(self):
        """Setup enhanced payments screen content"""
        # Enhanced top action bar with modern design
        self.setup_action_bar()
        
        # Enhanced filters and statistics
        self.setup_filters_and_stats()
        
        # Modern payments table with advanced features
        self.setup_payments_table()
    
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
        self.search_input.setPlaceholderText("Search payments by party, amount, reference, or method...")
        self.search_input.setAlignment(Qt.AlignLeft)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.search_input.textChanged.connect(self.filter_payments)
        search_layout.addWidget(self.search_input)
        
        action_layout.addWidget(search_container)
        action_layout.addStretch()
        
        # Enhanced action buttons with icons
        buttons_data = [
            ("📊 Export", "secondary", self.export_payments),
            ("📋 Reports", "warning", self.show_reports),
            ("💳 Record Payment", "primary", self.record_payment)
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
                        border-color: {PRIMARY};
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
            
            action_layout.addWidget(btn)
        
        self.add_content(action_frame)
    
    def setup_filters_and_stats(self):
        """Setup filters and quick stats"""
        container = QHBoxLayout()
        
        # Filters section
        filters_layout = QHBoxLayout()
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Payment Received", "Payment Made"])
        self.type_filter.setFixedWidth(150)
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                background: {WHITE};
            }}
        """)
        self.type_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.type_filter)
        
        filters_layout.addSpacing(20)
        
        # Method filter
        filters_layout.addWidget(QLabel("Method:"))
        self.method_filter = QComboBox()
        self.method_filter.addItems([
            "All", "Cash", "Bank Transfer", "Cheque", "UPI", 
            "Credit Card", "Debit Card", "Net Banking", "Other"
        ])
        self.method_filter.setFixedWidth(120)
        self.method_filter.setStyleSheet(self.type_filter.styleSheet())
        self.method_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.method_filter)
        
        filters_layout.addSpacing(20)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Pending", "Failed"])
        self.status_filter.setFixedWidth(100)
        self.status_filter.setStyleSheet(self.type_filter.styleSheet())
        self.status_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.status_filter)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.addStretch()
        
        # Total payments
        self.total_payments_label = QLabel("Total: 0")
        self.total_payments_label.setStyleSheet(f"""
            background: {PRIMARY}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.total_payments_label)
        
        # Received amount
        self.received_amount_label = QLabel("Received: ₹0")
        self.received_amount_label.setStyleSheet(f"""
            background: {SUCCESS}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.received_amount_label)
        
        # Paid amount
        self.paid_amount_label = QLabel("Paid: ₹0")
        self.paid_amount_label.setStyleSheet(f"""
            background: {DANGER}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.paid_amount_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 15px;
                background: {WHITE};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
            }}
        """)
        refresh_btn.clicked.connect(self.load_payments_data)
        stats_layout.addWidget(refresh_btn)
        
        container.addLayout(filters_layout)
        container.addLayout(stats_layout)
        
        container_widget = QWidget()
        container_widget.setLayout(container)
        self.add_content(container_widget)
    
    def setup_payments_table(self):
        """Setup payments data table"""
        # Table container
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        # Table
        headers = ["Date", "Type", "Party", "Amount", "Method", "Reference", "Status", "Actions"]
        self.payments_table = CustomTable(0, len(headers), headers)
        
        # Set column widths
        self.payments_table.setColumnWidth(0, 100)  # Date
        self.payments_table.setColumnWidth(1, 120)  # Type
        self.payments_table.setColumnWidth(2, 180)  # Party
        self.payments_table.setColumnWidth(3, 120)  # Amount
        self.payments_table.setColumnWidth(4, 100)  # Method
        self.payments_table.setColumnWidth(5, 120)  # Reference
        self.payments_table.setColumnWidth(6, 100)  # Status
        self.payments_table.setColumnWidth(7, 120)  # Actions
        
        table_layout.addWidget(self.payments_table)
        self.add_content(table_frame)
        
        # Store original data for filtering
        self.all_payments_data = []
    
    def load_payments_data(self):
        """Load payments data into table"""
        try:
            payments = db.get_payments()
            self.all_payments_data = payments
            self.populate_table(payments)
            self.update_stats(payments)
        except Exception as e:
            # Show sample data if database not available
            sample_data = [
                {
                    'id': 1, 'type': 'Payment Received', 'party_name': 'ABC Corp', 
                    'amount': 25000, 'date': '2024-01-01', 'method': 'Bank Transfer',
                    'reference': 'TXN123456', 'status': 'Completed'
                },
                {
                    'id': 2, 'type': 'Payment Made', 'party_name': 'XYZ Supplier',
                    'amount': 15000, 'date': '2024-01-02', 'method': 'UPI',
                    'reference': 'UPI789012', 'status': 'Completed'
                }
            ]
            self.all_payments_data = sample_data
            self.populate_table(sample_data)
            self.update_stats(sample_data)
    
    def populate_table(self, payments_data):
        """Populate table with payments data"""
        self.payments_table.setRowCount(len(payments_data))
        
        for row, payment in enumerate(payments_data):
            self.payments_table.setItem(row, 0, self.payments_table.create_item(payment['date']))
            
            # Type with color coding
            payment_type = payment['type']
            type_item = self.payments_table.create_item(payment_type)
            if payment_type == "Payment Received":
                type_item.setBackground(type_item.background().color().lighter(150))
            else:
                type_item.setBackground(type_item.background().color().darker(110))
            self.payments_table.setItem(row, 1, type_item)
            
            self.payments_table.setItem(row, 2, self.payments_table.create_item(payment.get('party_name', 'N/A')))
            
            # Amount with color coding
            amount = payment['amount']
            amount_text = f"₹{amount:,.2f}"
            amount_item = self.payments_table.create_item(amount_text)
            if payment_type == "Payment Received":
                amount_item.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            else:
                amount_item.setStyleSheet(f"color: {DANGER}; font-weight: bold;")
            self.payments_table.setItem(row, 3, amount_item)
            
            self.payments_table.setItem(row, 4, self.payments_table.create_item(payment.get('method', '')))
            self.payments_table.setItem(row, 5, self.payments_table.create_item(payment.get('reference', '')))
            
            # Status
            status = payment.get('status', 'Completed')
            status_item = self.payments_table.create_item(status)
            if status == "Completed":
                status_item.setBackground(status_item.background().color().lighter(150))
            elif status == "Failed":
                status_item.setBackground(status_item.background().color().darker(120))
            self.payments_table.setItem(row, 6, status_item)
            
            # Action buttons
            actions_widget = self.create_action_buttons(payment)
            self.payments_table.setCellWidget(row, 7, actions_widget)
    
    def create_action_buttons(self, payment):
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
                border: 1px solid {PRIMARY};
                border-radius: 12px;
                background: {WHITE};
                color: {PRIMARY};
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_payment(payment))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setStyleSheet(view_btn.styleSheet())
        edit_btn.clicked.connect(lambda: self.edit_payment(payment))
        layout.addWidget(edit_btn)
        
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
        delete_btn.clicked.connect(lambda: self.delete_payment(payment))
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_stats(self, payments):
        """Update quick stats labels"""
        total_count = len(payments)
        received_amount = sum(p['amount'] for p in payments if p['type'] == 'Payment Received')
        paid_amount = sum(p['amount'] for p in payments if p['type'] == 'Payment Made')
        
        self.total_payments_label.setText(f"Total: {total_count}")
        self.received_amount_label.setText(f"Received: ₹{received_amount:,.0f}")
        self.paid_amount_label.setText(f"Paid: ₹{paid_amount:,.0f}")
    
    def filter_payments(self):
        """Filter payments based on search and filters"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        method_filter = self.method_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_data = []
        for payment in self.all_payments_data:
            # Search filter
            if search_text:
                searchable_text = f"{payment.get('party_name', '')} {payment.get('reference', '')}".lower()
                if search_text not in searchable_text:
                    continue
            
            # Type filter
            if type_filter != "All" and payment['type'] != type_filter:
                continue
            
            # Method filter
            if method_filter != "All" and payment.get('method', '') != method_filter:
                continue
            
            # Status filter
            if status_filter != "All" and payment.get('status', 'Completed') != status_filter:
                continue
            
            filtered_data.append(payment)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
    
    def record_payment(self):
        """Open record payment dialog"""
        dialog = PaymentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def edit_payment(self, payment):
        """Open edit payment dialog"""
        dialog = PaymentDialog(self, payment)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def view_payment(self, payment):
        """View payment details"""
        details = f"""
Payment Details:

Type: {payment['type']}
Party: {payment.get('party_name', 'N/A')}
Amount: ₹{payment['amount']:,.2f}
Date: {payment['date']}
Method: {payment.get('method', 'N/A')}
Reference: {payment.get('reference', 'N/A')}
Status: {payment.get('status', 'N/A')}
Notes: {payment.get('notes', 'N/A')}
        """
        QMessageBox.information(self, "Payment Details", details.strip())
    
    def delete_payment(self, payment):
        """Delete payment with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this payment of ₹{payment['amount']:,.2f}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_payment(payment['id'])
                QMessageBox.information(self, "Success", "Payment deleted successfully!")
                self.load_payments_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete payment: {str(e)}")
    
    def export_payments(self):
        """Export payments data"""
        QMessageBox.information(self, "Export", "📊 Export functionality will be implemented soon!")
    
    def show_reports(self):
        """Show payment reports"""
        QMessageBox.information(self, "Reports", "📋 Payment reports functionality will be implemented soon!")
    
    def refresh_data(self):
        """Refresh payments data"""
        self.load_payments_data()
    
    def setup_filters_and_stats(self):
        """Setup enhanced filters and payment statistics"""
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
        
        # Statistics cards row
        stats_container = QHBoxLayout()
        
        # Enhanced statistics cards
        stats_data = [
            ("💰", "Total Received", "₹0", SUCCESS, "total_received_label"),
            ("💸", "Total Made", "₹0", DANGER, "total_made_label"),
            ("📋", "Total Payments", "0", PRIMARY, "total_payments_label"),
            ("💳", "This Month", "₹0", WARNING, "month_total_label")
        ]
        
        for icon, label_text, value, color, attr_name in stats_data:
            card = self.create_stat_card(icon, label_text, value, color)
            setattr(self, attr_name, card.findChild(QLabel, "value_label"))
            stats_container.addWidget(card)
        
        main_layout.addLayout(stats_container)
        
        # Add filters section
        filters_section = self.create_filters_section()
        main_layout.addWidget(filters_section)
        
        self.add_content(container_frame)
    
    def create_filters_section(self):
        """Create comprehensive filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setContentsMargins(15, 15, 15, 15)
        filters_layout.setSpacing(15)
        
        # Filters header
        filters_header = QLabel("🎯 Smart Filters")
        filters_header.setFont(QFont("Arial", 14, QFont.Bold))
        filters_header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        filters_layout.addWidget(filters_header)
        
        # Create two rows of filters for better organization
        filters_row1 = QHBoxLayout()
        filters_row1.setSpacing(20)
        
        filters_row2 = QHBoxLayout()
        filters_row2.setSpacing(20)
        
        # Enhanced filter controls with modern styling
        filter_style = f"""
            QComboBox {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 13px;
                color: {TEXT_PRIMARY};
                font-weight: 500;
                min-width: 140px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY};
                background: #F8FAFC;
            }}
            QComboBox:focus {{
                border-color: {PRIMARY};
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
        """
        
        label_style = f"""
            QLabel {{
                color: {TEXT_PRIMARY}; 
                font-weight: 600; 
                border: none;
                font-size: 13px;
                min-width: 100px;
            }}
        """
        
        # Row 1 Filters
        # Payment Type Filter
        type_container = QVBoxLayout()
        type_label = QLabel("💳 Payment Type:")
        type_label.setStyleSheet(label_style)
        type_container.addWidget(type_label)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Payment Received", "Payment Made"])
        self.type_filter.setStyleSheet(filter_style)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        type_container.addWidget(self.type_filter)
        filters_row1.addLayout(type_container)
        
        # Payment Method Filter
        method_container = QVBoxLayout()
        method_label = QLabel("💰 Payment Method:")
        method_label.setStyleSheet(label_style)
        method_container.addWidget(method_label)
        
        self.method_filter = QComboBox()
        method_items = [
            "All Methods", "Cash", "Bank Transfer", "UPI", "Cheque", 
            "Credit Card", "Debit Card", "Net Banking", "Other"
        ]
        self.method_filter.addItems(method_items)
        self.method_filter.setStyleSheet(filter_style)
        self.method_filter.currentTextChanged.connect(self.apply_filters)
        method_container.addWidget(self.method_filter)
        filters_row1.addLayout(method_container)
        
        # Date Range Filter
        date_container = QVBoxLayout()
        date_label = QLabel("📅 Date Range:")
        date_label.setStyleSheet(label_style)
        date_container.addWidget(date_label)
        
        self.date_filter = QComboBox()
        date_items = [
            "All Time", "Today", "Yesterday", "This Week", "Last Week",
            "This Month", "Last Month", "This Quarter", "This Year", "Custom Range"
        ]
        self.date_filter.addItems(date_items)
        self.date_filter.setStyleSheet(filter_style)
        self.date_filter.currentTextChanged.connect(self.apply_filters)
        date_container.addWidget(self.date_filter)
        filters_row1.addLayout(date_container)
        
        # Status Filter
        status_container = QVBoxLayout()
        status_label = QLabel("📊 Status:")
        status_label.setStyleSheet(label_style)
        status_container.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Completed", "Pending", "Failed", "Cancelled"])
        self.status_filter.setStyleSheet(filter_style)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        status_container.addWidget(self.status_filter)
        filters_row1.addLayout(status_container)
        
        filters_row1.addStretch()
        
        # Row 2 Filters - Removed amount range, party, and reference filters
        # Only keep Action Buttons
        # Action Buttons
        actions_container = QVBoxLayout()
        actions_label = QLabel("⚡ Actions:")
        actions_label.setStyleSheet(label_style)
        actions_container.addWidget(actions_label)
        
        actions_buttons = QHBoxLayout()
        actions_buttons.setSpacing(8)
        
        # Clear filters button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setFixedSize(80, 35)
        clear_btn.setToolTip("Clear all filters")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                background: {WHITE};
                font-size: 12px;
                color: {TEXT_PRIMARY};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {DANGER};
                color: white;
                border-color: {DANGER};
            }}
        """)
        clear_btn.clicked.connect(self.clear_filters)
        actions_buttons.addWidget(clear_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedSize(80, 35)
        refresh_btn.setToolTip("Refresh payment data")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                background: {WHITE};
                font-size: 12px;
                color: {TEXT_PRIMARY};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: white;
                border-color: {PRIMARY};
            }}
        """)
        refresh_btn.clicked.connect(self.load_payments_data)
        actions_buttons.addWidget(refresh_btn)
        
        actions_container.addLayout(actions_buttons)
        filters_row2.addLayout(actions_container)
        
        filters_row2.addStretch()
        
        # Add both rows to the main layout
        filters_layout.addLayout(filters_row1)
        filters_layout.addLayout(filters_row2)
        
        # Add filter status indicator
        self.filter_status_label = QLabel("📊 Showing all payments")
        self.filter_status_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-style: italic;
                border: none;
                padding: 5px;
                background: transparent;
            }}
        """)
        filters_layout.addWidget(self.filter_status_label)
        
        return filters_frame
    
    def create_stat_card(self, icon, label_text, value, color):
        """Create statistics card"""
        card = QFrame()
        card.setFixedSize(200, 80)
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
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(28, 28)
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
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(2)
        
        # Label
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(f"color: #6B7280; font-size: 11px; border: none; font-weight: 500;")
        text_container.addWidget(label_widget)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        text_container.addWidget(value_label)
        
        layout.addLayout(text_container)
        layout.addStretch()
        
        return card
    
    def setup_payments_table(self):
        """Setup enhanced payments table"""
        # Main container
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Table header
        header = QLabel("📋 Payment Transactions")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                border: none;
                padding: 10px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 8px;
            }}
        """)
        layout.addWidget(header)
        
        # Enhanced table
        headers = ["Date", "Type", "Party", "Amount", "Method", "Reference", "Status", "Actions"]
        self.payments_table = CustomTable(0, len(headers), headers)
        
        # Enhanced table styling
        self.payments_table.setStyleSheet(f"""
            QTableWidget {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                gridline-color: {BORDER};
                font-size: 13px;
                selection-background-color: rgba(59, 130, 246, 0.2);
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {BORDER};
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item:hover {{
                background: #F8FAFC;
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
        """)
        
        # Set column widths
        self.payments_table.setColumnWidth(0, 100)  # Date
        self.payments_table.setColumnWidth(1, 120)  # Type
        self.payments_table.setColumnWidth(2, 180)  # Party
        self.payments_table.setColumnWidth(3, 120)  # Amount
        self.payments_table.setColumnWidth(4, 100)  # Method
        self.payments_table.setColumnWidth(5, 120)  # Reference
        self.payments_table.setColumnWidth(6, 100)  # Status
        self.payments_table.setColumnWidth(7, 120)  # Actions
        
        layout.addWidget(self.payments_table)
        self.add_content(container_frame)
        
        # Store original data for filtering
        self.all_payments_data = []
    
    def load_payments_data(self):
        """Load payments data into table"""
        try:
            payments = db.get_payments()
            self.all_payments_data = payments or []
            self.populate_table(payments or [])
            self.update_stats(payments or [])
        except Exception as e:
            print(f"Database error: {e}")
            # Show sample data if database not available
            sample_data = [
                {
                    'id': 1, 'type': 'Payment Received', 'party_name': 'ABC Corporation', 
                    'amount': 25000, 'date': '2024-01-15', 'method': 'Bank Transfer',
                    'reference': 'TXN123456', 'status': 'Completed', 'notes': 'Invoice payment'
                },
                {
                    'id': 2, 'type': 'Payment Made', 'party_name': 'XYZ Supplier',
                    'amount': 15000, 'date': '2024-01-16', 'method': 'UPI',
                    'reference': 'UPI789012', 'status': 'Completed', 'notes': 'Office supplies'
                },
                {
                    'id': 3, 'type': 'Payment Received', 'party_name': 'Tech Solutions Pvt Ltd',
                    'amount': 50000, 'date': '2024-01-17', 'method': 'Cheque',
                    'reference': 'CHQ456789', 'status': 'Completed', 'notes': 'Service payment'
                },
                {
                    'id': 4, 'type': 'Payment Made', 'party_name': 'Global Industries Inc',
                    'amount': 8500, 'date': '2024-01-18', 'method': 'Cash',
                    'reference': '', 'status': 'Completed', 'notes': 'Petty cash'
                },
                {
                    'id': 5, 'type': 'Payment Received', 'party_name': 'Digital Marketing Co',
                    'amount': 75000, 'date': '2024-01-19', 'method': 'Net Banking',
                    'reference': 'NBK987654', 'status': 'Completed', 'notes': 'Project payment'
                }
            ]
            self.all_payments_data = sample_data
            self.populate_table(sample_data)
            self.update_stats(sample_data)
    
    def apply_filters(self):
        """Apply all selected filters to the payments data"""
        if not hasattr(self, 'all_payments_data'):
            return
        
        filtered_data = []
        
        # Get filter values
        type_filter = self.type_filter.currentText()
        method_filter = self.method_filter.currentText()
        date_filter = self.date_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for payment in self.all_payments_data:
            # Apply type filter
            if type_filter != "All Types" and payment.get('type', '') != type_filter:
                continue
            
            # Apply method filter
            if method_filter != "All Methods" and payment.get('method', '') != method_filter:
                continue
            
            # Apply status filter
            if status_filter != "All Status" and payment.get('status', 'Completed') != status_filter:
                continue
            
            # Apply date filter
            if not self.check_date_filter(payment.get('date', ''), date_filter):
                continue
            
            filtered_data.append(payment)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
        
        # Update filter status indicator
        self.update_filter_status(len(filtered_data), len(self.all_payments_data))
    
    def check_date_filter(self, payment_date, date_filter):
        """Check if payment date matches the selected date filter"""
        if date_filter == "All Time":
            return True
        
        try:
            from datetime import datetime, timedelta
            
            # Parse payment date
            payment_dt = datetime.strptime(payment_date, '%Y-%m-%d')
            today = datetime.now()
            
            if date_filter == "Today":
                return payment_dt.date() == today.date()
            elif date_filter == "Yesterday":
                yesterday = today - timedelta(days=1)
                return payment_dt.date() == yesterday.date()
            elif date_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return payment_dt >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_filter == "Last Week":
                week_start = today - timedelta(days=today.weekday() + 7)
                week_end = week_start + timedelta(days=6)
                return week_start.date() <= payment_dt.date() <= week_end.date()
            elif date_filter == "This Month":
                return (payment_dt.year == today.year and 
                       payment_dt.month == today.month)
            elif date_filter == "Last Month":
                if today.month == 1:
                    last_month = 12
                    last_year = today.year - 1
                else:
                    last_month = today.month - 1
                    last_year = today.year
                return (payment_dt.year == last_year and 
                       payment_dt.month == last_month)
            elif date_filter == "This Quarter":
                quarter = (today.month - 1) // 3 + 1
                quarter_start_month = (quarter - 1) * 3 + 1
                quarter_end_month = quarter * 3
                return (payment_dt.year == today.year and 
                       quarter_start_month <= payment_dt.month <= quarter_end_month)
            elif date_filter == "This Year":
                return payment_dt.year == today.year
            
        except ValueError:
            # Invalid date format
            return True
        
        return True
    
    def update_filter_status(self, filtered_count, total_count):
        """Update the UI to show current filter status"""
        if not hasattr(self, 'filter_status_label'):
            return
        
        if filtered_count == total_count:
            self.filter_status_label.setText("📊 Showing all payments")
            self.filter_status_label.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: 12px;
                    font-style: italic;
                    border: none;
                    padding: 5px;
                    background: transparent;
                }}
            """)
        else:
            self.filter_status_label.setText(f"🎯 Showing {filtered_count} of {total_count} payments (filtered)")
            self.filter_status_label.setStyleSheet(f"""
                QLabel {{
                    color: {WARNING};
                    font-size: 12px;
                    font-weight: bold;
                    border: 1px solid {WARNING};
                    border-radius: 6px;
                    padding: 5px 10px;
                    background: rgba(245, 158, 11, 0.1);
                }}
            """)
    
    def clear_filters(self):
        """Clear all applied filters"""
        if hasattr(self, 'type_filter'):
            self.type_filter.setCurrentIndex(0)
        if hasattr(self, 'method_filter'):
            self.method_filter.setCurrentIndex(0)
        if hasattr(self, 'date_filter'):
            self.date_filter.setCurrentIndex(0)
        if hasattr(self, 'status_filter'):
            self.status_filter.setCurrentIndex(0)
        
        # Reset to show all data
        self.populate_table(self.all_payments_data)
        self.update_stats(self.all_payments_data)
    
    def populate_table(self, payments_data):
        """Populate table with payments data"""
        self.payments_table.setRowCount(len(payments_data))
        
        for row, payment in enumerate(payments_data):
            # Date
            self.payments_table.setItem(row, 0, self.payments_table.create_item(payment['date']))
            
            # Type with color coding
            payment_type = payment['type']
            type_item = self.payments_table.create_item(payment_type)
            if payment_type == "Payment Received":
                type_item.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            else:
                type_item.setStyleSheet(f"color: {DANGER}; font-weight: bold;")
            self.payments_table.setItem(row, 1, type_item)
            
            # Party
            self.payments_table.setItem(row, 2, self.payments_table.create_item(payment.get('party_name', 'N/A')))
            
            # Amount with color coding
            amount = payment['amount']
            amount_text = f"₹{amount:,.2f}"
            amount_item = self.payments_table.create_item(amount_text)
            if payment_type == "Payment Received":
                amount_item.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            else:
                amount_item.setStyleSheet(f"color: {DANGER}; font-weight: bold;")
            self.payments_table.setItem(row, 3, amount_item)
            
            # Method
            self.payments_table.setItem(row, 4, self.payments_table.create_item(payment.get('method', 'N/A')))
            
            # Reference
            self.payments_table.setItem(row, 5, self.payments_table.create_item(payment.get('reference', 'N/A')))
            
            # Status
            status = payment.get('status', 'Completed')
            status_item = self.payments_table.create_item(status)
            if status == 'Completed':
                status_item.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            self.payments_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            # View button
            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(25, 25)
            view_btn.setToolTip("View payment details")
            view_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {PRIMARY_HOVER};
                }}
            """)
            view_btn.clicked.connect(lambda checked, p=payment: self.view_payment(p))
            actions_layout.addWidget(view_btn)
            
            # Edit button
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(25, 25)
            edit_btn.setToolTip("Edit payment")
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {WARNING};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #F59E0B;
                }}
            """)
            edit_btn.clicked.connect(lambda checked, p=payment: self.edit_payment(p))
            actions_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(25, 25)
            delete_btn.setToolTip("Delete payment")
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {DANGER};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #DC2626;
                }}
            """)
            delete_btn.clicked.connect(lambda checked, p=payment: self.delete_payment(p))
            actions_layout.addWidget(delete_btn)
            
            self.payments_table.setCellWidget(row, 7, actions_widget)
    
    def update_stats(self, payments_data):
        """Update statistics display"""
        if not hasattr(self, 'total_received_label'):
            return
        
        total_received = sum(p['amount'] for p in payments_data if p['type'] == 'Payment Received')
        total_made = sum(p['amount'] for p in payments_data if p['type'] == 'Payment Made')
        total_payments = len(payments_data)
        
        # Calculate this month's total
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        month_total = sum(p['amount'] for p in payments_data 
                         if p['date'].startswith(current_month))
        
        self.total_received_label.setText(f"₹{total_received:,.0f}")
        self.total_made_label.setText(f"₹{total_made:,.0f}")
        self.total_payments_label.setText(str(total_payments))
        self.month_total_label.setText(f"₹{month_total:,.0f}")
    
    def filter_payments(self):
        """Filter payments based on search text combined with other filters"""
        search_text = self.search_input.text().lower().strip()
        
        # Start with all data
        filtered_data = self.all_payments_data.copy()
        
        # Apply search filter if there's search text
        if search_text:
            search_filtered = []
            for payment in filtered_data:
                # Search in multiple fields
                searchable_text = f"""
                    {payment.get('party_name', '')} 
                    {payment.get('type', '')} 
                    {payment.get('method', '')} 
                    {payment.get('reference', '')} 
                    {payment.get('amount', '')}
                    {payment.get('status', '')}
                    {payment.get('notes', '')}
                """.lower()
                
                if search_text in searchable_text:
                    search_filtered.append(payment)
            
            filtered_data = search_filtered
        
        # Apply combo box filters if they exist
        if hasattr(self, 'type_filter'):
            # Get filter values
            type_filter = self.type_filter.currentText()
            method_filter = self.method_filter.currentText()
            date_filter = self.date_filter.currentText()
            status_filter = self.status_filter.currentText()
            amount_filter = self.amount_filter.currentText()
            party_filter = self.party_filter.currentText()
            reference_filter = self.reference_filter.currentText()
            
            # Apply additional filters
            additional_filtered = []
            for payment in filtered_data:
                # Apply type filter
                if type_filter != "All Types" and payment.get('type', '') != type_filter:
                    continue
                
                # Apply method filter
                if method_filter != "All Methods" and payment.get('method', '') != method_filter:
                    continue
                
                # Apply status filter
                if status_filter != "All Status" and payment.get('status', 'Completed') != status_filter:
                    continue
                
                # Apply party filter
                if party_filter != "All Parties":
                    party_name = party_filter.replace("🏢 ", "")
                    if payment.get('party_name', '') != party_name:
                        continue
                
                # Apply reference filter
                reference = payment.get('reference', '').strip()
                if reference_filter == "With Reference" and not reference:
                    continue
                elif reference_filter == "Without Reference" and reference:
                    continue
                
                # Apply amount filter
                amount = payment.get('amount', 0)
                if amount_filter == "Under ₹1,000" and amount >= 1000:
                    continue
                elif amount_filter == "₹1,000 - ₹10,000" and (amount < 1000 or amount > 10000):
                    continue
                elif amount_filter == "₹10,000 - ₹50,000" and (amount < 10000 or amount > 50000):
                    continue
                elif amount_filter == "₹50,000 - ₹1,00,000" and (amount < 50000 or amount > 100000):
                    continue
                elif amount_filter == "Above ₹1,00,000" and amount <= 100000:
                    continue
                
                # Apply date filter
                if not self.check_date_filter(payment.get('date', ''), date_filter):
                    continue
                
                additional_filtered.append(payment)
            
            filtered_data = additional_filtered
        
        # Update table and stats with filtered data
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
        
        # Show filter status if applicable
        if len(filtered_data) != len(self.all_payments_data):
            self.update_filter_status(len(filtered_data), len(self.all_payments_data))
    
    def record_payment(self):
        """Open record payment dialog"""
        dialog = PaymentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def edit_payment(self, payment):
        """Open edit payment dialog"""
        dialog = PaymentDialog(self, payment)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def view_payment(self, payment):
        """View payment details"""
        details = f"""
<h3>💳 Payment Details</h3>

<p><b>Type:</b> {payment['type']}</p>
<p><b>Party:</b> {payment.get('party_name', 'N/A')}</p>
<p><b>Amount:</b> ₹{payment['amount']:,.2f}</p>
<p><b>Date:</b> {payment['date']}</p>
<p><b>Method:</b> {payment.get('method', 'N/A')}</p>
<p><b>Reference:</b> {payment.get('reference', 'N/A')}</p>
<p><b>Status:</b> {payment.get('status', 'N/A')}</p>
<p><b>Notes:</b> {payment.get('notes', 'N/A')}</p>
        """
        QMessageBox.information(self, "Payment Details", details.strip())
    
    def delete_payment(self, payment):
        """Delete payment with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"❓ Are you sure you want to delete this payment of ₹{payment['amount']:,.2f}?\n\n"
            f"Party: {payment.get('party_name', 'N/A')}\n"
            f"Date: {payment['date']}\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_payment(payment['id'])
                QMessageBox.information(self, "Success", "✅ Payment deleted successfully!")
                self.load_payments_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to delete payment:\n\n{str(e)}")
