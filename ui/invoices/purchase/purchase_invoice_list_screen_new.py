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
    get_title_font, get_normal_font, get_bold_font,
    get_filter_combo_style, get_filter_frame_style,
    get_search_container_style, get_search_input_style, get_icon_button_style,
    get_filter_label_style, FONT_SIZE_SMALL
)

# Widget imports
from widgets import CustomButton, StatCard, ListTable, TableFrame, TableActionButton

# Controller import (NOT service or db directly)
from controllers.purchase_controller import purchase_controller

# Core imports for formatting only
from core.core_utils import format_currency

# UI imports
from ui.base import BaseScreen
from ui.invoices.purchase.purchase_invoice_form_dialog import PurchaseInvoiceDialog


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
    
    def __init__(self, parent=None):
        super().__init__(title="Purchase Invoices", parent=parent)
        self.setObjectName("PurchasesScreen")
        self._controller = purchase_controller
        self._all_purchases = []
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
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("🛒 Purchase Invoices")
        title.setFont(get_title_font())
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Export button
        export_btn = CustomButton("📤 Export", "secondary")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(export_btn)
        
        # Add button
        add_btn = CustomButton("+ New Purchase", "primary")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(add_btn)
        
        return header
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section."""
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Create stat cards (amber/orange theme for purchases)
        self._total_card = StatCard("📋", "Total Purchases", "0", PURCHASE_PRIMARY)
        self._amount_card = StatCard("💸", "Total Expense", "₹0", DANGER)
        self._unpaid_card = StatCard("⏰", "Unpaid", "0", "#6366F1")
        self._paid_card = StatCard("✅", "Paid", "0", SUCCESS)
        
        layout.addWidget(self._total_card)
        layout.addWidget(self._amount_card)
        layout.addWidget(self._unpaid_card)
        layout.addWidget(self._paid_card)
        
        return container
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section with search and dropdowns."""
        container = QFrame()
        container.setStyleSheet(get_filter_frame_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Search container
        search_container = self._create_search_input()
        layout.addWidget(search_container)
        
        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(status_label)
        
        self._status_combo = QComboBox()
        self._status_combo.setStyleSheet(get_filter_combo_style())
        self._status_combo.addItem("All", "All")
        self._status_combo.addItem("Paid", "Paid")
        self._status_combo.addItem("Unpaid", "Unpaid")
        self._status_combo.addItem("Cancelled", "Cancelled")
        self._status_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._status_combo)
        
        # Period filter
        period_label = QLabel("Period:")
        period_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(period_label)
        
        self._period_combo = QComboBox()
        self._period_combo.setStyleSheet(get_filter_combo_style())
        self._period_combo.addItem("All Time", "All Time")
        self._period_combo.addItem("Today", "Today")
        self._period_combo.addItem("This Week", "This Week")
        self._period_combo.addItem("This Month", "This Month")
        self._period_combo.addItem("This Year", "This Year")
        self._period_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._period_combo)
        
        # Amount filter
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(amount_label)
        
        self._amount_combo = QComboBox()
        self._amount_combo.setStyleSheet(get_filter_combo_style())
        self._amount_combo.addItem("All Amounts", "All Amounts")
        self._amount_combo.addItem("Under ₹10K", "Under ₹10K")
        self._amount_combo.addItem("₹10K - ₹50K", "₹10K - ₹50K")
        self._amount_combo.addItem("₹50K - ₹1L", "₹50K - ₹1L")
        self._amount_combo.addItem("Above ₹1L", "Above ₹1L")
        self._amount_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._amount_combo)
        
        # Supplier filter
        supplier_label = QLabel("Supplier:")
        supplier_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(supplier_label)
        
        self._supplier_combo = QComboBox()
        self._supplier_combo.setStyleSheet(get_filter_combo_style())
        self._supplier_combo.setMinimumWidth(120)
        self._supplier_combo.addItem("All Suppliers", "All Suppliers")
        self._supplier_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._supplier_combo)
        
        layout.addStretch()
        
        # Clear filters button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(32)
        clear_btn.setToolTip("Clear All Filters")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 13px;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                color: {DANGER};
            }}
        """)
        clear_btn.clicked.connect(self._on_clear_filters)
        layout.addWidget(clear_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Refresh Data")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(get_icon_button_style())
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh_btn)
        
        return container
    
    def _create_search_input(self) -> QFrame:
        """Create styled search input container."""
        container = QFrame()
        container.setObjectName("searchContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container.setMinimumWidth(200)
        container.setMaximumWidth(350)
        container.setFixedHeight(40)
        container.setStyleSheet(get_search_container_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)
        
        # Search icon
        icon = QLabel("🔍")
        icon.setStyleSheet("border: none; font-size: 14px;")
        layout.addWidget(icon)
        
        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search purchases...")
        self._search_input.setStyleSheet(get_search_input_style())
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)
        
        return container
    
    def _create_table_section(self) -> QWidget:
        """Create the purchases table."""
        frame = TableFrame()
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Table header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🛒 Purchase Invoice List")
        title_label.setFont(get_bold_font(16))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        header_layout.addWidget(title_label)
        
        self._count_label = QLabel("0 purchases")
        self._count_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                background: {BACKGROUND};
                padding: 6px 14px;
                border-radius: 16px;
                border: none;
            }}
        """)
        header_layout.addWidget(self._count_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Create table using common widget
        self._table = ListTable(headers=[
            "#", "Invoice No.", "Date", "Supplier", "Amount", "Status", "Actions"
        ])
        
        # Enable double-click to view
        self._table.itemDoubleClicked.connect(self._on_row_double_clicked)
        
        # Column configuration
        self._table.configure_columns([
            {"index": 0, "mode": "fixed", "width": 50},    # #
            {"index": 1, "mode": "fixed", "width": 120},   # Invoice No.
            {"index": 2, "mode": "fixed", "width": 100},   # Date
            {"index": 3, "mode": "stretch"},               # Supplier
            {"index": 4, "mode": "fixed", "width": 120},   # Amount
            {"index": 5, "mode": "fixed", "width": 100},   # Status
            {"index": 6, "mode": "fixed", "width": 150},   # Actions
        ])
        
        layout.addWidget(self._table)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self):
        """Load purchases from controller and update UI."""
        try:
            # Fetch all purchases
            self._all_purchases = self._controller.get_all_purchases()
            
            # Update supplier filter with available suppliers
            self._update_supplier_filter()
            
            # Apply current filters
            self._apply_filters()
            
        except Exception as e:
            self._show_error("Load Error", f"Failed to load purchases: {str(e)}")
    
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
    
    def _apply_filters(self):
        """Apply all current filters and update display."""
        search_text = self._get_search_text()
        status_filter = self._get_status_filter()
        period_filter = self._get_period_filter()
        amount_filter = self._get_amount_filter()
        supplier_filter = self._get_supplier_filter()
        
        # Filter purchases via controller
        filtered_purchases = self._controller.filter_purchases(
            purchases=self._all_purchases,
            search_text=search_text,
            status_filter=status_filter,
            period_filter=period_filter,
            amount_filter=amount_filter,
            supplier_filter=supplier_filter
        )
        
        # Update stats and table
        self._update_stats_display(filtered_purchases)
        self._populate_table(filtered_purchases)
    
    def _get_search_text(self) -> str:
        """Get current search text safely."""
        if hasattr(self, '_search_input'):
            return self._search_input.text().strip()
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
        self._count_label.setText(f"{stats.total} purchases")
    
    def _populate_table(self, purchases: list):
        """Populate table with purchase data."""
        self._table.setRowCount(0)
        
        for idx, purchase in enumerate(purchases):
            self._add_table_row(idx, purchase)
    
    def _add_table_row(self, idx: int, purchase: dict):
        """Add a single row to the table."""
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Row number
        num_item = QTableWidgetItem(str(idx + 1))
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
        self._apply_filters()
    
    def _on_filter_changed(self, index: int):
        """Handle filter combo change."""
        self._apply_filters()
    
    def _on_clear_filters(self):
        """Handle clear filters button click."""
        self._status_combo.setCurrentIndex(0)
        self._period_combo.setCurrentIndex(0)
        self._amount_combo.setCurrentIndex(0)
        self._supplier_combo.setCurrentIndex(0)
        self._search_input.clear()
        self._apply_filters()
    
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
        self._show_info("Export", "Export functionality will be implemented soon!")
    
    def _on_row_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on table row."""
        row = item.row()
        if row < len(self._all_purchases):
            # Get purchase from filtered view (need to apply filters again to match)
            filtered = self._controller.filter_purchases(
                purchases=self._all_purchases,
                search_text=self._get_search_text(),
                status_filter=self._get_status_filter(),
                period_filter=self._get_period_filter(),
                amount_filter=self._get_amount_filter(),
                supplier_filter=self._get_supplier_filter()
            )
            if row < len(filtered):
                self._open_purchase_readonly(filtered[row])
    
    def _on_view_clicked(self, purchase: dict):
        """Handle view button click - show print preview."""
        try:
            purchase_id = purchase.get('id')
            if not purchase_id:
                self._show_error("Error", "Invalid purchase data")
                return
            
            # Show print preview
            from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
            show_invoice_preview(self, purchase_id)
            
        except Exception as e:
            self._show_error("Error", f"Failed to view purchase: {str(e)}")
    
    def _on_delete_clicked(self, purchase: dict):
        """Handle delete button click with confirmation."""
        invoice_no = purchase.get('invoice_no', f"PUR-{purchase.get('id', 0):03d}")
        purchase_id = purchase.get('id')
        
        if not self._confirm_delete(invoice_no):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_purchase(purchase_id)
        
        if success:
            self._show_info("Success", f"Purchase invoice '{invoice_no}' deleted successfully!")
            self._load_data()
            self.purchase_updated.emit()
        else:
            self._show_error("Error", message)
    
    def _open_purchase_readonly(self, purchase: dict):
        """Open purchase dialog in read-only mode for viewing."""
        try:
            purchase_id = purchase.get('id')
            if not purchase_id:
                self._show_error("Error", "Invalid purchase data")
                return
            
            # Get full purchase data via controller
            purchase_data = self._controller.get_purchase_with_items(purchase_id)
            
            if not purchase_data:
                self._show_error("Error", f"Could not load purchase data for ID: {purchase_id}")
                return
            
            # Open PurchaseInvoiceDialog in read-only mode
            dialog = PurchaseInvoiceDialog(self, invoice_data=purchase_data, read_only=True)
            dialog.exec()
            
        except Exception as e:
            self._show_error("Error", f"Failed to open purchase: {str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Dialog Helpers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _confirm_delete(self, invoice_no: str) -> bool:
        """Show delete confirmation dialog."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{invoice_no}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def _show_info(self, title: str, message: str):
        """Show information message box."""
        QMessageBox.information(self, title, message)
    
    def _show_error(self, title: str, message: str):
        """Show error message box."""
        QMessageBox.critical(self, title, message)
    
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
