import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFrame, QComboBox, QLineEdit, QHeaderView,QAbstractItemView
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

class PartiesScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software - Parties")
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
        title = QLabel("Parties")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {TEXT_PRIMARY};")

        addPartyBtn = QPushButton("+ New Party")
        addPartyBtn.setFixedHeight(40)
        addPartyBtn.setStyleSheet(
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
        headerLayout.addWidget(addPartyBtn)
        contentLayout.addLayout(headerLayout)

        # Search Box
        searchBox = QLineEdit()
        searchBox.setPlaceholderText("Search by name or GSTIN")
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
            ["Party Name", "Mobile No", "Email", "Address", "Type", "Actions"]
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

        parties = [
            ["Sharma Enterprises", "8879 0000 111", "sharma.ent@gmail.com", "Mumbai", "Customer"],
            ["Radha Textiles", "98X7 333-222", "radha.txt@gmail.com", "New Delhi", "Supplier"],
            ["Ganesha Distributors", "29LMNOP45612T", "ganesha.dist@gmail.com", "Bengaluru", "Supplier"],
            ["Mehta & Sons", "24PQRSTU878C9VW", "mehta.sons@gmail.com", "Ahmedabad", "Both"],
        ]

        for row, party in enumerate(parties):
            for col, value in enumerate(party):
                item = QTableWidgetItem(value)
                item.setForeground(QColor(TEXT_PRIMARY))
                table.setItem(row, col, item)

            # Actions column
            actionsWidget = QWidget()
            actionsWidget.setStyleSheet("background: transparent;")  # <-- Make background transparent
            actionsLayout = QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(0, 0, 0, 0)
            actionsLayout.setSpacing(10)

            editBtn = QPushButton()
            editBtn.setIcon(QtGui.QIcon("/Users/fbabuna/Desktop/python_project/Pyqt5/gst_billing_software/edit-text.png"))  # Make sure edit-text.png is in the same directory
            editBtn.setIconSize(QtCore.QSize(20, 20))    # Adjust icon size as needed
            editBtn.setCursor(QCursor(Qt.PointingHandCursor))
            editBtn.setStyleSheet(f"border: none; color: {TEXT_PRIMARY}; background: transparent; padding: 24px;")  # Remove border, color is handled by icon

            deleteBtn = QPushButton()
            deleteBtn.setIcon(QtGui.QIcon("/Users/fbabuna/Desktop/python_project/Pyqt5/gst_billing_software/trash.png"))
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

        # mainLayout.addWidget(sidebar)
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

        # Add icons (emoji for simplicity, can use QIcon for real icons)
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
                    background-color: {"#1E40AF" if idx == 0 else "transparent"};
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartiesScreen()
    window.show()
    sys.exit(app.exec_())
