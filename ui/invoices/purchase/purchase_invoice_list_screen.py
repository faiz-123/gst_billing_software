"""
Purchase Invoice List Screen
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import QWidget, QDialog, QTableWidgetItem
from PySide6.QtCore import Qt, Signal

# Theme imports
from theme import (
    PRIMARY, SUCCESS, DANGER, WARNING, WARNING_LIGHT, SUCCESS_LIGHT, DANGER_LIGHT, PRIMARY_LIGHT,
    PURCHASE_PRIMARY, PURCHASE_PRIMARY_HOVER, PURCHASE_BG_LIGHT, PURCHASE_BORDER_ACCENT
)

# Widget imports
from widgets import StatCard, ListTable, TableFrame, StatsContainer, FilterWidget
from ui.base.list_table_helper import ListTableHelper

# Controller import (NOT service or db directly)
from controllers.purchase_controller import purchase_controller

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base.base_list_screen import BaseListScreen
from ui.error_handler import UIErrorHandler
from ui.invoices.purchase.purchase_invoice_form_dialog import PurchaseInvoiceDialog

logger = get_logger(__name__)


class PurchasesScreen(BaseListScreen):
    """
    Main screen for managing purchase invoices.
    
    This UI component handles:
    - Layout and visual presentation
    - User interactions (clicks, typing)
    - Signal emissions for external communication
    
    Business logic is delegated to PurchaseController.
    """
    
    # Signal emitted when purchase data changes
    purchase_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Purchase Invoices", parent=parent)
        self.setObjectName("PurchasesScreen")
        self._controller = purchase_controller
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return the text for the add button."""
        return "+ New Purchase"
    
    def _get_entity_name(self) -> str:
        """Return the entity name for pagination display."""
        return "purchase"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Creators (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
        
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section using StatsContainer."""
        # Create stat cards (amber/orange theme for purchases)
        self._total_card = StatCard("📋", "Total Purchases", "0", PURCHASE_PRIMARY)
        self._amount_card = StatCard("💸", "Total Expense", "₹0", DANGER)
        self._unpaid_card = StatCard("⏰", "Unpaid", "0", "#6366F1")
        self._paid_card = StatCard("✅", "Paid", "0", SUCCESS)
        
        return StatsContainer([
            self._total_card,
            self._amount_card,
            self._unpaid_card,
            self._paid_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget for consistency."""
        self._filter_widget = FilterWidget()
        
        # Search filter
        search_input = self._filter_widget.add_search_filter("Search purchases...")
        self._filter_widget.search_changed.connect(self._on_search_changed)
        
        # Status filter
        status_options = {
            "All": "All",
            "Unpaid": "Unpaid",
            "Partially Paid": "Partially Paid",
            "Paid": "Paid",
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
        
        # Supplier filter
        supplier_options = {"All Suppliers": "All Suppliers"}
        self._supplier_combo = self._filter_widget.add_combo_filter("supplier", "Supplier:", supplier_options)
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the purchases table."""
        frame = TableFrame()
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "#", "Invoice No.", "Date", "Supplier", "Amount", "Status", "Actions"
        ])
        
        # Enable double-click to view
        self._table.itemDoubleClicked.connect(self._on_row_double_clicked)
        
        # Column configuration
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},     # #
            {"width": 120, "resize": "fixed"},    # Invoice No.
            {"width": 100, "resize": "fixed"},    # Date
            {"resize": "stretch"},                 # Supplier
            {"width": 120, "resize": "fixed"},    # Amount
            {"width": 100, "resize": "fixed"},    # Status
            {"width": 150, "resize": "fixed"},    # Actions
        ])
        
        # Initialize ListTableHelper for populating the table
        self._table_helper = ListTableHelper(self._table, self.ITEMS_PER_PAGE)
        
        # Define column configurations for table population (columns 0-4 only, 5-6 are custom)
        self._column_configs = [
            {'type': 'row_number'},
            {'key': 'invoice_no', 'type': 'text', 'bold': True, 'color': PURCHASE_PRIMARY,
             'formatter': lambda v: v if v else f"PUR-000"},
            {'key': 'date', 'type': 'date', 'formatter': lambda v: str(v) if v else ''},
            {'key': 'party_name', 'type': 'text', 'formatter': lambda v: v or 'Unknown Supplier'},
            {'key': 'grand_total', 'type': 'currency', 'bold': True, 'align': Qt.AlignRight},
        ]
        
        frame.set_table(self._table)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods (required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_all_data(self) -> list:
        """Fetch all purchases from controller.
        
        Returns:
            List of all purchase records
        """
        return self._controller.get_all_purchases()
    
    def filter_data(self, all_data: list) -> list:
        """Filter purchases based on current filter selections.
        
        Args:
            all_data: List of all purchases to filter
            
        Returns:
            Filtered list of purchases
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        status_filter = self._status_combo.currentData() if hasattr(self, '_status_combo') else "All"
        period_filter = self._period_combo.currentData() if hasattr(self, '_period_combo') else "All Time"
        amount_filter = self._amount_combo.currentData() if hasattr(self, '_amount_combo') else "All Amounts"
        supplier_filter = self._supplier_combo.currentData() if hasattr(self, '_supplier_combo') else "All Suppliers"
        
        # Update supplier filter with available suppliers
        self._update_supplier_filter()
        
        return self._apply_filters(all_data, search_text, status_filter, period_filter, amount_filter, supplier_filter)
    
    def _apply_filters(self, purchases: list, search_text: str, status_filter: str, 
                       period_filter: str, amount_filter: str, supplier_filter: str) -> list:
        """Apply filters to purchases list - delegates to controller.
        
        Args:
            purchases: List of purchases to filter
            search_text: Search text
            status_filter: Status filter value
            period_filter: Period filter value
            amount_filter: Amount filter value
            supplier_filter: Supplier filter value
            
        Returns:
            Filtered list of purchases
        """
        return self._controller.filter_purchases(
            purchases=purchases,
            search_text=search_text,
            status_filter=status_filter,
            period_filter=period_filter,
            amount_filter=amount_filter,
            supplier_filter=supplier_filter
        )
    
    def _update_stats(self, all_data: list):
        """Update statistics cards with purchase data.
        
        Args:
            all_data: List of all purchases (unfiltered)
        """
        stats = self._controller.calculate_stats(all_data)
        self._total_card.set_value(str(stats.total))
        self._amount_card.set_value(f"₹{stats.total_amount:,.0f}")
        self._unpaid_card.set_value(str(stats.unpaid_count))
        self._paid_card.set_value(str(stats.paid_count))
    
    def _update_supplier_filter(self):
        """Update supplier dropdown with available suppliers."""
        suppliers = self._controller.extract_supplier_names(self._all_data)
        
        current_selection = self._supplier_combo.currentData()
        self._supplier_combo.blockSignals(True)
        self._supplier_combo.clear()
        self._supplier_combo.addItem("All Suppliers", "All Suppliers")
        
        for supplier in suppliers:
            self._supplier_combo.addItem(supplier, supplier)
        
        # Restore selection if still valid
        index = self._supplier_combo.findData(current_selection)
        if index >= 0:
            self._supplier_combo.setCurrentIndex(index)
        
        self._supplier_combo.blockSignals(False)
    
    def _populate_table(self, purchases: list):
        """Populate table with purchase data using ListTableHelper.
        
        Args:
            purchases: List of purchases for current page
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(purchases)} purchases using ListTableHelper")
        
        # Use ListTableHelper to populate basic columns (0-4)
        self._table_helper.populate(
            data=purchases,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Custom status color map for purchases
        purchase_status_colors = {
            'Paid': (SUCCESS, SUCCESS_LIGHT),
            'Unpaid': (WARNING, WARNING_LIGHT),
            'Partially Paid': (PRIMARY, PRIMARY_LIGHT),
            'Cancelled': (DANGER, DANGER_LIGHT),
        }
        
        # Add custom widgets for status (col 5) and action buttons (col 6)
        for row in range(self._table.rowCount()):
            purchase = purchases[row] if row < len(purchases) else None
            if purchase:
                # Column 5: Status badge using helper
                status = purchase.get('status', 'Unpaid')
                status_widget = self._table_helper.create_status_badge(status, purchase_status_colors)
                self._table.setCellWidget(row, 5, status_widget)
                
                # Column 6: Action buttons using helper
                actions = [
                    {'text': 'View', 'tooltip': 'View Purchase', 'bg_color': WARNING_LIGHT, 
                     'hover_color': PURCHASE_PRIMARY, 'size': (60, 32),
                     'callback': lambda checked, pur=purchase: self._on_view_clicked(pur)},
                    {'text': 'Del', 'tooltip': 'Delete Purchase', 'bg_color': DANGER_LIGHT, 
                     'hover_color': DANGER, 'size': (50, 32),
                     'callback': lambda checked, pur=purchase: self._on_delete_clicked(pur)},
                ]
                actions_widget = self._table_helper.create_action_buttons(actions)
                self._table.setCellWidget(row, 6, actions_widget)
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Screen-specific)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_add_clicked(self):
        """Handle add purchase button click."""
        dialog = PurchaseInvoiceDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.purchase_updated.emit()

    def _on_row_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on table row."""
        row = item.row()
        # Calculate actual index in filtered data based on current page
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        actual_idx = (current_page - 1) * self.ITEMS_PER_PAGE + row
        
        if actual_idx < len(self._filtered_data):
            self._open_purchase_readonly(self._filtered_data[actual_idx])
    
    def _on_view_clicked(self, purchase: dict):
        """Handle view button click - show print preview."""
        try:
            purchase_id = purchase.get('id')
            if not purchase_id:
                UIErrorHandler.show_error("Error", "Invalid purchase data")
                return
            
            # Show print preview
            from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
            show_invoice_preview(self, purchase_id)
            
        except Exception as e:
            logger.error(f"Failed to view purchase: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to view purchase: {str(e)}")
    
    def _on_delete_clicked(self, purchase: dict):
        """Handle delete button click with confirmation."""
        invoice_no = purchase.get('invoice_no', f"PUR-{purchase.get('id', 0):03d}")
        purchase_id = purchase.get('id')
        
        # Show confirmation dialog
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete '{invoice_no}'?\n\nThis action cannot be undone."
        ):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_purchase(purchase_id)
        
        if success:
            UIErrorHandler.show_success("Success", f"Purchase invoice '{invoice_no}' deleted successfully!")
            self._load_data()
            self.purchase_updated.emit()
        else:
            UIErrorHandler.show_error("Error", message)
    
    def _open_purchase_readonly(self, purchase: dict):
        """Open purchase dialog in read-only mode for viewing."""
        try:
            purchase_id = purchase.get('id')
            if not purchase_id:
                UIErrorHandler.show_error("Error", "Invalid purchase data")
                return
            
            # Get full purchase data via controller
            purchase_data = self._controller.get_purchase_with_items(purchase_id)
            
            if not purchase_data:
                UIErrorHandler.show_error("Error", f"Could not load purchase data for ID: {purchase_id}")
                return
            
            # Open PurchaseInvoiceDialog in read-only mode
            dialog = PurchaseInvoiceDialog(self, invoice_data=purchase_data, read_only=True)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Failed to open purchase: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to open purchase: {str(e)}")
    
