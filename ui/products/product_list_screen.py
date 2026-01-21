"""
Products List Screen (Refactored)
Simplified refactored version using reusable FilterWidget and ListTableHelper

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QFrame, QTableWidgetItem, QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor

# Theme imports
from theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, WHITE, BORDER,
    SUCCESS, DANGER, WARNING,
    FONT_SIZE_SMALL,
    get_normal_font, get_bold_font,
    get_filter_combo_style, get_filter_label_style,
    get_status_badge_style
)

# Widget imports
from widgets import (
    StatCard, ListTable, TableFrame, TableActionButton,
    SearchInputContainer, RefreshButton, ListHeader, StatsContainer,
    FilterWidget
)

# Base screen imports
from ui.base import BaseScreen, PaginationWidget

# Controller import
from controllers.product_controller import product_controller

# Error handler import
from ui.error_handler import UIErrorHandler

# Core imports
from core.core_utils import format_currency
from core.logger import get_logger

# Dialog import
from ui.products.product_form_dialog import ProductDialog

logger = get_logger(__name__)


class ProductsScreen(BaseScreen):
    """
    Refactored Products List Screen using reusable FilterWidget and PaginationWidget
    
    Improvements over previous version:
    - FilterWidget eliminates duplicate filter code
    - Better code organization with clear separation of concerns
    - Consistent with party_list_screen pattern
    """
    
    # Signal emitted when product data changes
    product_updated = Signal()
    
    # Pagination constant
    ITEMS_PER_PAGE = 49
    DEBOUNCE_DELAY = 500  # ms
    
    def __init__(self, parent=None):
        """Initialize products screen."""
        super().__init__(title="Products", parent=parent)
        self.setObjectName("ProductsScreen")
        logger.debug("Initializing ProductsScreen")
        
        self._controller = product_controller
        
        # Data caching
        self._all_products = []
        self._filtered_products = []
        self._is_loading = False
        
        # Pagination widget
        self.pagination_widget = None
        
        # Debounce timer for search
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._on_search_debounce)
        
        self._setup_ui()
        self._load_products()
    
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
        """Create header with title and add button."""
        header = ListHeader("Products & Services", "+ Add Product")
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section."""
        self._total_card = StatCard("📦", "Total Products", "0", PRIMARY)
        self._in_stock_card = StatCard("✅", "In Stock", "0", SUCCESS)
        self._low_stock_card = StatCard("⚠️", "Low Stock", "0", WARNING)
        self._out_stock_card = StatCard("❌", "Out of Stock", "0", DANGER)
        
        return StatsContainer([
            self._total_card,
            self._in_stock_card,
            self._low_stock_card,
            self._out_stock_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget."""
        filter_widget = FilterWidget()
        
        # Search filter
        filter_widget.add_search_filter("Search by name, HSN, category...")
        filter_widget.search_changed.connect(self._on_search_changed)
        
        # Type filter
        type_options = {
            "All Types": "all",
            "Goods": "Goods",
            "Service": "Service"
        }
        self._type_combo = filter_widget.add_combo_filter(
            "type", "Type:", type_options
        )
        
        # Category filter
        self._category_combo = filter_widget.add_combo_filter(
            "category", "Category:", {"All Categories": "all"}
        )
        self._category_combo.setMinimumWidth(150)
        
        # Stock filter
        stock_options = {
            "All": "All",
            "In Stock": "In Stock",
            "Low Stock": "Low Stock",
            "Out of Stock": "Out of Stock"
        }
        self._stock_combo = filter_widget.add_combo_filter(
            "stock", "Stock:", stock_options
        )
        
        # Stretch and refresh button
        filter_widget.add_stretch()
        filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the products table."""
        table_frame = TableFrame()
        
        self._table = ListTable(headers=[
            "#", "Name", "Type", "HSN", "Price", "Stock", "Edit", "Delete"
        ])
        
        self._table.configure_columns([
            {"width": 50, "resize": "fixed"},      # #
            {"resize": "stretch"},                  # Name
            {"width": 80, "resize": "fixed"},      # Type
            {"width": 120, "resize": "fixed"},     # HSN
            {"width": 120, "resize": "fixed"},     # Price
            {"width": 120, "resize": "fixed"},     # Stock
            {"width": 80, "resize": "fixed"},      # Edit
            {"width": 80, "resize": "fixed"},      # Delete
        ])
        
        table_frame.set_table(self._table)
        return table_frame
    
    def _create_pagination_controls(self) -> QWidget:
        """Create pagination widget."""
        self.pagination_widget = PaginationWidget(
            items_per_page=self.ITEMS_PER_PAGE,
            entity_name="product"
        )
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        return self.pagination_widget
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading and Filtering
    # ─────────────────────────────────────────────────────────────────────────
    
    def _load_products(self, reset_page: bool = False):
        """
        Load products with proper state management and pagination.
        
        Pattern:
        1. Check if already loading (prevent concurrent calls)
        2. Fetch all data from service → self._all_products
        3. Apply filters → self._filtered_products
        4. Update pagination state
        5. Update stats (with ALL data, not filtered)
        6. Get current page data
        7. Populate table with page data
        8. Handle errors gracefully
        9. Finally block: set _is_loading = False
        """
        # Step 1: Check if already loading
        if self._is_loading:
            logger.debug("Load already in progress, skipping concurrent request")
            return
        
        try:
            self._is_loading = True
            logger.info("Starting product data load")
            
            # Step 2: Fetch all products from service
            self._all_products = self._controller.get_all_products()
            logger.debug(f"Fetched {len(self._all_products)} products from service")
            
            # Step 3: Apply filters
            self._apply_filters()
            
            # Step 4: Update category filter options
            self._update_category_filter()
            
            # Step 5: Reset pagination if requested
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
                logger.debug("Pagination reset to page 1")
            
            # Step 6: Update stats using ALL data (unfiltered)
            self._update_stats()
            
            # Step 7: Populate table with filtered/paginated data
            self._populate_table()
            
            logger.info(f"Product load complete: {len(self._all_products)} total, "
                       f"{len(self._filtered_products)} filtered")
            
        except Exception as e:
            logger.error(f"Failed to load products: {str(e)}", exc_info=True)
            UIErrorHandler.show_error(
                "Load Error",
                f"Failed to load products: {str(e)}\n\nPlease try again or contact support."
            )
        finally:
            # Step 9: Always reset loading state
            self._is_loading = False
            logger.debug("Product load state reset")
    
    def _apply_filters(self):
        """
        Apply all current filters and update display.
        
        Process:
        1. Fetch current filter values
        2. Filter products using controller
        3. Update pagination state with filtered count
        4. Populate table with current page data
        5. Handle errors gracefully
        """
        try:
            logger.debug("Applying filters to products")
            
            # Step 1: Get current filter values
            search_text = self._get_search_text()
            type_filter = self._get_type_filter()
            category_filter = self._get_category_filter()
            stock_filter = self._get_stock_filter()
            
            logger.debug(f"Filter values: search='{search_text}', type={type_filter}, "
                        f"category={category_filter}, stock={stock_filter}")
            
            # Step 2: Apply filters using controller
            self._filtered_products = self._controller.filter_products(
                products=self._all_products,
                search_text=search_text,
                type_filter=type_filter,
                category_filter=category_filter,
                stock_filter=stock_filter
            )
            logger.debug(f"Filter result: {len(self._filtered_products)} products after filtering")
            
            # Step 3: Update pagination state with filtered count
            if self.pagination_widget:
                total_items = len(self._filtered_products)
                items_per_page = self.pagination_widget.get_items_per_page()
                # Ceiling division for total pages
                total_pages = (total_items + items_per_page - 1) // items_per_page
                
                self.pagination_widget.set_pagination_state(
                    current_page=1,
                    total_pages=total_pages,
                    total_items=total_items
                )
                logger.debug(f"Pagination updated: {total_pages} pages, {total_items} items")
            
            # Step 4: Populate table with current page data
            self._populate_table()
            
            logger.info(f"Filters applied successfully: {len(self._filtered_products)} "
                       f"products shown out of {len(self._all_products)} total")
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {str(e)}", exc_info=True)
            UIErrorHandler.show_error(
                "Filter Error",
                f"Failed to apply filters: {str(e)}\n\nPlease try again."
            )
    
    def _update_category_filter(self):
        """
        Update category dropdown with available categories from all products.
        
        Process:
        1. Extract unique categories from all products
        2. Update dropdown options
        3. Restore previous selection if still valid
        4. Handle errors gracefully
        """
        try:
            logger.debug("Updating category filter options")
            
            # Step 1: Extract unique categories
            categories = self._controller.extract_categories(self._all_products)
            logger.debug(f"Found {len(categories)} unique categories")
            
            # Step 2: Store current selection
            current_selection = self._category_combo.currentData()
            
            # Step 3: Update combo box
            self._category_combo.blockSignals(True)
            self._category_combo.clear()
            self._category_combo.addItem("All Categories", "all")
            
            for category in sorted(categories):
                self._category_combo.addItem(category, category)
            
            # Step 4: Restore selection if still valid
            if current_selection and current_selection != "all":
                index = self._category_combo.findData(current_selection)
                if index >= 0:
                    self._category_combo.setCurrentIndex(index)
                    logger.debug(f"Restored category selection: {current_selection}")
                else:
                    logger.debug(f"Previous category '{current_selection}' not found, using 'All'")
            
            self._category_combo.blockSignals(False)
            logger.info(f"Category filter updated with {len(categories)} options")
            
        except Exception as e:
            logger.error(f"Failed to update category filter: {str(e)}", exc_info=True)
    
    def _update_stats(self):
        """
        Update statistics cards using ALL data (unfiltered).
        
        Stats always show total counts across ALL products,
        not just the filtered subset. This gives users full visibility.
        
        Process:
        1. Calculate stats from all products
        2. Update each stat card
        3. Handle errors gracefully
        """
        try:
            logger.debug("Updating statistics from all products")
            
            # Step 1: Calculate stats
            stats = self._controller.calculate_stats(self._all_products)
            
            # Step 2: Update stat cards
            self._total_card.set_value(str(stats.total))
            self._in_stock_card.set_value(str(stats.in_stock))
            self._low_stock_card.set_value(str(stats.low_stock))
            self._out_stock_card.set_value(str(stats.out_of_stock))
            
            logger.debug(f"Stats updated: total={stats.total}, in_stock={stats.in_stock}, "
                        f"low_stock={stats.low_stock}, out_of_stock={stats.out_of_stock}")
            
        except Exception as e:
            logger.error(f"Failed to update stats: {str(e)}", exc_info=True)
            # Don't show error dialog for stats - silent failure is acceptable
    
    def _populate_table(self):
        """
        Populate table with filtered product data (paginated).
        
        Process:
        1. Clear existing rows
        2. Get pagination parameters (current page, items per page)
        3. Calculate slice indices for current page
        4. Get page data from filtered products
        5. Add rows to table
        6. Handle errors gracefully
        """
        try:
            logger.debug("Starting table population")
            
            # Step 1: Clear table
            self._table.setRowCount(0)
            
            if not self.pagination_widget:
                logger.warning("Pagination widget not available")
                return
            
            # Step 2: Get pagination parameters
            current_page = self.pagination_widget.get_current_page()
            items_per_page = self.pagination_widget.get_items_per_page()
            logger.debug(f"Populating table: page {current_page}, {items_per_page} items/page")
            
            # Step 3 & 4: Calculate slice and get page data
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_products = self._filtered_products[start_idx:end_idx]
            
            logger.debug(f"Page slice: {start_idx}:{end_idx}, {len(page_products)} items to display")
            
            # Step 5: Add rows
            for idx, product in enumerate(page_products):
                self._add_table_row(start_idx + idx, product)
            
            logger.info(f"Table populated: {len(page_products)} rows added for page {current_page}")
            
        except Exception as e:
            logger.error(f"Failed to populate table: {str(e)}", exc_info=True)
            UIErrorHandler.show_error(
                "Table Error",
                f"Failed to populate table: {str(e)}\n\nPlease try refreshing."
            )
    
    def _add_table_row(self, idx: int, product: dict):
        """
        Add a single row to the table with all columns formatted.
        
        Process:
        1. Create new row
        2. Set row number column
        3. Set name column with icon
        4. Set type column
        5. Set HSN code column
        6. Set price column with formatting
        7. Set stock cell with status indicator
        8. Add edit action button
        9. Add delete action button
        10. Handle errors gracefully
        """
        try:
            logger.debug(f"Adding row {idx + 1} to table")
            
            # Step 1: Create new row
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 50)
            
            # Step 2: Row number
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor(TEXT_SECONDARY))
            self._table.setItem(row, 0, num_item)
            
            # Step 3: Product name with icon
            product_type = product.get('product_type', product.get('type', ''))
            type_icon = "📦" if product_type == "Goods" else "🔧"
            name_text = f"{type_icon} {product.get('name', '')}"
            name_item = QTableWidgetItem(name_text)
            name_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            name_item.setData(Qt.UserRole, product.get('id'))
            self._table.setItem(row, 1, name_item)
            
            # Step 4: Product type
            type_item = QTableWidgetItem(product_type)
            type_item.setFont(get_normal_font())
            type_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 2, type_item)
            
            # Step 5: HSN Code
            hsn_code = product.get('hsn_code', '-') or '-'
            hsn_item = QTableWidgetItem(hsn_code)
            hsn_item.setFont(get_normal_font())
            self._table.setItem(row, 3, hsn_item)
            
            # Step 6: Price with currency formatting
            try:
                price = float(product.get('sales_rate', 0) or 0)
                price_text = format_currency(price)
            except (ValueError, TypeError):
                price_text = "₹0.00"
                logger.warning(f"Invalid price for product {product.get('id')}: {product.get('sales_rate')}")
            
            price_item = QTableWidgetItem(price_text)
            price_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(row, 4, price_item)
            
            # Step 7: Stock status cell
            stock_widget = self._create_stock_cell(product)
            self._table.setCellWidget(row, 5, stock_widget)
            
            # Step 8: Edit button
            edit_btn = TableActionButton(
                text="Edit", tooltip="Edit Product",
                bg_color="#EEF2FF", hover_color=PRIMARY, size=(60, 32)
            )
            edit_btn.clicked.connect(lambda checked, p=product: self._on_edit_clicked(p))
            self._table.setCellWidget(row, 6, edit_btn)
            
            # Step 9: Delete button
            delete_btn = TableActionButton(
                text="Del", tooltip="Delete Product",
                bg_color="#FEE2E2", hover_color=DANGER, size=(60, 32)
            )
            delete_btn.clicked.connect(lambda checked, p=product: self._on_delete_clicked(p))
            self._table.setCellWidget(row, 7, delete_btn)
            
            logger.debug(f"Row {idx + 1} added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add row {idx + 1}: {str(e)}", exc_info=True)
    
    def _create_stock_cell(self, product: dict) -> QWidget:
        """
        Create stock cell with status indicator and formatted display.
        
        Process:
        1. Determine product type
        2. Get stock status
        3. Format display text based on type (service vs. goods)
        4. Assign color and background based on status
        5. Create label with styling
        6. Return widget
        """
        try:
            widget = QWidget()
            widget.setStyleSheet("background: transparent; border: none;")
            
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setAlignment(Qt.AlignCenter)
            
            product_type = product.get('product_type', product.get('type', ''))
            status = self._controller.get_stock_status(product)
            
            logger.debug(f"Creating stock cell for {product.get('name')}: type={product_type}, status={status}")
            
            # Determine display text and colors
            if product_type == 'Service':
                # Services have unlimited stock
                text = "∞"
                color = PRIMARY
                bg = "#EEF2FF"
            else:
                # Goods have quantified stock
                try:
                    stock = (product.get('current_stock') or 
                            product.get('opening_stock') or 
                            product.get('stock_quantity') or 0)
                    stock = int(stock)
                except (ValueError, TypeError):
                    stock = 0
                    logger.warning(f"Invalid stock quantity for {product.get('id')}: {product.get('current_stock')}")
                
                unit = product.get('unit', 'Pcs')
                text = f"{stock} {unit}"
                
                # Color based on stock status
                if status == "In Stock":
                    color = SUCCESS
                    bg = "#ECFDF5"
                elif status == "Low Stock":
                    color = WARNING
                    bg = "#FFFBEB"
                else:  # Out of Stock
                    color = DANGER
                    bg = "#FEF2F2"
            
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(get_status_badge_style(color, bg))
            layout.addWidget(label)
            
            return widget
            
        except Exception as e:
            logger.error(f"Failed to create stock cell: {str(e)}", exc_info=True)
            # Return empty widget on error
            widget = QWidget()
            widget.setStyleSheet("background: transparent; border: none;")
            return widget
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers (Slots)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """
        Handle search text change with debouncing.
        
        Debouncing prevents excessive filtering on every keystroke.
        Waits for DEBOUNCE_DELAY ms of silence before applying filters.
        """
        logger.debug(f"Search text changed: '{text}'")
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(self.DEBOUNCE_DELAY)
    
    def _on_search_debounce(self):
        """Apply search after debounce delay expires."""
        logger.debug("Search debounce timeout, applying filters")
        self._apply_filters()
    
    def _on_filter_changed(self):
        """Handle filter combo change (type, category, stock)."""
        logger.debug("Filter changed, applying filters")
        self._apply_filters()
    
    def _on_pagination_page_changed(self, page: int):
        """
        Handle pagination page change.
        
        Only repopulates table with data from new page,
        doesn't reload data from server.
        """
        logger.debug(f"Page changed to {page}")
        self._populate_table()
    
    def _on_refresh_clicked(self):
        """
        Handle refresh button click.
        
        Reloads all data from server and resets pagination.
        """
        logger.info("Refresh button clicked, reloading all products")
        self._load_products(reset_page=True)
    
    def _on_add_clicked(self):
        """Handle add product button click."""
        logger.info("Add product dialog opened")
        dialog = ProductDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            logger.info("Product created, reloading data")
            self._load_products()
            self.product_updated.emit()
    
    def _on_edit_clicked(self, product: dict):
        """Handle edit button click."""
        product_id = product.get('id')
        product_name = product.get('name')
        logger.info(f"Edit product dialog opened: {product_id} ({product_name})")
        dialog = ProductDialog(product_data=product, parent=self)
        if dialog.exec() == QDialog.Accepted:
            logger.info(f"Product {product_id} updated, reloading data")
            self._load_products()
            self.product_updated.emit()
    
    def _on_delete_clicked(self, product: dict):
        """
        Handle delete button click with confirmation.
        
        Process:
        1. Get product name
        2. Show confirmation dialog
        3. If confirmed, call controller delete
        4. Reload data on success
        5. Show success/error message
        6. Handle errors gracefully
        """
        product_name = product.get('name', 'Unknown')
        product_id = product.get('id')
        
        logger.info(f"Delete requested for product {product_id} ({product_name})")
        
        # Step 2: Confirmation dialog
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\n"
            f"This action cannot be undone."
        ):
            logger.debug("Delete cancelled by user")
            return
        
        try:
            logger.debug(f"Deleting product {product_id}")
            # Step 3: Call controller delete
            success, message = self._controller.delete_product(product_id)
            
            if success:
                logger.info(f"Product {product_id} deleted successfully")
                # Step 4: Reload data
                self._load_products()
                # Step 5: Show success
                UIErrorHandler.show_success(
                    "Success",
                    f"Product '{product_name}' deleted successfully!"
                )
                self.product_updated.emit()
            else:
                logger.warning(f"Delete failed: {message}")
                UIErrorHandler.show_error("Error", message)
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {str(e)}", exc_info=True)
            UIErrorHandler.show_error(
                "Error",
                f"Failed to delete product: {str(e)}\n\nPlease try again."
            )
    
    def _on_export_clicked(self):
        """Handle export button click."""
        from PySide6.QtWidgets import QMessageBox
        logger.info("Export clicked")
        QMessageBox.information(
            self, "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export product data to CSV or Excel."
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Filter Value Getters
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_search_text(self) -> str:
        """Get current search text."""
        try:
            return self._type_combo.parent().parent().findChild(SearchInputContainer).text()
        except:
            return ""
    
    def _get_type_filter(self) -> str:
        """Get current type filter value."""
        try:
            data = self._type_combo.currentData()
            return "All" if data == "all" else data
        except:
            return "All"
    
    def _get_category_filter(self) -> str:
        """Get current category filter value."""
        try:
            data = self._category_combo.currentData()
            return "All Categories" if data == "all" else data
        except:
            return "All Categories"
    
    def _get_stock_filter(self) -> str:
        """Get current stock filter value."""
        try:
            return self._stock_combo.currentData() or "All"
        except:
            return "All"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh products."""
        self._load_products()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible."""
        super().showEvent(event)
        if not self._all_products:  # Only load if empty
            self._load_products()

