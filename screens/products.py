"""
Products screen - Modern responsive design for inventory management
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget, QTableWidgetItem,
    QToolButton, QSizePolicy, QScrollArea, QGridLayout, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

from .base_screen import BaseScreen
from .product_dialogue import ProductDialog
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from database import db


class ProductsScreen(BaseScreen):
    def __init__(self):
        super().__init__("Products & Services")
        self.all_products_data = []
        self.filter_combos = {}
        self.setup_products_screen()
        self.load_products_data()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible"""
        super().showEvent(event)
        self.load_products_data()
    
    def setup_products_screen(self):
        """Setup modern responsive products screen"""
        # Main container with scroll support
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        
        # Action bar (search + buttons)
        self.setup_action_bar(main_layout)
        
        # Statistics cards row
        self.setup_stats_section(main_layout)
        
        # Filters section
        self.setup_filters_section(main_layout)
        
        # Products table
        self.setup_products_table(main_layout)
        
        self.add_content(main_container)
    
    def setup_action_bar(self, parent_layout):
        """Setup top action bar with search and buttons"""
        action_frame = QFrame()
        action_frame.setObjectName("actionFrame")
        action_frame.setStyleSheet(f"""
            QFrame#actionFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(20, 15, 20, 15)
        action_layout.setSpacing(15)
        
        # Search container
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_container.setMinimumWidth(250)
        search_container.setMaximumWidth(450)
        search_container.setFixedHeight(48)
        search_container.setStyleSheet(f"""
            QFrame#searchContainer {{
                border: 2px solid {BORDER};
                border-radius: 10px;
                background: {WHITE};
            }}
            QFrame#searchContainer:hover {{
                border-color: {PRIMARY};
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 10, 0)
        search_layout.setSpacing(10)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 16px;")
        search_layout.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                font-size: 14px;
                background: transparent;
                color: {TEXT_PRIMARY};
                padding: 8px 0;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_SECONDARY};
            }}
        """)
        
        # Force uppercase as user types
        def force_upper(text):
            cursor_pos = self.search_input.cursorPosition()
            self.search_input.blockSignals(True)
            self.search_input.setText(text.upper())
            self.search_input.setCursorPosition(cursor_pos)
            self.search_input.blockSignals(False)
            self.filter_products()
        self.search_input.textChanged.connect(force_upper)
        search_layout.addWidget(self.search_input)
        
        action_layout.addWidget(search_container)
        action_layout.addStretch()
        
        # Action buttons
        buttons_config = [
            ("📊 Export", "secondary", self.export_products),
            ("📄 Import", "secondary", self.import_products),
            ("➕ Add Product", "primary", self.add_product)
        ]
        
        for text, style, callback in buttons_config:
            btn = self.create_action_button(text, style)
            btn.clicked.connect(callback)
            action_layout.addWidget(btn)
        
        parent_layout.addWidget(action_frame)
    
    def create_action_button(self, text, style):
        """Create styled action button"""
        btn = QPushButton(text)
        btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        if style == "primary":
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {PRIMARY}, stop:1 #1D4ED8);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 10px 24px;
                    min-width: 140px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3B82F6, stop:1 #1E40AF);
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
                    border: 2px solid {BORDER};
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 10px 20px;
                    min-width: 110px;
                }}
                QPushButton:hover {{
                    border-color: {PRIMARY};
                    background: #F8FAFC;
                    color: {PRIMARY};
                }}
                QPushButton:pressed {{
                    background: #EEF2FF;
                }}
            """)
        
        return btn
    
    def setup_stats_section(self, parent_layout):
        """Setup statistics cards with responsive grid - matching invoice/payments style"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent; border: none;")
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        
        # Stats data with colors and icons
        self.stat_labels = {}
        stats_config = [
            ("total", "📦", "Total Products", "0", PRIMARY),
            ("in_stock", "✅", "In Stock", "0", SUCCESS),
            ("low_stock", "⚠️", "Low Stock", "0", WARNING),
            ("out_stock", "❌", "Out of Stock", "0", DANGER),
        ]
        
        for key, icon, label_text, value, color in stats_config:
            card, value_label = self.create_stat_card(icon, label_text, value, color)
            self.stat_labels[key] = value_label
            stats_layout.addWidget(card)
        
        parent_layout.addWidget(stats_frame)
    
    def create_stat_card(self, icon, label_text, value, color):
        """Create modern statistics card - matching invoice/payments design"""
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
        value_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 22px;
            font-weight: 700;
            border: none;
        """)
        text_container.addWidget(value_label)
        
        layout.addLayout(text_container)
        layout.addStretch()
        
        return card, value_label
    
    def setup_filters_section(self, parent_layout):
        """Setup filter controls - same design as invoices.py"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        filter_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(16)
        
        # Filter label
        filter_label = QLabel("🎯 Filters")
        filter_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 600;
            border: none;
        """)
        filter_layout.addWidget(filter_label)
        
        # Separator
        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setFixedHeight(30)
        separator.setStyleSheet(f"background: {BORDER};")
        filter_layout.addWidget(separator)
        
        # Filter controls - same structure as invoices.py
        filter_controls = [
            ("Type", ["All", "Goods", "Service"], "type_filter"),
            ("Category", ["All Categories"], "category_filter"),
            ("Stock", ["All", "In Stock", "Low Stock", "Out of Stock"], "stock_filter"),
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
            # Container for label + combo (vertical layout like invoices.py)
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
            combo.currentTextChanged.connect(self.filter_products)
            setattr(self, attr_name, combo)
            self.filter_combos[attr_name] = combo
            filter_container.addWidget(combo)
            
            filter_layout.addLayout(filter_container)
        
        filter_layout.addStretch()
        
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
        refresh_btn.clicked.connect(self.load_products_data)
        filter_layout.addWidget(refresh_btn)
        
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
        filter_layout.addWidget(clear_btn)
        
        parent_layout.addWidget(filter_frame)
    
    def setup_products_table(self, parent_layout):
        """Setup enhanced products data table"""
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
        
        title_icon = QLabel("📦")
        title_icon.setStyleSheet("border: none; font-size: 20px;")
        title_container.addWidget(title_icon)
        
        table_title = QLabel("Products Inventory")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        title_container.addWidget(table_title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)
        
        # Count badge
        self.count_label = QLabel("0 products")
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
        
        table_layout.addLayout(header_layout)
        
        # Products table
        headers = ["#", "Product Name", "Type", "Price", "Stock", "Status", "Actions"]
        self.products_table = CustomTable(0, len(headers), headers)
        self.products_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enhanced table styling
        self.products_table.setStyleSheet(f"""
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
                font-size: 13px;
                text-transform: uppercase;
            }}
            QHeaderView::section:hover {{
                background-color: #F1F5F9;
            }}
        """)
        
        # Enable alternating row colors
        self.products_table.setAlternatingRowColors(True)
        
        # Column widths - responsive
        column_ratios = [0.05, 0.30, 0.10, 0.12, 0.12, 0.13, 0.18]
        for i, ratio in enumerate(column_ratios):
            self.products_table.setColumnWidth(i, int(800 * ratio))
        
        # Row height
        self.products_table.verticalHeader().setDefaultSectionSize(56)
        self.products_table.setMinimumHeight(400)
        
        table_layout.addWidget(self.products_table)
        parent_layout.addWidget(table_frame)
    
    def clear_filters(self):
        """Clear all filters"""
        if hasattr(self, 'type_filter'):
            self.type_filter.setCurrentIndex(0)
        if hasattr(self, 'category_filter'):
            self.category_filter.setCurrentIndex(0)
        if hasattr(self, 'stock_filter'):
            self.stock_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.filter_products()
    
    def load_products_data(self):
        """Load products data into table"""
        try:
            products = db.get_products()
            
            if products:
                products_list = []
                for product in products:
                    product_dict = dict(product) if hasattr(product, 'keys') else product
                    products_list.append(product_dict)
                self.all_products_data = products_list
                self.update_category_filter(products_list)
                self.populate_table(products_list)
                self.update_stats(products_list)
            else:
                print("Database is empty, loading sample data...")
                self.load_sample_data()
                
        except Exception as e:
            print(f"Database error, using sample data: {e}")
            self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = [
            {
                'id': 1, 'name': 'Dell Laptop XPS 13', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'LAP001', 'sales_rate': 75000, 'stock_quantity': 25,
                'low_stock_alert': 5, 'unit': 'Piece'
            },
            {
                'id': 2, 'name': 'iPhone 14 Pro', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'PHN001', 'sales_rate': 120000, 'stock_quantity': 15,
                'low_stock_alert': 3, 'unit': 'Piece'
            },
            {
                'id': 3, 'name': 'Web Development Service', 'type': 'Service', 'category': 'Professional',
                'sku': 'SRV001', 'sales_rate': 50000, 'stock_quantity': 0,
                'low_stock_alert': 0, 'unit': 'Hour'
            },
            {
                'id': 4, 'name': 'Office Chair', 'type': 'Goods', 'category': 'Furniture',
                'sku': 'FUR001', 'sales_rate': 8500, 'stock_quantity': 2,
                'low_stock_alert': 5, 'unit': 'Piece'
            },
            {
                'id': 5, 'name': 'Wireless Mouse', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'ACC001', 'sales_rate': 2500, 'stock_quantity': 50,
                'low_stock_alert': 10, 'unit': 'Piece'
            },
            {
                'id': 6, 'name': 'Digital Marketing', 'type': 'Service', 'category': 'Marketing',
                'sku': 'SRV002', 'sales_rate': 25000, 'stock_quantity': 0,
                'low_stock_alert': 0, 'unit': 'Project'
            }
        ]
        self.all_products_data = sample_data
        self.update_category_filter(sample_data)
        self.populate_table(sample_data)
        self.update_stats(sample_data)
    
    def update_category_filter(self, products):
        """Update category filter with available categories"""
        categories = set()
        for product in products:
            if product.get('category'):
                categories.add(product['category'])
        
        if hasattr(self, 'category_filter'):
            combo = self.category_filter
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("All Categories")
            for category in sorted(categories):
                combo.addItem(category)
            combo.blockSignals(False)
    
    def populate_table(self, products_data):
        """Populate table with products data"""
        self.products_table.setRowCount(len(products_data))
        
        for row, product in enumerate(products_data):
            self.products_table.setRowHeight(row, 56)
            
            # Column 0: Row number
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor(TEXT_SECONDARY))
            self.products_table.setItem(row, 0, num_item)
            
            # Column 1: Product name with icon
            product_type = product.get('product_type', '')
            type_icon = "📦" if product_type == "Goods" else "🔧"
            name_display = f"{type_icon}  {product.get('name', '')}"
            name_item = QTableWidgetItem(name_display)
            name_item.setFont(QFont("Arial", 12, QFont.DemiBold))
            self.products_table.setItem(row, 1, name_item)
            
            # Column 2: Type badge
            type_item = QTableWidgetItem(product_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 2, type_item)
            
            # Column 3: Price
            price = product.get('sales_rate', 0) or 0
            price_display = f"₹{price:,.2f}"
            price_item = QTableWidgetItem(price_display)
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setFont(QFont("Arial", 12, QFont.DemiBold))
            self.products_table.setItem(row, 3, price_item)
            
            # Column 4: Stock - use current_stock if available, fallback to opening_stock
            stock = product.get('current_stock', product.get('opening_stock', product.get('stock_quantity', 0))) or 0
            unit = product.get('unit', 'Piece')
            if product_type == 'Service':
                stock_text = "∞"
            else:
                stock_text = f"{int(stock)} {unit}"
            stock_item = QTableWidgetItem(stock_text)
            stock_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 4, stock_item)
            
            # Column 5: Status with color
            status = self.get_stock_status(product)
            status_widget = self.create_status_badge(status)
            self.products_table.setCellWidget(row, 5, status_widget)
            
            # Column 6: Action buttons
            actions_widget = self.create_action_buttons(product)
            self.products_table.setCellWidget(row, 6, actions_widget)
    
    def create_status_badge(self, status):
        """Create a colored status badge"""
        badge = QLabel(status)
        badge.setAlignment(Qt.AlignCenter)
        
        if status == "In Stock":
            color = SUCCESS
            bg = "#ECFDF5"
        elif status == "Low Stock":
            color = WARNING
            bg = "#FFFBEB"
        elif status == "Out of Stock":
            color = DANGER
            bg = "#FEF2F2"
        else:  # Service
            color = PRIMARY
            bg = "#EEF2FF"
        
        badge.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: {bg};
                padding: 6px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge)
        
        return container
    
    def get_stock_status(self, product):
        """Get stock status for a product"""
        if product.get('type', '').lower() == 'service':
            return "Service"
        
        # Use current_stock if available, fallback to opening_stock
        stock = product.get('current_stock', product.get('opening_stock', product.get('stock_quantity', 0))) or 0
        low_stock_alert = product.get('low_stock', product.get('low_stock_alert', 5)) or 5
        
        if stock <= 0:
            return "Out of Stock"
        elif stock <= low_stock_alert:
            return "Low Stock"
        else:
            return "In Stock"
    
    def create_action_buttons(self, product):
        """Create modern action buttons for each row"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        widget.setFixedHeight(40)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Action buttons - same style as parties
        actions = [
            ("Edit", "Edit Product", lambda _, p=product: self.edit_product(p), "#EEF2FF", PRIMARY),
            ("Del", "Delete Product", lambda _, p=product: self.delete_product(p), "#FEE2E2", DANGER)
        ]
        
        for text, tooltip, callback, bg_color, hover_color in actions:
            btn = QPushButton(text)
            btn.setFixedSize(42, 26)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    background: {bg_color};
                    font-size: 11px;
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
    
    def update_stats(self, products):
        """Update statistics with real data"""
        total = len(products)
        in_stock = sum(1 for p in products if self.get_stock_status(p) == "In Stock")
        low_stock = sum(1 for p in products if self.get_stock_status(p) == "Low Stock")
        out_stock = sum(1 for p in products if self.get_stock_status(p) == "Out of Stock")
        
        # Update stat cards
        if hasattr(self, 'stat_labels'):
            if 'total' in self.stat_labels:
                self.stat_labels['total'].setText(str(total))
            if 'in_stock' in self.stat_labels:
                self.stat_labels['in_stock'].setText(str(in_stock))
            if 'low_stock' in self.stat_labels:
                self.stat_labels['low_stock'].setText(str(low_stock))
            if 'out_stock' in self.stat_labels:
                self.stat_labels['out_stock'].setText(str(out_stock))
        
        # Update count label
        if hasattr(self, 'count_label'):
            self.count_label.setText(f"{total} products")
    
    def filter_products(self):
        """Filter products based on search and dropdown filters"""
        search_text = self.search_input.text().lower()
        
        # Get filter values using new attribute names
        type_text = self.type_filter.currentText() if hasattr(self, 'type_filter') else 'All'
        category_text = self.category_filter.currentText() if hasattr(self, 'category_filter') else 'All Categories'
        stock_text = self.stock_filter.currentText() if hasattr(self, 'stock_filter') else 'All'
        
        filtered_data = []
        for product in self.all_products_data:
            # Search filter
            if search_text:
                search_fields = [
                    (product.get('name') or '').lower(),
                    (product.get('sku') or '').lower(),
                    (product.get('category') or '').lower()
                ]
                if not any(search_text in field for field in search_fields):
                    continue
            
            # Type filter
            if type_text != "All" and product.get('type', '') != type_text:
                continue
            
            # Category filter
            if category_text != "All Categories" and product.get('category', '') != category_text:
                continue
            
            # Stock status filter
            status = self.get_stock_status(product)
            if stock_text != "All" and status != stock_text:
                continue
            
            filtered_data.append(product)
        
        self.populate_table(filtered_data)
        
        # Update count label with filter info
        if hasattr(self, 'count_label'):
            if len(filtered_data) == len(self.all_products_data):
                self.count_label.setText(f"{len(self.all_products_data)} products")
            else:
                self.count_label.setText(f"Showing {len(filtered_data)} of {len(self.all_products_data)}")
    
    def add_product(self):
        """Open add product dialog"""
        dialog = ProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products_data()
    
    def edit_product(self, product):
        """Open edit product dialog"""
        dialog = ProductDialog(self, product)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products_data()
    
    def delete_product(self, product):
        """Delete product with confirmation"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Are you sure you want to delete '{product.get('name', '')}'?")
        msg_box.setInformativeText("This action cannot be undone.")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {WHITE};
            }}
            QPushButton {{
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 500;
            }}
        """)
        
        if msg_box.exec_() == QMessageBox.Yes:
            try:
                db.delete_product(product['id'])
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
    
    def export_products(self):
        """Export products data"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")
    
    def import_products(self):
        """Import products data"""
        QMessageBox.information(self, "Import", "Import functionality will be implemented soon!")
