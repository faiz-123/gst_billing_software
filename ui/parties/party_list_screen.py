"""
Parties List Screen - Refactored to use global theme, widgets, services
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QComboBox, QFrame, QTableWidgetItem,
    QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

# Theme imports - use only available exports
from theme import (
    PRIMARY, WHITE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    SUCCESS, DANGER, WARNING, PURPLE,
    FONT_SIZE_SMALL, FONT_SIZE_NORMAL,
    get_normal_font, get_bold_font,
    get_filter_combo_style
)

# Widget imports
from widgets import (
    StatCard, ListTable, TableFrame, TableActionButton,
    SearchInputContainer, RefreshButton, ListHeader, StatsContainer
)

# Core imports
from core.enums import PartyType
from core.core_utils import format_currency
from core.services import party_service

# UI imports
from ui.base import BaseScreen
from ui.parties.party_form_dialog import PartyDialog


class PartiesScreen(BaseScreen):
    """Main screen for managing parties (customers and suppliers)"""
    
    party_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(title="Parties", parent=parent)
        self.setObjectName("PartiesScreen")
        self._setup_ui()
        self._load_parties()
    
    def _setup_ui(self):
        """Set up the main UI layout using BaseScreen's main_layout"""
        # Hide the default title label and content frame from BaseScreen
        self.title_label.hide()
        self.content_frame.hide()
        
        # Use the main_layout from BaseScreen
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Header section
        self.main_layout.addWidget(self._create_header())
        
        # Stats section
        self.main_layout.addWidget(self._create_stats_section())
        
        # Filters section
        self.main_layout.addWidget(self._create_filters_section())
        
        # Table section
        self.main_layout.addWidget(self._create_table_section(), 1)
    
    def _create_header(self) -> QWidget:
        """Create header with title and add button"""
        header = ListHeader("Parties", "+ Add Party")
        header.add_clicked.connect(self._on_add_party)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
    def _create_stats_section(self) -> QWidget:
        """Create statistics cards section with icons"""
        # Create stat cards with icons
        self.total_card = StatCard("👥", "Total Parties", "0", PRIMARY)
        self.customer_card = StatCard("🛒", "Customers", "0", SUCCESS)
        self.supplier_card = StatCard("🏭", "Suppliers", "0", PURPLE)
        self.receivable_card = StatCard("📈", "Total Receivable", "₹0", WARNING)
        self.payable_card = StatCard("📉", "Total Payable", "₹0", DANGER)
        
        return StatsContainer([
            self.total_card,
            self.customer_card,
            self.supplier_card,
            self.receivable_card,
            self.payable_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section with styled search"""
        filters_widget = QFrame()
        filters_widget.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        
        filters_layout = QHBoxLayout(filters_widget)
        filters_layout.setContentsMargins(16, 12, 16, 12)
        filters_layout.setSpacing(12)
        
        # Search container using common widget
        self._search_container = SearchInputContainer("Search by name, GSTIN, mobile...")
        self._search_container.textChanged.connect(self._force_upper_search)
        self._search_container.textChanged.connect(self._on_search_changed)
        filters_layout.addWidget(self._search_container)
        
        # Party type filter
        type_label = QLabel("Type:")
        type_label.setFont(get_normal_font())
        type_label.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        filters_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.setFont(get_normal_font())
        self.type_combo.setStyleSheet(get_filter_combo_style())
        self.type_combo.addItem("All Types", "all")
        self.type_combo.addItem("Customer", PartyType.CUSTOMER.value)
        self.type_combo.addItem("Supplier", PartyType.SUPPLIER.value)
        self.type_combo.addItem("Both", PartyType.BOTH.value)
        self.type_combo.currentIndexChanged.connect(self._on_filter_changed)
        filters_layout.addWidget(self.type_combo)
        
        # Balance type filter
        balance_label = QLabel("Balance:")
        balance_label.setFont(get_normal_font())
        balance_label.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        filters_layout.addWidget(balance_label)
        
        self.balance_combo = QComboBox()
        self.balance_combo.setFont(get_normal_font())
        self.balance_combo.setStyleSheet(get_filter_combo_style())
        self.balance_combo.addItem("All", "all")
        self.balance_combo.addItem("Receivable (Dr)", "dr")
        self.balance_combo.addItem("Payable (Cr)", "cr")
        self.balance_combo.currentIndexChanged.connect(self._on_filter_changed)
        filters_layout.addWidget(self.balance_combo)
        
        filters_layout.addStretch()
        
        # Refresh button using common widget
        refresh_btn = RefreshButton()
        refresh_btn.clicked.connect(self._load_parties)
        filters_layout.addWidget(refresh_btn)
        
        return filters_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the parties table with # column"""
        # Create table frame container
        table_frame = TableFrame()
        
        # Create table with headers
        self.table = ListTable(headers=[
            "#", "Name", "Type", "GSTIN", "Mobile", "Balance", "Balance Type", "Edit", "Delete"
        ])
        
        # Configure column widths
        self.table.configure_columns([
            {"width": 50, "resize": "fixed"},      # #
            {"resize": "stretch"},                  # Name
            {"width": 100, "resize": "fixed"},     # Type
            {"width": 160, "resize": "fixed"},     # GSTIN
            {"width": 120, "resize": "fixed"},     # Mobile
            {"width": 120, "resize": "fixed"},     # Balance
            {"width": 120, "resize": "fixed"},     # Balance Type (increased)
            {"width": 80, "resize": "fixed"},      # Edit
            {"width": 80, "resize": "fixed"},      # Delete (increased)
        ])
        
        table_frame.set_table(self.table)
        
        return table_frame
    
    def _load_parties(self):
        """Load parties from database and populate table"""
        try:
            # Get filter values
            search_text = self._search_container.text() if hasattr(self, '_search_container') else ""
            party_type = self.type_combo.currentData() if hasattr(self, 'type_combo') else "all"
            balance_type = self.balance_combo.currentData() if hasattr(self, 'balance_combo') else "all"
            
            # Get parties from service
            parties = party_service.get_parties()
            
            # Apply filters
            filtered_parties = self._apply_filters(parties, search_text, party_type, balance_type)
            
            # Update stats
            self._update_stats(parties)
            
            # Populate table
            self._populate_table(filtered_parties)
            
        except Exception as e:
            print(f"Error loading parties: {e}")
            self._show_error("Error", f"Failed to load parties: {str(e)}")
    
    def _apply_filters(self, parties: list, search_text: str, party_type: str, balance_type: str) -> list:
        """Apply filters to parties list"""
        filtered = parties
        
        # Search filter
        if search_text:
            search_lower = search_text.lower()
            filtered = [
                p for p in filtered
                if search_lower in (p.get('name') or '').lower()
                or search_lower in (p.get('gstin') or '').lower()
                or search_lower in (p.get('mobile') or '').lower()
            ]
        
        # Party type filter
        if party_type and party_type != "all":
            filtered = [
                p for p in filtered
                if (p.get('party_type') or '').lower() == party_type.lower()
            ]
        
        # Balance type filter
        if balance_type and balance_type != "all":
            filtered = [
                p for p in filtered
                if (p.get('balance_type') or '').lower() == balance_type.lower()
            ]
        
        return filtered
    
    def _update_stats(self, parties: list):
        """Update statistics cards"""
        total = len(parties)
        customers = len([p for p in parties if (p.get('party_type') or '').lower() == PartyType.CUSTOMER.value.lower()])
        suppliers = len([p for p in parties if (p.get('party_type') or '').lower() == PartyType.SUPPLIER.value.lower()])
        both = len([p for p in parties if (p.get('party_type') or '').lower() == PartyType.BOTH.value.lower()])
        
        # Calculate receivable and payable (dr = receivable, cr = payable)
        receivable = sum(
            float(p.get('opening_balance') or 0)
            for p in parties
            if (p.get('balance_type') or '').lower() == 'dr'
        )
        payable = sum(
            float(p.get('opening_balance') or 0)
            for p in parties
            if (p.get('balance_type') or '').lower() == 'cr'
        )
        
        # Update cards
        self.total_card.set_value(str(total))
        self.customer_card.set_value(str(customers + both))
        self.supplier_card.set_value(str(suppliers + both))
        self.receivable_card.set_value(format_currency(receivable))
        self.payable_card.set_value(format_currency(payable))
    
    def _populate_table(self, parties: list):
        """Populate table with party data"""
        self.table.setRowCount(0)
        
        for idx, party in enumerate(parties):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)
            
            # Column 0: Row number (#)
            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor(TEXT_SECONDARY))
            self.table.setItem(row, 0, num_item)
            
            # Column 1: Name with bold font (larger size)
            name_item = QTableWidgetItem(party.get('name', ''))
            name_item.setFont(get_bold_font(FONT_SIZE_NORMAL))
            name_item.setData(Qt.UserRole, party.get('id'))
            self.table.setItem(row, 1, name_item)
            
            # Column 2: Type
            party_type = party.get('party_type', '')
            type_item = QTableWidgetItem(party_type.title() if party_type else '')
            type_item.setFont(get_normal_font())
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, type_item)
            
            # Column 3: GSTIN
            gstin_item = QTableWidgetItem(party.get('gstin', '-') or '-')
            gstin_item.setFont(get_normal_font())
            self.table.setItem(row, 3, gstin_item)
            
            # Column 4: Mobile
            mobile_item = QTableWidgetItem(party.get('mobile', '-') or '-')
            mobile_item.setFont(get_normal_font())
            self.table.setItem(row, 4, mobile_item)
            
            # Column 5: Balance (centered)
            balance = float(party.get('opening_balance') or 0)
            balance_item = QTableWidgetItem(format_currency(balance))
            balance_item.setFont(get_bold_font(FONT_SIZE_SMALL))
            balance_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, balance_item)
            
            # Column 6: Balance Type
            balance_type = party.get('balance_type', '')
            balance_type_item = QTableWidgetItem(balance_type.upper() if balance_type else '-')
            balance_type_item.setFont(get_normal_font())
            balance_type_item.setTextAlignment(Qt.AlignCenter)
            if balance_type:
                if balance_type.lower() == 'dr':
                    balance_type_item.setForeground(QColor(WARNING))
                elif balance_type.lower() == 'cr':
                    balance_type_item.setForeground(QColor(DANGER))
            self.table.setItem(row, 6, balance_type_item)
            
            # Column 7: Edit button
            edit_btn = TableActionButton(
                text="Edit", tooltip="Edit Party",
                bg_color="#EEF2FF", hover_color=PRIMARY, size=(60, 32)
            )
            edit_btn.clicked.connect(lambda checked, p=party: self._on_edit_party(p))
            self.table.setCellWidget(row, 7, edit_btn)
            
            # Column 8: Delete button
            delete_btn = TableActionButton(
                text="Del", tooltip="Delete Party",
                bg_color="#FEE2E2", hover_color=DANGER, size=(60, 32)
            )
            delete_btn.clicked.connect(lambda checked, p=party: self._on_delete_party(p))
            self.table.setCellWidget(row, 8, delete_btn)
    
    def _force_upper_search(self, text: str):
        """Force search input to uppercase"""
        search_input = self._search_container._input
        cursor_pos = search_input.cursorPosition()
        search_input.blockSignals(True)
        search_input.setText(text.upper())
        search_input.setCursorPosition(cursor_pos)
        search_input.blockSignals(False)
    
    def _on_search_changed(self, text: str):
        """Handle search text change"""
        self._load_parties()
    
    def _on_filter_changed(self, index: int):
        """Handle filter change"""
        self._load_parties()
    
    def _on_add_party(self):
        """Show add party dialog"""
        dialog = PartyDialog(parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted or dialog.result_data:
            self._load_parties()
            self.party_updated.emit()
    
    def _on_edit_party(self, party: dict):
        """Show edit party dialog"""
        dialog = PartyDialog(party_data=party, parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted or dialog.result_data:
            self._load_parties()
            self.party_updated.emit()
    
    def _on_delete_party(self, party: dict):
        """Delete a party after confirmation"""
        party_name = party.get('name', 'Unknown')
        party_id = party.get('id')
        
        if not self._confirm_delete(party_name):
            return
        
        try:
            if party_service.delete_party(party_id):
                self._show_info("Success", f"Party '{party_name}' deleted successfully!")
                self._load_parties()
                self.party_updated.emit()
            else:
                self._show_error("Error", "Failed to delete party")
            
        except Exception as e:
            self._show_error("Error", f"Failed to delete party: {str(e)}")

    # ─────────────────────────────────────────────────────────────────────────
    # Dialog Helpers
    # ─────────────────────────────────────────────────────────────────────────
    
    def _confirm_delete(self, name: str) -> bool:
        """Show delete confirmation dialog."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?\n\nThis action cannot be undone.",
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

    def _on_export_clicked(self):
        """Handle export button click."""
        self._show_info(
            "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export party data to CSV or Excel."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────

    def refresh(self):
        """Public method to refresh the parties list"""
        self._load_parties()
