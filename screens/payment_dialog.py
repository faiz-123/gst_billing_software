"""
Payment Dialog - Modern, Responsive Payment Recording Interface
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTextEdit, QDoubleSpinBox, QDateEdit, QScrollArea,
    QApplication, QButtonGroup, QRadioButton, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER
)
from database import db
from .party_selector import PartySelector


class PaymentDialog(QDialog):
    """Modern, responsive dialog for recording payments"""
    
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.parties = []
        self.invoices = []
        self.party_data_map = {}
        
        self._init_window()
        self._load_data()
        self._build_ui()
        
        if self.payment_data:
            self._populate_form()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Initialization
    # ─────────────────────────────────────────────────────────────────────────
    
    def _init_window(self):
        """Initialize window properties"""
        title = "Record Payment" if not self.payment_data else "Edit Payment"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(800, 700)
        self.resize(900, 800)
        self._center_window()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {BACKGROUND};
            }}
        """)
    
    def _center_window(self):
        """Center window on screen"""
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _load_data(self):
        """Load parties and invoices from database"""
        try:
            self.parties = db.get_parties() or []
            self.invoices = db.get_invoices() or []
        except Exception as e:
            print(f"Database error: {e}")
            self.parties = []
            self.invoices = []
        
        # Build party lookup map
        for party in self.parties:
            name = party.get('name', '').strip()
            if name:
                self.party_data_map[name] = party
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Building
    # ─────────────────────────────────────────────────────────────────────────
    
    def _build_ui(self):
        """Build the complete UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {BACKGROUND};
            }}
            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {PRIMARY};
            }}
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 25, 30, 25)
        
        # Form sections
        content_layout.addWidget(self._create_payment_type_section())
        content_layout.addWidget(self._create_party_section())
        content_layout.addWidget(self._create_payment_details_section())
        content_layout.addWidget(self._create_notes_section())
        content_layout.addWidget(self._create_summary_section())
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)
        
        # Footer with actions
        main_layout.addWidget(self._create_footer())
        
        # Initialize form state
        self._update_invoice_combo()
        self._update_summary()
    
    def _create_header(self):
        """Create header section"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY};
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Title
        icon = "💳" if not self.payment_data else "✏️"
        title_text = "Record New Payment" if not self.payment_data else "Edit Payment"
        title = QLabel(f"{icon}  {title_text}")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Payment ID badge (for editing)
        if self.payment_data:
            payment_id = self.payment_data.get('id', 'N/A')
            badge = QLabel(f"#{payment_id}")
            badge.setStyleSheet("""
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 13px;
                font-weight: bold;
            """)
            layout.addWidget(badge)
        
        return header
    
    def _create_section_card(self, title, icon=""):
        """Create a styled section card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section header
        if title:
            header = QLabel(f"{icon} {title}" if icon else title)
            header.setFont(QFont("Arial", 14, QFont.Bold))
            header.setStyleSheet(f"color: {TEXT_PRIMARY};")
            layout.addWidget(header)
        
        return card, layout
    
    def _create_payment_type_section(self):
        """Create payment type selection section"""
        card, layout = self._create_section_card("Payment Type", "📋")
        
        # Radio button container
        type_container = QWidget()
        type_layout = QHBoxLayout(type_container)
        type_layout.setSpacing(20)
        type_layout.setContentsMargins(0, 5, 0, 0)
        
        self.payment_type_group = QButtonGroup(self)
        
        # Received option
        received_container, self.received_radio = self._create_type_option(
            "Payment Received", 
            "Money coming in from customers",
            SUCCESS,
            "💰"
        )
        self.received_radio.setChecked(True)
        self.payment_type_group.addButton(self.received_radio, 0)
        type_layout.addWidget(received_container)
        
        # Made option
        made_container, self.made_radio = self._create_type_option(
            "Payment Made",
            "Money going out to suppliers", 
            DANGER,
            "💸"
        )
        self.payment_type_group.addButton(self.made_radio, 1)
        type_layout.addWidget(made_container)
        
        type_layout.addStretch()
        
        self.payment_type_group.buttonClicked.connect(self._on_payment_type_changed)
        
        layout.addWidget(type_container)
        return card
    
    def _create_type_option(self, title, subtitle, color, icon):
        """Create a styled payment type option - returns (container, radio)"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)
        container.setFixedWidth(250)
        container.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        radio = QRadioButton()
        radio.setStyleSheet(f"""
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
            }}
            QRadioButton::indicator:checked {{
                background: {color};
                border: 2px solid {color};
                border-radius: 10px;
            }}
            QRadioButton::indicator:unchecked {{
                background: white;
                border: 2px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        layout.addWidget(radio)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(QFont("Arial", 13, QFont.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        text_layout.addWidget(title_label)
        
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        text_layout.addWidget(sub_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Make container clickable
        container.mousePressEvent = lambda e: radio.setChecked(True)
        
        return container, radio
    
    def _create_party_section(self):
        """Create party selection section"""
        card, layout = self._create_section_card("Party Details", "🏢")
        
        # Party search field
        party_layout = QVBoxLayout()
        party_layout.setSpacing(8)
        
        party_label = QLabel("Select Party <span style='color:#EF4444'>*</span>")
        party_label.setTextFormat(Qt.RichText)
        party_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 13px;")
        party_layout.addWidget(party_label)
        
        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Click or type to search parties...")
        self.party_search.setMinimumHeight(45)
        self.party_search.setStyleSheet(self._get_input_style())
        self.party_search.setCursor(Qt.PointingHandCursor)
        self.party_search.returnPressed.connect(self._open_party_selector)
        self.party_search.textChanged.connect(self._on_party_text_changed)
        self.party_search.mousePressEvent = lambda e: self._open_party_selector()
        party_layout.addWidget(self.party_search)
        
        # Party info display
        self.party_info = QLabel()
        self.party_info.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            padding: 5px 0;
        """)
        self.party_info.hide()
        party_layout.addWidget(self.party_info)
        
        layout.addLayout(party_layout)
        return card
    
    def _create_payment_details_section(self):
        """Create payment details section"""
        card, layout = self._create_section_card("Payment Details", "💰")
        
        # Create grid for form fields
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # Invoice selection
        invoice_label = QLabel("Link to Invoice")
        invoice_label.setStyleSheet(self._get_label_style())
        grid.addWidget(invoice_label, row, 0)
        
        self.invoice_combo = QComboBox()
        self.invoice_combo.setMinimumHeight(45)
        self.invoice_combo.setStyleSheet(self._get_input_style())
        self.invoice_combo.currentIndexChanged.connect(self._on_invoice_changed)
        grid.addWidget(self.invoice_combo, row, 1)
        
        row += 1
        
        # Amount input
        amount_label = QLabel("Amount <span style='color:#EF4444'>*</span>")
        amount_label.setTextFormat(Qt.RichText)
        amount_label.setStyleSheet(self._get_label_style())
        grid.addWidget(amount_label, row, 0)
        
        amount_container = QWidget()
        amount_layout = QHBoxLayout(amount_container)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_layout.setSpacing(10)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 99999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setMinimumHeight(45)
        self.amount_input.setStyleSheet(self._get_input_style())
        self.amount_input.valueChanged.connect(self._on_amount_changed)
        amount_layout.addWidget(self.amount_input)
        
        self.outstanding_badge = QLabel("Select party")
        self.outstanding_badge.setStyleSheet(f"""
            background: {BACKGROUND};
            color: {TEXT_SECONDARY};
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
        """)
        amount_layout.addWidget(self.outstanding_badge)
        
        grid.addWidget(amount_container, row, 1)
        
        row += 1
        
        # Payment date
        date_label = QLabel("Payment Date <span style='color:#EF4444'>*</span>")
        date_label.setTextFormat(Qt.RichText)
        date_label.setStyleSheet(self._get_label_style())
        grid.addWidget(date_label, row, 0)
        
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setMinimumHeight(45)
        self.payment_date.setDisplayFormat("dd-MM-yyyy")
        
        # Import calendar stylesheet if available
        try:
            from theme import get_calendar_stylesheet
            self.payment_date.setStyleSheet(self._get_input_style() + get_calendar_stylesheet())
        except ImportError:
            self.payment_date.setStyleSheet(self._get_input_style())
        
        grid.addWidget(self.payment_date, row, 1)
        
        row += 1
        
        # Payment method
        method_label = QLabel("Payment Method <span style='color:#EF4444'>*</span>")
        method_label.setTextFormat(Qt.RichText)
        method_label.setStyleSheet(self._get_label_style())
        grid.addWidget(method_label, row, 0)
        
        self.payment_method = QComboBox()
        self.payment_method.setMinimumHeight(45)
        self.payment_method.setStyleSheet(self._get_input_style())
        
        methods = [
            ("💵 Cash", "Cash"),
            ("🏦 Bank Transfer", "Bank Transfer"),
            ("📱 UPI", "UPI"),
            ("📝 Cheque", "Cheque"),
            ("💳 Credit Card", "Credit Card"),
            ("💳 Debit Card", "Debit Card"),
            ("💻 Net Banking", "Net Banking"),
            ("📋 Other", "Other")
        ]
        for display, value in methods:
            self.payment_method.addItem(display, value)
        
        grid.addWidget(self.payment_method, row, 1)
        
        row += 1
        
        # Reference number
        ref_label = QLabel("Reference / Transaction No.")
        ref_label.setStyleSheet(self._get_label_style())
        grid.addWidget(ref_label, row, 0)
        
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Enter transaction reference...")
        self.reference_input.setMinimumHeight(45)
        self.reference_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.reference_input, row, 1)
        
        layout.addLayout(grid)
        return card
    
    def _create_notes_section(self):
        """Create notes section"""
        card, layout = self._create_section_card("Additional Notes", "📝")
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add any notes, remarks, or additional details about this payment...")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(120)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 12px;
                background: {WHITE};
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY};
            }}
        """)
        
        layout.addWidget(self.notes_input)
        return card
    
    def _create_summary_section(self):
        """Create payment summary section"""
        card, layout = self._create_section_card("Payment Summary", "📊")
        
        self.summary_label = QLabel("Complete the form to see payment summary")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(f"""
            background: {BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 15px;
            color: {TEXT_SECONDARY};
            font-size: 13px;
            line-height: 1.5;
        """)
        layout.addWidget(self.summary_label)
        
        return card
    
    def _create_footer(self):
        """Create footer with action buttons"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-top: 1px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(15)
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setFixedSize(100, 42)
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WARNING};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #D97706;
            }}
        """)
        help_btn.clicked.connect(self._show_help)
        layout.addWidget(help_btn)
        
        layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(120, 42)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
                border-color: {DANGER};
                color: {DANGER};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        # Save button
        save_text = "Update Payment" if self.payment_data else "Save Payment"
        self.save_btn = QPushButton(f"✓ {save_text}")
        self.save_btn.setFixedSize(160, 42)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
            QPushButton:disabled {{
                background: {BORDER};
                color: {TEXT_SECONDARY};
            }}
        """)
        self.save_btn.clicked.connect(self._save_payment)
        layout.addWidget(self.save_btn)
        
        return footer
    
    # ─────────────────────────────────────────────────────────────────────────
    # Style Helpers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_input_style(self):
        """Get consistent input styling"""
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                padding: 10px 14px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: {PRIMARY};
            }}
            QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover, QDateEdit:hover {{
                border-color: {PRIMARY_HOVER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """
    
    def _get_label_style(self):
        """Get consistent label styling"""
        return f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 13px;"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_payment_type_changed(self):
        """Handle payment type change"""
        self._update_invoice_combo()
        self._update_summary()
        
        # Clear party when type changes
        self.party_search.clear()
        self.party_info.hide()
    
    def _on_party_text_changed(self, text):
        """Handle party search text changes"""
        text = text.strip()
        if text in self.party_data_map:
            party = self.party_data_map[text]
            party_type = party.get('type', 'N/A')
            phone = party.get('phone', '')
            info_text = f"Type: {party_type}"
            if phone:
                info_text += f"  |  Phone: {phone}"
            self.party_info.setText(info_text)
            self.party_info.show()
            
            self._update_invoice_combo()
            self._update_outstanding_display()
            self._update_summary()
        else:
            self.party_info.hide()
    
    def _open_party_selector(self):
        """Open party selector dialog"""
        try:
            dlg = PartySelector(self.parties, self)
            
            # Prefill search
            current = self.party_search.text().strip()
            if current:
                dlg.search.setText(current)
            
            # Position below input
            try:
                dlg.resize(max(350, self.party_search.width()), 400)
                pos = self.party_search.mapToGlobal(self.party_search.rect().bottomLeft())
                screen = QApplication.desktop().availableGeometry()
                
                x = pos.x()
                y = pos.y() + 5
                
                if y + 400 > screen.bottom():
                    y = self.party_search.mapToGlobal(self.party_search.rect().topLeft()).y() - 405
                
                dlg.move(int(x), int(y))
            except Exception:
                pass
            
            if dlg.exec_() == QDialog.Accepted and dlg.selected_name:
                self.party_search.setText(dlg.selected_name)
        except Exception as e:
            print(f"Party selector error: {e}")
    
    def _on_invoice_changed(self):
        """Handle invoice selection change"""
        self._update_outstanding_display()
        self._update_summary()
        
        # Auto-fill amount from invoice due
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            due = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
            if due > 0:
                self.amount_input.setValue(due)
    
    def _on_amount_changed(self):
        """Handle amount change"""
        self._update_summary()
        self._validate_amount()
    
    def _update_invoice_combo(self):
        """Update invoice dropdown based on selected party"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        
        party = self._get_selected_party()
        if not party:
            return
        
        party_id = party.get('id')
        
        # Filter invoices for this party with outstanding balance
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            
            due = inv.get('due_amount', inv.get('grand_total', 0))
            if due <= 0:
                continue
            
            inv_no = inv.get('invoice_no', f"INV-{inv.get('id', 0):03d}")
            status = inv.get('status', 'Sent')
            icon = "📄" if status == 'Sent' else "⏰" if status == 'Overdue' else "✓"
            
            display = f"{icon} {inv_no} — ₹{due:,.2f} due"
            self.invoice_combo.addItem(display, inv)
    
    def _update_outstanding_display(self):
        """Update the outstanding amount badge"""
        party = self._get_selected_party()
        invoice = self.invoice_combo.currentData()
        
        if invoice:
            due = invoice.get('due_amount', invoice.get('grand_total', 0))
            self.outstanding_badge.setText(f"Due: ₹{due:,.2f}")
            color = DANGER if due > 0 else SUCCESS
            self.outstanding_badge.setStyleSheet(f"""
                background: rgba({self._hex_to_rgb(color)}, 0.1);
                color: {color};
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            """)
        elif party:
            balance = party.get('opening_balance', 0)
            self.outstanding_badge.setText(f"Balance: ₹{balance:,.2f}")
            color = SUCCESS if balance >= 0 else DANGER
            self.outstanding_badge.setStyleSheet(f"""
                background: rgba({self._hex_to_rgb(color)}, 0.1);
                color: {color};
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            """)
        else:
            self.outstanding_badge.setText("Select party")
            self.outstanding_badge.setStyleSheet(f"""
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            """)
    
    def _validate_amount(self):
        """Validate payment amount"""
        amount = self.amount_input.value()
        invoice = self.invoice_combo.currentData()
        
        if invoice:
            due = invoice.get('due_amount', invoice.get('grand_total', 0))
            if amount > due:
                # Warning style for overpayment
                self.amount_input.setStyleSheet(f"""
                    QDoubleSpinBox {{
                        border: 2px solid {WARNING};
                        border-radius: 10px;
                        padding: 10px 14px;
                        background: rgba(245, 158, 11, 0.1);
                        font-size: 14px;
                        color: {TEXT_PRIMARY};
                    }}
                """)
                return
        
        # Normal style
        self.amount_input.setStyleSheet(self._get_input_style())
    
    def _update_summary(self):
        """Update the payment summary display"""
        party = self._get_selected_party()
        amount = self.amount_input.value()
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        
        if not party:
            self.summary_label.setText("Complete the form to see payment summary")
            self.summary_label.setStyleSheet(f"""
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 15px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
            """)
            return
        
        invoice = self.invoice_combo.currentData()
        
        html = f"""
        <div style='line-height: 1.6;'>
            <p><b>Type:</b> {payment_type}</p>
            <p><b>Party:</b> {party.get('name', 'N/A')}</p>
            <p><b>Amount:</b> ₹{amount:,.2f}</p>
            <p><b>Date:</b> {self.payment_date.date().toString('dd-MM-yyyy')}</p>
            <p><b>Method:</b> {self.payment_method.currentText()}</p>
        """
        
        if invoice:
            due = invoice.get('due_amount', invoice.get('grand_total', 0))
            remaining = due - amount
            inv_no = invoice.get('invoice_no', 'N/A')
            
            html += f"""
            <hr style='border: none; border-top: 1px solid {BORDER}; margin: 10px 0;'>
            <p><b>Invoice:</b> {inv_no}</p>
            <p><b>Invoice Due:</b> ₹{due:,.2f}</p>
            <p><b>After Payment:</b> ₹{max(0, remaining):,.2f}</p>
            """
            
            if remaining < 0:
                html += f"<p style='color: {WARNING};'><b>⚠️ Overpayment: ₹{abs(remaining):,.2f}</b></p>"
            elif remaining == 0:
                html += f"<p style='color: {SUCCESS};'><b>✓ Invoice will be fully paid</b></p>"
        else:
            html += "<p><b>Invoice:</b> Direct Payment</p>"
        
        html += "</div>"
        
        self.summary_label.setText(html)
        self.summary_label.setStyleSheet(f"""
            background: {BACKGROUND};
            border: 1px solid {SUCCESS};
            border-radius: 8px;
            padding: 15px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
        """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_selected_party(self):
        """Get currently selected party data"""
        name = self.party_search.text().strip()
        return self.party_data_map.get(name)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
<h3>💳 Payment Recording Help</h3>

<h4>Payment Types:</h4>
<p><b>Payment Received:</b> Money coming into your business from customers</p>
<p><b>Payment Made:</b> Money going out to suppliers</p>

<h4>Invoice Linking:</h4>
<p>• <b>With Invoice:</b> Links payment to a specific invoice for tracking</p>
<p>• <b>Direct Payment:</b> General payment not linked to any invoice</p>

<h4>Tips:</h4>
<ul>
<li>Always enter reference numbers for bank/UPI payments</li>
<li>Link payments to invoices when possible for better tracking</li>
<li>Add notes for special circumstances</li>
</ul>
        """
        QMessageBox.information(self, "Payment Help", help_text)
    
    def _populate_form(self):
        """Populate form with existing payment data"""
        if not self.payment_data:
            return
        
        # Payment type
        ptype = self.payment_data.get('type', 'Payment Received')
        if ptype == 'Payment Received':
            self.received_radio.setChecked(True)
        else:
            self.made_radio.setChecked(True)
        
        # Party
        party_id = self.payment_data.get('party_id')
        if party_id:
            for party in self.parties:
                if party.get('id') == party_id:
                    self.party_search.setText(party.get('name', ''))
                    break
        
        # Trigger update
        self._update_invoice_combo()
        
        # Invoice
        invoice_id = self.payment_data.get('invoice_id')
        if invoice_id:
            for i in range(self.invoice_combo.count()):
                inv = self.invoice_combo.itemData(i)
                if inv and inv.get('id') == invoice_id:
                    self.invoice_combo.setCurrentIndex(i)
                    break
        
        # Other fields
        self.amount_input.setValue(self.payment_data.get('amount', 0))
        
        date_str = self.payment_data.get('date', '')
        if date_str:
            date = QDate.fromString(date_str, 'yyyy-MM-dd')
            if date.isValid():
                self.payment_date.setDate(date)
        
        method = self.payment_data.get('method', 'Cash')
        for i in range(self.payment_method.count()):
            if self.payment_method.itemData(i) == method:
                self.payment_method.setCurrentIndex(i)
                break
        
        self.reference_input.setText(self.payment_data.get('reference', ''))
        self.notes_input.setPlainText(self.payment_data.get('notes', ''))
    
    def _save_payment(self):
        """Save payment to database"""
        # Validation
        party = self._get_selected_party()
        if not party:
            QMessageBox.warning(self, "Validation Error", "Please select a valid party!")
            self.party_search.setFocus()
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount!")
            self.amount_input.setFocus()
            return
        
        # Check reference for non-cash payments
        method = self.payment_method.currentData()
        reference = self.reference_input.text().strip()
        if method != "Cash" and not reference:
            reply = QMessageBox.question(
                self, "Missing Reference",
                f"No reference number for {method} payment.\n\nContinue without reference?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.reference_input.setFocus()
                return
        
        # Overpayment warning
        invoice = self.invoice_combo.currentData()
        if invoice:
            due = invoice.get('due_amount', invoice.get('grand_total', 0))
            if amount > due:
                reply = QMessageBox.question(
                    self, "Overpayment Warning",
                    f"Payment (₹{amount:,.2f}) exceeds due amount (₹{due:,.2f}).\n\nContinue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
        
        # Prepare data
        payment_type = "Payment Received" if self.received_radio.isChecked() else "Payment Made"
        
        payment_data = {
            'type': payment_type,
            'party_id': party['id'],
            'party_name': party['name'],
            'amount': amount,
            'date': self.payment_date.date().toString('yyyy-MM-dd'),
            'method': method,
            'reference': reference,
            'notes': self.notes_input.toPlainText().strip(),
            'status': 'Completed'
        }
        
        if invoice:
            payment_data['invoice_id'] = invoice['id']
            payment_data['invoice_no'] = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
        
        # Save
        try:
            self.save_btn.setEnabled(False)
            self.save_btn.setText("Saving...")
            
            if self.payment_data:
                payment_data['id'] = self.payment_data['id']
                db.update_payment(payment_data)
                msg = "Payment updated successfully!"
            else:
                import datetime
                payment_id = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                db.add_payment(
                    payment_id=payment_id,
                    party_id=payment_data['party_id'],
                    amount=payment_data['amount'],
                    date=payment_data['date'],
                    mode=payment_data['method'],
                    invoice_id=payment_data.get('invoice_id'),
                    notes=payment_data['notes']
                )
                msg = "Payment recorded successfully!"
            
            QMessageBox.information(self, "Success", f"✓ {msg}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment:\n\n{str(e)}")
        finally:
            self.save_btn.setEnabled(True)
            self.save_btn.setText("✓ " + ("Update Payment" if self.payment_data else "Save Payment"))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Window Events
    # ─────────────────────────────────────────────────────────────────────────
    
    def resizeEvent(self, event):
        """Handle window resize for responsive layout"""
        super().resizeEvent(event)
        # Could add responsive adjustments here if needed
