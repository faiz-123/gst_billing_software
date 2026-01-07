"""
Receipt Dialog - Customer Payment Recording Interface (Money IN)
For recording payments received from customers against sales invoices.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTextEdit, QDoubleSpinBox, QDateEdit, QScrollArea,
    QApplication, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER
)
from database import db
from .party_selector import PartySelector


class ReceiptDialog(QDialog):
    """Dialog for recording receipts from customers (money IN)"""
    
    def __init__(self, parent=None, receipt_data=None):
        super().__init__(parent)
        self.receipt_data = receipt_data
        self.parties = []
        self.invoices = []
        self.party_data_map = {}
        
        self._init_window()
        self._load_data()
        self._build_ui()
        
        if self.receipt_data:
            self._populate_form()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Initialization
    # ─────────────────────────────────────────────────────────────────────────
    
    def _init_window(self):
        """Initialize window properties"""
        title = "Record Receipt" if not self.receipt_data else "Edit Receipt"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(750, 650)
        self.showMaximized()
        
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
            # Get only customer type parties (for receipts)
            all_parties = db.get_parties() or []
            self.parties = [p for p in all_parties if p.get('party_type', '').lower() in ('customer', 'both', '')]
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
        content_layout.addWidget(self._create_party_section())
        content_layout.addWidget(self._create_settlement_mode_section())
        content_layout.addWidget(self._create_receipt_details_section())
        content_layout.addWidget(self._create_fifo_allocation_section())
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
                background: {SUCCESS};
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Title
        icon = "💰" if not self.receipt_data else "✏️"
        title_text = "Record Customer Receipt" if not self.receipt_data else "Edit Receipt"
        title = QLabel(f"{icon}  {title_text}")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Info badge
        info_badge = QLabel("Money IN")
        info_badge.setStyleSheet("""
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: bold;
        """)
        layout.addWidget(info_badge)
        
        # Receipt ID badge (for editing)
        if self.receipt_data:
            receipt_id = self.receipt_data.get('id', 'N/A')
            badge = QLabel(f"#{receipt_id}")
            badge.setStyleSheet("""
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 13px;
                font-weight: bold;
                margin-left: 10px;
            """)
            layout.addWidget(badge)
        
        return header
    
    def _create_section_card(self, title, icon=""):
        """Create a styled section card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: none;
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
    
    def _create_party_section(self):
        """Create customer selection section"""
        card, layout = self._create_section_card("Customer Details", "👤")
        
        # Party search field
        party_layout = QVBoxLayout()
        party_layout.setSpacing(8)
        
        party_label = QLabel("Select Customer <span style='color:#EF4444'>*</span>")
        party_label.setTextFormat(Qt.RichText)
        party_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 13px;")
        party_layout.addWidget(party_label)
        
        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Click or type to search customers...")
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
    
    def _create_settlement_mode_section(self):
        """Create settlement mode selection section"""
        card, layout = self._create_section_card("Settlement Mode", "⚙️")
        
        # Description
        desc = QLabel("Choose how to apply this receipt against outstanding invoices")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Radio button style options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)
        
        self.settlement_mode = "bill_to_bill"  # Default
        
        # Bill-to-Bill option
        self.btn_bill_to_bill = self._create_mode_button(
            "📄 Bill-to-Bill",
            "Select specific invoice to settle",
            "bill_to_bill",
            True
        )
        options_layout.addWidget(self.btn_bill_to_bill)
        
        # Auto-FIFO option
        self.btn_fifo = self._create_mode_button(
            "📊 Auto-FIFO",
            "Settle oldest invoices first",
            "fifo",
            False
        )
        options_layout.addWidget(self.btn_fifo)
        
        # Direct Receipt option
        self.btn_direct = self._create_mode_button(
            "💰 Direct/Advance",
            "No invoice linkage",
            "direct",
            False
        )
        options_layout.addWidget(self.btn_direct)
        
        layout.addLayout(options_layout)
        return card
    
    def _create_mode_button(self, title, subtitle, mode, is_active):
        """Create a settlement mode selection button"""
        btn = QFrame()
        btn.setFixedHeight(70)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("mode", mode)
        btn.setProperty("active", is_active)
        
        self._apply_mode_button_style(btn, is_active)
        
        btn_layout = QVBoxLayout(btn)
        btn_layout.setContentsMargins(15, 10, 15, 10)
        btn_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {PRIMARY if is_active else TEXT_PRIMARY}; border: none;")
        title_label.setProperty("title", True)
        btn_layout.addWidget(title_label)
        
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; border: none;")
        btn_layout.addWidget(sub_label)
        
        # Make clickable
        btn.mousePressEvent = lambda e, m=mode, b=btn: self._on_mode_selected(m, b)
        
        return btn
    
    def _apply_mode_button_style(self, btn, is_active):
        """Apply style to mode button based on active state"""
        if is_active:
            btn.setStyleSheet(f"""
                QFrame {{
                    background: {PRIMARY}10;
                    border: 2px solid {PRIMARY};
                    border-radius: 10px;
                }}
                QLabel {{
                    border: none;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 2px solid {BORDER};
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    border-color: {PRIMARY};
                    background: {BACKGROUND};
                }}
                QLabel {{
                    border: none;
                }}
            """)
    
    def _on_mode_selected(self, mode, clicked_btn):
        """Handle settlement mode selection"""
        self.settlement_mode = mode
        
        # Update all buttons
        for btn in [self.btn_bill_to_bill, self.btn_fifo, self.btn_direct]:
            is_active = btn == clicked_btn
            btn.setProperty("active", is_active)
            self._apply_mode_button_style(btn, is_active)
            
            # Update title color
            for child in btn.findChildren(QLabel):
                if child.property("title"):
                    child.setStyleSheet(f"color: {PRIMARY if is_active else TEXT_PRIMARY}; border: none;")
        
        # Update UI based on mode
        self._update_mode_ui()
        self._update_summary()
    
    def _update_mode_ui(self):
        """Update UI visibility based on selected settlement mode"""
        is_bill_to_bill = self.settlement_mode == "bill_to_bill"
        is_fifo = self.settlement_mode == "fifo"
        is_direct = self.settlement_mode == "direct"
        
        # Show/hide invoice combo (for bill-to-bill)
        if hasattr(self, 'invoice_combo'):
            self.invoice_combo.setVisible(is_bill_to_bill)
            self.invoice_label.setVisible(is_bill_to_bill)
        
        # Show/hide FIFO allocation section
        if hasattr(self, 'fifo_section'):
            self.fifo_section.setVisible(is_fifo)
            if is_fifo:
                self._calculate_fifo_allocation()
        
        # Update outstanding display
        self._update_outstanding_display()
    
    def _create_fifo_allocation_section(self):
        """Create FIFO allocation preview section"""
        self.fifo_section = QFrame()
        self.fifo_section.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        self.fifo_section.setVisible(False)  # Hidden by default
        
        layout = QVBoxLayout(self.fifo_section)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📊 FIFO Allocation Preview")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Total outstanding
        self.fifo_total_label = QLabel("Total Outstanding: ₹0")
        self.fifo_total_label.setStyleSheet(f"color: {DANGER}; font-weight: bold;")
        header_layout.addWidget(self.fifo_total_label)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("Amount will be allocated to oldest invoices first (FIFO)")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(desc)
        
        # Allocation table container
        self.fifo_allocation_container = QVBoxLayout()
        self.fifo_allocation_container.setSpacing(8)
        layout.addLayout(self.fifo_allocation_container)
        
        # Placeholder for allocation items
        self.fifo_allocation_label = QLabel("Select customer and enter amount to see allocation")
        self.fifo_allocation_label.setStyleSheet(f"""
            background: {BACKGROUND};
            border: 1px dashed {BORDER};
            border-radius: 8px;
            padding: 20px;
            color: {TEXT_SECONDARY};
            font-size: 13px;
        """)
        self.fifo_allocation_label.setAlignment(Qt.AlignCenter)
        self.fifo_allocation_container.addWidget(self.fifo_allocation_label)
        
        return self.fifo_section

    def _create_receipt_details_section(self):
        """Create receipt details section"""
        card, layout = self._create_section_card("Receipt Details", "💵")
        
        # Create grid for form fields
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # Invoice selection (for Bill-to-Bill mode)
        self.invoice_label = QLabel("Link to Sales Invoice")
        self.invoice_label.setStyleSheet(self._get_label_style())
        grid.addWidget(self.invoice_label, row, 0)
        
        self.invoice_combo = QComboBox()
        self.invoice_combo.setMinimumHeight(45)
        self.invoice_combo.setStyleSheet(self._get_input_style())
        self.invoice_combo.currentIndexChanged.connect(self._on_invoice_changed)
        grid.addWidget(self.invoice_combo, row, 1)
        
        row += 1
        
        # Amount input
        amount_label = QLabel("Amount Received <span style='color:#EF4444'>*</span>")
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
        
        self.outstanding_badge = QLabel("Select customer")
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
        
        # Receipt date
        date_label = QLabel("Receipt Date <span style='color:#EF4444'>*</span>")
        date_label.setTextFormat(Qt.RichText)
        date_label.setStyleSheet(self._get_label_style())
        grid.addWidget(date_label, row, 0)
        
        self.receipt_date = QDateEdit()
        self.receipt_date.setDate(QDate.currentDate())
        self.receipt_date.setCalendarPopup(True)
        self.receipt_date.setMinimumHeight(45)
        self.receipt_date.setDisplayFormat("dd-MM-yyyy")
        
        # Import calendar stylesheet if available
        try:
            from theme import get_calendar_stylesheet
            self.receipt_date.setStyleSheet(self._get_input_style() + get_calendar_stylesheet())
        except ImportError:
            self.receipt_date.setStyleSheet(self._get_input_style())
        
        grid.addWidget(self.receipt_date, row, 1)
        
        row += 1
        
        # Payment method
        method_label = QLabel("Received Via <span style='color:#EF4444'>*</span>")
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
        self.notes_input.setPlaceholderText("Add any notes, remarks, or additional details about this receipt...")
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
        """Create receipt summary section"""
        card, layout = self._create_section_card("Receipt Summary", "📊")
        
        self.summary_label = QLabel("Complete the form to see receipt summary")
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
        save_text = "Update Receipt" if self.receipt_data else "Save Receipt"
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
        self.save_btn.clicked.connect(self._save_receipt)
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
    
    def _on_party_text_changed(self, text):
        """Handle party search text changes"""
        text = text.strip()
        if text in self.party_data_map:
            party = self.party_data_map[text]
            party_type = party.get('party_type', 'N/A')
            phone = party.get('mobile', '')
            info_text = f"Type: {party_type}"
            if phone:
                info_text += f"  |  Phone: {phone}"
            self.party_info.setText(info_text)
            self.party_info.show()
            
            self._update_invoice_combo()
            self._update_outstanding_display()
            self._update_summary()
            
            # Update FIFO allocation if in FIFO mode
            if self.settlement_mode == "fifo":
                self._calculate_fifo_allocation()
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
        
        # Update FIFO allocation if in FIFO mode
        if self.settlement_mode == "fifo":
            self._calculate_fifo_allocation()
    
    def _calculate_fifo_allocation(self):
        """Calculate and display FIFO allocation preview"""
        party = self._get_selected_party()
        amount = self.amount_input.value()
        
        # Clear previous allocation widgets
        while self.fifo_allocation_container.count():
            item = self.fifo_allocation_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not party or amount <= 0:
            self.fifo_allocation_label = QLabel("Select customer and enter amount to see allocation")
            self.fifo_allocation_label.setStyleSheet(f"""
                background: {BACKGROUND};
                border: 1px dashed {BORDER};
                border-radius: 8px;
                padding: 20px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
            """)
            self.fifo_allocation_label.setAlignment(Qt.AlignCenter)
            self.fifo_allocation_container.addWidget(self.fifo_allocation_label)
            self.fifo_total_label.setText("Total Outstanding: ₹0")
            return
        
        # Get outstanding invoices for this customer, sorted by date (oldest first)
        party_id = party.get('id')
        outstanding_invoices = []
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            due = inv.get('due_amount', inv.get('grand_total', 0))
            if due > 0:
                outstanding_invoices.append(inv)
        
        # Sort by date (oldest first for FIFO)
        outstanding_invoices.sort(key=lambda x: x.get('date', ''))
        
        total_outstanding = sum(inv.get('due_amount', inv.get('grand_total', 0)) for inv in outstanding_invoices)
        self.fifo_total_label.setText(f"Total Outstanding: ₹{total_outstanding:,.2f}")
        
        if not outstanding_invoices:
            no_inv_label = QLabel("✅ No outstanding invoices for this customer")
            no_inv_label.setStyleSheet(f"""
                background: {SUCCESS}15;
                border: 1px solid {SUCCESS};
                border-radius: 8px;
                padding: 15px;
                color: {SUCCESS};
                font-size: 13px;
            """)
            no_inv_label.setAlignment(Qt.AlignCenter)
            self.fifo_allocation_container.addWidget(no_inv_label)
            return
        
        # Calculate allocation
        remaining_amount = amount
        self.fifo_allocations = []  # Store for saving
        
        for inv in outstanding_invoices:
            due = inv.get('due_amount', inv.get('grand_total', 0))
            inv_no = inv.get('invoice_no', f"INV-{inv.get('id', 0):03d}")
            inv_date = inv.get('date', 'N/A')
            
            if remaining_amount <= 0:
                allocation = 0
                status = "Pending"
                status_color = TEXT_SECONDARY
            elif remaining_amount >= due:
                allocation = due
                remaining_amount -= due
                status = "Full Payment"
                status_color = SUCCESS
            else:
                allocation = remaining_amount
                remaining_amount = 0
                status = "Partial"
                status_color = WARNING
            
            self.fifo_allocations.append({
                'invoice': inv,
                'amount': allocation
            })
            
            # Create allocation row
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {BACKGROUND};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QLabel {{
                    border: none;
                }}
            """)
            
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 12, 8)
            row_layout.setSpacing(15)
            
            # Invoice info
            inv_info = QLabel(f"📄 {inv_no}")
            inv_info.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; border: none;")
            row_layout.addWidget(inv_info)
            
            date_label = QLabel(f"Date: {inv_date}")
            date_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; border: none;")
            row_layout.addWidget(date_label)
            
            due_label = QLabel(f"Due: ₹{due:,.2f}")
            due_label.setStyleSheet(f"color: {DANGER}; font-size: 12px; border: none;")
            row_layout.addWidget(due_label)
            
            row_layout.addStretch()
            
            # Allocation amount
            alloc_label = QLabel(f"₹{allocation:,.2f}")
            alloc_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {PRIMARY}; border: none;")
            row_layout.addWidget(alloc_label)
            
            # Status badge
            status_badge = QLabel(status)
            status_badge.setStyleSheet(f"""
                background: {status_color}20;
                color: {status_color};
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                border: none;
            """)
            row_layout.addWidget(status_badge)
            
            self.fifo_allocation_container.addWidget(row)
        
        # Show remaining/excess if any
        if remaining_amount > 0:
            excess_label = QLabel(f"💰 Excess Amount: ₹{remaining_amount:,.2f} (will be added as advance)")
            excess_label.setStyleSheet(f"""
                background: {WARNING}15;
                border: 1px solid {WARNING};
                border-radius: 8px;
                padding: 12px;
                color: {WARNING};
                font-size: 13px;
                font-weight: bold;
            """)
            self.fifo_allocation_container.addWidget(excess_label)

    def _update_invoice_combo(self):
        """Update invoice dropdown based on selected customer"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("💰 Direct Receipt (No Invoice)", None)
        
        party = self._get_selected_party()
        if not party:
            return
        
        party_id = party.get('id')
        
        # Filter sales invoices for this customer with outstanding balance
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
            self.outstanding_badge.setText("Select customer")
            self.outstanding_badge.setStyleSheet(f"""
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            """)
    
    def _validate_amount(self):
        """Validate receipt amount"""
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
        """Update the receipt summary display"""
        party = self._get_selected_party()
        amount = self.amount_input.value()
        
        if not party:
            self.summary_label.setText("Complete the form to see receipt summary")
            self.summary_label.setStyleSheet(f"""
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 15px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
            """)
            return
        
        # Get settlement mode display
        mode_labels = {
            'bill_to_bill': '📄 Bill-to-Bill',
            'fifo': '📊 Auto-FIFO',
            'direct': '💰 Direct/Advance'
        }
        mode_display = mode_labels.get(self.settlement_mode, 'Unknown')
        
        html = f"""
        <div style='line-height: 1.6;'>
            <p><b>Type:</b> Receipt (Money IN)</p>
            <p><b>Customer:</b> {party.get('name', 'N/A')}</p>
            <p><b>Amount:</b> ₹{amount:,.2f}</p>
            <p><b>Date:</b> {self.receipt_date.date().toString('dd-MM-yyyy')}</p>
            <p><b>Received Via:</b> {self.payment_method.currentText()}</p>
            <p><b>Settlement:</b> {mode_display}</p>
        """
        
        if self.settlement_mode == "bill_to_bill":
            invoice = self.invoice_combo.currentData()
            if invoice:
                due = invoice.get('due_amount', invoice.get('grand_total', 0))
                remaining = due - amount
                inv_no = invoice.get('invoice_no', 'N/A')
                
                html += f"""
                <hr style='border: none; border-top: 1px solid {BORDER}; margin: 10px 0;'>
                <p><b>Invoice:</b> {inv_no}</p>
                <p><b>Invoice Due:</b> ₹{due:,.2f}</p>
                <p><b>After Receipt:</b> ₹{max(0, remaining):,.2f}</p>
                """
                
                if remaining < 0:
                    html += f"<p style='color: {WARNING};'><b>⚠️ Excess: ₹{abs(remaining):,.2f}</b></p>"
                elif remaining == 0:
                    html += f"<p style='color: {SUCCESS};'><b>✓ Invoice will be fully paid</b></p>"
            else:
                html += "<p><b>Invoice:</b> Direct Receipt (No invoice linked)</p>"
        
        elif self.settlement_mode == "fifo":
            if hasattr(self, 'fifo_allocations') and self.fifo_allocations:
                html += f"""
                <hr style='border: none; border-top: 1px solid {BORDER}; margin: 10px 0;'>
                <p><b>FIFO Allocation:</b> {len(self.fifo_allocations)} invoice(s)</p>
                """
                total_allocated = sum(a['amount'] for a in self.fifo_allocations)
                html += f"<p><b>Total Allocated:</b> ₹{total_allocated:,.2f}</p>"
                
                if amount > total_allocated:
                    excess = amount - total_allocated
                    html += f"<p style='color: {WARNING};'><b>Advance:</b> ₹{excess:,.2f}</p>"
            else:
                html += "<p><b>Allocation:</b> See FIFO preview above</p>"
        
        else:  # direct
            html += f"""
            <hr style='border: none; border-top: 1px solid {BORDER}; margin: 10px 0;'>
            <p><b>Note:</b> Direct receipt - no invoice linkage</p>
            <p style='color: {SUCCESS};'>Amount added to customer's credit balance</p>
            """
        
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
    
    def _populate_form(self):
        """Populate form with existing receipt data"""
        if not self.receipt_data:
            return
        
        # Party
        party_id = self.receipt_data.get('party_id')
        if party_id:
            for party in self.parties:
                if party.get('id') == party_id:
                    self.party_search.setText(party.get('name', ''))
                    break
        
        # Trigger update
        self._update_invoice_combo()
        
        # Invoice
        invoice_id = self.receipt_data.get('invoice_id')
        if invoice_id:
            for i in range(self.invoice_combo.count()):
                inv = self.invoice_combo.itemData(i)
                if inv and inv.get('id') == invoice_id:
                    self.invoice_combo.setCurrentIndex(i)
                    break
        
        # Other fields
        self.amount_input.setValue(self.receipt_data.get('amount', 0))
        
        date_str = self.receipt_data.get('date', '')
        if date_str:
            date = QDate.fromString(date_str, 'yyyy-MM-dd')
            if date.isValid():
                self.receipt_date.setDate(date)
        
        method = self.receipt_data.get('mode', 'Cash')
        for i in range(self.payment_method.count()):
            if self.payment_method.itemData(i) == method:
                self.payment_method.setCurrentIndex(i)
                break
        
        self.reference_input.setText(self.receipt_data.get('reference', ''))
        self.notes_input.setPlainText(self.receipt_data.get('notes', ''))
    
    def _save_receipt(self):
        """Save receipt to database"""
        # Validation
        party = self._get_selected_party()
        if not party:
            QMessageBox.warning(self, "Validation Error", "Please select a valid customer!")
            self.party_search.setFocus()
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount!")
            self.amount_input.setFocus()
            return
        
        # Check reference for non-cash receipts
        method = self.payment_method.currentData()
        reference = self.reference_input.text().strip()
        if method != "Cash" and not reference:
            reply = QMessageBox.question(
                self, "Missing Reference",
                f"No reference number for {method} receipt.\n\nContinue without reference?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.reference_input.setFocus()
                return
        
        # Mode-specific validation and warnings
        invoice = None
        if self.settlement_mode == "bill_to_bill":
            invoice = self.invoice_combo.currentData()
            if invoice:
                due = invoice.get('due_amount', invoice.get('grand_total', 0))
                if amount > due:
                    reply = QMessageBox.question(
                        self, "Excess Amount",
                        f"Receipt (₹{amount:,.2f}) exceeds due amount (₹{due:,.2f}).\n\nContinue?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
        
        elif self.settlement_mode == "fifo":
            # Confirm FIFO allocation
            if hasattr(self, 'fifo_allocations') and self.fifo_allocations:
                alloc_count = len([a for a in self.fifo_allocations if a['amount'] > 0])
                reply = QMessageBox.question(
                    self, "Confirm FIFO Settlement",
                    f"This will settle {alloc_count} invoice(s) using FIFO method.\n\nProceed?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.No:
                    return
        
        # Prepare notes
        receipt_notes = self.notes_input.toPlainText().strip()
        mode_label = {'bill_to_bill': 'Bill-to-Bill', 'fifo': 'FIFO', 'direct': 'Direct'}
        settlement_info = f"[{mode_label.get(self.settlement_mode, 'Unknown')}]"
        
        if receipt_notes:
            receipt_notes = f"[RECEIPT] {settlement_info} {receipt_notes}"
        else:
            receipt_notes = f"[RECEIPT] {settlement_info}"
        
        # Save using the payments table
        try:
            self.save_btn.setEnabled(False)
            self.save_btn.setText("Saving...")
            
            import datetime
            receipt_date = self.receipt_date.date().toString('yyyy-MM-dd')
            
            if self.settlement_mode == "fifo" and hasattr(self, 'fifo_allocations'):
                # Save multiple receipts for FIFO allocation
                self._save_fifo_receipts(party, method, reference, receipt_date, receipt_notes)
                msg = "FIFO receipts recorded successfully!"
            else:
                # Single receipt (bill-to-bill or direct)
                if self.receipt_data:
                    # Update existing
                    payment_data = {
                        'id': self.receipt_data['id'],
                        'payment_id': self.receipt_data.get('payment_id'),
                        'party_id': party['id'],
                        'amount': amount,
                        'date': receipt_date,
                        'mode': method,
                        'reference': reference,
                        'invoice_id': invoice['id'] if invoice else None,
                        'notes': receipt_notes,
                        'type': 'RECEIPT'
                    }
                    db.update_payment(payment_data)
                    msg = "Receipt updated successfully!"
                else:
                    payment_id = f"REC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    db.add_payment(
                        payment_id=payment_id,
                        party_id=party['id'],
                        amount=amount,
                        date=receipt_date,
                        mode=method,
                        reference=reference,
                        invoice_id=invoice['id'] if invoice else None,
                        notes=receipt_notes,
                        payment_type='RECEIPT'
                    )
                    msg = "Receipt recorded successfully!"
            
            QMessageBox.information(self, "Success", f"✓ {msg}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save receipt:\n\n{str(e)}")
        finally:
            self.save_btn.setEnabled(True)
            self.save_btn.setText("✓ " + ("Update Receipt" if self.receipt_data else "Save Receipt"))
    
    def _save_fifo_receipts(self, party, method, reference, receipt_date, base_notes):
        """Save multiple receipts for FIFO allocation"""
        import datetime
        
        total_amount = self.amount_input.value()
        allocated_total = 0
        
        for i, alloc in enumerate(self.fifo_allocations):
            if alloc['amount'] <= 0:
                continue
            
            invoice = alloc['invoice']
            alloc_amount = alloc['amount']
            allocated_total += alloc_amount
            
            # Generate unique payment ID with sequence
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            payment_id = f"REC-{timestamp}-{i+1:02d}"
            
            # Add invoice info to notes
            inv_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
            alloc_notes = f"{base_notes} [Allocated to {inv_no}]"
            
            db.add_payment(
                payment_id=payment_id,
                party_id=party['id'],
                amount=alloc_amount,
                date=receipt_date,
                mode=method,
                reference=reference,
                invoice_id=invoice['id'],
                notes=alloc_notes,
                payment_type='RECEIPT'
            )
        
        # If there's excess amount (advance), save as direct receipt
        excess = total_amount - allocated_total
        if excess > 0:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            payment_id = f"REC-{timestamp}-ADV"
            
            advance_notes = f"{base_notes} [Advance Payment]"
            
            db.add_payment(
                payment_id=payment_id,
                party_id=party['id'],
                amount=excess,
                date=receipt_date,
                mode=method,
                reference=reference,
                invoice_id=None,
                notes=advance_notes,
                payment_type='RECEIPT'
            )
