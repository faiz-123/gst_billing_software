"""
Products List Screen - Refactored to inherit from BaseListScreen
Uses common list patterns: pagination, filtering, table population, error handling

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import QWidget, QDialog, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

# Theme imports
from theme import (
    PRIMARY, SUCCESS, DANGER, WARNING, PRIMARY_LIGHT, DANGER_LIGHT,
    get_status_badge_style
)

# Widget imports
from widgets import (
    StatCard, ListTable, TableFrame, StatsContainer, FilterWidget
)

# UI imports - inherit from BaseListScreen
from ui.base.base_list_screen import BaseListScreen
from ui.base.list_table_helper import ListTableHelper

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


class ProductsScreen(BaseListScreen):
    """
    Refactored Products List Screen inheriting from BaseListScreen
    
    Inherits from BaseListScreen which provides:
    - Standard UI layout (_setup_ui)
    - Generic data loading pattern (_load_data)
    - Pagination support
    - Search debouncing
    - Error handling
    
    Uses ListTableHelper for table population - eliminating duplicate code.
    """
    
    # Signal emitted when product data changes
    product_updated = Signal()
    
    def __init__(self, parent=None):
        """Initialize products screen."""
        # Initialize base class - this calls _setup_ui() automatically
        super().__init__(title="Products", parent=parent)
        self.setObjectName("ProductsScreen")
        logger.debug("Initializing ProductsScreen")
        
        self._controller = product_controller
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration Overrides
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return text for add button"""
        return "+ Add Product"
    
    def _get_entity_name(self) -> str:
        """Return singular entity name for pagination"""
        return "product"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Overrides (Required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section with icons."""
        self._total_card = StatCard("📦", "Total Products", "0", PRIMARY)
        self._in_stock_card = StatCard("✅", "In Stock", "0", SUCCESS)
        self._low_stock_card = StatCard("⚠️", "Low Stock", "0", WARNING)
        self._out_stock_card = StatCard("❌", "Out of Stock", "0", DANGER)
        
        # Set tooltip for total card
        self._total_card.setToolTip("Total number of products/services")
        
        return StatsContainer([
            self._total_card,
            self._in_stock_card,
            self._low_stock_card,
            self._out_stock_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section using FilterWidget for consistency."""
        self._filter_widget = FilterWidget()
        
        # Search filter
        self._filter_widget.add_search_filter("Search by name, HSN, category...")
        self._filter_widget.search_changed.connect(self._on_search_changed)
        
        # Type filter
        type_options = {
            "All Types": "all",
            "Goods": "Goods",
            "Service": "Service"
        }
        self._type_combo = self._filter_widget.add_combo_filter(
            "type", "Type:", type_options
        )
        
        # Category filter (populated dynamically)
        self._category_combo = self._filter_widget.add_combo_filter(
            "category", "Category:", {"All Categories": "all"}
        )
        self._category_combo.setMinimumWidth(150)
        
        # Stock filter
        stock_options = {
            "All": "all",
            "In Stock": "In Stock",
            "Low Stock": "Low Stock",
            "Out of Stock": "Out of Stock"
        }
        self._stock_combo = self._filter_widget.add_combo_filter(
            "stock", "Stock:", stock_options
        )
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the products table with ListTableHelper integration."""
        table_frame = TableFrame()
        
        # Create table with headers
        self._table = ListTable(headers=[
            "#", "Name", "Type", "HSN", "Price", "Stock", "Edit", "Delete"
        ])
        
        # Configure column widths
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
        
        # Initialize ListTableHelper for populating the table
        self._table_helper = ListTableHelper(self._table, self.ITEMS_PER_PAGE)
        
        # Define column configurations for table population
        self._column_configs = [
            {'type': 'row_number'},
            {'key': 'name', 'type': 'text', 'bold': True, 'align': Qt.AlignLeft},
            {'key': 'product_type', 'type': 'text', 'align': Qt.AlignCenter,
             'formatter': lambda v: v or '-'},
            {'key': 'hsn_code', 'type': 'text', 'formatter': lambda v: v or '-'},
            {'key': 'sales_rate', 'type': 'currency', 'bold': True, 'align': Qt.AlignRight},
            {'type': 'custom', 'key': 'stock'},  # Custom stock cell
            {'type': 'button', 'text': 'Edit', 'tooltip': 'Edit Product',
             'bg_color': PRIMARY_LIGHT, 'hover_color': PRIMARY, 'size': (60, 32)},
            {'type': 'button', 'text': 'Del', 'tooltip': 'Delete Product',
             'bg_color': DANGER_LIGHT, 'hover_color': DANGER, 'size': (60, 32)},
        ]
        
        table_frame.set_table(self._table)
        return table_frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading Overrides (Required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _fetch_all_data(self) -> list:
        """Fetch all products from controller.
        
        Returns:
            List of all products
        """
        products = self._controller.get_all_products()
        
        # Update category filter options when data is loaded
        self._update_category_filter(products)
        
        return products
    
    def filter_data(self, all_data: list) -> list:
        """Apply filters to products list.
        
        Args:
            all_data: List of all products
            
        Returns:
            Filtered list of products
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        type_filter = self._type_combo.currentData() if hasattr(self, '_type_combo') else "all"
        category_filter = self._category_combo.currentData() if hasattr(self, '_category_combo') else "all"
        stock_filter = self._stock_combo.currentData() if hasattr(self, '_stock_combo') else "all"
        
        return self._apply_filters(all_data, search_text, type_filter, category_filter, stock_filter)
    
    def _apply_filters(self, products: list, search_text: str, type_filter: str, 
                       category_filter: str, stock_filter: str) -> list:
        """Apply filters to products list with validation.
        
        Args:
            products: List of products to filter
            search_text: Search text (name, HSN, category)
            type_filter: Product type filter (Goods, Service)
            category_filter: Category filter
            stock_filter: Stock status filter
            
        Returns:
            Filtered list of products
        """
        try:
            filtered = products
            
            # Search filter
            if search_text and search_text.strip():
                search_lower = search_text.lower().strip()
                filtered = [
                    p for p in filtered
                    if (search_lower in (str(p.get('name') or '')).lower()
                        or search_lower in (str(p.get('hsn_code') or '')).lower()
                        or search_lower in (str(p.get('category') or '')).lower())
                ]
                logger.debug(f"After search filter: {len(filtered)} products")
            
            # Type filter
            if type_filter and type_filter != "all":
                filtered = [
                    p for p in filtered
                    if (str(p.get('product_type') or p.get('type') or '')).lower() == type_filter.lower()
                ]
                logger.debug(f"After type filter ({type_filter}): {len(filtered)} products")
            
            # Category filter
            if category_filter and category_filter != "all":
                filtered = [
                    p for p in filtered
                    if (str(p.get('category') or '')).lower() == category_filter.lower()
                ]
                logger.debug(f"After category filter ({category_filter}): {len(filtered)} products")
            
            # Stock filter
            if stock_filter and stock_filter != "all":
                filtered = [
                    p for p in filtered
                    if self._controller.get_stock_status(p) == stock_filter
                ]
                logger.debug(f"After stock filter ({stock_filter}): {len(filtered)} products")
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}", exc_info=True)
            return products  # Return unfiltered list on error
    
    def _update_category_filter(self, products: list):
        """Update category dropdown with available categories.
        
        Args:
            products: List of all products
        """
        try:
            categories = self._controller.extract_categories(products)
            
            current_selection = self._category_combo.currentData()
            self._category_combo.blockSignals(True)
            self._category_combo.clear()
            self._category_combo.addItem("All Categories", "all")
            
            for category in sorted(categories):
                self._category_combo.addItem(category, category)
            
            # Restore selection if still valid
            if current_selection and current_selection != "all":
                index = self._category_combo.findData(current_selection)
                if index >= 0:
                    self._category_combo.setCurrentIndex(index)
            
            self._category_combo.blockSignals(False)
            logger.debug(f"Category filter updated with {len(categories)} options")
            
        except Exception as e:
            logger.error(f"Failed to update category filter: {str(e)}", exc_info=True)
    
    def _update_stats(self, products: list):
        """Update statistics cards with error handling.
        
        Args:
            products: List of all products (unfiltered for stats)
        """
        try:
            stats = self._controller.calculate_stats(products)
            
            self._total_card.set_value(str(stats.total))
            self._in_stock_card.set_value(str(stats.in_stock))
            self._low_stock_card.set_value(str(stats.low_stock))
            self._out_stock_card.set_value(str(stats.out_of_stock))
            
            logger.debug(f"Stats updated: total={stats.total}, in_stock={stats.in_stock}, "
                        f"low_stock={stats.low_stock}, out_of_stock={stats.out_of_stock}")
            
        except Exception as e:
            logger.error(f"Failed to update stats: {str(e)}", exc_info=True)
    
    def _populate_table(self, products: list):
        """Populate table with product data using ListTableHelper.
        
        Args:
            products: List of products for current page
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(products)} products using ListTableHelper")
        
        # Use ListTableHelper to populate the table
        self._table_helper.populate(
            data=products,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Add custom stock cells and connect button handlers for each row
        for row in range(self._table.rowCount()):
            product = products[row] if row < len(products) else None
            if product:
                # Update name column with icon based on product type
                product_type = product.get('product_type', product.get('type', ''))
                type_icon = "📦" if product_type == "Goods" else "🔧"
                name_item = self._table.item(row, 1)
                if name_item:
                    name_item.setText(f"{type_icon} {product.get('name', '')}")
                
                # Add custom stock cell (column 5)
                stock_widget = self._create_stock_cell(product)
                self._table.setCellWidget(row, 5, stock_widget)
                
                # Edit button (column 6)
                edit_btn = self._table.cellWidget(row, 6)
                if edit_btn:
                    edit_btn.clicked.connect(lambda checked, p=product: self._on_edit_product(p))
                
                # Delete button (column 7)
                delete_btn = self._table.cellWidget(row, 7)
                if delete_btn:
                    delete_btn.clicked.connect(lambda checked, p=product: self._on_delete_product(p))
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")
    
    def _create_stock_cell(self, product: dict) -> QWidget:
        """Create stock cell with status indicator.
        
        Args:
            product: Product data dict
            
        Returns:
            QWidget with styled stock display
        """
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignCenter)
        
        product_type = product.get('product_type', product.get('type', ''))
        status = self._controller.get_stock_status(product)
        
        if product_type == 'Service':
            # Services have unlimited stock
            text = "∞"
            color = PRIMARY
            bg = PRIMARY_LIGHT
        else:
            # Goods have quantified stock
            try:
                stock = (product.get('current_stock') or 
                        product.get('opening_stock') or 
                        product.get('stock_quantity') or 0)
                stock = int(stock)
            except (ValueError, TypeError):
                stock = 0
            
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handler Overrides
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_add_clicked(self):
        """Show add product dialog - overrides BaseListScreen."""
        dialog = ProductDialog(parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self._load_data()
            self.product_updated.emit()
    
    def _on_edit_product(self, product: dict):
        """Show edit product dialog."""
        dialog = ProductDialog(product_data=product, parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self._load_data()
            self.product_updated.emit()
    
    def _on_delete_product(self, product: dict):
        """Delete a product after confirmation.
        
        Checks for:
        - Confirmation from user
        - Related invoices (if any)
        """
        product_name = product.get('name', 'Unknown')
        product_id = product.get('id')
        
        try:
            # Validate product exists
            if not product_id:
                logger.warning("Attempt to delete product with no ID")
                UIErrorHandler.show_error("Error", "Invalid product selected")
                return
            
            # Confirmation from user
            if not UIErrorHandler.ask_confirmation(
                "Confirm Delete",
                f"Are you sure you want to delete '{product_name}'?\n\n"
                f"This action cannot be undone."
            ):
                logger.debug(f"Delete cancelled by user for product {product_id}")
                return
            
            # Attempt deletion
            logger.info(f"Deleting product {product_id} ({product_name})")
            success, message = self._controller.delete_product(product_id)
            
            if success:
                logger.info(f"Product {product_id} deleted successfully")
                UIErrorHandler.show_success("Success", f"Product '{product_name}' deleted successfully!")
                self._load_data(reset_page=True)
                self.product_updated.emit()
            else:
                logger.error(f"Failed to delete product {product_id}: {message}")
                UIErrorHandler.show_error("Error", message)
            
        except Exception as e:
            logger.error(f"Error deleting product {product.get('id')}: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to delete product: {str(e)}")
