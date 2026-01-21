"""
FilterWidget - Reusable filter builder widget
Encapsulates common filter UI pattern to eliminate duplication across list screens

Features:
- Dynamic filter addition (search, combo, date range, custom)
- Consistent styling
- Signal-based filter changes
- Clean API for building filters
"""

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QComboBox, QDateEdit, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDate

from theme import (
    WHITE, BORDER, TEXT_SECONDARY,
    get_normal_font, get_filter_combo_style, get_filter_frame_style, 
    get_filter_label_style
)

from widgets import SearchInputContainer, RefreshButton
from core.logger import get_logger

logger = get_logger(__name__)


class FilterWidget(QFrame):
    """
    Reusable filter widget that encapsulates common filter patterns
    
    Provides:
    - Search input with debouncing
    - Combo box filters (dropdown lists)
    - Date range filters
    - Custom filter widgets
    - Consistent styling
    - filters_changed signal
    """
    
    # Signals
    filters_changed = Signal()
    search_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize filter widget"""
        super().__init__(parent)
        
        self.setStyleSheet(get_filter_frame_style())
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 12)
        self.layout.setSpacing(12)
        
        self._filters = {}  # Store filter widgets by name
        self._search_input = None
        
        logger.debug("FilterWidget initialized")
    
    def add_search_filter(self, placeholder: str = "Search...") -> 'SearchInputContainer':
        """
        Add search input filter
        
        Args:
            placeholder: Placeholder text
            
        Returns:
            SearchInputContainer widget
        """
        self._search_input = SearchInputContainer(placeholder)
        self._search_input.textChanged.connect(self.search_changed.emit)
        self.layout.addWidget(self._search_input)
        
        logger.debug(f"Search filter added: {placeholder}")
        return self._search_input
    
    def add_combo_filter(self, name: str, label: str, options: dict) -> QComboBox:
        """
        Add combo box (dropdown) filter
        
        Args:
            name: Internal name for this filter
            label: Display label
            options: Dict {display_text: value}
                     First item should be "All" with value "all"
            
        Returns:
            QComboBox widget
        """
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(get_normal_font())
        label_widget.setStyleSheet(get_filter_label_style())
        self.layout.addWidget(label_widget)
        
        # Combo box
        combo = QComboBox()
        combo.setFont(get_normal_font())
        combo.setStyleSheet(get_filter_combo_style())
        
        # Add options
        for display_text, value in options.items():
            combo.addItem(display_text, value)
        
        # Connect signal
        combo.currentIndexChanged.connect(self.filters_changed.emit)
        
        # Store reference
        self._filters[name] = combo
        self.layout.addWidget(combo)
        
        logger.debug(f"Combo filter added: {name}")
        return combo
    
    def add_date_filter(self, name: str, label: str) -> QDateEdit:
        """
        Add date picker filter
        
        Args:
            name: Internal name for this filter
            label: Display label
            
        Returns:
            QDateEdit widget
        """
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(get_normal_font())
        label_widget.setStyleSheet(get_filter_label_style())
        self.layout.addWidget(label_widget)
        
        # Date picker
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setFont(get_normal_font())
        date_edit.dateChanged.connect(self.filters_changed.emit)
        
        # Store reference
        self._filters[name] = date_edit
        self.layout.addWidget(date_edit)
        
        logger.debug(f"Date filter added: {name}")
        return date_edit
    
    def add_custom_filter(self, name: str, label: str, widget: QWidget) -> QWidget:
        """
        Add custom filter widget
        
        Args:
            name: Internal name for this filter
            label: Display label
            widget: Custom QWidget
            
        Returns:
            The custom widget
        """
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(get_normal_font())
        label_widget.setStyleSheet(get_filter_label_style())
        self.layout.addWidget(label_widget)
        
        # Add custom widget
        self.layout.addWidget(widget)
        
        # Store reference
        self._filters[name] = widget
        
        logger.debug(f"Custom filter added: {name}")
        return widget
    
    def add_stretch(self):
        """Add stretch spacer"""
        self.layout.addStretch()
    
    def add_refresh_button(self, callback) -> 'RefreshButton':
        """
        Add refresh button
        
        Args:
            callback: Function to call on click
            
        Returns:
            RefreshButton widget
        """
        refresh_btn = RefreshButton()
        refresh_btn.clicked.connect(callback)
        self.layout.addWidget(refresh_btn)
        
        logger.debug("Refresh button added")
        return refresh_btn
    
    def get_filters(self) -> dict:
        """
        Get all filter values
        
        Returns:
            Dict {filter_name: filter_value}
        """
        filters = {}
        for name, widget in self._filters.items():
            if isinstance(widget, QComboBox):
                filters[name] = widget.currentData()
            elif isinstance(widget, QDateEdit):
                filters[name] = widget.date()
            elif hasattr(widget, 'text'):
                filters[name] = widget.text()
            else:
                filters[name] = widget
        
        return filters
    
    def get_search_text(self) -> str:
        """Get search input text"""
        if self._search_input:
            return self._search_input.text()
        return ""
    
    def get_filter(self, name: str):
        """Get specific filter widget by name"""
        return self._filters.get(name)
    
    def clear_search(self):
        """Clear search input"""
        if self._search_input:
            self._search_input.clear()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        for widget in self._filters.values():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif hasattr(widget, 'clear'):
                widget.clear()
        
        logger.debug("All filters reset")
