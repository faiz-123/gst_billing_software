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
from .payment_dialog import PaymentDialog
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER, get_title_font
)
from database import db

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
        self.payments_table.setColumnWidth(2, 250)  # Party
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
                amount_item.setForeground(QColor(SUCCESS))
            else:
                amount_item.setForeground(QColor(DANGER))
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
        # actions_container = QVBoxLayout()
        # actions_label = QLabel("⚡ Actions:")
        # actions_label.setStyleSheet(label_style)
        # actions_container.addWidget(actions_label)
                
        # actions_buttons = QHBoxLayout()
        # actions_buttons.setSpacing(8)
        
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
        filters_row1.addWidget(clear_btn)
        
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
        filters_row1.addWidget(refresh_btn)
        
        # actions_container.addLayout(actions_buttons)
        # filters_row2.addLayout(actions_container)
        
        # filters_row2.addStretch()
        
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
        self.payments_table.setColumnWidth(2, 250)  # Party
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
                type_item.setForeground(QColor(SUCCESS))
            else:
                type_item.setForeground(QColor(DANGER))
            self.payments_table.setItem(row, 1, type_item)
            
            # Party
            self.payments_table.setItem(row, 2, self.payments_table.create_item(payment.get('party_name', 'N/A')))
            
            # Amount with color coding
            amount = payment['amount']
            amount_text = f"₹{amount:,.2f}"
            amount_item = self.payments_table.create_item(amount_text)
            if payment_type == "Payment Received":
                amount_item.setForeground(QColor(SUCCESS))
            else:
                amount_item.setForeground(QColor(DANGER))
            self.payments_table.setItem(row, 3, amount_item)
            
            # Method
            self.payments_table.setItem(row, 4, self.payments_table.create_item(payment.get('method', 'N/A')))
            
            # Reference
            self.payments_table.setItem(row, 5, self.payments_table.create_item(payment.get('reference', 'N/A')))
            
            # Status
            status = payment.get('status', 'Completed')
            status_item = self.payments_table.create_item(status)
            if status == 'Completed':
                status_item.setForeground(QColor(SUCCESS))
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
