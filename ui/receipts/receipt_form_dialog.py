"""
Receipt Dialog - Customer Payment Recording Interface (Money IN)
For recording payments received from customers against sales invoices.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTextEdit, QDoubleSpinBox, QDateEdit, QScrollArea,
    QApplication, QGridLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER
)
from core.db.sqlite_db import db
from widgets import PartySelector


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
        # self.setMinimumSize(1200, 700)
        # self.resize(1400, 800)
        self._center_window()
        self.showMaximized()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {BACKGROUND};
            }}
        """)
    
    def _center_window(self):
        """Center window on screen"""
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
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
        """Build the complete UI with side-by-side layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Main content - side by side
        content = QWidget()
        content.setStyleSheet(f"background: {BACKGROUND};")
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 20, 25, 20)
        
        # LEFT PANEL - Customer & Payment Details
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel, 5)
        
        # RIGHT PANEL - Settlement & Summary
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, 4)
        
        main_layout.addWidget(content, 1)
        
        # Footer with actions
        main_layout.addWidget(self._create_footer())
        
        # Initialize form state
        self._update_invoice_combo()
        self._update_summary()
    
    def _create_left_panel(self):
        """Create left panel with customer and payment details"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Panel title
        title = QLabel("💰 Receipt Details")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(title)
        
        # Customer selection
        layout.addLayout(self._create_customer_field())
        
        # Settlement mode (compact)
        layout.addWidget(self._create_settlement_mode_compact())
        
        # Payment details grid
        layout.addLayout(self._create_payment_grid())
        
        # Notes (compact)
        layout.addLayout(self._create_notes_compact())
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self):
        """Create right panel with allocation preview and summary"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Panel title
        title = QLabel("📊 Settlement Preview")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(title)
        
        # Outstanding summary
        self.outstanding_card = self._create_outstanding_card()
        layout.addWidget(self.outstanding_card)
        
        # FIFO Allocation area (or invoice selection for bill-to-bill)
        self.allocation_area = QFrame()
        self.allocation_area.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        self.allocation_layout = QVBoxLayout(self.allocation_area)
        self.allocation_layout.setContentsMargins(15, 15, 15, 15)
        self.allocation_layout.setSpacing(10)
        
        # Placeholder
        self.allocation_placeholder = QLabel("Select customer to see invoices")
        self.allocation_placeholder.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        self.allocation_placeholder.setAlignment(Qt.AlignCenter)
        self.allocation_layout.addWidget(self.allocation_placeholder)
        
        layout.addWidget(self.allocation_area, 1)
        
        # Summary card at bottom
        layout.addWidget(self._create_summary_card())
        
        return panel
    
    def _create_customer_field(self):
        """Create customer selection field"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel("Customer <span style='color:#EF4444'>*</span>")
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(self._get_label_style())
        layout.addWidget(label)
        
        # Search field with button
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Type to search customer...")
        self.party_search.setMinimumHeight(45)
        self.party_search.setStyleSheet(self._get_input_style())
        self.party_search.textChanged.connect(self._on_party_text_changed)
        search_layout.addWidget(self.party_search)
        
        layout.addLayout(search_layout)
        
        # Party info badge
        self.party_info = QLabel()
        self.party_info.setStyleSheet(f"""
            background: {PRIMARY}15;
            color: {PRIMARY};
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
        """)
        self.party_info.hide()
        layout.addWidget(self.party_info)
        
        return layout
    
    def _create_settlement_mode_compact(self):
        """Create compact settlement mode selector"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        label = QLabel("Settlement:")
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600; font-size: 12px; border: none;")
        layout.addWidget(label)
        
        self.settlement_mode = "bill_to_bill"
        
        # Mode buttons (compact)
        self.btn_bill_to_bill = self._create_compact_mode_btn("📄 Bill-to-Bill", "bill_to_bill", True)
        layout.addWidget(self.btn_bill_to_bill)
        
        self.btn_fifo = self._create_compact_mode_btn("📊 Auto-FIFO", "fifo", False)
        layout.addWidget(self.btn_fifo)
        
        self.btn_direct = self._create_compact_mode_btn("💰 Direct", "direct", False)
        layout.addWidget(self.btn_direct)
        
        layout.addStretch()
        
        return container
    
    def _create_compact_mode_btn(self, text, mode, is_active):
        """Create compact mode selection button"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("mode", mode)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setMinimumHeight(32)
        
        self._apply_compact_btn_style(btn, is_active)
        btn.clicked.connect(lambda: self._on_compact_mode_selected(mode, btn))
        
        return btn
    
    def _apply_compact_btn_style(self, btn, is_active):
        """Apply style to compact mode button"""
        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {WHITE};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    border-color: {PRIMARY};
                    background: {PRIMARY}10;
                }}
            """)
    
    def _on_compact_mode_selected(self, mode, clicked_btn):
        """Handle compact mode selection"""
        self.settlement_mode = mode
        
        for btn in [self.btn_bill_to_bill, self.btn_fifo, self.btn_direct]:
            is_active = btn == clicked_btn
            btn.setChecked(is_active)
            self._apply_compact_btn_style(btn, is_active)
        
        self._update_allocation_area()
        self._update_summary()
    
    def _create_payment_grid(self):
        """Create payment details in a grid layout"""
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # Amount
        amount_label = QLabel("Amount <span style='color:#EF4444'>*</span>")
        amount_label.setTextFormat(Qt.RichText)
        amount_label.setStyleSheet(self._get_label_style())
        grid.addWidget(amount_label, row, 0)
        
        # Date
        date_label = QLabel("Date <span style='color:#EF4444'>*</span>")
        date_label.setTextFormat(Qt.RichText)
        date_label.setStyleSheet(self._get_label_style())
        grid.addWidget(date_label, row, 1)
        
        row += 1
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 99999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setMinimumHeight(45)
        self.amount_input.setStyleSheet(self._get_input_style())
        self.amount_input.valueChanged.connect(self._on_amount_changed)
        grid.addWidget(self.amount_input, row, 0)
        
        self.receipt_date = QDateEdit()
        self.receipt_date.setDate(QDate.currentDate())
        self.receipt_date.setCalendarPopup(True)
        self.receipt_date.setMinimumHeight(45)
        self.receipt_date.setDisplayFormat("dd-MM-yyyy")
        self.receipt_date.setStyleSheet(self._get_input_style())
        grid.addWidget(self.receipt_date, row, 1)
        
        row += 1
        
        # Payment method
        method_label = QLabel("Received Via <span style='color:#EF4444'>*</span>")
        method_label.setTextFormat(Qt.RichText)
        method_label.setStyleSheet(self._get_label_style())
        grid.addWidget(method_label, row, 0)
        
        # Reference
        ref_label = QLabel("Reference No.")
        ref_label.setStyleSheet(self._get_label_style())
        grid.addWidget(ref_label, row, 1)
        
        row += 1
        
        self.payment_method = QComboBox()
        self.payment_method.setMinimumHeight(45)
        self.payment_method.setStyleSheet(self._get_input_style())
        methods = [
            ("💵 Cash", "Cash"),
            ("🏦 Bank Transfer", "Bank Transfer"),
            ("📱 UPI", "UPI"),
            ("📝 Cheque", "Cheque"),
            ("💳 Card", "Card"),
        ]
        for display, value in methods:
            self.payment_method.addItem(display, value)
        grid.addWidget(self.payment_method, row, 0)
        
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Transaction reference...")
        self.reference_input.setMinimumHeight(45)
        self.reference_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.reference_input, row, 1)
        
        return grid
    
    def _create_notes_compact(self):
        """Create compact notes field"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel("Notes (optional)")
        label.setStyleSheet(self._get_label_style())
        layout.addWidget(label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add remarks...")
        self.notes_input.setFixedHeight(60)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 10px;
                background: {WHITE};
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY};
            }}
        """)
        layout.addWidget(self.notes_input)
        
        return layout
    
    def _create_outstanding_card(self):
        """Create outstanding amount display card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {DANGER}40;
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        self.outstanding_label = QLabel("Total Outstanding")
        self.outstanding_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; border: none;")
        layout.addWidget(self.outstanding_label)
        
        layout.addStretch()
        
        self.outstanding_amount = QLabel("₹0.00")
        self.outstanding_amount.setFont(QFont("Arial", 18, QFont.Bold))
        self.outstanding_amount.setStyleSheet(f"color: {DANGER}; border: none;")
        layout.addWidget(self.outstanding_amount)
        
        return card
    
    def _create_summary_card(self):
        """Create receipt summary card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {SUCCESS}10;
                border: 1px solid {SUCCESS}40;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        header = QLabel("📋 Receipt Summary")
        header.setFont(QFont("Arial", 13, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(header)
        
        self.summary_label = QLabel("Select customer to see summary")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; border: none; line-height: 1.4;")
        layout.addWidget(self.summary_label)
        
        return card
    
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
        """Handle party search text changes - opens selector when typing"""
        text = text.strip()
        
        # If exact match found, update display
        if text in self.party_data_map:
            party = self.party_data_map[text]
            party_type = party.get('party_type', 'N/A')
            phone = party.get('mobile', '')
            info_text = f"📌 {party_type}"
            if phone:
                info_text += f"  •  📞 {phone}"
            self.party_info.setText(info_text)
            self.party_info.show()
            
            self._update_outstanding_card()
            self._update_allocation_area()
            self._update_summary()
        else:
            self.party_info.hide()
            self._update_outstanding_card()
            self._update_allocation_area()
            
            # Open selector when user starts typing (and text is not empty)
            if text and len(text) >= 1:
                self._open_party_selector()
    
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
                from PySide6.QtGui import QGuiApplication
                dlg.resize(max(350, self.party_search.width()), 400)
                pos = self.party_search.mapToGlobal(self.party_search.rect().bottomLeft())
                screen = QGuiApplication.primaryScreen().availableGeometry()
                
                x = pos.x()
                y = pos.y() + 5
                
                if y + 400 > screen.bottom():
                    y = self.party_search.mapToGlobal(self.party_search.rect().topLeft()).y() - 405
                
                dlg.move(int(x), int(y))
            except Exception:
                pass
            
            if dlg.exec() == QDialog.Accepted and dlg.selected_name:
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
        self._update_allocation_area()
    
    def _update_outstanding_card(self):
        """Update the outstanding amount card"""
        party = self._get_selected_party()
        
        if not party:
            self.outstanding_amount.setText("₹0.00")
            self.outstanding_label.setText("Select a customer")
            return
        
        # Calculate total outstanding for this customer
        party_id = party.get('id')
        total_outstanding = 0
        invoice_count = 0
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            due = inv.get('due_amount', inv.get('grand_total', 0))
            if due > 0:
                total_outstanding += due
                invoice_count += 1
        
        self.outstanding_amount.setText(f"₹{total_outstanding:,.2f}")
        self.outstanding_label.setText(f"Total Outstanding ({invoice_count} invoices)")
        
        # Update card color based on amount
        if total_outstanding > 0:
            self.outstanding_card.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE}10;
                    border: 1px solid {DANGER}40;
                    border-radius: 8px;
                }}
            """)
            self.outstanding_amount.setStyleSheet(f"color: {DANGER}; border: none;")
        else:
            self.outstanding_card.setStyleSheet(f"""
                QFrame {{
                    background: {SUCCESS}10;
                    border: 1px solid {SUCCESS}40;
                    border-radius: 8px;
                }}
            """)
            self.outstanding_amount.setStyleSheet(f"color: {SUCCESS}; border: none;")
    
    def _update_allocation_area(self):
        """Update the allocation area based on settlement mode"""
        # Clear existing content
        while self.allocation_layout.count():
            item = self.allocation_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset selections
        self.selected_invoice = None
        self.invoice_cards = []
        
        party = self._get_selected_party()
        
        if not party:
            placeholder = QLabel("Select a customer to see invoice options")
            placeholder.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
            placeholder.setAlignment(Qt.AlignCenter)
            self.allocation_layout.addWidget(placeholder)
            return
        
        if self.settlement_mode == "bill_to_bill":
            self._show_bill_to_bill_selection()
        elif self.settlement_mode == "fifo":
            self._show_fifo_allocation()
        else:  # direct
            self._show_direct_mode()
    
    def _show_bill_to_bill_selection(self):
        """Show invoice selection for bill-to-bill mode as scrollable list"""
        header = QLabel("📄 Select Invoice to Settle")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; margin-bottom: 5px;")
        self.allocation_layout.addWidget(header)
        
        # Get outstanding invoices for this customer
        party = self._get_selected_party()
        if not party:
            return
            
        party_id = party.get('id')
        outstanding_invoices = []
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            due = inv.get('due_amount', inv.get('grand_total', 0))
            if due > 0:
                outstanding_invoices.append(inv)
        
        # Sort by date (newest first for bill-to-bill)
        outstanding_invoices.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if not outstanding_invoices:
            no_inv = QLabel("✅ No outstanding invoices for this customer")
            no_inv.setStyleSheet(f"color: {SUCCESS}; border: none; padding: 20px;")
            no_inv.setAlignment(Qt.AlignCenter)
            self.allocation_layout.addWidget(no_inv)
            
            # Add direct receipt option
            direct_btn = QPushButton("💰 Record as Direct Receipt")
            direct_btn.setMinimumHeight(40)
            direct_btn.setCursor(Qt.PointingHandCursor)
            direct_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {PRIMARY_HOVER};
                }}
            """)
            direct_btn.clicked.connect(lambda: self._on_compact_mode_selected("direct", self.btn_direct))
            self.allocation_layout.addWidget(direct_btn)
            self.allocation_layout.addStretch()
            return
        
        # Store selected invoice
        self.selected_invoice = None
        
        # Create scroll area for invoices
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{ width: 6px; background: transparent; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 5, 0)
        
        self.invoice_cards = []  # Store references to invoice cards
        
        for inv in outstanding_invoices:
            card = self._create_invoice_card(inv)
            scroll_layout.addWidget(card)
            self.invoice_cards.append(card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.allocation_layout.addWidget(scroll, 1)
        
        # Selected invoice details
        self.invoice_detail_label = QLabel("Click an invoice above to select it")
        self.invoice_detail_label.setWordWrap(True)
        self.invoice_detail_label.setStyleSheet(f"""
            background: {BACKGROUND};
            border: 1px dashed {BORDER};
            border-radius: 8px;
            padding: 12px;
            color: {TEXT_SECONDARY};
            font-size: 12px;
        """)
        self.invoice_detail_label.setAlignment(Qt.AlignCenter)
        self.allocation_layout.addWidget(self.invoice_detail_label)
    
    def _create_invoice_card(self, invoice):
        """Create a clickable invoice card"""
        card = QFrame()
        card.setProperty("invoice", invoice)
        card.setProperty("selected", False)
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(65)
        
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {PRIMARY};
                background: {PRIMARY}08;
            }}
            QLabel {{ border: none; }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Left side - Invoice info
        left = QVBoxLayout()
        left.setSpacing(2)
        
        inv_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        inv_date = invoice.get('date', 'N/A')
        
        title = QLabel(f"📄 {inv_no}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        left.addWidget(title)
        
        date_label = QLabel(f"Date: {inv_date}")
        date_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        left.addWidget(date_label)
        
        layout.addLayout(left)
        layout.addStretch()
        
        # Right side - Amount
        due = invoice.get('due_amount', invoice.get('grand_total', 0))
        amount_label = QLabel(f"₹{due:,.2f}")
        amount_label.setFont(QFont("Arial", 14, QFont.Bold))
        amount_label.setStyleSheet(f"color: {DANGER};")
        layout.addWidget(amount_label)
        
        # Make card clickable
        card.mousePressEvent = lambda e, c=card, inv=invoice: self._on_invoice_card_clicked(c, inv)
        
        return card
    
    def _on_invoice_card_clicked(self, card, invoice):
        """Handle invoice card click"""
        # Deselect all cards
        for c in self.invoice_cards:
            c.setProperty("selected", False)
            c.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border-color: {PRIMARY};
                    background: {PRIMARY}08;
                }}
                QLabel {{ border: none; }}
            """)
        
        # Select clicked card
        card.setProperty("selected", True)
        card.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY}15;
                border: 2px solid {PRIMARY};
                border-radius: 8px;
            }}
            QLabel {{ border: none; }}
        """)
        
        # Store selected invoice
        self.selected_invoice = invoice
        
        # Update detail label
        inv_no = invoice.get('invoice_no', 'N/A')
        due = invoice.get('due_amount', invoice.get('grand_total', 0))
        inv_date = invoice.get('date', 'N/A')
        
        self.invoice_detail_label.setText(
            f"<b>Selected:</b> {inv_no}  •  <b>Date:</b> {inv_date}  •  <b>Due:</b> ₹{due:,.2f}"
        )
        self.invoice_detail_label.setStyleSheet(f"""
            background: {SUCCESS}15;
            border: 1px solid {SUCCESS};
            border-radius: 8px;
            padding: 12px;
            color: {TEXT_PRIMARY};
            font-size: 12px;
        """)
        
        # Auto-fill amount
        if due > 0:
            self.amount_input.setValue(due)
        
        self._update_summary()
    
    def _show_fifo_allocation(self):
        """Show FIFO allocation preview"""
        header = QLabel("📊 Auto-FIFO Allocation")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; margin-bottom: 5px;")
        self.allocation_layout.addWidget(header)
        
        desc = QLabel("Amount will be allocated to oldest invoices first")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; border: none; margin-bottom: 10px;")
        self.allocation_layout.addWidget(desc)
        
        # Calculate and show allocations
        self._calculate_and_show_fifo()
    
    def _show_direct_mode(self):
        """Show direct/advance payment mode"""
        icon_label = QLabel("💰")
        icon_label.setFont(QFont("Arial", 36))
        icon_label.setStyleSheet("border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        self.allocation_layout.addWidget(icon_label)
        
        msg = QLabel("Direct / Advance Receipt")
        msg.setFont(QFont("Arial", 14, QFont.Bold))
        msg.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        msg.setAlignment(Qt.AlignCenter)
        self.allocation_layout.addWidget(msg)
        
        desc = QLabel("This receipt will not be linked to any invoice.\nAmount will be added to customer's credit balance.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; border: none;")
        desc.setAlignment(Qt.AlignCenter)
        self.allocation_layout.addWidget(desc)
        
        self.allocation_layout.addStretch()
    
    def _calculate_and_show_fifo(self):
        """Calculate FIFO allocation and display"""
        party = self._get_selected_party()
        amount = self.amount_input.value()
        
        if not party or amount <= 0:
            placeholder = QLabel("Enter amount to see allocation preview")
            placeholder.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
            placeholder.setAlignment(Qt.AlignCenter)
            self.allocation_layout.addWidget(placeholder)
            self.allocation_layout.addStretch()
            return
        
        # Get outstanding invoices sorted by date (oldest first)
        party_id = party.get('id')
        outstanding_invoices = []
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            due = inv.get('due_amount', inv.get('grand_total', 0))
            if due > 0:
                outstanding_invoices.append(inv)
        
        outstanding_invoices.sort(key=lambda x: x.get('date', ''))
        
        if not outstanding_invoices:
            no_inv = QLabel("✅ No outstanding invoices")
            no_inv.setStyleSheet(f"color: {SUCCESS}; border: none;")
            no_inv.setAlignment(Qt.AlignCenter)
            self.allocation_layout.addWidget(no_inv)
            self.allocation_layout.addStretch()
            return
        
        # Calculate allocation
        remaining = amount
        self.fifo_allocations = []
        
        # Create scroll area for allocations if many invoices
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{ width: 6px; background: transparent; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(6)
        scroll_layout.setContentsMargins(0, 0, 5, 0)
        
        for inv in outstanding_invoices:
            due = inv.get('due_amount', inv.get('grand_total', 0))
            inv_no = inv.get('invoice_no', f"INV-{inv.get('id', 0):03d}")
            inv_date = inv.get('date', 'N/A')
            
            if remaining <= 0:
                alloc_amount = 0
                status = "Pending"
                status_color = TEXT_SECONDARY
            elif remaining >= due:
                alloc_amount = due
                remaining -= due
                status = "Full"
                status_color = SUCCESS
            else:
                alloc_amount = remaining
                remaining = 0
                status = "Partial"
                status_color = WARNING
            
            if alloc_amount > 0:
                self.fifo_allocations.append({
                    'invoice': inv,
                    'invoice_id': inv.get('id'),
                    'invoice_no': inv_no,
                    'amount': alloc_amount
                })
            
            # Create row
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                }}
                QLabel {{ border: none; }}
            """)
            row.setFixedHeight(36)
            
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 4, 10, 4)
            row_layout.setSpacing(10)
            
            inv_label = QLabel(f"{inv_no}")
            inv_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 12px;")
            row_layout.addWidget(inv_label)
            
            due_label = QLabel(f"₹{due:,.0f}")
            due_label.setStyleSheet(f"color: {DANGER}; font-size: 11px;")
            row_layout.addWidget(due_label)
            
            row_layout.addStretch()
            
            alloc_label = QLabel(f"→ ₹{alloc_amount:,.0f}")
            alloc_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 12px;")
            row_layout.addWidget(alloc_label)
            
            status_badge = QLabel(status)
            status_badge.setFixedWidth(50)
            status_badge.setStyleSheet(f"""
                background: {status_color}20;
                color: {status_color};
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            """)
            status_badge.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(status_badge)
            
            scroll_layout.addWidget(row)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.allocation_layout.addWidget(scroll, 1)
        
        # Show excess if any
        if remaining > 0:
            excess = QLabel(f"💰 Advance: ₹{remaining:,.2f}")
            excess.setStyleSheet(f"color: {WARNING}; font-weight: bold; border: none; margin-top: 5px;")
            self.allocation_layout.addWidget(excess)
    
    def _update_invoice_detail(self):
        """Update invoice detail display"""
        if not hasattr(self, 'invoice_combo') or not hasattr(self, 'invoice_detail_label'):
            return
        
        try:
            invoice = self.invoice_combo.currentData()
            if invoice:
                due = invoice.get('due_amount', invoice.get('grand_total', 0))
                date = invoice.get('date', 'N/A')
                self.invoice_detail_label.setText(f"Date: {date}  •  Due: ₹{due:,.2f}")
                
                # Auto-fill amount
                if due > 0:
                    self.amount_input.setValue(due)
            else:
                self.invoice_detail_label.setText("Direct receipt - no invoice linkage")
        except RuntimeError:
            # Widget has been deleted
            pass
    
    def _on_invoice_changed(self):
        """Handle invoice selection change"""
        try:
            self._update_invoice_detail()
            self._update_summary()
        except RuntimeError:
            # Widgets may have been deleted
            pass

    def _update_invoice_combo(self):
        """Update invoice dropdown based on selected customer"""
        if not hasattr(self, 'invoice_combo'):
            return
        
        try:
            self.invoice_combo.clear()
        except RuntimeError:
            # Widget has been deleted
            return
            
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
            status = inv.get('status', 'Unpaid')
            icon = "📄" if status == 'Unpaid' else "⏰" if status == 'Overdue' else "✓"
            
            display = f"{icon} {inv_no} — ₹{due:,.2f} due"
            self.invoice_combo.addItem(display, inv)
    
    def _update_summary(self):
        """Update the receipt summary display"""
        party = self._get_selected_party()
        amount = self.amount_input.value()
        
        if not party:
            self.summary_label.setText("Select a customer to see summary")
            return
        
        # Get settlement mode display
        mode_labels = {
            'bill_to_bill': 'Bill-to-Bill',
            'fifo': 'Auto-FIFO',
            'direct': 'Direct/Advance'
        }
        mode_display = mode_labels.get(self.settlement_mode, 'Unknown')
        
        summary_parts = [
            f"<b>{party.get('name', 'N/A')}</b>",
            f"₹{amount:,.2f} via {self.payment_method.currentText()}",
            f"Mode: {mode_display}"
        ]
        
        if self.settlement_mode == "bill_to_bill":
            # Use selected_invoice from card selection
            invoice = getattr(self, 'selected_invoice', None)
            if invoice:
                inv_no = invoice.get('invoice_no', 'N/A')
                due = invoice.get('due_amount', 0)
                remaining = max(0, due - amount)
                summary_parts.append(f"Invoice: {inv_no}")
                if remaining == 0:
                    summary_parts.append(f"<span style='color:{SUCCESS}'>✓ Fully settled</span>")
                else:
                    summary_parts.append(f"Remaining: ₹{remaining:,.2f}")
            else:
                summary_parts.append("Select an invoice")
        
        elif self.settlement_mode == "fifo" and hasattr(self, 'fifo_allocations') and self.fifo_allocations:
            alloc_count = len(self.fifo_allocations)
            total_alloc = sum(a['amount'] for a in self.fifo_allocations)
            summary_parts.append(f"Settling {alloc_count} invoice(s)")
            if amount > total_alloc:
                summary_parts.append(f"Advance: ₹{amount - total_alloc:,.2f}")
        
        self.summary_label.setText(" • ".join(summary_parts))
    
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
            invoice = getattr(self, 'selected_invoice', None)
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
            else:
                # No invoice selected in bill-to-bill mode
                reply = QMessageBox.question(
                    self, "No Invoice Selected",
                    "No invoice selected. Record as Direct Receipt?",
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
