"""
Invoices screen - Create and manage invoices with enhanced UI and functionality
Responsive design with modern card-based layout
"""

import sys
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QAction, QSizePolicy, QGridLayout
)
from .invoice_dialogue import InvoiceDialog as ExternalInvoiceDialog
# Backwards compatibility: re-export under original name
InvoiceDialog = ExternalInvoiceDialog
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

from .base_screen import BaseScreen
from .invoice_print_preview import InvoicePrintPreview
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from database import db
from pdf_generator import InvoicePDFGenerator


class InvoicesScreen(BaseScreen):
    """Enhanced Invoices screen with modern responsive UI"""
    
    def __init__(self):
        super().__init__("💼 Invoices & Billing")
        self.all_invoices_data = []
        self.current_page = 1
        self.setup_invoices_screen()
        self.load_invoices_data()
    
    def setup_invoices_screen(self):
        """Setup enhanced invoices screen content"""
        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}")
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header section with search and actions
        self.setup_header_section(content_layout)
        
        # Stats cards row
        self.setup_stats_section(content_layout)
        
        # Filters section
        self.setup_filters_section(content_layout)
        
        # Table section
        self.setup_table_section(content_layout)
        
        scroll_area.setWidget(content_widget)
        self.add_content(scroll_area)
    
    def setup_header_section(self, parent_layout):
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
        self.search_input.setPlaceholderText("Search invoices...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {TEXT_PRIMARY};
                padding: 4px 0;
            }}
        """)
        self.search_input.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.search_input)
        
        header_layout.addWidget(search_frame)
        header_layout.addStretch()
        
        # Action buttons
        buttons_data = [
            ("📤 Export", "secondary", self.export_invoices),
            ("➕ New Invoice", "primary", self.create_invoice)
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
    
    def setup_stats_section(self, parent_layout):
        """Setup statistics cards with responsive grid"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent; border: none;")
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        
        # Statistics cards data
        stats_data = [
            ("📋", "Total Invoices", "0", PRIMARY, "total_invoices_label"),
            ("💰", "Total Revenue", "₹0", SUCCESS, "total_amount_label"),
            ("⏰", "Overdue", "0", DANGER, "overdue_label"),
            ("✅", "Paid", "0", "#10B981", "paid_label")
        ]
        
        for icon, label_text, value, color, attr_name in stats_data:
            card = self.create_stat_card(icon, label_text, value, color)
            setattr(self, attr_name, card.findChild(QLabel, "value_label"))
            stats_layout.addWidget(card)
        
        parent_layout.addWidget(stats_frame)
    
    def create_stat_card(self, icon, label_text, value, color):
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
        icon_label.setStyleSheet(f"font-size: 20px; border: none;")
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
    
    def setup_filters_section(self, parent_layout):
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
        filter_controls = [
            ("Status", ["All", "Paid", "Overdue", "Cancelled"], "status_filter"),
            ("Period", ["All Time", "Today", "This Week", "This Month", "This Year"], "period_filter"),
            ("Amount", ["All Amounts", "Under ₹10K", "₹10K - ₹50K", "₹50K - ₹1L", "Above ₹1L"], "amount_filter"),
            ("Party", ["All Parties"], "party_filter")
        ]
        
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
            combo.currentTextChanged.connect(self.filter_invoices)
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
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: white;
                border-color: {PRIMARY};
            }}
        """)
        refresh_btn.clicked.connect(self.load_invoices_data)
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
        clear_btn.clicked.connect(self.clear_filters)
        filters_layout.addWidget(clear_btn)
        
        parent_layout.addWidget(filters_frame)
    
    def setup_table_section(self, parent_layout):
        """Setup responsive table with pagination - styled like Parties table"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_frame.setStyleSheet(f"""
            QFrame#tableFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(24, 20, 24, 20)
        table_layout.setSpacing(16)

        # Table header with title and count
        header_layout = QHBoxLayout()
        
        # Title with icon
        title_container = QHBoxLayout()
        title_container.setSpacing(10)
        
        title_icon = QLabel("📄")
        title_icon.setStyleSheet("border: none; font-size: 20px;")
        title_container.addWidget(title_icon)

        table_title = QLabel("Invoice List")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        title_container.addWidget(table_title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)

        # Count badge
        self.count_label = QLabel("0 invoices")
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                background: {BACKGROUND};
                padding: 6px 14px;
                border-radius: 16px;
                border: none;
            }}
        """)
        header_layout.addWidget(self.count_label)
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
        self.items_per_page.currentTextChanged.connect(self.load_invoices_data)
        header_layout.addWidget(self.items_per_page)

        table_layout.addLayout(header_layout)

        # Create table
        headers = ["#", "Invoice No.", "Date", "Party", "Amount", "Status", "Actions"]
        self.invoices_table = QTableWidget(0, len(headers))
        self.invoices_table.setHorizontalHeaderLabels(headers)
        self.invoices_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Enhanced table styling (same as parties.py)
        self.invoices_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #F3F4F6;
                background-color: {WHITE};
                border: none;
                font-size: 14px;
                selection-background-color: #EEF2FF;
                alternate-background-color: #FAFBFC;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding: 12px 10px;
                font-size: 14px;
            }}
            QTableWidget::item:selected {{
                background-color: #EEF2FF;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {TEXT_SECONDARY};
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                padding: 12px 10px;
                font-size: 14px;
                text-transform: uppercase;
            }}
            QHeaderView::section:hover {{
                background-color: #F1F5F9;
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

        # Enable alternating row colors
        self.invoices_table.setAlternatingRowColors(True)

        # Table configuration
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.invoices_table.setSortingEnabled(True)
        self.invoices_table.setShowGrid(False)
        self.invoices_table.verticalHeader().setVisible(False)
        self.invoices_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set fixed column widths
        # ["#", "Invoice No.", "Date", "Party", "Amount", "Status", "Actions"]
        self.invoices_table.setColumnWidth(0, 40)    # #
        self.invoices_table.setColumnWidth(1, 100)   # Invoice No.
        self.invoices_table.setColumnWidth(2, 150)   # Date
        self.invoices_table.setColumnWidth(3, 150)   # Party
        self.invoices_table.setColumnWidth(4, 150)   # Amount
        self.invoices_table.setColumnWidth(5, 150)    # Status
        self.invoices_table.setColumnWidth(6, 200)   # Actions

        # Make Party column stretch to fill remaining space
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        # Row height
        self.invoices_table.verticalHeader().setDefaultSectionSize(48)
        self.invoices_table.setMinimumHeight(400)

        # Context menu and double-click to view
        self.invoices_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.invoices_table.customContextMenuRequested.connect(self.show_context_menu)
        self.invoices_table.itemDoubleClicked.connect(self.handle_double_click)

        table_layout.addWidget(self.invoices_table)

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
        self.prev_page_btn.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 500; padding: 0 12px; border: none;")
        pagination_layout.addWidget(self.page_info)
        
        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.setFixedHeight(32)
        self.next_page_btn.setStyleSheet(btn_style)
        self.next_page_btn.setCursor(Qt.PointingHandCursor)
        self.next_page_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_page_btn)
        
        table_layout.addWidget(pagination_frame)
        
        parent_layout.addWidget(table_frame)
    
    def load_invoices_data(self):
        """Load invoices data into table"""
        try:
            # Get invoices with party details using a JOIN query
            if hasattr(db, '_query'):
                # Use a JOIN query to get party names
                query = """
                    SELECT 
                        i.*,
                        COALESCE(p.name, 'Unknown Party') as party_name,
                        CASE 
                            WHEN i.grand_total > 0 AND i.date < date('now', '-30 days') THEN 'Overdue'
                            ELSE 'Sent'
                        END as status
                    FROM invoices i
                    LEFT JOIN parties p ON i.party_id = p.id
                    ORDER BY i.id DESC
                """
                invoices = db._query(query)
            else:
                # Fallback to basic method if _query not available
                invoices = db.get_invoices()
                
                # Add party names and status manually
                for invoice in invoices:
                    if invoice.get('party_id'):
                        try:
                            party = db.get_party_by_id(invoice['party_id'])
                            invoice['party_name'] = party.get('name', 'Unknown Party') if party else 'Unknown Party'
                        except:
                            invoice['party_name'] = 'Unknown Party'
                    else:
                        invoice['party_name'] = 'Unknown Party'
                    
                    # Add status based on business logic
                    if invoice.get('grand_total', 0) > 0:
                        invoice['status'] = 'Sent'  # Default status
                    else:
                        invoice['status'] = 'Draft'
            
            print(f"Loaded {len(invoices)} invoices from database")  # Debug info
            
            self.all_invoices_data = invoices
            self.populate_table(invoices)
            self.update_stats(invoices)
            
        except Exception as e:
            print(f"Error loading invoices: {e}")  # Debug info
            # If there's an error, show empty table instead of sample data
            self.all_invoices_data = []
            self.populate_table([])
            self.update_stats([])
            
            # Show a user-friendly message
            QMessageBox.information(
                self, 
                "Database Info", 
                f"Unable to load invoices from database.\n\nError: {str(e)}\n\nPlease check your database connection."
            )
    
    def populate_table(self, invoices_data):
        """Populate table with invoices data matching Party table style"""
        # Disable sorting while populating to avoid weird behavior
        self.invoices_table.setSortingEnabled(False)
        self.invoices_table.setRowCount(len(invoices_data))
        
        for row, invoice in enumerate(invoices_data):
            # Alternate row colors for better readability
            row_color = WHITE if row % 2 == 0 else "#F8FAFC"
            
            # Row number (column 0 - #)
            row_num_item = QTableWidgetItem(str(row + 1))
            row_num_item.setTextAlignment(Qt.AlignCenter)
            row_num_item.setFont(QFont("Arial", 14))
            row_num_item.setForeground(QColor(TEXT_SECONDARY))
            row_num_item.setBackground(QColor(row_color))
            self.invoices_table.setItem(row, 0, row_num_item)
            
            # Invoice number (column 1)
            invoice_item = QTableWidgetItem(str(invoice.get('invoice_no', f'INV-{invoice["id"]:03d}')))
            invoice_item.setFont(QFont("Arial", 14, QFont.Bold))
            invoice_item.setForeground(QColor(PRIMARY))
            invoice_item.setBackground(QColor(row_color))
            self.invoices_table.setItem(row, 1, invoice_item)
            
            # Date (column 2)
            date_item = QTableWidgetItem(str(invoice.get('date', '2024-01-01')))
            date_item.setFont(QFont("Arial", 14))
            date_item.setBackground(QColor(row_color))
            self.invoices_table.setItem(row, 2, date_item)
            
            # Party name (column 3)
            party_item = QTableWidgetItem(str(invoice.get('party_name', 'Sample Party')))
            party_item.setFont(QFont("Arial", 14))
            party_item.setBackground(QColor(row_color))
            self.invoices_table.setItem(row, 3, party_item)
            
            # Amount with currency formatting (column 4)
            amount = invoice.get('grand_total', 0)
            amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFont(QFont("Arial", 14, QFont.Bold))
            amount_item.setBackground(QColor(row_color))
            self.invoices_table.setItem(row, 4, amount_item)
            
            # Status with color coding (column 5)
            status = invoice.get('status', 'Draft')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFont(QFont("Arial", 14, QFont.Bold))

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
            else:
                status_item.setBackground(QColor(row_color))
            
            self.invoices_table.setItem(row, 5, status_item)
            
            # Action buttons (column 6)
            actions_widget = self.create_action_buttons(invoice)
            self.invoices_table.setCellWidget(row, 6, actions_widget)
        
        # Re-enable sorting after populating
        self.invoices_table.setSortingEnabled(True)
        self.update_pagination_info()
    
    def create_action_buttons(self, invoice):
        """Create action buttons for each invoice row matching Party table style"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        widget.setFixedHeight(28)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        # Action buttons - same style as parties.py
        actions = [
            ("View Pdf", "View Invoice", lambda _, inv=invoice: self.view_invoice(inv), "#EEF2FF", PRIMARY),
            ("Del", "Delete Invoice", lambda _, inv=invoice: self.delete_invoice(inv), "#FEE2E2", DANGER)
        ]

        for text, tooltip, callback, bg_color, hover_color in actions:
            btn = QPushButton(text)
            btn.setFixedSize(50, 28)
            if text == "View Pdf":
                btn.setFixedSize(80, 28)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    background: {bg_color};
                    font-size: 12px;
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
    def show_context_menu(self, position): pass
    
    def handle_double_click(self, item):
        """Handle double-click on invoice row - open invoice in read-only view mode"""
        row = item.row()
        if row < len(self.all_invoices_data):
            invoice = self.all_invoices_data[row]
            self.open_invoice_readonly(invoice)
    
    def open_invoice_readonly(self, invoice):
        """Open invoice dialog in read-only mode for viewing"""
        try:
            if isinstance(invoice, dict):
                invoice_id = invoice.get('id')
            else:
                invoice_id = invoice
            
            if not invoice_id:
                QMessageBox.warning(self, "Error", "Invalid invoice data")
                return
            
            # Get full invoice data from database by ID
            invoice_data = db.get_invoice_with_items_by_id(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", f"Could not load invoice data for ID: {invoice_id}")
                return
            
            # Open InvoiceDialog in read-only mode
            dialog = ExternalInvoiceDialog(self, invoice_data=invoice_data, read_only=True)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open invoice: {str(e)}")
    
    def send_invoice(self, invoice):
        """Send invoice to customer"""
        if isinstance(invoice, dict):
            invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
        else:
            invoice_no = f"Invoice ID: {invoice}"
        QMessageBox.information(self, "Send Invoice", f"Sending invoice {invoice_no}")
    
    def record_payment(self, invoice):
        """Record payment for invoice"""
        if isinstance(invoice, dict):
            invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
        else:
            invoice_no = f"Invoice ID: {invoice}"
        QMessageBox.information(self, "Record Payment", f"Recording payment for invoice {invoice_no}")
    
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
        
        # Update count label in table header
        self.count_label.setText(f"{total_count} invoices")
    
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
        """View invoice details - generates and shows PDF preview"""
        try:
            if isinstance(invoice, dict):
                invoice_id = invoice.get('id')
                invoice_no = invoice.get('invoice_no', f"INV-{invoice_id:03d}")
            else:
                invoice_id = invoice
                invoice_no = f"INV-{invoice_id:03d}"
            
            if not invoice_id:
                QMessageBox.warning(self, "Error", "Invalid invoice data")
                return
            
            # Show print preview
            self.show_print_preview(invoice_id)
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to view invoice: {str(e)}"
            )
    
    def show_print_preview(self, invoice_id):
        """Show HTML preview dialog - uses common utility to avoid code duplication"""
        from .invoice_preview import show_invoice_preview
        show_invoice_preview(self, invoice_id)
    
    def print_invoice(self, invoice):
        """Print/export invoice as PDF"""
        QMessageBox.information(self, "Print Invoice", "Print/PDF functionality will be implemented soon!")
    
    def delete_invoice(self, invoice):
        """Delete invoice with confirmation"""
        if isinstance(invoice, dict):
            invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
            invoice_id = invoice['id']
        else:
            invoice_no = f"Invoice ID: {invoice}"
            invoice_id = invoice
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete invoice {invoice_no}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_invoice(invoice_id)
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
