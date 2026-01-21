"""
Payments List Screen - Supplier Payments (Money OUT)
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import QWidget, QDialog, QMessageBox
from PySide6.QtCore import Qt, Signal

# Theme imports
from theme import PRIMARY, SUCCESS, DANGER, WARNING, WARNING_LIGHT, DANGER_LIGHT, PRIMARY_LIGHT

# Widget imports
from widgets import StatCard, ListTable, TableFrame, StatsContainer, FilterWidget
from ui.base.list_table_helper import ListTableHelper

# Controller import (NOT service directly)
from controllers.payment_controller import payment_controller

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base.base_list_screen import BaseListScreen
from ui.payments.payment_form_dialog import SupplierPaymentDialog
from ui.error_handler import UIErrorHandler

logger = get_logger(__name__)


class PaymentsScreen(BaseListScreen):
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return the text for the add button."""
        return "+ Add Payment"
    
    def _get_entity_name(self) -> str:
        """Return the entity name for pagination display."""
        return "payment"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Creators (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section using StatsContainer."""
        # Create stat cards - for supplier payments (money OUT)
        self._total_paid_card = StatCard("💸", "Total Paid", "₹0", DANGER)
        self._total_count_card = StatCard("📋", "Total Payments", "0", PRIMARY)
        self._month_total_card = StatCard("📅", "This Month", "₹0", WARNING)
        self._suppliers_card = StatCard("🏢", "Suppliers Paid", "0", SUCCESS)
        
        return StatsContainer([
            self._total_paid_card,
            self._total_count_card,
            self._month_total_card,
            self._suppliers_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget for consistency."""
        self._filter_widget = FilterWidget()
        
        # Search filter
        search_input = self._filter_widget.add_search_filter("Search supplier payments...")
        self._filter_widget.search_changed.connect(self._on_search_changed)
        
        # Method filter
        method_options = {
            "All Methods": "All Methods",
            "Cash": "Cash",
            "Bank Transfer": "Bank Transfer",
            "UPI": "UPI",
            "Cheque": "Cheque",
            "Credit Card": "Credit Card",
            "Debit Card": "Debit Card",
            "Net Banking": "Net Banking",
            "Other": "Other"
        }
        self._method_combo = self._filter_widget.add_combo_filter("method", "Method:", method_options)
        
        # Period filter
        period_options = {
            "All Time": "All Time",
            "Today": "Today",
            "This Week": "This Week",
            "This Month": "This Month",
            "This Year": "This Year"
        }
        self._period_combo = self._filter_widget.add_combo_filter("period", "Period:", period_options)
        
        # Status filter
        status_options = {
            "All Status": "All Status",
            "Completed": "Completed",
            "Pending": "Pending",
            "Failed": "Failed"
        }
        self._status_combo = self._filter_widget.add_combo_filter("status", "Status:", status_options)
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the payments table."""
        frame = TableFrame()
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "#", "Date", "Supplier", "Amount", "Method", 
            "Reference", "Invoice", "Status", "Actions"
        ])
        
        # Column configuration
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},     # #
            {"width": 100, "resize": "fixed"},    # Date
            {"resize": "stretch"},                 # Supplier
            {"width": 120, "resize": "fixed"},    # Amount
            {"width": 110, "resize": "fixed"},    # Method
            {"width": 130, "resize": "fixed"},    # Reference
            {"width": 100, "resize": "fixed"},    # Invoice
            {"width": 90, "resize": "fixed"},     # Status
            {"width": 140, "resize": "fixed"},    # Actions
        ])
        
        # Initialize ListTableHelper for populating the table
        self._table_helper = ListTableHelper(self._table, self.ITEMS_PER_PAGE)
        
        # Define column configurations for table population (columns 0-6 only, 7-8 are custom)
        self._column_configs = [
            {'type': 'row_number'},
            {'key': 'date', 'type': 'date', 'align': Qt.AlignCenter,
             'formatter': lambda v: str(v) if v else ''},
            {'key': 'party_name', 'type': 'text', 'bold': True,
             'formatter': lambda v: v or 'N/A'},
            {'key': 'amount', 'type': 'currency', 'bold': True, 'align': Qt.AlignRight, 'color': DANGER},
            {'key': 'mode', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: v or 'Cash'},
            {'key': 'reference', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: v or '-'},
            {'key': 'invoice_id', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: f"PUR-{v}" if v else '-'},
        ]
        
        frame.set_table(self._table)
        return frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_all_data(self) -> list:
        """Fetch all payments from controller.
        
        Returns:
            List of all payment records
        """
        return self._controller.get_all_payments()
    
    def filter_data(self, all_data: list) -> list:
        """Filter payments based on current filter selections.
        
        Args:
            all_data: List of all payments to filter
            
        Returns:
            Filtered list of payments
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        method_filter = self._method_combo.currentData() if hasattr(self, '_method_combo') else "All Methods"
        period_filter = self._period_combo.currentData() if hasattr(self, '_period_combo') else "All Time"
        status_filter = self._status_combo.currentData() if hasattr(self, '_status_combo') else "All Status"
        
        return self._apply_filters(all_data, search_text, method_filter, period_filter, status_filter)
    
    def _apply_filters(self, payments: list, search_text: str, method_filter: str, 
                       period_filter: str, status_filter: str) -> list:
        """Apply filters to payments list - delegates to controller.
        
        Args:
            payments: List of payments to filter
            search_text: Search text
            method_filter: Payment method filter value
            period_filter: Period filter value
            status_filter: Status filter value
            
        Returns:
            Filtered list of payments
        """
        return self._controller.filter_payments(
            payments=payments,
            search_text=search_text,
            method_filter=method_filter,
            period_filter=period_filter,
            status_filter=status_filter
        )
    
    def _update_stats(self, all_data: list):
        """Update statistics cards with payment data.
        
        Args:
            all_data: List of all payments (unfiltered)
        """
        stats = self._controller.calculate_stats(all_data)
        self._total_paid_card.set_value(f"₹{stats.total_paid:,.0f}")
        self._total_count_card.set_value(str(stats.total_count))
        self._month_total_card.set_value(f"₹{stats.month_total:,.0f}")
        self._suppliers_card.set_value(str(stats.suppliers_count))
    
    def _populate_table(self, payments: list):
        """Populate table with payment data using ListTableHelper.
        
        Args:
            payments: List of payments for current page
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(payments)} payments using ListTableHelper")
        
        # Use ListTableHelper to populate basic columns (0-6)
        self._table_helper.populate(
            data=payments,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Add custom widgets for status (col 7) and action buttons (col 8)
        for row in range(self._table.rowCount()):
            payment = payments[row] if row < len(payments) else None
            if payment:
                # Column 7: Status badge using helper
                status = payment.get('status', 'Completed')
                status_widget = self._table_helper.create_status_badge(status)
                self._table.setCellWidget(row, 7, status_widget)
                
                # Column 8: Action buttons using helper
                actions = [
                    {'text': 'View', 'tooltip': 'View Payment Details', 'bg_color': PRIMARY_LIGHT, 
                     'hover_color': PRIMARY, 'callback': lambda checked, p=payment: self._on_view_clicked(p)},
                    {'text': 'Edit', 'tooltip': 'Edit Payment', 'bg_color': WARNING_LIGHT, 
                     'hover_color': WARNING, 'callback': lambda checked, p=payment: self._on_edit_clicked(p)},
                    {'text': 'Del', 'tooltip': 'Delete Payment', 'bg_color': DANGER_LIGHT, 
                     'hover_color': DANGER, 'callback': lambda checked, p=payment: self._on_delete_clicked(p)},
                ]
                actions_widget = self._table_helper.create_action_buttons(actions)
                self._table.setCellWidget(row, 8, actions_widget)
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Screen-specific)
    # ─────────────────────────────────────────────────────────────────────────
    
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
    