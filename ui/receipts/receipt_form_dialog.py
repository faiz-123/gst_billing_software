"""
Receipt Dialog - Customer Payment Recording Interface (Money IN)
For recording payments received from customers against sales invoices.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTextEdit, QDoubleSpinBox, QDateEdit, QScrollArea,
    QApplication, QGridLayout, QCompleter, QStyledItemDelegate, QStyle,
    QToolTip, QCheckBox, QProgressBar
)
from PySide6.QtCore import Qt, QDate, QTimer, QEvent, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QColor, QTextDocument, QKeyEvent

from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER, PRIMARY_LIGHT
)
from core.db.sqlite_db import db
from ui.error_handler import UIErrorHandler
from widgets import PartySelector, DialogEditableComboBox


class ValidationIndicator(QLabel):
    """Visual validation indicator (✓ or ✗) for form fields"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.is_valid = None
        self.setAlignment(Qt.AlignCenter)
        self.reset()
    
    def set_valid(self, is_valid: bool):
        """Set validation state"""
        self.is_valid = is_valid
        if is_valid:
            self.setText("✓")
            self.setStyleSheet(f"color: {SUCCESS}; font-weight: bold; font-size: 14px; border: none;")
        else:
            self.setText("✗")
            self.setStyleSheet(f"color: {DANGER}; font-weight: bold; font-size: 14px; border: none;")
    
    def reset(self):
        """Reset to neutral state"""
        self.is_valid = None
        self.setText("")
        self.setStyleSheet("border: none;")


class ReceiptValidator:
    """Validates receipt form data"""
    
    def __init__(self):
        self.errors = {}
    
    def validate_party(self, party) -> bool:
        """Validate party selection"""
        if not party:
            self.errors['party'] = "Please select a customer"
            return False
        self.errors.pop('party', None)
        return True
    
    def validate_amount(self, amount: float) -> bool:
        """Validate receipt amount"""
        if amount <= 0:
            self.errors['amount'] = "Amount must be greater than zero"
            return False
        if amount > 99999999.99:
            self.errors['amount'] = "Amount exceeds maximum limit"
            return False
        self.errors.pop('amount', None)
        return True
    
    def validate_date(self, date: QDate) -> bool:
        """Validate receipt date"""
        if date > QDate.currentDate():
            self.errors['date'] = "Receipt date cannot be in future"
            return False
        self.errors.pop('date', None)
        return True
    
    def validate_payment_method(self, method: str) -> bool:
        """Validate payment method"""
        if not method or method.strip() == "":
            self.errors['method'] = "Please select a payment method"
            return False
        self.errors.pop('method', None)
        return True
    
    def validate_reference(self, reference: str, method: str) -> bool:
        """Validate reference based on method"""
        if method in ['Cheque', 'Bank Transfer', 'UPI'] and not reference.strip():
            self.errors['reference'] = f"Reference is required for {method}"
            return False
        self.errors.pop('reference', None)
        return True
    
    def validate_all(self, party, amount, date, method, reference) -> bool:
        """Validate all fields"""
        self.errors = {}
        results = [
            self.validate_party(party),
            self.validate_amount(amount),
            self.validate_date(date),
            self.validate_payment_method(method),
            self.validate_reference(reference, method)
        ]
        return all(results)
    
    def get_error(self, field: str) -> str:
        """Get error message for a field"""
        return self.errors.get(field, "")


class DuplicateChecker:
    """Checks for duplicate receipts"""
    
    @staticmethod
    def check_duplicate_reference(reference: str, exclude_payment_id: str = None) -> bool:
        """Check if reference number already exists"""
        if not reference or not reference.strip():
            return False
        
        try:
            existing = db._query(
                "SELECT * FROM payments WHERE mode = ?",
                (reference.strip(),)
            )
            if exclude_payment_id:
                existing = [p for p in existing if p.get('id') != exclude_payment_id]
            return len(existing) > 0
        except Exception as e:
            print(f"Error checking duplicate reference: {e}")
            return False
    
    @staticmethod
    def check_duplicate_payment(party_id: int, amount: float, date: str) -> bool:
        """Check if same amount paid to same party on same date"""
        try:
            existing = db._query(
                "SELECT * FROM payments WHERE party_id = ? AND amount = ? AND date = ?",
                (party_id, amount, date)
            )
            return len(existing) > 0
        except Exception as e:
            print(f"Error checking duplicate payment: {e}")
            return False
    
    @staticmethod
    def get_payment_history(party_id: int, limit: int = 5):
        """Get recent payment history for party"""
        try:
            return db._query(
                "SELECT * FROM payments WHERE party_id = ? ORDER BY date DESC LIMIT ?",
                (party_id, limit)
            )
        except Exception as e:
            print(f"Error fetching payment history: {e}")
            return []


class HighlightDelegate(QStyledItemDelegate):
    """Custom delegate that highlights matching text in the party dropdown."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.highlight_color = "#FEF3C7"
        self.highlight_text_color = "#92400E"
        
    def set_search_text(self, text: str):
        """Set the text to highlight in dropdown items."""
        self.search_text = text.strip().upper() if text else ""
    
    def paint(self, painter, option, index):
        """Paint the item with highlighted matching text."""
        painter.save()
        
        text = index.data(Qt.DisplayRole) or ""
        
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(PRIMARY))
            text_color = QColor(WHITE)
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor(PRIMARY_LIGHT))
            text_color = QColor(TEXT_PRIMARY)
        else:
            painter.fillRect(option.rect, QColor(WHITE))
            text_color = QColor(TEXT_PRIMARY)
        
        if self.search_text and self.search_text in text.upper():
            html_text = self._create_highlighted_html(text, text_color, option.state & QStyle.State_Selected)
            
            doc = QTextDocument()
            doc.setHtml(html_text)
            doc.setDefaultFont(option.font)
            doc.setTextWidth(option.rect.width() - 24)
            
            painter.translate(option.rect.left() + 12, option.rect.top() + 8)
            doc.drawContents(painter)
        else:
            painter.setPen(text_color)
            painter.setFont(option.font)
            text_rect = option.rect.adjusted(12, 8, -12, -8)
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)
        
        painter.restore()
    
    def _create_highlighted_html(self, text: str, text_color: QColor, is_selected: bool) -> str:
        """Create HTML string with matching text highlighted."""
        if not self.search_text:
            return f'<span style="color: {text_color.name()};">{text}</span>'
        
        text_upper = text.upper()
        search_upper = self.search_text.upper()
        
        if search_upper not in text_upper:
            return f'<span style="color: {text_color.name()};">{text}</span>'
        
        html = f'<span style="color: {text_color.name()};">'
        start = 0
        while True:
            idx = text_upper.find(search_upper, start)
            if idx == -1:
                html += text[start:]
                break
            html += text[start:idx]
            html += f'<span style="background-color: {self.highlight_color}; color: {self.highlight_text_color}; font-weight: bold;">{text[idx:idx+len(self.search_text)]}</span>'
            start = idx + len(self.search_text)
        html += '</span>'
        return html
    
    def sizeHint(self, option, index):
        """Larger item height for better visibility."""
        size = super().sizeHint(option, index)
        size.setHeight(44)
        return size


class ReceiptDialog(QDialog):
    """Dialog for recording receipts from customers (money IN)"""
    
    def __init__(self, parent=None, receipt_data=None):
        super().__init__(parent)
        self.receipt_data = receipt_data
        self.parties = []
        self.invoices = []
        self.party_data_map = {}
        self.form_dirty = False  # Track unsaved changes
        
        # New: Validation and business logic
        self.validator = ReceiptValidator()
        self.duplicate_checker = DuplicateChecker()
        self.payment_history = []
        
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
        self.resize(1600, 900)
        self._center_window()
        
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
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 25, 30, 25)
        
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
        layout.setSpacing(22)
        layout.setContentsMargins(28, 28, 28, 28)
        
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
        layout.setSpacing(18)
        layout.setContentsMargins(28, 28, 28, 28)
        
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
        self.allocation_layout.setContentsMargins(16, 16, 16, 16)
        self.allocation_layout.setSpacing(12)
        
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
        """Create customer selection field with QCompleter and highlighting"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel("Customer <span style='color:#EF4444'>*</span>")
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 13px; border: none;")
        layout.addWidget(label)
        
        # Create party combo box with search functionality
        party_names = [p.get('name', '').strip() for p in (self.parties or []) if p.get('name', '').strip()]
        self.party_search = DialogEditableComboBox(
            items=[],  # Don't add items - we'll use QCompleter only
            placeholder="🔍 Type to search customer name...",
            auto_upper=True
        )
        self.party_search.setFixedHeight(44)
        self.party_search.setMinimumWidth(400)
        
        # Disable native completer - we'll use our custom QCompleter
        self.party_search.setCompleter(None)
        
        # Style the combobox
        self.party_search.setStyleSheet(self._get_input_style())
        
        # Populate party_data_map and display names
        self.party_data_map = {}
        self.party_display_map = {}
        all_display_names = []
        
        for p in (self.parties or []):
            name = p.get('name', '').strip()
            if name:
                self.party_data_map[name] = p
                self.party_display_map[name] = name
                all_display_names.append(name)
        
        # Sort alphabetically
        all_display_names.sort()
        
        # Create custom completer - this is the ONLY popup we use
        self.party_completer = QCompleter(all_display_names, self)
        self.party_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.party_completer.setFilterMode(Qt.MatchContains)
        self.party_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.party_completer.setMaxVisibleItems(15)
        
        # Create highlight delegate for matched text
        self.party_highlight_delegate = HighlightDelegate(self.party_completer.popup())
        self.party_completer.popup().setItemDelegate(self.party_highlight_delegate)
        
        # Style the completer popup
        self.party_completer.popup().setStyleSheet(f"""
            QListView {{
                background: {WHITE};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                padding: 4px;
                font-size: 14px;
                outline: none;
            }}
            QListView::item {{
                padding: 14px 16px;
                min-height: 44px;
                border: none;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListView::item:hover {{
                background: {PRIMARY_LIGHT};
            }}
            QListView::item:selected {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        
        # Set completer on the line edit
        self.party_search.lineEdit().setCompleter(self.party_completer)
        
        # Pre-position completer popup before it shows
        self._setup_completer_positioning()
        
        # Connect completer activation to selection handler
        self.party_completer.activated.connect(self._on_party_completer_activated)

        def custom_show_popup():
            # Show all items by completing with empty prefix
            self.party_completer.setCompletionPrefix("")
            self.party_completer.complete()
            self._position_completer_popup()

        # Connect to handle text changes
        self.party_search.lineEdit().textEdited.connect(self._on_party_text_edited)

        self.party_search.showPopup = custom_show_popup
        
        # Install event filter for keyboard navigation
        self.party_search.lineEdit().installEventFilter(self)
        self.party_search.installEventFilter(self)
        
        layout.addWidget(self.party_search)
        
        # Party info badge
        self.party_info = QLabel()
        self.party_info.setStyleSheet(f"""
            background: {PRIMARY}15;
            color: {PRIMARY};
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            border: none;
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
        grid.setSpacing(18)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # Invoice selection (for Bill-to-Bill mode)
        invoice_label = QLabel("Link to Sales Invoice")
        invoice_label.setStyleSheet(self._get_label_style())
        grid.addWidget(invoice_label, row, 0)
        
        self.invoice_combo = QComboBox()
        self.invoice_combo.setMinimumHeight(45)
        self.invoice_combo.setStyleSheet(self._get_input_style())
        self.invoice_combo.currentIndexChanged.connect(self._on_invoice_changed)
        grid.addWidget(self.invoice_combo, row, 1)
        
        row += 1
        
        # Amount label and Date label
        amount_label = QLabel("Amount <span style='color:#EF4444'>*</span>")
        amount_label.setTextFormat(Qt.RichText)
        amount_label.setStyleSheet(self._get_label_style())
        grid.addWidget(amount_label, row, 0)
        
        date_label = QLabel("Date <span style='color:#EF4444'>*</span>")
        date_label.setTextFormat(Qt.RichText)
        date_label.setStyleSheet(self._get_label_style())
        grid.addWidget(date_label, row, 1)
        
        row += 1
        
        # Amount input and Date input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00, 99999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(0.00)
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
        self.receipt_date.setMaximumDate(QDate.currentDate())
        self.receipt_date.setStyleSheet(self._get_input_style())
        self.receipt_date.dateChanged.connect(self._on_date_changed)
        # Add calendar icon if available
        try:
            self.receipt_date.setCalendarIcon(QIcon("📅"))
        except:
            pass
        grid.addWidget(self.receipt_date, row, 1)
        
        row += 1
        
        # Payment method label and Reference label
        method_label = QLabel("Received Via <span style='color:#EF4444'>*</span>")
        method_label.setTextFormat(Qt.RichText)
        method_label.setStyleSheet(self._get_label_style())
        grid.addWidget(method_label, row, 0)
        
        ref_label = QLabel("Reference No.")
        ref_label.setStyleSheet(self._get_label_style())
        grid.addWidget(ref_label, row, 1)
        
        row += 1
        
        # Payment method input and Reference input
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
        self.payment_method.currentIndexChanged.connect(self._on_payment_method_changed)
        grid.addWidget(self.payment_method, row, 0)
        
        self.reference_input = QLineEdit()
        self.reference_input.setMinimumHeight(45)
        self.reference_input.setStyleSheet(self._get_input_style())
        self._update_reference_placeholder()
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
        self.amount_input.setRange(0.0, 99999999.99)
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
        # Prevent future dates
        self.receipt_date.setMaximumDate(QDate.currentDate())
        self.receipt_date.setStyleSheet(self._get_input_style())
        self.receipt_date.dateChanged.connect(self._on_date_changed)
        # Add calendar icon if available
        try:
            self.receipt_date.setCalendarIcon(QIcon("📅"))
        except:
            pass
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
        footer.setFixedHeight(85)
        footer.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-top: 1px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(35, 15, 35, 15)
        layout.setSpacing(15)
        
        layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(130, 45)
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
        self.save_btn.setFixedSize(170, 45)
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
        return f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 13px; border: none;"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_party_completer_activated(self, text: str):
        """Handle party selection from the completer dropdown.
        Sets the text, shows party info, and updates UI.
        """
        try:
            if text and text.strip():
                # Extract party name from display text
                clean_text = text.strip()
                party_name = self.party_display_map.get(clean_text, clean_text)
                
                # Set just the party name in the combo box
                self.party_search.blockSignals(True)
                self.party_search.lineEdit().setText(party_name)
                self.party_search.blockSignals(False)
                
                # Show party info
                party_data = self.party_data_map.get(party_name)
                if party_data:
                    party_type = party_data.get('party_type', 'N/A')
                    phone = party_data.get('mobile', '')
                    info_text = f"📌 {party_type}"
                    if phone:
                        info_text += f"  •  📞 {phone}"
                    self.party_info.setText(info_text)
                    self.party_info.show()
                    
                    # Update border to success
                    self.party_search.setStyleSheet(self.party_search.styleSheet().replace(
                        f"border: 2px solid {BORDER}",
                        "border: 2px solid #10B981"
                    ))
                    
                    # Show payment history if exists
                    payment_history = self.duplicate_checker.get_payment_history(party_data.get('id'))
                    self.payment_history = payment_history
                    
                    # Update preview areas
                    self._update_invoice_combo()
                    self._update_outstanding_card()
                    self._update_allocation_area()
                    self._update_summary()
                    
                    # Keep focus on party search field
                    QTimer.singleShot(150, lambda: self.party_search.lineEdit().setFocus())
        except Exception as e:
            print(f"Party completer activation error: {e}")

    def _on_party_text_edited(self, text: str):
        """Handle text editing in party search - position dropdown and validate."""
        try:
            # Reset styling when editing
            if hasattr(self, 'party_search'):
                current_style = self.party_search.styleSheet()
                if "#10B981" in current_style or "#EF4444" in current_style:
                    self.party_search.setStyleSheet(current_style.replace(
                        "border: 2px solid #10B981", f"border: 2px solid {BORDER}"
                    ).replace(
                        "border: 2px solid #EF4444", f"border: 2px solid {BORDER}"
                    ))
            
            if text and len(text) >= 1:
                # Update highlight delegate with search text
                if hasattr(self, 'party_highlight_delegate'):
                    self.party_highlight_delegate.set_search_text(text)

                # Position popup after QCompleter finishes its internal positioning
                QTimer.singleShot(0, self._position_completer_popup)
        except Exception as e:
            print(f"Party text edited error: {e}")

    def _on_party_text_changed(self, text):
        """Handle party search text changes for validation."""
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
    
    def _setup_completer_positioning(self):
        """Setup completer to position correctly when showing."""
        try:
            if hasattr(self, 'party_completer'):
                popup = self.party_completer.popup()
                dialog_ref = self
                
                # Override setVisible because QCompleter uses this internally
                original_setVisible = popup.setVisible
                def custom_setVisible(visible):
                    original_setVisible(visible)
                    if visible:
                        dialog_ref._position_completer_popup()
                popup.setVisible = custom_setVisible
        except Exception as e:
            print(f"Setup completer positioning error: {e}")

    def _position_completer_popup(self):
        """Position the completer popup with dynamic screen-aware positioning."""
        try:
            if not hasattr(self, 'party_completer'):
                return
                
            popup = self.party_completer.popup()
            
            # Get the combobox position in global coordinates
            combo_rect = self.party_search.rect()
            global_pos = self.party_search.mapToGlobal(combo_rect.bottomLeft())
            
            # Set popup width
            popup_width = max(self.party_search.width(), 450)
            popup.setFixedWidth(popup_width)
            
            # Calculate position
            gap = 10
            y_pos = global_pos.y() + gap
            x_pos = global_pos.x()
            
            # Get screen geometry for bounds checking
            screen = QApplication.screenAt(global_pos)
            if screen:
                screen_geometry = screen.availableGeometry()
                popup_height = min(popup.sizeHint().height(), 400)
                
                # Check if popup would go below screen - position above instead
                if y_pos + popup_height > screen_geometry.bottom():
                    top_pos = self.party_search.mapToGlobal(combo_rect.topLeft())
                    y_pos = top_pos.y() - popup_height - gap
                
                # Check horizontal bounds
                if x_pos + popup_width > screen_geometry.right():
                    x_pos = screen_geometry.right() - popup_width - 10
                if x_pos < screen_geometry.left():
                    x_pos = screen_geometry.left() + 10
            
            popup.move(x_pos, y_pos)
        except Exception as e:
            print(f"Position completer popup error: {e}")
    
    def eventFilter(self, obj, event):
        """Handle keyboard events for party search dropdown.
        Opens QCompleter popup when down arrow key is pressed.
        """
        try:
            # Check if event is from party search (either combobox or its lineEdit)
            if hasattr(self, 'party_search'):
                is_party_search = (obj == self.party_search or obj == self.party_search.lineEdit())
                
                if is_party_search and event.type() == QEvent.KeyPress:
                    # Down arrow key: open dropdown menu
                    if event.key() == Qt.Key_Down:
                        if hasattr(self, 'party_completer'):
                            popup = self.party_completer.popup()
                            if popup and not popup.isVisible():
                                # Call custom showPopup which triggers completer
                                self.party_search.showPopup()
                                return True
                            # If popup is visible, let default behavior navigate the list
        except Exception as e:
            pass
        
        # Default event handling
        return super().eventFilter(obj, event)
    
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
        self.form_dirty = True
        self._update_summary()
        self._update_allocation_area()
    
    def _on_payment_method_changed(self):
        """Handle payment method change"""
        self.form_dirty = True
        self._update_reference_placeholder()
    
    def _update_reference_placeholder(self):
        """Update reference field placeholder based on payment method"""
        method = self.payment_method.currentData()
        placeholders = {
            'Cash': 'No reference needed',
            'Bank Transfer': 'Transaction ID / UTR',
            'UPI': 'UPI Reference Number',
            'Cheque': 'Cheque Number',
            'Card': 'Card Transaction ID'
        }
        placeholder = placeholders.get(method, 'Enter reference...')
        self.reference_input.setPlaceholderText(placeholder)
    
    def _on_date_changed(self, date):
        """Handle date change - warn for backdated receipts"""
        self.form_dirty = True
        
        today = QDate.currentDate()
        if date > today:
            QMessageBox.warning(self, "Invalid Date", "Receipt date cannot be in the future")
            self.receipt_date.setDate(today)
            return
        
        if date < today.addDays(-7):  # Warn if more than 7 days old
            # Show tooltip warning
            self.receipt_date.setToolTip(f"⚠️ Receipt dated {date.toString('dd-MM-yyyy')} is {(today - date).days} days old")
    
    def _update_outstanding_card(self):
        """Update the outstanding amount card with color coding"""
        party = self._get_selected_party()
        
        if not party:
            self.outstanding_amount.setText("₹0.00")
            self.outstanding_label.setText("Select a customer")
            self.outstanding_card.setStyleSheet(f"""
                QFrame {{
                    background: {BACKGROUND};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                }}
            """)
            self.outstanding_amount.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
            return
        
        # Calculate total outstanding for this customer
        party_id = party.get('id')
        total_outstanding = 0
        invoice_count = 0
        
        # Get all payments for this party
        paid_amounts = {}
        try:
            payments = db._query("SELECT invoice_id, SUM(amount) as total FROM payments WHERE party_id = ? GROUP BY invoice_id", (party_id,))
            for p in payments:
                paid_amounts[p.get('invoice_id')] = p.get('total', 0)
        except Exception as e:
            print(f"Error fetching payments: {e}")
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            
            inv_id = inv.get('id')
            grand_total = float(inv.get('grand_total', 0) or 0)
            amount_paid = float(paid_amounts.get(inv_id, 0))
            balance_due = grand_total - amount_paid
            
            # Skip if fully paid or no amount
            if balance_due <= 0 or grand_total == 0:
                continue
            
            # Skip draft invoices with zero amount
            status = inv.get('status', 'outstanding').lower()
            if status == 'draft' and grand_total == 0:
                continue
            
            total_outstanding += balance_due
            invoice_count += 1
        
        self.outstanding_amount.setText(f"₹{total_outstanding:,.2f}")
        self.outstanding_label.setText(f"Total Outstanding ({invoice_count} invoices)")
        
        # Update card color based on amount range
        if total_outstanding > 0:
            # Danger for high amounts, warning for medium, success for none
            if total_outstanding > 100000:
                color = DANGER
                bg_opacity = "40"
            elif total_outstanding > 50000:
                color = WARNING
                bg_opacity = "40"
            else:
                color = PRIMARY
                bg_opacity = "40"
            
            self.outstanding_card.setStyleSheet(f"""
                QFrame {{
                    background: {color}15;
                    border: 1px solid {color}{bg_opacity};
                    border-radius: 8px;
                }}
            """)
            self.outstanding_amount.setStyleSheet(f"color: {color}; border: none;")
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
        
        # Preserve selected invoice if it exists
        selected_invoice_backup = getattr(self, 'selected_invoice', None)
        
        # Reset invoice_cards list (but not selected_invoice)
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
        
        # Restore selected invoice after mode display is set up
        if selected_invoice_backup:
            self.selected_invoice = selected_invoice_backup
    
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
        
        # Get all payments for this party
        paid_amounts = {}
        try:
            payments = db._query("SELECT invoice_id, SUM(amount) as total FROM payments WHERE party_id = ? GROUP BY invoice_id", (party_id,))
            for p in payments:
                paid_amounts[p.get('invoice_id')] = p.get('total', 0)
        except Exception as e:
            print(f"Error fetching payments: {e}")
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            
            inv_id = inv.get('id')
            grand_total = float(inv.get('grand_total', 0) or 0)
            amount_paid = float(paid_amounts.get(inv_id, 0))
            balance_due = grand_total - amount_paid
            
            # Skip if fully paid or no amount
            if balance_due <= 0 or grand_total == 0:
                continue
            
            # Skip draft invoices with zero amount
            status = inv.get('status', 'outstanding').lower()
            if status == 'draft' and grand_total == 0:
                continue
            
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
        scroll.setMinimumHeight(200)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(6)
        scroll_layout.setContentsMargins(0, 0, 5, 0)
        
        self.invoice_cards = []  # Store references to invoice cards
        
        for inv in outstanding_invoices:
            card = self._create_invoice_row_for_bill_to_bill(inv)
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
        """Create a clickable invoice card with detailed information"""
        card = QFrame()
        card.setProperty("invoice", invoice)
        card.setProperty("selected", False)
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(75)
        
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
        layout.setSpacing(12)
        
        # Left side - Invoice info
        left = QVBoxLayout()
        left.setSpacing(3)
        
        inv_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        inv_date = invoice.get('date', 'N/A')
        inv_type = invoice.get('invoice_type', 'GST')  # GST or Non-GST
        
        title = QLabel(f"📄 {inv_no}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        left.addWidget(title)
        
        details_text = f"Date: {inv_date}  •  Type: {inv_type}"
        date_label = QLabel(details_text)
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
    
    def _create_invoice_row_for_bill_to_bill(self, invoice):
        """Create a simple invoice row for bill-to-bill selection (FIFO format)"""
        row = QFrame()
        row.setProperty("invoice", invoice)
        row.setProperty("selected", False)
        row.setCursor(Qt.PointingHandCursor)
        row.setFixedHeight(36)
        
        row.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
            QFrame:hover {{
                border-color: {PRIMARY};
                background: {PRIMARY}08;
            }}
            QLabel {{ border: none; }}
        """)
        
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 4, 10, 4)
        row_layout.setSpacing(10)
        
        inv_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        inv_date = invoice.get('date', 'N/A')
        balance_due = invoice.get('balance_due', invoice.get('due_amount', invoice.get('grand_total', 0)))
        
        inv_label = QLabel(f"{inv_no}")
        inv_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 12px;")
        inv_label.setMinimumWidth(120)
        row_layout.addWidget(inv_label)
        
        date_label = QLabel(f"{inv_date}")
        date_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        date_label.setMinimumWidth(90)
        row_layout.addWidget(date_label)
        
        row_layout.addStretch()
        
        due_label = QLabel(f"₹{balance_due:,.2f}")
        due_label.setStyleSheet(f"color: {DANGER}; font-weight: bold; font-size: 12px;")
        due_label.setMinimumWidth(100)
        due_label.setAlignment(Qt.AlignRight)
        row_layout.addWidget(due_label)
        
        # Make row clickable
        row.mousePressEvent = lambda e, r=row, inv=invoice: self._on_invoice_card_clicked(r, inv)
        
        return row
    
    def _on_invoice_card_clicked(self, card, invoice):
        """Handle invoice card click - show detailed breakdown"""
        # Deselect all cards
        for c in self.invoice_cards:
            c.setProperty("selected", False)
            # Use proper styling for FIFO rows (1px border, 36px height)
            c.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
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
                border-radius: 6px;
            }}
            QLabel {{ border: none; }}
        """)
        
        # Store selected invoice
        self.selected_invoice = invoice
        
        # Create detailed breakdown card (FIFO style)
        inv_no = invoice.get('invoice_no', 'N/A')
        due = invoice.get('due_amount', invoice.get('grand_total', 0))
        inv_date = invoice.get('date', 'N/A')
        inv_type = invoice.get('invoice_type', 'GST')
        
        # Create breakdown widget
        breakdown_widget = QFrame()
        breakdown_widget.setStyleSheet(f"""
            QFrame {{
                background: {SUCCESS}15;
                border: 1px solid {SUCCESS};
                border-radius: 8px;
            }}
            QLabel {{ border: none; }}
        """)
        
        breakdown_layout = QVBoxLayout(breakdown_widget)
        breakdown_layout.setContentsMargins(12, 12, 12, 12)
        breakdown_layout.setSpacing(6)
        
        # Header row
        header = QLabel(f"📄 {inv_no}")
        header.setFont(QFont("Arial", 13, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        breakdown_layout.addWidget(header)
        
        # Details rows
        details_layout = QGridLayout()
        details_layout.setSpacing(8)
        
        date_label = QLabel(f"<b>Date:</b> {inv_date}")
        date_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; border: none;")
        details_layout.addWidget(date_label, 0, 0)
        
        type_label = QLabel(f"<b>Type:</b> {inv_type}")
        type_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; border: none;")
        details_layout.addWidget(type_label, 0, 1)
        
        due_label = QLabel(f"<b>Due Amount:</b> ₹{due:,.2f}")
        due_label.setStyleSheet(f"color: {DANGER}; font-size: 12px; font-weight: bold; border: none;")
        details_layout.addWidget(due_label, 1, 0, 1, 2)
        
        breakdown_layout.addLayout(details_layout)
        
        # Update label to be the breakdown widget
        if hasattr(self, 'invoice_detail_label') and self.invoice_detail_label.parent() is not None:
            self.invoice_detail_label.hide()
        
        # Add breakdown to allocation layout if not already there
        if not hasattr(self, 'invoice_breakdown_widget') or self.invoice_breakdown_widget is None:
            self.invoice_breakdown_widget = breakdown_widget
            self.allocation_layout.insertWidget(self.allocation_layout.count() - 1, self.invoice_breakdown_widget)
        else:
            # Check if existing widget is still valid (not deleted)
            try:
                # Try to access the layout - will fail if widget is deleted
                existing_layout = self.invoice_breakdown_widget.layout()
                
                if existing_layout is not None:
                    # Clear existing layout
                    while existing_layout.count():
                        item = existing_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    # Layout doesn't exist, create new one
                    existing_layout = QVBoxLayout(self.invoice_breakdown_widget)
                
                # Update the layout with new data
                existing_layout.setContentsMargins(12, 12, 12, 12)
                existing_layout.setSpacing(6)
                
                header = QLabel(f"📄 {inv_no}")
                header.setFont(QFont("Arial", 13, QFont.Bold))
                header.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
                existing_layout.addWidget(header)
                
                details_layout_new = QGridLayout()
                details_layout_new.setSpacing(8)
                
                date_label = QLabel(f"<b>Date:</b> {inv_date}")
                date_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; border: none;")
                details_layout_new.addWidget(date_label, 0, 0)
                
                type_label = QLabel(f"<b>Type:</b> {inv_type}")
                type_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; border: none;")
                details_layout_new.addWidget(type_label, 0, 1)
                
                due_label = QLabel(f"<b>Due Amount:</b> ₹{due:,.2f}")
                due_label.setStyleSheet(f"color: {DANGER}; font-size: 12px; font-weight: bold; border: none;")
                details_layout_new.addWidget(due_label, 1, 0, 1, 2)
                
                existing_layout.addLayout(details_layout_new)
                
            except RuntimeError:
                # Widget was deleted, create a new one
                self.invoice_breakdown_widget = breakdown_widget
                if self.invoice_breakdown_widget.parent() is None:
                    self.allocation_layout.insertWidget(self.allocation_layout.count() - 1, self.invoice_breakdown_widget)
        
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
        
        # Get all payments for this party
        paid_amounts = {}
        try:
            payments = db._query("SELECT invoice_id, SUM(amount) as total FROM payments WHERE party_id = ? GROUP BY invoice_id", (party_id,))
            for p in payments:
                paid_amounts[p.get('invoice_id')] = p.get('total', 0)
        except Exception as e:
            print(f"Error fetching payments: {e}")
        
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            
            inv_id = inv.get('id')
            grand_total = float(inv.get('grand_total', 0) or 0)
            amount_paid = float(paid_amounts.get(inv_id, 0))
            balance_due = grand_total - amount_paid
            
            # Skip if fully paid or no amount
            if balance_due <= 0 or grand_total == 0:
                continue
            
            # Skip draft invoices with zero amount
            status = inv.get('status', 'outstanding').lower()
            if status == 'draft' and grand_total == 0:
                continue
            
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
            balance_due = inv.get('balance_due', inv.get('due_amount', inv.get('grand_total', 0)))
            inv_no = inv.get('invoice_no', f"INV-{inv.get('id', 0):03d}")
            inv_date = inv.get('date', 'N/A')
            
            if remaining <= 0:
                alloc_amount = 0
                status = "Pending"
                status_color = TEXT_SECONDARY
            elif remaining >= balance_due:
                alloc_amount = balance_due
                remaining -= balance_due
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
            
            due_label = QLabel(f"₹{balance_due:,.0f}")
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
        
        # Get all payments for this party to calculate actual balance
        paid_amounts = {}
        try:
            payments = db._query("SELECT invoice_id, SUM(amount) as total FROM payments WHERE party_id = ? GROUP BY invoice_id", (party_id,))
            for p in payments:
                paid_amounts[p.get('invoice_id')] = p.get('total', 0)
        except Exception as e:
            print(f"Error fetching payments: {e}")
        
        # Filter sales invoices for this customer with outstanding balance
        for inv in self.invoices:
            if inv.get('party_id') != party_id:
                continue
            
            inv_id = inv.get('id')
            grand_total = float(inv.get('grand_total', 0) or 0)
            amount_paid = float(paid_amounts.get(inv_id, 0))
            balance_due = grand_total - amount_paid
            
            # Skip if fully paid
            if balance_due <= 0:
                continue
            
            # Skip draft invoices unless they have amount
            status = inv.get('status', 'outstanding').lower()
            if status == 'draft' and grand_total == 0:
                continue
            
            inv_no = inv.get('invoice_no', f"INV-{inv.get('id', 0):03d}")
            icon = "📄" if status == 'outstanding' else "⚠️" if status in ('overdue', 'final') else "✓"
            
            display = f"{icon} {inv_no} — ₹{balance_due:,.2f} due"
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
                balance_due = invoice.get('balance_due', invoice.get('due_amount', 0))
                remaining = max(0, balance_due - amount)
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
        """Get currently selected party data from the combo"""
        if hasattr(self.party_search, 'currentText'):
            name = self.party_search.currentText().strip()
        else:
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
                    if hasattr(self.party_search, 'setCurrentText'):
                        self.party_search.setCurrentText(party.get('name', ''))
                    else:
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
    
    def closeEvent(self, event):
        """Check for unsaved changes before closing"""
        if self.form_dirty and not self.receipt_data:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()
    
    def _update_invoice_status(self, invoice_id, amount_paid):
        """Update invoice status to 'paid' or 'partial paid' based on payment amount"""
        if not invoice_id:
            return
        
        try:
            # Get the invoice details
            invoice = None
            for inv in self.invoices:
                if inv.get('id') == invoice_id:
                    invoice = inv
                    break
            
            if not invoice:
                return
            
            # Calculate outstanding amount
            grand_total = invoice.get('grand_total', 0)
            due_amount = invoice.get('due_amount', grand_total)
            remaining_due = max(0, due_amount - amount_paid)
            
            # Determine status
            if remaining_due <= 0:
                new_status = 'Paid'
            elif remaining_due < due_amount:
                new_status = 'Partial paid'
            else:
                new_status = 'Outstanding'
            
            # Update the invoice in database
            invoice_data = invoice.copy()
            invoice_data['status'] = new_status
            # Calculate new balance_due
            invoice_data['balance_due'] = remaining_due
            print(f"Updated invoice {invoice_id}: {new_status}, Balance Due: ₹{remaining_due:,.2f} {invoice_data}")
            db.update_invoice(invoice_data)
            
        except Exception as e:
            print(f"Warning: Could not update invoice status: {e}")
    
    def _save_receipt(self):
        """Save receipt to database with comprehensive validation"""
        # ===== VALIDATION PHASE =====
        party = self._get_selected_party()
        amount = self.amount_input.value()
        receipt_date = self.receipt_date.date()
        method = self.payment_method.currentData()
        reference = self.reference_input.text().strip()
        
        # Comprehensive validation
        if not self.validator.validate_all(party, amount, receipt_date, method, reference):
            # Show first error
            errors = self.validator.errors
            error_message = "\n".join([f"❌ {v}" for v in errors.values()])
            UIErrorHandler.show_error("Validation Failed", f"Please fix the following errors:\n\n{error_message}")
            return
        
        # Validate party selection
        if not party:
            # Visual feedback
            self.party_search.setStyleSheet(self._get_input_style() + f"""
                QComboBox {{
                    border: 2px solid {DANGER} !important;
                }}
            """)
            UIErrorHandler.show_validation_error("Validation Error", ["Please select a valid customer!"])
            self.party_search.setFocus()
            return
        else:
            # Reset styling
            self.party_search.setStyleSheet(self._get_input_style())
        
        # ===== DUPLICATE DETECTION =====
        
        # Check for duplicate reference number (if provided)
        if reference:
            exclude_id = self.receipt_data.get('id') if self.receipt_data else None
            if self.duplicate_checker.check_duplicate_reference(reference, exclude_id):
                if not UIErrorHandler.ask_confirmation(
                    "Duplicate Reference",
                    f"Reference '{reference}' already exists!\n\n"
                    f"Do you want to use this reference anyway?"
                ):
                    self.reference_input.setFocus()
                    return
        
        # Check for duplicate payment (same amount on same date)
        if self.duplicate_checker.check_duplicate_payment(party.get('id'), amount, receipt_date.toString("yyyy-MM-dd")):
            if not UIErrorHandler.ask_confirmation(
                "Possible Duplicate Payment",
                f"A payment of ₹{amount:,.2f} for {party.get('name')} "
                f"on {receipt_date.toString('dd-MM-yyyy')} already exists!\n\n"
                f"Do you want to continue?"
            ):
                return
        
        # ===== OVER-PAYMENT CONFIRMATION =====
        
        invoice = None
        if self.settlement_mode == "bill_to_bill":
            invoice = getattr(self, 'selected_invoice', None)
            if invoice:
                due = invoice.get('due_amount', invoice.get('grand_total', 0))
                if amount > due:
                    if not UIErrorHandler.ask_confirmation(
                        "Excess Amount",
                        f"Receipt (₹{amount:,.2f}) exceeds due amount (₹{due:,.2f}).\n\nContinue?"
                    ):
                        return
            else:
                # No invoice selected in bill-to-bill mode
                if not UIErrorHandler.ask_confirmation(
                    "No Invoice Selected",
                    "No invoice selected. Record as Direct Receipt?"
                ):
                    return
        
        elif self.settlement_mode == "fifo":
            # Confirm FIFO allocation
            if hasattr(self, 'fifo_allocations') and self.fifo_allocations:
                alloc_count = len([a for a in self.fifo_allocations if a['amount'] > 0])
                if not UIErrorHandler.ask_confirmation(
                    "Confirm FIFO Settlement",
                    f"This will settle {alloc_count} invoice(s) using FIFO method.\n\nProceed?"
                ):
                    return
        
        # Prepare notes
        receipt_notes = self.notes_input.toPlainText().strip()
        mode_label = {'bill_to_bill': 'Bill-to-Bill', 'fifo': 'FIFO', 'direct': 'Direct'}
        settlement_info = f"[{mode_label.get(self.settlement_mode, 'Unknown')}]"
        
        # Add reference to notes if available
        if reference:
            settlement_info = f"{settlement_info} [Ref: {reference}]"
        
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
                    # Update invoice status if bill-to-bill
                    if self.settlement_mode == "bill_to_bill" and invoice:
                        self._update_invoice_status(invoice['id'], amount)
                    msg = "Receipt updated successfully!"
                else:
                    payment_id = f"REC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    db.add_payment(
                        payment_id=payment_id,
                        party_id=party['id'],
                        amount=amount,
                        date=receipt_date,
                        mode=method,
                        invoice_id=invoice['id'] if invoice else None,
                        notes=receipt_notes,
                        payment_type='RECEIPT'
                    )
                    # Update invoice status if bill-to-bill
                    if self.settlement_mode == "bill_to_bill" and invoice:
                        self._update_invoice_status(invoice['id'], amount)
                    msg = "Receipt recorded successfully!"
            
            QMessageBox.information(self, "Success", f"✓ {msg}")
            self.form_dirty = False
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
                invoice_id=invoice['id'],
                notes=alloc_notes,
                payment_type='RECEIPT'
            )
            # Update invoice status after FIFO allocation
            self._update_invoice_status(invoice['id'], alloc_amount)
        
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
                invoice_id=None,
                notes=advance_notes,
                payment_type='RECEIPT'
            )
