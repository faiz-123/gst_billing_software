import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFrame, QComboBox, QLineEdit, QHeaderView, QAbstractItemView
)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon, QCursor
# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"

class PaymentListScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software - Payments")
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
        title = QLabel("Payments")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {TEXT_PRIMARY};")

        addPaymentBtn = QPushButton("+ Record Payment")
        addPaymentBtn.setFixedHeight(40)
        addPaymentBtn.setStyleSheet(
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
        headerLayout.addWidget(addPaymentBtn)
        contentLayout.addLayout(headerLayout)

        # Search Box
        searchBox = QLineEdit()
        searchBox.setPlaceholderText("Search by party or payment ID")
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
        table = QTableWidget(4, 6)
        table.setHorizontalHeaderLabels(
            ["Payment ID", "Party Name", "Amount", "Date", "Status", "Actions"]
        )
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

        payments = [
            ["PAY001", "Sharma Enterprises", "₹5,000", "2025-09-01", "Completed"],
            ["PAY002", "Radha Textiles", "₹2,500", "2025-09-10", "Pending"],
            ["PAY003", "Ganesha Distributors", "₹7,200", "2025-09-15", "Completed"],
            ["PAY004", "Mehta & Sons", "₹1,800", "2025-09-20", "Failed"],
        ]

        for row, payment in enumerate(payments):
            for col, value in enumerate(payment):
                item = QTableWidgetItem(value)
                item.setForeground(QColor(TEXT_PRIMARY))
                table.setItem(row, col, item)

            # Actions column
            actionsWidget = QWidget()
            actionsWidget.setStyleSheet("background: transparent;")
            actionsLayout = QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(0, 0, 0, 0)
            actionsLayout.setSpacing(10)

            editBtn = QPushButton()
            editBtn.setIcon(QtGui.QIcon("/Users/fbabuna/Desktop/python_project/Pyqt5/gst_billing_software/edit-text.png"))
            editBtn.setIconSize(QtCore.QSize(20, 20))
            editBtn.setCursor(QCursor(Qt.PointingHandCursor))
            editBtn.setStyleSheet(f"border: none; color: {TEXT_PRIMARY}; background: transparent; padding: 24px;")

            deleteBtn = QPushButton()
            deleteBtn.setIcon(QtGui.QIcon("Pyqt5/gst_billing_software/trash.png"))
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
                    background-color: {"#1E40AF" if item == "Payments" else "transparent"};
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

    def dropdownStyle(self):
        return f"""
        QComboBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 4px 8px;
            background: white;
            color: {TEXT_PRIMARY};
        }}
        """


    def build_content_area(self):
        content = QVBoxLayout()
        content.setContentsMargins(20, 20, 20, 20)
        content.setSpacing(15)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        company_dropdown = QComboBox()
        company_dropdown.addItems(["Sukarna Distributors", "Other Company"])
        company_dropdown.setStyleSheet(f"""
            QComboBox {{
                padding: 6px 12px;
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 14px;
                background: white;
                color: {TEXT_PRIMARY};
            }}
        """)

        fy_dropdown = QComboBox()
        fy_dropdown.addItems(["FY 20-24", "FY 21-25"])
        fy_dropdown.setStyleSheet(company_dropdown.styleSheet())

        record_btn = QPushButton("+ Record Payment")
        record_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)

        top_bar.addWidget(company_dropdown)
        top_bar.addWidget(fy_dropdown)
        top_bar.addWidget(record_btn)

        # Title
        title = QLabel("Record Payments")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")

        # Search bar
        search = QLineEdit()
        search.setPlaceholderText("Search")
        search.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background: white;
                color: {TEXT_PRIMARY};
            }}
        """)

        # Table
        table = QTableWidget(4, 4)
        table.setHorizontalHeaderLabels(["Date", "Party", "Amount", "Mode"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 14px;
            }}
            QHeaderView::section {{
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
                font-weight: bold;
                padding: 10px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
        """)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        payments = [
            ("April 16, 2024", "XYZ Enterprises", "₹ 7,000", "Bank"),
            ("April 14, 2024", "John Doe", "₹ 5,500", "Cash"),
            ("April 10, 2024", "Acme Corp", "₹ 8,200", "UPI"),
            ("April 5, 2024", "Jane Smith", "₹ 3,000", "Bank"),
        ]

        for row, (date, party, amount, mode) in enumerate(payments):
            table.setItem(row, 0, QTableWidgetItem(date))
            table.setItem(row, 1, QTableWidgetItem(party))
            table.setItem(row, 2, QTableWidgetItem(amount))
            table.setItem(row, 3, QTableWidgetItem(mode))

        # Assemble content
        content.addLayout(top_bar)
        content.addWidget(title)
        content.addWidget(search)
        content.addWidget(table)

        container = QWidget()
        container.setLayout(content)
        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentListScreen()
    window.show()
    sys.exit(app.exec_())
