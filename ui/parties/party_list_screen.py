"""
Parties List Screen - Refactored to use global theme, widgets, services
Includes pagination, logging, company isolation, and performance optimizations
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QComboBox, QFrame, QTableWidgetItem,
    QMessageBox, QDialog, QSpinBox, QPushButton
)
from PySide6.QtCore import Qt, Signal, QTimer
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
from core.logger import get_logger

# Error handler import
from ui.error_handler import UIErrorHandler
from core.services import party_service

# UI imports
from ui.base import BaseScreen, PaginationWidget
from ui.parties.party_form_dialog import PartyDialog

logger = get_logger(__name__)


class PartiesScreen(BaseScreen):
    """Main screen for managing parties (customers and suppliers)"""
    
    party_updated = Signal()
    
    # Pagination constant
    ITEMS_PER_PAGE = 49  # Adjusted to match actual visible rows
    DEBOUNCE_DELAY = 500  # ms
    
    def __init__(self, parent=None):
        super().__init__(title="Parties", parent=parent)
        self.setObjectName("PartiesScreen")
        logger.debug("Initializing PartiesScreen")
        
        # Data caching
        self._all_parties = []
        self._filtered_parties = []
        self._is_loading = False
        
        # Pagination widget (will manage _current_page, _total_pages)
        self.pagination_widget = None
        
        # Debounce timer for search
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._on_search_debounce)
        
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
        
        # Table section (with stretching)
        self.main_layout.addWidget(self._create_table_section(), 1)
        
        # Pagination controls section
        self.main_layout.addWidget(self._create_pagination_controls())
    
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
        
        # Set tooltip for total card to clarify it shows ALL parties
        self.total_card.setToolTip("Total number of parties in the system (including all filtered results)")
        
        return StatsContainer([
            self.total_card,
            self.customer_card,
            self.supplier_card,
            self.receivable_card,
            self.payable_card
        ])
    
    def _create_filters_section(self) -> QWidget:
        """Create filters section with styled search and pagination"""
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
        refresh_btn.clicked.connect(lambda: self._load_parties(reset_page=True))
        filters_layout.addWidget(refresh_btn)
        
        return filters_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the parties table with pagination controls"""
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
    
    def _create_pagination_controls(self) -> QWidget:
        """Create pagination controls using the reusable PaginationWidget
        
        Returns:
            PaginationWidget for pagination controls
        """
        self.pagination_widget = PaginationWidget(
            items_per_page=self.ITEMS_PER_PAGE,
            entity_name="party",
            parent=self
        )
        
        # Connect signals
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        
        logger.debug("Pagination widget created and configured")
        return self.pagination_widget
    
    def _load_parties(self, reset_page: bool = False):
        """Load parties from database and populate table with pagination
        
        Args:
            reset_page: Reset to page 1 when called after filter change
        """
        if self._is_loading:
            logger.debug("Load already in progress, skipping")
            return
        
        try:
            self._is_loading = True
            logger.debug("Loading parties from database")
            
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            
            # Get filter values with validation
            search_text = self._get_safe_filter_value(self._search_container.text() if hasattr(self, '_search_container') else "")
            party_type = self.type_combo.currentData() if hasattr(self, 'type_combo') else "all"
            balance_type = self.balance_combo.currentData() if hasattr(self, 'balance_combo') else "all"
            
            # Get parties from service (all parties first for caching)
            self._all_parties = party_service.get_parties()
            logger.info(f"🔄 Fetched {len(self._all_parties)} TOTAL parties from database")
            
            if len(self._all_parties) == 0:
                logger.warning("⚠️  No parties returned from database!")
            
            # Apply filters
            self._filtered_parties = self._apply_filters(
                self._all_parties, 
                search_text, 
                party_type, 
                balance_type
            )
            logger.debug(f"🔍 After filtering: {len(self._filtered_parties)} parties (from {len(self._all_parties)} total)")
            
            # Calculate pagination (ALWAYS based on filtered count)
            total_pages = (len(self._filtered_parties) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            total_pages = max(1, total_pages)  # At least 1 page
            current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
            
            # Update pagination widget state
            if self.pagination_widget:
                self.pagination_widget.set_pagination_state(
                    current_page=current_page,
                    total_pages=total_pages,
                    total_items=len(self._filtered_parties)
                )
            
            # Update stats with ALL parties (NOT filtered - this is the key!)
            logger.info(f"📊 STATS: Showing stats for {len(self._all_parties)} TOTAL parties")
            logger.info(f"📊 PAGINATION: Showing page {current_page} of {total_pages} ({len(self._filtered_parties)} after filters)")
            self._update_stats(self._all_parties)
            
            # Populate table with current page (filtered data)
            page_data = self._get_current_page_data()
            logger.debug(f"📄 Populating table with {len(page_data)} parties for page {current_page}")
            self._populate_table(page_data)
            
            logger.info(f"Party list loaded successfully. Page {current_page}/{total_pages}")
            
        except Exception as e:
            logger.error(f"Error loading parties: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to load parties: {str(e)}")
        finally:
            self._is_loading = False
    
    def _apply_filters(self, parties: list, search_text: str, party_type: str, balance_type: str) -> list:
        """Apply filters to parties list with validation
        
        Args:
            parties: List of parties to filter
            search_text: Search text (name, GSTIN, mobile)
            party_type: Party type filter (Customer, Supplier, Both)
            balance_type: Balance type filter (Dr, Cr)
            
        Returns:
            Filtered list of parties
        """
        try:
            filtered = parties
            
            # Search filter with null-safety
            if search_text and search_text.strip():
                search_lower = search_text.lower().strip()
                filtered = [
                    p for p in filtered
                    if (search_lower in (str(p.get('name') or '')).lower()
                        or search_lower in (str(p.get('gstin') or '')).lower()
                        or search_lower in (str(p.get('mobile') or '')).lower())
                ]
                logger.debug(f"After search filter: {len(filtered)} parties")
            
            # Party type filter with validation
            if party_type and party_type != "all":
                try:
                    filtered = [
                        p for p in filtered
                        if (str(p.get('party_type') or '')).lower() == party_type.lower()
                    ]
                    logger.debug(f"After type filter ({party_type}): {len(filtered)} parties")
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error applying party type filter: {e}")
            
            # Balance type filter with validation
            if balance_type and balance_type != "all":
                try:
                    filtered = [
                        p for p in filtered
                        if (str(p.get('balance_type') or '')).lower() == balance_type.lower()
                    ]
                    logger.debug(f"After balance filter ({balance_type}): {len(filtered)} parties")
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error applying balance type filter: {e}")
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}", exc_info=True)
            return parties  # Return unfiltered list on error
    
    def _update_stats(self, parties: list):
        """Update statistics cards with error handling
        
        Args:
            parties: List of all parties (unfiltered for stats)
        """
        try:
            total = len(parties)
            logger.info(f"📊 _update_stats called with {total} parties")
            
            # Count party types with error handling
            customers = len([
                p for p in parties 
                if (str(p.get('party_type', '')).lower() in [PartyType.CUSTOMER.value.lower()])
            ])
            suppliers = len([
                p for p in parties 
                if (str(p.get('party_type', '')).lower() in [PartyType.SUPPLIER.value.lower()])
            ])
            both = len([
                p for p in parties 
                if (str(p.get('party_type', '')).lower() in [PartyType.BOTH.value.lower()])
            ])
            
            # Calculate receivable and payable with safe float conversion
            receivable = 0.0
            payable = 0.0
            
            for p in parties:
                try:
                    balance = float(p.get('opening_balance') or 0)
                    if str(p.get('balance_type', '')).lower() == 'dr':
                        receivable += balance
                    elif str(p.get('balance_type', '')).lower() == 'cr':
                        payable += balance
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error converting balance for party {p.get('id')}: {e}")
            
            # Update cards with validation
            self.total_card.set_value(str(total))
            self.customer_card.set_value(str(customers + both))
            self.supplier_card.set_value(str(suppliers + both))
            self.receivable_card.set_value(format_currency(receivable))
            self.payable_card.set_value(format_currency(payable))
            
            logger.info(f"✅ Stats updated successfully:")
            logger.info(f"   Total: {total}, Customers: {customers + both}, Suppliers: {suppliers + both}")
            logger.info(f"   Receivable: ₹{receivable}, Payable: ₹{payable}")
            
        except Exception as e:
            logger.error(f"Error updating stats: {str(e)}", exc_info=True)
    
    def _populate_table(self, parties: list):
        """Populate table with party data
        
        Args:
            parties: List of parties for current page (should be up to 49)
        """
        self.table.setRowCount(0)
        
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        # Calculate starting row number based on current page
        start_row_num = (current_page - 1) * self.ITEMS_PER_PAGE + 1
        
        logger.debug(f"Populating table with {len(parties)} parties, starting row num: {start_row_num}")
        
        for page_idx, party in enumerate(parties):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)
            
            # Calculate absolute row number across all pages
            absolute_row_num = start_row_num + page_idx
            
            # Column 0: Row number (#)
            num_item = QTableWidgetItem(str(absolute_row_num))
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
        
        logger.debug(f"Table populated with {self.table.rowCount()} rows")
    
    def _force_upper_search(self, text: str):
        """Force search input to uppercase"""
        try:
            search_input = self._search_container._input
            cursor_pos = search_input.cursorPosition()
            search_input.blockSignals(True)
            search_input.setText(text.upper())
            search_input.setCursorPosition(cursor_pos)
            search_input.blockSignals(False)
            logger.debug(f"Search text converted to uppercase: {text.upper()}")
        except Exception as e:
            logger.warning(f"Error forcing uppercase in search: {e}")
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debouncing
        
        Debouncing prevents excessive reload calls while user is typing
        """
        logger.debug(f"Search text changed: '{text}'")
        
        # Cancel previous timer
        self._search_debounce_timer.stop()
        
        # Start new debounce timer
        self._search_debounce_timer.start(self.DEBOUNCE_DELAY)
    
    def _on_search_debounce(self):
        """Execute search after debounce delay"""
        try:
            search_text = self._search_container.text() if hasattr(self, '_search_container') else ""
            logger.info(f"Search debounce triggered for: '{search_text}'")
            self._load_parties(reset_page=True)
        except Exception as e:
            logger.error(f"Error in search debounce: {str(e)}", exc_info=True)
    
    def _on_filter_changed(self, index: int):
        """Handle filter change with logging
        
        Args:
            index: The index of the changed filter combo (not used, for signal compatibility)
        """
        try:
            party_type = self.type_combo.currentData() if hasattr(self, 'type_combo') else "all"
            balance_type = self.balance_combo.currentData() if hasattr(self, 'balance_combo') else "all"
            logger.info(f"Filter changed - Type: {party_type}, Balance: {balance_type}")
            self._load_parties(reset_page=True)
        except Exception as e:
            logger.error(f"Error changing filter: {str(e)}", exc_info=True)
    
    def _on_pagination_page_changed(self, page: int):
        """Handle page change from pagination widget
        
        Args:
            page: The new page number
        """
        try:
            logger.info(f"Pagination page changed to {page}")
            page_data = self._get_current_page_data()
            self._populate_table(page_data)
        except Exception as e:
            logger.error(f"Error handling pagination page change: {str(e)}", exc_info=True)
    
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
        """Delete a party after confirmation and validation
        
        Checks for:
        - Confirmation from user
        - Transaction rollback on failure
        """
        party_name = party.get('name', 'Unknown')
        party_id = party.get('id')
        
        try:
            # Validate party exists
            if not party_id:
                logger.warning(f"Attempt to delete party with no ID")
                UIErrorHandler.show_error("Error", "Invalid party selected")
                return
            
            # Check for related invoices/transactions if method exists
            related_invoices = 0
            if hasattr(party_service, 'get_party_invoice_count'):
                related_invoices = party_service.get_party_invoice_count(party_id)
            
            if related_invoices and related_invoices > 0:
                logger.warning(f"Attempt to delete party {party_id} with {related_invoices} invoices")
                UIErrorHandler.show_warning(
                    "Cannot Delete",
                    f"Party '{party_name}' has {related_invoices} associated invoice(s).\n\n"
                    "Please delete all related invoices first or archive this party."
                )
                return
            
            # Confirmation from user
            if not UIErrorHandler.ask_confirmation(
                "Confirm Delete",
                f"Are you sure you want to delete '{party_name}'?\n\n"
                f"Balance: {format_currency(float(party.get('opening_balance') or 0))}\n\n"
                f"This action cannot be undone."
            ):
                logger.debug(f"Delete cancelled by user for party {party_id}")
                return
            
            # Attempt deletion
            logger.info(f"Deleting party {party_id} ({party_name})")
            if party_service.delete_party(party_id):
                logger.info(f"Party {party_id} deleted successfully")
                UIErrorHandler.show_success("Success", f"Party '{party_name}' deleted successfully!")
                self._load_parties(reset_page=True)
                self.party_updated.emit()
            else:
                logger.error(f"Failed to delete party {party_id}")
                UIErrorHandler.show_error("Error", "Failed to delete party. Please try again.")
            
        except Exception as e:
            logger.error(f"Error deleting party {party.get('id')}: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to delete party: {str(e)}")

    def _on_export_clicked(self):
        """Handle export button click."""
        logger.info("Export clicked")
        UIErrorHandler.show_warning(
            "Export", 
            "📤 Export functionality will be available soon!\n\n"
            "This will allow you to export party data to CSV or Excel."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Pagination & Helper Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_current_page_data(self) -> list:
        """Get parties for current page
        
        Returns:
            List of parties for current page
        """
        if not self.pagination_widget:
            return self._filtered_parties
        
        current_page = self.pagination_widget.get_current_page()
        start_idx = (current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        return self._filtered_parties[start_idx:end_idx]
    
    def _get_safe_filter_value(self, value: str) -> str:
        """Safely get filter value with null/empty checks
        
        Args:
            value: Filter value to validate
            
        Returns:
            Safe filter value (empty string if None/invalid)
        """
        try:
            return str(value or "").strip() if value else ""
        except Exception as e:
            logger.warning(f"Error getting safe filter value: {e}")
            return ""
    
    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────

    def refresh(self):
        """Public method to refresh the parties list"""
        logger.info("Manual refresh triggered")
        self._load_parties(reset_page=True)
