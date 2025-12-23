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
from .invoice_dialogue import InvoiceDialog as ExternalInvoiceDialog
# Backwards compatibility: re-export under original name
InvoiceDialog = ExternalInvoiceDialog
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from database import db


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
        dialog = ExternalInvoiceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_invoices_data()
    
    def edit_invoice(self, invoice):
        """Open edit invoice dialog"""
        dialog = ExternalInvoiceDialog(self, invoice)
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
