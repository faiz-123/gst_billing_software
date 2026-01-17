"""
Sales Invoice List Screen
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
from controllers.invoice_controller import invoice_controller

# Core imports for formatting only
from core.core_utils import format_currency

# UI imports
from ui.base import BaseScreen
from ui.invoices.sales.sales_invoice_form_dialog import InvoiceDialog


class InvoicesScreen(BaseScreen):
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
        self._all_invoices = []
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
        title = QLabel("Sales Invoices")
        title.setFont(get_title_font())
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Export button
        export_btn = CustomButton("📤 Export", "secondary")
        export_btn.setFixedWidth(120)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(export_btn)
        
        # Add button
        add_btn = CustomButton("+ New Invoice", "primary")
        add_btn.setFixedWidth(160)
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
        
        # Create stat cards
        self._total_card = StatCard("📋", "Total Invoices", "0", PRIMARY)
        self._amount_card = StatCard("💰", "Total Revenue", "₹0", SUCCESS)
        self._overdue_card = StatCard("⏰", "Overdue", "0", DANGER)
        self._paid_card = StatCard("✅", "Paid", "0", "#10B981")
        
        layout.addWidget(self._total_card)
        layout.addWidget(self._amount_card)
        layout.addWidget(self._overdue_card)
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
        self._status_combo.addItem("Unpaid", "Unpaid")
        self._status_combo.addItem("Partially Paid", "Partially Paid")
        self._status_combo.addItem("Paid", "Paid")
        self._status_combo.addItem("Overdue", "Overdue")
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
        
        # Party filter
        party_label = QLabel("Party:")
        party_label.setStyleSheet(get_filter_label_style())
        layout.addWidget(party_label)
        
        self._party_combo = QComboBox()
        self._party_combo.setStyleSheet(get_filter_combo_style())
        self._party_combo.setMinimumWidth(120)
        self._party_combo.addItem("All Parties", "All Parties")
        self._party_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._party_combo)
        
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
        self._search_input.setPlaceholderText("Search invoices...")
        self._search_input.setStyleSheet(get_search_input_style())
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)
        
        return container
    
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
        
        frame.set_table(self._table)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Data Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self):
        """Load invoices from controller and update UI."""
        try:
            # Fetch all invoices
            self._all_invoices = self._controller.get_all_invoices()
            
            # Update party filter with available parties
            self._update_party_filter()
            
            # Apply current filters
            self._apply_filters()
            
        except Exception as e:
            self._show_error("Load Error", f"Failed to load invoices: {str(e)}")
    
    def _update_party_filter(self):
        """Update party dropdown with available parties."""
        parties = self._controller.extract_party_names(self._all_invoices)
        
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
    
    def _apply_filters(self):
        """Apply all current filters and update display."""
        search_text = self._get_search_text()
        status_filter = self._get_status_filter()
        period_filter = self._get_period_filter()
        amount_filter = self._get_amount_filter()
        party_filter = self._get_party_filter()
        
        # Filter invoices via controller
        filtered_invoices = self._controller.filter_invoices(
            invoices=self._all_invoices,
            search_text=search_text,
            status_filter=status_filter,
            period_filter=period_filter,
            amount_filter=amount_filter,
            party_filter=party_filter
        )
        
        # Update stats and table
        self._update_stats_display(filtered_invoices)
        self._populate_table(filtered_invoices)
    
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
    
    def _get_party_filter(self) -> str:
        """Get current party filter value."""
        if hasattr(self, '_party_combo'):
            return self._party_combo.currentData() or "All Parties"
        return "All Parties"
    
    def _update_stats_display(self, invoices: list):
        """Update statistics cards with data from controller."""
        stats = self._controller.calculate_stats(invoices)
        self._total_card.set_value(str(stats.total))
        self._amount_card.set_value(f"₹{stats.total_amount:,.0f}")
        self._overdue_card.set_value(str(stats.overdue_count))
        self._paid_card.set_value(str(stats.paid_count))
    
    def _populate_table(self, invoices: list):
        """Populate table with invoice data."""
        self._table.setRowCount(0)
        
        for idx, invoice in enumerate(invoices):
            self._add_table_row(idx, invoice)
    
    def _add_table_row(self, idx: int, invoice: dict):
        """Add a single row to the table."""
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 50)
        
        # Column 0: Row number
        num_item = QTableWidgetItem(str(idx + 1))
        num_item.setTextAlignment(Qt.AlignCenter)
        num_item.setForeground(QColor(TEXT_SECONDARY))
        self._table.setItem(row, 0, num_item)
        
        # Column 1: Invoice No. (stores invoice ID in UserRole)
        invoice_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        invoice_item = QTableWidgetItem(invoice_no)
        invoice_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        invoice_item.setForeground(QColor(PRIMARY))
        invoice_item.setData(Qt.UserRole, invoice.get('id'))
        self._table.setItem(row, 1, invoice_item)
        
        # Column 2: Date
        date_item = QTableWidgetItem(str(invoice.get('date', '')))
        date_item.setFont(get_normal_font())
        self._table.setItem(row, 2, date_item)
        
        # Column 3: Party
        party_item = QTableWidgetItem(invoice.get('party_name', 'Unknown'))
        party_item.setFont(get_normal_font())
        self._table.setItem(row, 3, party_item)
        
        # Column 4: Amount
        amount = float(invoice.get('grand_total', 0) or 0)
        amount_item = QTableWidgetItem(format_currency(amount))
        amount_item.setFont(get_bold_font(FONT_SIZE_SMALL))
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._table.setItem(row, 4, amount_item)
        
        # Column 5: Status with color
        status = invoice.get('status', 'Unpaid')
        status_widget = self._create_status_cell(status)
        self._table.setCellWidget(row, 5, status_widget)
        
        # Column 6: Actions
        actions_widget = self._create_action_buttons(invoice)
        self._table.setCellWidget(row, 6, actions_widget)
    
    def _create_status_cell(self, status: str) -> QWidget:
        """Create status cell with colored badge."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignCenter)
        
        text_color, bg_color = self._controller.get_invoice_status_color(status)
        
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
    
    def _create_action_buttons(self, invoice: dict) -> QWidget:
        """Create action buttons for table row."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # View PDF button
        view_btn = TableActionButton(
            text="View",
            tooltip="View Invoice",
            bg_color="#EEF2FF",
            hover_color=PRIMARY,
            size=(60, 32)
        )
        view_btn.clicked.connect(lambda checked, inv=invoice: self._on_view_clicked(inv))
        layout.addWidget(view_btn)
        
        # Delete button
        del_btn = TableActionButton(
            text="Del",
            tooltip="Delete Invoice",
            bg_color="#FEE2E2",
            hover_color=DANGER,
            size=(50, 32)
        )
        del_btn.clicked.connect(lambda checked, inv=invoice: self._on_delete_clicked(inv))
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
        self._party_combo.setCurrentIndex(0)
        self._search_input.clear()
        self._apply_filters()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._load_data()
    
    def _on_add_clicked(self):
        """Handle add invoice button click."""
        dialog = InvoiceDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.invoice_updated.emit()
    
    def _on_export_clicked(self):
        """Handle export button click."""
        self._show_info("Export", "Export functionality will be implemented soon!")
    
    def _on_row_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on table row."""
        row = item.row()
        if row < len(self._all_invoices):
            # Get invoice from filtered view (need to apply filters again to match)
            filtered = self._controller.filter_invoices(
                invoices=self._all_invoices,
                search_text=self._get_search_text(),
                status_filter=self._get_status_filter(),
                period_filter=self._get_period_filter(),
                amount_filter=self._get_amount_filter(),
                party_filter=self._get_party_filter()
            )
            if row < len(filtered):
                self._open_invoice_readonly(filtered[row])
    
    def _on_view_clicked(self, invoice: dict):
        """Handle view button click - show print preview."""
        try:
            invoice_id = invoice.get('id')
            if not invoice_id:
                self._show_error("Error", "Invalid invoice data")
                return
            
            # Show print preview
            from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
            show_invoice_preview(self, invoice_id)
            
        except Exception as e:
            self._show_error("Error", f"Failed to view invoice: {str(e)}")
    
    def _on_delete_clicked(self, invoice: dict):
        """Handle delete button click with confirmation."""
        invoice_no = invoice.get('invoice_no', f"INV-{invoice.get('id', 0):03d}")
        invoice_id = invoice.get('id')
        
        if not self._confirm_delete(invoice_no):
            return
        
        # Delegate to controller
        success, message = self._controller.delete_invoice(invoice_id)
        
        if success:
            self._show_info("Success", f"Invoice '{invoice_no}' deleted successfully!")
            self._load_data()
            self.invoice_updated.emit()
        else:
            self._show_error("Error", message)
    
    def _open_invoice_readonly(self, invoice: dict):
        """Open invoice dialog in read-only mode for viewing."""
        try:
            invoice_id = invoice.get('id')
            if not invoice_id:
                self._show_error("Error", "Invalid invoice data")
                return
            
            # Get full invoice data via controller
            invoice_data = self._controller.get_invoice_with_items(invoice_id)
            
            if not invoice_data:
                self._show_error("Error", f"Could not load invoice data for ID: {invoice_id}")
                return
            
            # Open InvoiceDialog in read-only mode
            dialog = InvoiceDialog(self, invoice_data=invoice_data, read_only=True)
            dialog.exec()
            
        except Exception as e:
            self._show_error("Error", f"Failed to open invoice: {str(e)}")
    
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
        """Public method to refresh the invoices list."""
        self._load_data()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible."""
        super().showEvent(event)
        self._load_data()
