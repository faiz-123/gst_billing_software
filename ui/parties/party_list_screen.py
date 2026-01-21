"""
Parties List Screen - Refactored to inherit from BaseListScreen
Uses common list patterns: pagination, filtering, table population, error handling
"""

from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtCore import Qt, Signal

# Theme imports
from theme import PRIMARY, SUCCESS, DANGER, WARNING, PURPLE, PRIMARY_LIGHT, DANGER_LIGHT

# Widget imports
from widgets import StatCard, ListTable, TableFrame, StatsContainer, FilterWidget

# Core imports
from core.enums import PartyType
from core.core_utils import format_currency
from core.logger import get_logger

# Error handler import
from ui.error_handler import UIErrorHandler

# Controller import (NOT service or db directly)
from controllers.party_controller import party_controller

# UI imports - inherit from BaseListScreen
from ui.base.base_list_screen import BaseListScreen
from ui.base.list_table_helper import ListTableHelper
from ui.parties.party_form_dialog import PartyDialog

logger = get_logger(__name__)


class PartiesScreen(BaseListScreen):
    """Main screen for managing parties (customers and suppliers)
    
    Inherits from BaseListScreen which provides:
    - Standard UI layout (_setup_ui)
    - Generic data loading pattern (_load_data)
    - Pagination support
    - Search debouncing
    - Error handling
    """
    
    party_updated = Signal()
    
    def __init__(self, parent=None):
        # Initialize base class - this calls _setup_ui() automatically
        super().__init__(title="Parties", parent=parent)
        self.setObjectName("PartiesScreen")
    
    # ─────────────────────────────────────────────────────────────────────────
    # BaseListScreen Configuration Overrides
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_add_button_text(self) -> str:
        """Return text for add button"""
        return "+ Add Party"
    
    def _get_entity_name(self) -> str:
        """Return singular entity name for pagination"""
        return "party"
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI Section Overrides (Required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
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
        """Create filters section using FilterWidget for consistency"""
        self._filter_widget = FilterWidget()
        
        # Search filter - with uppercase conversion
        search_input = self._filter_widget.add_search_filter("Search by name, GSTIN, mobile...")
        search_input.textChanged.connect(self._force_upper_search)
        self._filter_widget.search_changed.connect(self._on_search_changed)
        
        # Party type filter
        type_options = {
            "All Types": "all",
            "Customer": PartyType.CUSTOMER.value,
            "Supplier": PartyType.SUPPLIER.value,
            "Both": PartyType.BOTH.value
        }
        self.type_combo = self._filter_widget.add_combo_filter("type", "Type:", type_options)
        
        # Balance type filter
        balance_options = {
            "All": "all",
            "Receivable (Dr)": "dr",
            "Payable (Cr)": "cr"
        }
        self.balance_combo = self._filter_widget.add_combo_filter("balance", "Balance:", balance_options)
        
        # Stretch and refresh button
        self._filter_widget.add_stretch()
        self._filter_widget.add_refresh_button(self._on_refresh_clicked)
        
        # Connect filter changes
        self._filter_widget.filters_changed.connect(self._on_filter_changed)
        
        return self._filter_widget
    
    def _create_table_section(self) -> QWidget:
        """Create the parties table with pagination controls"""
        # Create table frame container
        table_frame = TableFrame()
        
        # Create table with headers (use _table for consistency with other screens)
        self._table = ListTable(headers=[
            "#", "Name", "Type", "GSTIN", "Mobile", "Balance", "Balance Type", "Edit", "Delete"
        ])
        
        # Configure column widths
        self._table.configure_columns([
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
        
        # Initialize ListTableHelper for populating the table
        self._table_helper = ListTableHelper(self._table, self.ITEMS_PER_PAGE)
        
        # Define column configurations for table population
        self._column_configs = [
            {'type': 'row_number'},
            {'key': 'name', 'type': 'text', 'bold': True, 'align': Qt.AlignLeft},
            {'key': 'party_type', 'type': 'text', 'align': Qt.AlignCenter, 
             'formatter': lambda v: v.title() if v else ''},
            {'key': 'gstin', 'type': 'text', 'formatter': lambda v: v or '-'},
            {'key': 'mobile', 'type': 'text', 'formatter': lambda v: v or '-'},
            {'key': 'opening_balance', 'type': 'currency', 'bold': True, 'align': Qt.AlignCenter},
            {'key': 'balance_type', 'type': 'balance_type', 'align': Qt.AlignCenter,
             'formatter': lambda v: v.upper() if v else '-'},
            {'type': 'button', 'text': 'Edit', 'tooltip': 'Edit Party',
             'bg_color': PRIMARY_LIGHT, 'hover_color': PRIMARY, 'size': (60, 32)},
            {'type': 'button', 'text': 'Del', 'tooltip': 'Delete Party',
             'bg_color': DANGER_LIGHT, 'hover_color': DANGER, 'size': (60, 32)},
        ]
        
        table_frame.set_table(self._table)
        
        return table_frame
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading Overrides (Required by BaseListScreen)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _fetch_all_data(self) -> list:
        """Fetch all parties from controller
        
        Returns:
            List of all parties
        """
        return party_controller.get_all_parties()
    
    def filter_data(self, all_data: list) -> list:
        """Apply filters to parties list
        
        Args:
            all_data: List of all parties
            
        Returns:
            Filtered list of parties
        """
        search_text = self.get_safe_filter_value(
            self._filter_widget.get_search_text() if hasattr(self, '_filter_widget') else ""
        )
        party_type = self.type_combo.currentData() if hasattr(self, 'type_combo') else "all"
        balance_type = self.balance_combo.currentData() if hasattr(self, 'balance_combo') else "all"
        
        return self._apply_filters(all_data, search_text, party_type, balance_type)
    
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
        """Populate table with party data using ListTableHelper
        
        Args:
            parties: List of parties for current page (should be up to 49)
        """
        # Get current page from pagination widget
        current_page = self.pagination_widget.get_current_page() if self.pagination_widget else 1
        
        logger.debug(f"Populating table with {len(parties)} parties using ListTableHelper")
        
        # Use ListTableHelper to populate the table
        self._table_helper.populate(
            data=parties,
            column_configs=self._column_configs,
            current_page=current_page
        )
        
        # Connect button click handlers for each row
        for row in range(self._table.rowCount()):
            party = parties[row] if row < len(parties) else None
            if party:
                # Edit button (column 7)
                edit_btn = self._table.cellWidget(row, 7)
                if edit_btn:
                    edit_btn.clicked.connect(lambda checked, p=party: self._on_edit_party(p))
                
                # Delete button (column 8)
                delete_btn = self._table.cellWidget(row, 8)
                if delete_btn:
                    delete_btn.clicked.connect(lambda checked, p=party: self._on_delete_party(p))
        
        logger.debug(f"Table populated with {self._table.rowCount()} rows")
    
    def _force_upper_search(self, text: str):
        """Force search input to uppercase"""
        try:
            # Get the actual input field from the search container returned by FilterWidget
            search_input = self._filter_widget.get_filter("search")
            if hasattr(search_input, '_input'):  # SearchInputContainer has _input attribute
                cursor_pos = search_input._input.cursorPosition()
                search_input._input.blockSignals(True)
                search_input._input.setText(text.upper())
                search_input._input.setCursorPosition(cursor_pos)
                search_input._input.blockSignals(False)
                logger.debug(f"Search text converted to uppercase: {text.upper()}")
        except Exception as e:
            logger.warning(f"Error forcing uppercase in search: {e}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handler Overrides
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_add_clicked(self):
        """Show add party dialog - overrides BaseListScreen"""
        dialog = PartyDialog(parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted or dialog.result_data:
            self._load_data()
            self.party_updated.emit()
    
    def _on_edit_party(self, party: dict):
        """Show edit party dialog"""
        dialog = PartyDialog(party_data=party, parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted or dialog.result_data:
            self._load_data()
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
            if hasattr(party_controller, 'get_party_invoice_count'):
                related_invoices = party_controller.get_party_invoice_count(party_id)
            
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
            
            # Attempt deletion via controller
            logger.info(f"Deleting party {party_id} ({party_name})")
            success, message = party_controller.delete_party(party_id)
            if success:
                logger.info(f"Party {party_id} deleted successfully")
                UIErrorHandler.show_success("Success", f"Party '{party_name}' deleted successfully!")
                self._load_data(reset_page=True)
                self.party_updated.emit()
            else:
                logger.error(f"Failed to delete party {party_id}: {message}")
                UIErrorHandler.show_error("Error", message or "Failed to delete party. Please try again.")
            
        except Exception as e:
            logger.error(f"Error deleting party {party.get('id')}: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to delete party: {str(e)}")
