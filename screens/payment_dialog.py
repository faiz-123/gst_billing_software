"""
Payment Dialog - Record and manage payments with enhanced UI and functionality
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSplitter, QGroupBox,
    QAbstractItemView, QMenu, QAction, QCompleter, QButtonGroup, QRadioButton,
    QApplication, QDesktopWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QCursor

from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER, get_title_font
)
from database import db
from .party_selector import PartySelector

class PaymentDialog(QDialog):
    """Enhanced dialog for recording payments with modern UI"""
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.parties = []
        self.invoices = []
        self.filtering_in_progress = False  # Flag to prevent recursion
        
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
        
        # Dynamic window sizing - make it resizable and larger
        self.setMinimumSize(1200, 900)  # Set minimum size
        self.resize(1400, 1000)  # Initial size (larger than before)
        
        # Center the window on screen
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
        
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
        
        # Initialize all components after everything is created
        self.initialize_form()
    
    def setup_title_section(self):
        """Setup enhanced title section with compact layout"""
        title_container = QFrame()
        title_container.setFixedHeight(80)
        title_container.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY};
                border-radius: 8px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_container)
        # title_layout.setContentsMargins(12, 4, 12, 4)  # Significantly reduced vertical margins
        
        # Main title
        title_text = "💳 Record New Payment" if not self.payment_data else "📝 Edit Payment"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))  # Smaller font for reduced height
        self.title_label.setStyleSheet("color: white; border: none;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        # Payment ID for editing
        if self.payment_data:
            payment_id = self.payment_data.get('id', 'N/A')
            id_label = QLabel(f"Payment #{payment_id}")
            id_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 11px; border: none;")
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
        
        # Set proportions - give more space to the payment details form with larger window
        content_splitter.setSizes([800, 550])  # Increased from [500, 350] to utilize extra space
        
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
        layout.setContentsMargins(25, 20, 25, 20)  # Increased margins for larger window
        layout.setSpacing(25)  # Increased spacing for better layout
        
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
        form_layout.setSpacing(20)  # Increased spacing for larger window
        form_layout.setHorizontalSpacing(20)  # Increased horizontal spacing
        
        # Enhanced input styling with larger dimensions for bigger window
        input_style = f"""
            QComboBox, QDoubleSpinBox, QLineEdit, QDateEdit, QTextEdit {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 12px 15px;  /* Increased padding */
                background: {WHITE};
                font-size: 15px;  /* Slightly larger font */
                color: {TEXT_PRIMARY};
                min-height: 20px;  /* Increased height */
                max-height: 40px;  /* Increased max height */
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
    
        # Party selection with PartySelector (similar to invoice)
        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search and select party...")
        
        # Create party data map for lookup
        self.party_data_map = {}
        for party in self.parties:
            name = party.get('name', '').strip()
            if name:
                self.party_data_map[name] = party
        
        # Connect events for PartySelector functionality
        self.party_search.returnPressed.connect(self.open_party_selector)
        self.party_search.textChanged.connect(self.on_party_search_text_changed)
        self.party_search.setStyleSheet(input_style)
        
        form_layout.addRow("🏢 Select Party:", self.party_search)
        
        # Invoice reference with enhanced selection
        self.invoice_combo = QComboBox()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        self.invoice_combo.setStyleSheet(input_style)
        # Fix: Use currentIndexChanged for better functionality
        self.invoice_combo.currentIndexChanged.connect(self.on_invoice_changed)
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
        
        # Import calendar styling
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
        self.notes_input.setFixedHeight(100)  # Increased height for larger window
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
        frame.setFixedWidth(450)  # Set a fixed width for the summary section
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
        button_container.setFixedHeight(80)  # Reduced height
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
    
    def initialize_form(self):
        """Initialize form components after all widgets are created"""
        # Initialize invoice combo (will be empty initially)
        self.update_invoice_combo()
        
        # Initialize outstanding display
        self.update_outstanding_display()
        
        # Initialize summary
        self.update_summary()
    
    def open_party_selector(self):
        """Open PartySelector dialog when user presses Enter in party search"""
        try:
            selected = self._open_party_selector_dialog()
            if selected:
                self.party_search.setText(selected)
                self.on_party_selection_changed()
        except Exception as e:
            print(f"Party selector failed: {e}")
    
    def _open_party_selector_dialog(self, prefill_text: str = None):
        """Create, size, position and open the PartySelector below the input.
        Returns the selected name if accepted, else None.
        """
        dlg = PartySelector(self.parties, self)
        # Prefill search
        try:
            current_text = prefill_text or self.party_search.text()
            if current_text:
                dlg.search.setText(current_text)
                dlg.search.setCursorPosition(len(current_text))
        except Exception:
            pass
        # Size and position
        try:
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
            dlg.move(int(x), int(y))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec_() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None
    
    def on_party_search_text_changed(self, text):
        """Handle party search text changes - open selector when typing"""
        # If text is being typed and not empty, open the party selector
        if text.strip() and len(text.strip()) >= 1:  # Open when user types at least 1 character
            # Use QTimer to delay the opening slightly to avoid opening on every keystroke
            if not hasattr(self, '_party_search_timer'):
                self._party_search_timer = QTimer()
                self._party_search_timer.setSingleShot(True)
                self._party_search_timer.timeout.connect(lambda: self.open_party_selector_with_text(text))
            
            self._party_search_timer.stop()  # Stop any existing timer
            self._party_search_timer.start(300)  # Wait 300ms before opening
        
        # Update party selection when text matches a known party
        if text.strip() in self.party_data_map:
            self.on_party_selection_changed()
    
    def open_party_selector_with_text(self, search_text):
        """Open PartySelector with prefilled text"""
        try:
            # Only open if the search text is still current
            current_text = self.party_search.text().strip()
            if current_text and current_text == search_text.strip():
                selected = self._open_party_selector_dialog(prefill_text=current_text)
                if selected:
                    self.party_search.setText(selected)
                    self.on_party_selection_changed()
        except Exception as e:
            print(f"Party selector failed: {e}")
    
    def on_party_selection_changed(self):
        """Handle party selection change"""
        self.update_invoice_combo()
        self.update_outstanding_display()
        self.update_summary()
    
    def get_selected_party_data(self):
        """Get the currently selected party data"""
        party_name = self.party_search.text().strip()
        return self.party_data_map.get(party_name)
    
    def on_payment_type_changed(self):
        """Handle payment type change with visual feedback"""
        if hasattr(self, 'invoice_combo'):  # Only update if invoice combo exists
            self.update_invoice_combo()
        if hasattr(self, 'summary_content'):  # Only update if summary content exists
            self.update_summary()
        
        # Update UI colors based on type
        if hasattr(self, 'title_label'):  # Only update if title label exists
            if self.received_radio.isChecked():
                self.title_label.setText("💰 Record Payment Received")
            else:
                self.title_label.setText("💸 Record Payment Made")
        
        # Clear party selection when payment type changes
        if hasattr(self, 'party_search'):
            self.party_search.clear()
    
    def update_invoice_combo(self):
        """Update invoice combo with enhanced filtering and display"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("💰 Direct Payment (No Invoice)", None)
        
        party_data = self.get_selected_party_data()
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
        if hasattr(self, 'outstanding_label'):  # Only update if outstanding label exists
            self.update_outstanding_display()
        if hasattr(self, 'summary_content'):  # Only update if summary content exists
            self.update_summary()
        
        # Auto-fill amount with outstanding amount
        if hasattr(self, 'amount_input'):  # Only update if amount input exists
            invoice_data = self.invoice_combo.currentData()
            if invoice_data:
                due_amount = invoice_data.get('due_amount', invoice_data.get('grand_total', 0))
                if due_amount > 0:
                    self.amount_input.setValue(due_amount)
    
    def update_outstanding_display(self):
        """Update outstanding amount display with enhanced info"""
        party_data = self.get_selected_party_data()
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
        party_data = self.get_selected_party_data()
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
        
        # Set party by finding the party name and setting it in the search field
        party_id = self.payment_data.get('party_id')
        if party_id:
            # Find party by ID and set the name in search field
            for party in self.parties:
                if party.get('id') == party_id:
                    self.party_search.setText(party['name'])
                    self.on_party_selection_changed()
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
        party_data = self.get_selected_party_data()
        if not party_data:
            QMessageBox.warning(self, "Validation Error", "🏢 Please select a valid party!")
            self.party_search.setFocus()
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
                # Generate unique payment ID
                import datetime
                payment_id = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Call add_payment with individual parameters as expected
                db.add_payment(
                    payment_id=payment_id,
                    party_id=payment_data['party_id'],
                    amount=payment_data['amount'],
                    date=payment_data['date'],
                    mode=payment_data['method'],
                    invoice_id=payment_data.get('invoice_id'),
                    notes=payment_data['notes']
                )
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
