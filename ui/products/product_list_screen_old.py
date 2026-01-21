"""
Products List Screen
UI layer - handles layout, signals/slots, and user interactions only.

Architecture: UI → Controller → Service → DB
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QComboBox, QFrame, QTableWidgetItem,
    QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

# Theme imports
from theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    SUCCESS, DANGER, WARNING,
    FONT_SIZE_SMALL,
    get_normal_font, get_bold_font,
    get_filter_combo_style, get_filter_frame_style,
    get_filter_label_style, get_status_badge_style
)

# Widget imports
from widgets import (
    StatCard, ListTable, TableFrame, TableActionButton,
    SearchInputContainer, RefreshButton, ListHeader, StatsContainer
)

# Controller import (NOT service directly)
from controllers.product_controller import product_controller

# Error handler import
from ui.error_handler import UIErrorHandler

# Core imports for formatting only
from core.core_utils import format_currency

# UI imports
from ui.base import BaseScreen
from ui.products.product_form_dialog import ProductDialog

class ProductsScreen(BaseScreen):
    """
    Main screen for managing products and services.
    
    This UI component handles:
    - Layout and visual presentation
    - User interactions (clicks, typing)
    - Signal emissions for external communication
    
    Business logic is delegated to ProductController.
    """
    
    # Signal emitted when product data changes
    product_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Products", parent=parent)
        self.setObjectName("ProductsScreen")
        self._controller = product_controller
        self._all_products = []
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
    
    def _create_header(self) -> QWidget:
        """Create header with title and add button."""
        header = ListHeader("Products & Services", "+ Add Product")
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section."""
        # Create stat cards
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
        """Create filters section with search and dropdowns."""
        container = QFrame()
        container.setStyleSheet(get_filter_frame_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Search container using common widget
        self._search_container = SearchInputContainer("Search by name, HSN, category...")
        self._search_container.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_container)
        
        # Type filter
        type_label = QLabel("Type:")
        type_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(type_label)
        
        self._type_combo = QComboBox()
        self._type_combo.setStyleSheet(get_filter_combo_style())
        self._type_combo.addItem("All Types", "all")
        self._type_combo.addItem("Goods", "Goods")
        self._type_combo.addItem("Service", "Service")
        self._type_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._type_combo)
        
        # Category filter
        category_label = QLabel("Category:")
        category_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(category_label)
        
        self._category_combo = QComboBox()
        self._category_combo.setStyleSheet(get_filter_combo_style())
        self._category_combo.setMinimumWidth(150)
        self._category_combo.addItem("All Categories", "all")
        self._category_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._category_combo)
        
        # Stock filter
        stock_label = QLabel("Stock:")
        stock_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(stock_label)
        
        self._stock_combo = QComboBox()
        self._stock_combo.setStyleSheet(get_filter_combo_style())
        self._stock_combo.addItem("All", "All")
        self._stock_combo.addItem("In Stock", "In Stock")
        self._stock_combo.addItem("Low Stock", "Low Stock")
        self._stock_combo.addItem("Out of Stock", "Out of Stock")
        self._stock_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._stock_combo)
        
        layout.addStretch()
        
        # Refresh button using common widget
        refresh_btn = RefreshButton()
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh_btn)
        
        return container
    
    def _create_table_section(self) -> QWidget:
        """Create the products table."""
        # Create table frame container
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
        
        table_frame.set_table(self._table)
        return table_frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self):
        """Load products from controller and update UI."""
        try:
            # Fetch all products first
            self._all_products = self._controller.get_all_products()
            
            # Update category filter with available categories
            self._update_category_filter()
            
            # Apply current filters
            self._apply_filters()
            
        except Exception as e:
            self._show_error("Load Error", f"Failed to load products: {str(e)}")
    
    def _update_category_filter(self):
        """Update category dropdown with available categories."""
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
    
    def _apply_filters(self):
        """Apply all current filters and update display."""
        search_text = self._get_search_text()
        type_filter = self._get_type_filter()
        category_filter = self._get_category_filter()
        stock_filter = self._get_stock_filter()
        
        # Filter products via controller
        filtered_products = self._controller.filter_products(
            products=self._all_products,
            search_text=search_text,
            type_filter=type_filter,
            category_filter=category_filter,
            stock_filter=stock_filter
        )
        
        # Update stats and table
        self._update_stats_display(filtered_products)
        self._populate_table(filtered_products)
    
    def _get_search_text(self) -> str:
        """Get current search text safely."""
        if hasattr(self, '_search_container'):
            return self._search_container.text()
        return ""
    
    def _get_type_filter(self) -> str:
        """Get current type filter value."""
        if hasattr(self, '_type_combo'):
            data = self._type_combo.currentData()
            return "All" if data == "all" else data
        return "All"
    
    def _get_category_filter(self) -> str:
        """Get current category filter value."""
        if hasattr(self, '_category_combo'):
            data = self._category_combo.currentData()
            return "All Categories" if data == "all" else data
        return "All Categories"
    
    def _get_stock_filter(self) -> str:
        """Get current stock filter value."""
        if hasattr(self, '_stock_combo'):
            return self._stock_combo.currentData() or "All"
        return "All"
    
    def _update_stats_display(self, products: list):
        """Update statistics cards with data from controller."""
        stats = self._controller.calculate_stats(products)
        self._total_card.set_value(str(stats.total))
        self._in_stock_card.set_value(str(stats.in_stock))
        self._low_stock_card.set_value(str(stats.low_stock))
        self._out_stock_card.set_value(str(stats.out_of_stock))
    
    def _populate_table(self, products: list):
        """Populate table with product data."""
        self._table.setRowCount(0)
        
        for idx, product in enumerate(products):
            self._add_table_row(idx, product)
    
    def _add_table_row(self, idx: int, product: dict):
        """Add a single row to the table."""
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Row number
        num_item = QTableWidgetItem(str(idx + 1))
        num_item.setTextAlignment(Qt.AlignCenter)
        num_item.setForeground(QColor(TEXT_SECONDARY))
        self._table.setItem(row, 0, num_item)
        
        # Column 1: Name (stores product ID in UserRole)
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
        
        # Column 5: Stock with status indicator
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
        """Handle search text change."""
        self._apply_filters()
    
    def _on_filter_changed(self, index: int):
        """Handle filter combo change."""
        self._apply_filters()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_data()
    
    def _on_add_clicked(self):
        """Handle add product button click."""
        dialog = ProductDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.product_updated.emit()
    
    def _on_edit_clicked(self, product: dict):
        """Handle edit button click."""
        dialog = ProductDialog(product_data=product, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.product_updated.emit()
    
    def _on_delete_clicked(self, product: dict):
        """Handle delete button click with confirmation."""
        product_name = product.get('name', 'Unknown')
        product_id = product.get('id')
        
        # Use UIErrorHandler for consistent look & feel
        if not UIErrorHandler.ask_confirmation(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\nThis action cannot be undone."
        ):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_product(product_id)
        
        if success:
            UIErrorHandler.show_success("Success", f"Product '{product_name}' deleted successfully!")
            self._load_data()
            self.product_updated.emit()
        else:
            UIErrorHandler.show_error("Error", message)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Dialog Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _on_export_clicked(self):
        """Handle export button click."""
        QMessageBox.information(
            self, "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export receipt data to CSV or Excel."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh the products list."""
        self._load_data()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible."""
        super().showEvent(event)
        self._load_data()
