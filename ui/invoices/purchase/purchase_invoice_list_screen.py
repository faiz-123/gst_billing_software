"""
Purchases screen - Create and manage purchase invoices with enhanced UI and functionality
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
from ui.invoices.purchase.purchase_invoice_form_dialog import PurchaseInvoiceDialog
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

from ui.base.base_screen import BaseScreen
from ui.print.invoice_print_preview_screen import InvoicePrintPreview
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from core.db.sqlite_db import db
from ui.print.invoice_pdf_generator import InvoicePDFGenerator


class PurchasesScreen(BaseScreen):
    """Enhanced Purchases screen with modern responsive UI"""
    
    def __init__(self):
        super().__init__("🛒 Purchase Invoices")
        self.all_purchases_data = []
        self.current_page = 1
        self.setup_purchases_screen()
        self.load_purchases_data()
    
    def setup_purchases_screen(self):
        """Setup enhanced purchases screen content"""
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
        self.search_input.setPlaceholderText("Search purchase invoices...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {TEXT_PRIMARY};
                padding: 4px 0;
            }}
        """)
        self.search_input.textChanged.connect(self.filter_purchases)
        search_layout.addWidget(self.search_input)
        
        header_layout.addWidget(search_frame)
        header_layout.addStretch()
        
        # Action buttons
        buttons_data = [
            ("📤 Export", "secondary", self.export_purchases),
            ("➕ New Purchase", "primary", self.create_purchase)
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
        
        # Statistics cards data - using orange/amber theme for purchases
        stats_data = [
            ("📋", "Total Purchases", "0", "#F59E0B", "total_purchases_label"),
            ("💸", "Total Expense", "₹0", DANGER, "total_amount_label"),
            ("⏰", "Unpaid", "0", "#6366F1", "unpaid_label"),
            ("✅", "Paid", "0", SUCCESS, "paid_label")
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
            ("Status", ["All", "Paid", "Unpaid", "Cancelled"], "status_filter"),
            ("Period", ["All Time", "Today", "This Week", "This Month", "This Year"], "period_filter"),
            ("Amount", ["All Amounts", "Under ₹10K", "₹10K - ₹50K", "₹50K - ₹1L", "Above ₹1L"], "amount_filter"),
            ("Supplier", ["All Suppliers"], "supplier_filter")
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
            combo.currentTextChanged.connect(self.filter_purchases)
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
        refresh_btn.clicked.connect(self.load_purchases_data)
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
        """Setup responsive table with pagination"""
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
        
        title_icon = QLabel("🛒")
        title_icon.setStyleSheet("border: none; font-size: 20px;")
        title_container.addWidget(title_icon)

        table_title = QLabel("Purchase Invoice List")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        title_container.addWidget(table_title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)

        # Count badge
        self.count_label = QLabel("0 purchases")
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
        self.items_per_page.currentTextChanged.connect(self.load_purchases_data)
        header_layout.addWidget(self.items_per_page)

        table_layout.addLayout(header_layout)

        # Create table
        headers = ["#", "Invoice No.", "Date", "Supplier", "Amount", "Status", "Actions"]
        self.purchases_table = QTableWidget(0, len(headers))
        self.purchases_table.setHorizontalHeaderLabels(headers)
        self.purchases_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Enhanced table styling
        self.purchases_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #F3F4F6;
                background-color: {WHITE};
                border: none;
                font-size: 14px;
                selection-background-color: #FEF3C7;
                alternate-background-color: #FFFBEB;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding: 12px 10px;
                font-size: 14px;
            }}
            QTableWidget::item:selected {{
                background-color: #FEF3C7;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #FFFBEB;
                color: {TEXT_SECONDARY};
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #FCD34D;
                padding: 12px 10px;
                font-size: 14px;
                text-transform: uppercase;
            }}
            QHeaderView::section:hover {{
                background-color: #FEF3C7;
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
                background: #F59E0B;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        # Enable alternating row colors
        self.purchases_table.setAlternatingRowColors(True)

        # Table configuration
        self.purchases_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.purchases_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.purchases_table.setSortingEnabled(True)
        self.purchases_table.setShowGrid(False)
        self.purchases_table.verticalHeader().setVisible(False)
        self.purchases_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set fixed column widths
        self.purchases_table.setColumnWidth(0, 40)    # #
        self.purchases_table.setColumnWidth(1, 120)   # Invoice No.
        self.purchases_table.setColumnWidth(2, 150)   # Date
        self.purchases_table.setColumnWidth(3, 150)   # Supplier
        self.purchases_table.setColumnWidth(4, 150)   # Amount
        self.purchases_table.setColumnWidth(5, 100)   # Status
        self.purchases_table.setColumnWidth(6, 200)   # Actions

        # Make Supplier column stretch to fill remaining space
        header = self.purchases_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        # Row height
        self.purchases_table.verticalHeader().setDefaultSectionSize(48)
        self.purchases_table.setMinimumHeight(400)

        # Context menu and double-click to view
        self.purchases_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.purchases_table.customContextMenuRequested.connect(self.show_context_menu)
        self.purchases_table.itemDoubleClicked.connect(self.handle_double_click)

        table_layout.addWidget(self.purchases_table)

        # Pagination footer
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: #FFFBEB;
                border: none;
                border-top: 1px solid #FCD34D;
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
                background: #FEF3C7;
                border-color: #F59E0B;
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
    
    def load_purchases_data(self):
        """Load purchase invoices data into table"""
        try:
            # Get purchase invoices with supplier details using a JOIN query
            if hasattr(db, '_query'):
                # Filter by company_id for data isolation
                company_id = db.get_current_company_id()
                if company_id:
                    query = """
                        SELECT 
                            pi.*,
                            COALESCE(p.name, 'Unknown Supplier') as party_name,
                            CASE 
                                WHEN pi.status = 'Paid' THEN 'Paid'
                                WHEN pi.grand_total > 0 AND pi.date < date('now', '-30 days') THEN 'Unpaid'
                                ELSE COALESCE(pi.status, 'Unpaid')
                            END as display_status
                        FROM purchase_invoices pi
                        LEFT JOIN parties p ON pi.supplier_id = p.id
                        WHERE pi.company_id = ?
                        ORDER BY pi.id DESC
                    """
                    purchases = db._query(query, (company_id,))
                else:
                    query = """
                        SELECT 
                            pi.*,
                            COALESCE(p.name, 'Unknown Supplier') as party_name,
                            CASE 
                                WHEN pi.status = 'Paid' THEN 'Paid'
                                WHEN pi.grand_total > 0 AND pi.date < date('now', '-30 days') THEN 'Unpaid'
                                ELSE COALESCE(pi.status, 'Unpaid')
                            END as display_status
                        FROM purchase_invoices pi
                        LEFT JOIN parties p ON pi.supplier_id = p.id
                        ORDER BY pi.id DESC
                    """
                    purchases = db._query(query)
            else:
                purchases = db.get_purchase_invoices()
                
                # Add party names and status manually
                for purchase in purchases:
                    if purchase.get('supplier_id'):
                        try:
                            party = db.get_party_by_id(purchase['supplier_id'])
                            purchase['party_name'] = party.get('name', 'Unknown Supplier') if party else 'Unknown Supplier'
                        except:
                            purchase['party_name'] = 'Unknown Supplier'
                    else:
                        purchase['party_name'] = 'Unknown Supplier'
                    
                    purchase['display_status'] = purchase.get('status', 'Unpaid')
            
            print(f"Loaded {len(purchases)} purchase invoices from database")
            
            self.all_purchases_data = purchases
            self.populate_table(purchases)
            self.update_stats(purchases)
            
        except Exception as e:
            print(f"Error loading purchases: {e}")
            self.all_purchases_data = []
            self.populate_table([])
            self.update_stats([])
            
            QMessageBox.information(
                self, 
                "Database Info", 
                f"Unable to load purchase invoices from database.\n\nError: {str(e)}\n\nPlease check your database connection."
            )
    
    def populate_table(self, purchases_data):
        """Populate table with purchase invoice data"""
        self.purchases_table.setSortingEnabled(False)
        self.purchases_table.setRowCount(len(purchases_data))
        
        for row, purchase in enumerate(purchases_data):
            row_color = WHITE if row % 2 == 0 else "#FFFBEB"
            
            # Row number (column 0)
            row_num_item = QTableWidgetItem(str(row + 1))
            row_num_item.setTextAlignment(Qt.AlignCenter)
            row_num_item.setFont(QFont("Arial", 14))
            row_num_item.setForeground(QColor(TEXT_SECONDARY))
            row_num_item.setBackground(QColor(row_color))
            self.purchases_table.setItem(row, 0, row_num_item)
            
            # Invoice number (column 1)
            invoice_item = QTableWidgetItem(str(purchase.get('invoice_no', f'PUR-{purchase["id"]:03d}')))
            invoice_item.setFont(QFont("Arial", 14, QFont.Bold))
            invoice_item.setForeground(QColor("#F59E0B"))  # Amber color for purchase
            invoice_item.setBackground(QColor(row_color))
            self.purchases_table.setItem(row, 1, invoice_item)
            
            # Date (column 2)
            date_item = QTableWidgetItem(str(purchase.get('date', '2024-01-01')))
            date_item.setFont(QFont("Arial", 14))
            date_item.setBackground(QColor(row_color))
            self.purchases_table.setItem(row, 2, date_item)
            
            # Supplier name (column 3)
            supplier_item = QTableWidgetItem(str(purchase.get('party_name', 'Unknown Supplier')))
            supplier_item.setFont(QFont("Arial", 14))
            supplier_item.setBackground(QColor(row_color))
            self.purchases_table.setItem(row, 3, supplier_item)
            
            # Amount with currency formatting (column 4)
            amount = purchase.get('grand_total', 0)
            amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFont(QFont("Arial", 14, QFont.Bold))
            amount_item.setBackground(QColor(row_color))
            self.purchases_table.setItem(row, 4, amount_item)
            
            # Status with color coding (column 5)
            status = purchase.get('display_status', purchase.get('status', 'Unpaid'))
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFont(QFont("Arial", 14, QFont.Bold))

            # Color code status
            status_colors = {
                'Draft': ("#6B7280", "#F3F4F6"),
                'Unpaid': ("#6366F1", "#EEF2FF"),
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
            
            self.purchases_table.setItem(row, 5, status_item)
            
            # Action buttons (column 6)
            actions_widget = self.create_action_buttons(purchase)
            self.purchases_table.setCellWidget(row, 6, actions_widget)
        
        self.purchases_table.setSortingEnabled(True)
        self.update_pagination_info()
    
    def create_action_buttons(self, purchase):
        """Create action buttons for each purchase row"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        widget.setFixedHeight(28)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        actions = [
            ("View", "View Purchase", lambda _, inv=purchase: self.view_purchase(inv), "#FEF3C7", "#F59E0B"),
            ("Del", "Delete Purchase", lambda _, inv=purchase: self.delete_purchase(inv), "#FEE2E2", DANGER)
        ]

        for text, tooltip, callback, bg_color, hover_color in actions:
            btn = QPushButton(text)
            btn.setFixedSize(50, 28)
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
    
    def update_pagination_info(self):
        """Update pagination information"""
        total_items = len(self.all_purchases_data)
        items_per_page = int(self.items_per_page.currentText())
        current_page = getattr(self, 'current_page', 1)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        
        start_item = (current_page - 1) * items_per_page + 1
        end_item = min(current_page * items_per_page, total_items)
        
        if total_items == 0:
            start_item = 0
        
        self.pagination_info.setText(f"Showing {start_item} - {end_item} of {total_items} items")
        self.page_info.setText(f"Page {current_page} of {total_pages}")
        
        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)
    
    def clear_filters(self):
        """Clear all applied filters"""
        self.status_filter.setCurrentIndex(0)
        self.period_filter.setCurrentIndex(0)
        self.amount_filter.setCurrentIndex(0)
        self.supplier_filter.setCurrentIndex(0)
        self.filter_purchases()
    
    def previous_page(self):
        """Go to previous page"""
        current_page = getattr(self, 'current_page', 1)
        if current_page > 1:
            self.current_page = current_page - 1
            self.load_purchases_data()
    
    def next_page(self):
        """Go to next page"""
        total_items = len(self.all_purchases_data)
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        current_page = getattr(self, 'current_page', 1)
        
        if current_page < total_pages:
            self.current_page = current_page + 1
            self.load_purchases_data()
    
    def show_context_menu(self, position):
        """Show context menu for table row"""
        pass
    
    def handle_double_click(self, item):
        """Handle double-click on purchase row"""
        row = item.row()
        if row < len(self.all_purchases_data):
            purchase = self.all_purchases_data[row]
            self.open_purchase_readonly(purchase)
    
    def open_purchase_readonly(self, purchase):
        """Open purchase dialog in read-only mode"""
        try:
            if isinstance(purchase, dict):
                purchase_id = purchase.get('id')
            else:
                purchase_id = purchase
            
            if not purchase_id:
                QMessageBox.warning(self, "Error", "Invalid purchase data")
                return
            
            purchase_data = db.get_purchase_invoice_with_items_by_id(purchase_id)
            
            if not purchase_data:
                QMessageBox.warning(self, "Error", f"Could not load purchase data for ID: {purchase_id}")
                return
            
            dialog = PurchaseInvoiceDialog(self, invoice_data=purchase_data, read_only=True)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open purchase: {str(e)}")
    
    def update_stats(self, purchases):
        """Update statistics with all metrics"""
        total_count = len(purchases)
        total_amount = sum(inv.get('grand_total', 0) for inv in purchases)
        
        unpaid_count = sum(1 for inv in purchases if inv.get('display_status', inv.get('status')) in ['Unpaid', 'Draft'])
        paid_count = sum(1 for inv in purchases if inv.get('display_status', inv.get('status')) == 'Paid')
        
        self.total_purchases_label.setText(str(total_count))
        self.total_amount_label.setText(f"₹{total_amount:,.0f}")
        self.unpaid_label.setText(str(unpaid_count))
        self.paid_label.setText(str(paid_count))
        
        self.count_label.setText(f"{total_count} purchases")
    
    def filter_purchases(self):
        """Filter purchases based on multiple criteria"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        period_filter = self.period_filter.currentText()
        amount_filter = self.amount_filter.currentText()
        supplier_filter = self.supplier_filter.currentText()
        
        filtered_data = []
        for purchase in self.all_purchases_data:
            # Search filter
            if search_text:
                searchable_text = f"{purchase.get('invoice_no', '')} {purchase.get('party_name', '')}".lower()
                if search_text not in searchable_text:
                    continue
            
            # Status filter
            status = purchase.get('display_status', purchase.get('status', 'Unpaid'))
            if status_filter != "All" and status != status_filter:
                continue
            
            # Amount filter
            amount = purchase.get('grand_total', 0)
            if amount_filter == "Under ₹10K" and amount >= 10000:
                continue
            elif amount_filter == "₹10K - ₹50K" and not (10000 <= amount < 50000):
                continue
            elif amount_filter == "₹50K - ₹1L" and not (50000 <= amount < 100000):
                continue
            elif amount_filter == "Above ₹1L" and amount < 100000:
                continue
            
            # Supplier filter
            if supplier_filter != "All Suppliers" and purchase.get('party_name', '') != supplier_filter:
                continue
            
            filtered_data.append(purchase)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
    
    def create_purchase(self):
        """Open create purchase invoice dialog"""
        dialog = PurchaseInvoiceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_purchases_data()
    
    def edit_purchase(self, purchase):
        """Open edit purchase dialog"""
        dialog = PurchaseInvoiceDialog(self, purchase)
        if dialog.exec_() == QDialog.Accepted:
            self.load_purchases_data()
    
    def view_purchase(self, purchase):
        """View purchase details"""
        try:
            if isinstance(purchase, dict):
                purchase_id = purchase.get('id')
            else:
                purchase_id = purchase
            
            if not purchase_id:
                QMessageBox.warning(self, "Error", "Invalid purchase data")
                return
            
            # Show print preview
            from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
            show_invoice_preview(self, purchase_id)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view purchase: {str(e)}")
    
    def delete_purchase(self, purchase):
        """Delete purchase with confirmation"""
        if isinstance(purchase, dict):
            invoice_no = purchase.get('invoice_no', f"PUR-{purchase['id']:03d}")
            purchase_id = purchase['id']
        else:
            invoice_no = f"Purchase ID: {purchase}"
            purchase_id = purchase
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete purchase invoice {invoice_no}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_purchase_invoice(purchase_id)
                QMessageBox.information(self, "Success", "Purchase invoice deleted successfully!")
                self.load_purchases_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete purchase: {str(e)}")
    
    def export_purchases(self):
        """Export purchases data"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")
    
    def refresh_data(self):
        """Refresh purchases data"""
        self.load_purchases_data()
