"""
Products screen - Manage inventory and services
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_title_font
)
from database import db

class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Add Product" if not product_data else "Edit Product")
        self.setModal(True)
        self.setFixedSize(900, 900)
        # self.setup_ui_old()
        self.build_ui()
    
    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        # Title
        title = QLabel("Add Product")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; padding: 2px 0px 2px 0px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)

        # Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)
        form_frame.setMinimumWidth(600)
        form_frame.setMinimumHeight(500)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(18)

        # HSN Code & Item Name (side by side)
        row_hsn_item = QHBoxLayout()
        row_hsn_item.setSpacing(16)
        item_col = QVBoxLayout()
        item_col.addWidget(self.label("Item Name"))
        self.name_input = self.input()
        self.name_input.setPlaceholderText("Enter Item Name")
        item_col.addWidget(self.name_input)
        hsn_col = QVBoxLayout()
        hsn_col.addWidget(self.label("HSN Code"))
        self.hsn_code = self.input()
        self.hsn_code.setPlaceholderText("Enter HSN Code")
        hsn_col.addWidget(self.hsn_code)
        row_hsn_item.addLayout(item_col)
        row_hsn_item.addSpacing(16)
        row_hsn_item.addLayout(hsn_col)
        form_layout.addLayout(row_hsn_item)

        # Unit of Measure & Barcode (side by side)
        row_uom_barcode = QHBoxLayout()
        row_uom_barcode.setSpacing(16)
        barcode_col = QVBoxLayout()
        barcode_col.addWidget(self.label("Barcode / SKU"))
        self.barcode_input = self.input()
        self.barcode_input.setPlaceholderText("Enter Barcode or SKU")
        barcode_col.addWidget(self.barcode_input)
        uom_col = QVBoxLayout()
        uom_col.addWidget(self.label("Unit of Measure"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["PCS", "KG", "LTR", "BOX"])
        self.unit_combo.setMinimumHeight(40)
        self.unit_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
                font-size: 16px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {PRIMARY};
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
        """)
        uom_col.addWidget(self.unit_combo)
        row_uom_barcode.addLayout(barcode_col, 1)
        row_uom_barcode.addSpacing(16)
        row_uom_barcode.addLayout(uom_col, 1)
        form_layout.addLayout(row_uom_barcode)

        # Sales Rate & Purchase Rate (side by side)
        row_sales_purchase = QHBoxLayout()
        row_sales_purchase.setSpacing(16)
        sales_col = QVBoxLayout()
        sales_col.addWidget(self.label("Sales Rate"))
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 999999.99)
        self.selling_price.setDecimals(2)
        self.selling_price.setMinimumHeight(40)
        self.selling_price.setStyleSheet(self.input_style())
        sales_col.addWidget(self.selling_price)
        purchase_col = QVBoxLayout()
        purchase_col.addWidget(self.label("Purchase Rate"))
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 999999.99)
        self.purchase_price.setDecimals(2)
        self.purchase_price.setMinimumHeight(40)
        self.purchase_price.setStyleSheet(self.input_style())
        purchase_col.addWidget(self.purchase_price)
        row_sales_purchase.addLayout(sales_col)
        row_sales_purchase.addSpacing(16)
        row_sales_purchase.addLayout(purchase_col)
        form_layout.addLayout(row_sales_purchase)


        # Discount & MRP (side by side)
        row_discount_mrp = QHBoxLayout()
        row_discount_mrp.setSpacing(16)
        discount_col = QVBoxLayout()
        discount_col.addWidget(self.label("Discount %"))
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix("%")
        self.discount_input.setMinimumHeight(40)
        self.discount_input.setStyleSheet(self.input_style())
        discount_col.addWidget(self.discount_input)
        mrp_col = QVBoxLayout()
        mrp_col.addWidget(self.label("MRP"))
        self.mrp = QDoubleSpinBox()
        self.mrp.setRange(0, 999999.99)
        self.mrp.setDecimals(2)
        self.mrp.setMinimumHeight(40)
        self.mrp.setStyleSheet(self.input_style())
        mrp_col.addWidget(self.mrp)
        row_discount_mrp.addLayout(discount_col)
        row_discount_mrp.addSpacing(16)
        row_discount_mrp.addLayout(mrp_col)
        form_layout.addLayout(row_discount_mrp)

        # Tax Rate (GST)
        row_tax = QHBoxLayout()
        row_tax.setSpacing(16)
        tax_col = QVBoxLayout()
        tax_col.addWidget(self.label("Tax Rate (GST) %"))
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setDecimals(2)
        self.tax_rate.setValue(18.0)  # Default GST rate
        self.tax_rate.setMinimumHeight(40)
        self.tax_rate.setStyleSheet(self.input_style())
        tax_col.addWidget(self.tax_rate)
        
        # Tax inclusive checkbox
        checkbox_col = QVBoxLayout()
        checkbox_col.addWidget(self.label("Tax Options"))
        self.tax_inclusive = QCheckBox("Price is inclusive of tax")
        self.tax_inclusive.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY};")
        checkbox_col.addWidget(self.tax_inclusive)
        
        row_tax.addLayout(tax_col)
        row_tax.addSpacing(16)
        row_tax.addLayout(checkbox_col)
        form_layout.addLayout(row_tax)

        # Opening Qty & Low Stock Alert (side by side)
        row_opening = QHBoxLayout()
        row_opening.setSpacing(16)
        qty_col = QVBoxLayout()
        qty_col.addWidget(self.label("Opening Stock"))
        self.opening_stock = QSpinBox()
        self.opening_stock.setRange(0, 999999)
        self.opening_stock.setMinimumHeight(40)
        self.opening_stock.setStyleSheet(self.input_style())
        qty_col.addWidget(self.opening_stock)
        alert_col = QVBoxLayout()
        alert_col.addWidget(self.label("Low Stock Alert"))
        self.low_stock_alert = QSpinBox()
        self.low_stock_alert.setRange(0, 999999)
        self.low_stock_alert.setValue(10)
        self.low_stock_alert.setMinimumHeight(40)
        self.low_stock_alert.setStyleSheet(self.input_style())
        alert_col.addWidget(self.low_stock_alert)
        row_opening.addLayout(qty_col)
        row_opening.addSpacing(16)
        row_opening.addLayout(alert_col)
        form_layout.addLayout(row_opening)

        # Additional Product Details
        row_additional = QHBoxLayout()
        row_additional.setSpacing(16)
        
        # Product Type
        type_col = QVBoxLayout()
        type_col.addWidget(self.label("Product Type"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Goods", "Service"])
        self.type_combo.setMinimumHeight(40)
        self.type_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
                font-size: 16px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {PRIMARY};
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
        """)
        type_col.addWidget(self.type_combo)
        
        # Category
        category_col = QVBoxLayout()
        category_col.addWidget(self.label("Category"))
        self.category_input = self.input()
        self.category_input.setPlaceholderText("e.g., Electronics, Clothing")
        category_col.addWidget(self.category_input)
        
        row_additional.addLayout(type_col)
        row_additional.addSpacing(16)
        row_additional.addLayout(category_col)
        form_layout.addLayout(row_additional)

        # Description & Additional Fields
        desc_row = QHBoxLayout()
        desc_row.setSpacing(16)
        
        # Description column
        desc_col = QVBoxLayout()
        desc_col.addWidget(self.label("Description"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description")
        self.description_input.setMinimumHeight(60)
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
                font-size: 16px;
                font-family: Arial;
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY};
            }}
        """)
        desc_col.addWidget(self.description_input)
        
        # Additional fields column
        additional_col = QVBoxLayout()
        
        # Add some spacing at top
        additional_col.addSpacing(20)
        
        # Track stock checkbox
        self.track_stock = QCheckBox("Track stock for this product")
        self.track_stock.setChecked(True)
        self.track_stock.setStyleSheet(f"""
            QCheckBox {{
                font-size: 16px; 
                color: {TEXT_PRIMARY}; 
                margin-top: 10px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {BORDER};
                border-radius: 3px;
                background: {WHITE};
            }}
            QCheckBox::indicator:checked {{
                background: {PRIMARY};
                border-color: {PRIMARY};
            }}
        """)
        additional_col.addWidget(self.track_stock)
        
        desc_row.addLayout(desc_col, 2)
        desc_row.addSpacing(20)
        desc_row.addLayout(additional_col, 1)
        form_layout.addLayout(desc_row)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border-radius: 6px;
                padding: 10px 50px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 2px solid {BORDER};
                border-radius: 6px;
                padding: 10px 50px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {BORDER};
            }}
        """)

        # Connect button signals
        save_btn.clicked.connect(self.save_product)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # Populate form if editing
        if self.product_data:
            self.populate_form()

    def label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 16))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold; border: none;")
        return lbl

    def input(self):
        edit = QLineEdit()
        edit.setStyleSheet(self.input_style())
        edit.setMinimumHeight(40)
        edit.setFont(QFont("Arial", 16))
        return edit

    def input_style(self):
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
                font-size: 16px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border-color: {PRIMARY};
            }}
        """
    
    def populate_form(self):
        """Populate form with existing product data"""
        data = self.product_data
        
        # Basic info
        self.name_input.setText(data.get('name', ''))
        
        type_index = self.type_combo.findText(data.get('type', 'Goods'))
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.category_input.setText(data.get('category', ''))
        self.barcode_input.setText(data.get('barcode', ''))
        self.description_input.setPlainText(data.get('description', ''))
        
        # Pricing
        self.purchase_price.setValue(data.get('purchase_price', 0))
        self.selling_price.setValue(data.get('selling_price', 0))
        self.mrp.setValue(data.get('mrp', 0))
        self.discount_input.setValue(data.get('discount', 0))
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
            'barcode': self.barcode_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'purchase_price': self.purchase_price.value(),
            'selling_price': selling_price,
            'mrp': self.mrp.value(),
            'discount': self.discount_input.value(),
            'tax_rate': self.tax_rate.value(),
            'hsn_code': self.hsn_code.text().strip(),
            'tax_inclusive': self.tax_inclusive.isChecked(),
            'unit': self.unit_combo.currentText(),
            'track_stock': self.track_stock.isChecked(),
            'stock_quantity': self.opening_stock.value() if self.track_stock.isChecked() else 0,
            'low_stock_alert': self.low_stock_alert.value() if self.track_stock.isChecked() else 0
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
        """Setup polished products screen content"""
        # Enhanced action bar with modern styling
        self.setup_action_bar()
        
        # Modern header with statistics cards
        self.setup_header_stats()
        
        # Enhanced filters section
        self.setup_filters()
        
        # Modern products table
        self.setup_products_table()
    
    def setup_header_stats(self):
        """Setup modern header with statistics"""
        stats_layout = QHBoxLayout()
        stats_layout.setObjectName("stats_layout")

        # Create stat cards and store label references
        self.total_products_label, card1 = self.create_stat_card("📦", "Total Products", "0", PRIMARY)
        self.in_stock_label, card2 = self.create_stat_card("📈", "In Stock", "0", SUCCESS)
        self.low_stock_label, card3 = self.create_stat_card("⚠️", "Low Stock", "0", WARNING)
        self.out_stock_label, card4 = self.create_stat_card("❌", "Out of Stock", "0", DANGER)
        
        stats_layout.addWidget(card1)
        stats_layout.addWidget(card2)
        stats_layout.addWidget(card3)
        stats_layout.addWidget(card4)
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.add_content(stats_widget)
    
    def create_stat_card(self, icon, label, value, color):
        """Create a statistics card and return the value label for updates"""
        card = QFrame()
        card.setFixedHeight(100)
        card.setFixedWidth(250)
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: #f8f9fa;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(icon_label)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: #6B7280; font-size: 14px; border: none;")
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(label_widget)
        layout.addLayout(text_layout)
        
        return value_label, card
    
    def setup_action_bar(self):
        """Setup enhanced top action bar"""
        action_frame = QFrame()
        action_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {WHITE}, stop:1 #F8FAFC);
                border: 2px solid {BORDER};
                border-radius: 15px;
                margin: 5px;
                padding: 10px;
            }}
        """)
        
        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(15)
        
        # Enhanced search with icon
        search_container = QFrame()
        search_container.setFixedWidth(350)
        search_container.setFixedHeight(45)
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
        search_icon.setStyleSheet("border: none;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by name, SKU, or category...")
        self.search_input.setAlignment(Qt.AlignLeft)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        
        action_layout.addWidget(search_container)
        action_layout.addStretch()
        
        # Enhanced buttons with icons
        buttons_data = [
            ("📊 Export", "secondary", self.export_products),
            ("📄 Import", "secondary", self.import_products),
            ("➕ Add Product", "primary", self.add_product)
        ]
        
        for text, style, callback in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setMinimumWidth(120)
            btn.clicked.connect(callback)
            
            if style == "primary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {PRIMARY};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: #2563EB;
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
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        border-color: {PRIMARY};
                        background: #f8f9fa;
                    }}
                """)
            
            action_layout.addWidget(btn)
        
        self.add_content(action_frame)
    
    def setup_filters(self):
        """Setup enhanced filter controls"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(25)
        
        # Filter title
        filter_title = QLabel("🎯 Filters")
        filter_title.setFont(QFont("Arial", 14, QFont.Bold))
        filter_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        filter_layout.addWidget(filter_title)
        
        # Modern filter dropdowns
        filters_data = [
            ("Type:", ["All", "Goods", "Service"]),
            ("Category:", ["All Categories"]),
            ("Stock Status:", ["All", "In Stock", "Low Stock", "Out of Stock"]),
            ("Price Range:", ["All", "Under ₹1000", "₹1000-₹10000", "Above ₹10000"])
        ]
        
        self.filter_combos = {}
        
        for label_text, items in filters_data:
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 500; border: none;")
            filter_layout.addWidget(label)
            
            # Combo
            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedHeight(35)
            combo.setFixedWidth(140)
            combo.setStyleSheet(f"""
                QComboBox {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    padding: 6px 12px;
                    background: {WHITE};
                    font-size: 14px;
                    color: {TEXT_PRIMARY};
                }}
                QComboBox:hover {{
                    border-color: {PRIMARY};
                }}
                QComboBox:focus {{
                    border-color: {PRIMARY};
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
                    border: 2px solid {PRIMARY};
                    background: {WHITE};
                    selection-background-color: {PRIMARY};
                    selection-color: white;
                    border-radius: 8px;
                }}
            """)
            combo.currentTextChanged.connect(self.filter_products)
            
            # Store reference for filtering
            filter_key = label_text.lower().replace(":", "").replace(" ", "_")
            self.filter_combos[filter_key] = combo
            
            filter_layout.addWidget(combo)
            filter_layout.addSpacing(10)
        
        filter_layout.addStretch()
        
        # Enhanced action buttons
        action_buttons = [
            ("🔄", "Refresh", self.load_products_data),
            ("🗑️", "Clear Filters", self.clear_filters)
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
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: white;
                    border-color: {PRIMARY};
                }}
                QPushButton:pressed {{
                    background: #1D4ED8;
                }}
            """)
            btn.clicked.connect(callback)
            filter_layout.addWidget(btn)
        
        self.add_content(filter_frame)
    
    def clear_filters(self):
        """Clear all filters"""
        for combo in self.filter_combos.values():
            combo.setCurrentIndex(0)
        self.search_input.clear()
        self.filter_products()
    
    def setup_products_table(self):
        """Setup enhanced products data table"""
        # Modern table container
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                margin: 5px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(25, 25, 25, 25)
        table_layout.setSpacing(15)
        
        # Table header with count
        header_layout = QHBoxLayout()
        
        table_title = QLabel("📦 Products Inventory")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        header_layout.addWidget(table_title)
        
        self.count_label = QLabel("Total: 0 products")
        self.count_label.setStyleSheet(f"color: #6B7280; font-size: 14px; border: none;")
        header_layout.addWidget(self.count_label)
        
        header_layout.addStretch()
        
        # View toggle buttons
        view_buttons = QWidget()
        view_layout = QHBoxLayout(view_buttons)
        view_layout.setSpacing(5)
        view_layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid_view_btn = QPushButton("⊞")
        self.list_view_btn = QPushButton("☰")
        
        for btn in [self.grid_view_btn, self.list_view_btn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    background: {WHITE};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: white;
                }}
            """)
            view_layout.addWidget(btn)
        
        self.list_view_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {PRIMARY};
                border-radius: 6px;
                background: {PRIMARY};
                color: white;
                font-size: 14px;
            }}
        """)
        
        header_layout.addWidget(view_buttons)
        table_layout.addLayout(header_layout)
        
        # Enhanced table
        headers = ["#", "Product Name", "Type", "Category", "SKU", "Price", "Stock", "Status", "Actions"]
        self.products_table = CustomTable(0, len(headers), headers)
        
        # Enhanced table styling
        self.products_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #E5E7EB;
                background-color: {WHITE};
                border: none;
                font-size: 14px;
                selection-background-color: #EEF2FF;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding: 12px 8px;
            }}
            QTableWidget::item:selected {{
                background-color: #EEF2FF;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {TEXT_PRIMARY};
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                padding: 12px 8px;
                font-size: 14px;
            }}
            QHeaderView::section:hover {{
                background-color: #F1F5F9;
            }}
        """)
        
        # Set optimal column widths
        column_widths = [50, 200, 80, 120, 100, 100, 80, 100, 140]
        for i, width in enumerate(column_widths):
            self.products_table.setColumnWidth(i, width)
        
        # Set minimum height for better appearance
        self.products_table.setMinimumHeight(400)
        
        table_layout.addWidget(self.products_table)
        self.add_content(table_frame)
        
        # Store original data for filtering
        self.all_products_data = []
    
    def load_products_data(self):
        """Load products data into table"""
        try:
            products = db.get_products()
            
            # Convert database rows to dictionaries if needed
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
                # Database is empty, load sample data
                print("Database is empty, loading sample data...")
                self.load_sample_data()
                
        except Exception as e:
            # Show enhanced sample data if database not available
            print(f"Database error, using sample data: {e}")
            self.load_sample_data()
    
    def load_sample_data(self):
        """Load enhanced sample data"""
        sample_data = [
            {
                'id': 1, 'name': 'Dell Laptop XPS 13', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'LAP001', 'selling_price': 75000, 'stock_quantity': 25,
                'low_stock_alert': 5, 'brand': 'Dell', 'unit': 'Piece'
            },
            {
                'id': 2, 'name': 'iPhone 14 Pro', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'PHN001', 'selling_price': 120000, 'stock_quantity': 15,
                'low_stock_alert': 3, 'brand': 'Apple', 'unit': 'Piece'
            },
            {
                'id': 3, 'name': 'Web Development Service', 'type': 'Service', 'category': 'Professional',
                'sku': 'SRV001', 'selling_price': 50000, 'stock_quantity': 0,
                'low_stock_alert': 0, 'brand': '', 'unit': 'Hour'
            },
            {
                'id': 4, 'name': 'Office Chair', 'type': 'Goods', 'category': 'Furniture',
                'sku': 'FUR001', 'selling_price': 8500, 'stock_quantity': 2,
                'low_stock_alert': 5, 'brand': 'Herman Miller', 'unit': 'Piece'
            },
            {
                'id': 5, 'name': 'Wireless Mouse', 'type': 'Goods', 'category': 'Electronics',
                'sku': 'ACC001', 'selling_price': 2500, 'stock_quantity': 50,
                'low_stock_alert': 10, 'brand': 'Logitech', 'unit': 'Piece'
            },
            {
                'id': 6, 'name': 'Digital Marketing Service', 'type': 'Service', 'category': 'Marketing',
                'sku': 'SRV002', 'selling_price': 25000, 'stock_quantity': 0,
                'low_stock_alert': 0, 'brand': '', 'unit': 'Project'
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
        
        if 'category' in self.filter_combos:
            combo = self.filter_combos['category']
            combo.clear()
            combo.addItem("All Categories")
            for category in sorted(categories):
                combo.addItem(category)
    
    def populate_table(self, products_data):
        """Populate table with enhanced products data"""
        self.products_table.setRowCount(len(products_data))
        
        for row, product in enumerate(products_data):
            # Column 0: Row number
            self.products_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # Column 1: Product name with icon
            product_type = product.get('type', '')
            type_icon = "📦" if product_type == "Goods" else "🔧"
            name_display = f"{type_icon} {product.get('name', '')}"
            self.products_table.setItem(row, 1, QTableWidgetItem(name_display))
            
            # Column 2: Type with styling
            self.products_table.setItem(row, 2, QTableWidgetItem(product.get('type', '')))
            
            # Column 3: Category
            self.products_table.setItem(row, 3, QTableWidgetItem(product.get('category', 'N/A')))
            
            # Column 4: SKU
            self.products_table.setItem(row, 4, QTableWidgetItem(product.get('sku', 'N/A')))
            
            # Column 5: Price with currency
            price_display = f"₹{product.get('selling_price', 0):,.2f}"
            self.products_table.setItem(row, 5, QTableWidgetItem(price_display))
            
            # Column 6: Stock display with units
            stock = product.get('stock_quantity', 0)
            unit = product.get('unit', 'Piece')
            if product.get('type', '') == 'Service':
                stock_text = "∞"
            else:
                stock_text = f"{stock} {unit}"
            self.products_table.setItem(row, 6, QTableWidgetItem(stock_text))
            
            # Column 7: Status with color coding
            status = self.get_stock_status(product)
            status_item = QTableWidgetItem(status)
            
            # Color code status
            if status == "In Stock":
                status_item.setBackground(Qt.green)
                status_item.setForeground(Qt.white)
            elif status == "Low Stock":
                status_item.setBackground(Qt.yellow)
                status_item.setForeground(Qt.black)
            elif status == "Out of Stock":
                status_item.setBackground(Qt.red)
                status_item.setForeground(Qt.white)
            
            self.products_table.setItem(row, 7, status_item)
            
            # Column 8: Action buttons
            actions_widget = self.create_action_buttons(product)
            self.products_table.setCellWidget(row, 8, actions_widget)
    
    def update_stats(self, products_data):
        """Update statistics with real data"""
        try:
            total_products = len(products_data)
            in_stock = len([p for p in products_data if self.get_stock_status(p) == "In Stock"])
            low_stock = len([p for p in products_data if self.get_stock_status(p) == "Low Stock"])
            out_of_stock = len([p for p in products_data if self.get_stock_status(p) == "Out of Stock"])
            
            # Update count label
            if hasattr(self, 'count_label'):
                self.count_label.setText(f"📊 Total: {total_products} products")
            
            # Print stats for debugging
            print(f"Product Stats - Total: {total_products}, In Stock: {in_stock}, "
                  f"Low Stock: {low_stock}, Out of Stock: {out_of_stock}")
                  
        except Exception as e:
            print(f"Error updating product stats: {e}")
    
    def get_stock_status(self, product):
        """Get stock status for a product"""
        if product.get('type', '').lower() == 'service':
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
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(25, 25)
        view_btn.setToolTip("View Details")
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
        view_btn.clicked.connect(lambda: self.view_product(product))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setToolTip("Edit Product")
        edit_btn.setStyleSheet(f"""
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
        edit_btn.clicked.connect(lambda: self.edit_product(product))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(25, 25)
        delete_btn.setToolTip("Delete Product")
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
    
    def filter_products(self):
        """Enhanced filter products based on search and multiple filters"""
        search_text = self.search_input.text().lower()
        
        # Get filter values safely
        type_filter = self.filter_combos.get('type', type('', (), {'currentText': lambda: 'All'}))
        category_filter = self.filter_combos.get('category', type('', (), {'currentText': lambda: 'All Categories'}))
        stock_filter = self.filter_combos.get('stock_status', type('', (), {'currentText': lambda: 'All'}))
        
        type_text = type_filter.currentText() if hasattr(type_filter, 'currentText') else 'All'
        category_text = category_filter.currentText() if hasattr(category_filter, 'currentText') else 'All Categories'
        stock_text = stock_filter.currentText() if hasattr(stock_filter, 'currentText') else 'All'
        
        filtered_data = []
        for product in self.all_products_data:
            # Search filter (name, SKU, category)
            if search_text:
                search_fields = [
                    product.get('name', '').lower(),
                    product.get('sku', '').lower(),
                    product.get('category', '').lower()
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
        self.update_stats(filtered_data)
        
        # Update count
        if hasattr(self, 'count_label'):
            if len(filtered_data) == len(self.all_products_data):
                self.count_label.setText(f"📊 Total: {len(self.all_products_data)} products")
            else:
                self.count_label.setText(f"🔍 Showing: {len(filtered_data)} of {len(self.all_products_data)} products")
    
    def get_stock_status(self, product):
        """Get stock status for product"""
        if product.get('type', '').lower() == 'service':
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
        in_stock_count = sum(1 for p in products if self.get_stock_status(p) == "In Stock")
        low_stock_count = sum(1 for p in products if self.get_stock_status(p) == "Low Stock")
        out_stock_count = sum(1 for p in products if self.get_stock_status(p) == "Out of Stock")
        
        self.total_products_label.setText(str(total))
        self.in_stock_label.setText(str(in_stock_count))
        self.low_stock_label.setText(str(low_stock_count))
        self.out_stock_label.setText(str(out_stock_count))
    
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
