"""
Invoice Viewer Screen - Display full invoice details with line items
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QMessageBox, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSplitter,
    QAbstractItemView, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from widgets import CustomButton, CustomTable
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER
)
from database import db


class InvoiceViewerWidget(QWidget):
    """Widget to display complete invoice details"""
    
    edit_requested = pyqtSignal(str)  # Signal to edit invoice
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_invoice = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the invoice viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with search and actions
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Invoice header section
        self.header_frame = self.create_invoice_header_section()
        splitter.addWidget(self.header_frame)
        
        # Items table section
        self.items_frame = self.create_items_section()
        splitter.addWidget(self.items_frame)
        
        # Totals section
        self.totals_frame = self.create_totals_section()
        splitter.addWidget(self.totals_frame)
        
        splitter.setSizes([200, 300, 150])
        layout.addWidget(splitter)
        
        # Initially hide all content
        self.show_no_invoice_message()
    
    def create_header(self):
        """Create header with search and action buttons"""
        layout = QHBoxLayout()
        
        # Search section
        search_label = QLabel("🔍 Search Invoice:")
        search_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 14px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter invoice number (e.g., INV-002)")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 16px;
                color: {TEXT_PRIMARY};
                background: {WHITE};
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY};
            }}
        """)
        self.search_input.setFixedWidth(300)
        self.search_input.returnPressed.connect(self.search_invoice)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedSize(100, 40)
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_HOVER};
            }}
        """)
        self.search_btn.clicked.connect(self.search_invoice)
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)
        layout.addStretch()
        
        # Action buttons
        self.edit_btn = QPushButton("📝 Edit")
        self.edit_btn.setFixedSize(100, 40)
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WARNING};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #F59E0B;
            }}
        """)
        self.edit_btn.clicked.connect(self.edit_invoice)
        self.edit_btn.setVisible(False)
        
        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.setFixedSize(100, 40)
        self.print_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """)
        self.print_btn.clicked.connect(self.print_invoice)
        self.print_btn.setVisible(False)
        
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.print_btn)
        
        return layout
    
    def create_invoice_header_section(self):
        """Create invoice header details section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QGridLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create labels for invoice header
        self.invoice_no_label = self.create_info_label("", "Invoice Number")
        self.date_label = self.create_info_label("", "Invoice Date")
        self.due_date_label = self.create_info_label("", "Due Date")
        self.party_label = self.create_info_label("", "Customer/Client")
        self.status_label = self.create_info_label("", "Status")
        
        # Layout in grid
        layout.addWidget(QLabel("📄 Invoice Number:"), 0, 0)
        layout.addWidget(self.invoice_no_label, 0, 1)
        layout.addWidget(QLabel("📅 Date:"), 0, 2)
        layout.addWidget(self.date_label, 0, 3)
        
        layout.addWidget(QLabel("🏢 Customer:"), 1, 0)
        layout.addWidget(self.party_label, 1, 1, 1, 2)
        layout.addWidget(QLabel("📊 Status:"), 1, 3)
        layout.addWidget(self.status_label, 1, 4)
        
        return frame
    
    def create_items_section(self):
        """Create items table section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("🛍️ Invoice Items")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {TEXT_PRIMARY};
                padding: 10px;
                border: none;
            }}
        """)
        layout.addWidget(title)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {BORDER};
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {BACKGROUND};
                color: {TEXT_PRIMARY};
                font-weight: bold;
                border: 1px solid {BORDER};
                padding: 8px;
            }}
        """)
        
        layout.addWidget(self.items_table)
        return frame
    
    def create_totals_section(self):
        """Create totals summary section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Notes section (left side)
        notes_layout = QVBoxLayout()
        notes_label = QLabel("📝 Notes:")
        notes_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY};")
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setMaximumHeight(100)
        self.notes_display.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px;
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
            }}
        """)
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_display)
        notes_layout.addStretch()
        
        layout.addLayout(notes_layout, 2)
        layout.addStretch(1)
        
        # Totals section (right side)
        totals_layout = QVBoxLayout()
        
        self.subtotal_label = self.create_total_label("Subtotal:", "₹0.00")
        self.discount_label = self.create_total_label("Total Discount:", "₹0.00", color="#EF4444")
        self.tax_label = self.create_total_label("Total Tax:", "₹0.00")
        self.grand_total_label = self.create_total_label("Grand Total:", "₹0.00", 
                                                        size="20px", bold=True, color=PRIMARY)
        
        for label_pair in [self.subtotal_label, self.discount_label, 
                          self.tax_label, self.grand_total_label]:
            row_layout = QHBoxLayout()
            row_layout.addWidget(label_pair[0])
            row_layout.addWidget(label_pair[1])
            totals_layout.addLayout(row_layout)
        
        layout.addLayout(totals_layout, 1)
        return frame
    
    def create_info_label(self, text, placeholder=""):
        """Create styled info label"""
        label = QLabel(text or f"[{placeholder}]")
        label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY if text else TEXT_SECONDARY};
                font-size: 14px;
                font-weight: {"bold" if text else "normal"};
                padding: 5px;
                border: none;
                background: transparent;
            }}
        """)
        return label
    
    def create_total_label(self, title, amount, color=None, size="16px", bold=False):
        """Create total label pair (title, amount)"""
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: {size};
                font-weight: {"bold" if bold else "normal"};
                border: none;
                text-align: right;
            }}
        """)
        
        amount_label = QLabel(amount)
        amount_label.setStyleSheet(f"""
            QLabel {{
                color: {color or TEXT_PRIMARY};
                font-size: {size};
                font-weight: {"bold" if bold else "normal"};
                border: none;
                text-align: right;
                padding: 5px 10px;
                background: {BACKGROUND if bold else "transparent"};
                border-radius: 6px;
            }}
        """)
        amount_label.setFixedWidth(120)
        amount_label.setAlignment(Qt.AlignRight)
        
        return (title_label, amount_label)
    
    def show_no_invoice_message(self):
        """Show message when no invoice is loaded"""
        self.current_invoice = None
        
        # Hide action buttons
        self.edit_btn.setVisible(False)
        self.print_btn.setVisible(False)
        
        # Clear all displays
        self.invoice_no_label.setText("[No invoice loaded]")
        self.date_label.setText("[No date]")
        self.party_label.setText("[No customer]")
        self.status_label.setText("[No status]")
        
        # Clear items table
        self.items_table.setRowCount(0)
        self.items_table.setColumnCount(0)
        
        # Clear totals
        self.subtotal_label[1].setText("₹0.00")
        self.discount_label[1].setText("₹0.00")
        self.tax_label[1].setText("₹0.00")
        self.grand_total_label[1].setText("₹0.00")
        
        # Clear notes
        self.notes_display.setText("")
    
    def search_invoice(self):
        """Search for invoice by number"""
        invoice_no = self.search_input.text().strip()
        if not invoice_no:
            QMessageBox.warning(self, "Error", "Please enter an invoice number")
            return
        
        try:
            # Get complete invoice with items
            invoice_data = db.get_invoice_with_items(invoice_no)
            
            if not invoice_data:
                QMessageBox.information(self, "Not Found", 
                                      f"Invoice '{invoice_no}' not found in database")
                self.show_no_invoice_message()
                return
            
            self.display_invoice(invoice_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error searching invoice: {str(e)}")
            self.show_no_invoice_message()
    
    def display_invoice(self, invoice_data):
        """Display complete invoice data"""
        self.current_invoice = invoice_data
        
        invoice = invoice_data['invoice']
        party = invoice_data['party']
        items = invoice_data['items']
        
        # Show action buttons
        self.edit_btn.setVisible(True)
        self.print_btn.setVisible(True)
        
        # Update header information
        self.invoice_no_label.setText(invoice['invoice_no'])
        self.date_label.setText(invoice['date'])
        self.party_label.setText(party['name'] if party else f"Party ID: {invoice['party_id']}")
        self.status_label.setText(invoice.get('status', 'Unknown'))
        
        # Update items table
        self.populate_items_table(items)
        
        # Calculate and display totals
        self.update_totals(items, invoice)
        
        # Update notes
        self.notes_display.setText(invoice.get('notes', 'No additional notes'))
    
    def populate_items_table(self, items):
        """Populate the items table with line items"""
        if not items:
            self.items_table.setRowCount(0)
            self.items_table.setColumnCount(0)
            return
        
        # Set up table headers
        headers = ["No", "Product", "HSN Code", "Qty", "Unit", "Rate", 
                  "Disc%", "Tax%", "Amount"]
        self.items_table.setColumnCount(len(headers))
        self.items_table.setHorizontalHeaderLabels(headers)
        self.items_table.setRowCount(len(items))
        
        # Populate data
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.items_table.setItem(row, 1, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 2, QTableWidgetItem(item['hsn_code'] or ''))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['quantity']:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(item['unit']))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"₹{item['rate']:,.2f}"))
            self.items_table.setItem(row, 6, QTableWidgetItem(f"{item['discount_percent']:.1f}%"))
            self.items_table.setItem(row, 7, QTableWidgetItem(f"{item['tax_percent']:.1f}%"))
            self.items_table.setItem(row, 8, QTableWidgetItem(f"₹{item['amount']:,.2f}"))
        
        # Adjust column widths
        header = self.items_table.horizontalHeader()
        header.setStretchLastSection(False)
        for i in range(len(headers)):
            if i == 1:  # Product name column
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def update_totals(self, items, invoice):
        """Update totals display"""
        if not items:
            return
        
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        total_discount = sum(item['discount_amount'] for item in items)
        total_tax = sum(item['tax_amount'] for item in items)
        
        self.subtotal_label[1].setText(f"₹{subtotal:,.2f}")
        self.discount_label[1].setText(f"-₹{total_discount:,.2f}")
        self.tax_label[1].setText(f"₹{total_tax:,.2f}")
        self.grand_total_label[1].setText(f"₹{invoice['grand_total']:,.2f}")
    
    def edit_invoice(self):
        """Edit the current invoice"""
        if self.current_invoice:
            from .invoice_dialogue import InvoiceDialog
            invoice_no = self.current_invoice['invoice']['invoice_no']
            
            # Create edit dialog with existing invoice data
            dialog = InvoiceDialog(self, invoice_data=self.current_invoice, invoice_number=invoice_no)
            if dialog.exec_() == dialog.Accepted:
                # Refresh the display after editing
                self.search_invoice()  # Re-search to show updated data
    
    def print_invoice(self):
        """Print the current invoice"""
        if self.current_invoice:
            QMessageBox.information(self, "Print", "Print functionality will be implemented soon!")


class InvoiceViewerScreen(QWidget):
    """Main invoice viewer screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main screen"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("📄 Invoice Viewer")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {TEXT_PRIMARY};
                padding: 20px;
                background: {BACKGROUND};
                border-bottom: 2px solid {BORDER};
            }}
        """)
        layout.addWidget(title)
        
        # Main viewer widget
        self.viewer = InvoiceViewerWidget()
        layout.addWidget(self.viewer)
