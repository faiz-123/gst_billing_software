"""
Payments List Screen - Supplier Payments (Money OUT)
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFrame,
    QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

# Theme imports
from theme import (
    PRIMARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    SUCCESS, DANGER, WARNING,
    FONT_SIZE_SMALL,
    get_title_font, get_normal_font, get_bold_font,
    get_filter_combo_style, get_filter_frame_style,
    get_search_container_style, get_search_input_style, get_icon_button_style,
    get_filter_label_style, get_clear_button_style
)

# Widget imports
from widgets import CustomButton, StatCard, ListTable, TableFrame, TableActionButton

# Controller import (NOT service directly)
from controllers.payment_controller import payment_controller, PaymentFilters

# Core imports for formatting only
from core.core_utils import format_currency

# UI imports
from ui.base import BaseScreen
from ui.payments.payment_form_dialog import SupplierPaymentDialog
from ui.error_handler import UIErrorHandler


class PaymentsScreen(BaseScreen):
    """
    Screen for managing supplier payments (money going out).
    
    This UI component handles:
    - Layout and visual presentation
    - User interactions (clicks, typing)
    - Signal emissions for external communication
    
    Business logic is delegated to PaymentController.
    """
    
    # Signal emitted when payment data changes
    payment_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Payments (Money Out)", parent=parent)
        self.setObjectName("PaymentsScreen")
        self._controller = payment_controller
        self._setup_ui()
        self._load_data()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible."""
        super().showEvent(event)
        self._load_data()
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Setup Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Hide default BaseScreen elements
        self.title_label.hide()
        self.content_frame.hide()
        
        # Configure main layout
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Add sections
        self.main_layout.addWidget(self._create_header())
        self.main_layout.addWidget(self._create_stats_section())
        self.main_layout.addWidget(self._create_filters_section())
        self.main_layout.addWidget(self._create_table_section(), 1)
    
    def _create_header(self) -> QWidget:
        """Create header with title and add button."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("💸 Payments (Money Out)")
        title.setFont(get_title_font())
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Export button
        export_btn = CustomButton("📤 Export", "secondary")
        export_btn.setFixedWidth(120)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(export_btn)
        
        # Add button
        add_btn = CustomButton("+ Add Payment", "primary")
        add_btn.setFixedWidth(160)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(add_btn)
        
        return header
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section."""
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Create stat cards - for supplier payments (money OUT)
        self._total_paid_card = StatCard("💸", "Total Paid", "₹0", DANGER)
        self._total_count_card = StatCard("📋", "Total Payments", "0", PRIMARY)
        self._month_total_card = StatCard("📅", "This Month", "₹0", WARNING)
        self._suppliers_card = StatCard("🏢", "Suppliers Paid", "0", SUCCESS)
        
        layout.addWidget(self._total_paid_card)
        layout.addWidget(self._total_count_card)
        layout.addWidget(self._month_total_card)
        layout.addWidget(self._suppliers_card)
        
        return container
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section with search and filters."""
        container = QFrame()
        container.setStyleSheet(get_filter_frame_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Search container
        search_container = self._create_search_input()
        layout.addWidget(search_container)
        
        # Method filter
        method_label = QLabel("Method:")
        method_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(method_label)
        
        self._method_combo = QComboBox()
        self._method_combo.setStyleSheet(get_filter_combo_style())
        self._method_combo.addItems([
            "All Methods", "Cash", "Bank Transfer", "UPI", 
            "Cheque", "Credit Card", "Debit Card", "Net Banking", "Other"
        ])
        self._method_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._method_combo)
        
        # Period filter
        period_label = QLabel("Period:")
        period_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(period_label)
        
        self._period_combo = QComboBox()
        self._period_combo.setStyleSheet(get_filter_combo_style())
        self._period_combo.addItems([
            "All Time", "Today", "This Week", "This Month", "This Year"
        ])
        self._period_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._period_combo)
        
        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(status_label)
        
        self._status_combo = QComboBox()
        self._status_combo.setStyleSheet(get_filter_combo_style())
        self._status_combo.addItems(["All Status", "Completed", "Pending", "Failed"])
        self._status_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._status_combo)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Refresh Data")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(get_icon_button_style())
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh_btn)
        
        # Clear filters button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(32)
        clear_btn.setToolTip("Clear All Filters")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(get_clear_button_style())
        clear_btn.clicked.connect(self._on_clear_filters)
        layout.addWidget(clear_btn)
        
        return container
    
    def _create_search_input(self) -> QFrame:
        """Create styled search input container."""
        container = QFrame()
        container.setObjectName("searchContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container.setMinimumWidth(250)
        container.setMaximumWidth(400)
        container.setFixedHeight(40)
        container.setStyleSheet(get_search_container_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)
        
        # Search icon
        icon = QLabel("🔍")
        icon.setStyleSheet("border: none; font-size: 14px;")
        layout.addWidget(icon)
        
        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search supplier payments...")
        self._search_input.setStyleSheet(get_search_input_style())
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)
        
        return container
    
    def _create_table_section(self) -> QWidget:
        """Create the payments table."""
        frame = TableFrame()
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "Date", "Supplier", "Amount", "Method", 
            "Reference", "Invoice", "Status", "Actions"
        ])
        
        # Column configuration
        self._table.configure_columns([
            {"width": 100, "resize": "fixed"},    # Date
            {"resize": "stretch"},                 # Supplier
            {"width": 120, "resize": "fixed"},    # Amount
            {"width": 110, "resize": "fixed"},    # Method
            {"width": 130, "resize": "fixed"},    # Reference
            {"width": 100, "resize": "fixed"},    # Invoice
            {"width": 90, "resize": "fixed"},     # Status
            {"width": 140, "resize": "fixed"},    # Actions
        ])
        
        frame.set_table(self._table)
        return frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self):
        """Load payments from controller and update UI."""
        try:
            # Get current filter values
            filters = self._get_current_filters()
            
            # Fetch filtered data and stats from controller
            payments, stats = self._controller.get_filtered_payments(filters=filters)
            
            # Update UI
            self._update_stats_display(stats)
            self._populate_table(payments)
            
        except Exception as e:
            self._show_error("Load Error", f"Failed to load payments: {str(e)}")
    
    def _get_current_filters(self) -> PaymentFilters:
        """Get current filter values from UI controls."""
        return PaymentFilters(
            search_text=self._search_input.text().strip() if hasattr(self, '_search_input') else "",
            method=self._method_combo.currentText() if hasattr(self, '_method_combo') else "All Methods",
            period=self._period_combo.currentText() if hasattr(self, '_period_combo') else "All Time",
            status=self._status_combo.currentText() if hasattr(self, '_status_combo') else "All Status"
        )
    
    def _update_stats_display(self, stats):
        """Update statistics cards with data from controller."""
        self._total_paid_card.set_value(f"₹{stats.total_paid:,.0f}")
        self._total_count_card.set_value(str(stats.total_count))
        self._month_total_card.set_value(f"₹{stats.month_total:,.0f}")
        self._suppliers_card.set_value(str(stats.suppliers_count))
    
    def _populate_table(self, payments: list):
        """Populate table with payment data."""
        self._table.setRowCount(0)
        
        for idx, payment in enumerate(payments):
            self._add_table_row(idx, payment)
    
    def _add_table_row(self, idx: int, payment: dict):
        """Add a single row to the table."""
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Date
        date_item = QTableWidgetItem(str(payment.get('date', '')))
        date_item.setTextAlignment(Qt.AlignCenter)
        date_item.setData(Qt.UserRole, payment.get('id'))  # Store ID
        self._table.setItem(row, 0, date_item)
        
        # Column 1: Supplier name
        supplier_item = QTableWidgetItem(str(payment.get('party_name', 'N/A')))
        supplier_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        self._table.setItem(row, 1, supplier_item)
        
        # Column 2: Amount (red for money OUT)
        amount = float(payment.get('amount') or 0)
        amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        amount_item.setForeground(QColor(DANGER))  # Red for money OUT
        self._table.setItem(row, 2, amount_item)
        
        # Column 3: Method
        method_item = QTableWidgetItem(str(payment.get('mode', 'Cash')))
        method_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 3, method_item)
        
        # Column 4: Reference
        reference_item = QTableWidgetItem(str(payment.get('reference', '') or '-'))
        reference_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 4, reference_item)
        
        # Column 5: Invoice (linked purchase invoice)
        invoice_id = payment.get('invoice_id')
        invoice_text = f"PUR-{invoice_id}" if invoice_id else "-"
        invoice_item = QTableWidgetItem(invoice_text)
        invoice_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 5, invoice_item)
        
        # Column 6: Status with color
        status = payment.get('status', 'Completed')
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        status_colors = {
            'Completed': (SUCCESS, "#D1FAE5"),
            'Pending': (WARNING, "#FEF3C7"),
            'Failed': (DANGER, "#FEE2E2"),
        }
        
        if status in status_colors:
            color, bg_color = status_colors[status]
            status_item.setForeground(QColor(color))
            status_item.setBackground(QColor(bg_color))
        
        self._table.setItem(row, 6, status_item)
        
        # Column 7: Action buttons
        actions_widget = self._create_action_buttons(payment)
        self._table.setCellWidget(row, 7, actions_widget)
    
    def _create_action_buttons(self, payment: dict) -> QWidget:
        """Create styled action buttons for table row."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # View button
        view_btn = TableActionButton(
            text="View",
            tooltip="View Payment Details",
            bg_color="#EEF2FF",
            hover_color=PRIMARY
        )
        view_btn.clicked.connect(lambda checked, p=payment: self._on_view_clicked(p))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = TableActionButton(
            text="Edit",
            tooltip="Edit Payment",
            bg_color="#FEF3C7",
            hover_color=WARNING
        )
        edit_btn.clicked.connect(lambda checked, p=payment: self._on_edit_clicked(p))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = TableActionButton(
            text="Del",
            tooltip="Delete Payment",
            bg_color="#FEE2E2",
            hover_color=DANGER
        )
        delete_btn.clicked.connect(lambda checked, p=payment: self._on_delete_clicked(p))
        layout.addWidget(delete_btn)
        
        return widget

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Slots)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self._load_data()
    
    def _on_filter_changed(self, index: int):
        """Handle filter combo change."""
        self._load_data()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_data()
    
    def _on_clear_filters(self):
        """Clear all filter controls and reload data."""
        self._search_input.clear()
        self._method_combo.setCurrentIndex(0)
        self._period_combo.setCurrentIndex(0)
        self._status_combo.setCurrentIndex(0)
        self._load_data()
    
    def _on_add_clicked(self):
        """Handle add payment button click."""
        dialog = SupplierPaymentDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.payment_updated.emit()
    
    def _on_view_clicked(self, payment: dict):
        """Handle view button click - show payment details."""
        invoice_text = f"PUR-{payment.get('invoice_id')}" if payment.get('invoice_id') else '-'
        notes = (payment.get('notes', '') or '').replace('[PAYMENT]', '').strip() or '-'
        
        details = f"""
<h3>💸 Supplier Payment Details</h3>

<p><b>Supplier:</b> {payment.get('party_name', 'N/A')}</p>
<p><b>Amount:</b> ₹{payment.get('amount', 0):,.2f}</p>
<p><b>Date:</b> {payment.get('date', 'N/A')}</p>
<p><b>Method:</b> {payment.get('mode', 'N/A')}</p>
<p><b>Reference:</b> {payment.get('reference', 'N/A') or '-'}</p>
<p><b>Invoice:</b> {invoice_text}</p>
<p><b>Status:</b> {payment.get('status', 'N/A')}</p>
<p><b>Notes:</b> {notes}</p>
        """
        QMessageBox.information(self, "Payment Details", details.strip())
    
    def _on_edit_clicked(self, payment: dict):
        """Handle edit button click."""
        dialog = SupplierPaymentDialog(parent=self, payment_data=payment)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.payment_updated.emit()
    
    def _on_delete_clicked(self, payment: dict):
        """Handle delete button click with confirmation."""
        party_name = payment.get('party_name', 'Unknown')
        amount = float(payment.get('amount') or 0)
        payment_id = payment.get('id')
        
        # Use UIErrorHandler for consistent confirmation
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete this supplier payment?\n\n"
            f"Supplier: {party_name}\n"
            f"Amount: ₹{amount:,.2f}\n"
            f"Date: {payment.get('date', '')}\n\n"
            f"This action cannot be undone."
        ):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_payment(payment_id)
        
        if success:
            UIErrorHandler.show_success("Success", "✓ Payment deleted successfully!")
            self._load_data()
            self.payment_updated.emit()
        else:
            UIErrorHandler.show_error("Error", message)
    
    def _on_export_clicked(self):
        """Handle export button click."""
        UIErrorHandler.show_warning(
            "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export payment data to CSV or Excel."
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Dialog Helpers
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh the payments list."""
        self._load_data()
