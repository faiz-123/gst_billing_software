"""
Purchase Invoice List Screen
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
    SUCCESS, DANGER, WHITE, BACKGROUND,
    get_normal_font, get_bold_font,
    FONT_SIZE_SMALL
)

# Widget imports
from widgets import StatCard, ListTable, TableFrame, TableActionButton, ListHeader, StatsContainer, FilterWidget
from ui.base import PaginationWidget

# Controller import (NOT service or db directly)
from controllers.purchase_controller import purchase_controller

# Core imports for formatting only
from core.core_utils import format_currency
from core.logger import get_logger

# UI imports
from ui.base import BaseScreen
from ui.error_handler import UIErrorHandler
from ui.invoices.purchase.purchase_invoice_form_dialog import PurchaseInvoiceDialog

logger = get_logger(__name__)

# Purchase-specific colors (amber/orange theme)
PURCHASE_PRIMARY = "#F59E0B"  # Amber
PURCHASE_PRIMARY_HOVER = "#D97706"  # Darker amber
PURCHASE_BG_LIGHT = "#FFFBEB"  # Light amber background
PURCHASE_BORDER_ACCENT = "#FCD34D"  # Amber border


class PurchasesScreen(BaseScreen):
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
    
    # Pagination constant
    ITEMS_PER_PAGE = 49
    
    def __init__(self, parent=None):
        super().__init__(title="Purchase Invoices", parent=parent)
        self.setObjectName("PurchasesScreen")
        self._controller = purchase_controller
        self._all_purchases = []
        self._filtered_purchases = []
        self._is_loading = False
        self.pagination_widget = None
        self._setup_ui()
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
        header = ListHeader("🛒 Purchase Invoices", "+ New Purchase")
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
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
        self._filter_widget.add_refresh_button(lambda: self._load_data())
        
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
        
        frame.set_table(self._table)
        return frame

    def _create_pagination_controls(self) -> QWidget:
        """Create pagination controls using PaginationWidget."""
        self.pagination_widget = PaginationWidget(
            items_per_page=self.ITEMS_PER_PAGE,
            entity_name="purchase",
            parent=self
        )
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        return self.pagination_widget

    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self, reset_page: bool = False):
        """Load purchases from controller and update UI with proper loading state.
        
        Args:
            reset_page: Reset to first page when called after filter change
        """
        # 1. Check if already loading (prevent concurrent calls)
        if self._is_loading:
            logger.debug("Load already in progress, skipping")
            return
        
        try:
            self._is_loading = True
            logger.debug("Loading purchases from database")
            
            # 2. Fetch all data from service → self._all_purchases
            self._all_purchases = self._controller.get_all_purchases()
            logger.info(f"🔄 Fetched {len(self._all_purchases)} TOTAL purchases from database")
            
            if len(self._all_purchases) == 0:
                logger.warning("⚠️  No purchases returned from database!")
            
            # 3. Apply filters → self._filtered_purchases
            search_text = self._get_search_text()
            status_filter = self._get_status_filter()
            period_filter = self._get_period_filter()
            amount_filter = self._get_amount_filter()
            supplier_filter = self._get_supplier_filter()
            
            self._filtered_purchases = self._controller.filter_purchases(
                purchases=self._all_purchases,
                search_text=search_text,
                status_filter=status_filter,
                period_filter=period_filter,
                amount_filter=amount_filter,
                supplier_filter=supplier_filter
            )
            logger.debug(f"🔍 After filtering: {len(self._filtered_purchases)} purchases (from {len(self._all_purchases)} total)")
            
            # Update supplier filter with available suppliers
            self._update_supplier_filter()
            
            # 4. Update pagination state (reset page if needed, otherwise preserve)
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            
            total_pages = (len(self._filtered_purchases) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
            
            if self.pagination_widget:
                self.pagination_widget.set_pagination_state(current_page, total_pages, len(self._filtered_purchases))
                logger.debug(f"📄 Pagination: Page {current_page}/{total_pages}, Total items: {len(self._filtered_purchases)}")
            
            # 5. Update stats (with ALL data, not filtered)
            logger.info(f"📊 STATS: Showing stats for {len(self._all_purchases)} TOTAL purchases")
            self._update_stats_display(self._all_purchases)
            
            # 6. Get current page data and 7. Populate table with page data
            page_data = self._get_current_page_data()
            logger.debug(f"📄 Populating table with {len(page_data)} purchases on page {current_page}")
            self._populate_table(page_data)
            
            logger.info(f"Purchase list loaded successfully. Total: {len(self._all_purchases)}, Filtered: {len(self._filtered_purchases)}")
            
        # 8. Handle errors gracefully
        except Exception as e:
            logger.error(f"Error loading purchases: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to load purchases: {str(e)}")
        # 9. Finally block: set _is_loading = False
        finally:
            self._is_loading = False
    
    def _update_supplier_filter(self):
        """Update supplier dropdown with available suppliers."""
        suppliers = self._controller.extract_supplier_names(self._all_purchases)
        
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
    
    def _get_search_text(self) -> str:
        """Get current search text safely."""
        if hasattr(self, '_filter_widget'):
            return self._filter_widget.get_search_text().strip()
        return ""
    
    def _get_status_filter(self) -> str:
        """Get current status filter value."""
        if hasattr(self, '_status_combo'):
            return self._status_combo.currentData() or "All"
        return "All"
    
    def _get_period_filter(self) -> str:
        """Get current period filter value."""
        if hasattr(self, '_period_combo'):
            return self._period_combo.currentData() or "All Time"
        return "All Time"
    
    def _get_amount_filter(self) -> str:
        """Get current amount filter value."""
        if hasattr(self, '_amount_combo'):
            return self._amount_combo.currentData() or "All Amounts"
        return "All Amounts"
    
    def _get_supplier_filter(self) -> str:
        """Get current supplier filter value."""
        if hasattr(self, '_supplier_combo'):
            return self._supplier_combo.currentData() or "All Suppliers"
        return "All Suppliers"
    
    def _update_stats_display(self, purchases: list):
        """Update statistics cards with data from controller."""
        stats = self._controller.calculate_stats(purchases)
        self._total_card.set_value(str(stats.total))
        self._amount_card.set_value(f"₹{stats.total_amount:,.0f}")
        self._unpaid_card.set_value(str(stats.unpaid_count))
        self._paid_card.set_value(str(stats.paid_count))
    
    def _get_current_page_data(self) -> list:
        """Get purchases for the current page based on pagination state."""
        if not self.pagination_widget:
            return self._filtered_purchases
        
        current_page = self.pagination_widget.get_current_page()
        start_idx = (current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        return self._filtered_purchases[start_idx:end_idx]
    
    def _populate_table(self, purchases: list):
        """Populate table with purchase data."""
        self._table.setRowCount(0)
        
        # Get current page for row numbering offset
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        for page_idx, purchase in enumerate(purchases):
            # Calculate absolute row number accounting for pagination
            absolute_row_num = (current_page - 1) * self.ITEMS_PER_PAGE + page_idx + 1
            self._add_table_row(absolute_row_num, purchase)
    
    def _add_table_row(self, absolute_row_num: int, purchase: dict):
        """Add a single row to the table.
        
        Args:
            absolute_row_num: The absolute row number (accounting for pagination)
            purchase: The purchase data dictionary
        """
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Row number (absolute, accounting for pagination)
        num_item = QTableWidgetItem(str(absolute_row_num))
        num_item.setTextAlignment(Qt.AlignCenter)
        num_item.setForeground(QColor(TEXT_SECONDARY))
        self._table.setItem(row, 0, num_item)
        
        # Column 1: Invoice No. (stores purchase ID in UserRole)
        invoice_no = purchase.get('invoice_no', f"PUR-{purchase.get('id', 0):03d}")
        invoice_item = QTableWidgetItem(invoice_no)
        invoice_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        invoice_item.setForeground(QColor(PURCHASE_PRIMARY))
        invoice_item.setData(Qt.UserRole, purchase.get('id'))
        self._table.setItem(row, 1, invoice_item)
        
        # Column 2: Date
        date_item = QTableWidgetItem(str(purchase.get('date', '')))
        date_item.setFont(get_normal_font())
        self._table.setItem(row, 2, date_item)
        
        # Column 3: Supplier
        supplier_item = QTableWidgetItem(purchase.get('party_name', 'Unknown Supplier'))
        supplier_item.setFont(get_normal_font())
        self._table.setItem(row, 3, supplier_item)
        
        # Column 4: Amount
        amount = float(purchase.get('grand_total', 0) or 0)
        amount_item = QTableWidgetItem(format_currency(amount))
        amount_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._table.setItem(row, 4, amount_item)
        
        # Column 5: Status with color
        status = purchase.get('status', 'Unpaid')
        status_widget = self._create_status_cell(status)
        self._table.setCellWidget(row, 5, status_widget)
        
        # Column 6: Actions
        actions_widget = self._create_action_buttons(purchase)
        self._table.setCellWidget(row, 6, actions_widget)
    
    def _create_status_cell(self, status: str) -> QWidget:
        """Create status cell with colored badge."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignCenter)
        
        text_color, bg_color = self._controller.get_purchase_status_color(status)
        
        label = QLabel(status)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background: {bg_color};
                padding: 4px 12px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(label)
        
        return widget
    
    def _create_action_buttons(self, purchase: dict) -> QWidget:
        """Create action buttons for table row."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # View button
        view_btn = TableActionButton(
            text="View",
            tooltip="View Purchase",
            bg_color="#FEF3C7",
            hover_color=PURCHASE_PRIMARY,
            size=(60, 32)
        )
        view_btn.clicked.connect(lambda checked, pur=purchase: self._on_view_clicked(pur))
        layout.addWidget(view_btn)
        
        # Delete button
        del_btn = TableActionButton(
            text="Del",
            tooltip="Delete Purchase",
            bg_color="#FEE2E2",
            hover_color=DANGER,
            size=(50, 32)
        )
        del_btn.clicked.connect(lambda checked, pur=purchase: self._on_delete_clicked(pur))
        layout.addWidget(del_btn)
        
        return widget
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Slots)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self._load_data(reset_page=True)
    
    def _on_filter_changed(self, index: int):
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
    
    def _on_clear_filters(self):
        """Handle clear filters button click."""
        if hasattr(self, '_filter_widget'):
            self._filter_widget.reset_filters()
            self._filter_widget.clear_search()
        self._load_data()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_data()
    
    def _on_add_clicked(self):
        """Handle add purchase button click."""
        dialog = PurchaseInvoiceDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.purchase_updated.emit()
    
    def _on_export_clicked(self):
        """Handle export button click."""
        UIErrorHandler.show_info("Export", "Export functionality will be implemented soon!")
    
    def _on_row_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on table row."""
        row = item.row()
        # Get current page data to access the correct purchase
        page_data = self._get_current_page_data()
        if row < len(page_data):
            self._open_purchase_readonly(page_data[row])
    
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh the purchases list."""
        self._load_data()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible."""
        super().showEvent(event)
        self._load_data()
