"""
BaseListScreen - Generic list screen base class
Provides common functionality for all list-based screens (parties, products, invoices, etc.)

Architecture: Encapsulates common patterns to eliminate duplication across 6 list screens
Pattern: Template Method - subclasses override specific sections

Features:
- Common UI layout (header, stats, filters, table)
- Generic data loading with error handling
- Pagination support (via PaginationWidget)
- Loading state management
- Consistent signal emissions
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor

from theme import (
    PRIMARY, WHITE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    get_normal_font
)

from core.logger import get_logger
from ui.base.base_screen import BaseScreen
from ui.base.pagination_widget import PaginationWidget
from ui.error_handler import UIErrorHandler
from widgets import RefreshButton

logger = get_logger(__name__)


class BaseListScreen(BaseScreen):
    """
    Generic base class for all list screens (parties, products, invoices, etc.)
    
    Provides:
    - Common UI structure and layout
    - Generic data loading pattern
    - Pagination widget integration
    - Loading state management
    - Error handling
    
    Subclasses must override:
    - _create_stats_section() - Define stat cards
    - _create_filters_section() - Define filters
    - _create_table_section() - Define table columns
    - filter_data(all_data) - Apply filters to data
    - get_stats(all_data) - Calculate statistics
    """
    
    # Common signal for data changes
    data_updated = Signal()
    
    # Configuration (set by subclass in __init__)
    ITEMS_PER_PAGE = 49  # Default pagination size
    DEBOUNCE_DELAY = 500  # ms - for search debouncing
    
    def __init__(self, title: str, parent=None):
        """
        Initialize base list screen
        
        Args:
            title: Screen title (e.g., "Parties", "Products", "Invoices")
            parent: Parent widget
        """
        super().__init__(title=title, parent=parent)
        
        # State management
        self._is_loading = False
        self._all_data = []
        self._filtered_data = []
        self.pagination_widget = None
        
        # Search debounce timer
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._on_search_debounce)
        
        logger.debug(f"Initializing {self.__class__.__name__}")
        
        # Setup UI (standard layout for all screens)
        self._setup_ui()
    
    def showEvent(self, event):
        """Refresh data when screen becomes visible - common for all list screens."""
        super().showEvent(event)
        self._load_data()
    
    def _setup_ui(self):
        """
        Set up the standard UI layout - IDENTICAL for all list screens
        
        Layout order:
        1. Header (title + buttons)
        2. Stats section (stat cards)
        3. Filters section (search + dropdowns)
        4. Table section (main list)
        5. Pagination controls
        """
        # Hide default BaseScreen elements
        self.title_label.hide()
        self.content_frame.hide()
        
        # Configure main layout
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Add UI sections in standard order
        self.main_layout.addWidget(self._create_header())
        self.main_layout.addWidget(self._create_stats_section())
        self.main_layout.addWidget(self._create_filters_section())
        self.main_layout.addWidget(self._create_table_section(), 1)  # Stretch table
        self.main_layout.addWidget(self._create_pagination_controls())
        
        logger.debug(f"UI setup completed for {self.__class__.__name__}")
    
    def _create_header(self) -> QWidget:
        """
        Create header with title and action buttons
        
        Subclasses can override to customize header
        Returns:
            QWidget header container
        """
        from widgets import ListHeader
        
        header = ListHeader(self.title, self._get_add_button_text())
        header.add_clicked.connect(self._on_add_clicked)
        header.export_clicked.connect(self._on_export_clicked)
        return header
    
    def _get_add_button_text(self) -> str:
        """Get text for add button - override in subclass if needed"""
        return "+ Add"
    
    def _create_stats_section(self) -> QWidget:
        """
        Create statistics section with stat cards
        
        MUST BE OVERRIDDEN by subclass
        Should return QWidget with StatCard widgets
        """
        raise NotImplementedError("Subclass must implement _create_stats_section()")
    
    def _create_filters_section(self) -> QWidget:
        """
        Create filters section with search and dropdowns
        
        MUST BE OVERRIDDEN by subclass
        Should return QWidget with SearchInputContainer and filter dropdowns
        """
        raise NotImplementedError("Subclass must implement _create_filters_section()")
    
    def _create_table_section(self) -> QWidget:
        """
        Create table section with ListTable
        
        MUST BE OVERRIDDEN by subclass
        Should return QWidget with configured ListTable
        """
        raise NotImplementedError("Subclass must implement _create_table_section()")
    
    def _create_pagination_controls(self) -> QWidget:
        """
        Create pagination controls using PaginationWidget
        
        Can be overridden for custom pagination
        Returns:
            PaginationWidget
        """
        self.pagination_widget = PaginationWidget(
            items_per_page=self.ITEMS_PER_PAGE,
            entity_name=self._get_entity_name(),
            parent=self
        )
        
        # Connect pagination signal
        self.pagination_widget.page_changed.connect(self._on_pagination_page_changed)
        
        logger.debug("Pagination widget created")
        return self.pagination_widget
    
    def _get_entity_name(self) -> str:
        """Get singular entity name (e.g., 'party', 'product', 'invoice')"""
        return "item"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading and Filtering - Generic Implementation
    # ─────────────────────────────────────────────────────────────────────────
    
    def _load_data(self, reset_page: bool = False):
        """
        Generic data loading pattern with error handling
        
        Flow:
        1. Check if already loading
        2. Fetch all data from controller/service
        3. Apply filters
        4. Update pagination state
        5. Update stats
        6. Populate table
        7. Handle errors gracefully
        
        Args:
            reset_page: Reset to page 1 when called after filter change
        """
        if self._is_loading:
            logger.debug("Load already in progress, skipping")
            return
        
        try:
            self._is_loading = True
            logger.debug(f"Loading data for {self.__class__.__name__}")
            
            # Reset to page 1 if requested
            if reset_page and self.pagination_widget:
                self.pagination_widget.reset_to_page_one()
            
            # Fetch all data (subclass responsibility via service/controller)
            self._all_data = self._fetch_all_data()
            logger.info(f"🔄 Fetched {len(self._all_data)} TOTAL items")
            
            if len(self._all_data) == 0:
                logger.warning("⚠️  No data returned from database!")
            
            # Apply filters
            self._filtered_data = self.filter_data(self._all_data)
            logger.debug(f"🔍 After filtering: {len(self._filtered_data)} items (from {len(self._all_data)} total)")
            
            # Calculate and update pagination
            self._update_pagination(reset_page)
            
            # Update stats with ALL data (not filtered)
            logger.info(f"📊 STATS: Showing stats for {len(self._all_data)} TOTAL items")
            self._update_stats(self._all_data)
            
            # Populate table with current page data
            page_data = self._get_current_page_data()
            logger.debug(f"📄 Populating table with {len(page_data)} items for page")
            self._populate_table(page_data)
            
            logger.info(f"Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}", exc_info=True)
            UIErrorHandler.show_error("Error", f"Failed to load data: {str(e)}")
        finally:
            self._is_loading = False
    
    def _fetch_all_data(self) -> list:
        """
        Fetch all data from service/controller
        
        MUST BE OVERRIDDEN by subclass
        Returns:
            List of all data items
        """
        raise NotImplementedError("Subclass must implement _fetch_all_data()")
    
    def filter_data(self, all_data: list) -> list:
        """
        Apply filters to data
        
        MUST BE OVERRIDDEN by subclass
        Args:
            all_data: Unfiltered data list
            
        Returns:
            Filtered data list
        """
        raise NotImplementedError("Subclass must implement filter_data()")
    
    def _update_pagination(self, reset_page: bool = False):
        """
        Update pagination widget state
        
        Args:
            reset_page: Whether page was reset
        """
        if not self.pagination_widget:
            return
        
        # Calculate pagination based on filtered data
        total_pages = max(1, (len(self._filtered_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        current_page = 1 if reset_page else self.pagination_widget.get_current_page()
        
        # Update widget state
        self.pagination_widget.set_pagination_state(
            current_page=current_page,
            total_pages=total_pages,
            total_items=len(self._filtered_data)
        )
        
        logger.debug(f"Pagination updated: Page {current_page}/{total_pages}")
    
    def _get_stats(self) -> dict:
        """
        Get statistics from all data
        
        MUST BE OVERRIDDEN by subclass
        Should call self._update_stats() internally
        Returns:
            Dict with stat values
        """
        raise NotImplementedError("Subclass must implement _get_stats()")
    
    def _update_stats(self, all_data: list):
        """
        Update statistics display
        
        MUST BE OVERRIDDEN by subclass
        Args:
            all_data: All items for calculation (not filtered)
        """
        raise NotImplementedError("Subclass must implement _update_stats()")
    
    def _populate_table(self, data: list):
        """
        Populate table with data
        
        MUST BE OVERRIDDEN by subclass
        Args:
            data: Data for current page only
        """
        raise NotImplementedError("Subclass must implement _populate_table()")
    
    def _get_current_page_data(self) -> list:
        """
        Get data for current page
        
        Returns:
            Slice of filtered data for current page
        """
        if not self.pagination_widget:
            return self._filtered_data
        
        current_page = self.pagination_widget.get_current_page()
        start_idx = (current_page - 1) * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        return self._filtered_data[start_idx:end_idx]
    
    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers - Common Signal Slots
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debouncing"""
        logger.debug(f"Search text changed: '{text}'")
        
        # Cancel previous timer
        self._search_debounce_timer.stop()
        
        # Start new debounce timer
        self._search_debounce_timer.start(self.DEBOUNCE_DELAY)
    
    def _on_search_debounce(self):
        """Execute search after debounce delay"""
        try:
            logger.info(f"Search debounce triggered")
            self._load_data(reset_page=True)
        except Exception as e:
            logger.error(f"Error in search debounce: {str(e)}", exc_info=True)
    
    def _on_filter_changed(self, *args):
        """Handle filter change - reload data
        
        Args:
            *args: Accept any arguments from signal (combo index, date, etc.)
        """
        try:
            logger.info(f"Filter changed")
            self._load_data(reset_page=True)
        except Exception as e:
            logger.error(f"Error changing filter: {str(e)}", exc_info=True)
    
    def _on_pagination_page_changed(self, page: int):
        """Handle pagination page change"""
        try:
            logger.info(f"Page changed to {page}")
            page_data = self._get_current_page_data()
            self._populate_table(page_data)
        except Exception as e:
            logger.error(f"Error handling page change: {str(e)}", exc_info=True)
    
    def _on_add_clicked(self):
        """Handle add button click - override in subclass"""
        logger.info("Add button clicked")
    
    def _on_export_clicked(self):
        """Handle export button click - override in subclass"""
        logger.info("Export button clicked")
        UIErrorHandler.show_warning(
            "Export",
            "📤 Export functionality will be available soon!"
        )
    
    def _on_refresh_clicked(self):
        """Handle refresh button click - clears filters and reloads data"""
        logger.info("Refresh button clicked - clearing filters")
        if hasattr(self, '_filter_widget') and self._filter_widget:
            self._filter_widget.reset_filters()
            self._filter_widget.clear_search()
        self._load_data(reset_page=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Common Filter Getters - Subclasses can use these directly
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_search_text(self) -> str:
        """Get current search text safely - common pattern for all screens"""
        if hasattr(self, '_filter_widget') and self._filter_widget:
            return self._filter_widget.get_search_text().strip()
        return ""
    
    def _get_filter_value(self, combo_attr: str, default: str = "All") -> str:
        """Get current filter combo value safely
        
        Args:
            combo_attr: Attribute name of the combo (e.g., '_status_combo')
            default: Default value if combo not found
            
        Returns:
            Current combo value or default
        """
        if hasattr(self, combo_attr):
            combo = getattr(self, combo_attr)
            if combo:
                return combo.currentData() or default
        return default
    
    # ─────────────────────────────────────────────────────────────────────────
    # Public Interface
    # ─────────────────────────────────────────────────────────────────────────
    
    def refresh(self):
        """Public method to refresh the data list"""
        logger.info("Manual refresh triggered")
        self._load_data(reset_page=True)
    
    def get_safe_filter_value(self, value: str) -> str:
        """Safely get filter value with null/empty checks"""
        try:
            return str(value or "").strip() if value else ""
        except Exception as e:
            logger.warning(f"Error getting safe filter value: {e}")
            return ""
