"""
Product dialog module (moved from products.py to avoid circular imports)
"""
from PyQt5.QtWidgets import (
	QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QDialog, QMessageBox,
	QFormLayout, QLineEdit, QComboBox, QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from theme import (
	SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
	BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER
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
        title = QLabel("Add Product")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; padding: 2px 0px 2px 0px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)
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
        # HSN and Item Name
        row_hsn_item = QHBoxLayout()
        row_hsn_item.setSpacing(16)
        item_col = QVBoxLayout()
        item_label = QLabel("Item Name <span style=\"color:#d32f2f\">*</span>")
        item_label.setTextFormat(Qt.RichText)
        item_label.setFont(QFont("Arial", 16))
        item_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold; border: none;")
        item_col.addWidget(item_label)
        self.name_input = self.input()
        self.name_input.setPlaceholderText("Enter Item Name")
        self.name_input.textChanged.connect(self._on_name_changed)
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
        # Unit of Measure & Barcode
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
        self.unit_combo.setStyleSheet(self.input_style())
        uom_col.addWidget(self.unit_combo)
        row_uom_barcode.addLayout(barcode_col, 1)
        row_uom_barcode.addSpacing(16)
        row_uom_barcode.addLayout(uom_col, 1)
        form_layout.addLayout(row_uom_barcode)
        # Sales & Purchase
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
        # Discount & MRP
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
        # Tax row
        row_tax = QHBoxLayout()
        row_tax.setSpacing(16)
        tax_col = QVBoxLayout()
        tax_col.addWidget(self.label("Tax Rate (GST) %"))
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setDecimals(2)
        self.tax_rate.setValue(18.0)
        self.tax_rate.setMinimumHeight(40)
        self.tax_rate.setStyleSheet(self.input_style())
        tax_col.addWidget(self.tax_rate)
        checkbox_col = QVBoxLayout()
        checkbox_col.addWidget(self.label("Tax Options"))
        self.tax_inclusive = QCheckBox("Price is inclusive of tax")
        self.tax_inclusive.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY};")
        checkbox_col.addWidget(self.tax_inclusive)
        row_tax.addLayout(tax_col)
        row_tax.addSpacing(16)
        row_tax.addLayout(checkbox_col)
        form_layout.addLayout(row_tax)
        # Opening & Low Stock
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
        # Additional: type and category
        row_additional = QHBoxLayout()
        row_additional.setSpacing(16)
        type_col = QVBoxLayout()
        type_col.addWidget(self.label("Product Type"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Goods", "Service"])
        self.type_combo.setMinimumHeight(40)
        self.type_combo.setStyleSheet(self.input_style())
        type_col.addWidget(self.type_combo)
        category_col = QVBoxLayout()
        category_col.addWidget(self.label("Category"))
        self.category_input = self.input()
        self.category_input.setPlaceholderText("e.g., Electronics, Clothing")
        category_col.addWidget(self.category_input)
        row_additional.addLayout(type_col)
        row_additional.addSpacing(16)
        row_additional.addLayout(category_col)
        form_layout.addLayout(row_additional)
        # Description and extra
        desc_row = QHBoxLayout()
        desc_row.setSpacing(16)
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
        additional_col = QVBoxLayout()
        additional_col.addSpacing(20)
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
        save_btn.clicked.connect(self.save_product)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
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
            # Highlight the input in red instead of showing a message box
            self._set_name_error_state(True)
            self.name_input.setFocus()
            if not self.name_input.placeholderText():
                self.name_input.setPlaceholderText("Item Name is required")
            return
        
        selling_price = self.selling_price.value()
        if selling_price <= 0:
            QMessageBox.warning(self, "Error", "Selling price must be greater than 0!")
            return
        
        # Compute DB-aligned fields
        hsn = self.hsn_code.text().strip() or None
        stock_qty = float(self.opening_stock.value() if self.track_stock.isChecked() else 0)

        try:
            if self.product_data:  # Editing
                update_payload = {
                    'id': self.product_data['id'],
                    'name': name,
                    'hsn_code': hsn,
                    'sales_rate': float(selling_price),
                    'stock_quantity': stock_qty,
                }
                db.update_product(update_payload)
                QMessageBox.information(self, "Success", "Product updated successfully!")
            else:  # Adding new
                db.add_product(
                    name=name,
                    hsn_code=hsn,
                    sales_rate=float(selling_price),
                    stock_quantity=stock_qty,
                )
                QMessageBox.information(self, "Success", "Product added successfully!")
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")

    def _on_name_changed(self, text: str):
        """Clear error state when user starts typing a non-empty name."""
        if text and text.strip():
            self._set_name_error_state(False)

    def _set_name_error_state(self, is_error: bool):
        """Apply or clear red error styling on the Item Name input."""
        if is_error:
            self.name_input.setStyleSheet(
                f"border: 2px solid {DANGER}; border-radius: 6px; padding: 12px; background-color: #fff5f5; color: {TEXT_PRIMARY}; font-size: 16px;"
            )
            self.name_input.setToolTip("Item Name is required")
        else:
            # Restore the standard input style
            self.name_input.setStyleSheet(self.input_style())
            self.name_input.setToolTip("")
