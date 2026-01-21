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
        """Load products from controller and update UI."""
        if self._is_loading:
            return
        
        try:
            self._is_loading = True
            
            # Fetch all products
            self._all_products = self._controller.get_all_products()
            logger.debug(f"Loaded {len(self._all_products)} products")
            
            # Update category filter
            self._update_category_filter()
            
            # Reset pagination if requested
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            
            # Apply filters
            self._apply_filters()
            
        except Exception as e:
            logger.error(f"Failed to load products: {str(e)}")
            UIErrorHandler.show_error("Load Error", f"Failed to load products: {str(e)}")
        finally:
            self._is_loading = False
    
    def _apply_filters(self):
        """Apply all current filters and update display."""
        try:
            search_text = self._get_search_text()
            type_filter = self._get_type_filter()
            category_filter = self._get_category_filter()
            stock_filter = self._get_stock_filter()
            
            # Filter products
            self._filtered_products = self._controller.filter_products(
                products=self._all_products,
                search_text=search_text,
                type_filter=type_filter,
                category_filter=category_filter,
                stock_filter=stock_filter
            )
            
            # Update pagination state
            if self.pagination_widget:
                self.pagination_widget.set_pagination_state(
                    total_items=len(self._filtered_products),
                    current_page=1
                )
            
            # Update stats (using ALL data, not filtered)
            self._update_stats()
            
            # Populate table
            self._populate_table()
            
            logger.debug(f"Filters applied: {len(self._filtered_products)} products shown")
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {str(e)}")
            UIErrorHandler.show_error("Filter Error", f"Failed to apply filters: {str(e)}")
    
    def _update_category_filter(self):
        """Update category dropdown with available categories."""
        try:
            categories = self._controller.extract_categories(self._all_products)
            
            current_selection = self._category_combo.currentData()
            self._category_combo.blockSignals(True)
            self._category_combo.clear()
            self._category_combo.addItem("All Categories", "all")
            
            for category in categories:
                self._category_combo.addItem(category, category)
            
            # Restore selection if still valid
            index = self._category_combo.findData(current_selection)
            if index >= 0:
                self._category_combo.setCurrentIndex(index)
            
            self._category_combo.blockSignals(False)
        except Exception as e:
            logger.error(f"Failed to update category filter: {str(e)}")
    
    def _update_stats(self):
        """Update statistics cards using ALL data (unfiltered)."""
        try:
            stats = self._controller.calculate_stats(self._all_products)
            self._total_card.set_value(str(stats.total))
            self._in_stock_card.set_value(str(stats.in_stock))
            self._low_stock_card.set_value(str(stats.low_stock))
            self._out_stock_card.set_value(str(stats.out_of_stock))
        except Exception as e:
            logger.error(f"Failed to update stats: {str(e)}")
    
    def _populate_table(self):
        """Populate table with filtered product data (paginated)."""
        try:
            self._table.setRowCount(0)
            
            if not self.pagination_widget:
                return
            
            # Get current page
            current_page = self.pagination_widget.get_current_page()
            items_per_page = self.pagination_widget.get_items_per_page()
            
            # Calculate pagination
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_products = self._filtered_products[start_idx:end_idx]
            
            # Add rows
            for idx, product in enumerate(page_products):
                self._add_table_row(start_idx + idx, product)
            
        except Exception as e:
            logger.error(f"Failed to populate table: {str(e)}")
            UIErrorHandler.show_error("Table Error", f"Failed to populate table: {str(e)}")
    
    def _add_table_row(self, idx: int, product: dict):
        """Add a single row to the table."""
        try:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 50)
            
            # Column 0: Row number
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor(TEXT_SECONDARY))
            self._table.setItem(row, 0, num_item)
            
            # Column 1: Name
            product_type = product.get('product_type', product.get('type', ''))
            type_icon = "📦" if product_type == "Goods" else "🔧"
            name_text = f"{type_icon} {product.get('name', '')}"
            name_item = QTableWidgetItem(name_text)
            name_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            name_item.setData(Qt.UserRole, product.get('id'))
            self._table.setItem(row, 1, name_item)
            
            # Column 2: Type
            type_item = QTableWidgetItem(product_type)
            type_item.setFont(get_normal_font())
            type_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 2, type_item)
            
            # Column 3: HSN Code
            hsn_item = QTableWidgetItem(product.get('hsn_code', '-') or '-')
            hsn_item.setFont(get_normal_font())
            self._table.setItem(row, 3, hsn_item)
            
            # Column 4: Price
            price = float(product.get('sales_rate', 0) or 0)
            price_item = QTableWidgetItem(format_currency(price))
            price_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(row, 4, price_item)
            
            # Column 5: Stock
            stock_widget = self._create_stock_cell(product)
            self._table.setCellWidget(row, 5, stock_widget)
            
            # Column 6: Edit button
            edit_btn = TableActionButton(
                text="Edit", tooltip="Edit Product",
                bg_color="#EEF2FF", hover_color=PRIMARY, size=(60, 32)
            )
            edit_btn.clicked.connect(lambda checked, p=product: self._on_edit_clicked(p))
            self._table.setCellWidget(row, 6, edit_btn)
            
            # Column 7: Delete button
            delete_btn = TableActionButton(
                text="Del", tooltip="Delete Product",
                bg_color="#FEE2E2", hover_color=DANGER, size=(60, 32)
            )
            delete_btn.clicked.connect(lambda checked, p=product: self._on_delete_clicked(p))
            self._table.setCellWidget(row, 7, delete_btn)
            
        except Exception as e:
            logger.error(f"Failed to add table row: {str(e)}")
    
    def _create_stock_cell(self, product: dict) -> QWidget:
        """Create stock cell with status indicator."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignCenter)
        
        product_type = product.get('product_type', product.get('type', ''))
        status = self._controller.get_stock_status(product)
        
        if product_type == 'Service':
            text = "∞"
            color = PRIMARY
            bg = "#EEF2FF"
        else:
            stock = product.get('current_stock', product.get('opening_stock', product.get('stock_quantity', 0))) or 0
            unit = product.get('unit', 'Pcs')
            text = f"{int(stock)} {unit}"
            
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
    # Event Handlers (Slots)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debouncing."""
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(self.DEBOUNCE_DELAY)
    
    def _on_search_debounce(self):
        """Apply search after debounce delay."""
        self._apply_filters()
    
    def _on_filter_changed(self):
        """Handle filter combo change."""
        self._apply_filters()
    
    def _on_pagination_page_changed(self, page: int):
        """Handle pagination page change."""
        self._populate_table()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_products(reset_page=True)
    
    def _on_add_clicked(self):
        """Handle add product button click."""
        dialog = ProductDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_products()
            self.product_updated.emit()
    
    def _on_edit_clicked(self, product: dict):
        """Handle edit button click."""
        dialog = ProductDialog(product_data=product, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_products()
            self.product_updated.emit()
    
    def _on_delete_clicked(self, product: dict):
        """Handle delete button click with confirmation."""
        product_name = product.get('name', 'Unknown')
        product_id = product.get('id')
        
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\nThis action cannot be undone."
        ):
            return
        
        try:
            success, message = self._controller.delete_product(product_id)
            
            if success:
                UIErrorHandler.show_success("Success", f"Product '{product_name}' deleted successfully!")
                self._load_products()
                self.product_updated.emit()
            else:
                UIErrorHandler.show_error("Error", message)
        except Exception as e:
            logger.error(f"Failed to delete product: {str(e)}")
            UIErrorHandler.show_error("Error", f"Failed to delete product: {str(e)}")
    
    def _on_export_clicked(self):
        """Handle export button click."""
        from PySide6.QtWidgets import QMessageBox
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

