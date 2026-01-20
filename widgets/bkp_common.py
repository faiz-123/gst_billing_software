"""
Custom widgets and reusable UI components
"""

from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QLabel, QComboBox, QTableWidget, 
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QAbstractItemView,
    QScrollArea, QWidget, QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QDialog, QListWidget, QMessageBox, QCompleter, QStyledItemDelegate,
    QApplication, QStyle
)
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt, QEvent, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

# Import from the new theme module location
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import (
    get_button_style, BORDER, WHITE, TEXT_PRIMARY, FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE, BACKGROUND, TEXT_SECONDARY, PRIMARY, PRIMARY_HOVER,
    get_dialog_input_style, get_readonly_input_style, get_error_input_style,
    get_checkbox_style, get_textarea_style, get_label_font, get_checkbox_font,
    get_stat_card_style, get_stat_label_style, get_stat_value_style,
    get_stat_icon_container_style, get_table_frame_style, get_enhanced_table_style,
    get_row_action_button_style
)

class CustomButton(QPushButton):
    """Custom styled button"""
    def __init__(self, text, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(get_button_style(button_type))
        self.setMinimumHeight(40)

class CustomInput(QLineEdit):
    """Custom styled input field"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 12px;
                background: {WHITE};
                color: {TEXT_PRIMARY};
                font-size: {FONT_SIZE_LARGE}px;
                min-height: 16px;
            }}
        """)

class CustomLabel(QLabel):
    """Custom styled label"""
    def __init__(self, text, is_title=False, parent=None):
        super().__init__(text, parent)
        if is_title:
            font = QFont("Arial", 16)
            font.setBold(True)
            self.setFont(font)
        self.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                border: none;
                font-weight: {'bold' if is_title else 'normal'};
            }}
        """)

class CustomComboBox(QComboBox):
    """Custom styled combo box"""
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        self.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px;
                background: {WHITE};
                color: {TEXT_PRIMARY};
                height: 28px;
                font-size: {FONT_SIZE_LARGE}px;
            }}
            QComboBox::drop-down {{
                height: 20px;
                width: 20px;
                subcontrol-position: center right;
                border-color: transparent;
            }}
        """)

class CustomTable(QTableWidget):
    """Custom styled table widget"""
    def __init__(self, rows=0, columns=0, headers=None, parent=None):
        super().__init__(rows, columns, parent)
        
        if headers:
            self.setHorizontalHeaderLabels(headers)
            
        # Style the table
        self.setStyleSheet(f"""
            QTableWidget {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                gridline-color: {BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
                font-size: {FONT_SIZE_NORMAL}px;
            }}
            QTableWidget::item:selected {{
                background: {BACKGROUND};
            }}
        """)
        
        # Header styling
        self.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {BACKGROUND};
                color: {TEXT_SECONDARY};
                padding: 8px;
                border: 1px solid {BORDER};
                font-weight: bold;
            }}
        """)
        
        # Table settings
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def create_item(self, text, alignment=Qt.AlignLeft | Qt.AlignVCenter):
        """Create a configured QTableWidgetItem for consistent table cell styling.

        Args:
            text (str): Text to display in the cell.
            alignment (Qt.Alignment): Text alignment for the cell.

        Returns:
            QTableWidgetItem: Configured table item.
        """
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(alignment)
        return item


class StatCard(QFrame):
    """
    Reusable statistics card widget with icon and consistent styling.
    
    Displays a single statistic with an icon, title, and value.
    Used across list screens (parties, products, invoices, payments, receipts).
    
    Args:
        icon: Emoji or text icon to display
        title: Label text for the statistic
        value: Initial value to display (default "0")
        color: Accent color for styling (default PRIMARY)
        parent: Parent widget
    """
    
    def __init__(self, icon: str, title: str, value: str = "0", color: str = PRIMARY, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._title = title
        self._color = color
        self._setup_ui(value)
    
    def _setup_ui(self, value: str):
        """Initialize the card UI layout."""
        from PySide6.QtWidgets import QSizePolicy
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(80)
        self.setStyleSheet(get_stat_card_style(self._color))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(get_stat_icon_container_style(self._color))
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(self._icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px; border: none;")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(4)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet(get_stat_label_style())
        text_container.addWidget(title_label)
        
        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(get_stat_value_style())
        text_container.addWidget(self._value_label)
        
        layout.addLayout(text_container)
        layout.addStretch()
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self._value_label.setText(value)


class TableActionButton(QPushButton):
    """
    Reusable action button for table rows (Edit, Delete, View, etc.).
    
    Used across list screens to provide consistent action buttons in tables.
    
    Args:
        text: Button text (e.g., "Edit", "Del", "View")
        tooltip: Tooltip text shown on hover
        bg_color: Background color (default "#EEF2FF")
        hover_color: Hover/accent color (default PRIMARY)
        size: Tuple of (width, height) for button size
        parent: Parent widget
    
    Example:
        edit_btn = TableActionButton(
            text="Edit",
            tooltip="Edit this item",
            bg_color="#EEF2FF",
            hover_color=PRIMARY
        )
        edit_btn.clicked.connect(lambda: self._on_edit(item))
    """
    
    def __init__(
        self, 
        text: str, 
        tooltip: str = "",
        bg_color: str = "#EEF2FF",
        hover_color: str = PRIMARY,
        size: tuple = (40, 28),
        parent=None
    ):
        super().__init__(text, parent)
        self.setFixedSize(size[0], size[1])
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(get_row_action_button_style(bg_color, hover_color))


class ListTable(QTableWidget):
    """
    Reusable table widget with consistent styling for list screens.
    
    Pre-configured with common settings:
    - Alternating row colors
    - Row selection mode
    - No edit triggers
    - Hidden vertical header
    - No grid lines
    - 50px row height
    - Enhanced table styling
    
    Args:
        headers: List of column header labels
        parent: Parent widget
    
    Example:
        table = ListTable(headers=["#", "Name", "Type", "Actions"])
        table.configure_columns([
            {"width": 50, "resize": "fixed"},      # #
            {"resize": "stretch"},                  # Name
            {"width": 100, "resize": "fixed"},     # Type
            {"width": 80, "resize": "fixed"},      # Actions
        ])
    """
    
    def __init__(self, headers: list = None, parent=None):
        super().__init__(parent)
        self._setup_table(headers)
    
    def _setup_table(self, headers: list):
        """Initialize table with common settings."""
        self.setStyleSheet(get_enhanced_table_style())
        
        if headers:
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
        
        # Common table settings
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.verticalHeader().setDefaultSectionSize(50)
    
    def configure_columns(self, column_configs: list):
        """
        Configure column widths and resize modes.
        
        Args:
            column_configs: List of dicts with optional keys:
                - "width": Fixed width in pixels
                - "resize" or "mode": "fixed", "stretch", or "resize_to_contents"
        
        Example:
            table.configure_columns([
                {"width": 50, "resize": "fixed"},
                {"resize": "stretch"},
                {"width": 100, "resize": "fixed"},
            ])
        """
        header = self.horizontalHeader()
        
        for idx, config in enumerate(column_configs):
            if idx >= self.columnCount():
                break
            
            # Support both "resize" and "mode" keys
            resize_mode = config.get("resize", config.get("mode", "fixed"))
            if resize_mode == "stretch":
                header.setSectionResizeMode(idx, QHeaderView.Stretch)
            elif resize_mode == "resize_to_contents":
                header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(idx, QHeaderView.Fixed)
            
            # Set fixed width if specified
            if "width" in config:
                self.setColumnWidth(idx, config["width"])
    
    def add_row_with_data(self, row_data: list, row_height: int = 50) -> int:
        """
        Add a row with data items.
        
        Args:
            row_data: List of (text, alignment, font, foreground_color) tuples or just text
            row_height: Height of the row (default 50)
        
        Returns:
            Row index of the added row
        """
        row = self.rowCount()
        self.insertRow(row)
        self.setRowHeight(row, row_height)
        
        for col, data in enumerate(row_data):
            if col >= self.columnCount():
                break
            
            if isinstance(data, QWidget):
                self.setCellWidget(row, col, data)
            elif isinstance(data, QTableWidgetItem):
                self.setItem(row, col, data)
            elif isinstance(data, dict):
                item = QTableWidgetItem(str(data.get("text", "")))
                if "alignment" in data:
                    item.setTextAlignment(data["alignment"])
                if "font" in data:
                    item.setFont(data["font"])
                if "foreground" in data:
                    from PySide6.QtGui import QColor
                    item.setForeground(QColor(data["foreground"]))
                if "user_data" in data:
                    item.setData(Qt.UserRole, data["user_data"])
                self.setItem(row, col, item)
            else:
                item = QTableWidgetItem(str(data) if data is not None else "")
                self.setItem(row, col, item)
        
        return row


class TableFrame(QFrame):
    """
    Reusable frame container for tables with consistent styling.
    
    Provides a styled frame for embedding tables.
    Can either use helper methods (set_table, add_header) which auto-create a layout,
    or create your own layout with QVBoxLayout(frame).
    
    Args:
        parent: Parent widget
    
    Example 1 (using helpers):
        frame = TableFrame()
        frame.set_table(table)
        
    Example 2 (manual layout):
        frame = TableFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(table)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = None
        self._setup_frame()
    
    def _setup_frame(self):
        """Initialize frame styling."""
        self.setObjectName("tableFrame")
        self.setStyleSheet(get_table_frame_style())
    
    def _ensure_layout(self):
        """Create layout if not exists."""
        if self._layout is None:
            self._layout = QVBoxLayout(self)
            self._layout.setContentsMargins(16, 16, 16, 16)
            self._layout.setSpacing(0)
    
    def set_table(self, table: QTableWidget):
        """Add a table to this frame."""
        self._ensure_layout()
        self._layout.addWidget(table)
    
    def add_header(self, widget: QWidget):
        """Add a header widget above the table."""
        self._ensure_layout()
        self._layout.insertWidget(0, widget)
        self._layout.setSpacing(12)


class SearchInputContainer(QFrame):
    """
    Reusable search input container with icon.
    
    A styled search box with a search icon emoji and consistent styling
    across all list screens.
    
    Args:
        placeholder: Placeholder text for the search input
        auto_upper: If True, automatically converts input to uppercase
        parent: Parent widget
    
    Example:
        search = SearchInputContainer("Search by name...", auto_upper=True)
        search.textChanged.connect(self._on_search)
        text = search.text()
    """
    
    def __init__(self, placeholder: str = "Search...", auto_upper: bool = True, parent=None):
        super().__init__(parent)
        self._auto_upper = auto_upper
        self._setup_ui(placeholder)
    
    def _setup_ui(self, placeholder: str):
        """Initialize the search input UI."""
        from theme import get_search_container_style, get_search_input_style
        from PySide6.QtWidgets import QSizePolicy
        
        self.setObjectName("searchContainer")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        self.setFixedHeight(40)
        self.setStyleSheet(get_search_container_style())
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)
        
        # Search icon
        icon = QLabel("🔍")
        icon.setStyleSheet("border: none; font-size: 14px;")
        layout.addWidget(icon)
        
        # Search input
        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        self._input.setStyleSheet(get_search_input_style())
        layout.addWidget(self._input)
        
        # Connect auto uppercase if enabled
        if self._auto_upper:
            self._input.textChanged.connect(self._to_upper)
    
    def _to_upper(self, text: str):
        """Convert text to uppercase while preserving cursor position."""
        upper = text.upper()
        if text != upper:
            cursor_pos = self._input.cursorPosition()
            self._input.blockSignals(True)
            self._input.setText(upper)
            self._input.setCursorPosition(cursor_pos)
            self._input.blockSignals(False)
    
    def text(self) -> str:
        """Get the current search text."""
        return self._input.text().strip()
    
    def setText(self, text: str):
        """Set the search text."""
        self._input.setText(text)
    
    def clear(self):
        """Clear the search text."""
        self._input.clear()
    
    @property
    def textChanged(self):
        """Signal emitted when text changes."""
        return self._input.textChanged


class RefreshButton(QPushButton):
    """
    Reusable refresh button with consistent styling.
    
    A styled button with refresh icon emoji for refreshing data.
    
    Args:
        parent: Parent widget
    
    Example:
        refresh_btn = RefreshButton()
        refresh_btn.clicked.connect(self._on_refresh)
    """
    
    def __init__(self, parent=None):
        super().__init__("🔄", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the button UI."""
        from theme import get_icon_button_style
        
        self.setFixedSize(32, 32)
        self.setToolTip("Refresh Data")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(get_icon_button_style())


class ListHeader(QWidget):
    """
    Reusable header widget for list screens.
    
    Creates a consistent header with title, optional export button, and add button.
    
    Args:
        title: The title text to display
        add_button_text: Text for the primary add button
        show_export: Whether to show the export button (default True)
        parent: Parent widget
    
    Signals:
        add_clicked: Emitted when add button is clicked
        export_clicked: Emitted when export button is clicked
    
    Example:
        header = ListHeader("Products", "+ Add Product")
        header.add_clicked.connect(self._on_add)
        header.export_clicked.connect(self._on_export)
    """
    
    def __init__(self, title: str, add_button_text: str, show_export: bool = True, parent=None):
        super().__init__(parent)
        self._setup_ui(title, add_button_text, show_export)
    
    def _setup_ui(self, title: str, add_button_text: str, show_export: bool):
        """Initialize the header UI."""
        from theme import get_title_font, TEXT_PRIMARY
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(get_title_font())
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Export button (optional)
        if show_export:
            self._export_btn = CustomButton("📤 Export", "secondary")
            self._export_btn.setFixedWidth(120)
            self._export_btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(self._export_btn)
        
        # Add button
        self._add_btn = CustomButton(add_button_text, "primary")
        self._add_btn.setFixedWidth(160)
        self._add_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self._add_btn)
    
    @property
    def add_clicked(self):
        """Signal emitted when add button is clicked."""
        return self._add_btn.clicked
    
    @property
    def export_clicked(self):
        """Signal emitted when export button is clicked."""
        if hasattr(self, '_export_btn'):
            return self._export_btn.clicked
        return None


class StatsContainer(QFrame):
    """
    Reusable container for statistics cards.
    
    A styled container that holds StatCard widgets in a horizontal layout.
    
    Args:
        cards: List of StatCard widgets to add
        parent: Parent widget
    
    Example:
        stats = StatsContainer([
            StatCard("📦", "Total", "0", PRIMARY),
            StatCard("✅", "Active", "0", SUCCESS),
        ])
        # or add cards later:
        stats = StatsContainer()
        stats.add_card(StatCard("📦", "Total", "0", PRIMARY))
    """
    
    def __init__(self, cards: list = None, parent=None):
        super().__init__(parent)
        self._setup_ui()
        if cards:
            for card in cards:
                self.add_card(card)
    
    def _setup_ui(self):
        """Initialize the container UI."""
        from PySide6.QtWidgets import QSizePolicy
        
        self.setStyleSheet("background: transparent; border: none;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)
    
    def add_card(self, card):
        """Add a StatCard to the container."""
        self._layout.addWidget(card)
        return card


class SearchBox(QLineEdit):
    """Custom search input"""
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(35)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding-left: 10px;
                background: {WHITE};
                font-size: {FONT_SIZE_NORMAL}px;
            }}
        """)

class FormField(QVBoxLayout):
    """Custom form field with label and input"""
    def __init__(self, label_text, input_widget, parent=None):
        super().__init__()
        self.setSpacing(4)
        
        # Label
        label = CustomLabel(label_text, is_title=True)
        self.addWidget(label)
        
        # Input widget
        self.input_widget = input_widget
        self.addWidget(input_widget)
        
    def get_value(self):
        """Get the value from the input widget"""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'currentText'):
            return self.input_widget.currentText()
        return None
        
    def set_value(self, value):
        """Set the value of the input widget"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setCurrentText'):
            self.input_widget.setCurrentText(str(value))


# ============================================================================
# Dialog-specific widgets (for forms and dialogs)
# ============================================================================

class DialogInput(QLineEdit):
    """Dialog-styled input field with consistent height and styling"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_dialog_input_style())
        self.setFixedHeight(44)
    
    def set_error(self, is_error: bool, tooltip: str = ""):
        """Set error state with visual feedback"""
        if is_error:
            self.setStyleSheet(get_error_input_style())
            self.setToolTip(tooltip)
        else:
            self.setStyleSheet(get_dialog_input_style())
            self.setToolTip("")
    
    def set_readonly(self, readonly: bool):
        """Set read-only state with visual feedback"""
        self.setReadOnly(readonly)
        if readonly:
            self.setStyleSheet(get_readonly_input_style())
        else:
            self.setStyleSheet(get_dialog_input_style())


class DialogComboBox(QComboBox):
    """Dialog-styled combo box with consistent height and styling"""
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        self.setStyleSheet(get_dialog_input_style())
        self.setFixedHeight(44)


class DialogEditableComboBox(QComboBox):
    """Dialog-styled editable combo box - allows selecting from list or typing new value"""
    def __init__(self, items=None, placeholder="", auto_upper=True, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self._auto_upper = auto_upper
        if items:
            self.addItems(items)
        if placeholder:
            self.lineEdit().setPlaceholderText(placeholder)
        self._apply_styles()
        self.setFixedHeight(44)
        
        # Clear the default selection - start with empty
        self.setCurrentIndex(-1)
        self.lineEdit().clear()
        
        # Connect auto uppercase if enabled
        if self._auto_upper:
            self.lineEdit().textChanged.connect(self._to_upper)
        
        # Install event filter for keyboard handling
        self.lineEdit().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events - open dropdown on down arrow"""
        if obj == self.lineEdit() and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Down:
                self.showPopup()
                return True
        return super().eventFilter(obj, event)
    
    def _apply_styles(self):
        """Apply styles including dropdown list background"""
        self.setStyleSheet(get_dialog_input_style() + f"""
            QComboBox QAbstractItemView {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 4px;
                selection-background-color: {PRIMARY};
                selection-color: {WHITE};
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 30px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: {PRIMARY};
            }}
        """)
    
    def _to_upper(self, text: str):
        """Convert text to uppercase while preserving cursor position."""
        upper = text.upper()
        if text != upper:
            line_edit = self.lineEdit()
            cursor_pos = line_edit.cursorPosition()
            line_edit.blockSignals(True)
            line_edit.setText(upper)
            line_edit.setCursorPosition(cursor_pos)
            line_edit.blockSignals(False)
    
    def text(self) -> str:
        """Get the current text (typed or selected)"""
        return self.currentText().strip()
    
    def setText(self, text: str):
        """Set the current text"""
        self.setCurrentText(text)


class DialogSpinBox(QSpinBox):
    """Dialog-styled spin box with consistent height and styling"""
    def __init__(self, min_val=0, max_val=9999999, parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setStyleSheet(get_dialog_input_style())
        self.setFixedHeight(44)
    
    def set_readonly(self, readonly: bool):
        """Set read-only state with visual feedback"""
        self.setReadOnly(readonly)
        if readonly:
            self.setStyleSheet(get_readonly_input_style())
        else:
            self.setStyleSheet(get_dialog_input_style())


class DialogDoubleSpinBox(QDoubleSpinBox):
    """Dialog-styled double spin box with consistent height and styling"""
    def __init__(self, min_val=0.0, max_val=9999999.99, decimals=2, parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setDecimals(decimals)
        self.setStyleSheet(get_dialog_input_style())
        self.setFixedHeight(44)
    
    def set_error(self, is_error: bool, tooltip: str = ""):
        """Set error state with visual feedback"""
        if is_error:
            self.setStyleSheet(get_error_input_style())
            self.setToolTip(tooltip)
        else:
            self.setStyleSheet(get_dialog_input_style())
            self.setToolTip("")
    
    def set_readonly(self, readonly: bool):
        """Set read-only state with visual feedback"""
        self.setReadOnly(readonly)
        if readonly:
            self.setStyleSheet(get_readonly_input_style())
        else:
            self.setStyleSheet(get_dialog_input_style())


class DialogCheckBox(QCheckBox):
    """Dialog-styled checkbox with consistent styling"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFont(get_checkbox_font())
        self.setStyleSheet(get_checkbox_style())


class DialogTextEdit(QTextEdit):
    """Dialog-styled text edit/area with consistent styling"""
    def __init__(self, placeholder="", height=80, parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setFixedHeight(height)
        self.setStyleSheet(get_textarea_style())


class DialogFieldGroup(QWidget):
    """Field group with label and input widget for dialogs - supports Rich Text labels"""
    def __init__(self, label_text: str, input_widget: QWidget, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label with Rich Text support (for required field asterisks)
        label = QLabel(label_text)
        label.setTextFormat(Qt.RichText)
        label.setFont(get_label_font())
        label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none; background: transparent;")
        layout.addWidget(label)
        
        # Input widget
        self.input_widget = input_widget
        layout.addWidget(input_widget)
    
    def get_value(self):
        """Get the value from the input widget"""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'value'):
            return self.input_widget.value()
        elif hasattr(self.input_widget, 'currentText'):
            return self.input_widget.currentText()
        elif hasattr(self.input_widget, 'toPlainText'):
            return self.input_widget.toPlainText()
        elif hasattr(self.input_widget, 'isChecked'):
            return self.input_widget.isChecked()
        return None
    
    def set_value(self, value):
        """Set the value of the input widget"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setValue'):
            self.input_widget.setValue(value)
        elif hasattr(self.input_widget, 'setCurrentText'):
            self.input_widget.setCurrentText(str(value))
        elif hasattr(self.input_widget, 'setPlainText'):
            self.input_widget.setPlainText(str(value))
        elif hasattr(self.input_widget, 'setChecked'):
            self.input_widget.setChecked(bool(value))


class SidebarButton(QPushButton):
    """Enhanced sidebar button with active state and modern design"""
    def __init__(self, text, icon="", parent=None):
        super().__init__(parent)
        self.text = text
        self.icon = icon
        self.is_active = False
        self.is_collapsed = False
        self.is_separator_before = False  # For visual grouping
        self.update_text()
        self.setObjectName("sidebarButton")
        self.setCursor(Qt.PointingHandCursor)
        
    def update_text(self):
        """Update button text with icon"""
        if self.is_collapsed:
            # Show only icon when collapsed
            display_text = self.icon if self.icon else self.text[0].upper()
        else:
            # Show icon and text when expanded
            display_text = f"{self.icon}  {self.text}" if self.icon else self.text
        self.setText(display_text)
        
    def set_collapsed(self, collapsed):
        """Set the collapsed state for the button"""
        self.is_collapsed = collapsed
        # Update Qt property for CSS selector
        self.setProperty("collapsed", str(collapsed).lower())
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update_text()
        
    def set_active(self, active):
        """Set active state"""
        self.is_active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

class Sidebar(QFrame):
    """Enhanced sidebar component with modern design"""
    def __init__(self, parent=None, company_name="GST Billing"):
        super().__init__(parent)
        self.is_collapsed = False
        self.expanded_width = 260  # Slightly reduced for cleaner look
        self.collapsed_width = 70
        self.active_button = None
        self.menu_buttons = []
        self.company_name = company_name
        
        self.setFixedWidth(self.expanded_width)
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the sidebar UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header section
        self.create_header()
        
        # Menu section
        self.create_menu_section()
        
        # Footer section
        self.create_footer()
        
    def create_header(self):
        """Create header with company logo/name and toggle button"""
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setFixedHeight(70)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 12, 12)
        
        # Logo circle with initials (clickable to toggle when collapsed)
        self.logo_circle = QPushButton()
        self.logo_circle.setObjectName("logoCircle")
        self.logo_circle.setFixedSize(40, 40)
        self.logo_circle.setCursor(Qt.PointingHandCursor)
        # Get initials from company name
        initials = "".join([word[0].upper() for word in self.company_name.split()[:2]])
        self.logo_circle.setText(initials)
        self.logo_circle.clicked.connect(self.on_logo_click)
        
        # Company name title
        self.title_label = QLabel(self.company_name)
        self.title_label.setObjectName("sidebarTitle")
        self.title_label.setWordWrap(True)
        
        # Toggle button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setObjectName("toggleButton")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        header_layout.addWidget(self.logo_circle)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.title_label, 1)
        header_layout.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(header_frame)
        
    def create_menu_section(self):
        """Create scrollable menu section"""
        # Scroll area for menu items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setObjectName("menuScrollArea")
        self.scroll_area.setStyleSheet("""
            QScrollArea#menuScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#menuScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 6px;
                border-radius: 3px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Menu container inside scroll area
        self.menu_frame = QWidget()
        self.menu_frame.setObjectName("menuFrame")
        
        self.menu_layout = QVBoxLayout(self.menu_frame)
        self.menu_layout.setContentsMargins(12, 16, 12, 10)
        self.menu_layout.setSpacing(4)
        
        self.scroll_area.setWidget(self.menu_frame)
        self.main_layout.addWidget(self.scroll_area, 1)
        
    def create_footer(self):
        """Create footer section with version info"""
        footer_frame = QFrame()
        footer_frame.setObjectName("sidebarFooter")
        footer_frame.setFixedHeight(50)
        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(16, 8, 16, 12)
        footer_layout.setAlignment(Qt.AlignCenter)
        
        # Version label
        self.version_label = QLabel("v1.0.0")
        self.version_label.setObjectName("versionLabel")
        self.version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.version_label)
        
        self.main_layout.addWidget(footer_frame)
        
    def add_menu_section(self, title):
        """Add a section header"""
        if not self.is_collapsed:
            section_label = QLabel(title)
            section_label.setObjectName("sectionHeader")
            self.menu_layout.addWidget(section_label)
            
        # Add some spacing
        self.menu_layout.addSpacing(5)
    
    def add_separator(self):
        """Add a visual separator line"""
        separator = QFrame()
        separator.setObjectName("menuSeparator")
        separator.setFixedHeight(1)
        self.menu_layout.addSpacing(8)
        self.menu_layout.addWidget(separator)
        self.menu_layout.addSpacing(8)
        
    def add_menu_item(self, text, icon="", callback=None):
        """Add a menu item to sidebar"""
        btn = SidebarButton(text, icon)
        btn.setMinimumHeight(44)
        
        if callback:
            btn.clicked.connect(callback)
            btn.clicked.connect(lambda: self.set_active_button(btn))
            
        self.menu_buttons.append(btn)
        self.menu_layout.addWidget(btn)
        return btn
        
    def add_stretch(self):
        """Add stretch to push items"""
        self.menu_layout.addStretch()
        
    def set_active_button(self, button):
        """Set the active menu button"""
        # Deactivate previous button
        if self.active_button:
            self.active_button.set_active(False)
            
        # Activate new button
        self.active_button = button
        button.set_active(True)
        
    def update_company_name(self, company_name):
        """Update the company name displayed in the sidebar"""
        self.company_name = company_name
        self.title_label.setText(company_name)
        # Update logo initials
        initials = "".join([word[0].upper() for word in company_name.split()[:2]])
        self.logo_circle.setText(initials)
    
    def on_logo_click(self):
        """Handle logo click - expand sidebar if collapsed"""
        if self.is_collapsed:
            self.toggle_sidebar()
        
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.setFixedWidth(self.collapsed_width)
            self.title_label.hide()
            self.toggle_btn.hide()  # Hide toggle button when collapsed
            self.logo_circle.show()  # Keep logo visible - clicking it will expand
            self.version_label.hide()
            # Update all buttons to collapsed mode
            for button in self.menu_buttons:
                button.set_collapsed(True)
            # Hide section headers and separators
            for i in range(self.menu_layout.count()):
                item = self.menu_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'objectName'):
                        if widget.objectName() in ["sectionHeader", "menuSeparator"]:
                            widget.hide()
        else:
            self.setFixedWidth(self.expanded_width)
            self.title_label.show()
            self.toggle_btn.show()  # Show toggle button when expanded
            self.version_label.show()
            # Update all buttons to expanded mode
            for button in self.menu_buttons:
                button.set_collapsed(False)
            # Show section headers and separators
            for i in range(self.menu_layout.count()):
                item = self.menu_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'objectName'):
                        if widget.objectName() in ["sectionHeader", "menuSeparator"]:
                            widget.show()
                        
    def apply_styles(self):
        """Apply modern professional styling to sidebar"""
        self.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: none;
            }
            
            QFrame#sidebarHeader {
                background-color: #0F172A;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 0px;
            }
            
            QFrame#menuFrame {
                background: transparent;
            }
            
            QFrame#sidebarFooter {
                background-color: rgba(15, 23, 42, 0.95);
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 0px;
            }
            
            QFrame#menuSeparator {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
            }
            
            QPushButton#logoCircle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3B82F6, stop:1 #8B5CF6);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 20px;
                border: none;
            }
            
            QPushButton#logoCircle:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #60A5FA, stop:1 #A78BFA);
            }
            
            QLabel#sidebarTitle {
                color: #F1F5F9;
                font-weight: 600;
                font-size: 15px;
                padding: 0px;
                margin: 0px;
                border: none;
            }
            
            QLabel#versionLabel {
                color: rgba(148, 163, 184, 0.6);
                font-size: 11px;
                border: none;
            }
            
            QLabel#sectionHeader {
                color: #64748B;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 8px 12px 4px 12px;
                border: none;
            }
            
            QPushButton#toggleButton {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #94A3B8;
                font-size: 16px;
            }
            
            QPushButton#toggleButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                color: #F1F5F9;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            
            QPushButton#sidebarButton {
                text-align: left;
                padding: 12px 14px;
                border: none;
                color: #94A3B8;
                background: transparent;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                margin: 2px 4px;
            }
            
            /* Collapsed sidebar buttons - center the icons */
            QPushButton#sidebarButton[collapsed="true"] {
                text-align: center;
                padding: 12px 8px;
                font-size: 18px;
            }
            
            QPushButton#sidebarButton:hover {
                background-color: rgba(255, 255, 255, 0.06);
                color: #F1F5F9;
            }
            
            QPushButton#sidebarButton[active="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.2), stop:1 rgba(59, 130, 246, 0.05));
                color: #60A5FA;
                font-weight: 600;
                border-left: 3px solid #3B82F6;
                padding-left: 11px;
            }
            
            QPushButton#sidebarButton[active="true"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.25), stop:1 rgba(59, 130, 246, 0.08));
            }
            
            QPushButton#sidebarButton:pressed {
                background-color: rgba(59, 130, 246, 0.15);
            }
        """)


class PartySelector(QDialog):
    """Reusable party selector dialog with search and add functionality"""
    def __init__(self, parties, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Party")
        self.setModal(True)
        self.selected_name = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Search"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Type to filter parties...")
        layout.addWidget(self.search)
        self.list = QListWidget()
        # Increase font size of the listbox for readability
        self.list.setStyleSheet("QListWidget { font-size: 16px; } QListWidget::item { padding: 6px; }")
        layout.addWidget(self.list)
        btns = QHBoxLayout()
        ok = QPushButton("Select")
        cancel = QPushButton("Cancel")
        btns.addStretch()
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.parties = [p.get('name', '') for p in (parties or []) if p.get('name')]
        self.list.addItems(self.parties)
        
        # Connect uppercase enforcement
        self.search.textChanged.connect(self.force_upper)
        self.search.textChanged.connect(self.filter)
        # Allow arrow key navigation from the search box
        self.search.installEventFilter(self)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

        # Select first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def force_upper(self, text):
        """Force uppercase input while preserving cursor position"""
        cursor_pos = self.search.cursorPosition()
        self.search.blockSignals(True)
        self.search.setText(text.upper())
        self.search.setCursorPosition(cursor_pos)
        self.search.blockSignals(False)

    def filter(self, text):
        text = text.strip().lower()
        self.list.clear()
        for name in self.parties:
            if text in name.lower():
                self.list.addItem(name)
        # Reset selection after filtering
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def eventFilter(self, obj, event):
        if obj is self.search and event.type() == QEvent.KeyPress:
            key = event.key()
            count = self.list.count()
            # Enter always accepts, even if no list items
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.accept()
                return True
            # Arrow navigation only when items exist
            if count > 0:
                current = self.list.currentRow()
                if key == Qt.Key_Down:
                    next_row = min(current + 1 if current >= 0 else 0, count - 1)
                    self.list.setCurrentRow(next_row)
                    return True
                if key == Qt.Key_Up:
                    prev_row = max(current - 1 if current > 0 else 0, 0)
                    self.list.setCurrentRow(prev_row)
                    return True
        return super().eventFilter(obj, event)

    def accept(self):
        item = self.list.currentItem()
        if item and item.text().strip():
            self.selected_name = item.text().strip()
        else:
            # If nothing selected, use the typed text from the search box
            typed = (self.search.text() or '').strip()
            if typed:
                # Check if the typed name exists in the parties list
                typed_upper = typed.upper()
                name_exists = any(party.upper() == typed_upper for party in self.parties)
                
                if not name_exists:
                    # Ask user if they want to add the new party
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Party Not Found")
                    msg_box.setIcon(QMessageBox.Question)
                    msg_box.setText(f"Party '{typed}' not found in Party List.")
                    msg_box.setInformativeText("Do you want to add this party?")
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setDefaultButton(QMessageBox.Yes)
                    
                    # Style the message box
                    msg_box.setStyleSheet("""
                        QMessageBox {
                            background-color: white;
                            color: #333;
                            font-size: 14px;
                        }
                        QMessageBox QLabel {
                            color: #333;
                            font-size: 14px;
                            padding: 10px;
                        }
                        QMessageBox QPushButton {
                            background-color: #2563eb;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 6px;
                            font-size: 14px;
                            font-weight: bold;
                            min-width: 80px;
                        }
                        QMessageBox QPushButton:hover {
                            background-color: #1d4ed8;
                        }
                        QMessageBox QPushButton:pressed {
                            background-color: #1e40af;
                        }
                    """)
                    
                    reply = msg_box.exec()
                    
                    if reply == QMessageBox.Yes:
                        # Import and open PartyDialog
                        try:
                            from ui.parties.party_form_dialog import PartyDialog
                            add_party_dialog = PartyDialog(self)
                            add_party_dialog.setWindowTitle(f"➕ Add New Party: {typed}")
                            
                            # Pre-fill the name field with the typed text
                            if hasattr(add_party_dialog, 'name_input'):
                                add_party_dialog.name_input.setText(typed)
                            
                            # Show the add party dialog
                            result = add_party_dialog.exec()
                            
                            if result == QDialog.Accepted and add_party_dialog.result_data:
                                # Party was successfully added, use the new party name
                                self.selected_name = add_party_dialog.result_data.get('name', typed)
                                
                                # Show styled success message
                                success_box = QMessageBox(self)
                                success_box.setWindowTitle("Success")
                                success_box.setIcon(QMessageBox.Information)
                                success_box.setText(f"Party '{self.selected_name}' has been added successfully!")
                                success_box.setStandardButtons(QMessageBox.Ok)
                                success_box.setStyleSheet("""
                                    QMessageBox {
                                        background-color: white;
                                        color: #333;
                                        font-size: 14px;
                                    }
                                    QMessageBox QLabel {
                                        color: #16a34a;
                                        font-size: 14px;
                                        font-weight: bold;
                                        padding: 10px;
                                    }
                                    QMessageBox QPushButton {
                                        background-color: #16a34a;
                                        color: white;
                                        border: none;
                                        padding: 8px 16px;
                                        border-radius: 6px;
                                        font-size: 14px;
                                        font-weight: bold;
                                        min-width: 80px;
                                    }
                                    QMessageBox QPushButton:hover {
                                        background-color: #15803d;
                                    }
                                    QMessageBox QPushButton:pressed {
                                        background-color: #14532d;
                                    }
                                """)
                                success_box.exec()
                            else:
                                # User cancelled party creation, don't close selector
                                return
                                
                        except ImportError as e:
                            QMessageBox.critical(
                                self,
                                "Error",
                                f"Could not open Add Party dialog: {str(e)}"
                            )
                            return
                        except Exception as e:
                            QMessageBox.critical(
                                self,
                                "Error",
                                f"An error occurred while adding party: {str(e)}"
                            )
                            return
                    else:
                        # User chose not to add party, don't close selector
                        return
                else:
                    # Party exists, use the typed name
                    self.selected_name = typed
        
        super().accept()


class ProductSelector(QDialog):
    """Reusable product selector dialog with search and add functionality"""
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Product")
        self.setModal(True)
        self.selected_name = None

        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Type to filter products...")
        layout.addWidget(self.search)
        self.list = QListWidget()
        # Increase font size of the listbox for readability
        self.list.setStyleSheet("QListWidget { font-size: 16px; } QListWidget::item { padding: 6px; }")
        layout.addWidget(self.list)
        btns = QHBoxLayout()
        ok = QPushButton("Select")
        cancel = QPushButton("Cancel")
        btns.addStretch()
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.products = [p.get('name', '') for p in (products or []) if p.get('name')]
        self.list.addItems(self.products)
        
        # Connect uppercase enforcement
        self.search.textChanged.connect(self.force_upper)
        self.search.textChanged.connect(self.filter)
        # Allow arrow key navigation from the search box
        self.search.installEventFilter(self)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

        # Select first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def force_upper(self, text):
        """Force uppercase input while preserving cursor position"""
        cursor_pos = self.search.cursorPosition()
        self.search.blockSignals(True)
        self.search.setText(text.upper())
        self.search.setCursorPosition(cursor_pos)
        self.search.blockSignals(False)

    def filter(self, text):
        text = text.strip().lower()
        self.list.clear()
        for name in self.products:
            if text in name.lower():
                self.list.addItem(name)
        # Reset selection after filtering
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def eventFilter(self, obj, event):
        if obj is self.search and event.type() == QEvent.KeyPress:
            key = event.key()
            count = self.list.count()
            # Enter always accepts, even if no list items
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.accept()
                return True
            # Arrow navigation only when items exist
            if count > 0:
                current = self.list.currentRow()
                if key == Qt.Key_Down:
                    next_row = min(current + 1 if current >= 0 else 0, count - 1)
                    self.list.setCurrentRow(next_row)
                    return True
                if key == Qt.Key_Up:
                    prev_row = max(current - 1 if current > 0 else 0, 0)
                    self.list.setCurrentRow(prev_row)
                    return True
        return super().eventFilter(obj, event)

    def accept(self):
        item = self.list.currentItem()
        if item and item.text().strip():
            self.selected_name = item.text().strip()
        else:
            # If nothing selected, use the typed text from the search box
            typed = (self.search.text() or '').strip()
            if typed:
                # Check if the typed name exists in the products list
                typed_upper = typed.upper()
                name_exists = any(product.upper() == typed_upper for product in self.products)
                
                if not name_exists:
                    # Ask user if they want to add the new product
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Product Not Found")
                    msg_box.setIcon(QMessageBox.Question)
                    msg_box.setText(f"Product '{typed}' not found in Product List.")
                    msg_box.setInformativeText("Do you want to add this product?")
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setDefaultButton(QMessageBox.Yes)
                    
                    # Style the message box
                    msg_box.setStyleSheet("""
                        QMessageBox {
                            background-color: white;
                            color: #333;
                            font-size: 14px;
                        }
                        QMessageBox QLabel {
                            color: #333;
                            font-size: 14px;
                            padding: 10px;
                            border: none;
                        }
                        QMessageBox QPushButton {
                            background-color: #2563eb;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 6px;
                            font-size: 14px;
                            font-weight: bold;
                            min-width: 80px;
                        }
                        QMessageBox QPushButton:hover {
                            background-color: #1d4ed8;
                        }
                        QMessageBox QPushButton:pressed {
                            background-color: #1e40af;
                        }
                    """)
                    
                    reply = msg_box.exec()
                    
                    if reply == QMessageBox.Yes:
                        # Import and open ProductDialog
                        try:
                            from ui.products.product_form_dialog import ProductDialog
                            add_product_dialog = ProductDialog(self)
                            add_product_dialog.setWindowTitle(f"➕ Add New Product: {typed}")
                            
                            # Pre-fill the name field with the typed text
                            if hasattr(add_product_dialog, 'name_input'):
                                add_product_dialog.name_input.setText(typed)
                            
                            # Show the add product dialog
                            result = add_product_dialog.exec()
                            
                            if result == QDialog.Accepted:
                                # Product was successfully added, use the typed name
                                self.selected_name = typed
                                
                                # Show styled success message
                                success_box = QMessageBox(self)
                                success_box.setWindowTitle("Success")
                                success_box.setIcon(QMessageBox.Information)
                                success_box.setText(f"Product '{self.selected_name}' has been added successfully!")
                                success_box.setStandardButtons(QMessageBox.Ok)
                                success_box.setStyleSheet("""
                                    QMessageBox {
                                        background-color: white;
                                        color: #333;
                                        font-size: 14px;
                                    }
                                    QMessageBox QLabel {
                                        color: #16a34a;
                                        font-size: 14px;
                                        font-weight: bold;
                                        padding: 10px;
                                    }
                                    QMessageBox QPushButton {
                                        background-color: #16a34a;
                                        color: white;
                                        border: none;
                                        padding: 8px 16px;
                                        border-radius: 6px;
                                        font-size: 14px;
                                        font-weight: bold;
                                        min-width: 80px;
                                    }
                                    QMessageBox QPushButton:hover {
                                        background-color: #15803d;
                                    }
                                    QMessageBox QPushButton:pressed {
                                        background-color: #14532d;
                                    }
                                """)
                                success_box.exec()
                            else:
                                # User cancelled product creation, don't close selector
                                return
                                
                        except ImportError as e:
                            QMessageBox.critical(
                                self,
                                "Error",
                                f"Could not open Add Product dialog: {str(e)}"
                            )
                            return
                        except Exception as e:
                            QMessageBox.critical(
                                self,
                                "Error",
                                f"An error occurred while adding product: {str(e)}"
                            )
                            return
                    else:
                        # User chose not to add product, don't close selector
                        return
                else:
                    # Product exists, use the typed name
                    self.selected_name = typed
        
        super().accept()


# ============================================================================
# Invoice Item Widget and Helper Functions
# ============================================================================

from PySide6.QtCore import Signal, QTimer
from theme import (
    get_row_number_style, get_product_input_style, get_hsn_readonly_style,
    get_unit_label_style, get_circle_button_style, get_item_widget_normal_style,
    get_error_highlight_style, get_success_highlight_style,
    get_item_row_even_style, get_item_row_odd_style, get_item_row_error_style,
    get_stock_indicator_style, get_action_icon_button_style,
    SUCCESS, DANGER, PRIMARY, PRIMARY_HOVER
)


def highlight_error(widget, message: str = "", duration_ms: int = 3000):
    """
    Highlight a widget with error styling temporarily.
    
    Args:
        widget: The Qt widget to highlight
        message: Optional tooltip message to display
        duration_ms: Duration in milliseconds before removing highlight
    """
    if widget is None:
        return
    
    original_style = widget.styleSheet()
    error_style = original_style + get_error_highlight_style()
    widget.setStyleSheet(error_style)
    
    if message:
        original_tooltip = widget.toolTip()
        widget.setToolTip(message)
        QTimer.singleShot(duration_ms, lambda: widget.setToolTip(original_tooltip))
    
    QTimer.singleShot(duration_ms, lambda: widget.setStyleSheet(original_style))


def highlight_success(widget, duration_ms: int = 2000):
    """
    Highlight a widget with success styling temporarily.
    
    Args:
        widget: The Qt widget to highlight
        duration_ms: Duration in milliseconds before removing highlight
    """
    if widget is None:
        return
    
    original_style = widget.styleSheet()
    success_style = original_style + get_success_highlight_style()
    widget.setStyleSheet(success_style)
    
    QTimer.singleShot(duration_ms, lambda: widget.setStyleSheet(original_style))


def show_validation_error(parent, widget, title: str, message: str, duration_ms: int = 3000):
    """
    Show a validation error with visual feedback.
    
    Args:
        parent: Parent widget for the message box
        widget: Widget to highlight (can be None)
        title: Message box title
        message: Error message
        duration_ms: Duration of highlight in milliseconds
    """
    if widget:
        highlight_error(widget, message, duration_ms)
        widget.setFocus()
    
    QMessageBox.warning(parent, title, message)


class ProductHighlightDelegate(QStyledItemDelegate):
    """Delegate to highlight matching text in product dropdown."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
    
    def set_search_text(self, text):
        self.search_text = text.upper() if text else ""
    
    def paint(self, painter, option, index):
        from PySide6.QtGui import QTextDocument, QAbstractTextDocumentLayout
        from PySide6.QtCore import QRectF
        
        # Get the text to display
        text = index.data(Qt.DisplayRole) or ""
        
        # Set up the style options
        self.initStyleOption(option, index)
        
        painter.save()
        
        # Draw selection/hover background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(PRIMARY))
            text_color = "white"
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor("#EFF6FF"))
            text_color = TEXT_PRIMARY
        else:
            text_color = TEXT_PRIMARY
        
        # Create HTML with highlighted text
        if self.search_text and self.search_text in text.upper():
            # Find and highlight matching text (case-insensitive)
            upper_text = text.upper()
            start = upper_text.find(self.search_text)
            if start >= 0:
                end = start + len(self.search_text)
                highlighted = (
                    f'<span style="color: {text_color};">'
                    f'{text[:start]}'
                    f'<span style="background-color: #FEF08A; color: #000; font-weight: bold;">'
                    f'{text[start:end]}'
                    f'</span>'
                    f'{text[end:]}'
                    f'</span>'
                )
            else:
                highlighted = f'<span style="color: {text_color};">{text}</span>'
        else:
            highlighted = f'<span style="color: {text_color};">{text}</span>'
        
        # Render HTML
        doc = QTextDocument()
        doc.setHtml(f'<div style="padding: 8px 12px; font-size: 14px;">{highlighted}</div>')
        
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)
        
        painter.restore()


class InvoiceItemWidget(QFrame):
    """
    Widget representing a single invoice line item.
    Contains product selection with dropdown, quantity, rate, discount, tax, and total fields.
    Product selection uses QComboBox with QCompleter similar to party search.
    
    Improvements:
    - Alternating row colors for better readability
    - Keyboard navigation (Tab through fields, Enter to add new row)
    - Stock display when selecting product
    - Duplicate product warning
    - Validation with red border on errors
    - Combined action buttons (icons)
    """
    
    # Signals
    item_changed = Signal()  # Emitted when any item data changes
    add_requested = Signal()  # Emitted when add button is clicked
    
    # Standard field height for consistency
    FIELD_HEIGHT = 34
    
    def __init__(self, products=None, parent_dialog=None, parent=None):
        super().__init__(parent)
        self.products = products or []
        self.parent_dialog = parent_dialog
        self.selected_product = None
        self._row_number = 0
        self._has_validation_error = False
        
        # Build product data maps for quick lookup
        self.product_data_map = {}  # name -> product data
        self.product_display_map = {}  # display_text -> name
        for p in self.products:
            name = p.get('name', '').strip()
            if name:
                self.product_data_map[name] = p
                # Create display text with price and stock info
                rate = p.get('sales_rate', 0) or 0
                stock = p.get('opening_stock', 0) or 0
                stock_text = f"📦 {stock}" if stock > 0 else "❌ 0"
                display_text = f"{name}  •  ₹{rate:,.2f}  •  {stock_text}"
                self.product_display_map[display_text] = name
        
        # Set initial style (will be updated based on row number)
        self.setStyleSheet(get_item_row_even_style())
        self.setFrameShape(QFrame.StyledPanel)
        
        self.setup_ui()
        self.connect_signals()
        self.setup_product_completer()
    
    def setup_ui(self):
        """Set up the item widget UI with standardized field heights."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)
        
        H = self.FIELD_HEIGHT  # Standard height for all fields
        
        # Row number (read-only) - matches "NO" header
        self.row_number_edit = QLineEdit("1")
        self.row_number_edit.setReadOnly(True)
        self.row_number_edit.setAlignment(Qt.AlignCenter)
        self.row_number_edit.setFixedWidth(40)
        self.row_number_edit.setFixedHeight(H)
        self.row_number_edit.setStyleSheet(get_row_number_style())
        main_layout.addWidget(self.row_number_edit)
        
        # Product ComboBox with search - matches "PRODUCT" header (580px total with stock)
        self.product_input = QComboBox()
        self.product_input.setEditable(True)
        self.product_input.setInsertPolicy(QComboBox.NoInsert)
        self.product_input.lineEdit().setPlaceholderText("🔍 Search product...")
        self.product_input.setFixedWidth(520)
        self.product_input.setFixedHeight(H)
        
        # Style the combobox - no thick focus border
        self.product_input.setStyleSheet(f"""
            QComboBox {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 10px;
                padding-right: 28px;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QComboBox:focus {{
                border: 1px solid {PRIMARY};
            }}
            QComboBox:hover {{
                border: 1px solid {PRIMARY_HOVER};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {TEXT_SECONDARY};
                margin-right: 8px;
            }}
        """)
        
        # Disable native completer - we'll use custom QCompleter
        self.product_input.setCompleter(None)
        
        main_layout.addWidget(self.product_input)
        
        # Stock indicator (shows after product selection) - part of product column
        self.stock_label = QLabel("")
        self.stock_label.setFixedWidth(60)
        self.stock_label.setFixedHeight(H - 10)
        self.stock_label.setAlignment(Qt.AlignCenter)
        self.stock_label.setVisible(False)
        main_layout.addWidget(self.stock_label)
        
        # HSN Code (read-only, auto-filled) - matches "HSN" header
        self.hsn_edit = QLineEdit()
        self.hsn_edit.setPlaceholderText("HSN")
        self.hsn_edit.setReadOnly(True)
        self.hsn_edit.setFixedWidth(80)
        self.hsn_edit.setFixedHeight(H)
        self.hsn_edit.setAlignment(Qt.AlignCenter)
        self.hsn_edit.setStyleSheet(get_hsn_readonly_style())
        main_layout.addWidget(self.hsn_edit)
        
        # Quantity - matches "QTY" header
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setFixedWidth(60)
        self.quantity_spin.setFixedHeight(H)
        self.quantity_spin.setStyleSheet(self._get_spinbox_style())
        main_layout.addWidget(self.quantity_spin)
        
        # Unit label - matches "UNIT" header
        self.unit_label = QLabel("Pcs")
        self.unit_label.setFixedWidth(55)
        self.unit_label.setFixedHeight(H)
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.setStyleSheet(get_unit_label_style())
        main_layout.addWidget(self.unit_label)
        
        # Rate - matches "RATE" header
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 9999999.99)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setValue(0)
        self.rate_spin.setPrefix("₹")
        self.rate_spin.setFixedWidth(90)
        self.rate_spin.setFixedHeight(H)
        self.rate_spin.setStyleSheet(self._get_spinbox_style())
        main_layout.addWidget(self.rate_spin)
        
        # Discount % - matches "DISC%" header
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setDecimals(1)
        self.discount_spin.setValue(0)
        self.discount_spin.setSuffix("%")
        self.discount_spin.setFixedWidth(70)
        self.discount_spin.setFixedHeight(H)
        self.discount_spin.setStyleSheet(self._get_spinbox_style())
        main_layout.addWidget(self.discount_spin)
        
        # Tax % - matches "TAX%" header
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 100)
        self.tax_spin.setDecimals(1)
        self.tax_spin.setValue(18)  # Default GST rate
        self.tax_spin.setSuffix("%")
        self.tax_spin.setFixedWidth(70)
        self.tax_spin.setFixedHeight(H)
        self.tax_spin.setStyleSheet(self._get_spinbox_style())
        main_layout.addWidget(self.tax_spin)
        
        # Total amount (read-only display) - matches "AMOUNT" header
        self.total_label = QLabel("₹0.00")
        self.total_label.setFixedWidth(100)
        self.total_label.setFixedHeight(H)
        self.total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.total_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                padding: 4px 8px;
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)
        main_layout.addWidget(self.total_label)
        
        # Action buttons container (combined +/-) - matches empty header
        action_container = QWidget()
        action_container.setFixedWidth(60)
        action_container.setStyleSheet("background: transparent;")
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(4)
        
        # Add button (+) - smaller icon button
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(26, 26)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFocusPolicy(Qt.NoFocus)
        self.add_btn.setStyleSheet(get_action_icon_button_style(SUCCESS))
        self.add_btn.setToolTip("Add new item row (Enter)")
        action_layout.addWidget(self.add_btn)
        
        # Remove button (-) - smaller icon button
        self.remove_btn = QPushButton("−")
        self.remove_btn.setFixedSize(26, 26)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setFocusPolicy(Qt.NoFocus)
        self.remove_btn.setStyleSheet(get_action_icon_button_style(DANGER))
        self.remove_btn.setToolTip("Remove this item (Del)")
        action_layout.addWidget(self.remove_btn)
        
        main_layout.addWidget(action_container)
    
    def _get_spinbox_style(self):
        """Get consistent spinbox style."""
        return f"""
            QSpinBox, QDoubleSpinBox {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {PRIMARY};
            }}
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 20px;
                border: none;
                background: transparent;
            }}
        """
    
    def setup_product_completer(self):
        """Set up the product autocomplete with QCompleter."""
        # Build display list with price info
        display_names = list(self.product_display_map.keys())
        # Also add plain names for direct matching
        display_names.extend(self.product_data_map.keys())
        
        # Create completer
        self.product_completer = QCompleter(display_names, self)
        self.product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.product_completer.setFilterMode(Qt.MatchContains)
        self.product_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.product_completer.setMaxVisibleItems(10)
        
        # Style the completer popup
        self.product_completer.popup().setStyleSheet(f"""
            QListView {{
                background: {WHITE};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                padding: 4px;
                font-size: 14px;
                outline: none;
            }}
            QListView::item {{
                padding: 10px 14px;
                min-height: 36px;
                border: none;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListView::item:hover {{
                background: #EFF6FF;
            }}
            QListView::item:selected {{
                background: {PRIMARY};
                color: {WHITE};
            }}
        """)
        
        # Set completer on line edit
        self.product_input.lineEdit().setCompleter(self.product_completer)
        
        # Connect completer activation
        self.product_completer.activated.connect(self._on_product_completer_activated)
        
        # Override showPopup to use completer
        original_show_popup = self.product_input.showPopup
        def custom_show_popup():
            self.product_completer.setCompletionPrefix("")
            self.product_completer.complete()
            self._position_completer_popup()
        self.product_input.showPopup = custom_show_popup
    
    def _position_completer_popup(self):
        """Position the completer popup with dynamic screen-aware positioning.
        This matches the party completer positioning approach.
        """
        try:
            if not hasattr(self, 'product_completer'):
                return
                
            popup = self.product_completer.popup()
            
            # Get the combobox position in global coordinates
            combo_rect = self.product_input.rect()
            global_pos = self.product_input.mapToGlobal(combo_rect.bottomLeft())
            
            # Set popup width (wider to show product info)
            popup_width = max(self.product_input.width(), 400)
            popup.setFixedWidth(popup_width)
            
            # Calculate position - use bottomLeft() so we start BELOW the search box
            gap = 25  # Gap between search box and popup (same as party completer)
            y_pos = global_pos.y() + gap
            x_pos = global_pos.x()
            
            # Get screen geometry for bounds checking
            screen = QApplication.screenAt(global_pos)
            if screen:
                screen_geometry = screen.availableGeometry()
                popup_height = min(popup.sizeHint().height(), 300)  # Max 300px height
                
                # Check if popup would go below screen - position above instead
                if y_pos + popup_height > screen_geometry.bottom():
                    top_pos = self.product_input.mapToGlobal(combo_rect.topLeft())
                    y_pos = top_pos.y() - popup_height - gap
                
                # Check if popup would go off right edge
                if x_pos + popup_width > screen_geometry.right():
                    x_pos = screen_geometry.right() - popup_width - 10
            
            # Move popup to calculated position
            popup.move(x_pos, y_pos)
        except Exception as e:
            print(f"Position completer popup error: {e}")
    
    def connect_signals(self):
        """Connect widget signals to handlers."""
        # Recalculate on value changes
        self.quantity_spin.valueChanged.connect(self.on_value_changed)
        self.rate_spin.valueChanged.connect(self.on_value_changed)
        self.discount_spin.valueChanged.connect(self.on_value_changed)
        self.tax_spin.valueChanged.connect(self.on_value_changed)
        
        # Product text changes
        self.product_input.lineEdit().textEdited.connect(self._on_product_text_edited)
        
        # Add button
        self.add_btn.clicked.connect(self.add_requested.emit)
        
        # Install event filter for keyboard navigation on all editable widgets
        self.product_input.lineEdit().installEventFilter(self)
        self.product_input.installEventFilter(self)
        self.quantity_spin.installEventFilter(self)
        self.rate_spin.installEventFilter(self)
        self.discount_spin.installEventFilter(self)
        self.tax_spin.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events for navigation and shortcuts.
        
        - Tab: Move to next field
        - Enter: Move to next field (add new row only when on last field - tax)
        - Down: Open product dropdown
        - Delete: Trigger remove action
        """
        try:
            from PySide6.QtCore import QEvent
            
            is_product_input = (obj == self.product_input or obj == self.product_input.lineEdit())
            
            if event.type() == QEvent.KeyPress:
                key = event.key()
                
                # Product input specific handling
                if is_product_input:
                    # Down arrow: open dropdown
                    if key == Qt.Key_Down:
                        if not self.product_completer.popup().isVisible():
                            self.product_input.showPopup()
                            return True
                    
                    # Tab or Enter: confirm selection and move to quantity
                    elif key in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
                        text = self.product_input.currentText().strip()
                        if text:
                            self._select_product_by_text(text)
                            # Move focus to quantity
                            self.quantity_spin.setFocus()
                            self.quantity_spin.selectAll()
                            return True
                    
                    # Escape: clear/close dropdown
                    elif key == Qt.Key_Escape:
                        if self.product_completer.popup().isVisible():
                            self.product_completer.popup().hide()
                            return True
                
                # Enter on quantity: move to rate
                elif obj == self.quantity_spin and key in (Qt.Key_Return, Qt.Key_Enter):
                    self.rate_spin.setFocus()
                    self.rate_spin.selectAll()
                    return True
                
                # Enter on rate: move to discount
                elif obj == self.rate_spin and key in (Qt.Key_Return, Qt.Key_Enter):
                    self.discount_spin.setFocus()
                    self.discount_spin.selectAll()
                    return True
                
                # Enter on discount: move to tax
                elif obj == self.discount_spin and key in (Qt.Key_Return, Qt.Key_Enter):
                    self.tax_spin.setFocus()
                    self.tax_spin.selectAll()
                    return True
                
                # Enter on tax field adds new row
                elif obj == self.tax_spin and key in (Qt.Key_Return, Qt.Key_Enter):
                    # Validate current row first
                    if self.validate():
                        self.add_requested.emit()
                        return True
                
                # Delete key anywhere triggers remove (if allowed)
                elif key == Qt.Key_Delete and event.modifiers() & Qt.ControlModifier:
                    self.remove_btn.click()
                    return True
                
        except Exception as e:
            print(f"Event filter error: {e}")
        
        return super().eventFilter(obj, event)
    
    def _on_product_text_edited(self, text):
        """Handle product text editing for suggestions."""
        try:
            if text and len(text) >= 1:
                # Position popup after typing
                QTimer.singleShot(0, self._position_completer_popup)
        except Exception as e:
            print(f"Product text edited error: {e}")
    
    def _on_product_completer_activated(self, text):
        """Handle product selection from completer dropdown."""
        try:
            self._select_product_by_text(text)
            # Move focus to quantity after selection
            QTimer.singleShot(50, lambda: self.quantity_spin.setFocus())
        except Exception as e:
            print(f"Product completer activation error: {e}")
    
    def _select_product_by_text(self, text):
        """Select a product by its display text or name.
        
        Also shows stock indicator and checks for duplicate products.
        """
        try:
            # Extract product name from display text
            product_name = self.product_display_map.get(text, text)
            
            # If text contains price info separator, extract name
            if "  •  " in product_name:
                product_name = product_name.split("  •  ")[0].strip()
            
            # Find matching product
            product_data = self.product_data_map.get(product_name)
            
            if product_data:
                # Check for duplicate product in other rows
                if self._check_duplicate_product(product_data.get('id')):
                    QMessageBox.warning(
                        self, "Duplicate Product",
                        f"⚠️ '{product_name}' is already added to this invoice.\n\n"
                        "Consider updating the quantity in the existing row instead."
                    )
                    # Still allow, but show warning
                
                self.selected_product = product_data
                
                # Set just the product name (without price)
                self.product_input.blockSignals(True)
                self.product_input.setCurrentText(product_name)
                self.product_input.blockSignals(False)
                
                # Auto-fill fields
                self.hsn_edit.setText(product_data.get('hsn_code', '') or '')
                self.rate_spin.setValue(product_data.get('sales_rate', 0) or 0)
                self.unit_label.setText(product_data.get('unit', 'Pcs') or 'Pcs')
                
                # Show stock indicator
                self._update_stock_indicator(product_data)
                
                # Set tax rate based on parent dialog's tax type
                tax_rate = product_data.get('tax_rate', 18) or 18
                if self.parent_dialog:
                    if hasattr(self.parent_dialog, '_tax_type') and self.parent_dialog._tax_type == "NON_GST":
                        tax_rate = 0
                    elif hasattr(self.parent_dialog, 'gst_combo'):
                        if self.parent_dialog.gst_combo.currentText() == "Non-GST":
                            tax_rate = 0
                
                self.tax_spin.setValue(tax_rate)
                self.calculate_total()
                
                # Clear any validation error
                self._clear_validation_error()
                
                # Visual feedback - green border briefly
                self._show_selection_success()
        except Exception as e:
            print(f"Select product by text error: {e}")
    
    def _check_duplicate_product(self, product_id) -> bool:
        """Check if the product is already added in another row.
        
        Returns:
            True if duplicate found, False otherwise.
        """
        if not product_id or not self.parent_dialog:
            return False
        
        try:
            items_layout = self.parent_dialog.items_layout
            for i in range(items_layout.count()):
                widget = items_layout.itemAt(i).widget()
                if widget and isinstance(widget, InvoiceItemWidget) and widget != self:
                    if widget.selected_product and widget.selected_product.get('id') == product_id:
                        return True
        except Exception as e:
            print(f"Duplicate check error: {e}")
        
        return False
    
    def _update_stock_indicator(self, product_data):
        """Update the stock indicator label based on product stock."""
        try:
            stock = product_data.get('opening_stock', 0) or 0
            
            if stock > 0:
                self.stock_label.setText(f"📦 {stock}")
                self.stock_label.setStyleSheet(get_stock_indicator_style(True))
                self.stock_label.setToolTip(f"Available stock: {stock}")
            else:
                self.stock_label.setText("❌ 0")
                self.stock_label.setStyleSheet(get_stock_indicator_style(False))
                self.stock_label.setToolTip("Out of stock!")
            
            self.stock_label.setVisible(True)
        except Exception as e:
            print(f"Update stock indicator error: {e}")
    
    def _show_selection_success(self):
        """Show brief visual feedback on successful selection."""
        try:
            original_style = self.product_input.styleSheet()
            success_style = original_style.replace(f"border: 1px solid {BORDER}", "border: 2px solid #10B981")
            self.product_input.setStyleSheet(success_style)
            QTimer.singleShot(1500, lambda: self.product_input.setStyleSheet(original_style))
        except:
            pass
    
    def on_value_changed(self):
        """Handle changes to numeric values."""
        self.calculate_total()
        self.item_changed.emit()
    
    def calculate_total(self):
        """Calculate and display the line item total."""
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()
        discount_percent = self.discount_spin.value()
        tax_percent = self.tax_spin.value()
        
        # Calculate subtotal
        subtotal = quantity * rate
        
        # Apply discount
        discount_amount = subtotal * (discount_percent / 100)
        after_discount = subtotal - discount_amount
        
        # Apply tax
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        
        self.total_label.setText(f"₹{total:,.2f}")
    
    def set_row_number(self, number: int):
        """Set the row number display and apply alternating row color."""
        self._row_number = number
        self.row_number_edit.setText(str(number))
        
        # Apply alternating row colors (odd/even)
        if not self._has_validation_error:
            if number % 2 == 0:
                self.setStyleSheet(get_item_row_even_style())
            else:
                self.setStyleSheet(get_item_row_odd_style())
    
    def validate(self) -> bool:
        """Validate the item row.
        
        Returns:
            True if valid, False if there are validation errors.
        """
        product_name = self.product_input.currentText().strip()
        
        if not product_name:
            self._show_validation_error("Product is required")
            return False
        
        if self.rate_spin.value() <= 0:
            self._show_validation_error("Rate must be greater than 0")
            self.rate_spin.setFocus()
            return False
        
        self._clear_validation_error()
        return True
    
    def _show_validation_error(self, message: str = ""):
        """Show validation error with red border on the row."""
        self._has_validation_error = True
        self.setStyleSheet(get_item_row_error_style())
        if message:
            self.setToolTip(f"⚠️ {message}")
    
    def _clear_validation_error(self):
        """Clear validation error styling."""
        self._has_validation_error = False
        self.setToolTip("")
        # Restore alternating row color
        if self._row_number % 2 == 0:
            self.setStyleSheet(get_item_row_even_style())
        else:
            self.setStyleSheet(get_item_row_odd_style())
    
    def get_item_data(self) -> dict:
        """
        Get the item data as a dictionary.
        
        Returns:
            dict: Item data including product, quantity, rate, discounts, tax, etc.
                  Returns None if no product is selected.
        """
        product_name = self.product_input.currentText().strip()
        if not product_name:
            return None
        
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()
        discount_percent = self.discount_spin.value()
        tax_percent = self.tax_spin.value()
        
        # Calculate amounts
        subtotal = quantity * rate
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * (tax_percent / 100)
        total = taxable_amount + tax_amount
        
        return {
            'product_name': product_name,
            'product_id': self.selected_product.get('id') if self.selected_product else None,
            'hsn_code': self.hsn_edit.text(),
            'unit': self.unit_label.text(),
            'quantity': quantity,
            'rate': rate,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'tax_percent': tax_percent,
            'tax_amount': tax_amount,
            'taxable_amount': taxable_amount,
            'total': total,
        }
    
    def set_item_data(self, data: dict):
        """
        Set item data from a dictionary.
        
        Args:
            data: Dictionary containing item data
        """
        if 'product_name' in data:
            self.product_input.setCurrentText(data['product_name'])
        if 'hsn_code' in data:
            self.hsn_edit.setText(data['hsn_code'])
        if 'unit' in data:
            self.unit_label.setText(data['unit'])
        if 'quantity' in data:
            self.quantity_spin.setValue(data['quantity'])
        if 'rate' in data:
            self.rate_spin.setValue(data['rate'])
        if 'discount_percent' in data:
            self.discount_spin.setValue(data['discount_percent'])
        if 'tax_percent' in data:
            self.tax_spin.setValue(data['tax_percent'])
        
        self.calculate_total()
    
    def set_product_by_data(self, product_data: dict):
        """
        Set product directly from product data dictionary.
        Used by quick_add_product feature.
        
        Args:
            product_data: Product dictionary with name, hsn_code, sales_rate, etc.
        """
        if not product_data:
            return
        
        self.selected_product = product_data
        name = product_data.get('name', '')
        
        self.product_input.blockSignals(True)
        self.product_input.setCurrentText(name)
        self.product_input.blockSignals(False)
        
        self.hsn_edit.setText(product_data.get('hsn_code', '') or '')
        self.rate_spin.setValue(product_data.get('sales_rate', 0) or 0)
        self.unit_label.setText(product_data.get('unit', 'Piece') or 'Piece')
        
        # Set tax rate based on parent dialog's tax type
        tax_rate = product_data.get('tax_rate', 18) or 18
        if self.parent_dialog:
            if hasattr(self.parent_dialog, '_tax_type') and self.parent_dialog._tax_type == "NON_GST":
                tax_rate = 0
        
        self.tax_spin.setValue(tax_rate)
        self.calculate_total()
        self.item_changed.emit()

