"""
Payments Screen - Modern, Responsive Payment Management Interface
Matching the design patterns from invoices.py
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QAbstractItemView, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from .base_screen import BaseScreen
from .payment_dialog import PaymentDialog
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, PRIMARY_HOVER
)
from database import db


class PaymentsScreen(BaseScreen):
    """Modern, responsive Payments screen matching invoices.py design"""
    
    def __init__(self):
        super().__init__("💳 Payments & Transactions")
        self.all_payments_data = []
        self.current_page = 1
        self._setup_screen()
        self._load_data()
    
    def _setup_screen(self):
        """Setup the complete screen UI"""
        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header section with search and actions
        self._setup_header_section(content_layout)
        
        # Stats cards row
        self._setup_stats_section(content_layout)
        
        # Filters section
        self._setup_filters_section(content_layout)
        
        # Table section
        self._setup_table_section(content_layout)
        
        scroll_area.setWidget(content_widget)
        self.add_content(scroll_area)
    
    def _setup_header_section(self, parent_layout):
        """Setup header with search and action buttons"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(16)
        
        # Search box with icon
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QFrame:focus-within {{
                border-color: {PRIMARY};
            }}
        """)
        search_frame.setMinimumWidth(250)
        search_frame.setMaximumWidth(400)
        search_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 8, 12, 8)
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 16px;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search payments...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {TEXT_PRIMARY};
                padding: 4px 0;
            }}
        """)
        self.search_input.textChanged.connect(self._filter_payments)
        search_layout.addWidget(self.search_input)
        
        header_layout.addWidget(search_frame)
        header_layout.addStretch()
        
        # Action buttons
        buttons_data = [
            ("📤 Export", "secondary", self._export_payments),
            ("💳 Record Payment", "primary", self._record_payment)
        ]
        
        for text, style, callback in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            
            if style == "primary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {PRIMARY};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 600;
                        padding: 8px 20px;
                    }}
                    QPushButton:hover {{
                        background: {PRIMARY_HOVER};
                    }}
                    QPushButton:pressed {{
                        background: #1D4ED8;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {WHITE};
                        color: {TEXT_PRIMARY};
                        border: 1px solid {BORDER};
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: {BACKGROUND};
                        border-color: {PRIMARY};
                        color: {PRIMARY};
                    }}
                """)
            
            header_layout.addWidget(btn)
        
        parent_layout.addWidget(header_frame)
    
    def _setup_stats_section(self, parent_layout):
        """Setup statistics cards with responsive grid"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent; border: none;")
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        
        # Statistics cards data
        stats_data = [
            ("💰", "Total Received", "₹0", SUCCESS, "total_received_label"),
            ("💸", "Total Paid", "₹0", DANGER, "total_paid_label"),
            ("📋", "Total Payments", "0", PRIMARY, "total_count_label"),
            ("📅", "This Month", "₹0", WARNING, "month_total_label")
        ]
        
        for icon, label_text, value, color, attr_name in stats_data:
            card = self._create_stat_card(icon, label_text, value, color)
            setattr(self, attr_name, card.findChild(QLabel, "value_label"))
            stats_layout.addWidget(card)
        
        parent_layout.addWidget(stats_frame)
    
    def _create_stat_card(self, icon, label_text, value, color):
        """Create modern statistics card"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(80)
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                border-color: {color};
                background: #FAFBFC;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}20;
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px; border: none;")
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container)
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(4)
        
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            border: none;
        """)
        text_container.addWidget(label_widget)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 22px;
            font-weight: 700;
            border: none;
        """)
        text_container.addWidget(value_label)
        
        layout.addLayout(text_container)
        layout.addStretch()
        
        return card
    
    def _setup_filters_section(self, parent_layout):
        """Setup responsive filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        filters_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(16, 12, 16, 12)
        filters_layout.setSpacing(16)
        
        # Filter label
        filter_label = QLabel("🎯 Filters")
        filter_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 600;
            border: none;
        """)
        filters_layout.addWidget(filter_label)
        
        # Add separator
        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setFixedHeight(30)
        separator.setStyleSheet(f"background: {BORDER};")
        filters_layout.addWidget(separator)
        
        # Filter controls
        combo_style = f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                padding-right: 30px;
                background: {BACKGROUND};
                font-size: 13px;
                color: {TEXT_PRIMARY};
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {TEXT_SECONDARY};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {BORDER};
                background: {WHITE};
                selection-background-color: {PRIMARY};
                selection-color: white;
                outline: none;
            }}
        """
        
        filter_controls = [
            ("Type", ["All Types", "Payment Received", "Payment Made"], "type_filter"),
            ("Method", ["All Methods", "Cash", "Bank Transfer", "UPI", "Cheque", "Credit Card", "Debit Card", "Net Banking", "Other"], "method_filter"),
            ("Period", ["All Time", "Today", "This Week", "This Month", "This Year"], "period_filter"),
            ("Status", ["All Status", "Completed", "Pending", "Failed"], "status_filter")
        ]
        
        for label_text, items, attr_name in filter_controls:
            # Container for label + combo
            filter_container = QVBoxLayout()
            filter_container.setSpacing(4)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 500;
                border: none;
            """)
            filter_container.addWidget(label)
            
            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedHeight(32)
            combo.setStyleSheet(combo_style)
            combo.currentTextChanged.connect(self._filter_payments)
            setattr(self, attr_name, combo)
            filter_container.addWidget(combo)
            
            filters_layout.addLayout(filter_container)
        
        filters_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Refresh Data")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: white;
                border-color: {PRIMARY};
            }}
        """)
        refresh_btn.clicked.connect(self._load_data)
        filters_layout.addWidget(refresh_btn)
        
        # Clear filters button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(32)
        clear_btn.setToolTip("Clear All Filters")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 13px;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                color: {DANGER};
            }}
        """)
        clear_btn.clicked.connect(self._clear_filters)
        filters_layout.addWidget(clear_btn)
        
        parent_layout.addWidget(filters_frame)
    
    def _setup_table_section(self, parent_layout):
        """Setup responsive table with pagination"""
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Table header
        table_header = QFrame()
        table_header.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: none;
                border-bottom: 1px solid {BORDER};
                border-radius: 12px 12px 0 0;
            }}
        """)
        
        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        table_title = QLabel("💳 Payment Transactions")
        table_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 600;
            border: none;
        """)
        header_layout.addWidget(table_title)
        header_layout.addStretch()
        
        # Items per page
        items_label = QLabel("Show:")
        items_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; border: none;")
        header_layout.addWidget(items_label)
        
        self.items_per_page = QComboBox()
        self.items_per_page.addItems(["25", "50", "100", "200"])
        self.items_per_page.setCurrentText("50")
        self.items_per_page.setFixedWidth(70)
        self.items_per_page.setFixedHeight(28)
        self.items_per_page.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                background: {WHITE};
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.items_per_page.currentTextChanged.connect(self._load_data)
        header_layout.addWidget(self.items_per_page)
        
        table_layout.addWidget(table_header)
        
        # Create table
        headers = ["Date", "Type", "Party", "Amount", "Method", "Reference", "Status", "Actions"]
        self.payments_table = QTableWidget(0, len(headers))
        self.payments_table.setHorizontalHeaderLabels(headers)
        
        # Table styling
        self.payments_table.setStyleSheet(f"""
            QTableWidget {{
                background: {WHITE};
                border: none;
                gridline-color: {BORDER};
                font-size: 13px;
                selection-background-color: {PRIMARY}15;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {BORDER};
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item:hover {{
                background: {BACKGROUND};
            }}
            QTableWidget::item:selected {{
                background: {PRIMARY}20;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background: {WHITE};
                color: {TEXT_SECONDARY};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {BORDER};
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        
        # Table configuration
        self.payments_table.setAlternatingRowColors(False)
        self.payments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.payments_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.payments_table.setSortingEnabled(True)
        self.payments_table.setShowGrid(False)
        self.payments_table.verticalHeader().setVisible(False)
        self.payments_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Column sizing - responsive
        header = self.payments_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Date
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Type
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Party - stretches
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Amount
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Method
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Reference
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Actions
        
        self.payments_table.setColumnWidth(0, 100)  # Date
        self.payments_table.setColumnWidth(1, 130)  # Type
        self.payments_table.setColumnWidth(3, 120)  # Amount
        self.payments_table.setColumnWidth(4, 110)  # Method
        self.payments_table.setColumnWidth(5, 130)  # Reference
        self.payments_table.setColumnWidth(6, 90)   # Status
        self.payments_table.setColumnWidth(7, 120)  # Actions
        
        # Row height
        self.payments_table.verticalHeader().setDefaultSectionSize(42)
        
        table_layout.addWidget(self.payments_table)
        
        # Pagination footer
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: none;
                border-top: 1px solid {BORDER};
                border-radius: 0 0 12px 12px;
            }}
        """)
        
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(16, 10, 16, 10)
        
        self.pagination_info = QLabel("Showing 0 - 0 of 0 items")
        self.pagination_info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; border: none;")
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addStretch()
        
        # Pagination controls
        btn_style = f"""
            QPushButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
                border-color: {PRIMARY};
            }}
            QPushButton:disabled {{
                color: {BORDER};
                background: {BACKGROUND};
            }}
        """
        
        self.prev_page_btn = QPushButton("← Previous")
        self.prev_page_btn.setFixedHeight(32)
        self.prev_page_btn.setStyleSheet(btn_style)
        self.prev_page_btn.setCursor(Qt.PointingHandCursor)
        self.prev_page_btn.clicked.connect(self._previous_page)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 500; padding: 0 12px; border: none;")
        pagination_layout.addWidget(self.page_info)
        
        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.setFixedHeight(32)
        self.next_page_btn.setStyleSheet(btn_style)
        self.next_page_btn.setCursor(Qt.PointingHandCursor)
        self.next_page_btn.clicked.connect(self._next_page)
        pagination_layout.addWidget(self.next_page_btn)
        
        table_layout.addWidget(pagination_frame)
        
        parent_layout.addWidget(table_frame)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading & Filtering
    # ─────────────────────────────────────────────────────────────────────────
    
    def _load_data(self):
        """Load payments data into table"""
        try:
            payments = db.get_payments() or []
            self.all_payments_data = payments
            self._populate_table(payments)
            self._update_stats(payments)
        except Exception as e:
            print(f"Database error: {e}")
            self.all_payments_data = []
            self._populate_table([])
            self._update_stats([])
    
    def _populate_table(self, payments_data):
        """Populate table with payments data"""
        self.payments_table.setRowCount(len(payments_data))
        
        for row, payment in enumerate(payments_data):
            # Date
            date_item = QTableWidgetItem(str(payment.get('date', '')))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.payments_table.setItem(row, 0, date_item)
            
            # Type with color coding
            payment_type = payment.get('type', 'Payment Received')
            type_item = QTableWidgetItem(payment_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            
            if payment_type == "Payment Received":
                type_item.setForeground(QColor(SUCCESS))
                type_item.setBackground(QColor("#D1FAE5"))
            else:
                type_item.setForeground(QColor(DANGER))
                type_item.setBackground(QColor("#FEE2E2"))
            
            self.payments_table.setItem(row, 1, type_item)
            
            # Party name
            party_item = QTableWidgetItem(str(payment.get('party_name', 'N/A')))
            self.payments_table.setItem(row, 2, party_item)
            
            # Amount with color coding
            amount = payment.get('amount', 0)
            amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFont(QFont("Arial", 11, QFont.Bold))
            
            if payment_type == "Payment Received":
                amount_item.setForeground(QColor(SUCCESS))
            else:
                amount_item.setForeground(QColor(DANGER))
            
            self.payments_table.setItem(row, 3, amount_item)
            
            # Method
            method_item = QTableWidgetItem(str(payment.get('method', 'Cash')))
            method_item.setTextAlignment(Qt.AlignCenter)
            self.payments_table.setItem(row, 4, method_item)
            
            # Reference
            reference_item = QTableWidgetItem(str(payment.get('reference', '') or '-'))
            reference_item.setTextAlignment(Qt.AlignCenter)
            self.payments_table.setItem(row, 5, reference_item)
            
            # Status with color coding
            status = payment.get('status', 'Completed')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            status_colors = {
                'Completed': (SUCCESS, "#D1FAE5"),
                'Pending': (WARNING, "#FEF3C7"),
                'Failed': (DANGER, "#FEE2E2"),
            }
            
            if status in status_colors:
                color, bg_color = status_colors[status]
                status_item.setForeground(QColor(color))
                status_item.setBackground(QColor(bg_color))
            
            self.payments_table.setItem(row, 6, status_item)
            
            # Action buttons
            actions_widget = self._create_action_buttons(payment)
            self.payments_table.setCellWidget(row, 7, actions_widget)
        
        self._update_pagination_info()
    
    def _create_action_buttons(self, payment):
        """Create action buttons for each payment row"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        widget.setFixedHeight(40)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        actions = [
            ("View", "View Details", lambda _, p=payment: self._view_payment(p), "#EEF2FF", PRIMARY),
            ("Edit", "Edit Payment", lambda _, p=payment: self._edit_payment(p), "#FEF3C7", WARNING),
            ("Del", "Delete", lambda _, p=payment: self._delete_payment(p), "#FEE2E2", DANGER)
        ]
        
        for text, tooltip, callback, bg_color, hover_color in actions:
            btn = QPushButton(text)
            btn.setFixedSize(36, 26)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    background: {bg_color};
                    font-size: 10px;
                    font-weight: 600;
                    color: {TEXT_PRIMARY};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: {hover_color};
                    border-color: {hover_color};
                    color: white;
                }}
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        return widget
    
    def _update_stats(self, payments_data):
        """Update statistics display"""
        total_received = sum(p.get('amount', 0) for p in payments_data if p.get('type') == 'Payment Received')
        total_paid = sum(p.get('amount', 0) for p in payments_data if p.get('type') == 'Payment Made')
        total_count = len(payments_data)
        
        # Calculate this month's total
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        month_total = sum(
            p.get('amount', 0) for p in payments_data 
            if str(p.get('date', '')).startswith(current_month)
        )
        
        if hasattr(self, 'total_received_label') and self.total_received_label:
            self.total_received_label.setText(f"₹{total_received:,.0f}")
        if hasattr(self, 'total_paid_label') and self.total_paid_label:
            self.total_paid_label.setText(f"₹{total_paid:,.0f}")
        if hasattr(self, 'total_count_label') and self.total_count_label:
            self.total_count_label.setText(str(total_count))
        if hasattr(self, 'month_total_label') and self.month_total_label:
            self.month_total_label.setText(f"₹{month_total:,.0f}")
    
    def _filter_payments(self):
        """Filter payments based on search and filter controls"""
        search_text = self.search_input.text().lower().strip()
        type_filter = self.type_filter.currentText()
        method_filter = self.method_filter.currentText()
        period_filter = self.period_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_data = []
        
        for payment in self.all_payments_data:
            # Search filter
            if search_text:
                searchable = f"""
                    {payment.get('party_name', '')} 
                    {payment.get('reference', '')} 
                    {payment.get('method', '')}
                    {payment.get('notes', '')}
                """.lower()
                if search_text not in searchable:
                    continue
            
            # Type filter
            if type_filter != "All Types" and payment.get('type') != type_filter:
                continue
            
            # Method filter
            if method_filter != "All Methods" and payment.get('method') != method_filter:
                continue
            
            # Status filter
            if status_filter != "All Status" and payment.get('status', 'Completed') != status_filter:
                continue
            
            # Period filter
            if not self._check_period_filter(payment.get('date', ''), period_filter):
                continue
            
            filtered_data.append(payment)
        
        self._populate_table(filtered_data)
        self._update_stats(filtered_data)
    
    def _check_period_filter(self, payment_date, period_filter):
        """Check if payment date matches the period filter"""
        if period_filter == "All Time":
            return True
        
        try:
            from datetime import datetime, timedelta
            
            payment_dt = datetime.strptime(str(payment_date), '%Y-%m-%d')
            today = datetime.now()
            
            if period_filter == "Today":
                return payment_dt.date() == today.date()
            elif period_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return payment_dt >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period_filter == "This Month":
                return payment_dt.year == today.year and payment_dt.month == today.month
            elif period_filter == "This Year":
                return payment_dt.year == today.year
        except ValueError:
            return True
        
        return True
    
    def _clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.method_filter.setCurrentIndex(0)
        self.period_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        
        self._populate_table(self.all_payments_data)
        self._update_stats(self.all_payments_data)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Pagination
    # ─────────────────────────────────────────────────────────────────────────
    
    def _update_pagination_info(self):
        """Update pagination info display"""
        total = len(self.all_payments_data)
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (total + items_per_page - 1) // items_per_page)
        
        start = (self.current_page - 1) * items_per_page + 1
        end = min(self.current_page * items_per_page, total)
        
        if total == 0:
            start = 0
            end = 0
        
        self.pagination_info.setText(f"Showing {start} - {end} of {total} items")
        self.page_info.setText(f"Page {self.current_page} of {total_pages}")
        
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._filter_payments()
    
    def _next_page(self):
        """Go to next page"""
        total = len(self.all_payments_data)
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (total + items_per_page - 1) // items_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            self._filter_payments()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────
    
    def _record_payment(self):
        """Open record payment dialog"""
        dialog = PaymentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()
    
    def _edit_payment(self, payment):
        """Open edit payment dialog"""
        dialog = PaymentDialog(self, payment)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()
    
    def _view_payment(self, payment):
        """View payment details"""
        details = f"""
<h3>💳 Payment Details</h3>

<p><b>Type:</b> {payment.get('type', 'N/A')}</p>
<p><b>Party:</b> {payment.get('party_name', 'N/A')}</p>
<p><b>Amount:</b> ₹{payment.get('amount', 0):,.2f}</p>
<p><b>Date:</b> {payment.get('date', 'N/A')}</p>
<p><b>Method:</b> {payment.get('method', 'N/A')}</p>
<p><b>Reference:</b> {payment.get('reference', 'N/A') or '-'}</p>
<p><b>Status:</b> {payment.get('status', 'N/A')}</p>
<p><b>Notes:</b> {payment.get('notes', '') or '-'}</p>
        """
        QMessageBox.information(self, "Payment Details", details.strip())
    
    def _delete_payment(self, payment):
        """Delete payment with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this payment?\n\n"
            f"Party: {payment.get('party_name', 'N/A')}\n"
            f"Amount: ₹{payment.get('amount', 0):,.2f}\n"
            f"Date: {payment.get('date', 'N/A')}\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_payment(payment.get('id'))
                QMessageBox.information(self, "Success", "✓ Payment deleted successfully!")
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete payment:\n\n{str(e)}")
    
    def _export_payments(self):
        """Export payments data"""
        QMessageBox.information(
            self, "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export payment data to CSV or Excel."
        )
