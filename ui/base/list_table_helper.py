"""
ListTableHelper - Encapsulates common table population logic
Eliminates duplicate code for populating tables across all list screens

Features:
- Generic row population with styling
- Consistent column configuration
- Action button binding
- Type-specific formatting
- Color-coded status indicators
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, WARNING, DANGER,
    FONT_SIZE_SMALL,
    get_normal_font, get_bold_font
)

from core.logger import get_logger

logger = get_logger(__name__)


class ListTableHelper:
    """Helper class for populating list tables with common patterns"""
    
    def __init__(self, table: QTableWidget, items_per_page: int = 49):
        """
        Initialize helper
        
        Args:
            table: QTableWidget instance to populate
            items_per_page: Items per page (for row numbering across pages)
        """
        self.table = table
        self.items_per_page = items_per_page
        logger.debug("ListTableHelper initialized")
    
    def populate(self, data: list, column_configs: list, current_page: int = 1, 
                 row_formatter=None):
        """
        Populate table with data
        
        Args:
            data: List of data items for current page
            column_configs: List of column configuration dicts
                Each config: {
                    'key': 'field_name',
                    'type': 'text'|'number'|'currency'|'status'|'button',
                    'align': Qt.AlignLeft|Qt.AlignCenter|Qt.AlignRight,
                    'bold': True/False,
                    'color': color_code_or_None,
                    'formatter': callable or None
                }
            current_page: Current page number (for row numbering)
            row_formatter: Optional callable(row_idx, item) -> row_data_dict
            
        Returns:
            Number of rows added
        """
        self.table.setRowCount(0)
        
        # Calculate starting row number
        start_row_num = (current_page - 1) * self.items_per_page + 1
        
        logger.debug(f"Populating table with {len(data)} items, starting row: {start_row_num}")
        
        for page_idx, item in enumerate(data):
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 50)
            
            # Calculate absolute row number
            absolute_row_num = start_row_num + page_idx
            
            # Add columns based on configuration
            for col_idx, config in enumerate(column_configs):
                # Special handling for row number column
                if config.get('type') == 'row_number':
                    self._add_row_number_cell(row_idx, col_idx, absolute_row_num)
                    continue
                
                # Special handling for button columns
                if config.get('type') == 'button':
                    self._add_button_cell(row_idx, col_idx, item, config)
                    continue
                
                # Get value from item (dict or object)
                key = config.get('key')
                value = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
                
                # Format value based on type
                formatted_value = self._format_value(value, config)
                
                # Create and configure cell
                cell = QTableWidgetItem(formatted_value)
                self._configure_cell(cell, config)
                
                # Store data for reference
                if key == 'id' and col_idx == 1:  # Typically name column
                    cell.setData(Qt.UserRole, item.get('id') if isinstance(item, dict) else item.id)
                
                self.table.setItem(row_idx, col_idx, cell)
        
        logger.debug(f"Table populated with {self.table.rowCount()} rows")
        return self.table.rowCount()
    
    def _add_row_number_cell(self, row: int, col: int, row_num: int):
        """Add row number cell"""
        cell = QTableWidgetItem(str(row_num))
        cell.setTextAlignment(Qt.AlignCenter)
        cell.setForeground(QColor(TEXT_SECONDARY))
        cell.setFont(get_normal_font())
        self.table.setItem(row, col, cell)
    
    def _add_button_cell(self, row: int, col: int, item: dict, config: dict):
        """Add button cell"""
        from widgets import TableActionButton
        
        button_text = config.get('text', 'Action')
        button_bg = config.get('bg_color', '#EEF2FF')
        button_hover = config.get('hover_color', '#3B82F6')
        button_size = config.get('size', (60, 32))
        
        button = TableActionButton(
            text=button_text,
            tooltip=config.get('tooltip', ''),
            bg_color=button_bg,
            hover_color=button_hover,
            size=button_size
        )
        
        # Store item reference
        button.item_data = item
        
        self.table.setCellWidget(row, col, button)
    
    def _format_value(self, value, config: dict) -> str:
        """Format value based on type"""
        if value is None:
            return '-'
        
        value_type = config.get('type', 'text')
        
        # Use custom formatter if provided
        if 'formatter' in config:
            try:
                return config['formatter'](value)
            except Exception as e:
                logger.warning(f"Error in custom formatter: {e}")
                return str(value)
        
        # Type-specific formatting
        if value_type == 'text':
            return str(value)
        elif value_type == 'number':
            try:
                return str(int(value)) if isinstance(value, (int, float)) else str(value)
            except:
                return str(value)
        elif value_type == 'currency':
            from core.core_utils import format_currency
            try:
                return format_currency(float(value))
            except:
                return '-'
        elif value_type == 'status':
            return str(value).upper()
        elif value_type == 'date':
            return str(value)
        else:
            return str(value)
    
    def _configure_cell(self, cell: QTableWidgetItem, config: dict):
        """Configure cell appearance"""
        # Font
        if config.get('bold'):
            cell.setFont(get_bold_font())
        else:
            cell.setFont(get_normal_font())
        
        # Alignment
        alignment = config.get('align', Qt.AlignLeft)
        cell.setTextAlignment(alignment | Qt.AlignVCenter)
        
        # Color - for status-based coloring
        value_type = config.get('type', 'text')
        if value_type == 'status':
            cell_text = cell.text().lower()
            if 'paid' in cell_text or 'complete' in cell_text:
                cell.setForeground(QColor('#10B981'))  # Green
            elif 'pending' in cell_text:
                cell.setForeground(QColor(WARNING))  # Orange
            elif 'cancelled' in cell_text or 'failed' in cell_text:
                cell.setForeground(QColor(DANGER))  # Red
        elif value_type == 'balance_type':
            cell_text = cell.text().upper()
            if cell_text == 'DR':
                cell.setForeground(QColor(WARNING))
            elif cell_text == 'CR':
                cell.setForeground(QColor(DANGER))
        
        # Custom color from config
        if 'color' in config and config['color']:
            cell.setForeground(QColor(config['color']))
