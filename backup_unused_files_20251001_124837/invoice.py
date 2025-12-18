import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QDateEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QFrame, QSizePolicy, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1E40AF"
BACKGROUND = "#F9FAFB"
BORDER = "#E5E7EB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
DANGER = "#DC2626"

APP_STYLESHEET = f"""

QGroupBox {{
  border: 2px solid {BORDER};
  border-radius: 6px;
  margin-top: 7px;
  font-weight: bold;
  padding: 8px;
}}
QGroupBox::title {{
  subcontrol-origin: margin;
  subcontrol-position: top left;
  padding-left: 20px;
  color: {TEXT_PRIMARY};
}}

QLineEdit, QDateEdit, QComboBox {{
  border: 1px solid {BORDER};
  border-radius: 6px;
  padding: 6px;
  background: #FFFFFF;
  color: {TEXT_PRIMARY};
  height: 28px;
  font-size: 16px;
}}

QComboBox {{
  border: 1px solid {BORDER};
  border-radius: 6px;
  padding: 6px;
  background: #FFFFFF;
  color: {TEXT_PRIMARY};
  height: 28px;
  font-size: 16px;
}}

QComboBox::drop-down, QDateEdit::drop-down {{
  height: 20px;
  width: 20px;
  subcontrol-position: center right;
  border-color: transparent;
}}
"""
class CreateInvoice(QMainWindow):
    # Hide the default vertical numbering column
    def save_invoice(self):
        QMessageBox.information(self, "Invoice Saved", "Invoice has been saved successfully!")
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice")
        self.setMinimumSize(1440, 1024)
        self.setStyleSheet(f"background-color: {BACKGROUND}; font-family: Arial; font-size: 14px;")

        container = QWidget()
        self.setCentralWidget(container)
        mainLayout = QVBoxLayout(container)
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setContentsMargins(40, 40, 40, 10)
        mainLayout.setSpacing(20)

        # Title outside frame
        lblTitle = QLabel("New Invoice")
        lblTitle.setFont(QFont("Arial", 32, QFont.Bold))
        lblTitle.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 32px; border: none;")
        mainLayout.addWidget(lblTitle, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Main form frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)
        # form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 20, 40, 10)
        form_layout.setSpacing(18)

        # GroupBox: Parties Details
        party_group = QGroupBox("Parties Details")
        party_group_layout = QVBoxLayout(party_group)
        party_group_layout.setContentsMargins(20, 20, 20, 20)
        
        # Customer Name and Mobile No horizontally, each label above textbox
        row_name_mobile = QHBoxLayout()

        # Customer Name vertical (QComboBox)
        customer_name_layout = QVBoxLayout()
        customer_name_label = QLabel("Customer Name")
        customer_name_label.setStyleSheet("border: none;")
        customer_name_combo = QComboBox()
        customer_name_combo.setEditable(True)
        customer_name_combo.setInsertPolicy(QComboBox.NoInsert)
        customer_name_combo.addItems(["Select Customer", "XYZ Enterprises", "ABC Traders", "LMN Pvt Ltd"])
        customer_name_combo.setFixedWidth(450)
        # customer_name_combo.setStyleSheet("QComboBox::drop-down { height: 20px; width: 20px; subcontrol-position: center right; border-color: transparent; }")
        customer_name_layout.addWidget(customer_name_label)
        customer_name_layout.addWidget(customer_name_combo)
        row_name_mobile.addLayout(customer_name_layout)
            
        # Mobile No vertical
        mobile_layout = QVBoxLayout()
        mobile_label = QLabel("Mobile No.")
        mobile_label.setStyleSheet("border: none;")
        mobile_input = QLineEdit()
        mobile_input.setPlaceholderText("Enter Mobile Number")
        mobile_input.setStyleSheet("border: 1px solid #D1D5DB; border-radius: 6px; padding: 6px; background: white; color: #111827; font-size: 14px;")
        mobile_layout.addWidget(mobile_label)
        mobile_layout.addWidget(mobile_input)
        row_name_mobile.addLayout(mobile_layout)

        party_group_layout.addLayout(row_name_mobile)

        # Address and City horizontally, each label above textbox
        row_address_city = QHBoxLayout()

        # City vertical
        city_layout = QVBoxLayout()
        city_label = QLabel("City")
        city_label.setStyleSheet("border: none;")
        city_input = QLineEdit()
        city_input.setPlaceholderText("Enter City")
        city_layout.addWidget(city_label)
        city_layout.addWidget(city_input)
        row_address_city.addLayout(city_layout)

        # Address vertical
        address_layout = QVBoxLayout()
        address_label = QLabel("Address")
        address_label.setStyleSheet("border: none;")
        address_input = QLineEdit()
        address_input.setPlaceholderText("Enter Address")
        address_layout.addWidget(address_label)
        address_layout.addWidget(address_input)
        row_address_city.addLayout(address_layout)

        party_group_layout.addLayout(row_address_city)


        # GroupBox: Invoice Details
        invoice_group = QGroupBox("Invoice Details")
        invoice_group_layout = QVBoxLayout(invoice_group)
        invoice_group_layout.setContentsMargins(20, 20, 20, 20)
        invoice_group_layout.setSpacing(10)
        
        # Invoice Number and Date horizontally, label and textbox also horizontally
        row_invoice_date = QHBoxLayout()

        # Invoice Number horizontal
        invoice_no_layout = QHBoxLayout()
        invoice_no_label = QLabel("Invoice No")
        invoice_no_label.setStyleSheet("border: none;")
        invoice_no_input = QLineEdit()
        invoice_no_input.setFixedWidth(150)
        invoice_no_input.setAlignment(Qt.AlignLeft)
        invoice_no_layout.addWidget(invoice_no_label)
        invoice_no_layout.addWidget(invoice_no_input)
        invoice_no_layout.addStretch(1)
        row_invoice_date.addLayout(invoice_no_layout)

        # Date horizontal
        date_layout = QHBoxLayout()
        date_label = QLabel("Date")
        date_label.setStyleSheet("border: none;")
        date_input = QDateEdit(QDate.currentDate())
        date_input.setCalendarPopup(True)
        date_input.setFixedWidth(150)
        date_input.setStyleSheet("border: 1px solid #D1D5DB; border-radius: 6px; padding: 6px; background: white; color: #111827; font-size: 18px;")

        date_layout.addWidget(date_label)
        date_layout.addWidget(date_input)
        row_invoice_date.addLayout(date_layout)

        invoice_group_layout.addLayout(row_invoice_date)

        # Invoice Type horizontal
        type_layout = QHBoxLayout()
        invoice_type_label = QLabel("Invoice Type")
        invoice_type_label.setStyleSheet("border: none;")
        invoice_type_combo = QComboBox()
        invoice_type_combo.addItems(["GST", "Non-GST"])
        invoice_type_combo.setFixedWidth(150)
        type_layout.addWidget(invoice_type_label)
        type_layout.addWidget(invoice_type_combo)
        type_layout.addStretch(1)
        invoice_group_layout.addLayout(type_layout)

        # Add both group boxes horizontally
        details_row = QHBoxLayout()
        details_row.addWidget(party_group, stretch=1)
        details_row.addWidget(invoice_group, stretch=1)
        form_layout.addLayout(details_row)

        header_list = ["NO", "ITEM/ SERVICE", "HSN", "QTY", "PRICE (₹)", "DISCOUNT", "TAX %", "AMOUNT (₹)", "ACTION"]

        # Create Invoice Items groupbox and add table inside
        items_group_layout = QVBoxLayout()
        # items_group_layout.setContentsMargins(20, 20, 20, 20)
        self.table = QTableWidget(0, 9)
        self.table.setMinimumHeight(370)  # Increased table height
        self.table.setHorizontalHeaderLabels(header_list)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)   # Taller rows

        self.table.setStyleSheet("""
        QHeaderView::section {
        background-color: #F9FAFB;
        padding: 2px 4px;
        border: 1px solid #E5E7EB;
        font-weight: bold;
        font-size: 12px;
        min-height: 22px;
        max-height: 22px;
        }
        QTableWidget {
        gridline-color: #E5E7EB;
        border: none;
        }
        QTableWidget::item {
        padding: 2px 6px;
        font-size: 18px;
        min-height: 28px;
        }
        QTableWidget::item:selected {
        background: #FFFFFF;
        }
        """)
        # Set header row height small
        self.table.horizontalHeader().setFixedHeight(40)
        # Set first item row height large (example, for all rows use loop)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 20)
        # Set custom column widths for better layout
        self.table.setColumnWidth(0, 60)   # NO (very small)
        self.table.setColumnWidth(1, 500)  # ITEM/ SERVICE (large)
        self.table.setColumnWidth(2, 150)   # HSN (small)
        self.table.setColumnWidth(3, 130)   # QTY (small)
        self.table.setColumnWidth(4, 150)  # PRICE (medium)
        self.table.setColumnWidth(5, 150)   # DISCOUNT (small)
        self.table.setColumnWidth(6, 150)   # TAX % (small)
        self.table.setColumnWidth(7, 150)  # AMOUNT (large)
        self.table.setColumnWidth(8, 120)  # ACTION (button)
        items_group_layout.addWidget(self.table)
        # form_layout.addWidget(items_group)
        form_layout.addLayout(items_group_layout)
        form_layout.setSpacing(20)

        # Create horizontal layout below table: buttons on left, summary on right
        bottom_layout = QHBoxLayout()
        
        # Left side: Buttons container
        buttons_layout = QVBoxLayout()
        
        # Footer Buttons
        footerLayout = QHBoxLayout()
        btnCancel = QPushButton("Cancel")
        btnCancel.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 20px;
                color: #374151;
            }
            QPushButton:hover {
                background: #F3F4F6;
            }
        """)
        btnCancel.clicked.connect(self.close)
        footerLayout.addWidget(btnCancel)

        btnSave = QPushButton("Save Invoice")
        btnSave.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_HOVER};
            }}
        """)
        btnSave.clicked.connect(self.save_invoice)
        footerLayout.addWidget(btnSave)
        footerLayout.setAlignment(Qt.AlignLeft)
        
        buttons_layout.addLayout(footerLayout)
        buttons_layout.addStretch()  # Push buttons to top
        
        # Right side: Summary section
        summaryLayout = QVBoxLayout()
        summaryLayout.setSpacing(4)

        def create_summary_row(label_text, default_value="0.00"):
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY}; border: none; font-weight: bold;")
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            txt = QLineEdit(f"₹ {default_value}")
            txt.setFixedWidth(150)
            txt.setAlignment(Qt.AlignRight)
            txt.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 6px; padding: 2px 6px; background: white;")
            row.addWidget(lbl)
            row.addWidget(txt)
            row.setAlignment(Qt.AlignRight)
            return row

        summaryLayout.addLayout(create_summary_row("Subtotal :"))
        summaryLayout.addLayout(create_summary_row("CGST (9%) :"))
        summaryLayout.addLayout(create_summary_row("SGST (9%) :"))
        summaryLayout.addLayout(create_summary_row("IGST (0%) :"))
        summaryLayout.addLayout(create_summary_row("Round Off :"))
        summaryLayout.addLayout(create_summary_row("Grand Total :"))
        
        # Add container widget for summary layout
        summaryContainer = QWidget()
        summaryContainer.setLayout(summaryLayout)
        summaryContainer.setFixedWidth(300)
        # Add both sides to horizontal layout
        bottom_layout.addLayout(buttons_layout)
        bottom_layout.addStretch()  # Space between buttons and summary
        bottom_layout.addWidget(summaryContainer)
        
        form_layout.addLayout(bottom_layout)

        # Add dummy data to the table, with QComboBox in 'ITEM/ SERVICE' column
        self.table.insertRow(0)
        dummy_values = [
            "1", "Product A", "1234", "2", "500.00", "10", "18", "980.00", ""
        ]
        for col, value in enumerate(dummy_values):
            if col == 1:
                combo = QComboBox()
                combo.addItems(["Product A", "Product B", "Service C", "Service D"])
                combo.setCurrentText(value)
                self.table.setCellWidget(0, col, combo)
            else:
                item = QTableWidgetItem(value)
                self.table.setItem(0, col, item)
            item.setTextAlignment(Qt.AlignCenter)  # or Qt.AlignLeft, Qt.AlignRight

        mainLayout.addWidget(form_frame, alignment=Qt.AlignTop)

        # Add Item button below the table
        add_item_btn = QPushButton("+ Add Item")
        add_item_btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {PRIMARY};
                font-weight: bold;
                padding: 6px 20px;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: white;
            }}
        """)
        add_item_btn.setFixedWidth(120)
        def add_table_row(after_row=None):
            if after_row is None:
                row = self.table.rowCount()
            else:
                row = after_row + 1
            self.table.insertRow(row)
            default_values = [str(row+1), "Product A", "", "", "", "", "", "", ""]
            for col, value in enumerate(default_values):
                if col == 1:
                    combo = QComboBox()
                    combo.addItems(["Product A", "Product B", "Service C", "Service D"])
                    combo.setCurrentText(value)
                    self.table.setCellWidget(row, col, combo)
                elif col == 8:
                    add_item_btn = QPushButton("Add Item")
                    add_item_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: white;
                            color: {PRIMARY};
                            font-weight: bold;
                            padding: 6px 20px;
                            border-radius: 6px;
                            border: 1px solid {PRIMARY};
                        }}
                        QPushButton:hover {{
                            background: {PRIMARY};
                            color: white;
                        }}
                    """)
                    add_item_btn.setFixedWidth(100)
                    add_item_btn.clicked.connect(lambda checked, r=row: add_table_row(r))
                    self.table.setCellWidget(row, col, add_item_btn)
                else:
                    item = QTableWidgetItem(value)
                    self.table.setItem(row, col, item)

        # For your initial row:
        add_table_row()
        add_item_btn.clicked.connect(add_table_row)
        items_group_layout.addWidget(add_item_btn, alignment=Qt.AlignLeft)

        # Add the "Add Item" button to the last column of the last row
        btn_row = self.table.rowCount() - 1
        for col in range(self.table.columnCount()):
            if col == self.table.columnCount() - 1:
                self.table.setCellWidget(btn_row, col, add_item_btn)
            elif col == 8:
                item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = CreateInvoice()
    window.showMaximized()
    sys.exit(app.exec_())
