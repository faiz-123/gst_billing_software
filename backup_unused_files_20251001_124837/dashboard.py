import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFrame, QComboBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
SUCCESS_BG = "#8ACBB5"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
PURPLE = "#9333EA"
WHITE = "#FFFFFF"


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(f"background-color: {BACKGROUND}; font-family: Arial;")

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = self.build_sidebar()
        main_layout.addWidget(sidebar)

        # Content Area
        content = self.build_content()
        main_layout.addWidget(content, stretch=1)

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

    def build_content(self):
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Top Bar
        top_bar = QHBoxLayout()
        company_label = QLabel("Company Name Organidsation")
        company_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 6px; padding: 12px 12px;")
        top_bar.addWidget(company_label)

        # top_bar.addStretch()
        top_bar.addSpacing(10)
        fy_dropdown = QComboBox()
        fy_dropdown.addItems(["FY 2023-2024", "FY 2024-2025"])
        fy_dropdown.setStyleSheet("""
        QComboBox {
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 12px;
        }
        """)
        top_bar.addWidget(fy_dropdown)

        top_bar.addStretch()
        user_btn = QPushButton("👤")
        user_btn.setFixedSize(40, 40)
        user_btn.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 18px;")
        top_bar.addWidget(user_btn)

        content_layout.addLayout(top_bar)

        # Metric Cards Row
        metrics = QHBoxLayout()
        metrics.setSpacing(20)
        metrics.addWidget(self.metric_card("₹12,500", "Sales Today", SUCCESS, "₹"))
        metrics.addWidget(self.metric_card("₹8,000", "Pending Payments", DANGER, "!"))
        metrics.addWidget(self.metric_card("120", "Pending Invoice", PRIMARY, "?"))
        metrics.addWidget(self.metric_card("₹5,200", "Expenses", PURPLE, "₹"))
        content_layout.addLayout(metrics)

        # Action Buttons
        actions = QHBoxLayout()
        actions.setSpacing(15)
        for text in ["New Invoice", "Add Product", "Add Parties", "New Payment"]:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {PRIMARY_HOVER};
                }}
            """)
            actions.addWidget(btn)
        content_layout.addLayout(actions)

        # Bottom Section (Tables)
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        # Left: Recent Invoices
        invoices_card = self.card_with_table("Recent Invoices", ["Invoice #", "Date", "Party", "Amount", "Status"], [
            ("", "", "", "", ""),
            ("INV-001", "01/02/2024", "XYZ Enterprises", "₹9,000", "Paid"),
            ("INV-002", "01/02/2024", "John Doe", "₹2,500", "Unpaid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            ("INV-003", "01/02/2024", "Acme Corporation", "₹5,500", "Paid"),
            
        ])
        bottom.addWidget(invoices_card, 3)

        # Right: Low Stock + Payments
        right_section = QVBoxLayout()
        right_section.setSpacing(20)
        right_section.addWidget(self.card_with_table("Low Stock", ["Product", "Qty"], [
            ("Product A", "3"),
            ("Product B", "1"),
            ("Product C", "5"),
        ]))
        right_section.addWidget(self.card_with_table("Recent Payments", ["Customer", "Amount"], [
            ("Customer X", "₹3,000"),
            ("Customer Y", "₹1,200"),
            ("Customer Z", "₹800"),
        ]))
        bottom.addLayout(right_section, 1)

        content_layout.addLayout(bottom)

        return content

    def metric_card(self, value, label, color, icon):
        frame = QFrame()
        frame.setFixedHeight(100)
        frame.setStyleSheet(f"background-color: {WHITE}; border-radius: 10px; border: 1px solid {BORDER};")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        # layout.setSpacing(5)

        
        avatar = QLabel(icon)
        avatar.setObjectName("avatar")
        avatar.setFixedSize(46, 46)
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)
        avatar.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 23px;
            font-size: 28px;
        """)

        text_layout = QVBoxLayout()
        val_label = QLabel(value)
        val_label.setFont(QFont("Arial", 26, QFont.Bold))
        val_label.setAlignment(Qt.AlignCenter)
        val_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        
        txt_label = QLabel(label)
        txt_label.setAlignment(Qt.AlignCenter)
        txt_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 18px; border: none;")
        text_layout.addWidget(val_label)
        text_layout.addWidget(txt_label)
        layout.addLayout(text_layout)

        return frame


    def card_with_table(self, title, headers, rows):
        frame = QFrame()
        count=len(rows)*40
        frame.setFixedHeight(count + 80)
        frame.setStyleSheet(f"background-color: white; border: 1px solid {BORDER}; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)


        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {TEXT_PRIMARY}; border: none;")
        lbl.setFixedHeight(32)  # Set your desired height in pixels
        layout.addWidget(lbl)

        table = QTableWidget(len(rows), len(headers))
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)  # hide row numbers
        table.setEditTriggers(QTableWidget.NoEditTriggers) # make cells non-editable
        table.setSelectionMode(QTableWidget.NoSelection) # disable selection
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
            }
             QTableWidget::item {
        border-bottom: 1px solid #E5E7EB;  /* Add bottom line to each cell */
    }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #374151;
                font-weight: bold;
                padding: 6px;
                border: none;
                font-size: 16px;
            }
        """)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignHCenter)
                item.setTextAlignment(Qt.AlignVCenter)
                item.setFont(QFont("Arial", 14))
                if headers[c] == "Status":
                    if val == "Paid":
                        item.setForeground(QColor(SUCCESS_BG))
                        item.setFont(QFont("Arial", 16, QFont.Bold))
                    elif val == "Unpaid":
                        item.setForeground(QColor(DANGER))
                        item.setFont(QFont("Arial", 16, QFont.Bold))
                table.setItem(r, c, item)
                

        table.resizeColumnsToContents()
        table.setFixedHeight(150)
        table.setShowGrid(False)
        layout.addWidget(table)
        

        return frame


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
