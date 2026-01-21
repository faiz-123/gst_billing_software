"""
Sales Invoice List Screen
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import QWidget, QDialog, QTableWidgetItem
from PySide6.QtCore import Qt, Signal

# Theme imports
from theme import PRIMARY, SUCCESS, DANGER, WARNING, WARNING_LIGHT, SUCCESS_LIGHT, DANGER_LIGHT, PRIMARY_LIGHT

# Widget imports
from widgets import StatCard, ListTable, TableFrame, TableActionButton, ListHeader, StatsContainer, FilterWidget
from ui.base.list_table_helper import ListTableHelper

# Controller import (NOT service or db directly)
from controllers.invoice_controller import invoice_controller

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base.base_list_screen import BaseListScreen
from ui.error_handler import UIErrorHandler
from ui.invoices.sales.sales_invoice_form_dialog import InvoiceDialog

logger = get_logger(__name__)


class InvoicesScreen(BaseListScreen):
    """
    Main screen for managing sales invoices.
    
    This UI component handles:
    - Layout and visual presentation
    - User interactions (clicks, typing)
    - Signal emissions for external communication
    
    Business logic is delegated to InvoiceController.
    """
    
    # Signal emitted when invoice data changes
    invoice_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Sales Invoices", parent=parent)
        self.setObjectName("InvoicesScreen")
        self._controller = invoice_controller
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return the text for the add button."""
        return "+ New Invoice"
    
    def _get_entity_name(self) -> str:
        """Return the entity name for pagination display."""
        return "invoice"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Creators (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section using StatsContainer."""
        # Create stat cards
        self._total_card = StatCard("📋", "Total Invoices", "0", PRIMARY)
        self._amount_card = StatCard("💰", "Total Revenue", "₹0", SUCCESS)
        self._overdue_card = StatCard("⏰", "Overdue", "0", DANGER)
        self._paid_card = StatCard("✅", "Paid", "0", "#10B981")
        
        return StatsContainer([
            self._total_card,
            self._amount_card,
            self._overdue_card,
            self._paid_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget for consistency."""
        self._filter_widget = FilterWidget()
        
        # Search filter
        search_input = self._filter_widget.add_search_filter("Search invoices...")
        self._filter_widget.search_changed.connect(self._on_search_changed)
        
        # Status filter
        status_options = {
            "All": "All",
            "Unpaid": "Unpaid",
            "Partially Paid": "Partially Paid",
            "Paid": "Paid",
            "Overdue": "Overdue",
            "Cancelled": "Cancelled"
        }
        self._status_combo = self._filter_widget.add_combo_filter("status", "Status:", status_options)
        
        # Period filter
        period_options = {
            "All Time": "All Time",
            "Today": "Today",
            "This Week": "This Week",
            "This Month": "This Month",
            "This Year": "This Year"
        }
        self._period_combo = self._filter_widget.add_combo_filter("period", "Period:", period_options)
        
        # Amount filter
        amount_options = {
            "All Amounts": "All Amounts",
            "Under ₹10K": "Under ₹10K",
            "₹10K - ₹50K": "₹10K - ₹50K",
            "₹50K - ₹1L": "₹50K - ₹1L",
            "Above ₹1L": "Above ₹1L"
        }
        self._amount_combo = self._filter_widget.add_combo_filter("amount", "Amount:", amount_options)
        
        # Party filter
        party_options = {"All Parties": "All Parties"}
        self._party_combo = self._filter_widget.add_combo_filter("party", "Party:", party_options)
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the invoices table."""
        frame = TableFrame()
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "#", "Invoice No.", "Date", "Party", "Amount", "Status", "Actions"
        ])
        
        # Enable double-click to view
        self._table.itemDoubleClicked.connect(self._on_row_double_clicked)
        
        # Column configuration
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},     # #
            {"width": 120, "resize": "fixed"},    # Invoice No.
            {"width": 100, "resize": "fixed"},    # Date
            {"resize": "stretch"},                 # Party
            {"width": 120, "resize": "fixed"},    # Amount
            {"width": 100, "resize": "fixed"},    # Status
            {"width": 150, "resize": "fixed"},    # Actions
        ])
        
        # Initialize ListTableHelper for populating the table
        self._table_helper = ListTableHelper(self._table, self.ITEMS_PER_PAGE)
        
        # Define column configurations for table population (columns 0-4 only, 5-6 are custom)
        self._column_configs = [
            {'type': 'row_number'},
            {'key': 'invoice_no', 'type': 'text', 'bold': True, 'color': PRIMARY,
             'formatter': lambda v: v if v else f"INV-000"},
            {'key': 'date', 'type': 'date', 'formatter': lambda v: str(v) if v else ''},
            {'key': 'party_name', 'type': 'text', 'formatter': lambda v: v or 'Unknown'},
            {'key': 'grand_total', 'type': 'currency', 'bold': True, 'align': Qt.AlignRight},
        ]
        
        frame.set_table(self._table)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_all_data(self) -> list:
        """Fetch all invoices from controller.
        
        Returns:
            List of all invoice records
        """
        return self._controller.get_all_invoices()
    
    def filter_data(self, all_data: list) -> list:
        """Apply filters to invoices list
        
        Args:
            all_data: List of all invoices
            
        Returns:
            Filtered list of invoices
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        status_filter = self._status_combo.currentData() if hasattr(self, '_status_combo') else "All"
        period_filter = self._period_combo.currentData() if hasattr(self, '_period_combo') else "All Time"
        amount_filter = self._amount_combo.currentData() if hasattr(self, '_amount_combo') else "All Amounts"
        party_filter = self._party_combo.currentData() if hasattr(self, '_party_combo') else "All Parties"
        
        # Update party filter with available parties
        self._update_party_filter()
        
        return self._apply_filters(all_data, search_text, status_filter, period_filter, amount_filter, party_filter)
    
    def _apply_filters(self, invoices: list, search_text: str, status_filter: str, 
                       period_filter: str, amount_filter: str, party_filter: str) -> list:
        """Apply filters to invoices list with validation
        
        Args:
            invoices: List of invoices to filter
            search_text: Search text (invoice no, party name)
            status_filter: Status filter (Paid, Unpaid, etc.)
            period_filter: Period filter (Today, This Week, etc.)
            amount_filter: Amount range filter
            party_filter: Party name filter
            
        Returns:
            Filtered list of invoices
        """
        # Delegate to controller for actual filtering logic
        return self._controller.filter_invoices(
            invoices=invoices,
            search_text=search_text,
            status_filter=status_filter,
            period_filter=period_filter,
            amount_filter=amount_filter,
            party_filter=party_filter
        )
    
    def _update_stats(self, all_data: list):
        """Update statistics cards with invoice data.
        
        Args:
            all_data: List of all invoices (unfiltered)
        """
        stats = self._controller.calculate_stats(all_data)
        self._total_card.set_value(str(stats.total))
        self._amount_card.set_value(f"₹{stats.total_amount:,.0f}")
        self._overdue_card.set_value(str(stats.overdue_count))
        self._paid_card.set_value(str(stats.paid_count))
    
    def _update_party_filter(self):
        """Update party dropdown with available parties."""
        parties = self._controller.extract_party_names(self._all_data)
        
        current_selection = self._party_combo.currentData()
        self._party_combo.blockSignals(True)
        self._party_combo.clear()
        self._party_combo.addItem("All Parties", "All Parties")
        
        for party in parties:
            self._party_combo.addItem(party, party)
        
        # Restore selection if still valid
        index = self._party_combo.findData(current_selection)
        if index >= 0:
            self._party_combo.setCurrentIndex(index)
        
        self._party_combo.blockSignals(False)
    
    def _populate_table(self, invoices: list):
        """Populate table with invoice data using ListTableHelper.
        
        Args:
            invoices: List of invoices for current page
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(invoices)} invoices using ListTableHelper")
        
        # Use ListTableHelper to populate basic columns (0-4)
        self._table_helper.populate(
            data=invoices,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Custom status color map for invoices
        invoice_status_colors = {
            'Paid': (SUCCESS, SUCCESS_LIGHT),
            'Unpaid': (WARNING, WARNING_LIGHT),
            'Partially Paid': (PRIMARY, PRIMARY_LIGHT),
            'Overdue': (DANGER, DANGER_LIGHT),
            'Cancelled': (DANGER, DANGER_LIGHT),
        }
        
        # Add custom widgets for status (col 5) and action buttons (col 6)
        for row in range(self._table.rowCount()):
            invoice = invoices[row] if row < len(invoices) else None
            if invoice:
                # Column 5: Status badge using helper
                status = invoice.get('status', 'Unpaid')
                status_widget = self._table_helper.create_status_badge(status, invoice_status_colors)
                self._table.setCellWidget(row, 5, status_widget)
                
                # Column 6: Action buttons using helper
                actions = [
                    {'text': 'View', 'tooltip': 'View Invoice', 'bg_color': PRIMARY_LIGHT, 
                     'hover_color': PRIMARY, 'size': (60, 32),
                     'callback': lambda checked, inv=invoice: self._on_view_clicked(inv)},
                    {'text': 'Del', 'tooltip': 'Delete Invoice', 'bg_color': DANGER_LIGHT, 
                     'hover_color': DANGER, 'size': (50, 32),
                     'callback': lambda checked, inv=invoice: self._on_delete_clicked(inv)},
                ]
                actions_widget = self._table_helper.create_action_buttons(actions)
                self._table.setCellWidget(row, 6, actions_widget)
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Screen-specific)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_add_clicked(self):
        """Handle add invoice button click."""
        dialog = InvoiceDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.invoice_updated.emit()
    
    def _on_row_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on table row."""
        row = item.row()
        # Calculate actual index in filtered data based on current page
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        actual_idx = (current_page - 1) * self.ITEMS_PER_PAGE + row
        
        if actual_idx < len(self._filtered_data):
            self._open_invoice_readonly(self._filtered_data[actual_idx])
    
    def _on_view_clicked(self, invoice: dict):
        """Handle view button click - show print preview."""
        try:
            invoice_id = invoice.get('id')
            if not invoice_id:
                UIErrorHandler.show_error("Error", "Invalid invoice data")
                return
            
            # Show print preview
            from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
            show_invoice_preview(self, invoice_id)
            
        except Exception as e:
            UIErrorHandler.show_error("Error", f"Failed to view invoice: {str(e)}")
    
    def _on_delete_clicked(self, invoice: dict):
        """Handle delete button click with confirmation."""
        invoice_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        invoice_id = invoice.get('id')
        
        # Show confirmation dialog
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete '{invoice_no}'?\n\nThis action cannot be undone."
        ):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_invoice(invoice_id)
        
        if success:
            UIErrorHandler.show_success("Success", f"Invoice '{invoice_no}' deleted successfully!")
            self._load_data()
            self.invoice_updated.emit()
        else:
            UIErrorHandler.show_error("Error", message)
    
    def _open_invoice_readonly(self, invoice: dict):
        """Open invoice dialog in read-only mode for viewing."""
        try:
            invoice_id = invoice.get('id')
            if not invoice_id:
                UIErrorHandler.show_error("Error", "Invalid invoice data")
                return
            
            # Get full invoice data via controller
            invoice_data = self._controller.get_invoice_with_items(invoice_id)
            
            if not invoice_data:
                UIErrorHandler.show_error("Error", f"Could not load invoice data for ID: {invoice_id}")
                return
            # Open InvoiceDialog in read-only mode
            dialog = InvoiceDialog(self, invoice_data=invoice_data, read_only=True)
            dialog.exec()
            
        except Exception as e:
            UIErrorHandler.show_error("Error", f"Failed to open invoice: {str(e)}")
    
