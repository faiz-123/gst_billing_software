"""
Receipts List Screen - Customer Receipts (Money IN)
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB

✅ Uses ListHeader
✅ Uses StatsContainer
✅ Uses FilterWidget
✅ Uses PaginationWidget
✅ Proper _load_receipts(reset_page=False) pattern
✅ _is_loading guard
✅ Stats from ALL data, not filtered
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
    get_normal_font, get_bold_font
)

# Widget imports
from widgets import StatCard, ListTable, TableFrame, TableActionButton, ListHeader, StatsContainer, FilterWidget
from ui.base import PaginationWidget

# Controller import (NOT service directly)
from controllers.receipt_controller import receipt_controller, ReceiptFilters

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base import BaseScreen
from ui.receipts.receipt_form_dialog import ReceiptDialog
from ui.error_handler import UIErrorHandler

logger = get_logger(__name__)


class ReceiptsScreen(BaseScreen):
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
    
    # Pagination constant
    ITEMS_PER_PAGE = 49
    
    def __init__(self, parent=None):
        super().__init__(title="Receipts (Money In)", parent=parent)
        self.setObjectName("ReceiptsScreen")
        self._controller = receipt_controller
        self._all_receipts = []
        self._filtered_receipts = []
        self._is_loading = False
        self.pagination_widget = None
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
        self.main_layout.addWidget(self._create_pagination_controls())
    
    def _create_header(self) -> QWidget:
        """Create header with title and add button using ListHeader."""
        header = ListHeader("💰 Receipts (Money In)", "+ Add Receipt")
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
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
        self._filter_widget.add_refresh_button(lambda: self._load_data())
        
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
        
        frame.set_table(self._table)
        return frame
    
    def _create_pagination_controls(self) -> QWidget:
        """Create pagination controls using PaginationWidget."""
        self.pagination_widget = PaginationWidget(
            items_per_page=self.ITEMS_PER_PAGE,
            entity_name="receipt",
            parent=self
        )
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        return self.pagination_widget
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self, reset_page: bool = False):
        """Load receipts from controller and update UI with proper loading state.
        
        Args:
            reset_page: Reset to first page when called after filter change
        """
        # 1. Check if already loading (prevent concurrent calls)
        if self._is_loading:
            logger.debug("Load already in progress, skipping")
            return
        
        try:
            self._is_loading = True
            logger.debug("Loading receipts from database")
            
            # 2. Fetch all data from service → self._all_receipts
            all_receipts, _ = self._controller.get_filtered_receipts()  # Get all without filters
            self._all_receipts = all_receipts
            logger.info(f"🔄 Fetched {len(self._all_receipts)} TOTAL receipts from database")
            
            if len(self._all_receipts) == 0:
                logger.warning("⚠️  No receipts returned from database!")
            
            # 3. Apply filters → self._filtered_receipts
            filters = self._get_current_filters()
            self._filtered_receipts = self._controller._apply_filters(self._all_receipts, filters)
            
            # Apply party filter (additional filter from UI)
            party_filter = self._get_party_filter()
            if party_filter and party_filter != "All Customers":
                self._filtered_receipts = [
                    r for r in self._filtered_receipts
                    if r.get('party_name') == party_filter
                ]
            
            logger.debug(f"🔍 After filtering: {len(self._filtered_receipts)} receipts (from {len(self._all_receipts)} total)")
            
            # Update party/customer filter with available parties
            self._update_party_filter()
            
            # 4. Update pagination state (reset page if needed, otherwise preserve)
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            
            total_pages = (len(self._filtered_receipts) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            if total_pages == 0:
                total_pages = 1
            current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
            
            if self.pagination_widget:
                self.pagination_widget.set_pagination_state(current_page, total_pages, len(self._filtered_receipts))
                logger.debug(f"📄 Pagination: Page {current_page}/{total_pages}, Total items: {len(self._filtered_receipts)}")
            
            # 5. Update stats (with ALL data, not filtered)
            logger.info(f"📊 STATS: Showing stats for {len(self._all_receipts)} TOTAL receipts")
            stats = self._controller._calculate_stats(self._all_receipts)
            self._update_stats_display(stats)
            
            # 6. Get current page data and 7. Populate table with page data
            page_data = self._get_current_page_data()
            logger.debug(f"📄 Populating table with {len(page_data)} receipts on page {current_page}")
            self._populate_table(page_data)
            
            logger.info(f"Receipt list loaded successfully. Total: {len(self._all_receipts)}, Filtered: {len(self._filtered_receipts)}")
            
        # 8. Handle errors gracefully
        except Exception as e:
            logger.error(f"Error loading receipts: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to load receipts: {str(e)}")
        # 9. Finally block: set _is_loading = False
        finally:
            self._is_loading = False
    
    def _update_party_filter(self):
        """Update party/customer dropdown with available parties."""
        # Extract unique party names from all receipts
        parties = sorted(set(r.get('party_name', '') for r in self._all_receipts if r.get('party_name')))
        
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
    
    def _get_search_text(self) -> str:
        """Get current search text safely."""
        if hasattr(self, '_filter_widget'):
            return self._filter_widget.get_search_text().strip()
        return ""
    
    def _get_method_filter(self) -> str:
        """Get current method filter value."""
        if hasattr(self, '_method_combo'):
            return self._method_combo.currentData() or "All Methods"
        return "All Methods"
    
    def _get_period_filter(self) -> str:
        """Get current period filter value."""
        if hasattr(self, '_period_combo'):
            return self._period_combo.currentData() or "All Time"
        return "All Time"
    
    def _get_status_filter(self) -> str:
        """Get current status filter value."""
        if hasattr(self, '_status_combo'):
            return self._status_combo.currentData() or "All Status"
        return "All Status"
    
    def _get_party_filter(self) -> str:
        """Get current party filter value."""
        if hasattr(self, '_party_combo'):
            return self._party_combo.currentData() or "All Customers"
        return "All Customers"
    
    def _get_current_filters(self) -> ReceiptFilters:
        """Get current filter values from UI controls."""
        return ReceiptFilters(
            search_text=self._get_search_text(),
            method=self._get_method_filter(),
            period=self._get_period_filter(),
            status=self._get_status_filter()
        )
    
    def _update_stats_display(self, stats):
        """Update statistics cards with data from controller."""
        self._total_received_card.set_value(f"₹{stats.total_received:,.0f}")
        self._total_count_card.set_value(str(stats.total_count))
        self._month_total_card.set_value(f"₹{stats.month_total:,.0f}")
        self._customers_card.set_value(str(stats.customers_count))
    
    def _get_current_page_data(self) -> list:
        """Get receipts for the current page based on pagination state."""
        if not self.pagination_widget:
            return self._filtered_receipts
        
        current_page = self.pagination_widget.get_current_page()
        start_idx = (current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        return self._filtered_receipts[start_idx:end_idx]
    
    def _populate_table(self, receipts: list):
        """Populate table with receipt data."""
        self._table.setRowCount(0)
        
        # Get current page for row numbering offset
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        for page_idx, receipt in enumerate(receipts):
            # Calculate absolute row number accounting for pagination
            absolute_row_num = (current_page - 1) * self.ITEMS_PER_PAGE + page_idx + 1
            self._add_table_row(absolute_row_num, receipt)
    
    def _add_table_row(self, absolute_row_num: int, receipt: dict):
        """Add a single row to the table.
        
        Args:
            absolute_row_num: The absolute row number (accounting for pagination)
            receipt: The receipt data dictionary
        """
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Row number (absolute, accounting for pagination)
        num_item = QTableWidgetItem(str(absolute_row_num))
        num_item.setTextAlignment(Qt.AlignCenter)
        num_item.setForeground(QColor(TEXT_SECONDARY))
        self._table.setItem(row, 0, num_item)
        
        # Column 1: Date
        date_item = QTableWidgetItem(str(receipt.get('date', '')))
        date_item.setTextAlignment(Qt.AlignCenter)
        date_item.setData(Qt.UserRole, receipt.get('id'))  # Store ID
        self._table.setItem(row, 1, date_item)
        
        # Column 2: Customer name
        customer_item = QTableWidgetItem(str(receipt.get('party_name', 'N/A')))
        customer_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        self._table.setItem(row, 2, customer_item)
        
        # Column 3: Amount (green for money IN)
        amount = float(receipt.get('amount') or 0)
        amount_item = QTableWidgetItem(f"₹{amount:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        amount_item.setForeground(QColor(SUCCESS))  # Green for money IN
        self._table.setItem(row, 3, amount_item)
        
        # Column 4: Method
        method_item = QTableWidgetItem(str(receipt.get('mode', 'Cash')))
        method_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 4, method_item)
        
        # Column 5: Reference
        reference_item = QTableWidgetItem(str(receipt.get('reference', '') or '-'))
        reference_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 5, reference_item)
        
        # Column 6: Invoice (linked sales invoice)
        invoice_id = receipt.get('invoice_id')
        invoice_text = f"INV-{invoice_id}" if invoice_id else "-"
        invoice_item = QTableWidgetItem(invoice_text)
        invoice_item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, 6, invoice_item)
        
        # Column 7: Status with color
        status = receipt.get('status', 'Completed')
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
        
        self._table.setItem(row, 7, status_item)
        
        # Column 8: Action buttons
        actions_widget = self._create_action_buttons(receipt)
        self._table.setCellWidget(row, 8, actions_widget)
    
    def _create_action_buttons(self, receipt: dict) -> QWidget:
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
            tooltip="View Receipt Details",
            bg_color="#EEF2FF",
            hover_color=PRIMARY
        )
        view_btn.clicked.connect(lambda checked, r=receipt: self._on_view_clicked(r))
        layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = TableActionButton(
            text="Edit",
            tooltip="Edit Receipt",
            bg_color="#FEF3C7",
            hover_color=WARNING
        )
        edit_btn.clicked.connect(lambda checked, r=receipt: self._on_edit_clicked(r))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = TableActionButton(
            text="Del",
            tooltip="Delete Receipt",
            bg_color="#FEE2E2",
            hover_color=DANGER
        )
        delete_btn.clicked.connect(lambda checked, r=receipt: self._on_delete_clicked(r))
        layout.addWidget(delete_btn)
        
        return widget

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Slots)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self._load_data(reset_page=True)
    
    def _on_filter_changed(self, index: int = None):
        """Handle filter combo change."""
        self._load_data(reset_page=True)
    
    def _on_pagination_page_changed(self, page: int):
        """Handle page change from pagination widget.
        
        Args:
            page: The new page number
        """
        try:
            logger.info(f"Pagination page changed to {page}")
            page_data = self._get_current_page_data()
            self._populate_table(page_data)
        except Exception as e:
            logger.error(f"Error handling pagination page change: {str(e)}", exc_info=True)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_data()
    
    def _on_clear_filters(self):
        """Handle clear filters button click."""
        if hasattr(self, '_filter_widget'):
            self._filter_widget.reset_filters()
            self._filter_widget.clear_search()
        self._load_data(reset_page=True)
    
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
    
    def _on_export_clicked(self):
        """Handle export button click."""
        UIErrorHandler.show_warning(
            "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export receipt data to CSV or Excel."
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh the receipts list."""
        self._load_data()
