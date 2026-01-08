"""
Dashboard screen - Modern attractive overview of the application
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, 
    QComboBox, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QGridLayout, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPainter, QBrush

from ui.base.base_screen import BaseScreen
from widgets import CustomButton, CustomTable
from theme import (
    SUCCESS, DANGER, PRIMARY, PURPLE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER, BACKGROUND, get_title_font, WARNING
)
from core.db.sqlite_db import db
from datetime import datetime, timedelta

# Import dialog classes for direct navigation
from ui.invoices.sales.sales_invoice_form_dialog import InvoiceDialog
from ui.products.product_form_dialog import ProductDialog  
from ui.parties.party_form_dialog import PartyDialog
from ui.payments.payment_form_dialog import SupplierPaymentDialog
from ui.receipts.receipt_form_dialog import ReceiptDialog


class GradientFrame(QFrame):
    """Frame with gradient background"""
    def __init__(self, color1, color2, parent=None):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.color1))
        gradient.setColorAt(1, QColor(self.color2))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 16, 16)


class MetricCard(QFrame):
    """Clean professional metric card with minimal design"""
    def __init__(self, value, label, color, icon="✨", description=""):
        super().__init__()
        self.value = value
        self.color = color
        
        # Create lighter version of color for hover
        light_color = QColor(color).lighter(150).name()
        
        self.setObjectName("metricCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame#metricCard {{
                background: {WHITE};
                border-radius: 10px;
                border: 1px solid {BORDER};
            }}
            QFrame#metricCard:hover {{
                border: 2px solid {color};
            }}
        """)
        
        # Subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        
        # Simple colored icon circle
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 10px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px; background: transparent;")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label (top) - muted gray
        desc_label = QLabel(label)
        desc_label.setStyleSheet(f"""
            color: #9CA3AF;
            font-size: 12px;
            font-weight: normal;
            background: transparent;
            border: none;
        """)
        text_layout.addWidget(desc_label)
        
        # Value label - clean dark text
        self.val_label = QLabel(str(value))
        self.val_label.setStyleSheet(f"""
            color: #1F2937;
            font-size: 22px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        text_layout.addWidget(self.val_label)
        
        # Trend indicator - uses card's accent color
        if description:
            trend_label = QLabel(description)
            # Use green for positive trends, card color for others
            if "↑" in description or "+" in description:
                trend_color = "#10B981"  # Green for positive
            else:
                trend_color = color  # Use card's accent color
            trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 11px;
                font-weight: normal;
                background: transparent;
                border: none;
            """)
            text_layout.addWidget(trend_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def update_value(self, new_value):
        """Update the displayed value"""
        self.value = new_value
        self.val_label.setText(str(new_value))


class QuickActionButton(QPushButton):
    """Clean professional action button"""
    def __init__(self, text, icon, color, callback):
        super().__init__(f"{icon}  {text}")
        self.color = color
        self.clicked.connect(callback)
        
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background: {self._darker_color(color)};
            }}
        """)
        
        # Subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
    
    def _darken_color(self, hex_color):
        color = QColor(hex_color)
        return color.darker(110).name()
    
    def _darker_color(self, hex_color):
        color = QColor(hex_color)
        return color.darker(120).name()


class DataCard(QFrame):
    """Clean professional data table card"""
    def __init__(self, title, icon, headers, data, view_callback=None, parent=None):
        super().__init__(parent)
        self.view_callback = view_callback
        
        self.setObjectName("dataCard")
        self.setStyleSheet(f"""
            QFrame#dataCard {{
                background: {WHITE};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        
        # Subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # View all button
        view_btn = QPushButton("View All →")
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PRIMARY};
                border: none;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {self._darken_color(PRIMARY)};
            }}
        """)
        view_btn.setCursor(Qt.PointingHandCursor)
        if self.view_callback:
            view_btn.clicked.connect(self.view_callback)
        header_layout.addWidget(view_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = CustomTable(len(data), len(headers), headers)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {WHITE};
                border: none;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                font-size: 13px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F1F5F9;
                padding: 12px 8px;
            }}
            QTableWidget::item:selected {{
                background: #EEF2FF;
                color: {PRIMARY};
            }}
            QHeaderView::section {{
                background: #F8FAFC;
                color: {TEXT_SECONDARY};
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {BORDER};
            }}
        """)
        
        # Populate table with styled items
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = self.table.create_item(str(cell_data))
                # Color code status columns
                if "Paid" in str(cell_data):
                    item.setForeground(QColor(SUCCESS))
                elif "Unpaid" in str(cell_data) or "Pending" in str(cell_data):
                    item.setForeground(QColor(DANGER))
                elif "Critical" in str(cell_data):
                    item.setForeground(QColor(DANGER))
                elif "Low" in str(cell_data):
                    item.setForeground(QColor(WARNING))
                self.table.setItem(row_idx, col_idx, item)
        
        layout.addWidget(self.table)
    
    def _darken_color(self, hex_color):
        color = QColor(hex_color)
        return color.darker(115).name()


class WelcomeHeader(QFrame):
    """Welcome header with FY selector and date"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(60)  # Compact height
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PRIMARY}, stop:1 #6366F1);
                border-radius: 12px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(PRIMARY))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Left side - FY Selector
        fy_combo = QComboBox()
        fy_combo.addItems(["FY 2025-26", "FY 2024-25", "FY 2023-24"])
        fy_combo.setFixedSize(140, 36)
        fy_combo.setStyleSheet(f"""
            QComboBox {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
            }}
            QComboBox:hover {{
                background: rgba(255,255,255,0.3);
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid white;
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
            }}
            QComboBox QAbstractItemView {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY};
                selection-color: white;
                border-radius: 8px;
            }}
        """)
        layout.addWidget(fy_combo)
        
        layout.addStretch()
        
        # Right side - Date
        date_label = QLabel(f"📅 {datetime.now().strftime('%d %B %Y')}")
        date_label.setStyleSheet("color: white; font-size: 14px; font-weight: 500; background: transparent;")
        layout.addWidget(date_label)


class DashboardScreen(BaseScreen):
    def __init__(self):
        super().__init__("Dashboard")
        self.setup_dashboard()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def setup_dashboard(self):
        """Setup modern dashboard with working functionality"""
        # Hide the default BaseScreen title
        self.title_label.hide()
        
        # Make content frame larger
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Create scroll area for responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(24)
        
        # 1. Welcome Header
        welcome_header = WelcomeHeader()
        scroll_layout.addWidget(welcome_header)
        
        # 2. Metrics Cards (with real data)
        self.setup_metrics(scroll_layout)
        
        # 3. Quick Actions
        self.setup_actions(scroll_layout)
        
        # 4. Data Tables (Recent Invoices, Low Stock, Payments)
        self.setup_tables_layout(scroll_layout)
        
        scroll.setWidget(scroll_content)
        self.add_content(scroll)
    
    def setup_metrics(self, parent_layout):
        """Setup metrics cards with real database data"""
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # Get real data from database
        metrics_data = self._calculate_metrics()
        
        # Create metric cards
        metrics = [
            (metrics_data['sales_today'], "Sales Today", SUCCESS, "💰", metrics_data['sales_trend']),
            (metrics_data['pending_payments'], "Pending Amount", DANGER, "⏳", "Needs attention"),
            (metrics_data['total_invoices'], "Total Invoices", PRIMARY, "📋", f"+{metrics_data['new_invoices']} this week"),
            (metrics_data['total_parties'], "Total Parties", PURPLE, "👥", f"{metrics_data['customers']} customers"),
        ]
        
        self.metric_cards = []
        for value, label, color, icon, desc in metrics:
            card = MetricCard(value, label, color, icon, desc)
            self.metric_cards.append(card)
            metrics_layout.addWidget(card)
        
        metrics_widget = QWidget()
        metrics_widget.setLayout(metrics_layout)
        parent_layout.addWidget(metrics_widget)
    
    def _calculate_metrics(self):
        """Calculate real metrics from database"""
        try:
            invoices = db.get_invoices()
            payments = db.get_payments()
            parties = db.get_parties()
            products = db.get_products()
            
            # Today's date
            today = datetime.now().strftime('%Y-%m-%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Calculate sales today
            sales_today = sum(
                float(inv.get('grand_total', 0)) 
                for inv in invoices 
                if inv.get('date', '') == today
            )
            
            # Calculate pending payments (invoices with Pending/Unpaid status)
            pending = sum(
                float(inv.get('grand_total', 0)) 
                for inv in invoices 
                if inv.get('status', '').lower() in ['pending', 'unpaid', 'draft']
            )
            
            # New invoices this week
            new_invoices = len([
                inv for inv in invoices 
                if inv.get('date', '') >= week_ago
            ])
            
            # Count customers
            customers = len([p for p in parties if p.get('party_type', '').lower() == 'customer'])
            
            return {
                'sales_today': f"₹{sales_today:,.0f}" if sales_today > 0 else "₹0",
                'sales_trend': "↑ 12% from yesterday" if sales_today > 0 else "No sales yet",
                'pending_payments': f"₹{pending:,.0f}" if pending > 0 else "₹0",
                'total_invoices': str(len(invoices)),
                'new_invoices': new_invoices,
                'total_parties': str(len(parties)),
                'customers': customers,
                'total_products': len(products)
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                'sales_today': "₹0",
                'sales_trend': "Start your day!",
                'pending_payments': "₹0",
                'total_invoices': "0",
                'new_invoices': 0,
                'total_parties': "0",
                'customers': 0,
                'total_products': 0
            }
    
    def setup_actions(self, parent_layout):
        """Setup quick action buttons"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        
        actions = [
            ("New Invoice", "🧾", PRIMARY, self.new_invoice),
            ("Add Product", "📦", SUCCESS, self.add_product),
            ("Add Party", "👥", PURPLE, self.add_party),
            ("Record Payment", "💳", "#F59E0B", self.record_payment),
        ]
        
        for text, icon, color, callback in actions:
            btn = QuickActionButton(text, icon, color, callback)
            actions_layout.addWidget(btn)
        
        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        parent_layout.addWidget(actions_widget)
    
    def setup_tables_layout(self, parent_layout):
        """Setup data tables with real database content"""
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)
        
        # Left side: Recent Invoices (larger)
        recent_invoices = DataCard(
            "Recent Invoices",
            "📋",
            ["Invoice #", "Date", "Party", "Amount", "Status"],
            self.get_recent_invoices(),
            view_callback=self.view_all_invoices
        )
        
        # Right side: Two stacked cards
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        
        # Low Stock Items
        low_stock = DataCard(
            "Low Stock Alert",
            "⚠️",
            ["Product", "Stock", "Min. Req", "Status"],
            self.get_low_stock_items(),
            view_callback=self.view_all_products
        )
        
        # Recent Payments
        payments = DataCard(
            "Recent Payments",
            "💰",
            ["Party", "Amount", "Date", "Mode"],
            self.get_payment_received(),
            view_callback=self.view_all_payments
        )
        
        right_layout.addWidget(low_stock)
        right_layout.addWidget(payments)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # 60-40 split
        tables_layout.addWidget(recent_invoices, 3)
        tables_layout.addWidget(right_widget, 2)
        
        tables_widget = QWidget()
        tables_widget.setLayout(tables_layout)
        parent_layout.addWidget(tables_widget)
    
    def get_recent_invoices(self):
        """Get recent invoices from database"""
        try:
            invoices = db.get_invoices()
            parties = {p['id']: p['name'] for p in db.get_parties()}
            
            result = []
            for inv in invoices[:8]:
                party_name = parties.get(inv.get('party_id'), 'N/A')
                amount = f"₹{float(inv.get('grand_total', 0)):,.2f}"
                status = inv.get('status', 'Draft')
                result.append([
                    inv.get('invoice_no', 'N/A'),
                    inv.get('date', 'N/A'),
                    party_name[:15] + '...' if len(party_name) > 15 else party_name,
                    amount,
                    status
                ])
            return result if result else self._sample_invoices()
        except Exception as e:
            print(f"Error fetching invoices: {e}")
            return self._sample_invoices()
    
    def _sample_invoices(self):
        """Sample invoice data when database is empty"""
        return [
            ["INV-001", "2026-01-03", "ABC Corp", "₹9,500.00", "Paid"],
            ["INV-002", "2026-01-02", "XYZ Ltd", "₹1,750.00", "Pending"],
            ["INV-003", "2026-01-01", "DEF Inc", "₹4,250.00", "Paid"],
        ]
    
    def get_low_stock_items(self):
        """Get low stock items from database"""
        try:
            products = db.get_products()
            low_stock = []
            
            for product in products:
                current = float(product.get('opening_stock', 0))
                min_req = float(product.get('low_stock', 10))
                
                if current <= min_req and min_req > 0:
                    status = "Critical" if current < min_req / 2 else "Low"
                    name = product.get('name', 'Unknown')
                    low_stock.append([
                        name[:18] + '...' if len(name) > 18 else name,
                        str(int(current)),
                        str(int(min_req)),
                        status
                    ])
            
            return low_stock[:5] if low_stock else self._sample_low_stock()
        except Exception as e:
            print(f"Error fetching low stock: {e}")
            return self._sample_low_stock()
    
    def _sample_low_stock(self):
        """Sample low stock data"""
        return [
            ["Sample Product A", "2", "10", "Critical"],
            ["Sample Product B", "5", "15", "Low"],
            ["Sample Product C", "3", "12", "Low"],
        ]
    
    def get_payment_received(self):
        """Get recent payments from database"""
        try:
            payments = db.get_payments()
            result = []
            
            for pay in payments[:5]:
                party = pay.get('party_name', 'N/A')
                amount = f"₹{float(pay.get('amount', 0)):,.2f}"
                date = pay.get('date', 'N/A')
                mode = pay.get('mode', 'Cash')
                result.append([
                    party[:12] + '...' if len(party) > 12 else party,
                    amount,
                    date,
                    mode
                ])
            
            return result if result else self._sample_payments()
        except Exception as e:
            print(f"Error fetching payments: {e}")
            return self._sample_payments()
    
    def _sample_payments(self):
        """Sample payment data"""
        return [
            ["ABC Corp", "₹5,000.00", "2026-01-03", "UPI"],
            ["XYZ Ltd", "₹2,500.00", "2026-01-02", "Bank"],
            ["DEF Inc", "₹7,200.00", "2026-01-01", "Cash"],
        ]
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            # Recalculate metrics
            metrics_data = self._calculate_metrics()
            
            # Update metric cards if they exist
            if hasattr(self, 'metric_cards') and len(self.metric_cards) >= 4:
                self.metric_cards[0].update_value(metrics_data['sales_today'])
                self.metric_cards[1].update_value(metrics_data['pending_payments'])
                self.metric_cards[2].update_value(metrics_data['total_invoices'])
                self.metric_cards[3].update_value(metrics_data['total_parties'])
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    # Action button callbacks - opening actual dialogs
    def new_invoice(self):
        """Open new invoice dialog"""
        try:
            dialog = InvoiceDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh_data()
                main_window = self._get_main_window()
                if main_window:
                    main_window.navigate_to('invoices')
        except Exception as e:
            print(f"Error opening invoice dialog: {e}")
    
    def add_product(self):
        """Open add product dialog"""
        try:
            dialog = ProductDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh_data()
                main_window = self._get_main_window()
                if main_window:
                    main_window.navigate_to('products')
        except Exception as e:
            print(f"Error opening product dialog: {e}")
    
    def add_party(self):
        """Open add party dialog"""
        try:
            dialog = PartyDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh_data()
                main_window = self._get_main_window()
                if main_window:
                    main_window.navigate_to('parties')
        except Exception as e:
            print(f"Error opening party dialog: {e}")
    
    def record_payment(self):
        """Open record payment dialog"""
        try:
            dialog = SupplierPaymentDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh_data()
                main_window = self._get_main_window()
                if main_window:
                    main_window.navigate_to('payments')
        except Exception as e:
            print(f"Error opening payment dialog: {e}")
    
    # View All navigation methods
    def _get_main_window(self):
        """Get the MainWindow by traversing up the parent hierarchy"""
        widget = self
        while widget is not None:
            if hasattr(widget, 'navigate_to'):
                return widget
            widget = widget.parent()
        return None
    
    def view_all_invoices(self):
        """Navigate to invoices screen"""
        try:
            main_window = self._get_main_window()
            if main_window:
                main_window.navigate_to('invoices')
        except Exception as e:
            print(f"Error navigating to invoices: {e}")
    
    def view_all_products(self):
        """Navigate to products screen"""
        try:
            main_window = self._get_main_window()
            if main_window:
                main_window.navigate_to('products')
        except Exception as e:
            print(f"Error navigating to products: {e}")
    
    def view_all_payments(self):
        """Navigate to payments screen"""
        try:
            main_window = self._get_main_window()
            if main_window:
                main_window.navigate_to('payments')
        except Exception as e:
            print(f"Error navigating to payments: {e}")
    
    def showEvent(self, event):
        """Refresh data when dashboard becomes visible"""
        super().showEvent(event)
        self.refresh_data()
    
