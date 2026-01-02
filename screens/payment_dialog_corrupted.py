"""
Payment Dialog - Record and manage payments with modern enhanced UI
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSplitter, QGroupBox,
    QAbstractItemView, QMenu, QAction, QCompleter, QButtonGroup, QRadioButton, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QCursor

from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER, get_title_font, FONT_SIZE_NORMAL, FONT_SIZE_LARGE
)
from database import db

class PaymentDialog(QDialog):
    """Modern payment dialog with enhanced UI features and improved UX"""
    
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.parties = []
        self.invoices = []
        
        # Initialize window
        self.init_window()
        
        # Load data
        self.load_data()
        
        # Setup modern UI
        self.setup_modern_ui()
        
        # Populate if editing
        if self.payment_data:
            self.populate_form()
    
    def init_window(self):
        """Initialize window with modern styling"""
        title = "💳 Record Payment" if not self.payment_data else "📝 Edit Payment"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        self.resize(1000, 700)
        
        # Try to center relative to parent
        try:
            if self.parent():
                parent_geo = self.parent().geometry()
                x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
                y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
                self.move(max(0, x), max(0, y))
        except:
            pass
        
        # Modern window styling
        self.setStyleSheet(f"""
            QDialog {{
                background: {BACKGROUND};
                border: none;
            }}
        """)
    
    def load_data(self):
        """Load parties and invoices data"""
        try:
            if hasattr(db, 'get_parties') and callable(db.get_parties):
                self.parties = db.get_parties() or []
            if hasattr(db, 'get_invoices') and callable(db.get_invoices):
                self.invoices = db.get_invoices() or []
        except Exception as e:
            print(f"Database error: {e}")
            # Fallback sample data
            self.parties = [
                {'id': 1, 'name': 'ABC Corporation', 'type': 'Customer', 'opening_balance': 5000, 'phone': '+91 98765 43210'},
                {'id': 2, 'name': 'XYZ Limited', 'type': 'Supplier', 'opening_balance': -2000, 'phone': '+91 98765 43211'},
                {'id': 3, 'name': 'Tech Solutions Pvt Ltd', 'type': 'Both', 'opening_balance': 0, 'phone': '+91 98765 43212'}
            ]
            self.invoices = [
                {'id': 1, 'invoice_no': 'INV-001', 'party_id': 1, 'grand_total': 54000, 'status': 'Sent', 'due_amount': 54000},
                {'id': 2, 'invoice_no': 'INV-002', 'party_id': 2, 'grand_total': 25000, 'status': 'Sent', 'due_amount': 25000}
            ]
    
    def setup_modern_ui(self):
        """Setup modern enhanced UI layout"""
        # Main layout with proper margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Modern title section
        self.create_title_section(main_layout)
        
        # Main content area
        self.create_main_content(main_layout)
        
        # Action buttons
        self.create_action_buttons(main_layout)
    
    def create_title_section(self, parent_layout):
        """Create modern title section"""
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
                border: none;
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        # Main title with icon
        title_text = "💳 Record New Payment" if not self.payment_data else "📝 Edit Payment"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Arial", 22, QFont.Bold))
        self.title_label.setStyleSheet("color: white; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Payment ID if editing
        if self.payment_data:
            payment_id = self.payment_data.get('id', 'N/A')
            id_label = QLabel(f"Payment #{payment_id}")
            id_label.setFont(QFont("Arial", 14))
            id_label.setStyleSheet("color: rgba(255,255,255,0.9); border: none;")
            title_layout.addWidget(id_label)
        
        parent_layout.addWidget(title_frame)
    
    def create_main_content(self, parent_layout):
        """Create main content area with modern layout"""
        # Content container
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 16px;
                margin: 5px;
            }}
        """)
        
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left side - Payment form
        left_panel = self.create_payment_form()
        content_layout.addWidget(left_panel, 2)
        
        # Right side - Summary and info
        right_panel = self.create_summary_panel()
        content_layout.addWidget(right_panel, 1)
        
        parent_layout.addWidget(content_frame)
    
    def create_payment_form(self):
        """Create modern payment form"""
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: none;
                border-radius: 16px 0 0 16px;
                padding: 20px;
            }}
        """)
        
        main_layout = QVBoxLayout(form_frame)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Section header
        header = QLabel("💼 Payment Information")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                border: none;
                padding: 12px 0;
                background: transparent;
            }}
        """)
        main_layout.addWidget(header)
        
        # Form sections
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Payment type section
        self.create_payment_type_section(form_layout)
        
        # Party and invoice section
        self.create_party_invoice_section(form_layout)
        
        # Amount and date section
        self.create_amount_date_section(form_layout)
        
        # Method and reference section
        self.create_method_reference_section(form_layout)
        
        # Notes section
        self.create_notes_section(form_layout)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        return form_frame
    
    def create_payment_type_section(self, parent_layout):
        """Create payment type selection section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(12)
        
        # Section title
        type_label = QLabel("📋 Payment Type")
        type_label.setFont(QFont("Arial", 16, QFont.Bold))
        type_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; padding: 0;")
        section_layout.addWidget(type_label)
        
        # Radio buttons
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(30)
        
        self.payment_type_group = QButtonGroup()
        
        # Received radio
        self.received_radio = QRadioButton("💰 Payment Received")
        self.received_radio.setChecked(True)
        self.received_radio.setFont(QFont("Arial", 14, QFont.Medium))
        self.received_radio.setStyleSheet(f"""
            QRadioButton {{
                color: {TEXT_PRIMARY};
                spacing: 8px;
                padding: 8px;
                border: 2px solid transparent;
                border-radius: 8px;
            }}
            QRadioButton:hover {{
                background: rgba(16, 185, 129, 0.1);
                border-color: {SUCCESS};
            }}
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {BORDER};
                background: {WHITE};
            }}
            QRadioButton::indicator:checked {{
                background: {SUCCESS};
                border-color: {SUCCESS};
            }}
            QRadioButton::indicator:checked:after {{
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background: white;
                margin: 6px;
            }}
        """)
        
        # Made radio
        self.made_radio = QRadioButton("💸 Payment Made")
        self.made_radio.setFont(QFont("Arial", 14, QFont.Medium))
        self.made_radio.setStyleSheet(f"""
            QRadioButton {{
                color: {TEXT_PRIMARY};
                spacing: 8px;
                padding: 8px;
                border: 2px solid transparent;
                border-radius: 8px;
            }}
            QRadioButton:hover {{
                background: rgba(239, 68, 68, 0.1);
                border-color: {DANGER};
            }}
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {BORDER};
                background: {WHITE};
            }}
            QRadioButton::indicator:checked {{
                background: {DANGER};
                border-color: {DANGER};
            }}
            QRadioButton::indicator:checked:after {{
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background: white;
                margin: 6px;
            }}
        """)
        
        self.payment_type_group.addButton(self.received_radio, 0)
        self.payment_type_group.addButton(self.made_radio, 1)
        self.payment_type_group.buttonClicked.connect(self.on_payment_type_changed)
        
        radio_layout.addWidget(self.received_radio)
        radio_layout.addWidget(self.made_radio)
        radio_layout.addStretch()
        
        section_layout.addLayout(radio_layout)
        parent_layout.addWidget(section_frame)
    
    def create_party_invoice_section(self, parent_layout):
        """Create party and invoice selection section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(16)
        
        # Grid layout for better alignment
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)
        
        # Party selection
        party_label = self.create_field_label("🏢 Select Party", required=True)
        grid_layout.addWidget(party_label, 0, 0)
        
        self.party_combo = QComboBox()
        self.party_combo.setEditable(True)
        self.party_combo.addItem("Select Party...", None)
        self.party_combo.setMinimumHeight(45)
        self.party_combo.setStyleSheet(self.get_input_style())
        self.party_combo.currentTextChanged.connect(self.on_party_changed)
        grid_layout.addWidget(self.party_combo, 1, 0)
        
        # Invoice reference
        invoice_label = self.create_field_label("📄 Invoice Reference")
        grid_layout.addWidget(invoice_label, 0, 1)
        
        self.invoice_combo = QComboBox()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        self.invoice_combo.setMinimumHeight(45)
        self.invoice_combo.setStyleSheet(self.get_input_style())
        self.invoice_combo.currentTextChanged.connect(self.on_invoice_changed)
        grid_layout.addWidget(self.invoice_combo, 1, 1)
        
        section_layout.addLayout(grid_layout)
        
        # Outstanding amount display
        self.outstanding_frame = QFrame()
        self.outstanding_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid {SUCCESS};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        self.outstanding_frame.setVisible(False)
        
        outstanding_layout = QHBoxLayout(self.outstanding_frame)
        outstanding_layout.setContentsMargins(12, 8, 12, 8)
        
        self.outstanding_label = QLabel("💡 Select party to see balance")
        self.outstanding_label.setFont(QFont("Arial", 14, QFont.Medium))
        self.outstanding_label.setStyleSheet(f"color: {SUCCESS}; border: none;")
        outstanding_layout.addWidget(self.outstanding_label)
        outstanding_layout.addStretch()
        
        section_layout.addWidget(self.outstanding_frame)
        
        parent_layout.addWidget(section_frame)
        
        # Update party combo
        self.update_party_combo()
    
    def create_amount_date_section(self, parent_layout):
        """Create amount and date section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(16)
        
        # Grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)
        
        # Amount
        amount_label = self.create_field_label("💰 Amount", required=True)
        grid_layout.addWidget(amount_label, 0, 0)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 9999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setValue(0.00)
        self.amount_input.setMinimumHeight(45)
        self.amount_input.setStyleSheet(self.get_input_style())
        self.amount_input.valueChanged.connect(self.validate_amount)
        grid_layout.addWidget(self.amount_input, 1, 0)
        
        # Payment date
        date_label = self.create_field_label("📅 Payment Date")
        grid_layout.addWidget(date_label, 0, 1)
        
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setMinimumHeight(45)
        
        # Apply calendar styling
        from theme import get_calendar_stylesheet
        self.payment_date.setStyleSheet(self.get_input_style() + get_calendar_stylesheet())
        grid_layout.addWidget(self.payment_date, 1, 1)
        
        section_layout.addLayout(grid_layout)
        parent_layout.addWidget(section_frame)
    
    def create_method_reference_section(self, parent_layout):
        """Create payment method and reference section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(16)
        
        # Grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)
        
        # Payment method
        method_label = self.create_field_label("💳 Payment Method")
        grid_layout.addWidget(method_label, 0, 0)
        
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
        
        self.payment_method.setMinimumHeight(45)
        self.payment_method.setStyleSheet(self.get_input_style())
        grid_layout.addWidget(self.payment_method, 1, 0)
        
        # Reference number
        ref_label = self.create_field_label("🔗 Reference Number")
        grid_layout.addWidget(ref_label, 0, 1)
        
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Transaction/reference number...")
        self.reference_input.setMinimumHeight(45)
        self.reference_input.setStyleSheet(self.get_input_style())
        grid_layout.addWidget(self.reference_input, 1, 1)
        
        section_layout.addLayout(grid_layout)
        parent_layout.addWidget(section_frame)
    
    def create_notes_section(self, parent_layout):
        """Create notes section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(12)
        
        # Notes label
        notes_label = self.create_field_label("� Notes & Remarks")
        section_layout.addWidget(notes_label)
        
        # Notes input
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add payment notes, remarks, or additional details...")
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 12px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY};
                background: #F8FAFC;
            }}
        """)
        section_layout.addWidget(self.notes_input)
        
        parent_layout.addWidget(section_frame)
    
    def create_summary_panel(self):
        """Create right panel with summary and tips"""
        panel_frame = QFrame()
        panel_frame.setStyleSheet(f"""
            QFrame {{
                background: #F8FAFC;
                border: none;
                border-radius: 0 16px 16px 0;
                padding: 0;
            }}
        """)
        
        panel_layout = QVBoxLayout(panel_frame)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(20)
        
        # Summary header
        summary_header = QLabel("� Payment Summary")
        summary_header.setFont(QFont("Arial", 16, QFont.Bold))
        summary_header.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                border: none;
                padding: 12px 0;
            }}
        """)
        panel_layout.addWidget(summary_header)
        
        # Summary content
        self.summary_content = QLabel("Select party and invoice to see payment summary")
        self.summary_content.setWordWrap(True)
        self.summary_content.setAlignment(Qt.AlignTop)
        self.summary_content.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 16px;
                background: {WHITE};
                font-size: 13px;
                line-height: 1.4;
            }}
        """)
        panel_layout.addWidget(self.summary_content)
        
        # Help button
        help_btn = QPushButton("💡 Payment Help")
        help_btn.setMinimumHeight(40)
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
            }}
        """)
        help_btn.clicked.connect(self.show_help)
        panel_layout.addWidget(help_btn)
        
        panel_layout.addStretch()
        
        return panel_frame
    
    def create_action_buttons(self, parent_layout):
        """Create modern action buttons"""
        button_frame = QFrame()
        button_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER};
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 0 30px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background: #F3F4F6;
                border-color: {DANGER};
                color: {DANGER};
            }}
            QPushButton:pressed {{
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        # Save button
        save_text = "💾 Update Payment" if self.payment_data else "💾 Record Payment"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {SUCCESS}, stop:1 #10B981);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 0 40px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10B981, stop:1 #059669);
            }}
            QPushButton:pressed {{
                background: {SUCCESS};
            }}
            QPushButton:disabled {{
                background: {BORDER};
                color: {TEXT_SECONDARY};
            }}
        """)
        self.save_btn.clicked.connect(self.save_payment)
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addWidget(button_frame)
    
    # Helper methods for styling
    def create_field_label(self, text, required=False):
        """Create styled field label"""
        label = QLabel(text)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        
        if required:
            label.setText(f"{text} *")
            label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; padding: 0;")
        else:
            label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; padding: 0;")
        
        return label
    
    def get_input_style(self):
        """Get standard input styling"""
        return f"""
            QComboBox, QLineEdit, QDoubleSpinBox, QDateEdit {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
                min-height: 21px;
            }}
            QComboBox:focus, QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: {PRIMARY};
                background: #F8FAFC;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QDateEdit::drop-down {{
                border: none;
                padding-right: 20px;
            }}
        """
    
    # Event handlers and business logic
    def update_party_combo(self):
        """Update party combo based on payment type"""
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        self.party_combo.clear()
        self.party_combo.addItem("Select Party...", None)
        
        # Filter parties based on payment type
        for party in self.parties:
            party_type = party.get('type', 'Both')
            opening_balance = party.get('opening_balance', 0)
            phone = party.get('phone', '')
            
            show_party = False
            if payment_type == "Payment Received":
                show_party = party_type in ['Customer', 'Both'] or opening_balance > 0
                icon = "👤"
            else:
                show_party = party_type in ['Supplier', 'Both'] or opening_balance < 0
                icon = "🏭"
            
            if show_party:
                balance_info = f" | Balance: ₹{opening_balance:,.0f}" if opening_balance != 0 else ""
                phone_info = f" | 📞 {phone[:10]}..." if phone else ""
                display_text = f"{icon} {party['name']}{balance_info}{phone_info}"
                self.party_combo.addItem(display_text, party)
    
    def on_payment_type_changed(self):
        """Handle payment type change"""
        self.update_party_combo()
        self.update_invoice_combo()
        self.update_summary()
        
        # Update title color
        if self.received_radio.isChecked():
            self.title_label.setText("💰 Record Payment Received")
        else:
            self.title_label.setText("💸 Record Payment Made")
    
    def on_party_changed(self):
        """Handle party selection change"""
        self.update_invoice_combo()
        self.update_outstanding_display()
        self.update_summary()
    
    def update_invoice_combo(self):
        """Update invoice combo with filtered invoices"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        
        party_data = self.party_combo.currentData()
        if party_data:
            party_id = party_data['id']
            
            # Filter invoices for selected party
            relevant_invoices = [inv for inv in self.invoices if inv.get('party_id') == party_id]
            
            for invoice in relevant_invoices:
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
        """Update outstanding amount display"""
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            self.outstanding_label.setText(f"💡 Due: ₹{due_amount:,.2f}")
            self.outstanding_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid {DANGER};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            self.outstanding_label.setStyleSheet(f"color: {DANGER}; border: none;")
            self.outstanding_frame.setVisible(True)
            
        elif party_data:
            balance = party_data.get('opening_balance', 0)
            if balance != 0:
                self.outstanding_label.setText(f"💰 Balance: ₹{balance:,.2f}")
                color = SUCCESS if balance > 0 else DANGER
                bg_color = "rgba(16, 185, 129, 0.1)" if balance > 0 else "rgba(239, 68, 68, 0.1)"
                self.outstanding_frame.setStyleSheet(f"""
                    QFrame {{
                        background: {bg_color};
                        border: 1px solid {color};
                        border-radius: 8px;
                        padding: 12px;
                    }}
                """)
                self.outstanding_label.setStyleSheet(f"color: {color}; border: none;")
                self.outstanding_frame.setVisible(True)
            else:
                self.outstanding_frame.setVisible(False)
        else:
            self.outstanding_frame.setVisible(False)
    
    def validate_amount(self):
        """Validate payment amount"""
        amount = self.amount_input.value()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            if amount > due_amount:
                # Show overpayment warning
                self.amount_input.setStyleSheet(f"""
                    QDoubleSpinBox {{
                        border: 2px solid {WARNING};
                        border-radius: 10px;
                        padding: 12px 16px;
                        background: rgba(245, 158, 11, 0.1);
                        font-size: 14px;
                        color: {TEXT_PRIMARY};
                    }}
                """)
            else:
                self.amount_input.setStyleSheet(self.get_input_style())
        
        self.update_summary()
    
    def update_summary(self):
        """Update payment summary"""
        # Safety check - widgets must be initialized
        if not hasattr(self, 'amount_input') or not hasattr(self, 'summary_content'):
            return
        
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        amount = self.amount_input.value()
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        
        if not party_data:
            self.summary_content.setText("Select party to see payment summary")
            return
        
        summary_html = f"""
        <div style='line-height: 1.6;'>
        <h3 style='color: {PRIMARY}; margin: 0 0 12px 0;'>📊 Payment Summary</h3>
        
        <p><strong>Type:</strong> {payment_type}</p>
        <p><strong>Party:</strong> {party_data.get('name', 'N/A')}</p>
        <p><strong>Amount:</strong> <span style='color: {PRIMARY}; font-weight: bold;'>₹{amount:,.2f}</span></p>
        """
        
        if invoice_data:
            due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            remaining = due_amount - amount
            
            summary_html += f"""
            <p><strong>Invoice:</strong> {invoice_data.get('invoice_no', 'N/A')}</p>
            <p><strong>Due Amount:</strong> ₹{due_amount:,.2f}</p>
            <p><strong>Remaining:</strong> ₹{remaining:,.2f}</p>
            """
            
            if remaining < 0:
                summary_html += f"<p style='color: {WARNING}; font-weight: bold;'>⚠️ Overpayment: ₹{abs(remaining):,.2f}</p>"
            elif remaining == 0:
                summary_html += f"<p style='color: {SUCCESS}; font-weight: bold;'>✅ Invoice will be fully paid</p>"
        else:
            summary_html += "<p><strong>Invoice:</strong> Direct Payment</p>"
        
        # Balance impact
        current_balance = party_data.get('opening_balance', 0)
        if payment_type == "Payment Received":
            new_balance = current_balance - amount
        else:
            new_balance = current_balance + amount
        
        summary_html += f"""
        <hr style='margin: 12px 0; border: 1px solid {BORDER};'>
        <p><strong>Current Balance:</strong> ₹{current_balance:,.2f}</p>
        <p><strong>New Balance:</strong> ₹{new_balance:,.2f}</p>
        </div>
        """
        
        self.summary_content.setText(summary_html)
    
    def show_help(self):
        """Show payment help dialog"""
        help_html = f"""
        <div style='line-height: 1.6;'>
        <h2 style='color: {PRIMARY};'>💳 Payment Recording Help</h2>
        
        <h3 style='color: {TEXT_PRIMARY};'>📋 Payment Types:</h3>
        <p><strong>Payment Received:</strong> Money coming into your business from customers</p>
        <p><strong>Payment Made:</strong> Money going out of your business to suppliers</p>
        
        <h3 style='color: {TEXT_PRIMARY};'>🏢 Party Selection:</h3>
        <p>Choose the customer or supplier for this payment. The list is filtered based on payment type.</p>
        
        <h3 style='color: {TEXT_PRIMARY};'>📄 Invoice Linking:</h3>
        <p><strong>With Invoice:</strong> Links payment to specific invoice for automatic reconciliation</p>
        <p><strong>Direct Payment:</strong> General payment not linked to any specific invoice</p>
        
        <h3 style='color: {TEXT_PRIMARY};'>💰 Amount Guidelines:</h3>
        <ul>
        <li>Enter the exact amount received or paid</li>
        <li>System warns about overpayments</li>
        <li>Partial payments are allowed</li>
        </ul>
        
        <h3 style='color: {TEXT_PRIMARY};'>💡 Best Practices:</h3>
        <ul>
        <li>Always enter reference numbers for bank transactions</li>
        <li>Add notes for cash payments</li>
        <li>Link payments to invoices when possible</li>
        <li>Double-check amount before saving</li>
        </ul>
        </div>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Payment Help")
        msg.setText(help_html)
        msg.setTextFormat(Qt.RichText)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def populate_form(self):
        """Populate form with existing payment data"""
        if not self.payment_data:
            return
        
        try:
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
            
            # Set payment date
            payment_date = self.payment_data.get('date', '')
            if payment_date:
                try:
                    date_obj = QDate.fromString(payment_date, 'yyyy-MM-dd')
                    self.payment_date.setDate(date_obj)
                except:
                    pass
            
            # Set payment method
            method = self.payment_data.get('method', 'Cash')
            for i in range(self.payment_method.count()):
                if self.payment_method.itemData(i) == method:
                    self.payment_method.setCurrentIndex(i)
                    break
            
            # Set reference and notes
            self.reference_input.setText(self.payment_data.get('reference', ''))
            self.notes_input.setPlainText(self.payment_data.get('notes', ''))
            
        except Exception as e:
            print(f"Error populating form: {e}")
    
    def save_payment(self):
        """Save payment with enhanced validation"""
        # Validate required fields
        party_data = self.party_combo.currentData()
        if not party_data:
            self.show_validation_error("🏢 Please select a party!")
            self.party_combo.setFocus()
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            self.show_validation_error("💰 Please enter a valid amount!")
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
        
        # Check for overpayment
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
            self.save_btn.setEnabled(False)
            self.save_btn.setText("💾 Saving...")
            
            if self.payment_data:  # Editing
                payment_data['id'] = self.payment_data['id']
                if hasattr(db, 'update_payment') and callable(db.update_payment):
                    db.update_payment(payment_data)
                success_msg = "✅ Payment updated successfully!"
            else:  # New payment
                if hasattr(db, 'add_payment') and callable(db.add_payment):
                    db.add_payment(payment_data)
                success_msg = "✅ Payment recorded successfully!"
            
            # Show success message
            self.show_success_message(success_msg, payment_data)
            self.accept()
        
        except Exception as e:
            self.show_error_message(f"❌ Failed to save payment:\n\n{str(e)}")
        finally:
            self.save_btn.setEnabled(True)
            save_text = "💾 Update Payment" if self.payment_data else "💾 Record Payment"
            self.save_btn.setText(save_text)
    
    def show_validation_error(self, message):
        """Show validation error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Validation Error")
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {WHITE};
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
        """)
        msg.exec_()
    
    def show_success_message(self, message, payment_data):
        """Show success message with details"""
        party_name = payment_data.get('party_name', 'N/A')
        amount = payment_data.get('amount', 0)
        method = payment_data.get('method', 'N/A')
        date = payment_data.get('date', 'N/A')
        
        details = f"""
{message}

Payment Details:
• Party: {party_name}
• Amount: ₹{amount:,.2f}
• Method: {method}
• Date: {QDate.fromString(date, 'yyyy-MM-dd').toString('dd-MM-yyyy')}
        """
        
        if payment_data.get('invoice_no'):
            details += f"\n• Invoice: {payment_data['invoice_no']}"
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText(details.strip())
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {WHITE};
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
        """)
        msg.exec_()
    
    def show_error_message(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {WHITE};
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
        """)
        msg.exec_()
    
    def create_action_buttons(self, parent_layout):
        """Create modern action buttons"""
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 12, 20, 12)
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setFixedSize(100, 40)
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WARNING};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #F59E0B;
            }}
            QPushButton:pressed {{
            }}
        """)
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #DC2626;
            }}
            QPushButton:pressed {{
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        save_text = "💾 Update Payment" if self.payment_data else "💾 Record Payment"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setFixedSize(150, 40)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
            QPushButton:pressed {{
            }}
        """)
        self.save_btn.clicked.connect(self.save_payment)
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addWidget(button_frame)
    
    # Helper methods for styling
    def create_field_label(self, text, required=False):
        """Create styled field label"""
        label = QLabel(text)
        if required:
            label.setText(f"{text} <span style='color:#DC2626'>*</span>")
            label.setTextFormat(Qt.RichText)
        
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                border: none;
                padding: 0;
                margin-bottom: 4px;
            }}
        """)
        return label
    
    def get_input_style(self):
        """Get consistent input styling"""
        return f"""
            QComboBox, QDoubleSpinBox, QLineEdit, QDateEdit {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY};
            }}
            QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QDateEdit:focus {{
                border-color: {PRIMARY};
                background: #F8FAFC;
            }}
            QComboBox:hover, QDoubleSpinBox:hover, QLineEdit:hover, QDateEdit:hover {{
                border-color: {PRIMARY_HOVER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {TEXT_SECONDARY};
                margin-right: 8px;
            }}
        """
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
        
        # Apply calendar styling
        from theme import get_calendar_stylesheet
        self.payment_date.setStyleSheet(input_style + get_calendar_stylesheet())
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
