import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"


class AddProductScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Product")
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        self.setMinimumSize(900,900)
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
        item_name_input = self.input()
        item_name_input.setPlaceholderText("Enter Item Name")
        item_col.addWidget(item_name_input)
        hsn_col = QVBoxLayout()
        hsn_col.addWidget(self.label("HSN Code"))
        hsn_input = self.input()
        hsn_input.setPlaceholderText("Enter HSN Code")
        hsn_col.addWidget(hsn_input)
        row_hsn_item.addLayout(item_col)
        row_hsn_item.addSpacing(16)
        row_hsn_item.addLayout(hsn_col)
        form_layout.addLayout(row_hsn_item)

        # Unit of Measure & Barcode (side by side)
        row_uom_barcode = QHBoxLayout()
        row_uom_barcode.setSpacing(16)
        barcode_col = QVBoxLayout()
        barcode_col.addWidget(self.label("Barcode / SKU"))
        barcode_input = self.input()
        barcode_input.setPlaceholderText("Enter Barcode or SKU")
        barcode_col.addWidget(barcode_input)
        uom_col = QVBoxLayout()
        uom_col.addWidget(self.label("Unit of Measure"))
        uom = QComboBox()
        uom.addItems(["PCS", "KG", "LTR", "BOX"])
        uom.setStyleSheet(self.input_style())
        uom_col.addWidget(uom)
        row_uom_barcode.addLayout(barcode_col, 1)
        row_uom_barcode.addSpacing(16)
        row_uom_barcode.addLayout(uom_col, 1)
        form_layout.addLayout(row_uom_barcode)

        # Sales Rate & Purchase Rate (side by side)
        row_sales_purchase = QHBoxLayout()
        row_sales_purchase.setSpacing(16)
        sales_col = QVBoxLayout()
        sales_col.addWidget(self.label("Sales Rate"))
        sales_input = self.input()
        sales_input.setPlaceholderText("Enter Sales Rate")
        sales_col.addWidget(sales_input)
        purchase_col = QVBoxLayout()
        purchase_col.addWidget(self.label("Purchase Rate"))
        purchase_input = self.input()
        purchase_input.setPlaceholderText("Enter Purchase Rate")
        purchase_col.addWidget(purchase_input)
        row_sales_purchase.addLayout(sales_col)
        row_sales_purchase.addSpacing(16)
        row_sales_purchase.addLayout(purchase_col)
        form_layout.addLayout(row_sales_purchase)


        # Discount & MRP (side by side)
        row_discount_mrp = QHBoxLayout()
        row_discount_mrp.setSpacing(16)
        discount_col = QVBoxLayout()
        discount_col.addWidget(self.label("Discount %"))
        discount_input = self.input()
        discount_input.setPlaceholderText("Enter Discount %")
        discount_col.addWidget(discount_input)
        mrp_col = QVBoxLayout()
        mrp_col.addWidget(self.label("MRP"))
        mrp_input = self.input()
        mrp_input.setPlaceholderText("Enter MRP")
        mrp_col.addWidget(mrp_input)
        row_discount_mrp.addLayout(discount_col)
        row_discount_mrp.addSpacing(16)
        row_discount_mrp.addLayout(mrp_col)
        form_layout.addLayout(row_discount_mrp)

        # Taxes (CGST, SGST, IGST) side by side
        row_taxes = QHBoxLayout()
        row_taxes.setSpacing(16)
        cgst_col = QVBoxLayout()
        cgst_col.addWidget(self.label("CGST %"))
        cgst_input = self.input()
        cgst_input.setPlaceholderText("Enter CGST %")
        cgst_col.addWidget(cgst_input)
        sgst_col = QVBoxLayout()
        sgst_col.addWidget(self.label("SGST %"))
        sgst_input = self.input()
        sgst_input.setPlaceholderText("Enter SGST %")
        sgst_col.addWidget(sgst_input)
        igst_col = QVBoxLayout()
        igst_col.addWidget(self.label("IGST %"))
        igst_input = self.input()
        igst_input.setPlaceholderText("Enter IGST %")
        igst_col.addWidget(igst_input)
        row_taxes.addLayout(cgst_col)
        row_taxes.addSpacing(16)
        row_taxes.addLayout(sgst_col)
        row_taxes.addSpacing(16)
        row_taxes.addLayout(igst_col)
        form_layout.addLayout(row_taxes)

        # Opening Qty & Opening Value (side by side)
        row_opening = QHBoxLayout()
        row_opening.setSpacing(16)
        qty_col = QVBoxLayout()
        qty_col.addWidget(self.label("Opening Qty"))
        qty_input = self.input()
        qty_input.setPlaceholderText("Enter Opening Qty")
        qty_col.addWidget(qty_input)
        value_col = QVBoxLayout()
        value_col.addWidget(self.label("Opening Value"))
        value_input = self.input()
        value_input.setPlaceholderText("Enter Opening Value")
        value_col.addWidget(value_input)
        row_opening.addLayout(qty_col)
        row_opening.addSpacing(16)
        row_opening.addLayout(value_col)
        form_layout.addLayout(row_opening)

        # Quality Alert & Reorder Level (side by side)
        row_quality_reorder = QHBoxLayout()
        row_quality_reorder.setSpacing(16)
        quality_col = QVBoxLayout()
        quality_col.addWidget(self.label("Quality Alert"))
        quality_input = self.input()
        quality_input.setPlaceholderText("Enter Quality Alert")
        quality_col.addWidget(quality_input)
        reorder_col = QVBoxLayout()
        reorder_col.addWidget(self.label("Reorder Level"))
        reorder_input = self.input()
        reorder_input.setPlaceholderText("Enter Reorder Level")
        reorder_col.addWidget(reorder_input)
        row_quality_reorder.addLayout(quality_col)
        row_quality_reorder.addSpacing(16)
        row_quality_reorder.addLayout(reorder_col)
        form_layout.addLayout(row_quality_reorder)

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

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

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
            QLineEdit, QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
                font-size: 16px;
            }}
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddProductScreen()
    window.resize(800, 600)  # Responsive initial size
    window.show()
    sys.exit(app.exec_())
