"""
Dashboard screen - Main overview of the application
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable
from theme import (
    SUCCESS, DANGER, PRIMARY, PURPLE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, get_title_font
)
from database import db

# Import dialog classes for direct navigation
from .invoices import InvoiceDialog
from .products import ProductDialog  
from .parties import PartyDialog
from .payments import PaymentDialog

class MetricCard(QFrame):
    """Enhanced metric card widget following horizontal layout design"""
    def __init__(self, value, label, color, icon="✨"):
        super().__init__()
        METRIC_CARD_HEIGHT = 120
        
        self.setFixedHeight(METRIC_CARD_HEIGHT)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {WHITE}; 
                border-radius: 12px; 
                border: 2px solid {BORDER};
            }}
            QFrame:hover {{
                border-color: {PRIMARY};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Icon avatar
        avatar = QLabel(icon)
        avatar.setFixedSize(50, 50)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(avatar)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Value label
        val_label = QLabel(value)
        val_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        val_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        
        # Description label
        desc_label = QLabel(label)
        desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 16px; border: none;")
        
        text_layout.addWidget(val_label)
        text_layout.addWidget(desc_label)
        layout.addLayout(text_layout)

class DashboardScreen(BaseScreen):
    def __init__(self):
        super().__init__("Dashboard")
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Setup dashboard content with larger frame layout"""
        # Hide the default BaseScreen title
        self.title_label.hide()
        
        # Remove Dashboard header - no longer needed
        
        # Make content frame larger by reducing main layout margins
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced from default
        
        # 2. FY Combobox with stylish arrow
        self.setup_fy_selector()
        
        # 3&4. Metrics cards with magic icons and larger fonts
        self.setup_metrics()
        
        # 5&6. Action buttons (increased width, full row)
        self.setup_actions()
        
                # 7&8. Tables layout (Recent invoices left, Low stock + Payment received right)
        self.setup_tables_layout()
            
    def setup_fy_selector(self):
        """Setup FY selector with stylish dropdown"""
        fy_layout = QHBoxLayout()
        fy_layout.setAlignment(Qt.AlignLeft)
        
        fy_combo = QComboBox()
        fy_combo.addItems(["FY 2024-25", "FY 2023-24", "FY 2022-23"])
        fy_combo.setFixedSize(200, 40)
        fy_combo.setStyleSheet(f"""
            QComboBox {{
                font-size: 16px;
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 12px 16px;
                background-color: {WHITE};
                color: {TEXT_PRIMARY};
                min-width: 150px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {TEXT_SECONDARY};
                width: 8px;
                height: 8px;
                border-top: none;
                border-right: none;
            }}
        """)
        
        fy_layout.addWidget(fy_combo)
        
        self.add_content_layout(fy_layout)
        
        # Add spacing widget
        spacing_widget = QWidget()
        spacing_widget.setFixedHeight(20)
        self.add_content(spacing_widget)
    
    def setup_metrics(self):
        """Setup metrics cards with magic icons and larger fonts"""
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # Enhanced metrics with magic card icons
        metrics = [
            ("₹12,500", "Sales Today", SUCCESS, "💰"),
            ("₹8,000", "Pending Payments", DANGER, "⏳"),
            ("120", "Total Invoices", PRIMARY, "📋"),
            ("₹5,200", "Monthly Expenses", PURPLE, "💸")
        ]
        
        for value, label, color, icon in metrics:
            card = MetricCard(value, label, color, icon)
            metrics_layout.addWidget(card)
        
        metrics_widget = QWidget()
        metrics_widget.setLayout(metrics_layout)
        self.add_content(metrics_widget)
        
        # Add spacing widget
        spacing_widget = QWidget()
        spacing_widget.setFixedHeight(30)
        self.add_content(spacing_widget)
    
    def setup_actions(self):
        """Setup action buttons with increased width, filling whole row"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)
        
        actions = [
            ("New Invoice", self.new_invoice, "🧾"),
            ("Add Product", self.add_product, "📦"),
            ("Add Party", self.add_party, "👥"),
            ("Record Payment", self.record_payment, "💳")
        ]
        
        for text, callback, icon in actions:
            btn = QPushButton(f"{icon}  {text}")
            btn.setFixedHeight(50)
            btn.setMinimumWidth(200)  # Increased button width
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 12px 20px;
                }}
                QPushButton:hover {{
                    background: #2563EB;
                }}
                QPushButton:pressed {{
                    background: #1D4ED8;
                }}
            """)
            actions_layout.addWidget(btn)
        
        # Fill the whole row
        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        self.add_content(actions_widget)
        
        # Add spacing widget
        spacing_widget = QWidget()
        spacing_widget.setFixedHeight(30)
        self.add_content(spacing_widget)
    
    def setup_tables_layout(self):
        """Setup tables: Recent invoices (left), Low stock + Payment received (right)"""
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)
        
        # Left side: Recent Invoices (full height)
        recent_invoices = self.create_data_table(
            "Recent Invoices",
            ["Invoice No.", "Date", "Party", "Amount", "Status"],
            self.get_recent_invoices(),
            height=400
        )
        
        # Right side: Two tables vertically stacked
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(15)
        
        # Low Stock table
        low_stock = self.create_data_table(
            "Low Stock Items",
            ["Product", "Current Stock", "Min. Required", "Status"],
            self.get_low_stock_items(),
            height=185
        )
        
        # Payment Received table
        payment_received = self.create_data_table(
            "Recent Payments Received",
            ["Party", "Amount", "Date", "Method"],
            self.get_payment_received(),
            height=185
        )
        
        right_side_layout.addWidget(low_stock)
        right_side_layout.addWidget(payment_received)
        
        right_side_widget = QWidget()
        right_side_widget.setLayout(right_side_layout)
        
        # Add to main layout (60% left, 40% right)
        tables_layout.addWidget(recent_invoices, 3)
        tables_layout.addWidget(right_side_widget, 2)
        
        tables_widget = QWidget()
        tables_widget.setLayout(tables_layout)
        self.add_content(tables_widget)
    
    def create_data_table(self, title, headers, data, height=200):
        """Create a data table with title and custom height"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(title_label)
        
        # Table
        table = CustomTable(len(data), len(headers), headers)
        table.setMaximumHeight(height)
        table.setMinimumHeight(height)
        
        # Enhanced table styling
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {BORDER};
                background-color: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #E5E7EB;
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {PRIMARY};
                color: white;
            }}
            QHeaderView::section {{
                background-color: #F3F4F6;
                color: {TEXT_PRIMARY};
                font-weight: bold;
                border: 1px solid {BORDER};
                padding: 10px;
            }}
        """)
        
        # Populate table
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                table.setItem(row, col, table.create_item(str(cell_data)))
        
        layout.addWidget(table)
        return frame
    
    def get_recent_invoices(self):
        """Get recent invoices data"""
        try:
            invoices = db.get_invoices()
            return [
                [inv['invoice_no'], inv['date'], inv['party_name'] or 'N/A', 
                 f"₹{inv['grand_total']:,.2f}", inv['status']]
                for inv in invoices[:8]  # More invoices for larger table
            ]
        except:
            # Sample data if no database
            return [
                ["INV-1001", "2024-01-01", "ABC Corp", "₹9,500", "Paid"],
                ["INV-1002", "2024-01-02", "XYZ Ltd", "₹1,750", "Unpaid"],
                ["INV-1003", "2024-01-03", "DEF Inc", "₹4,250", "Paid"],
                ["INV-1004", "2024-01-04", "GHI Corp", "₹12,000", "Pending"],
                ["INV-1005", "2024-01-05", "JKL Ltd", "₹8,750", "Paid"],
                ["INV-1006", "2024-01-06", "MNO Inc", "₹3,500", "Unpaid"],
                ["INV-1007", "2024-01-07", "PQR Corp", "₹15,200", "Paid"],
                ["INV-1008", "2024-01-08", "STU Ltd", "₹6,800", "Pending"]
            ]
    
    def get_low_stock_items(self):
        """Get low stock items data"""
        try:
            # This would come from products table with stock management
            products = db.get_products()
            # Filter for low stock items
            low_stock = []
            for product in products:
                current_stock = getattr(product, 'stock', 0)
                min_required = getattr(product, 'min_stock', 10)
                if current_stock <= min_required:
                    status = "Critical" if current_stock < min_required // 2 else "Low"
                    low_stock.append([product['name'], current_stock, min_required, status])
            return low_stock[:5]
        except:
            # Sample data if no database
            return [
                ["Laptop Dell XPS", "2", "10", "Critical"],
                ["Mobile iPhone 15", "5", "15", "Low"],
                ["Printer Canon", "1", "5", "Critical"],
                ["Mouse Wireless", "8", "20", "Low"],
                ["Keyboard RGB", "3", "12", "Low"]
            ]
    
    def get_payment_received(self):
        """Get recent payments received data"""
        try:
            payments = db.get_payments()
            return [
                [pay['party_name'] or 'N/A', f"₹{pay['amount']:,.2f}", 
                 pay['date'], pay.get('payment_method', 'Cash')]
                for pay in payments[:5] if pay.get('type') == 'received'
            ]
        except:
            # Sample data if no database
            return [
                ["ABC Corp", "₹5,000", "2024-01-08", "UPI"],
                ["XYZ Ltd", "₹2,500", "2024-01-07", "Bank Transfer"],
                ["DEF Inc", "₹7,200", "2024-01-06", "Cash"],
                ["GHI Corp", "₹12,000", "2024-01-05", "Cheque"],
                ["JKL Ltd", "₹3,800", "2024-01-04", "UPI"]
            ]
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # This would refresh all metrics and tables
        pass
    
    # Action button callbacks
    def new_invoice(self):
        """Open new invoice dialog"""
        dialog = InvoiceDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Navigate to invoices screen to show the new invoice
            if hasattr(self.parent(), 'navigate_to'):
                self.parent().navigate_to('invoices')
    
    def add_product(self):
        """Open add product dialog"""
        dialog = ProductDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Navigate to products screen to show the new product
            if hasattr(self.parent(), 'navigate_to'):
                self.parent().navigate_to('products')
    
    def add_party(self):
        """Open add party dialog"""
        dialog = PartyDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Navigate to parties screen to show the new party
            if hasattr(self.parent(), 'navigate_to'):
                self.parent().navigate_to('parties')
    
    def record_payment(self):
        """Open record payment dialog"""
        dialog = PaymentDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Navigate to payments screen to show the new payment
            if hasattr(self.parent(), 'navigate_to'):
                self.parent().navigate_to('payments')
    
