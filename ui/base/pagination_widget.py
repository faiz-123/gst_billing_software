"""
Reusable Pagination Widget for list screens
Handles pagination controls (Previous/Next buttons, page info, item counts)
Can be reused across multiple screens (parties, invoices, products, payments, etc.)
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal

from theme import (
    PRIMARY, WHITE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_SIZE_NORMAL,
    get_normal_font, get_bold_font
)

from core.logger import get_logger

logger = get_logger(__name__)


class PaginationWidget(QWidget):
    """Reusable pagination controls widget
    
    Emits signals for page navigation and provides state management.
    Can be customized with:
    - items_per_page: Number of items per page (default 49)
    - entity_name: Singular form of entity (e.g., "party", "invoice", "product")
    
    Signals:
        page_changed: Emitted when page changes with new page number
        page_navigation: Emitted with ('previous' or 'next') when nav buttons clicked
    """
    
    # Signals
    page_changed = Signal(int)  # Emits new page number
    page_navigation = Signal(str)  # Emits 'previous' or 'next'
    
    def __init__(self, items_per_page: int = 49, entity_name: str = "item", parent=None):
        """Initialize pagination widget
        
        Args:
            items_per_page: Number of items to show per page (default 49)
            entity_name: Name of entity for display (e.g., "party", "invoice")
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.items_per_page = items_per_page
        self.entity_name = entity_name
        
        # State
        self._current_page = 1
        self._total_pages = 1
        self._total_items = 0
        
        logger.debug(f"Initializing PaginationWidget with {items_per_page} items per page")
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create frame with styling
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(16, 12, 16, 12)
        pagination_layout.setSpacing(12)
        
        # Previous button
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setFont(get_normal_font())
        self.prev_btn.setStyleSheet(self._get_button_style())
        self.prev_btn.clicked.connect(self._on_previous_clicked)
        pagination_layout.addWidget(self.prev_btn)
        
        # Page info label
        pagination_layout.addSpacing(10)
        self.page_info_label = QLabel("Page 0 of 0")
        self.page_info_label.setFont(get_bold_font(FONT_SIZE_NORMAL))
        self.page_info_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        self.page_info_label.setMinimumWidth(120)
        self.page_info_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addSpacing(10)
        
        # Items per page info
        self.items_label = QLabel(f"Items per page: {self.items_per_page}")
        self.items_label.setFont(get_normal_font())
        self.items_label.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        pagination_layout.addWidget(self.items_label)
        
        # Stretch spacer
        pagination_layout.addStretch()
        
        # Total records label
        self.total_records_label = QLabel(f"Total: 0 {self.entity_name}s")
        self.total_records_label.setFont(get_normal_font())
        self.total_records_label.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
        pagination_layout.addWidget(self.total_records_label)
        
        pagination_layout.addSpacing(10)
        
        # Next button
        self.next_btn = QPushButton("Next →")
        self.next_btn.setFont(get_normal_font())
        self.next_btn.setStyleSheet(self._get_button_style())
        self.next_btn.clicked.connect(self._on_next_clicked)
        pagination_layout.addWidget(self.next_btn)
        
        main_layout.addWidget(pagination_frame)
    
    @staticmethod
    def _get_button_style() -> str:
        """Get button stylesheet"""
        return f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background: {TEXT_SECONDARY};
                color: {BORDER};
            }}
        """
    
    def set_pagination_state(self, current_page: int, total_pages: int, total_items: int):
        """Update pagination state and UI
        
        Args:
            current_page: Current page number
            total_pages: Total number of pages
            total_items: Total number of items (across all pages)
        """
        self._current_page = current_page
        self._total_pages = total_pages
        self._total_items = total_items
        
        logger.debug(f"Pagination state updated: Page {current_page}/{total_pages}, Total items: {total_items}")
        
        self._update_ui()
    
    def _update_ui(self):
        """Update UI labels and button states"""
        # Update page info
        self.page_info_label.setText(f"Page {self._current_page} of {self._total_pages}")
        
        # Update total records label
        plural = "s" if self._total_items != 1 else ""
        self.total_records_label.setText(f"Total: {self._total_items} {self.entity_name}{plural}")
        
        # Update button states
        self.prev_btn.setEnabled(self._current_page > 1)
        self.next_btn.setEnabled(self._current_page < self._total_pages)
        
        logger.debug(f"Pagination UI updated - Page: {self._current_page}/{self._total_pages}, "
                     f"Prev enabled: {self.prev_btn.isEnabled()}, Next enabled: {self.next_btn.isEnabled()}")
    
    def _on_previous_clicked(self):
        """Handle previous button click"""
        if self._current_page > 1:
            self._current_page -= 1
            logger.info(f"Pagination: Navigating to page {self._current_page}")
            self.page_changed.emit(self._current_page)
            self.page_navigation.emit('previous')
            self._update_ui()
    
    def _on_next_clicked(self):
        """Handle next button click"""
        if self._current_page < self._total_pages:
            self._current_page += 1
            logger.info(f"Pagination: Navigating to page {self._current_page}")
            self.page_changed.emit(self._current_page)
            self.page_navigation.emit('next')
            self._update_ui()
    
    def reset_to_page_one(self):
        """Reset pagination to first page"""
        self._current_page = 1
        self._total_pages = 1
        self._total_items = 0
        logger.debug("Pagination reset to page 1")
        self._update_ui()
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
    
    def set_current_page(self, page: int):
        """Set current page without emitting signals (for programmatic updates)"""
        if 1 <= page <= self._total_pages:
            self._current_page = page
            self._update_ui()
    
    def get_items_per_page(self) -> int:
        """Get items per page"""
        return self.items_per_page
    
    def get_total_items(self) -> int:
        """Get total items"""
        return self._total_items
    
    def get_total_pages(self) -> int:
        """Get total pages"""
        return self._total_pages
