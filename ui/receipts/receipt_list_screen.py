"""
Receipts List Screen - Customer Receipts (Money IN)
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
from controllers.receipt_controller import receipt_controller, ReceiptFilters

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base.base_list_screen import BaseListScreen
from ui.receipts.receipt_form_dialog import ReceiptDialog
from ui.error_handler import UIErrorHandler

logger = get_logger(__name__)


class ReceiptsScreen(BaseListScreen):
    """
    Screen for managing customer receipts (money coming in).
    
    This UI component handles:
    - Layout and visual presentation
    - User interactions (clicks, typing)
    - Signal emissions for external communication
    
    Business logic is delegated to ReceiptController.
    """
    
    # Signal emitted when receipt data changes
    receipt_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Receipts (Money In)", parent=parent)
        self.setObjectName("ReceiptsScreen")
        self._controller = receipt_controller
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return the text for the add button."""
        return "+ Add Receipt"
    
    def _get_entity_name(self) -> str:
        """Return the entity name for pagination display."""
        return "receipt"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Creators (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section using StatsContainer."""
        # Create stat cards - for customer receipts (money IN)
        self._total_received_card = StatCard("💰", "Total Received", "₹0", SUCCESS)
        self._total_count_card = StatCard("📋", "Total Receipts", "0", PRIMARY)
        self._month_total_card = StatCard("📅", "This Month", "₹0", WARNING)
        self._customers_card = StatCard("👥", "Customers Paid", "0", SUCCESS)
        
        return StatsContainer([
            self._total_received_card,
            self._total_count_card,
            self._month_total_card,
            self._customers_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget for consistency."""
        self._filter_widget = FilterWidget()
        
        # Search filter
        self._filter_widget.add_search_filter("Search customer receipts...")
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
        
        # Customer/Party filter
        party_options = {"All Customers": "All Customers"}
        self._party_combo = self._filter_widget.add_combo_filter("party", "Customer:", party_options)
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the receipts table."""
        frame = TableFrame()
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "#", "Date", "Customer", "Amount", "Method", 
            "Reference", "Invoice", "Status", "Actions"
        ])
        
        # Column configuration
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},     # #
            {"width": 100, "resize": "fixed"},    # Date
            {"resize": "stretch"},                 # Customer
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
            {'key': 'amount', 'type': 'currency', 'bold': True, 'align': Qt.AlignRight, 'color': SUCCESS},
            {'key': 'mode', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: v or 'Cash'},
            {'key': 'reference', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: v or '-'},
            {'key': 'invoice_id', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: f"INV-{v}" if v else '-'},
        ]
        
        frame.set_table(self._table)
        return frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_all_data(self) -> list:
        """Fetch all receipts from controller.
        
        Returns:
            List of all receipt records
        """
        all_receipts, _ = self._controller.get_filtered_receipts()
        return all_receipts
    
    def filter_data(self, all_data: list) -> list:
        """Filter receipts based on current filter selections.
        
        Args:
            all_data: List of all receipts to filter
            
        Returns:
            Filtered list of receipts
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        method_filter = self._method_combo.currentData() if hasattr(self, '_method_combo') else "All Methods"
        period_filter = self._period_combo.currentData() if hasattr(self, '_period_combo') else "All Time"
        status_filter = self._status_combo.currentData() if hasattr(self, '_status_combo') else "All Status"
        party_filter = self._party_combo.currentData() if hasattr(self, '_party_combo') else "All Customers"
        
        # Update party/customer filter with available parties
        self._update_party_filter()
        
        return self._apply_filters(all_data, search_text, method_filter, period_filter, status_filter, party_filter)
    
    def _apply_filters(self, receipts: list, search_text: str, method_filter: str, 
                       period_filter: str, status_filter: str, party_filter: str) -> list:
        """Apply filters to receipts list - delegates to controller.
        
        Args:
            receipts: List of receipts to filter
            search_text: Search text
            method_filter: Payment method filter value
            period_filter: Period filter value
            status_filter: Status filter value
            party_filter: Party/customer filter value
            
        Returns:
            Filtered list of receipts
        """
        # Use controller's filter with ReceiptFilters dataclass
        filters = ReceiptFilters(
            search_text=search_text,
            method=method_filter,
            period=period_filter,
            status=status_filter
        )
        filtered = self._controller._apply_filters(receipts, filters)
        
        # Apply party filter (additional filter from UI)
        if party_filter and party_filter != "All Customers":
            filtered = [
                r for r in filtered
                if r.get('party_name') == party_filter
            ]
        
        return filtered
    
    def _update_stats(self, all_data: list):
        """Update statistics cards with receipt data.
        
        Args:
            all_data: List of all receipts (unfiltered)
        """
        stats = self._controller._calculate_stats(all_data)
        self._total_received_card.set_value(f"₹{stats.total_received:,.0f}")
        self._total_count_card.set_value(str(stats.total_count))
        self._month_total_card.set_value(f"₹{stats.month_total:,.0f}")
        self._customers_card.set_value(str(stats.customers_count))
    
    def _update_party_filter(self):
        """Update party/customer dropdown with available parties."""
        # Extract unique party names from all receipts
        parties = sorted(set(r.get('party_name', '') for r in self._all_data if r.get('party_name')))
        
        current_selection = self._party_combo.currentData()
        self._party_combo.blockSignals(True)
        self._party_combo.clear()
        self._party_combo.addItem("All Customers", "All Customers")
        
        for party in parties:
            self._party_combo.addItem(party, party)
        
        # Restore selection if still valid
        index = self._party_combo.findData(current_selection)
        if index >= 0:
            self._party_combo.setCurrentIndex(index)
        
        self._party_combo.blockSignals(False)
    
    def _populate_table(self, receipts: list):
        """Populate table with receipt data using ListTableHelper.
        
        Args:
            receipts: List of receipts for current page
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(receipts)} receipts using ListTableHelper")
        
        # Use ListTableHelper to populate basic columns (0-6)
        self._table_helper.populate(
            data=receipts,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Add custom widgets for status (col 7) and action buttons (col 8)
        for row in range(self._table.rowCount()):
            receipt = receipts[row] if row < len(receipts) else None
            if receipt:
                # Column 7: Status badge using helper
                status = receipt.get('status', 'Completed')
                status_widget = self._table_helper.create_status_badge(status)
                self._table.setCellWidget(row, 7, status_widget)
                
                # Column 8: Action buttons using helper
                actions = [
                    {'text': 'View', 'tooltip': 'View Receipt Details', 'bg_color': PRIMARY_LIGHT, 
                     'hover_color': PRIMARY, 'callback': lambda checked, r=receipt: self._on_view_clicked(r)},
                    {'text': 'Edit', 'tooltip': 'Edit Receipt', 'bg_color': WARNING_LIGHT, 
                     'hover_color': WARNING, 'callback': lambda checked, r=receipt: self._on_edit_clicked(r)},
                    {'text': 'Del', 'tooltip': 'Delete Receipt', 'bg_color': DANGER_LIGHT, 
                     'hover_color': DANGER, 'callback': lambda checked, r=receipt: self._on_delete_clicked(r)},
                ]
                actions_widget = self._table_helper.create_action_buttons(actions)
                self._table.setCellWidget(row, 8, actions_widget)
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Screen-specific)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_add_clicked(self):
        """Handle add receipt button click."""
        dialog = ReceiptDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.receipt_updated.emit()
    
    def _on_view_clicked(self, receipt: dict):
        """Handle view button click - show receipt details."""
        invoice_text = f"INV-{receipt.get('invoice_id')}" if receipt.get('invoice_id') else '-'
        notes = (receipt.get('notes', '') or '').replace('[RECEIPT]', '').strip() or '-'
        
        details = f"""
<h3>💰 Customer Receipt Details</h3>

<p><b>Customer:</b> {receipt.get('party_name', 'N/A')}</p>
<p><b>Amount:</b> ₹{receipt.get('amount', 0):,.2f}</p>
<p><b>Date:</b> {receipt.get('date', 'N/A')}</p>
<p><b>Method:</b> {receipt.get('mode', 'N/A')}</p>
<p><b>Reference:</b> {receipt.get('reference', 'N/A') or '-'}</p>
<p><b>Invoice:</b> {invoice_text}</p>
<p><b>Status:</b> {receipt.get('status', 'N/A')}</p>
<p><b>Notes:</b> {notes}</p>
        """
        QMessageBox.information(self, "Receipt Details", details.strip())
    
    def _on_edit_clicked(self, receipt: dict):
        """Handle edit button click."""
        dialog = ReceiptDialog(parent=self, receipt_data=receipt)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.receipt_updated.emit()
    
    def _on_delete_clicked(self, receipt: dict):
        """Handle delete button click with confirmation."""
        party_name = receipt.get('party_name', 'Unknown')
        amount = float(receipt.get('amount') or 0)
        receipt_id = receipt.get('id')
        date = receipt.get('date', '')
        
        # Show confirmation dialog
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete this customer receipt?\n\n"
            f"Customer: {party_name}\n"
            f"Amount: ₹{amount:,.2f}\n"
            f"Date: {date}\n\n"
            f"This action cannot be undone."
        ):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_receipt(receipt_id)
        
        if success:
            UIErrorHandler.show_success("Success", "✓ Receipt deleted successfully!")
            self._load_data()
            self.receipt_updated.emit()
        else:
            UIErrorHandler.show_error("Error", message)
    