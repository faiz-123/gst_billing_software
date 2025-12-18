import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QFrame, QSizePolicy, QHeaderView, QAbstractItemView
)
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QCursor

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"


class InvoiceScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software - Invoices")
        self.resize(1200, 700)
        self.setStyleSheet(f"background-color: {BACKGROUND};")

        # Main Layout
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        sidebar = self.build_sidebar()
        mainLayout.addWidget(sidebar)

        # Right Content Area
        content = QWidget()
        contentLayout = QVBoxLayout(content)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        contentLayout.setSpacing(15)

        # Header Row
        headerLayout = QHBoxLayout()
        title = QLabel("Invoices")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {TEXT_PRIMARY};")

        addInvoiceBtn = QPushButton("+ New Invoice")
        addInvoiceBtn.setFixedHeight(40)
        addInvoiceBtn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 24px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            """
        )

        headerLayout.addWidget(title)
        headerLayout.addStretch()
        headerLayout.addWidget(addInvoiceBtn)
        contentLayout.addLayout(headerLayout)

        # Search Box
        searchBox = QLineEdit()
        searchBox.setPlaceholderText("Search by invoice no., party, or date")
        searchBox.setFixedHeight(35)
        searchBox.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding-left: 10px;
                background: white;
            }}
            """
        )
        contentLayout.addWidget(searchBox)

        # Table
        table = QTableWidget(6, 6)
        table.setHorizontalHeaderLabels([
            "Invoice No.", "Date", "Party", "Amount", "Status", "Actions"
        ])
        table.horizontalHeader().setStyleSheet(
            f"QHeaderView::section {{ background-color: {BACKGROUND}; color: {TEXT_SECONDARY}; padding: 8px; border: none; }}"
        )
        table.setStyleSheet(
            f"QTableWidget {{ background: white; border: 1px solid {BORDER}; border-radius: 6px; }}"
        )
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        invoices = [
            ["1001", "01/04/2023", "Supplier A", "₹ 9,500", "Paid"],
            ["1002", "02/04/2023", "Customer B", "₹ 1,750", "Unpaid"],
            ["1003", "03/04/2023", "Supplier C", "₹ 4,250", "Paid"],
            ["1004", "04/04/2023", "Customer D", "₹ 8,200", "Unpaid"],
            ["1005", "05/04/2023", "Supplier E", "₹ 9,500", "Paid"],
            ["1006", "05/04/2023", "Customer F", "₹ 1,750", "Unpaid"],
        ]

        for row, invoice in enumerate(invoices):
            for col, value in enumerate(invoice):
                item = QTableWidgetItem(value)
                item.setForeground(QColor(TEXT_PRIMARY))
                if col == 4:  # Status
                    if value == "Paid":
                        item.setBackground(QColor(SUCCESS))
                        item.setForeground(QColor("white"))
                    else:
                        item.setBackground(QColor(DANGER))
                        item.setForeground(QColor("white"))
                table.setItem(row, col, item)

            # Actions column
            actionsWidget = QWidget()
            actionsWidget.setStyleSheet("background: transparent;")
            actionsLayout = QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(0, 0, 0, 0)
            actionsLayout.setSpacing(10)

            editBtn = QPushButton()
            editBtn.setIcon(QIcon("/Users/fbabuna/Desktop/python_project/Pyqt5/gst_billing_software/edit-text.png"))
            editBtn.setIconSize(QtCore.QSize(20, 20))
            editBtn.setCursor(QCursor(Qt.PointingHandCursor))
            editBtn.setStyleSheet(f"border: none; color: {TEXT_PRIMARY}; background: transparent; padding: 24px;")

            deleteBtn = QPushButton()
            deleteBtn.setIcon(QIcon("/Users/fbabuna/Desktop/python_project/Pyqt5/gst_billing_software/trash.png"))
            deleteBtn.setIconSize(QtCore.QSize(20, 20))
            deleteBtn.setCursor(QCursor(Qt.PointingHandCursor))
            deleteBtn.setStyleSheet(f"""
                    QPushButton {{
                        color: {DANGER};
                        border: none;
                        font-size: 14px;
                        background: transparent;
                    }}
                    QPushButton:hover {{
                        background-color: #FEE2E2;
                        color: #B91C1C;
                    }}
                """)

            actionsLayout.addWidget(editBtn)
            actionsLayout.addWidget(deleteBtn)
            actionsLayout.addStretch()
            table.setCellWidget(row, 5, actionsWidget)

        contentLayout.addWidget(table)
        mainLayout.addWidget(content)

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #0A2E5C;")

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(20, 30, 20, 20)

        title = QLabel("GST Billing Software")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title)

        dashboard_items = [
            ("🏠", "Dashboard"),
            ("🧾", "Invoices"),
            ("📦", "Products"),
            ("👥", "Parties"),
            ("💳", "Payments"),
            ("📈", "Reports"),
            ("⚙", "Settings")
        ]

        for idx, (icon, item) in enumerate(dashboard_items):
            btn = QPushButton(f"{icon}  {item}")
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {"#1E40AF" if item == "Invoices" else "transparent"};
                    color: white;
                    font-size: 18px;
                    text-align: left;
                    padding-left: 12px;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: #1E3A8A;
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def build_content(self):
        content = QFrame()
        contentLayout = QVBoxLayout(content)
        contentLayout.setContentsMargins(30, 20, 30, 20)
        contentLayout.setSpacing(15)

        # Top bar
        topBar = QHBoxLayout()
        companyBtn = QPushButton("ABC Traders")
        companyBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                color: {TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                border: 1px solid {PRIMARY};
            }}
        """)

        fyBtn = QPushButton("2023-2024")
        fyBtn.setStyleSheet(companyBtn.styleSheet())

        topBar.addWidget(companyBtn)
        topBar.addWidget(fyBtn)
        topBar.addStretch()

        profileBtn = QPushButton("A")
        profileBtn.setFixedSize(32, 32)
        profileBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                border-radius: 16px;
                color: white;
                font-weight: bold;
            }}
        """)
        topBar.addWidget(profileBtn)

        contentLayout.addLayout(topBar)

        # Title and New Invoice
        titleLayout = QHBoxLayout()
        title = QLabel("Invoices")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: bold;")
        titleLayout.addWidget(title)

        titleLayout.addStretch()
        newInvoiceBtn = QPushButton("+ New Invoice")
        newInvoiceBtn.setCursor(Qt.PointingHandCursor)
        newInvoiceBtn.setFixedHeight(40)
        newInvoiceBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                border-radius: 6px;
                padding: 0 16px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)
        titleLayout.addWidget(newInvoiceBtn)

        contentLayout.addLayout(titleLayout)

        # Search Bar
        search = QLineEdit()
        search.setPlaceholderText("Search by invoice no., party, or date")
        search.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
        """)
        contentLayout.addWidget(search)

        # Table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Invoice No.", "Date", "Party", "Amount", "Status", "Actions"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(False)
        table.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {BACKGROUND};
                color: {TEXT_SECONDARY};
                border: none;
                font-weight: bold;
                padding: 10px;
            }}
            QTableWidget {{
                background-color: white;
                border: 1px solid {BORDER};
                border-radius: 6px;
                gridline-color: {BORDER};
            }}
            QTableWidget::item {{
                padding: 12px;
            }}
        """)

        invoices = [
            ("1001", "01/04/2023", "Supplier A", "₹ 9,500", "Paid"),
            ("1002", "02/04/2023", "Customer B", "₹ 1,750", "Unpaid"),
            ("1003", "03/04/2023", "Supplier C", "₹ 4,250", "Paid"),
            ("1004", "04/04/2023", "Customer D", "₹ 8,200", "Unpaid"),
            ("1005", "05/04/2023", "Supplier E", "₹ 9,500", "Paid"),
            ("1006", "05/04/2023", "Customer F", "₹ 1,750", "Unpaid"),
        ]

        table.setRowCount(len(invoices))
        for row, (inv, date, party, amt, status) in enumerate(invoices):
            table.setItem(row, 0, QTableWidgetItem(inv))
            table.setItem(row, 1, QTableWidgetItem(date))
            table.setItem(row, 2, QTableWidgetItem(party))
            table.setItem(row, 3, QTableWidgetItem(amt))

            statusItem = QTableWidgetItem(status)
            if status == "Paid":
                statusItem.setBackground(QColor(SUCCESS))
                statusItem.setForeground(QColor("white"))
            else:
                statusItem.setBackground(QColor(DANGER))
                statusItem.setForeground(QColor("white"))
            table.setItem(row, 4, statusItem)

            actionItem = QTableWidgetItem("👁")
            actionItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 5, actionItem)

        table.resizeColumnsToContents()
        contentLayout.addWidget(table)

        return content


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceScreen()
    window.show()
    sys.exit(app.exec_())
