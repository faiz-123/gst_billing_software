"""
Payments screen - Record and manage payments
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from .base_screen import BaseScreen
from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY, 
    BORDER, BACKGROUND, get_title_font
)
from database import db

class PaymentDialog(QDialog):
    """Dialog for recording payments"""
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.setWindowTitle("Record Payment" if not payment_data else "Edit Payment")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.parties = []
        self.invoices = []
        self.load_data()
        self.setup_ui()
    
    def load_data(self):
        """Load parties and invoices data"""
        try:
            self.parties = db.get_parties()
            self.invoices = db.get_invoices()
        except:
            # Sample data if database not available
            self.parties = [
                {'id': 1, 'name': 'ABC Corp', 'opening_balance': 5000},
                {'id': 2, 'name': 'XYZ Ltd', 'opening_balance': -2000}
            ]
            self.invoices = [
                {'id': 1, 'invoice_no': 'INV-001', 'party_id': 1, 'grand_total': 54000, 'status': 'Sent'},
                {'id': 2, 'invoice_no': 'INV-002', 'party_id': 2, 'grand_total': 25000, 'status': 'Sent'}
            ]
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Record Payment" if not self.payment_data else "Edit Payment")
        title.setFont(get_title_font(20))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Payment details section
        details_frame = self.create_payment_details()
        layout.addWidget(details_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = CustomButton("Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = CustomButton("Record Payment", "primary")
        save_btn.clicked.connect(self.save_payment)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Populate form if editing
        if self.payment_data:
            self.populate_form()
    
    def create_payment_details(self):
        """Create payment details section"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Section title
        section_title = QLabel("Payment Details")
        section_title.setFont(get_title_font(16))
        section_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(section_title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Payment type
        self.payment_type = QComboBox()
        self.payment_type.addItems(["Payment Received", "Payment Made"])
        self.payment_type.setFixedHeight(40)
        self.payment_type.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        self.payment_type.currentTextChanged.connect(self.on_payment_type_changed)
        form_layout.addRow("Payment Type:", self.payment_type)
        
        # Party selection
        self.party_combo = QComboBox()
        self.party_combo.addItem("Select Party", None)
        self.update_party_combo()
        self.party_combo.setFixedHeight(40)
        self.party_combo.setStyleSheet(self.payment_type.styleSheet())
        self.party_combo.currentTextChanged.connect(self.on_party_changed)
        form_layout.addRow("Party:", self.party_combo)
        
        # Invoice reference (optional)
        self.invoice_combo = QComboBox()
        self.invoice_combo.addItem("No Invoice (Direct Payment)", None)
        self.invoice_combo.setFixedHeight(40)
        self.invoice_combo.setStyleSheet(self.payment_type.styleSheet())
        self.invoice_combo.currentTextChanged.connect(self.on_invoice_changed)
        form_layout.addRow("Invoice (Optional):", self.invoice_combo)
        
        # Amount
        amount_layout = QHBoxLayout()
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setFixedHeight(40)
        self.amount_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
                font-size: 14px;
            }}
        """)
        amount_layout.addWidget(self.amount_input)
        
        # Outstanding amount display
        self.outstanding_label = QLabel("")
        self.outstanding_label.setStyleSheet(f"color: {PRIMARY}; font-weight: bold;")
        amount_layout.addWidget(self.outstanding_label)
        
        amount_widget = QWidget()
        amount_widget.setLayout(amount_layout)
        form_layout.addRow("Amount *:", amount_widget)
        
        # Payment date
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setFixedHeight(40)
        self.payment_date.setStyleSheet(f"""
            QDateEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                background: {WHITE};
            }}
        """)
        form_layout.addRow("Payment Date:", self.payment_date)
        
        # Payment method
        self.payment_method = QComboBox()
        self.payment_method.addItems([
            "Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card", 
            "Debit Card", "Net Banking", "Other"
        ])
        self.payment_method.setFixedHeight(40)
        self.payment_method.setStyleSheet(self.payment_type.styleSheet())
        form_layout.addRow("Payment Method:", self.payment_method)
        
        # Reference number
        self.reference_input = CustomInput("Enter reference/transaction number")
        self.reference_input.setFixedHeight(40)
        form_layout.addRow("Reference No:", self.reference_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add payment notes...")
        self.notes_input.setFixedHeight(80)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: {WHITE};
            }}
        """)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        return frame
    
    def update_party_combo(self):
        """Update party combo based on payment type"""
        payment_type = self.payment_type.currentText()
        self.party_combo.clear()
        self.party_combo.addItem("Select Party", None)
        
        # Filter parties based on payment type
        for party in self.parties:
            if payment_type == "Payment Received":
                # Show customers (parties we receive money from)
                if party.get('type') in ['Customer', 'Both'] or party.get('opening_balance', 0) > 0:
                    self.party_combo.addItem(party['name'], party)
            else:  # Payment Made
                # Show suppliers (parties we pay money to)
                if party.get('type') in ['Supplier', 'Both'] or party.get('opening_balance', 0) < 0:
                    self.party_combo.addItem(party['name'], party)
    
    def on_payment_type_changed(self):
        """Handle payment type change"""
        self.update_party_combo()
        self.update_invoice_combo()
    
    def on_party_changed(self):
        """Handle party selection change"""
        self.update_invoice_combo()
        self.update_outstanding_display()
    
    def update_invoice_combo(self):
        """Update invoice combo based on selected party"""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("No Invoice (Direct Payment)", None)
        
        party_data = self.party_combo.currentData()
        if party_data:
            # Filter invoices for selected party
            party_invoices = [inv for inv in self.invoices if inv.get('party_id') == party_data['id']]
            for invoice in party_invoices:
                if invoice.get('status') != 'Paid':  # Only show unpaid invoices
                    invoice_no = invoice.get('invoice_no', f"INV-{invoice['id']:03d}")
                    invoice_text = f"{invoice_no} - ₹{invoice['grand_total']:,.2f}"
                    self.invoice_combo.addItem(invoice_text, invoice)
    
    def on_invoice_changed(self):
        """Handle invoice selection change"""
        self.update_outstanding_display()
        
        # Auto-fill amount with invoice total
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            self.amount_input.setValue(invoice_data['grand_total'])
    
    def update_outstanding_display(self):
        """Update outstanding amount display"""
        party_data = self.party_combo.currentData()
        invoice_data = self.invoice_combo.currentData()
        
        if invoice_data:
            # Show invoice outstanding
            outstanding = invoice_data['grand_total']
            self.outstanding_label.setText(f"Outstanding: ₹{outstanding:,.2f}")
        elif party_data:
            # Show party balance
            balance = party_data.get('opening_balance', 0)
            if balance > 0:
                self.outstanding_label.setText(f"Receivable: ₹{balance:,.2f}")
            elif balance < 0:
                self.outstanding_label.setText(f"Payable: ₹{abs(balance):,.2f}")
            else:
                self.outstanding_label.setText("No outstanding amount")
        else:
            self.outstanding_label.setText("")
    
    def populate_form(self):
        """Populate form with existing payment data"""
        data = self.payment_data
        
        # Payment type
        type_index = self.payment_type.findText(data.get('type', 'Payment Received'))
        if type_index >= 0:
            self.payment_type.setCurrentIndex(type_index)
        
        # Find and select party
        for i in range(self.party_combo.count()):
            party_data = self.party_combo.itemData(i)
            if party_data and party_data['id'] == data.get('party_id'):
                self.party_combo.setCurrentIndex(i)
                break
        
        # Amount and other fields
        self.amount_input.setValue(data.get('amount', 0))
        
        # Payment date
        from PyQt5.QtCore import QDate
        date_str = data.get('date', QDate.currentDate().toString('yyyy-MM-dd'))
        payment_date = QDate.fromString(date_str, 'yyyy-MM-dd')
        self.payment_date.setDate(payment_date)
        
        # Payment method
        method_index = self.payment_method.findText(data.get('method', 'Cash'))
        if method_index >= 0:
            self.payment_method.setCurrentIndex(method_index)
        
        self.reference_input.setText(data.get('reference', ''))
        self.notes_input.setPlainText(data.get('notes', ''))
    
    def save_payment(self):
        """Save payment data"""
        # Validate required fields
        party_data = self.party_combo.currentData()
        if not party_data:
            QMessageBox.warning(self, "Error", "Please select a party!")
            return
        
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid amount!")
            return
        
        payment_data = {
            'type': self.payment_type.currentText(),
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'amount': amount,
            'date': self.payment_date.date().toString('yyyy-MM-dd'),
            'method': self.payment_method.currentText(),
            'reference': self.reference_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip(),
            'status': 'Completed'
        }
        
        # Add invoice reference if selected
        invoice_data = self.invoice_combo.currentData()
        if invoice_data:
            payment_data['invoice_id'] = invoice_data['id']
            invoice_no = invoice_data.get('invoice_no', f"INV-{invoice_data['id']:03d}")
            payment_data['invoice_no'] = invoice_no
        
        try:
            if self.payment_data:  # Editing
                payment_data['id'] = self.payment_data['id']
                db.update_payment(payment_data)
                QMessageBox.information(self, "Success", "Payment updated successfully!")
            else:  # Recording new
                db.add_payment(payment_data)
                QMessageBox.information(self, "Success", "Payment recorded successfully!")
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment: {str(e)}")

class PaymentsScreen(BaseScreen):
    def __init__(self):
        super().__init__("Payments")
        self.setup_payments_screen()
        self.load_payments_data()
    
    def setup_payments_screen(self):
        """Setup payments screen content"""
        # Top action bar
        self.setup_action_bar()
        
        # Filters and stats
        self.setup_filters_and_stats()
        
        # Payments table
        self.setup_payments_table()
    
    def setup_action_bar(self):
        """Setup top action bar"""
        action_layout = QHBoxLayout()
        
        # Search
        self.search_input = CustomInput("Search payments...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_payments)
        action_layout.addWidget(self.search_input)
        
        action_layout.addStretch()
        
        # Export button
        export_btn = CustomButton("Export", "secondary")
        export_btn.clicked.connect(self.export_payments)
        action_layout.addWidget(export_btn)
        
        # Record payment button
        record_btn = CustomButton("Record Payment", "primary")
        record_btn.clicked.connect(self.record_payment)
        action_layout.addWidget(record_btn)
        
        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        self.add_content(action_widget)
    
    def setup_filters_and_stats(self):
        """Setup filters and quick stats"""
        container = QHBoxLayout()
        
        # Filters section
        filters_layout = QHBoxLayout()
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Payment Received", "Payment Made"])
        self.type_filter.setFixedWidth(150)
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                background: {WHITE};
            }}
        """)
        self.type_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.type_filter)
        
        filters_layout.addSpacing(20)
        
        # Method filter
        filters_layout.addWidget(QLabel("Method:"))
        self.method_filter = QComboBox()
        self.method_filter.addItems([
            "All", "Cash", "Bank Transfer", "Cheque", "UPI", 
            "Credit Card", "Debit Card", "Net Banking", "Other"
        ])
        self.method_filter.setFixedWidth(120)
        self.method_filter.setStyleSheet(self.type_filter.styleSheet())
        self.method_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.method_filter)
        
        filters_layout.addSpacing(20)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Pending", "Failed"])
        self.status_filter.setFixedWidth(100)
        self.status_filter.setStyleSheet(self.type_filter.styleSheet())
        self.status_filter.currentTextChanged.connect(self.filter_payments)
        filters_layout.addWidget(self.status_filter)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.addStretch()
        
        # Total payments
        self.total_payments_label = QLabel("Total: 0")
        self.total_payments_label.setStyleSheet(f"""
            background: {PRIMARY}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.total_payments_label)
        
        # Received amount
        self.received_amount_label = QLabel("Received: ₹0")
        self.received_amount_label.setStyleSheet(f"""
            background: {SUCCESS}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.received_amount_label)
        
        # Paid amount
        self.paid_amount_label = QLabel("Paid: ₹0")
        self.paid_amount_label.setStyleSheet(f"""
            background: {DANGER}; 
            color: {WHITE}; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-weight: bold;
        """)
        stats_layout.addWidget(self.paid_amount_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 15px;
                background: {WHITE};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
            }}
        """)
        refresh_btn.clicked.connect(self.load_payments_data)
        stats_layout.addWidget(refresh_btn)
        
        container.addLayout(filters_layout)
        container.addLayout(stats_layout)
        
        container_widget = QWidget()
        container_widget.setLayout(container)
        self.add_content(container_widget)
    
    def setup_payments_table(self):
        """Setup payments data table"""
        # Table container
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        # Table
        headers = ["Date", "Type", "Party", "Amount", "Method", "Reference", "Status", "Actions"]
        self.payments_table = CustomTable(0, len(headers), headers)
        
        # Set column widths
        self.payments_table.setColumnWidth(0, 100)  # Date
        self.payments_table.setColumnWidth(1, 120)  # Type
        self.payments_table.setColumnWidth(2, 180)  # Party
        self.payments_table.setColumnWidth(3, 120)  # Amount
        self.payments_table.setColumnWidth(4, 100)  # Method
        self.payments_table.setColumnWidth(5, 120)  # Reference
        self.payments_table.setColumnWidth(6, 100)  # Status
        self.payments_table.setColumnWidth(7, 120)  # Actions
        
        table_layout.addWidget(self.payments_table)
        self.add_content(table_frame)
        
        # Store original data for filtering
        self.all_payments_data = []
    
    def load_payments_data(self):
        """Load payments data into table"""
        try:
            payments = db.get_payments()
            self.all_payments_data = payments
            self.populate_table(payments)
            self.update_stats(payments)
        except Exception as e:
            # Show sample data if database not available
            sample_data = [
                {
                    'id': 1, 'type': 'Payment Received', 'party_name': 'ABC Corp', 
                    'amount': 25000, 'date': '2024-01-01', 'method': 'Bank Transfer',
                    'reference': 'TXN123456', 'status': 'Completed'
                },
                {
                    'id': 2, 'type': 'Payment Made', 'party_name': 'XYZ Supplier',
                    'amount': 15000, 'date': '2024-01-02', 'method': 'UPI',
                    'reference': 'UPI789012', 'status': 'Completed'
                }
            ]
            self.all_payments_data = sample_data
            self.populate_table(sample_data)
            self.update_stats(sample_data)
    
    def populate_table(self, payments_data):
        """Populate table with payments data"""
        self.payments_table.setRowCount(len(payments_data))
        
        for row, payment in enumerate(payments_data):
            self.payments_table.setItem(row, 0, self.payments_table.create_item(payment['date']))
            
            # Type with color coding
            payment_type = payment['type']
            type_item = self.payments_table.create_item(payment_type)
            if payment_type == "Payment Received":
                type_item.setBackground(type_item.background().color().lighter(150))
            else:
                type_item.setBackground(type_item.background().color().darker(110))
            self.payments_table.setItem(row, 1, type_item)
            
            self.payments_table.setItem(row, 2, self.payments_table.create_item(payment.get('party_name', 'N/A')))
            
            # Amount with color coding
            amount = payment['amount']
            amount_text = f"₹{amount:,.2f}"
            amount_item = self.payments_table.create_item(amount_text)
            if payment_type == "Payment Received":
                amount_item.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            else:
                amount_item.setStyleSheet(f"color: {DANGER}; font-weight: bold;")
            self.payments_table.setItem(row, 3, amount_item)
            
            self.payments_table.setItem(row, 4, self.payments_table.create_item(payment.get('method', '')))
            self.payments_table.setItem(row, 5, self.payments_table.create_item(payment.get('reference', '')))
            
            # Status
            status = payment.get('status', 'Completed')
            status_item = self.payments_table.create_item(status)
            if status == "Completed":
                status_item.setBackground(status_item.background().color().lighter(150))
            elif status == "Failed":
                status_item.setBackground(status_item.background().color().darker(120))
            self.payments_table.setItem(row, 6, status_item)
            
            # Action buttons
            actions_widget = self.create_action_buttons(payment)
            self.payments_table.setCellWidget(row, 7, actions_widget)
    
    def create_action_buttons(self, payment):
        """Create action buttons for each row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(25, 25)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {PRIMARY};
                border-radius: 12px;
                background: {WHITE};
                color: {PRIMARY};
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_payment(payment))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.setStyleSheet(view_btn.styleSheet())
        edit_btn.clicked.connect(lambda: self.edit_payment(payment))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(25, 25)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {DANGER};
                border-radius: 12px;
                background: {WHITE};
                color: {DANGER};
            }}
            QPushButton:hover {{
                background: {DANGER};
                color: {WHITE};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_payment(payment))
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_stats(self, payments):
        """Update quick stats labels"""
        total_count = len(payments)
        received_amount = sum(p['amount'] for p in payments if p['type'] == 'Payment Received')
        paid_amount = sum(p['amount'] for p in payments if p['type'] == 'Payment Made')
        
        self.total_payments_label.setText(f"Total: {total_count}")
        self.received_amount_label.setText(f"Received: ₹{received_amount:,.0f}")
        self.paid_amount_label.setText(f"Paid: ₹{paid_amount:,.0f}")
    
    def filter_payments(self):
        """Filter payments based on search and filters"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        method_filter = self.method_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_data = []
        for payment in self.all_payments_data:
            # Search filter
            if search_text:
                searchable_text = f"{payment.get('party_name', '')} {payment.get('reference', '')}".lower()
                if search_text not in searchable_text:
                    continue
            
            # Type filter
            if type_filter != "All" and payment['type'] != type_filter:
                continue
            
            # Method filter
            if method_filter != "All" and payment.get('method', '') != method_filter:
                continue
            
            # Status filter
            if status_filter != "All" and payment.get('status', 'Completed') != status_filter:
                continue
            
            filtered_data.append(payment)
        
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)
    
    def record_payment(self):
        """Open record payment dialog"""
        dialog = PaymentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def edit_payment(self, payment):
        """Open edit payment dialog"""
        dialog = PaymentDialog(self, payment)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments_data()
    
    def view_payment(self, payment):
        """View payment details"""
        details = f"""
Payment Details:

Type: {payment['type']}
Party: {payment.get('party_name', 'N/A')}
Amount: ₹{payment['amount']:,.2f}
Date: {payment['date']}
Method: {payment.get('method', 'N/A')}
Reference: {payment.get('reference', 'N/A')}
Status: {payment.get('status', 'N/A')}
Notes: {payment.get('notes', 'N/A')}
        """
        QMessageBox.information(self, "Payment Details", details.strip())
    
    def delete_payment(self, payment):
        """Delete payment with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this payment of ₹{payment['amount']:,.2f}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_payment(payment['id'])
                QMessageBox.information(self, "Success", "Payment deleted successfully!")
                self.load_payments_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete payment: {str(e)}")
    
    def export_payments(self):
        """Export payments data"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")
    
    def refresh_data(self):
        """Refresh payments data"""
        self.load_payments_data()
