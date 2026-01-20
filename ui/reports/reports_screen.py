"""
Reports screen - Comprehensive business reports and analytics
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, 
    QGridLayout, QComboBox, QDateEdit, QSpinBox, QScrollArea, QFileDialog,
    QMessageBox, QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtPrintSupport import QPrinter

from ui.base.base_screen import BaseScreen
from widgets import CustomButton, CustomTable
from theme import (
    PRIMARY, WHITE, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, BACKGROUND,
    SUCCESS, DANGER, WARNING, PURPLE, get_title_font
)
from core.db.sqlite_db import db
from datetime import datetime, timedelta
import json
import csv
import os


class ReportsScreen(BaseScreen):
    """Reports and analytics screen with multiple report types"""
    
    def __init__(self):
        super().__init__(title="Reports & Analytics")
        self.setup_reports_ui()
        
    def setup_reports_ui(self):
        """Setup reports UI with tabs and various report options"""
        # Clear default content
        while self.content_layout.count():
            self.content_layout.takeAt(0)
            
        # Create tab widget for different reports
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {BORDER}; }}
            QTabBar::tab {{ 
                background: {BACKGROUND}; 
                color: {TEXT_PRIMARY};
                padding: 8px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{ 
                background: {WHITE};
                border-bottom: 2px solid {PRIMARY};
            }}
        """)
        
        # Create different report tabs
        self.create_sales_report_tab()
        self.create_purchase_report_tab()
        self.create_party_report_tab()
        self.create_product_report_tab()
        self.create_tax_report_tab()
        self.create_payment_report_tab()
        
        self.content_layout.addWidget(self.tabs)
        
    def create_sales_report_tab(self):
        """Create sales report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Filters section
        filter_layout = self.create_filter_section("Sales Report Filters")
        layout.addLayout(filter_layout)
        
        # Report table
        self.sales_table = CustomTable()
        self.sales_table.setColumnCount(8)
        self.sales_table.setHorizontalHeaderLabels([
            "Invoice No", "Date", "Party", "Amount", "CGST", "SGST", "IGST", "Total"
        ])
        layout.addWidget(QLabel("Sales Records:"))
        layout.addWidget(self.sales_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_sales_report,
            on_export_csv=lambda: self.export_to_csv(self.sales_table, "sales_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.sales_table, "sales_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Sales Report")
        
    def create_purchase_report_tab(self):
        """Create purchase report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Filters section
        filter_layout = self.create_filter_section("Purchase Report Filters")
        layout.addLayout(filter_layout)
        
        # Report table
        self.purchase_table = CustomTable()
        self.purchase_table.setColumnCount(8)
        self.purchase_table.setHorizontalHeaderLabels([
            "Invoice No", "Date", "Supplier", "Amount", "CGST", "SGST", "IGST", "Total"
        ])
        layout.addWidget(QLabel("Purchase Records:"))
        layout.addWidget(self.purchase_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_purchase_report,
            on_export_csv=lambda: self.export_to_csv(self.purchase_table, "purchase_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.purchase_table, "purchase_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Purchase Report")
        
    def create_party_report_tab(self):
        """Create party/customer report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        self.total_parties_label = self.create_stat_card("Total Parties", "0")
        self.active_parties_label = self.create_stat_card("Active Parties", "0")
        self.total_outstanding_label = self.create_stat_card("Outstanding", "₹ 0")
        
        stats_layout.addWidget(self.total_parties_label)
        stats_layout.addWidget(self.active_parties_label)
        stats_layout.addWidget(self.total_outstanding_label)
        layout.addLayout(stats_layout)
        
        # Report table
        self.party_table = CustomTable()
        self.party_table.setColumnCount(6)
        self.party_table.setHorizontalHeaderLabels([
            "Party Name", "Type", "Total Transactions", "Total Amount", "Outstanding", "Last Transaction"
        ])
        layout.addWidget(QLabel("Party Details:"))
        layout.addWidget(self.party_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_party_report,
            on_export_csv=lambda: self.export_to_csv(self.party_table, "party_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.party_table, "party_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Party Report")
        
    def create_product_report_tab(self):
        """Create product report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        self.total_products_label = self.create_stat_card("Total Products", "0")
        self.total_quantity_label = self.create_stat_card("Total Quantity", "0")
        self.total_value_label = self.create_stat_card("Total Value", "₹ 0")
        
        stats_layout.addWidget(self.total_products_label)
        stats_layout.addWidget(self.total_quantity_label)
        stats_layout.addWidget(self.total_value_label)
        layout.addLayout(stats_layout)
        
        # Report table
        self.product_table = CustomTable()
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels([
            "Product Name", "HSN Code", "Total Quantity", "Unit Price", "Total Amount", "Tax Rate", "Category"
        ])
        layout.addWidget(QLabel("Product Details:"))
        layout.addWidget(self.product_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_product_report,
            on_export_csv=lambda: self.export_to_csv(self.product_table, "product_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.product_table, "product_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Product Report")
        
    def create_tax_report_tab(self):
        """Create tax compliance report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Tax summary stats
        stats_layout = QHBoxLayout()
        self.cgst_collected_label = self.create_stat_card("CGST Collected", "₹ 0")
        self.sgst_collected_label = self.create_stat_card("SGST Collected", "₹ 0")
        self.igst_collected_label = self.create_stat_card("IGST Collected", "₹ 0")
        
        stats_layout.addWidget(self.cgst_collected_label)
        stats_layout.addWidget(self.sgst_collected_label)
        stats_layout.addWidget(self.igst_collected_label)
        layout.addLayout(stats_layout)
        
        # Filters
        filter_layout = self.create_filter_section("Tax Report Filters")
        layout.addLayout(filter_layout)
        
        # Tax report table
        self.tax_table = CustomTable()
        self.tax_table.setColumnCount(7)
        self.tax_table.setHorizontalHeaderLabels([
            "Invoice No", "Date", "Party", "Taxable Amount", "CGST %", "SGST %", "IGST %"
        ])
        layout.addWidget(QLabel("Tax Details:"))
        layout.addWidget(self.tax_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_tax_report,
            on_export_csv=lambda: self.export_to_csv(self.tax_table, "tax_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.tax_table, "tax_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Tax Report")
        
    def create_payment_report_tab(self):
        """Create payment and receipt report tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Payment summary stats
        stats_layout = QHBoxLayout()
        self.total_received_label = self.create_stat_card("Total Received", "₹ 0")
        self.total_paid_label = self.create_stat_card("Total Paid", "₹ 0")
        self.pending_payments_label = self.create_stat_card("Pending", "₹ 0")
        
        stats_layout.addWidget(self.total_received_label)
        stats_layout.addWidget(self.total_paid_label)
        stats_layout.addWidget(self.pending_payments_label)
        layout.addLayout(stats_layout)
        
        # Filters
        filter_layout = self.create_filter_section("Payment Report Filters")
        layout.addLayout(filter_layout)
        
        # Payment table
        self.payment_table = CustomTable()
        self.payment_table.setColumnCount(6)
        self.payment_table.setHorizontalHeaderLabels([
            "Payment No", "Date", "Party", "Type", "Amount", "Mode"
        ])
        layout.addWidget(QLabel("Payment Records:"))
        layout.addWidget(self.payment_table)
        
        # Action buttons
        button_layout = self.create_action_buttons(
            on_view=self.load_payment_report,
            on_export_csv=lambda: self.export_to_csv(self.payment_table, "payment_report"),
            on_export_pdf=lambda: self.export_to_pdf(self.payment_table, "payment_report")
        )
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab_widget, "Payment Report")
        
    def create_filter_section(self, title):
        """Create reusable filter section"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Filter controls
        filter_controls = QHBoxLayout()
        
        # Date range
        from_date_label = QLabel("From Date:")
        from_date_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setStyleSheet(self.get_input_style())
        
        to_date_label = QLabel("To Date:")
        to_date_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet(self.get_input_style())
        
        filter_controls.addWidget(from_date_label)
        filter_controls.addWidget(self.from_date)
        filter_controls.addWidget(to_date_label)
        filter_controls.addWidget(self.to_date)
        filter_controls.addStretch()
        
        layout.addLayout(filter_controls)
        return layout
        
    def create_action_buttons(self, on_view=None, on_export_csv=None, on_export_pdf=None):
        """Create action buttons for reports"""
        layout = QHBoxLayout()
        
        view_btn = CustomButton("Generate Report", PRIMARY)
        view_btn.clicked.connect(on_view)
        
        export_csv_btn = CustomButton("Export CSV", SUCCESS)
        export_csv_btn.clicked.connect(on_export_csv)
        
        export_pdf_btn = CustomButton("Export PDF", WARNING)
        export_pdf_btn.clicked.connect(on_export_pdf)
        
        layout.addWidget(view_btn)
        layout.addWidget(export_csv_btn)
        layout.addWidget(export_pdf_btn)
        layout.addStretch()
        
        return layout
        
    def create_stat_card(self, label, value):
        """Create a stat card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        card.setFixedHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {PRIMARY}; font-size: 18px; font-weight: bold;")
        
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        
        return card
        
    def get_input_style(self):
        """Get input field styling"""
        return f"""
            QDateEdit {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 5px;
            }}
            QDateEdit::drop-down {{
                border: none;
            }}
        """
        
    def load_sales_report(self):
        """Load and display sales report"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get invoices from database
            all_invoices = db.get_invoices() if hasattr(db, 'get_invoices') else []
            
            # Filter by date and type (Sales invoices are type 0 or NULL, Purchase are type 1)
            invoices = [
                inv for inv in all_invoices 
                if inv.get('date', '') >= from_date and inv.get('date', '') <= to_date
                and (inv.get('internal_type') is None or inv.get('internal_type') == 0 or inv.get('internal_type') == 'SALES')
            ]
            
            self.populate_sales_table(invoices)
            QMessageBox.information(self, "Success", f"Sales report loaded successfully! ({len(invoices)} records)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sales report: {str(e)}")
            
    def load_purchase_report(self):
        """Load and display purchase report"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get purchase invoices
            all_invoices = db.get_invoices() if hasattr(db, 'get_invoices') else []
            
            # Filter by date and type (Purchase invoices are type 1 or 'PURCHASE')
            purchases = [
                inv for inv in all_invoices 
                if inv.get('date', '') >= from_date and inv.get('date', '') <= to_date
                and (inv.get('internal_type') == 1 or inv.get('internal_type') == 'PURCHASE')
            ]
            
            self.populate_purchase_table(purchases)
            QMessageBox.information(self, "Success", f"Purchase report loaded successfully! ({len(purchases)} records)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load purchase report: {str(e)}")
            
    def load_party_report(self):
        """Load and display party report"""
        try:
            parties = db.get_parties() if hasattr(db, 'get_parties') else []
            self.populate_party_table(parties)
            self.update_party_stats(parties)
            QMessageBox.information(self, "Success", "Party report loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load party report: {str(e)}")
            
    def load_product_report(self):
        """Load and display product report"""
        try:
            products = db.get_products() if hasattr(db, 'get_products') else []
            self.populate_product_table(products)
            self.update_product_stats(products)
            QMessageBox.information(self, "Success", "Product report loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load product report: {str(e)}")
            
    def load_tax_report(self):
        """Load and display tax report"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get all invoices
            all_invoices = db.get_invoices() if hasattr(db, 'get_invoices') else []
            
            # Filter by date range
            invoices = [
                inv for inv in all_invoices 
                if inv.get('date', '') >= from_date and inv.get('date', '') <= to_date
            ]
            
            self.populate_tax_table(invoices)
            self.update_tax_stats(invoices)
            QMessageBox.information(self, "Success", f"Tax report loaded successfully! ({len(invoices)} records)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tax report: {str(e)}")
            
    def load_payment_report(self):
        """Load and display payment report"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            payments = db.get_payments() if hasattr(db, 'get_payments') else []
            self.populate_payment_table(payments)
            self.update_payment_stats(payments)
            QMessageBox.information(self, "Success", "Payment report loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payment report: {str(e)}")
            
    def populate_sales_table(self, invoices):
        """Populate sales table with data"""
        self.sales_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            # Get party name from party_id
            party_name = ""
            if invoice.get('party_id') and hasattr(db, 'get_party_by_id'):
                party = db.get_party_by_id(invoice.get('party_id'))
                party_name = party.get('name', '') if party else ""
            
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(invoice.get('invoice_no', ''))))
            self.sales_table.setItem(row, 1, QTableWidgetItem(str(invoice.get('date', ''))))
            self.sales_table.setItem(row, 2, QTableWidgetItem(party_name))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"₹ {float(invoice.get('subtotal', 0)):.2f}"))
            self.sales_table.setItem(row, 4, QTableWidgetItem(f"₹ {float(invoice.get('cgst', 0)):.2f}"))
            self.sales_table.setItem(row, 5, QTableWidgetItem(f"₹ {float(invoice.get('sgst', 0)):.2f}"))
            self.sales_table.setItem(row, 6, QTableWidgetItem(f"₹ {float(invoice.get('igst', 0)):.2f}"))
            self.sales_table.setItem(row, 7, QTableWidgetItem(f"₹ {float(invoice.get('grand_total', 0)):.2f}"))
            
    def populate_purchase_table(self, invoices):
        """Populate purchase table with data"""
        self.purchase_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            # Get party name from party_id
            party_name = ""
            if invoice.get('party_id') and hasattr(db, 'get_party_by_id'):
                party = db.get_party_by_id(invoice.get('party_id'))
                party_name = party.get('name', '') if party else ""
            
            self.purchase_table.setItem(row, 0, QTableWidgetItem(str(invoice.get('invoice_no', ''))))
            self.purchase_table.setItem(row, 1, QTableWidgetItem(str(invoice.get('date', ''))))
            self.purchase_table.setItem(row, 2, QTableWidgetItem(party_name))
            self.purchase_table.setItem(row, 3, QTableWidgetItem(f"₹ {float(invoice.get('subtotal', 0)):.2f}"))
            self.purchase_table.setItem(row, 4, QTableWidgetItem(f"₹ {float(invoice.get('cgst', 0)):.2f}"))
            self.purchase_table.setItem(row, 5, QTableWidgetItem(f"₹ {float(invoice.get('sgst', 0)):.2f}"))
            self.purchase_table.setItem(row, 6, QTableWidgetItem(f"₹ {float(invoice.get('igst', 0)):.2f}"))
            self.purchase_table.setItem(row, 7, QTableWidgetItem(f"₹ {float(invoice.get('grand_total', 0)):.2f}"))
            
    def populate_party_table(self, parties):
        """Populate party table with data"""
        self.party_table.setRowCount(len(parties))
        for row, party in enumerate(parties):
            self.party_table.setItem(row, 0, QTableWidgetItem(str(party.get('name', ''))))
            self.party_table.setItem(row, 1, QTableWidgetItem(str(party.get('type', ''))))
            self.party_table.setItem(row, 2, QTableWidgetItem(str(party.get('transaction_count', 0))))
            self.party_table.setItem(row, 3, QTableWidgetItem(f"₹ {float(party.get('total_amount', 0)):.2f}"))
            self.party_table.setItem(row, 4, QTableWidgetItem(f"₹ {float(party.get('outstanding', 0)):.2f}"))
            self.party_table.setItem(row, 5, QTableWidgetItem(str(party.get('last_transaction', ''))))
            
    def populate_product_table(self, products):
        """Populate product table with data"""
        self.product_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.product_table.setItem(row, 0, QTableWidgetItem(str(product.get('name', ''))))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(product.get('hsn_code', ''))))
            self.product_table.setItem(row, 2, QTableWidgetItem(str(int(product.get('current_stock', 0)))))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"₹ {float(product.get('sales_rate', 0)):.2f}"))
            self.product_table.setItem(row, 4, QTableWidgetItem(f"₹ {float(product.get('sales_rate', 0)) * float(product.get('current_stock', 0)):.2f}"))
            self.product_table.setItem(row, 5, QTableWidgetItem(f"{float(product.get('tax_rate', 0)):.0f}%"))
            self.product_table.setItem(row, 6, QTableWidgetItem(str(product.get('category', ''))))
            
    def populate_tax_table(self, invoices):
        """Populate tax table with data"""
        self.tax_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            # Get party name from party_id
            party_name = ""
            if invoice.get('party_id') and hasattr(db, 'get_party_by_id'):
                party = db.get_party_by_id(invoice.get('party_id'))
                party_name = party.get('name', '') if party else ""
            
            self.tax_table.setItem(row, 0, QTableWidgetItem(str(invoice.get('invoice_no', ''))))
            self.tax_table.setItem(row, 1, QTableWidgetItem(str(invoice.get('date', ''))))
            self.tax_table.setItem(row, 2, QTableWidgetItem(party_name))
            self.tax_table.setItem(row, 3, QTableWidgetItem(f"₹ {float(invoice.get('subtotal', 0)):.2f}"))
            self.tax_table.setItem(row, 4, QTableWidgetItem("9%"))
            self.tax_table.setItem(row, 5, QTableWidgetItem("9%"))
            self.tax_table.setItem(row, 6, QTableWidgetItem("0%"))
            
    def populate_payment_table(self, payments):
        """Populate payment table with data"""
        self.payment_table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            self.payment_table.setItem(row, 0, QTableWidgetItem(str(payment.get('id', ''))))
            self.payment_table.setItem(row, 1, QTableWidgetItem(str(payment.get('date', ''))))
            self.payment_table.setItem(row, 2, QTableWidgetItem(str(payment.get('party_name', ''))))
            self.payment_table.setItem(row, 3, QTableWidgetItem(str(payment.get('type', ''))))
            self.payment_table.setItem(row, 4, QTableWidgetItem(f"₹ {float(payment.get('amount', 0)):.2f}"))
            self.payment_table.setItem(row, 5, QTableWidgetItem(str(payment.get('mode', ''))))
            
    def update_party_stats(self, parties):
        """Update party statistics"""
        total = len(parties)
        active = sum(1 for p in parties if p.get('active'))
        outstanding = sum(float(p.get('outstanding', 0)) for p in parties)
        
        labels = self.total_parties_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(str(total))
        
        labels = self.active_parties_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(str(active))
            
        labels = self.total_outstanding_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {outstanding:.2f}")
        
    def update_product_stats(self, products):
        """Update product statistics"""
        total = len(products)
        qty = sum(int(p.get('current_stock', 0)) for p in products)
        value = sum(float(p.get('sales_rate', 0)) * float(p.get('current_stock', 0)) for p in products)
        
        labels = self.total_products_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(str(total))
        
        labels = self.total_quantity_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(str(int(qty)))
            
        labels = self.total_value_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {value:.2f}")
        
    def update_tax_stats(self, invoices):
        """Update tax statistics"""
        cgst = sum(float(inv.get('cgst', 0)) for inv in invoices)
        sgst = sum(float(inv.get('sgst', 0)) for inv in invoices)
        igst = sum(float(inv.get('igst', 0)) for inv in invoices)
        
        labels = self.cgst_collected_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {cgst:.2f}")
        
        labels = self.sgst_collected_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {sgst:.2f}")
            
        labels = self.igst_collected_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {igst:.2f}")
        
    def update_payment_stats(self, payments):
        """Update payment statistics"""
        total_received = sum(float(p.get('amount', 0)) for p in payments if p.get('type') == 'RECEIPT')
        total_paid = sum(float(p.get('amount', 0)) for p in payments if p.get('type') == 'PAYMENT')
        pending = 0  # Calculate from invoices if needed
        
        labels = self.total_received_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {total_received:.2f}")
        
        labels = self.total_paid_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {total_paid:.2f}")
            
        labels = self.pending_payments_label.findChildren(QLabel)
        if labels:
            labels[-1].setText(f"₹ {pending:.2f}")
        
    def export_to_csv(self, table, report_name):
        """Export table to CSV file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {report_name}",
                f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = []
                for col in range(table.columnCount()):
                    headers.append(table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Success", f"Report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV: {str(e)}")
            
    def export_to_pdf(self, table, report_name):
        """Export table to PDF file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {report_name}",
                f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
                
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            
            # Create PDF with table data
            from PySide6.QtGui import QPainter, QFont
            painter = QPainter(printer)
            
            if not painter.isActive():
                printer.setPageSize(QPrinter.A4)
                printer.setOrientation(QPrinter.Landscape)
                
            QMessageBox.information(self, "Success", f"Report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")
            
    def refresh_data(self):
        """Refresh report data when screen is shown"""
        pass
