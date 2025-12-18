"""
Products screen - Manage inventory and services
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, get_title_font
)
from database import db

class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Add Product" if not product_data else "Edit Product")
        self.setModal(True)
        self.setFixedSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Add New Product" if not self.product_data else "Edit Product")
        title.setFont(get_title_font(20))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {BORDER};
                background: {WHITE};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {WHITE};
                border-bottom: 1px solid {WHITE};
            }}
        """)
        
        # Basic Info Tab
        basic_tab = self.create_basic_info_tab()
        tab_widget.addTab(basic_tab, "Basic Info")
        
        # Pricing Tab
        pricing_tab = self.create_pricing_tab()
        tab_widget.addTab(pricing_tab, "Pricing & Tax")
        
        # Stock Tab
        stock_tab = self.create_stock_tab()
        tab_widget.addTab(stock_tab, "Stock & Units")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = CustomButton("Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = CustomButton("Save Product", "primary")
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Populate form if editing
        if self.product_data:
            self.populate_form()
    
    def create_basic_info_tab(self):
        """Create basic information tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Product Name
        self.name_input = CustomInput("Enter product name")
        self.name_input.setFixedHeight(40)
        layout.addRow("Product Name *:", self.name_input)
        
        # Product Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Goods", "Service"])
        self.type_combo.setFixedHeight(40)
        self.type_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        layout.addRow("Type:", self.type_combo)
        
        # Category
        self.category_input = CustomInput("e.g., Electronics, Clothing, etc.")
        self.category_input.setFixedHeight(40)
        layout.addRow("Category:", self.category_input)
        
        # Brand
        self.brand_input = CustomInput("Enter brand name")
        self.brand_input.setFixedHeight(40)
        layout.addRow("Brand:", self.brand_input)
        
        # SKU/Code
        self.sku_input = CustomInput("Enter product code/SKU")
        self.sku_input.setFixedHeight(40)
        layout.addRow("Product Code:", self.sku_input)
        
        # Barcode
        self.barcode_input = CustomInput("Enter barcode")
        self.barcode_input.setFixedHeight(40)
        layout.addRow("Barcode:", self.barcode_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description")
        self.description_input.setFixedHeight(80)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: {WHITE};
            }}
        """)
        layout.addRow("Description:", self.description_input)
        
        return tab
    
    def create_pricing_tab(self):
        """Create pricing and tax tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Purchase Price
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 999999.99)
        self.purchase_price.setDecimals(2)
        self.purchase_price.setFixedHeight(40)
        self.purchase_price.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        layout.addRow("Purchase Price:", self.purchase_price)
        
        # Selling Price
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 999999.99)
        self.selling_price.setDecimals(2)
        self.selling_price.setFixedHeight(40)
        self.selling_price.setStyleSheet(self.purchase_price.styleSheet())
        layout.addRow("Selling Price *:", self.selling_price)
        
        # MRP
        self.mrp = QDoubleSpinBox()
        self.mrp.setRange(0, 999999.99)
        self.mrp.setDecimals(2)
        self.mrp.setFixedHeight(40)
        self.mrp.setStyleSheet(self.purchase_price.styleSheet())
        layout.addRow("MRP:", self.mrp)
        
        # Tax Information
        tax_frame = QFrame()
        tax_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                background: {BACKGROUND};
                padding: 15px;
            }}
        """)
        tax_layout = QFormLayout(tax_frame)
        
        tax_title = QLabel("Tax Information")
        tax_title.setFont(QFont("Arial", 12, QFont.Bold))
        tax_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; margin-bottom: 10px;")
        tax_layout.addRow("", tax_title)
        
        # Tax Rate
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setDecimals(2)
        self.tax_rate.setValue(18.0)  # Default GST rate
        self.tax_rate.setSuffix("%")
        self.tax_rate.setFixedHeight(35)
        self.tax_rate.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                background: {WHITE};
            }}
        """)
        tax_layout.addRow("Tax Rate (GST):", self.tax_rate)
        
        # HSN Code
        self.hsn_code = CustomInput("Enter HSN/SAC code")
        self.hsn_code.setFixedHeight(35)
        tax_layout.addRow("HSN/SAC Code:", self.hsn_code)
        
        # Tax Inclusive checkbox
        self.tax_inclusive = QCheckBox("Price is inclusive of tax")
        self.tax_inclusive.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
        """)
        tax_layout.addRow("", self.tax_inclusive)
        
        layout.addRow("", tax_frame)
        
        return tab
    
    def create_stock_tab(self):
        """Create stock and units tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Units
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "Piece", "Kg", "Gram", "Liter", "Meter", "Box", "Packet", 
            "Dozen", "Set", "Hour", "Service", "Nos"
        ])
        self.unit_combo.setEditable(True)
        self.unit_combo.setFixedHeight(40)
        self.unit_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        layout.addRow("Unit:", self.unit_combo)
        
        # Stock tracking checkbox
        self.track_stock = QCheckBox("Track stock for this product")
        self.track_stock.setChecked(True)
        self.track_stock.stateChanged.connect(self.toggle_stock_fields)
        self.track_stock.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
                color: {TEXT_PRIMARY};
                margin: 10px 0;
            }}
        """)
        layout.addRow("", self.track_stock)
        
        # Stock fields (only shown if tracking is enabled)
        self.stock_frame = QFrame()
        stock_layout = QFormLayout(self.stock_frame)
        
        # Opening Stock
        self.opening_stock = QSpinBox()
        self.opening_stock.setRange(0, 999999)
        self.opening_stock.setFixedHeight(40)
        self.opening_stock.setStyleSheet(f"""
            QSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        stock_layout.addRow("Opening Stock:", self.opening_stock)
        
        # Low Stock Alert
        self.low_stock_alert = QSpinBox()
        self.low_stock_alert.setRange(0, 999999)
        self.low_stock_alert.setValue(10)
        self.low_stock_alert.setFixedHeight(40)
        self.low_stock_alert.setStyleSheet(self.opening_stock.styleSheet())
        stock_layout.addRow("Low Stock Alert:", self.low_stock_alert)
        
        # Location/Warehouse
        self.location_input = CustomInput("Enter storage location")
        self.location_input.setFixedHeight(40)
        stock_layout.addRow("Location:", self.location_input)
        
        layout.addRow("", self.stock_frame)
        
        return tab
    
    def toggle_stock_fields(self, state):
        """Toggle stock fields based on checkbox"""
        self.stock_frame.setVisible(state == Qt.Checked)
    
    def populate_form(self):
        """Populate form with existing product data"""
        data = self.product_data
        
        # Basic info
        self.name_input.setText(data.get('name', ''))
        
        type_index = self.type_combo.findText(data.get('type', 'Goods'))
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.category_input.setText(data.get('category', ''))
        self.brand_input.setText(data.get('brand', ''))
        self.sku_input.setText(data.get('sku', ''))
        self.barcode_input.setText(data.get('barcode', ''))
        self.description_input.setPlainText(data.get('description', ''))
        
        # Pricing
        self.purchase_price.setValue(data.get('purchase_price', 0))
        self.selling_price.setValue(data.get('selling_price', 0))
        self.mrp.setValue(data.get('mrp', 0))
        self.tax_rate.setValue(data.get('tax_rate', 18))
        self.hsn_code.setText(data.get('hsn_code', ''))
        self.tax_inclusive.setChecked(data.get('tax_inclusive', False))
        
        # Stock
        unit_index = self.unit_combo.findText(data.get('unit', 'Piece'))
        if unit_index >= 0:
            self.unit_combo.setCurrentIndex(unit_index)
        
        self.track_stock.setChecked(data.get('track_stock', True))
        self.opening_stock.setValue(data.get('stock_quantity', 0))
        self.low_stock_alert.setValue(data.get('low_stock_alert', 10))
        self.location_input.setText(data.get('location', ''))
    
    def save_product(self):
        """Save product data"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required!")
            return
        
        selling_price = self.selling_price.value()
        if selling_price <= 0:
            QMessageBox.warning(self, "Error", "Selling price must be greater than 0!")
            return
        
        product_data = {
            'name': name,
            'type': self.type_combo.currentText(),
            'category': self.category_input.text().strip(),
            'brand': self.brand_input.text().strip(),
            'sku': self.sku_input.text().strip(),
            'barcode': self.barcode_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'purchase_price': self.purchase_price.value(),
            'selling_price': selling_price,
            'mrp': self.mrp.value(),
            'tax_rate': self.tax_rate.value(),
            'hsn_code': self.hsn_code.text().strip(),
            'tax_inclusive': self.tax_inclusive.isChecked(),
            'unit': self.unit_combo.currentText(),
            'track_stock': self.track_stock.isChecked(),
            'stock_quantity': self.opening_stock.value() if self.track_stock.isChecked() else 0,
            'low_stock_alert': self.low_stock_alert.value() if self.track_stock.isChecked() else 0,
            'location': self.location_input.text().strip()
        }
        
        try:
            if self.product_data:  # Editing
                product_data['id'] = self.product_data['id']
                db.update_product(product_data)
                QMessageBox.information(self, "Success", "Product updated successfully!")
            else:  # Adding new
                db.add_product(product_data)
                QMessageBox.information(self, "Success", "Product added successfully!")
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")

class ProductsScreen(BaseScreen):
    def __init__(self):
        super().__init__("Products & Services")
        self.setup_products_screen()
        self.load_products_data()
    
    def setup_products_screen(self):
        """Setup products screen content"""
        # Top action bar
        self.setup_action_bar()
        
        # Filters and stats
        self.setup_filters_and_stats()
        
        # Products table
        self.setup_products_table()
    
    def setup_action_bar(self):
        """Setup top action bar"""
        action_layout = QHBoxLayout()
        
        # Search
        self.search_input = CustomInput("Search products...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_products)
        action_layout.addWidget(self.search_input)
        
        action_layout.addStretch()
        
        # Export button
        export_btn = CustomButton("Export", "secondary")
        export_btn.clicked.connect(self.export_products)
        action_layout.addWidget(export_btn)
        
        # Import button
        import_btn = CustomButton("Import", "secondary")
        import_btn.clicked.connect(self.import_products)
        action_layout.addWidget(import_btn)
        
        # Add product button
        add_btn = CustomButton("Add Product", "primary")
        add_btn.clicked.connect(self.add_product)
        action_layout.addWidget(add_btn)
        
        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        self.add_content(action_widget)
    
    def setup_filters_and_stats(self):
        """Setup filters and quick stats"""
        container = QHBoxLayout()
        
        # Filters section
        filters_layout = QHBoxLayout()
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Goods", "Service"])
        self.type_filter.setFixedWidth(100)
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                background: {WHITE};
            }}
        """)
        self.type_filter.currentTextChanged.connect(self.filter_products)
        filters_layout.addWidget(self.type_filter)
        
        filters_layout.addSpacing(20)
        
        # Category filter
        filters_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories"])
        self.category_filter.setFixedWidth(150)
        self.category_filter.setStyleSheet(self.type_filter.styleSheet())
        self.category_filter.currentTextChanged.connect(self.filter_products)
        filters_layout.addWidget(self.category_filter)
        
        filters_layout.addSpacing(20)
        
        # Stock filter
        filters_layout.addWidget(QLabel("Stock:"))
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(["All", "In Stock", "Low Stock", "Out of Stock"])
        self.stock_filter.setFixedWidth(120)
        self.stock_filter.setStyleSheet(self.type_filter.styleSheet())
        self.stock_filter.currentTextChanged.connect(self.filter_products)
        filters_layout.addWidget(self.stock_filter)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.addStretch()
        
        # Total products
        self.total_products_label = QLabel("Total: 0")
        self.total_products_label.setStyleSheet(f"""
            background: {PRIMARY}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.total_products_label)
        
        # Low stock alert
        self.low_stock_label = QLabel("Low Stock: 0")
        self.low_stock_label.setStyleSheet(f"""
            background: {WARNING}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.low_stock_label)
        
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
        refresh_btn.clicked.connect(self.load_products_data)
        stats_layout.addWidget(refresh_btn)
        
        container.addLayout(filters_layout)
        container.addLayout(stats_layout)
        
        container_widget = QWidget()
        container_widget.setLayout(container)
        self.add_content(container_widget)
    
    def setup_products_table(self):
        """Setup products data table"""
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
        headers = ["Name", "Type", "Category", "SKU", "Price", "Stock", "Status", "Actions"]
        self.products_table = CustomTable(0, len(headers), headers)
        
        # Set column widths
        self.products_table.setColumnWidth(0, 200)  # Name
        self.products_table.setColumnWidth(1, 80)   # Type
        self.products_table.setColumnWidth(2, 120)  # Category
        self.products_table.setColumnWidth(3, 100)  # SKU
        self.products_table.setColumnWidth(4, 100)  # Price
        self.products_table.setColumnWidth(5, 80)   # Stock
        self.products_table.setColumnWidth(6, 100)  # Status
        self.products_table.setColumnWidth(7, 120)  # Actions
        
        table_layout.addWidget(self.products_table)
        self.add_content(table_frame)
        
        # Store original data for filtering
        self.all_products_data = []
    
    def load_products_data(self):
        """Load products data into table"""
        try:
            products = db.get_products()
            self.all_products_data = products
            self.update_category_filter(products)
            self.populate_table(products)
            self.update_stats(products)
        except Exception as e:
            # Show sample data if database not available
            sample_data = [
                {
                    'id': 1, 'name': 'Laptop', 'type': 'Goods', 'category': 'Electronics',
                    'sku': 'LAP001', 'selling_price': 45000, 'stock_quantity': 10,
                    'low_stock_alert': 5
                },
                {
                    'id': 2, 'name': 'Consulting Service', 'type': 'Service', 'category': 'Professional',
                    'sku': 'SRV001', 'selling_price': 2000, 'stock_quantity': 0,
                    'low_stock_alert': 0
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
        
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        for category in sorted(categories):
            self.category_filter.addItem(category)
    
    def populate_table(self, products_data):
        """Populate table with products data"""
        self.products_table.setRowCount(len(products_data))
        
        for row, product in enumerate(products_data):
            self.products_table.setItem(row, 0, self.products_table.create_item(product['name']))
            self.products_table.setItem(row, 1, self.products_table.create_item(product['type']))
            self.products_table.setItem(row, 2, self.products_table.create_item(product.get('category', '')))
            self.products_table.setItem(row, 3, self.products_table.create_item(product.get('sku', '')))
            self.products_table.setItem(row, 4, self.products_table.create_item(f"₹{product['selling_price']:,.2f}"))
            
            # Stock display
            stock = product.get('stock_quantity', 0)
            if product['type'] == 'Service':
                stock_text = "N/A"
            else:
                stock_text = str(stock)
            self.products_table.setItem(row, 5, self.products_table.create_item(stock_text))
            
            # Status
            status = self.get_stock_status(product)
            status_item = self.products_table.create_item(status)
            
            # Color code status
            if status == "Low Stock":
                status_item.setBackground(status_item.background().color().lighter(180))
            elif status == "Out of Stock":
                status_item.setBackground(status_item.background().color().darker(120))
            
            self.products_table.setItem(row, 6, status_item)
            
            # Action buttons
            actions_widget = self.create_action_buttons(product)
            self.products_table.setCellWidget(row, 7, actions_widget)
    
    def get_stock_status(self, product):
        """Get stock status for product"""
        if product['type'] == 'Service':
            return "Service"
        
        stock = product.get('stock_quantity', 0)
        low_stock_alert = product.get('low_stock_alert', 0)
        
        if stock <= 0:
            return "Out of Stock"
        elif stock <= low_stock_alert:
            return "Low Stock"
        else:
            return "In Stock"
    
    def create_action_buttons(self, product):
        """Create action buttons for each row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setStyleSheet(f"""
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
        edit_btn.clicked.connect(lambda: self.edit_product(product))
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
        delete_btn.clicked.connect(lambda: self.delete_product(product))
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_stats(self, products):
        """Update quick stats labels"""
        total = len(products)
        low_stock_count = sum(1 for p in products if self.get_stock_status(p) == "Low Stock")
        
        self.total_products_label.setText(f"Total: {total}")
        self.low_stock_label.setText(f"Low Stock: {low_stock_count}")
    
    def filter_products(self):
        """Filter products based on search and filters"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()
        stock_filter = self.stock_filter.currentText()
        
        filtered_data = []
        for product in self.all_products_data:
            # Search filter
            if search_text and search_text not in product['name'].lower():
                continue
            
            # Type filter
            if type_filter != "All" and product['type'] != type_filter:
                continue
            
            # Category filter
            if category_filter != "All Categories" and product.get('category', '') != category_filter:
                continue
            
            # Stock filter
            stock_status = self.get_stock_status(product)
            if stock_filter == "In Stock" and stock_status != "In Stock":
                continue
            elif stock_filter == "Low Stock" and stock_status != "Low Stock":
                continue
            elif stock_filter == "Out of Stock" and stock_status != "Out of Stock":
                continue
            
            filtered_data.append(product)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
    
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
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{product['name']}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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
    
    def refresh_data(self):
        """Refresh products data"""
        self.load_products_data()
