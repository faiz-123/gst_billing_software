"""
Standalone InvoiceDialog for creating/editing invoices.
Extracted from screens/invoices.py to avoid a huge single file.
"""

import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QScrollArea, QSplitter,
    QAbstractItemView, QMenu, QAction, QShortcut, QListWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QKeySequence
from PyQt5.QtWidgets import QCompleter
from ui.parties.party_selector_dialog import PartySelector, ProductSelector

from widgets import CustomButton, CustomTable, CustomInput, FormField
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER, get_calendar_stylesheet
)
from core.db.sqlite_db import db


def map_user_selection_to_internal(invoice_selection: str) -> str:
    """Map user-facing invoice selection to internal invoice type.

    User selections:
      - 'GST - Same State' -> 'TAX Local'
      - 'GST - Other State' -> 'TAX InterState'
      - ' Non-GST' -> 'Bill of Supply' (or 'Retail' depending on bill type)
    """
    s = (invoice_selection or '').strip().lower()
    if s == 'GST - Same State' or s == 'gst same state' or s == 'gst (same state)':
        return 'TAX Local'
    if s == 'GST - Other State' or s == 'gst other state' or s == 'gst (other state)':
        return 'TAX InterState'
    # Default for anything that implies no GST
    if ' Non-GST' in s or 'non-gst' in s or 'without' in s:
        return 'Bill of Supply'
    # Preserve existing simple GST/Non-GST choices
    if s in ['gst', 'gst only']:
        return 'TAX Local'
    if s in ['non-gst', 'nongst', 'non gst']:
        return 'Bill of Supply'
    return invoice_selection


# ============================================================================
# COMMON STYLES - Centralized styling for consistency
# ============================================================================
COMMON_STYLES = {
    'label': f"""
        QLabel {{
            font-weight: 600;
            color: {TEXT_PRIMARY};
            font-size: 14px;
            border: none;
            background: transparent;
            margin: 0;
            padding: 2px;
        }}
    """,
    'input': f"""
        QLineEdit, QDateEdit, QComboBox, QTextEdit {{
            border: 2px solid {BORDER};
            border-radius: 8px;
            padding: 12px 15px;
            background: {WHITE};
            font-size: 15px;
            color: {TEXT_PRIMARY};
        }}
        QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {{
            border: 2px solid {PRIMARY};
        }}
    """,
    'input_error': f"""
        QLineEdit, QDateEdit, QComboBox {{
            border: 2px solid {DANGER};
            border-radius: 8px;
            padding: 12px 15px;
            background: #FEF2F2;
            font-size: 15px;
            color: {TEXT_PRIMARY};
        }}
    """,
    'input_success': f"""
        QLineEdit, QDateEdit, QComboBox {{
            border: 2px solid {SUCCESS};
            border-radius: 8px;
            padding: 12px 15px;
            background: #F0FDF4;
            font-size: 15px;
            color: {TEXT_PRIMARY};
        }}
    """,
    'amount_label': f"""
        QLabel {{
            font-weight: bold;
            color: {PRIMARY};
            font-size: 14px;
            padding: 8px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid {BORDER};
            border-radius: 6px;
        }}
    """,
    'widget_base': f"""
        QComboBox, QDoubleSpinBox, QSpinBox {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 6px 8px;
            background: {WHITE};
            font-size: 14px;
            color: {TEXT_PRIMARY};
        }}
        QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
            border: 2px solid {PRIMARY};
            background: #F8FAFC;
        }}
        QComboBox:hover, QDoubleSpinBox:hover, QSpinBox:hover {{
            border-color: {PRIMARY};
        }}
    """,
}


# ============================================================================
# VALIDATION HELPERS - Better user feedback
# ============================================================================
def highlight_error(widget, message: str = None, duration_ms: int = 3000):
    """
    Highlight a widget with error styling and optional tooltip.
    Auto-clears after duration_ms milliseconds.
    """
    if not widget:
        return
    
    original_style = widget.styleSheet()
    original_tooltip = widget.toolTip()
    
    # Apply error style
    error_style = f"""
        border: 2px solid {DANGER} !important;
        background: #FEF2F2 !important;
    """
    widget.setStyleSheet(widget.styleSheet() + error_style)
    
    if message:
        widget.setToolTip(f"⚠️ {message}")
    
    # Shake animation effect (visual feedback)
    try:
        from PyQt5.QtCore import QPropertyAnimation, QPoint
        original_pos = widget.pos()
        
        def shake():
            anim = QPropertyAnimation(widget, b"pos")
            anim.setDuration(50)
            anim.setLoopCount(3)
            anim.setStartValue(original_pos)
            anim.setKeyValueAt(0.25, original_pos + QPoint(5, 0))
            anim.setKeyValueAt(0.75, original_pos + QPoint(-5, 0))
            anim.setEndValue(original_pos)
            anim.start()
            widget._shake_anim = anim  # Keep reference
        
        shake()
    except Exception:
        pass  # Animation is optional enhancement
    
    # Auto-clear after duration
    def clear_error():
        try:
            widget.setStyleSheet(original_style)
            widget.setToolTip(original_tooltip)
        except Exception:
            pass
    
    QTimer.singleShot(duration_ms, clear_error)


def highlight_success(widget, duration_ms: int = 2000):
    """
    Briefly highlight a widget with success styling.
    """
    if not widget:
        return
    
    original_style = widget.styleSheet()
    
    success_style = f"""
        border: 2px solid {SUCCESS} !important;
        background: #F0FDF4 !important;
    """
    widget.setStyleSheet(widget.styleSheet() + success_style)
    
    def clear_success():
        try:
            widget.setStyleSheet(original_style)
        except Exception:
            pass
    
    QTimer.singleShot(duration_ms, clear_success)


def number_to_words_indian(number: float) -> str:
    """
    Convert a number to words in Indian format (Lakhs, Crores).
    Example: 123456.78 -> "One Lakh Twenty Three Thousand Four Hundred Fifty Six and Seventy Eight Paise"
    """
    if number == 0:
        return "Zero Rupees Only"
    
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
            'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    def two_digits(n):
        if n < 20:
            return ones[n]
        else:
            return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')
    
    def three_digits(n):
        if n >= 100:
            return ones[n // 100] + ' Hundred' + (' ' + two_digits(n % 100) if n % 100 else '')
        else:
            return two_digits(n)
    
    # Handle negative numbers
    if number < 0:
        return "Minus " + number_to_words_indian(-number)
    
    # Split into rupees and paise
    rupees = int(number)
    paise = round((number - rupees) * 100)
    
    if rupees == 0:
        words = ""
    else:
        # Indian numbering: Crore (10^7), Lakh (10^5), Thousand (10^3), Hundred (10^2)
        crores = rupees // 10000000
        rupees %= 10000000
        lakhs = rupees // 100000
        rupees %= 100000
        thousands = rupees // 1000
        rupees %= 1000
        hundreds = rupees
        
        parts = []
        if crores:
            parts.append(two_digits(crores) + ' Crore')
        if lakhs:
            parts.append(two_digits(lakhs) + ' Lakh')
        if thousands:
            parts.append(two_digits(thousands) + ' Thousand')
        if hundreds:
            parts.append(three_digits(hundreds))
        
        words = ' '.join(parts) + ' Rupees'
    
    # Add paise if present
    if paise > 0:
        if words:
            words += ' and ' + two_digits(paise) + ' Paise'
        else:
            words = two_digits(paise) + ' Paise'
    
    return words + ' Only' if words else 'Zero Rupees Only'


def show_validation_error(parent, field_widget, title: str, message: str):
    """
    Show validation error message and highlight the field.
    """
    highlight_error(field_widget, message)
    QMessageBox.warning(parent, title, f"⚠️ {message}")
    if field_widget:
        field_widget.setFocus()


class InvoiceItemWidget(QWidget):
    """Enhanced widget for invoice line items with better styling and validation"""
    
    item_changed = pyqtSignal()  # Signal for when item data changes
    add_requested = pyqtSignal()  # Signal to request adding a new item row
    
    def __init__(self, item_data=None, products=None, parent_dialog=None):
        super().__init__()
        self.products = products or []
        self.parent_dialog = parent_dialog  # Reference to InvoiceDialog
        self._product_selector_active = False
        self.setup_ui()
        if item_data:
            self.populate_data(item_data)
        self.setFixedHeight(50)  # Consistent height for all items
    
    def setup_ui(self):
        """Setup enhanced item widget UI with better styling"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(1)
        
        # Enhanced styling for all widgets
        widget_style = f"""
            QComboBox, QDoubleSpinBox, QSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
                border: 2px solid {PRIMARY};
                background: #F8FAFC;
            }}
            QComboBox:hover, QDoubleSpinBox:hover, QSpinBox:hover {{
                border-color: {PRIMARY};
            }}
        """

        # Row number (read-only textbox) aligned with "No" header
        self.row_no_edit = QLineEdit()
        self.row_no_edit.setReadOnly(True)
        self.row_no_edit.setFixedWidth(100)
        self.row_no_edit.setFixedHeight(45)
        self.row_no_edit.setAlignment(Qt.AlignCenter)
        self.row_no_edit.setFocusPolicy(Qt.NoFocus)
        self.row_no_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 0;
                border-radius: 6px;
                padding: 0;
                background: {BACKGROUND};
                color: {TEXT_SECONDARY};
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(self.row_no_edit)
        
        # Product selection: QLineEdit with suggestion box (QCompleter)
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("🛍️ Type to select product…")
        self.product_input.setFixedWidth(500)
        self.product_input.setFixedHeight(40)
        self.product_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {WHITE};
                font-size: 14px;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY};
                background: #F8FAFC;
            }}
        """)
        # Build completer data
        self._product_map = {}
        product_names = []
        for p in (self.products or []):
            name = p.get('name', '').strip()
            if name:
                self._product_map[name] = p
                product_names.append(name)

        layout.addWidget(self.product_input)
        layout.setSpacing(20)

        # Install event filter for Enter key navigation
        self.product_input.installEventFilter(self)

        try:
            self.product_input.textEdited.connect(self.on_product_search_edited)
        except Exception:
            pass
        # Enter opens selector
        try:
            self.product_input.returnPressed.connect(self.open_product_selector)
        except Exception:
            pass

        # HSN No entry box - made read-only
        self.hsn_edit = QLineEdit()
        self.hsn_edit.setPlaceholderText("HSN")
        self.hsn_edit.setReadOnly(True)  # Make HSN field read-only
        self.hsn_edit.setFixedWidth(100)
        self.hsn_edit.setFixedHeight(40)
        self.hsn_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {BACKGROUND};
                font-size: 14px;
                color: {TEXT_SECONDARY};
            }}
        """)
        self.hsn_edit.setToolTip("HSN code for the product (read-only)")
        layout.addWidget(self.hsn_edit)

        
        # Quantity with validation
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setFixedWidth(100)
        self.quantity_spin.setFixedHeight(40)
        self.quantity_spin.setStyleSheet(widget_style)
        self.quantity_spin.setToolTip("Enter quantity")
        self.quantity_spin.valueChanged.connect(self.calculate_total)
        # Handle Enter key to move to next field
        self.quantity_spin.installEventFilter(self)
        layout.addWidget(self.quantity_spin)
        
        # Unit display with better styling
        self.unit_label = QLabel("Piece")
        self.unit_label.setFixedWidth(85)
        self.unit_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                font-style: italic;
                padding: 6px;
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        self.unit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.unit_label)
        
        # Rate with currency prefix
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 999999.99)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setPrefix("₹")
        self.rate_spin.setFixedWidth(110)
        self.rate_spin.setFixedHeight(40)
        self.rate_spin.setStyleSheet(widget_style)
        self.rate_spin.setToolTip("Enter rate per unit")
        self.rate_spin.valueChanged.connect(self.calculate_total)
        # Handle Enter key to move to next field
        self.rate_spin.installEventFilter(self)
        layout.addWidget(self.rate_spin)
        
        # Discount percentage
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setSuffix("%")
        self.discount_spin.setFixedWidth(110)
        self.discount_spin.setFixedHeight(40)
        self.discount_spin.setStyleSheet(widget_style)
        self.discount_spin.setToolTip("Discount percentage")
        self.discount_spin.valueChanged.connect(self.calculate_total)
        # Handle Enter key to add new row when pressed on last editable field
        self.discount_spin.installEventFilter(self)
        layout.addWidget(self.discount_spin)
        
        # Tax percentage - made read-only
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 100)
        self.tax_spin.setDecimals(2)
        self.tax_spin.setValue(18)
        self.tax_spin.setSuffix("%")
        self.tax_spin.setReadOnly(True)  # Make tax field read-only
        self.tax_spin.setFixedWidth(110)
        self.tax_spin.setFixedHeight(40)
        self.tax_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 8px;
                background: {BACKGROUND};
                font-size: 14px;
                color: {TEXT_SECONDARY};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 0px;
                height: 0px;
            }}
        """)
        self.tax_spin.setToolTip("Tax percentage (GST) - read-only")
        self.tax_spin.valueChanged.connect(self.calculate_total)
        layout.addWidget(self.tax_spin)        
        
        # Amount display with enhanced styling
        self.amount_label = QLabel("₹0.00")
        self.amount_label.setFixedWidth(110)
        self.amount_label.setFixedHeight(45)
        self.amount_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold; 
                color: {PRIMARY};
                font-size: 14px;
                padding: 8px;
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        self.amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.amount_label)

        # Enhanced add button
        self.add_btn = QPushButton("➕")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.setAutoDefault(False)  # Prevent Enter key from triggering this button
        self.add_btn.setDefault(False)      # Ensure this is not the default button
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: {WHITE};
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: #059669;
                border: none;
            }}
            QPushButton:pressed {{
                background: #B91C1C;
                border: none;
            }}
        """)
        self.add_btn.setToolTip("Add this item")
        # Emit signal so parent can add a new row
        self.add_btn.clicked.connect(self.add_requested.emit)
        layout.addWidget(self.add_btn)

        # Enhanced remove button
        self.remove_btn = QPushButton("✖")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setAutoDefault(False)  # Prevent Enter key from triggering this button
        self.remove_btn.setDefault(False)      # Ensure this is not the default button
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER};
                color: {WHITE};
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: #DC2626;

            }}
            QPushButton:pressed {{
                background: #B91C1C;
            }}
        """)
        self.remove_btn.setToolTip("Remove this item")
        layout.addWidget(self.remove_btn)

        # layout.setAlignment(self.product_combo, Qt.AlignLeft)
        layout.setAlignment(self.hsn_edit, Qt.AlignLeft)
        layout.setAlignment(self.quantity_spin, Qt.AlignLeft)
        layout.setAlignment(self.unit_label, Qt.AlignLeft)
        layout.setAlignment(self.rate_spin, Qt.AlignLeft)
        layout.setAlignment(self.discount_spin, Qt.AlignLeft)
        layout.setAlignment(self.tax_spin, Qt.AlignLeft)
        layout.setAlignment(self.remove_btn, Qt.AlignCenter)
        layout.setAlignment(self.amount_label, Qt.AlignCenter)

    def set_row_number(self, n: int):
        """Set the display number for this row (1-based)."""
        try:
            self.row_no_edit.setText(str(n))
        except Exception:
            pass

    def eventFilter(self, obj, event):
        """Handle Enter key navigation within item row"""
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QKeyEvent
        
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Define the tab order for editable fields
                fields = [self.product_input, self.quantity_spin, self.rate_spin, self.discount_spin]
                
                try:
                    current_index = fields.index(obj)
                    
                    # Special handling for product input
                    if obj == self.product_input:
                        typed_text = self.product_input.text().strip()
                        if typed_text:
                            # Check if product is already selected (exact match exists)
                            exact_match = None
                            for product_name in self._product_map.keys():
                                if product_name.upper() == typed_text.upper():
                                    exact_match = product_name
                                    break
                            
                            if exact_match:
                                # Product already selected, move to quantity
                                self.quantity_spin.setFocus()
                                self.quantity_spin.selectAll()
                                return True
                            else:
                                # No exact match, let returnPressed open selector
                                return False
                        else:
                            # No text, move to next field
                            self.quantity_spin.setFocus()
                            self.quantity_spin.selectAll()
                            return True
                    
                    if current_index < len(fields) - 1:
                        # Move to next field
                        next_field = fields[current_index + 1]
                        next_field.setFocus()
                        if hasattr(next_field, 'selectAll'):
                            next_field.selectAll()
                    else:
                        # Last field - add new row
                        self.add_requested.emit()
                    return True  # Event handled
                except ValueError:
                    # obj not in fields list, let default handling occur
                    pass
        
        # Call parent event filter
        return super().eventFilter(obj, event)

    def on_product_search_edited(self, text: str):
        """Open ProductSelector when user types in the product search box.
        Prefill selector search with typed text and avoid opening multiple times.
        """
        try:
            # Check if party is selected first
            if self.parent_dialog and hasattr(self.parent_dialog, 'party_search'):
                party_text = self.parent_dialog.party_search.text().strip()
                if not party_text:
                    # Clear product input and show error
                    self.product_input.blockSignals(True)
                    self.product_input.clear()
                    self.product_input.blockSignals(False)
                    highlight_error(self.parent_dialog.party_search, "Please select a party first")
                    self.parent_dialog.party_search.setFocus()
                    return
            
            if self._product_selector_active:
                return
            if not text or not text.strip():
                return
            self._product_selector_active = True
            selected = self._open_product_selector_dialog(prefill_text=text)
            if selected:
                # Set chosen product name back to the input without re-triggering textEdited
                old_state = self.product_input.blockSignals(True)
                try:
                    self.product_input.setText(selected)
                    # Immediately apply selected product data to rate/discount/tax/unit
                    try:
                        self.on_product_selected(selected)
                    except Exception as _e:
                        print(f"on_product_selected failed: {_e}")
                finally:
                    self.product_input.blockSignals(old_state)
                
                # Focus on quantity field after product selection
                self.quantity_spin.setFocus()
                self.quantity_spin.selectAll()
        except Exception as e:
            print(f"Product search edit handler error: {e}")
        finally:
            self._product_selector_active = False

    # The following helper sections mirror the original dialog
    def open_product_selector(self):
        try:
            # Check if party is selected first
            if self.parent_dialog and hasattr(self.parent_dialog, 'party_search'):
                party_text = self.parent_dialog.party_search.text().strip()
                if not party_text:
                    highlight_error(self.parent_dialog.party_search, "Please select a party first")
                    self.parent_dialog.party_search.setFocus()
                    return
            
            # Check if typed text exactly matches a product name
            typed_text = self.product_input.text().strip()
            exact_match = None
            
            # Check for exact match (case-insensitive)
            for product_name in self._product_map.keys():
                if product_name.upper() == typed_text.upper():
                    exact_match = product_name
                    break
            
            if exact_match:
                # Direct match found, no need to open selector
                selected = exact_match
                self.product_input.setText(selected)
                # Apply selected product to update dependent fields
                try:
                    self.on_product_selected(selected)
                except Exception as _e:
                    print(f"on_product_selected failed: {_e}")
                
                # Focus on quantity field after product selection
                self.quantity_spin.setFocus()
                self.quantity_spin.selectAll()
            else:
                # No exact match, open selector
                selected = self._open_product_selector_dialog()
                if selected:
                    self.product_input.setText(selected)
                    # Apply selected product to update dependent fields
                    try:
                        self.on_product_selected(selected)
                    except Exception as _e:
                        print(f"on_product_selected failed: {_e}")
                    
                    # Focus on quantity field after product selection
                    self.quantity_spin.setFocus()
                    self.quantity_spin.selectAll()
        except Exception as e:
            print(f"Product selector failed: {e}")

    def _open_product_selector_dialog(self, prefill_text: str = None):
        """Create, size, position and open the ProductSelector below the input.
        Returns the selected name if accepted, else None.
        """
        dlg = ProductSelector(self.products, self)
        # Prefill search
        try:
            if prefill_text:
                dlg.search.setText(prefill_text)
                dlg.search.setCursorPosition(len(prefill_text))
        except Exception:
            pass
        # Size and position
        try:
            from PyQt5.QtWidgets import QApplication
            input_w = max(300, self.product_input.width())
            dlg_h = min(dlg.sizeHint().height(), 420)
            margin = 8  # vertical gap to avoid overlap with the input
            dlg.resize(input_w, dlg_h)
            bl = self.product_input.mapToGlobal(self.product_input.rect().bottomLeft())
            x, y = bl.x(), bl.y() + margin
            screen = QApplication.desktop().availableGeometry(self.product_input)
            if y + dlg_h > screen.bottom():
                tl = self.product_input.mapToGlobal(self.product_input.rect().topLeft())
                y = tl.y() - dlg_h - margin
            if x + input_w > screen.right():
                x = max(screen.left(), screen.right() - input_w)
            dlg.move(int(x), int(y+65))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec_() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None

    def on_product_selected(self, name: str):
        """Handle product selection from completer and update fields"""
        product_data = self._product_map.get(name)
        self.selected_product = product_data
        if product_data:
            self.rate_spin.setValue(product_data.get('sales_rate', 0))
            
            # Set tax rate based on invoice type
            if self.parent_dialog and hasattr(self.parent_dialog, 'gst_combo'):
                invoice_type = self.parent_dialog.gst_combo.currentText()
                if invoice_type == "Non-GST":
                    self.tax_spin.setValue(0)  # No tax for Non-GST invoices
                else:
                    self.tax_spin.setValue(product_data.get('tax_rate', 18))  # Use product's tax rate for GST invoices
            else:
                # Fallback to product tax rate if parent dialog not available
                self.tax_spin.setValue(product_data.get('tax_rate', 18))
            
            self.unit_label.setText(product_data.get('unit', 'Piece'))
            
            # Auto-apply product discount if available
            if 'discount_percent' in product_data:
                self.discount_spin.setValue(product_data.get('discount_percent', 0))
            
            self.calculate_total()
            self.item_changed.emit()
    
    def calculate_total(self):
        """Calculate line item total with improved precision"""
        try:
            quantity = self.quantity_spin.value()
            rate = self.rate_spin.value()
            discount_percent = self.discount_spin.value()
            tax_percent = self.tax_spin.value()
            
            # Calculate subtotal after discount
            subtotal = quantity * rate
            discount_amount = subtotal * (discount_percent / 100)
            after_discount = subtotal - discount_amount
            
            # Calculate tax
            tax_amount = after_discount * (tax_percent / 100)
            total = after_discount + tax_amount
            
            # Update display with animation-like effect
            self.amount_label.setText(f"₹{total:,.2f}")
            
            # Change color based on amount
            if total > 10000:
                color = SUCCESS
            elif total > 5000:
                color = PRIMARY
            else:
                color = TEXT_PRIMARY
                
            self.amount_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold; 
                    color: {color};
                    font-size: 14px;
                    padding: 8px;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid {color};
                    border-radius: 6px;
                }}
            """)
            
            # Emit signal to update parent totals
            self.item_changed.emit()
            
        except Exception as e:
            print(f"Error calculating total: {e}")
            self.amount_label.setText("₹0.00")
    
    def get_item_data(self):
        """Get item data as dictionary"""
        # Use the selected product from completer or fallback to typed name lookup
        product_data = getattr(self, 'selected_product', None)
        if not product_data and hasattr(self, 'product_input'):
            name = self.product_input.text().strip()
            if name and hasattr(self, '_product_map'):
                product_data = self._product_map.get(name)
        if not product_data:
            return None
        
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()
        discount_percent = self.discount_spin.value()
        tax_percent = self.tax_spin.value()
        
        subtotal = quantity * rate
        discount_amount = subtotal * (discount_percent / 100)
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        
        return {
            'product_id': product_data.get('id'),
            'product_name': product_data.get('name') or self.product_input.text().strip(),
            'hsn_no': self.hsn_edit.text().strip(),
            'quantity': quantity,
            'unit': product_data.get('unit', 'Piece'),
            'rate': rate,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'tax_percent': tax_percent,
            'tax_amount': tax_amount,
            'amount': total
        }

    def update_tax_rate_for_invoice_type(self, invoice_type: str):
        """Update tax rate based on invoice type"""
        if invoice_type == "Non-GST":
            self.tax_spin.setValue(0)
        else:
            # For GST invoices, use product's tax rate if available
            if hasattr(self, 'selected_product') and self.selected_product:
                self.tax_spin.setValue(self.selected_product.get('tax_rate', 18))
            else:
                self.tax_spin.setValue(18)
        
        # Recalculate total after tax change
        self.calculate_total()


class InvoiceDialog(QDialog):
    """Enhanced dialog for creating/editing invoices with modern UI"""
    def __init__(self, parent=None, invoice_data=None, invoice_number=None, read_only=False):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.products = []
        self.parties = []
        self.read_only = read_only  # Read-only mode flag
        # Guard to avoid re-entrant opening of PartySelector from typing
        self._party_selector_active = False
        # Auto-save timer
        self._autosave_timer = None
        self._has_unsaved_changes = False

        # Load existing invoice if invoice_number is provided
        if invoice_number and not invoice_data:
            self.load_existing_invoice(invoice_number)

        # Initialize window properties
        self.init_window()

        # Load required data
        self.load_data()

        # Setup the complete UI
        self.setup_ui()

        # Populate data if editing
        if self.invoice_data:
            self.populate_invoice_data()

        # Apply read-only mode if enabled
        if self.read_only:
            QTimer.singleShot(200, self.apply_read_only_mode)

        # Force maximize after everything is set up
        QTimer.singleShot(100, self.ensure_maximized)
        
        # Set initial focus on party search box for new invoices
        if not self.invoice_data and not self.read_only:
            QTimer.singleShot(150, self.set_initial_focus)
            # Start auto-save for new invoices
            QTimer.singleShot(200, self.setup_autosave)

    def load_existing_invoice(self, invoice_number):
        """Load existing invoice data by invoice number"""
        try:
            invoice_data = db.get_invoice_with_items(invoice_number)
            if invoice_data:
                self.invoice_data = invoice_data
            else:
                QMessageBox.warning(self, "Error", f"Invoice '{invoice_number}' not found!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoice: {str(e)}")

    def populate_invoice_data(self):
        """Populate form fields with existing invoice data"""
        if not self.invoice_data:
            return
        
        try:
            invoice = self.invoice_data['invoice']
            party = self.invoice_data['party']
            items = self.invoice_data.get('items', [])
            
            # Set invoice number
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setText(invoice['invoice_no'])
            
            # Set dates
            if hasattr(self, 'invoice_date'):
                from PyQt5.QtCore import QDate
                date_obj = QDate.fromString(invoice['date'], 'yyyy-MM-dd')
                self.invoice_date.setDate(date_obj)
            
            # Set party
            if hasattr(self, 'party_search') and party:
                self.party_search.setText(party['name'])
            
            # Set bill type if available
            if hasattr(self, 'billtype_combo') and invoice.get('bill_type'):
                index = self.billtype_combo.findText(invoice['bill_type'])
                if index >= 0:
                    self.billtype_combo.setCurrentIndex(index)
            
            # Set invoice type (GST/Non-GST) if available
            if hasattr(self, 'gst_combo') and invoice.get('tax_type'):
                index = self.gst_combo.findText(invoice['tax_type'])
                if index >= 0:
                    self.gst_combo.setCurrentIndex(index)
            
            # Populate items
            if items:
                # Clear ALL existing item widgets (not just count-1)
                widgets_to_remove = []
                for i in range(self.items_layout.count()):
                    item_widget = self.items_layout.itemAt(i).widget()
                    if isinstance(item_widget, InvoiceItemWidget):
                        widgets_to_remove.append(item_widget)
                
                for widget in widgets_to_remove:
                    self.items_layout.removeWidget(widget)
                    widget.deleteLater()
                
                # Add items from database
                for item_data in items:
                    item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                    
                    # Set product name
                    item_widget.product_input.setText(item_data['product_name'])
                    
                    # Set HSN code
                    item_widget.hsn_edit.setText(item_data.get('hsn_code', ''))
                    
                    # Set values
                    item_widget.quantity_spin.setValue(item_data['quantity'])
                    item_widget.rate_spin.setValue(item_data['rate'])
                    item_widget.discount_spin.setValue(item_data['discount_percent'])
                    item_widget.tax_spin.setValue(item_data['tax_percent'])
                    
                    # Set unit
                    item_widget.unit_label.setText(item_data.get('unit', 'Piece'))
                    
                    # Connect signals (only if not in read-only mode)
                    if not self.read_only:
                        item_widget.add_requested.connect(self.add_item)
                        item_widget.remove_btn.clicked.connect(lambda checked, w=item_widget: self.remove_item(w))
                    item_widget.item_changed.connect(self.update_totals)
                    
                    # Add to layout (before the stretch)
                    self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
                
                # Update row numbers and totals
                self.number_items()
                self.update_totals()
            
            # Check if invoice is FINAL and disable editing if so
            if invoice.get('status') == 'FINAL':
                self.disable_editing_after_final_save(show_message=False)
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error populating invoice data: {str(e)}")

    def apply_read_only_mode(self):
        """Apply read-only mode to the entire dialog - disable all editing"""
        try:
            # Update window title to indicate view mode
            invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else 'Invoice'
            self.setWindowTitle(f"📄 View Invoice - {invoice_no} (Read Only)")
            
            # Disable header inputs
            if hasattr(self, 'billtype_combo'):
                self.billtype_combo.setEnabled(False)
            if hasattr(self, 'party_search'):
                self.party_search.setReadOnly(True)
                self.party_search.setStyleSheet(self.party_search.styleSheet() + f"background: {BACKGROUND};")
            if hasattr(self, 'gst_combo'):
                self.gst_combo.setEnabled(False)
            if hasattr(self, 'invoice_date'):
                self.invoice_date.setEnabled(False)
            if hasattr(self, 'invoice_number'):
                self.invoice_number.setReadOnly(True)
            
            # Disable all item widgets - keep buttons visible but disabled to maintain layout
            if hasattr(self, 'items_layout'):
                for i in range(self.items_layout.count()):
                    item_widget = self.items_layout.itemAt(i).widget()
                    if item_widget and hasattr(item_widget, 'product_input'):
                        # Disable all inputs in item widget
                        if hasattr(item_widget, 'product_input'):
                            item_widget.product_input.setReadOnly(True)
                            item_widget.product_input.setStyleSheet(item_widget.product_input.styleSheet() + f"background: {BACKGROUND};")
                        if hasattr(item_widget, 'hsn_edit'):
                            item_widget.hsn_edit.setReadOnly(True)
                        if hasattr(item_widget, 'quantity_spin'):
                            item_widget.quantity_spin.setEnabled(False)
                        if hasattr(item_widget, 'rate_spin'):
                            item_widget.rate_spin.setEnabled(False)
                        if hasattr(item_widget, 'discount_spin'):
                            item_widget.discount_spin.setEnabled(False)
                        if hasattr(item_widget, 'tax_spin'):
                            item_widget.tax_spin.setEnabled(False)
                        # Keep buttons visible but make them invisible (maintain space)
                        if hasattr(item_widget, 'remove_btn'):
                            item_widget.remove_btn.setEnabled(False)
                            item_widget.remove_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
                        if hasattr(item_widget, 'add_btn'):
                            item_widget.add_btn.setEnabled(False)
                            item_widget.add_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
            
            # Disable action buttons (Save, Save & Print) but keep Close
            if hasattr(self, 'save_button'):
                self.save_button.setEnabled(False)
                self.save_button.hide()
            if hasattr(self, 'save_print_button'):
                self.save_print_button.setEnabled(False)
                self.save_print_button.hide()
            
            # Add a "Print Preview" button for viewing
            if hasattr(self, 'preview_button'):
                self.preview_button.setEnabled(True)
            
            # Disable notes/terms if they exist
            if hasattr(self, 'notes_edit'):
                self.notes_edit.setReadOnly(True)
            if hasattr(self, 'terms_edit'):
                self.terms_edit.setReadOnly(True)
            
            print(f"✅ Read-only mode applied for invoice: {invoice_no}")
            
        except Exception as e:
            print(f"Error applying read-only mode: {e}")

    def ensure_maximized(self):
        """Ensure the window is properly maximized"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        self.setWindowState(Qt.WindowMaximized)
        self.showMaximized()

    def set_initial_focus(self):
        """Set initial focus on the party search box for new invoices"""
        try:
            if hasattr(self, 'party_search'):
                self.party_search.setFocus()
                # Optional: clear any existing text and position cursor at start
                self.party_search.selectAll()
        except Exception as e:
            print(f"Error setting initial focus: {e}")

    def setup_autosave(self):
        """Setup auto-save timer to save draft every 30 seconds"""
        try:
            self._autosave_timer = QTimer(self)
            self._autosave_timer.timeout.connect(self.autosave_draft)
            self._autosave_timer.start(30000)  # 30 seconds
            print("Auto-save enabled: Draft will be saved every 30 seconds")
        except Exception as e:
            print(f"Failed to setup auto-save: {e}")

    def autosave_draft(self):
        """Auto-save current invoice data as draft"""
        try:
            # Only save if there's meaningful data
            party_text = self.party_search.text().strip() if hasattr(self, 'party_search') else ''
            
            # Check if any items have been added
            item_count = 0
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    if item_widget.get_item_data():
                        item_count += 1
            
            # Only save if there's party or items
            if party_text or item_count > 0:
                draft_data = self.collect_draft_data()
                # Save to config
                try:
                    from config import config
                    config.set('invoice_draft', draft_data)
                    self._has_unsaved_changes = False
                    print(f"Draft auto-saved: {party_text or 'No party'}, {item_count} items")
                except Exception as config_error:
                    print(f"Could not save draft to config: {config_error}")
        except Exception as e:
            print(f"Auto-save draft failed: {e}")

    def collect_draft_data(self):
        """Collect current form data for draft saving"""
        try:
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            return {
                'party_name': self.party_search.text().strip() if hasattr(self, 'party_search') else '',
                'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else '',
                'bill_type': self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH',
                'invoice_type': self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST',
                'internal_invoice_type': map_user_selection_to_internal(self.gst_combo.currentText()) if hasattr(self, 'gst_combo') else map_user_selection_to_internal('GST'),
                'items': items,
                'notes': self.notes.toPlainText() if hasattr(self, 'notes') and self.notes else '',
                'saved_at': QDate.currentDate().toString('yyyy-MM-dd')
            }
        except Exception as e:
            print(f"Error collecting draft data: {e}")
            return {}

    def closeEvent(self, event):
        """Handle dialog close - stop auto-save timer"""
        try:
            if self._autosave_timer:
                self._autosave_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)

    def init_window(self):
        """Initialize window properties and styling"""
        title = "📄 Create Invoice" if not self.invoice_data else "📝 Edit Invoice"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1200, 900)
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {BACKGROUND}, stop:1 #F8FAFC);
                border: 2px solid {BORDER};
                border-radius: 15px;
            }}
        """)

    def load_data(self):
        """Load products and parties data with error handling"""
        try:
            self.products = db.get_products() or []
            self.parties = db.get_parties() or []
        except Exception as e:
            print(f"Database error: {e}")
            # Fallback sample data
            self.products = [
                {'id': 1, 'name': 'Dell Laptop XPS 13', 'selling_price': 75000, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 2, 'name': 'iPhone 14 Pro', 'selling_price': 120000, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 3, 'name': 'Web Development Service', 'selling_price': 50000, 'tax_rate': 18, 'unit': 'Hour', 'type': 'Service'},
                {'id': 4, 'name': 'Office Chair', 'selling_price': 8500, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'},
                {'id': 5, 'name': 'Wireless Mouse', 'selling_price': 2500, 'tax_rate': 18, 'unit': 'Piece', 'type': 'Goods'}
            ]
            self.parties = [
                {'id': 1, 'name': 'ABC Corporation', 'gst_number': '27AABCU9603R1Z0', 'phone': '+91 98765 43210'},
                {'id': 2, 'name': 'XYZ Limited', 'gst_number': '27AABCU9603R1Z1', 'phone': '+91 98765 43211'},
                {'id': 3, 'name': 'Tech Solutions Pvt Ltd', 'gst_number': '27AABCU9603R1Z2', 'phone': '+91 98765 43212'}
            ]

    def setup_ui(self):
        """Setup enhanced dialog UI with modern design and better organization"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(30 , 30, 30, 100)
        self.setup_content_sections()
        self.setup_action_buttons()
        self.apply_final_styling()
    def setup_content_sections(self):
        """Setup the main content sections with enhanced layout"""
        self.content_splitter = QSplitter(Qt.Vertical)
        # self.content_splitter.setStyleSheet(f"""
        #     QSplitter {{ border: none; background: transparent; }}
        #     QSplitter::handle {{ background: {BORDER}; border-radius: 3px; height: 6px; margin: 2px 10px; }}
        #     QSplitter::handle:hover {{ background: {PRIMARY}; }}
        # """)
        self.header_frame = self.create_header_section()
        self.content_splitter.addWidget(self.header_frame)
        self.items_frame = self.create_items_section()
        self.content_splitter.addWidget(self.items_frame)
        self.totals_frame = self.create_totals_section()
        self.content_splitter.addWidget(self.totals_frame)
        self.content_splitter.setSizes([180, 450, 150])
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, False)
        self.content_splitter.setCollapsible(2, False)
        self.main_layout.addWidget(self.content_splitter)
        # Only add empty item row for new invoices (not in read-only mode or editing existing)
        if not self.read_only and not self.invoice_data:
            self.add_item()

    def setup_action_buttons(self):
        """Setup enhanced action buttons with better organization"""
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; padding: 8px; }}
        """)
        button_container.setFixedHeight(70)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(15, 10, 15, 10)
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(8)
        self.help_button = self.create_action_button("❓ Help", "help", WARNING, self.show_help, "Get help with invoice creation")
        utility_layout.addWidget(self.help_button)
        # self.preview_button = self.create_action_button("👁️ Preview", "preview", TEXT_SECONDARY, self.preview_invoice, "Preview how the invoice will look when printed")
        # utility_layout.addWidget(self.preview_button)
        button_layout.addLayout(utility_layout)
        button_layout.addStretch()
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        self.cancel_button = self.create_action_button("❌ Cancel", "cancel", DANGER, self.reject, "Cancel and close without saving")
        action_layout.addWidget(self.cancel_button)
        
        # Reset button
        self.reset_button = self.create_action_button("🔄 Reset", "reset", WARNING, self.reset_form, "Clear all values and reset to defaults")
        action_layout.addWidget(self.reset_button)
        
        # Save Print button (single button - removed separate Save Invoice)
        save_text = "💾 Update & Print" if self.invoice_data else "💾 Save Print"
        self.save_print_button = self.create_action_button(save_text, "save_print", PRIMARY, self.save_and_print, "Save invoice and open print preview")
        action_layout.addWidget(self.save_print_button)
        
        button_layout.addLayout(action_layout)
        self.main_layout.addWidget(button_container)

    def create_action_button(self, text, button_type, color, callback, tooltip):
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setMinimumWidth(120)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setAutoDefault(False)  # Prevent Enter key from triggering this button
        button.setDefault(False)      # Ensure this is not the default button
        hover_color = self.get_hover_color(color)
        pressed_color = self.get_pressed_color(color)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {hover_color});
                color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: bold; padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hover_color}, stop:1 {pressed_color});
            }}
            QPushButton:pressed {{ background: {pressed_color}; }}
            QPushButton:disabled {{ background: #9CA3AF; color: #6B7280; }}
        """)
        button.clicked.connect(callback)
        return button

    def get_hover_color(self, base_color):
        color_map = {SUCCESS: "#059669", DANGER: "#DC2626", WARNING: "#F59E0B", PRIMARY: PRIMARY_HOVER, TEXT_SECONDARY: "#6B7280"}
        return color_map.get(base_color, "#6B7280")

    def get_pressed_color(self, base_color):
        color_map = {SUCCESS: "#047857", DANGER: "#B91C1C", WARNING: "#D97706", PRIMARY: "#1D4ED8", TEXT_SECONDARY: "#4B5563"}
        return color_map.get(base_color, "#4B5563")

    def apply_final_styling(self):
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.showMaximized()
        self.setup_keyboard_shortcuts()
        self.setup_validation()

    def setup_keyboard_shortcuts(self):
        # Save shortcuts
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_invoice)
        
        # Add new item shortcuts
        new_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_item_shortcut.activated.connect(self.add_item)
        new_item_shortcut2 = QShortcut(QKeySequence("Ctrl+Return"), self)
        new_item_shortcut2.activated.connect(self.add_item)
        
        # Quick navigation shortcuts
        party_shortcut = QShortcut(QKeySequence("Alt+P"), self)
        party_shortcut.activated.connect(lambda: self.party_search.setFocus() if hasattr(self, 'party_search') else None)
        
        date_shortcut = QShortcut(QKeySequence("Alt+D"), self)
        date_shortcut.activated.connect(lambda: self.invoice_date.setFocus() if hasattr(self, 'invoice_date') else None)
        
        # Print shortcut
        print_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        print_shortcut.activated.connect(self.save_and_print)
        
        # Reset shortcut
        reset_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reset_shortcut.activated.connect(self.reset_form)
        
        # Help and cancel
        help_shortcut = QShortcut(QKeySequence.HelpContents, self)
        help_shortcut.activated.connect(self.show_help)
        cancel_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        cancel_shortcut.activated.connect(self.reject)

    def setup_validation(self):
        # Set initial balance due visibility based on default bill type
        if hasattr(self, 'billtype_combo'):
            self.on_bill_type_changed(self.billtype_combo.currentText())

    def show_help(self):
        help_text = """
        <h3>📋 Invoice Creation Help</h3>
        
        <h4>📝 Steps:</h4>
        <p><b>1. Invoice Details:</b> Fill in invoice number, date, and due date</p>
        <p><b>2. Party Selection:</b> Choose the customer/client</p>
        <p><b>3. Add Items:</b> Click 'Add Item' to add products/services</p>
        <p><b>4. Calculations:</b> Totals are calculated automatically</p>
        <p><b>5. Save:</b> Click 'Save Invoice' to create the invoice</p>
        
        <h4>⌨️ Keyboard Shortcuts:</h4>
        <table style='margin-left: 10px;'>
            <tr><td><b>Ctrl+S</b></td><td>Save Invoice</td></tr>
            <tr><td><b>Ctrl+P</b></td><td>Save & Print</td></tr>
            <tr><td><b>Ctrl+N</b></td><td>Add New Item</td></tr>
            <tr><td><b>Ctrl+R</b></td><td>Reset Form</td></tr>
            <tr><td><b>Alt+P</b></td><td>Focus Party Search</td></tr>
            <tr><td><b>Alt+D</b></td><td>Focus Invoice Date</td></tr>
            <tr><td><b>Enter</b></td><td>Next field / Add row</td></tr>
            <tr><td><b>Esc</b></td><td>Cancel & Close</td></tr>
        </table>
        """
        QMessageBox.information(self, "Invoice Help", help_text)

    def preview_invoice(self):
        # Collect data from the form
        party_name = getattr(self, 'party_search').text().strip() if hasattr(self, 'party_search') else ''
        inv_date = self.invoice_date.date().toString('yyyy-MM-dd') if hasattr(self, 'invoice_date') else ''
        invoice_no = self.invoice_number.text() if hasattr(self, 'invoice_number') else ''
        bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else ''
        items = []
        for i in range(self.items_layout.count() - 1):
            w = self.items_layout.itemAt(i).widget()
            if isinstance(w, InvoiceItemWidget):
                d = w.get_item_data()
                if d:
                    items.append(d)
        subtotal = sum((it['quantity'] * it['rate']) for it in items) if items else 0
        total_discount = sum(it['discount_amount'] for it in items) if items else 0
        total_tax = sum(it['tax_amount'] for it in items) if items else 0
        grand_total = subtotal - total_discount + total_tax
        cgst = sum(it['tax_amount']/2 for it in items if it['tax_amount'] > 0) if items else 0
        sgst = cgst
        igst = 0  # For now, assuming intra-state
        # GST summary row (assuming all items same rate for demo)
        gst_rate = items[0]['tax_percent'] if items else 0
        gst_summary = f"""
            <tr>
                <td style='border:1px solid #bbb;padding:4px;'>GST%</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{gst_rate:.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{subtotal-total_discount:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{cgst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{sgst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{igst:,.2f}</td>
                <td style='border:1px solid #bbb;padding:4px;text-align:right;'>{total_tax:,.2f}</td>
            </tr>
        """
        # Build item rows
        rows_html = "".join([
            f"<tr>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:center'>{i+1}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it['product_name']}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it.get('hsn_no','')}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['quantity']:.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb'>{it.get('unit','')}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['rate']:,.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['discount_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>{it['tax_percent']:,.2f}%</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['amount']:,.2f}</td>"
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['tax_amount']/2:,.2f}</td>"  # CGST
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹{it['tax_amount']/2:,.2f}</td>"  # SGST
            f"<td style='padding:6px;border:1px solid #bbb;text-align:right'>₹0.00</td>"  # IGST
            f"</tr>"
            for i, it in enumerate(items)
        ])
        # In Words
        def num2words(n):
            # Simple number to words for demo (Indian style)
            import math
            units = ["", "Thousand", "Lakh", "Crore"]
            s = ""
            if n == 0:
                return "Zero"
            if n < 0:
                return "Minus " + num2words(-n)
            i = 0
            while n > 0:
                rem = n % 1000 if i == 0 else n % 100
                if rem != 0:
                    s = f"{rem} {units[i]} " + s
                n = n // 1000 if i == 0 else n // 100
                i += 1
            return s.strip()
        in_words = num2words(int(round(grand_total))) + " Only"
        # HTML
        html = f"""
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
        body {{ font-family: Arial, sans-serif; color: #222; margin: 0; background: #fff; }}
        .invoice-box {{ max-width: 900px; margin: 20px auto; border: 1px solid #bbb; padding: 24px 32px 32px 32px; background: #fff; }}
        .header {{ text-align: center; border-bottom: 2px solid #222; padding-bottom: 8px; margin-bottom: 8px; }}
        .header h1 {{ font-size: 24px; margin: 0; letter-spacing: 2px; }}
        .header .subtitle {{ font-size: 13px; color: #444; margin-top: 2px; }}
        .meta-table, .meta-table td {{ font-size: 13px; }}
        .meta-table {{ width: 100%; margin-bottom: 8px; }}
        .meta-table td {{ padding: 2px 6px; }}
        .section-title {{ background: #e5e7eb; font-weight: bold; padding: 4px 8px; border: 1px solid #bbb; }}
        .items-table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin-bottom: 0; }}
        .items-table th, .items-table td {{ border: 1px solid #bbb; padding: 5px 4px; }}
        .items-table th {{ background: #f3f4f6; font-size: 13px; }}
        .totals-table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin-top: 0; }}
        .totals-table td {{ border: 1px solid #bbb; padding: 4px 6px; }}
        .totals-table .label {{ text-align: right; font-weight: bold; background: #f9fafb; }}
        .totals-table .value {{ text-align: right; font-weight: bold; background: #f9fafb; }}
        .gst-summary-table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin-top: 0; }}
        .gst-summary-table td {{ border: 1px solid #bbb; padding: 4px 6px; }}
        .footer-box {{ background: #e0f2fe; border: 1px solid #bbb; padding: 10px 16px; margin-top: 18px; font-size: 15px; font-weight: bold; text-align: right; }}
        .footer-details {{ font-size: 12px; color: #444; margin-top: 8px; }}
        </style>
        </head>
        <body>
        <div class='invoice-box'>
            <div class='header'>
                <div style='font-size:11px; text-align:right; float:right;'>TAX INVOICE</div>
                <h1>SUPER POWER BATTERIES (INDIA)</h1>
                <div class='subtitle'>A-1/2, Gangotri Appartment, R. V. Desai Road, Vadodara - 390001 Gujarat<br>ph. (0265-2427631, 8815991781 | mail : )</div>
                <div class='subtitle' style='font-weight:bold;'>Terms : {bill_type}</div>
            </div>
            <table class='meta-table'>
                <tr>
                    <td><b>Buyer's Name and Address</b><br>{party_name or '—'}<br>GSTIN: —</td>
                    <td>
                        <table style='width:100%; font-size:13px;'>
                            <tr><td>Invoice No.:</td><td>{invoice_no}</td></tr>
                            <tr><td>Date:</td><td>{inv_date}</td></tr>
                            <tr><td>Ref No. & Dt.:</td><td> </td></tr>
                            <tr><td>Vehicle No.:</td><td> </td></tr>
                            <tr><td>Transport:</td><td> </td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            <div class='section-title'>Item Details</div>
            <table class='items-table'>
                <tr>
                    <th>No</th><th>Description</th><th>HSN Code</th><th>MRP</th><th>Qty</th><th>Unit</th><th>Rate</th><th>Discount</th><th>Tax%</th><th>CGST</th><th>SGST</th><th>IGST</th><th>Total</th>
                </tr>
                {rows_html if rows_html else "<tr><td colspan='13' style='text-align:center;color:#6b7280'>No items added</td></tr>"}
            </table>
            <table class='totals-table'>
                <tr><td class='label' colspan='12'>Total Amount Before Tax</td><td class='value'>₹{subtotal:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Discount</td><td class='value'>₹{total_discount:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Add: CGST/SGST</td><td class='value'>₹{cgst+sgst:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Add: IGST</td><td class='value'>₹{igst:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Tax Amount</td><td class='value'>₹{total_tax:,.2f}</td></tr>
                <tr><td class='label' colspan='12'>Total Invoice After Tax</td><td class='value'>₹{grand_total:,.2f}</td></tr>
            </table>
            <div class='section-title'>GST SUMMARY</div>
            <table class='gst-summary-table'>
                <tr style='background:#f3f4f6;'><td>GST%</td><td>Taxable Amt</td><td>CGST Amt</td><td>SGST Amt</td><td>IGST Amt</td><td>Tax Amt</td></tr>
                {gst_summary}
            </table>
            <div class='footer-box'>Net Amount<br><span style='font-size:22px;'>₹{grand_total:,.2f}</span></div>
            <div class='footer-details'>In Words : {in_words}<br>GSTIN : 24AADPF6173E1ZT<br>Bank Details :<br>BANK OF INDIA, A/C NO: 230327100001287<br>IFSC CODE: BKID0002303<br>Terms & Conditions: Subject to Vadodara - 390001 jurisdiction E.&O.E.<br><br><b>For SUPER POWER BATTERIES (INDIA)</b></div>
        </div>
        </body>
        </html>
        """
        # Show in a modal dialog with a QTextBrowser and simple actions
        dlg = QDialog(self)
        dlg.setWindowTitle("Invoice Preview")
        dlg.setModal(True)
        dlg.resize(900, 900)
        container = QVBoxLayout(dlg)
        view = QTextEdit()
        view.setReadOnly(True)
        view.setHtml(html)
        container.addWidget(view)
        actions = QHBoxLayout()
        actions.addStretch()
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: #1d4ed8;
            }}
        """)
        print_btn.clicked.connect(lambda: self.print_invoice(html))
        actions.addWidget(print_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {TEXT_SECONDARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: #4b5563;
            }}
        """)
        close_btn.clicked.connect(dlg.reject)
        actions.addWidget(close_btn)
        container.addLayout(actions)

        dlg.exec_()

    def print_invoice(self, html_content):
        """Print the invoice using the system's print dialog"""
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtGui import QTextDocument
            
            # Create a printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            
            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Invoice")
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Create a QTextDocument and set the HTML content
                document = QTextDocument()
                document.setHtml(html_content)
                
                # Print the document
                document.print_(printer)
                
                QMessageBox.information(self, "Success", "Invoice sent to printer successfully!")
                
        except ImportError:
            # Fallback if print support is not available
            QMessageBox.warning(self, "Print Unavailable", 
                              "Print functionality requires PyQt5 print support.\n"
                              "You can copy the invoice content and print manually.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", 
                               f"An error occurred while printing:\n{str(e)}")

    def save_and_print(self):
        """Save invoice and open print preview"""
        try:
            # Show confirmation dialog first
            reply = QMessageBox.question(
                self, 
                "Confirm Save & Print", 
                "Do you want to save this invoice and print it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return  # User cancelled
            
            # Step 1: Validate invoice data
            if not self.validate_invoice_for_final_save():
                return
            
            # Step 2: Save invoice as FINAL
            saved_invoice_id = self.save_final_invoice()
            if not saved_invoice_id:
                return
                
            # Step 3: Generate PDF and show print preview
            self.show_print_preview(saved_invoice_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Save & Print Error", 
                               f"An error occurred during save & print:\n{str(e)}")

    def validate_invoice_for_final_save(self):
        """Validate that invoice has all required data for final save"""
        # Check invoice number
        invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
        if not invoice_no:
            show_validation_error(
                self,
                self.invoice_number if hasattr(self, 'invoice_number') else None,
                "Validation Error",
                "Invoice number is required!"
            )
            return False
        
        # Check date
        if not hasattr(self, 'invoice_date') or not self.invoice_date.date():
            show_validation_error(
                self,
                self.invoice_date if hasattr(self, 'invoice_date') else None,
                "Validation Error",
                "Invoice date is required!"
            )
            return False
        
        # Check party selection
        party_text = getattr(self, 'party_search').text().strip() if hasattr(self, 'party_search') else ''
        party_data = getattr(self, 'party_data_map', {}).get(party_text)
        if not party_data or not party_text:
            show_validation_error(
                self,
                self.party_search if hasattr(self, 'party_search') else None,
                "Validation Error",
                "Please select a valid customer!"
            )
            return False
        
        # Check at least one item
        items = []
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                if item_data:
                    items.append(item_data)
        
        if not items:
            # Highlight item count badge
            if hasattr(self, 'item_count_badge'):
                highlight_error(self.item_count_badge, "Add at least one item")
            QMessageBox.warning(self, "Validation Error", "⚠️ Please add at least one item!")
            return False
        
        # Check for duplicate invoice number if creating new invoice
        if not self.invoice_data and hasattr(db, 'invoice_no_exists') and db.invoice_no_exists(invoice_no):
            show_validation_error(
                self,
                self.invoice_number if hasattr(self, 'invoice_number') else None,
                "Validation Error",
                f"Invoice number '{invoice_no}' already exists. Please use a unique invoice number."
            )
            return False
        
        return True

    def save_final_invoice(self):
        """Save invoice with FINAL status and return invoice ID"""
        try:
            # Collect all invoice data
            party_text = getattr(self, 'party_search').text().strip()
            party_data = getattr(self, 'party_data_map', {}).get(party_text)
            
            if not party_data or 'id' not in party_data:
                raise Exception(f"Invalid party selected: {party_text}")
            
            items = []
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        items.append(item_data)
            
            # Calculate totals
            subtotal = sum(item['quantity'] * item['rate'] for item in items)
            total_discount = sum(item['discount_amount'] for item in items)
            
            # Calculate GST breakdown
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            is_interstate = False  # TODO: Implement state-based logic
            
            for item in items:
                tax_amount = item['tax_amount']
                if tax_amount > 0:
                    if is_interstate:
                        total_igst += tax_amount
                    else:
                        total_cgst += tax_amount / 2
                        total_sgst += tax_amount / 2
            
            total_tax = sum(item['tax_amount'] for item in items)
            grand_total = subtotal - total_discount + total_tax
            
            invoice_no = self.invoice_number.text().strip()
            invoice_date = self.invoice_date.date().toString('yyyy-MM-dd')
            
            # Get or generate unique invoice number for final save
            if not self.invoice_data:
                # For new invoice, ensure unique number
                original_no = invoice_no
                counter = 1
                while hasattr(db, 'invoice_no_exists') and db.invoice_no_exists(invoice_no):
                    invoice_no = f"{original_no}-{counter}"
                    counter += 1
                
                # Update the display with final invoice number
                if hasattr(self, 'invoice_number'):
                    self.invoice_number.setText(invoice_no)
            
            # Get invoice type from combo box (user-facing) and map to internal
            invoice_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST'
            internal_invoice_type = map_user_selection_to_internal(invoice_type)
            # For DB and templates we still want 'GST' or 'Non-GST' semantic
            tax_type_for_db = 'Non-GST' if internal_invoice_type == 'Bill of Supply' else 'GST'
            
            # Get bill type (CASH/CREDIT)
            bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH'
            
            # Get round-off amount
            round_off = getattr(self, 'roundoff_amount', 0.0)
            
            # Get notes
            notes = self.notes.toPlainText().strip() if hasattr(self, 'notes') and self.notes else None
            
            # Calculate balance due (for CREDIT bills, balance = grand_total)
            balance_due = grand_total + round_off if bill_type == 'CREDIT' else 0.0
            
            # Save invoice with FINAL status
            if self.invoice_data:
                # Update existing invoice
                if 'id' not in self.invoice_data:
                    raise Exception("Invalid invoice data - missing ID")
                    
                invoice_data = {
                    'id': self.invoice_data['id'],
                    'invoice_no': invoice_no,
                    'date': invoice_date,
                    'party_id': party_data['id'],
                    'tax_type': tax_type_for_db,
                    'internal_type': internal_invoice_type,
                    'bill_type': bill_type,
                    'subtotal': subtotal,
                    'discount': total_discount,
                    'cgst': total_cgst,
                    'sgst': total_sgst,
                    'igst': total_igst,
                    'round_off': round_off,
                    'grand_total': grand_total + round_off,
                    'balance_due': balance_due,
                    'status': 'FINAL',
                    'notes': notes,
                }
                db.update_invoice(invoice_data)
                invoice_id = self.invoice_data['id']
                
                # Update items
                db.delete_invoice_items(invoice_id)
                for item in items:
                    db.add_invoice_item(
                        invoice_id,
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
            else:
                # Create new invoice
                invoice_id = db.add_invoice(
                    invoice_no=invoice_no,
                    date=invoice_date,
                    party_id=party_data['id'],
                    tax_type=tax_type_for_db,
                    subtotal=subtotal,
                    cgst=total_cgst,
                    sgst=total_sgst,
                    igst=total_igst,
                    round_off=round_off,
                    grand_total=grand_total + round_off,
                    status='FINAL',
                    internal_type=internal_invoice_type,
                    bill_type=bill_type,
                    discount=total_discount,
                    balance_due=balance_due,
                    notes=notes
                )
                
                # Add items
                for item in items:
                    db.add_invoice_item(
                        invoice_id,
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
            
            # Update stock for sales items (decrease stock for products with track_stock enabled)
            db.update_stock_for_sales_items(items)
            
            # Disable editing after final save
            self.disable_editing_after_final_save()
            
            return invoice_id
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save invoice: {str(e)}")
            return None

    def disable_editing_after_final_save(self, show_message=True):
        """Disable all editing controls after invoice is saved as FINAL"""
        # Disable the Save & Print button itself
        if hasattr(self, 'save_print_button'):
            self.save_print_button.setEnabled(False)
            self.save_print_button.setText("✓ Saved & Final")
        
        # Disable regular save button
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(False)
            self.save_button.setText("✓ Finalized")
        
        # Show final status message only if requested
        if show_message:
            QMessageBox.information(self, "Invoice Finalized", 
                                  "Invoice has been saved as FINAL and cannot be edited further.")

    def show_print_preview(self, invoice_id):
        """Show HTML preview dialog - uses common utility"""
        from ui.invoices.sales.invoice_preview_screen import show_invoice_preview
        show_invoice_preview(self, invoice_id)

    def generate_invoice_html(self, invoice_id):
        """Generate HTML content for the invoice"""
        try:
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            
            # Get invoice data
            invoice_data = generator.get_invoice_data(invoice_id)
            if not invoice_data:
                return None
            
            # Get invoice type and set appropriate template
            invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
            generator.template_path = generator.get_template_path(invoice_type)
            
            # Prepare template data based on invoice type
            if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
                template_data = generator.prepare_non_gst_template_data(invoice_data)
            else:
                template_data = generator.prepare_template_data(invoice_data)
            
            html_content = generator.render_html_template(template_data, invoice_type)
            
            return html_content
                
        except Exception as e:
            QMessageBox.critical(self, "HTML Generation Error", 
                               f"Failed to generate HTML: {str(e)}")
            return None

    def show_html_preview_dialog(self, html_content, invoice_id):
        """Show HTML preview directly in QWebEngineView - renders exactly like browser"""
        import tempfile
        import os
        from PyQt5.QtCore import QUrl
        
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
        except ImportError:
            QMessageBox.critical(self, "Error", "PyQtWebEngine not installed.\n\nRun: pip3 install PyQtWebEngine")
            return
        
        try:
            # Get invoice number for filename
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            invoice_data = generator.get_invoice_data(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            invoice_no = invoice_data['invoice']['invoice_no']
            
            # Create preview dialog
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle(f"📄 Invoice Preview - {invoice_no}")
            preview_dialog.setModal(True)
            preview_dialog.resize(900, 850)
            preview_dialog.setMinimumSize(800, 600)
            
            # Main layout
            layout = QVBoxLayout(preview_dialog)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # Header bar with title and buttons
            header_frame = QFrame()
            header_frame.setFixedHeight(60)
            header_frame.setStyleSheet(f"""
                QFrame {{ 
                    background: {PRIMARY}; 
                    border-radius: 8px; 
                }}
            """)
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(15, 5, 15, 5)
            
            # Title
            title_label = QLabel(f"📄 Invoice: {invoice_no}")
            title_label.setStyleSheet(f"color: {WHITE}; font-size: 16px; font-weight: bold;")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # Button style
            btn_style = f"""
                QPushButton {{
                    background: {WHITE};
                    color: {PRIMARY};
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 15px;
                    min-width: 100px;
                }}
                QPushButton:hover {{ background: #e0e7ff; }}
                QPushButton:pressed {{ background: #c7d2fe; }}
            """
            
            # Create temp PDF path for later use
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"Invoice_{invoice_no}.pdf")
            
            # Store references in dialog for callbacks
            preview_dialog.html_content = html_content
            preview_dialog.pdf_path = pdf_path
            preview_dialog.invoice_no = invoice_no
            
            # Save PDF button
            save_btn = QPushButton("💾 Save PDF")
            save_btn.setStyleSheet(btn_style)
            save_btn.clicked.connect(lambda: self.save_invoice_as_pdf(preview_dialog))
            header_layout.addWidget(save_btn)
            
            # Print button
            print_btn = QPushButton("🖨️ Print")
            print_btn.setStyleSheet(btn_style)
            print_btn.clicked.connect(lambda: self.print_invoice_preview(preview_dialog))
            header_layout.addWidget(print_btn)
            
            # Open in Browser button
            browser_btn = QPushButton("🌐 Open in Browser")
            browser_btn.setStyleSheet(btn_style)
            browser_btn.clicked.connect(lambda: self.open_html_in_browser(html_content, invoice_no))
            header_layout.addWidget(browser_btn)
            
            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #ef4444;
                    color: {WHITE};
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 15px;
                    min-width: 80px;
                }}
                QPushButton:hover {{ background: #dc2626; }}
                QPushButton:pressed {{ background: #b91c1c; }}
            """)
            close_btn.clicked.connect(preview_dialog.close)
            header_layout.addWidget(close_btn)
            
            layout.addWidget(header_frame)
            
            # HTML Viewer using QWebEngineView - renders exactly like browser!
            html_viewer = QWebEngineView()
            html_viewer.setStyleSheet(f"""
                QWebEngineView {{
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    background: white;
                }}
            """)
            
            # Configure settings
            settings = html_viewer.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            
            # Load HTML content directly - this renders exactly like in Chrome!
            html_viewer.setHtml(html_content)
            
            layout.addWidget(html_viewer, 1)  # Stretch factor 1 to fill space
            
            # Store reference to prevent garbage collection
            preview_dialog.html_viewer = html_viewer
            
            # Show dialog
            preview_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to show preview: {str(e)}")
            print(f"❌ Preview failed: {e}")

    def save_invoice_as_pdf(self, preview_dialog):
        """Save the invoice as PDF using WebEngine's printToPdf"""
        from PyQt5.QtCore import QMarginsF
        from PyQt5.QtGui import QPageLayout, QPageSize
        
        # Get save path from user
        default_filename = f"Invoice_{preview_dialog.invoice_no}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Invoice as PDF",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not save_path:
            return
        
        # Store save path for callback
        preview_dialog.save_path = save_path
        
        # Setup page layout for PDF (A4 size with margins)
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(10, 10, 10, 10)
        )
        
        # Generate PDF from the rendered HTML
        def on_pdf_saved(file_path, success):
            if success:
                QMessageBox.information(self, "Saved", f"PDF saved successfully:\n{file_path}")
                # Ask to open
                reply = QMessageBox.question(self, "Open PDF?", "Would you like to open the saved PDF?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.open_pdf_file(file_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to save PDF")
        
        preview_dialog.html_viewer.page().pdfPrintingFinished.connect(on_pdf_saved)
        preview_dialog.html_viewer.page().printToPdf(save_path, page_layout)

    def print_invoice_preview(self, preview_dialog):
        """Print the invoice using system print dialog"""
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            preview_dialog.html_viewer.page().print(printer, lambda ok: None)

    def open_html_in_browser(self, html_content, invoice_no):
        """Open the HTML invoice in the default browser"""
        import tempfile
        import webbrowser
        import os
        
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, f"Invoice_{invoice_no}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        webbrowser.open(f'file://{html_path}')

    def generate_pdf_with_webengine(self, html_content, pdf_path, invoice_no, invoice_id):
        """Use QWebEngineView to render HTML and export to PDF"""
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
            from PyQt5.QtCore import QUrl, QMarginsF, QSizeF
            from PyQt5.QtGui import QPageLayout, QPageSize
            
            # Create a hidden webview for rendering
            webview = QWebEngineView()
            webview.setMinimumSize(800, 600)
            
            # Configure settings for better rendering
            settings = webview.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            
            # Store references for the callback
            self._pdf_webview = webview
            self._pdf_path = pdf_path
            self._pdf_invoice_no = invoice_no
            self._pdf_invoice_id = invoice_id
            self._pdf_html_content = html_content
            
            # Connect to loadFinished signal
            webview.loadFinished.connect(self._on_webview_load_finished)
            
            # Load HTML content
            webview.setHtml(html_content)
            
            print(f"📄 Loading HTML into WebEngine for PDF generation...")
            
        except ImportError as e:
            QMessageBox.critical(self, "WebEngine Error", 
                f"PyQtWebEngine is not installed.\n\nPlease run:\npip3 install PyQtWebEngine\n\nError: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Generation Error", f"Failed to initialize WebEngine: {str(e)}")
            print(f"❌ WebEngine initialization failed: {e}")

    def _on_webview_load_finished(self, ok):
        """Called when HTML is loaded in WebEngine, now generate PDF"""
        from PyQt5.QtCore import QMarginsF
        from PyQt5.QtGui import QPageLayout, QPageSize
        
        if not ok:
            QMessageBox.warning(self, "Load Error", "Failed to load HTML content")
            return
        
        print(f"✅ HTML loaded, generating PDF...")
        
        # Setup page layout for PDF (A4 size with margins)
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(10, 10, 10, 10)  # Small margins (left, top, right, bottom)
        )
        
        # Generate PDF
        self._pdf_webview.page().printToPdf(
            self._pdf_path,
            page_layout
        )
        
        # Connect to pdfPrintingFinished signal
        self._pdf_webview.page().pdfPrintingFinished.connect(self._on_pdf_generated)

    def _on_pdf_generated(self, file_path, success):
        """Called when PDF generation is complete"""
        if success:
            print(f"✅ PDF generated successfully: {file_path}")
            # Show the PDF preview dialog
            self.show_pdf_preview_dialog(
                file_path, 
                self._pdf_invoice_no, 
                self._pdf_html_content, 
                self._pdf_invoice_id
            )
        else:
            QMessageBox.critical(self, "PDF Error", "Failed to generate PDF file")
            print(f"❌ PDF generation failed")
        
        # Cleanup
        if hasattr(self, '_pdf_webview'):
            self._pdf_webview.deleteLater()
            del self._pdf_webview

    def show_pdf_preview_dialog(self, pdf_path, invoice_no, html_content, invoice_id):
        """Show PDF preview inside PyQt dialog with embedded viewer"""
        import os
        import shutil
        from PyQt5.QtCore import QUrl
        
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
        except ImportError:
            QMessageBox.critical(self, "Error", "PyQtWebEngine not installed")
            return
        
        # Create preview dialog - larger to show PDF properly
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"📄 Invoice Preview - {invoice_no}")
        preview_dialog.setModal(True)
        preview_dialog.resize(900, 800)
        preview_dialog.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(preview_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header bar with title and buttons
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet(f"""
            QFrame {{ 
                background: {PRIMARY}; 
                border-radius: 8px; 
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Title
        title_label = QLabel(f"📄 Invoice: {invoice_no}")
        title_label.setStyleSheet(f"color: {WHITE}; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Button style
        btn_style = f"""
            QPushButton {{
                background: {WHITE};
                color: {PRIMARY};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 15px;
                min-width: 100px;
            }}
            QPushButton:hover {{ background: #e0e7ff; }}
            QPushButton:pressed {{ background: #c7d2fe; }}
        """
        
        # Save As button
        save_btn = QPushButton("💾 Save As")
        save_btn.setStyleSheet(btn_style)
        save_btn.clicked.connect(lambda: self.save_pdf_as(pdf_path, invoice_no))
        header_layout.addWidget(save_btn)
        
        # Print button
        print_btn = QPushButton("🖨️ Print")
        print_btn.setStyleSheet(btn_style)
        print_btn.clicked.connect(lambda: self.print_pdf(pdf_path))
        header_layout.addWidget(print_btn)
        
        # Open External button
        open_btn = QPushButton("📖 Open External")
        open_btn.setStyleSheet(btn_style)
        open_btn.clicked.connect(lambda: self.open_pdf_file(pdf_path))
        header_layout.addWidget(open_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: #ef4444;
                color: {WHITE};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{ background: #dc2626; }}
            QPushButton:pressed {{ background: #b91c1c; }}
        """)
        close_btn.clicked.connect(preview_dialog.close)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_frame)
        
        # PDF Viewer using QWebEngineView
        pdf_viewer = QWebEngineView()
        pdf_viewer.setStyleSheet(f"""
            QWebEngineView {{
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        
        # Configure settings
        settings = pdf_viewer.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        
        # Load PDF file directly in WebEngineView (Chrome's built-in PDF viewer)
        pdf_url = QUrl.fromLocalFile(pdf_path)
        pdf_viewer.setUrl(pdf_url)
        
        layout.addWidget(pdf_viewer, 1)  # Stretch factor 1 to fill space
        
        # Store reference to prevent garbage collection
        preview_dialog.pdf_viewer = pdf_viewer
        
        # Show dialog
        preview_dialog.exec_() 

    def open_pdf_file(self, pdf_path):
        """Open PDF file with system default viewer"""
        import subprocess
        import os
        
        try:
            if os.path.exists(pdf_path):
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':
                    if os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', pdf_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', pdf_path])
                print(f"📖 Opened PDF: {pdf_path}")
            else:
                QMessageBox.warning(self, "File Not Found", f"PDF file not found: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open PDF: {str(e)}")

    def save_pdf_as(self, pdf_path, invoice_no):
        """Save PDF to user-chosen location"""
        import shutil
        
        try:
            default_filename = f"Invoice_{invoice_no}.pdf"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                default_filename,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if save_path:
                shutil.copy2(pdf_path, save_path)
                QMessageBox.information(self, "Saved", f"PDF saved to:\n{save_path}")
                
                # Ask to open
                reply = QMessageBox.question(self, "Open PDF?", "Would you like to open the saved PDF?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.open_pdf_file(save_path)
                    
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")

    def print_pdf(self, pdf_path):
        """Print PDF using system print dialog"""
        import subprocess
        import os
        
        try:
            if os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
                # Use lpr command for printing on macOS
                subprocess.run(['lpr', pdf_path])
                QMessageBox.information(self, "Print", "PDF sent to default printer!")
            else:
                # Open PDF and let user print from viewer
                self.open_pdf_file(pdf_path)
                QMessageBox.information(self, "Print", "PDF opened. Use Ctrl+P to print.")
        except Exception as e:
            # Fallback: open PDF for manual printing
            self.open_pdf_file(pdf_path)
            QMessageBox.information(self, "Print", f"PDF opened. Please print from the viewer.\n\nError: {str(e)}")

    def open_invoice_in_browser(self, invoice_id, dialog):
        """Open the invoice HTML in browser and close preview dialog"""
        try:
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            import tempfile
            import webbrowser
            
            generator = InvoicePDFGenerator()
            
            # Get invoice data
            invoice_data = generator.get_invoice_data(invoice_id)
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            # Get invoice type and set appropriate template
            invoice_type = invoice_data['invoice'].get('tax_type', 'GST')
            generator.template_path = generator.get_template_path(invoice_type)
            
            # Prepare template data based on invoice type
            if invoice_type and invoice_type.upper() in ['NON-GST', 'NON GST', 'NONGST']:
                template_data = generator.prepare_non_gst_template_data(invoice_data)
            else:
                template_data = generator.prepare_template_data(invoice_data)
            
            html_content = generator.render_html_template(template_data, invoice_type)
            
            # Create temporary HTML file
            temp_dir = tempfile.gettempdir()
            html_filename = f"invoice_{invoice_data['invoice']['invoice_no']}.html"
            html_path = os.path.join(temp_dir, html_filename)
            
            # Save HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open('file://' + html_path)
            print(f"Invoice HTML opened in browser: {html_path}")
            print("To save as PDF: Press Ctrl+P (or Cmd+P on Mac) and save as PDF")
            
            # Close the preview dialog
            dialog.close()
            
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"Invoice opened in browser!\n\nTo save as PDF:\n• Press Ctrl+P (or Cmd+P on Mac)\n• Choose 'Save as PDF' option")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open invoice in browser: {str(e)}")

    def download_invoice_pdf(self, invoice_id, html_content):
        """Download invoice as PDF file using browser's print-to-PDF functionality"""
        try:
            # Get invoice data for filename
            from ui.print.invoice_pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            invoice_data = generator.get_invoice_data(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            invoice_no = invoice_data['invoice']['invoice_no']
            
            # Try native PDF generation using QPrinter
            try:
                from PyQt5.QtPrintSupport import QPrinter
                from PyQt5.QtGui import QTextDocument
                
                # Get save location from user
                default_filename = f"Invoice_{invoice_no}.pdf"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Invoice PDF",
                    default_filename,
                    "PDF Files (*.pdf);;All Files (*)"
                )
                
                if not file_path:
                    return  # User cancelled
                
                # Create QTextDocument and set HTML content
                document = QTextDocument()
                document.setHtml(html_content)
                
                # Set up printer for PDF output
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
                
                # Print document to PDF
                document.print(printer)
                
                # Show success message
                QMessageBox.information(
                    self, 
                    "PDF Saved", 
                    f"Invoice PDF saved successfully!\n\nLocation: {file_path}"
                )
                
                # Ask if user wants to open the PDF
                reply = QMessageBox.question(
                    self,
                    "Open PDF?",
                    "Would you like to open the PDF file now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # Open the PDF file with system default application
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS and Linux
                        os.system(f'open "{file_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{file_path}"')
                
            except ImportError as print_error:
                print(f"QPrinter not available: {print_error}")
                
                # Fallback: Generate HTML file and give instructions
                QMessageBox.information(
                    self,
                    "PDF Download Instructions",
                    f"Direct PDF generation is not available.\n\n"
                    f"Alternative method:\n"
                    f"1. Click 'Open in Browser' button\n"
                    f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                    f"3. Choose 'Save as PDF' option\n"
                    f"4. Save as '{invoice_no}.pdf'"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "PDF Download Error", f"Failed to download PDF: {str(e)}")

    def generate_invoice_pdf(self, invoice_id):
        """Generate PDF for the invoice using the PDF generator module"""
        try:
            from ui.print.invoice_pdf_generator import generate_invoice_pdf
            pdf_path = generate_invoice_pdf(invoice_id)
            
            if pdf_path and os.path.exists(pdf_path):
                return pdf_path
            else:
                QMessageBox.critical(self, "PDF Generation Error", 
                                   "Failed to generate PDF. Please check your data and try again.")
                return None
                
        except ImportError:
            QMessageBox.critical(self, "PDF Generation Error", 
                               "PDF generation requires ReportLab library.\nPlease install it using: pip install reportlab")
            return None
        except Exception as e:
            QMessageBox.critical(self, "PDF Generation Error", 
                               f"Failed to generate PDF: {str(e)}")
            return None

    # The following helper sections mirror the original dialog
    def open_party_selector(self):
        try:
            # Check if typed text exactly matches a party name
            typed_text = self.party_search.text().strip()
            exact_match = None
            
            # Check for exact match (case-insensitive)
            for party_name in self.party_data_map.keys():
                if party_name.upper() == typed_text.upper():
                    exact_match = party_name
                    break
            
            if exact_match:
                # Direct match found, no need to open selector
                selected = exact_match
                self.party_search.setText(selected)
                
                # Focus on Date field after party selection
                if hasattr(self, 'invoice_date'):
                    self.invoice_date.setFocus()
            else:
                # No exact match, open selector
                selected = self._open_party_selector_dialog()
                if selected:
                    self.party_search.setText(selected)
                    
                    # Focus on Date field after party selection
                    if hasattr(self, 'invoice_date'):
                        self.invoice_date.setFocus()
        except Exception as e:
            print(f"Party selector failed: {e}")

    def _focus_first_product_input(self):
        """Focus on the first item row's product input field"""
        try:
            if hasattr(self, 'items_layout'):
                for i in range(self.items_layout.count()):
                    widget = self.items_layout.itemAt(i).widget()
                    if isinstance(widget, InvoiceItemWidget) and hasattr(widget, 'product_input'):
                        widget.product_input.setFocus()
                        return
        except Exception as e:
            print(f"Focus first product input failed: {e}")

    def _open_party_selector_dialog(self, prefill_text: str = None):
        """Create, size, position and open the PartySelector below the input.
        Returns the selected name if accepted, else None.
        """
        dlg = PartySelector(self.parties, self)
        # Prefill search
        try:
            if prefill_text:
                dlg.search.setText(prefill_text)
                dlg.search.setCursorPosition(len(prefill_text))
        except Exception:
            pass
        # Size and position
        try:
            from PyQt5.QtWidgets import QApplication
            input_w = max(300, self.party_search.width())
            dlg_h = min(dlg.sizeHint().height(), 420)
            margin = 8  # vertical gap to avoid overlap with the input
            dlg.resize(input_w, dlg_h)
            bl = self.party_search.mapToGlobal(self.party_search.rect().bottomLeft())
            x, y = bl.x(), bl.y() + margin
            screen = QApplication.desktop().availableGeometry(self.party_search)
            if y + dlg_h > screen.bottom():
                tl = self.party_search.mapToGlobal(self.party_search.rect().topLeft())
                y = tl.y() - dlg_h - margin
            if x + input_w > screen.right():
                x = max(screen.left(), screen.right() - input_w)
            dlg.move(int(x), int(y+65))
        except Exception:
            pass
        return dlg.selected_name if dlg.exec_() == QDialog.Accepted and getattr(dlg, 'selected_name', None) else None

    def create_header_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; }}
        """)
        # Two row header
        frame.setFixedHeight(200)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        label_style = f"""
            QLabel {{ font-weight: 600; color: {TEXT_PRIMARY}; font-size: 14px; border: none; background: transparent; margin: 0; padding: 0; }}
        """

        # ========== ROW 1: Bill Type, Tax Type, (stretch), Date, Invoice No ==========
        row1 = QHBoxLayout()
        row1.setSpacing(15)

        # Bill Type
        bill_box = QWidget()
        bill_box.setStyleSheet("background: transparent;")
        bill_box_layout = QVBoxLayout(bill_box)
        bill_box_layout.setContentsMargins(0, 0, 0, 0)
        bill_box_layout.setSpacing(2)
        bill_lbl = QLabel("💵 Bill Type")
        bill_lbl.setStyleSheet(label_style)
        bill_box_layout.addWidget(bill_lbl)
        try:
            self.billtype_combo
        except Exception:
            self.billtype_combo = QComboBox()
            self.billtype_combo.addItems(["CASH", "CREDIT"])
        self.billtype_combo.setFixedHeight(40)
        # Dynamic background for bill type: green for CASH, red for CREDIT
        def update_billtype_style(text):
            t = (text or '').strip().upper()
            if 'CASH' in t:
                bg = '#10B981'  # green-500
                fg = WHITE
            elif 'CREDIT' in t:
                bg = '#EF4444'  # red-500
                fg = WHITE
            else:
                bg = WHITE
                fg = TEXT_PRIMARY
            try:
                self.billtype_combo.setStyleSheet(f"""
                    QComboBox {{ background: {bg}; color: {fg}; border-radius: 6px; padding: 6px; font-size: 14px; }}
                    QComboBox QAbstractItemView {{
                        background: {bg};
                        color: {TEXT_PRIMARY};
                        selection-background-color: {PRIMARY};
                        selection-color: {WHITE};
                    }}
                """)
            except Exception:
                pass
        update_billtype_style(self.billtype_combo.currentText())
        self.billtype_combo.currentTextChanged.connect(update_billtype_style)
        # Update totals when bill type changes (for Balance Due visibility)
        self.billtype_combo.currentTextChanged.connect(lambda: self.update_totals() if hasattr(self, 'items_layout') else None)
        bill_box_layout.addWidget(self.billtype_combo)
        bill_box.setFixedWidth(140)
        row1.addWidget(bill_box)

        # Tax Type
        gst_box = QWidget()
        gst_box.setStyleSheet("background: transparent;")
        gst_box.setStyleSheet("background: transparent;")
        gst_box_layout = QVBoxLayout(gst_box)
        gst_box_layout.setContentsMargins(0, 0, 0, 0)
        gst_box_layout.setSpacing(2)
        gst_lbl = QLabel("📋 Tax Type")
        gst_lbl.setStyleSheet(label_style)
        gst_box_layout.addWidget(gst_lbl)
        try:
            self.gst_combo
        except Exception:
            self.gst_combo = QComboBox()
            self.gst_combo.addItems(["GST - Same State", "GST - Other State", "Non-GST"])
        self.gst_combo.setFixedHeight(40)
        # Add tooltip explaining GST tax types
        self.gst_combo.setToolTip(
            "<b>GST Tax Types:</b><br><br>"
            "<b>GST - Same State:</b><br>"
            "• CGST (Central GST) - Tax paid to Central Govt<br>"
            "• SGST (State GST) - Tax paid to State Govt<br>"
            "• Used when buyer & seller are in same state<br><br>"
            "<b>GST - Other State:</b><br>"
            "• IGST (Integrated GST) - Tax on interstate sales<br>"
            "• Used when buyer & seller are in different states<br><br>"
            "<b>Non-GST:</b><br>"
            "• No GST applicable (exempt goods/services)"
        )
        try:
            self.gst_combo.setStyleSheet(f"""
                QComboBox {{ background: {PRIMARY}; color: {WHITE}; border-radius: 6px; padding: 6px; font-size: 14px; }}
                QComboBox QAbstractItemView {{
                    background: {PRIMARY};
                    color: {TEXT_PRIMARY};
                    selection-background-color: {PRIMARY};
                    selection-color: {WHITE};
                }}
            """)
        except Exception:
            pass
        # Update totals when tax type changes (for CGST/SGST/IGST visibility)
        self.gst_combo.currentTextChanged.connect(lambda: self.update_totals() if hasattr(self, 'items_layout') else None)
        gst_box_layout.addWidget(self.gst_combo)
        gst_box.setFixedWidth(160)
        row1.addWidget(gst_box)

        # Stretch to push Date and Invoice No to the right
        row1.addStretch()

        # Invoice Date (right corner)
        inv_date_box = QWidget()
        inv_date_box.setStyleSheet("background: transparent;")
        inv_date_box_layout = QVBoxLayout(inv_date_box)
        inv_date_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_date_box_layout.setSpacing(2)
        inv_date_lbl = QLabel("📅 Date")
        inv_date_lbl.setStyleSheet(label_style)
        inv_date_box_layout.addWidget(inv_date_lbl)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setFixedHeight(40)
        self.invoice_date.setStyleSheet(f"""
            QDateEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 4px 6px;
                padding-right: 25px;
                background: {WHITE};
                font-size: 16px;
            }}
            QDateEdit:focus {{
                border: 2px solid {PRIMARY};
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 22px;
                border: none;
                background: {WHITE};
            }}
            QDateEdit::down-arrow {{
                image: url(assets/icons/calendar.png);
                width: 20px;
                height: 20px;
            }}
            /* Calendar popup styling */
            QCalendarWidget {{
                background: {WHITE};
            }}
            QCalendarWidget QWidget {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
            }}
            QCalendarWidget QAbstractItemView {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY};
                selection-color: {WHITE};
            }}
            QCalendarWidget QToolButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
            }}
            QCalendarWidget QMenu {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
            }}
            QCalendarWidget QSpinBox {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
            }}
            QCalendarWidget #qt_calendar_navigationbar {{
                background: {WHITE};
            }}
        """)
        # Connect editingFinished to focus on product input after date
        self.invoice_date.editingFinished.connect(self._focus_first_product_input)
        inv_date_box_layout.addWidget(self.invoice_date)
        inv_date_box.setFixedWidth(140)
        row1.addWidget(inv_date_box)

        # Invoice Number (right corner)
        inv_num_box = QWidget()
        inv_num_box.setStyleSheet("background: transparent;")
        inv_num_box_layout = QVBoxLayout(inv_num_box)
        inv_num_box_layout.setContentsMargins(0, 0, 0, 0)
        inv_num_box_layout.setSpacing(2)
        inv_num_lbl = QLabel("📄 Invoice No")
        inv_num_lbl.setStyleSheet(label_style)
        inv_num_box_layout.addWidget(inv_num_lbl)
        # determine next invoice number
        try:
            if hasattr(db, 'get_next_invoice_number'):
                next_inv_no = db.get_next_invoice_number()
            else:
                invoices = db.get_invoices() or []
                max_no = 0
                for inv in invoices:
                    inv_no = str(inv.get('invoice_no', ''))
                    if inv_no.startswith('INV-'):
                        try:
                            num = int(inv_no.replace('INV-', '').split()[0])
                            max_no = max(max_no, num)
                        except Exception:
                            pass
                next_inv_no = f"INV-{max_no+1:03d}"
        except Exception:
            next_inv_no = "INV-001"
        self.invoice_number = QLineEdit(next_inv_no)
        self.invoice_number.setReadOnly(True)
        self.invoice_number.setFixedHeight(40)
        self.invoice_number.setAlignment(Qt.AlignCenter)
        self.invoice_number.setStyleSheet(f"""
            QLineEdit {{
                color: #EF4444;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                border: 1px solid {BORDER};
                border-radius: 6px;
                background: {WHITE};
            }}
        """)
        inv_num_box_layout.addWidget(self.invoice_number)
        inv_num_box.setFixedWidth(140)
        row1.addWidget(inv_num_box)

        layout.addLayout(row1)

        # ========== ROW 2: Select Party (full width) ==========
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        party_box = QWidget()
        party_box.setStyleSheet("background: transparent;")
        party_box_layout = QVBoxLayout(party_box)
        party_box_layout.setContentsMargins(0, 0, 0, 0)
        party_box_layout.setSpacing(2)
        party_header = QHBoxLayout()
        party_header.setSpacing(5)
        party_label = QLabel("🏢 Select Party")
        party_label.setStyleSheet(label_style)
        party_header.addWidget(party_label)
        add_party_link = QLabel("<a href='#'>+Add New</a>")
        add_party_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_party_link.setOpenExternalLinks(False)
        add_party_link.setStyleSheet("color: #2563EB; font-size: 12px; border: none; background: transparent;")
        add_party_link.setCursor(Qt.PointingHandCursor)
        add_party_link.linkActivated.connect(self.open_quick_add_party_dialog)
        party_header.addWidget(add_party_link)
        party_header.addStretch()
        party_box_layout.addLayout(party_header)

        self.party_search = QLineEdit()
        self.party_search.setPlaceholderText("🔍 Search customer...")
        self.party_search.setFixedHeight(50)
        self.party_search.setFixedWidth(500)
        self.party_search.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 16px;
                background: {WHITE};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY};
            }}
        """)
        # populate party_data_map
        self.party_data_map = {}
        for p in (self.parties or []):
            name = p.get('name', '').strip()
            if name:
                self.party_data_map[name] = p
        self.party_search.textEdited.connect(self.on_party_search_edited)
        self.party_search.returnPressed.connect(self.open_party_selector)
        party_box_layout.addWidget(self.party_search)
        row2.addWidget(party_box, 1)  # Stretch to fill full width

        layout.addLayout(row2)

        return frame

    def open_quick_add_party_dialog(self, link=None):
        """Open a quick dialog to add a new party without leaving the invoice"""
        try:
            from ui.parties.party_form_dialog import PartyDialog
            dialog = PartyDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # Refresh parties list
                self.parties = db.get_parties() or []
                # Update party_data_map
                self.party_data_map = {}
                for party in self.parties:
                    name = party.get('name', '').strip()
                    if name:
                        self.party_data_map[name] = party
                
                # If a new party was created, select it automatically
                if hasattr(dialog, 'saved_party_name') and dialog.saved_party_name:
                    self.party_search.setText(dialog.saved_party_name)
                    highlight_success(self.party_search)
                    QMessageBox.information(self, "Success", f"✅ Party '{dialog.saved_party_name}' added and selected!")
                else:
                    QMessageBox.information(self, "Success", "✅ New party added! You can now search and select it.")
        except ImportError:
            QMessageBox.warning(self, "Feature Unavailable", "Party dialog module not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open party dialog: {str(e)}")

    def on_party_search_edited(self, text: str):
        """Open PartySelector when user types in the party search box.
        Prefill selector search with typed text and avoid opening multiple times.
        """
        try:
            if self._party_selector_active:
                return
            if not text or not text.strip():
                return
            self._party_selector_active = True
            selected = self._open_party_selector_dialog(prefill_text=text)
            if selected:
                # Set chosen party name back to the input without re-triggering textEdited
                old_state = self.party_search.blockSignals(True)
                try:
                    self.party_search.setText(selected)
                finally:
                    self.party_search.blockSignals(old_state)
        except Exception as e:
            print(f"Party search edit handler error: {e}")
        finally:
            self._party_selector_active = False

    def on_invoice_type_changed(self, invoice_type: str):
        """Update tax rates for all items when invoice type changes"""
        try:
            for i in range(self.items_layout.count() - 1):  # exclude the stretch at the end
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    widget.update_tax_rate_for_invoice_type(invoice_type)
            
            # Update overall totals
            self.update_totals()
        except Exception as e:
            print(f"Invoice type change handler error: {e}")

    def on_bill_type_changed(self, bill_type: str):
        """Show/hide Balance Due based on bill type"""
        try:
            # Update totals to reflect bill type visibility changes
            self.update_totals()
        except Exception as e:
            print(f"Bill type change handler error: {e}")

    def create_items_section(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background: {WHITE}; border: 2px solid {BORDER}; border-radius: 15px; margin: 5px; }}
        """)
        # frame.setFixedHeight(420)  # Reduced height
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 10)

        # Quick Products Section - Show recently used products as clickable chips
        quick_products_layout = QHBoxLayout()
        quick_products_layout.setSpacing(8)
        quick_products_layout.setContentsMargins(5, 5, 5, 5)
        
        quick_label = QLabel("⚡ Quick Add:")
        quick_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold; border: none;")
        quick_products_layout.addWidget(quick_label)
        
        # Get top 5 most used products (sorted by sales_rate as proxy for popularity)
        top_products = sorted(self.products[:8], key=lambda x: x.get('sales_rate', 0), reverse=True)[:5]
        
        for product in top_products:
            chip = QPushButton(product.get('name', '')[:20])  # Truncate long names
            chip.setFixedHeight(28)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setFocusPolicy(Qt.NoFocus)  # Prevent keyboard focus - only mouse clicks
            chip.setToolTip(f"Add {product.get('name', '')} - ₹{product.get('sales_rate', 0):,.2f}")
            chip.setStyleSheet(f"""
                QPushButton {{
                    background: #EFF6FF;
                    color: {PRIMARY};
                    border: 1px solid {PRIMARY};
                    border-radius: 14px;
                    font-size: 11px;
                    padding: 4px 12px;
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: {WHITE};
                }}
            """)
            # Store product data in the button
            chip.product_data = product
            chip.clicked.connect(lambda checked, p=product: self.quick_add_product(p))
            quick_products_layout.addWidget(chip)
        
        quick_products_layout.addStretch()

        # Items count badge at right corner of Quick Add row
        items_label = QLabel("📦 Items:")
        items_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        quick_products_layout.addWidget(items_label)
        self.item_count_badge = QLabel("0")
        self.item_count_badge.setFixedSize(56, 46)
        self.item_count_badge.setStyleSheet(f"""
            QLabel {{ background: {PRIMARY}; color: {WHITE}; border-radius: 14px; font-size: 14px; font-weight: bold; }}
        """)
        quick_products_layout.addWidget(self.item_count_badge)

        layout.addLayout(quick_products_layout)

        headers_layout = QHBoxLayout()
        headers_layout.setSpacing(0)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        # Add leading No column for row numbering and HSN No after Product
        headers = [
            "No", "🛍️ Product", "📦 HSN No", "Qty", "📏 Unit",
            "💰 Rate", "🏷️ Disc%", "📋 Tax%", "💵 Amount", "❌ Action"
        ]
        widths = [100, 500, 100, 100, 85, 110, 110, 110, 110, 110]
        for header, width in zip(headers, widths):
            label = QLabel(header)
            label.setFixedWidth(width)
            label.setFixedHeight(35)
            label.setStyleSheet(f"""
                QLabel {{ font-weight: bold; color: {TEXT_PRIMARY}; padding: 0; margin: 0; background: {BACKGROUND}; border: 1px solid {PRIMARY}; border-radius: 6px; font-size: 13px; }}
            """)
            label.setAlignment(Qt.AlignCenter)
            headers_layout.addWidget(label)
        layout.addLayout(headers_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # scroll_area.setFixedHeight(380)  # Reduced scroll area height
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: 1px solid {BORDER}; border-radius: 10px; background: {BACKGROUND}; }}
        """)
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(1)
        self.items_layout.setContentsMargins(1, 1, 1, 1)
        self.items_layout.addStretch()
        scroll_area.setWidget(self.items_widget)
        layout.addWidget(scroll_area)
        
        # Subtotal row at bottom, aligned with Amount column
        subtotal_row = QHBoxLayout()
        subtotal_row.setSpacing(0)
        subtotal_row.setContentsMargins(0, 5, 0, 0)
        
        # Add spacers to align with Amount column (No:100 + Product:500 + HSN:100 + Qty:100 + Unit:85 + Rate:110 + Disc:110 + Tax:110 = 1215)
        spacer_widget = QWidget()
        spacer_widget.setFixedWidth(1215)
        subtotal_row.addWidget(spacer_widget)
        
        # Subtotal label aligned with Amount header
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setFixedWidth(110)
        subtotal_label.setFixedHeight(25)
        subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        subtotal_label.setStyleSheet(f"font-size: 13px; border: none; background: transparent;")
        subtotal_row.addWidget(subtotal_label)
        
        # Subtotal value - simple style like totals section
        self.items_subtotal_label = QLabel("₹0.00")
        self.items_subtotal_label.setFixedWidth(110)
        self.items_subtotal_label.setFixedHeight(25)
        self.items_subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_subtotal_label.setStyleSheet(f"font-size: 13px; border: none; background: transparent;")
        subtotal_row.addWidget(self.items_subtotal_label)
        
        # Action column spacer
        action_spacer = QWidget()
        action_spacer.setFixedWidth(110)
        subtotal_row.addWidget(action_spacer)
        
        layout.addLayout(subtotal_row)
        
        return frame

    def create_totals_section(self):
        frame = QFrame()
        frame.setStyleSheet(f""" QFrame {{ background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px; }} """)
        frame.setMinimumHeight(150)  # Minimum height instead of fixed
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)

        # Notes area: lazy add via text link
        notes_container = QVBoxLayout()
        notes_header = QHBoxLayout()
        add_note_link = QLabel("<a href='add'>+Add Note</a>")
        add_note_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        add_note_link.setOpenExternalLinks(False)
        add_note_link.setStyleSheet("color: #2563EB; font-size: 13px; border: none;")
        # Handler to create/show notes editor lazily
        def _handle_add_note_link(_):
            try:
                if not hasattr(self, 'notes') or self.notes is None:
                    self.notes = QTextEdit()
                    self.notes.setPlaceholderText("Add any additional information or terms...")
                    self.notes.setStyleSheet(f"border: 2px solid {BORDER}; border-radius: 8px; padding: 10px; background: {WHITE}; font-size: 13px;")
                    self.notes.setFixedHeight(80)
                    notes_container.insertWidget(1, self.notes)
                else:
                    self.notes.setVisible(True)
            except Exception as e:
                print(f"Failed to add notes editor: {e}")
        add_note_link.linkActivated.connect(_handle_add_note_link)
        # Place the link at the left; stretch goes after to push remaining content to the right
        notes_header.addWidget(add_note_link)
        notes_header.addStretch()
        notes_container.addLayout(notes_header)
        # Initially, no notes editor is shown; created on demand via link
        if not hasattr(self, 'notes'):
            self.notes = None
        
        # Amount in words label - positioned below notes
        amount_words_container = QVBoxLayout()
        amount_words_container.setSpacing(2)
        
        amount_words_title = QLabel("💰 In Words:")
        amount_words_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        amount_words_container.addWidget(amount_words_title)
        
        self.amount_in_words_label = QLabel("Zero Rupees Only")
        self.amount_in_words_label.setWordWrap(True)
        self.amount_in_words_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-style: italic;
                color: {PRIMARY};
                background: #EFF6FF;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 10px;
            }}
        """)
        self.amount_in_words_label.setMinimumWidth(280)
        self.amount_in_words_label.setMaximumWidth(400)
        self.amount_in_words_label.setMaximumHeight(50)
        amount_words_container.addWidget(self.amount_in_words_label)
        
        notes_container.addLayout(amount_words_container)
        notes_container.addStretch()

        layout.addLayout(notes_container, 2)

        # Totals on the right
        self.totals_layout = QFormLayout()  # Store reference for show/hide functionality
        self.totals_layout.setSpacing(8)  # Better spacing between rows
        
        # Hidden subtotal label for backward compatibility (not displayed - shown in items section)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setVisible(False)
        
        # Discount label (visible only when discount > 0)
        self.discount_label = QLabel("-₹0.00")
        self.discount_label.setStyleSheet("font-size: 14px; color: red; border: none; background: transparent;")
        self.totals_layout.addRow("Discount:", self.discount_label)
        
        # Tax row with breakdown box beside it
        # Create a container for Tax amount + breakdown box
        tax_container = QWidget()
        tax_container.setStyleSheet("background: transparent; border: none;")
        tax_container_layout = QHBoxLayout(tax_container)
        tax_container_layout.setContentsMargins(0, 0, 0, 0)
        tax_container_layout.setSpacing(8)
        
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        self.tax_label.setFixedWidth(80)
        tax_container_layout.addWidget(self.tax_label)
        
        # Tax breakdown box (shows CGST+SGST or IGST)
        self.tax_breakdown_box = QLabel("")
        self.tax_breakdown_box.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {TEXT_PRIMARY};
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 3px 8px;
            }}
        """)
        self.tax_breakdown_box.setVisible(False)
        tax_container_layout.addWidget(self.tax_breakdown_box)
        tax_container_layout.addStretch()
        
        # Store reference to tax container row
        self.tax_row_label = QLabel("Tax:")
        self.tax_row_label.setStyleSheet("font-size: 14px; border-radius: 6px;; background: transparent;")
        self.totals_layout.addRow(self.tax_row_label, tax_container)
        
        # Hidden GST breakdown labels (for backward compatibility - values still calculated)
        self.cgst_label = QLabel("₹0.00")
        self.cgst_label.setVisible(False)
        self.sgst_label = QLabel("₹0.00")
        self.sgst_label.setVisible(False)
        self.igst_label = QLabel("₹0.00")
        self.igst_label.setVisible(False)
        
        # Round-off row (hidden by default, shown when grand total has decimal)
        self.roundoff_container = QWidget()
        roundoff_layout = QHBoxLayout(self.roundoff_container)
        roundoff_layout.setContentsMargins(0, 0, 0, 0)
        roundoff_layout.setSpacing(5)
        
        self.roundoff_link = QLabel("<a href='roundoff'>Round Off</a>")
        self.roundoff_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.roundoff_link.setOpenExternalLinks(False)
        self.roundoff_link.setStyleSheet("color: #2563EB; font-size: 12px; border: none;")
        self.roundoff_link.linkActivated.connect(self.show_roundoff_options)
        roundoff_layout.addWidget(self.roundoff_link)
        
        self.roundoff_value_label = QLabel("₹0.00")
        self.roundoff_value_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        roundoff_layout.addWidget(self.roundoff_value_label)
        
        self.roundoff_container.setVisible(False)
        
        # Store round-off amount
        self.roundoff_amount = 0.0
        
        # Grand Total row with roundoff beside it
        grand_total_container = QWidget()
        grand_total_container.setStyleSheet("background: transparent; border: none;")
        grand_total_container_layout = QHBoxLayout(grand_total_container)
        grand_total_container_layout.setContentsMargins(0, 0, 0, 0)
        grand_total_container_layout.setSpacing(8)
        
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY}; background: {BACKGROUND}; padding: 6px 10px; border-radius: 6px;")
        self.grand_total_label.setMinimumWidth(120)
        grand_total_container_layout.addWidget(self.grand_total_label)
        
        # Add roundoff container beside grand total
        grand_total_container_layout.addWidget(self.roundoff_container)
        grand_total_container_layout.addStretch()
        
        self.totals_layout.addRow("Grand Total:", grand_total_container)
        
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.paid_amount_spin = QDoubleSpinBox()
        self.paid_amount_spin.setRange(0, 999999999)
        self.paid_amount_spin.setDecimals(2)
        self.paid_amount_spin.setPrefix("₹")
        self.paid_amount_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                font-size: 14px;
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px;
                background: {WHITE};
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid {PRIMARY};
            }}
        """)
        self.paid_amount_spin.setFixedWidth(140)
        self.paid_amount_spin.setFixedHeight(30)
        self.paid_amount_spin.setValue(0)
        # totals_layout.addRow("Paid Amount:", self.paid_amount_spin)
        # Balance label - same size as Grand Total
        self.balance_label = QLabel("₹0.00")
        self.balance_label.setMinimumWidth(120)
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #EF4444; background: #FEF2F2; padding: 6px 10px; border-radius: 6px;")
        # Store reference to balance due row for show/hide functionality
        self.balance_due_row = self.totals_layout.rowCount()
        self.totals_layout.addRow("Balance Due:", self.balance_label)
        # Update balance when paid amount changes
        self.paid_amount_spin.valueChanged.connect(self.update_balance_due)
        layout.addStretch(1)
        layout.addLayout(self.totals_layout, 1)
        return frame

    def show_roundoff_options(self, link=None):
        """Show popup with round-off options (up/down)"""
        try:
            grand_total = float(self.grand_total_label.text().replace('₹','').replace(',',''))
            
            # Calculate round down and round up values
            round_down = int(grand_total)
            round_up = round_down + 1 if grand_total > round_down else round_down
            
            diff_down = grand_total - round_down
            diff_up = round_up - grand_total
            
            # Create popup menu with minimum width
            menu = QMenu(self)
            menu.setMinimumWidth(180)
            menu.setStyleSheet(f"""
                QMenu {{
                    background: {WHITE};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 5px;
                    min-width: 180px;
                }}
                QMenu::item {{
                    padding: 10px 15px;
                    border-radius: 4px;
                    color: {TEXT_PRIMARY};
                    background: transparent;
                }}
                QMenu::item:selected {{
                    background: {PRIMARY};
                    color: {WHITE};
                }}
            """)
            
            # Round down option - shorter text
            down_action = QAction(f"⬇ Down (-₹{diff_down:.2f})", self)
            down_action.triggered.connect(lambda: self.apply_roundoff(-diff_down, round_down))
            menu.addAction(down_action)
            
            # Round up option - shorter text
            up_action = QAction(f"⬆ Up (+₹{diff_up:.2f})", self)
            up_action.triggered.connect(lambda: self.apply_roundoff(diff_up, round_up))
            menu.addAction(up_action)
            
            # No rounding option
            no_round_action = QAction("✕ No Rounding", self)
            no_round_action.triggered.connect(lambda: self.apply_roundoff(0, grand_total))
            menu.addAction(no_round_action)
            
            # Show menu at link position
            menu.exec_(self.roundoff_link.mapToGlobal(self.roundoff_link.rect().bottomLeft()))
            
        except Exception as e:
            print(f"Error showing roundoff options: {e}")

    def apply_roundoff(self, roundoff_amount, final_total):
        """Apply the selected round-off amount"""
        try:
            self.roundoff_amount = roundoff_amount
            
            if roundoff_amount > 0:
                self.roundoff_value_label.setText(f"+₹{roundoff_amount:.2f}")
                self.roundoff_value_label.setStyleSheet("font-size: 14px; color: green; border: none; background: transparent;")
            elif roundoff_amount < 0:
                self.roundoff_value_label.setText(f"-₹{abs(roundoff_amount):.2f}")
                self.roundoff_value_label.setStyleSheet("font-size: 14px; color: red; border: none; background: transparent;")
            else:
                self.roundoff_value_label.setText("₹0.00")
                self.roundoff_value_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
            
            # Update grand total with rounded value
            self.grand_total_label.setText(f"₹{final_total:,.2f}")
            
            # Update amount in words
            if hasattr(self, 'amount_in_words_label'):
                self.amount_in_words_label.setText(number_to_words_indian(final_total))
            
            # Update balance due
            self.update_balance_due()
            
        except Exception as e:
            print(f"Error applying roundoff: {e}")

    def update_balance_due(self):
            try:
                grand_total = 0.0
                try:
                    grand_total = float(self.grand_total_label.text().replace('₹','').replace(',',''))
                except Exception:
                    pass
                paid = self.paid_amount_spin.value()
                balance = max(0, grand_total - paid)
                self.balance_label.setText(f"₹{balance:,.2f}")
            except Exception:
                self.balance_label.setText("₹0.00")
            
    # Items management
    def quick_add_product(self, product_data):
        """Quickly add a product to the invoice from the quick-select chips"""
        try:
            # Check if party is selected first
            if hasattr(self, 'party_search'):
                party_text = self.party_search.text().strip()
                if not party_text:
                    highlight_error(self.party_search, "Please select a party first")
                    self.party_search.setFocus()
                    return
            
            # Check if there's an empty first row that we can fill instead of creating new
            first_item_widget = None
            for i in range(self.items_layout.count()):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    first_item_widget = widget
                    break
            
            # If first row exists and has no product selected, fill it instead of creating new row
            if first_item_widget and not first_item_widget.product_input.text().strip():
                item_widget = first_item_widget
            else:
                # Create a new item widget with the product pre-selected
                item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
                item_widget.add_requested.connect(self.add_item)
                item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
                item_widget.item_changed.connect(self.update_totals)
                item_widget.setStyleSheet(f""" QWidget:hover {{ background: rgba(59, 130, 246, 0.05); border-radius: 8px; }} """)
                # Add to layout
                self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
            
            # Pre-fill with the product data
            item_widget.product_input.setText(product_data.get('name', ''))
            item_widget.selected_product = product_data
            item_widget.rate_spin.setValue(product_data.get('sales_rate', 0))
            item_widget.unit_label.setText(product_data.get('unit', 'Piece'))
            item_widget.hsn_edit.setText(product_data.get('hsn_code', ''))
            
            # Set tax based on invoice type
            if hasattr(self, 'gst_combo') and self.gst_combo.currentText() == "Non-GST":
                item_widget.tax_spin.setValue(0)
            else:
                item_widget.tax_spin.setValue(product_data.get('tax_rate', 18))
            
            # Calculate total for the item
            item_widget.calculate_total()
            
            self.number_items()
            self.update_totals()
            
            # Focus on quantity field for quick entry
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.setFocus())
            QTimer.singleShot(50, lambda: item_widget.quantity_spin.selectAll())
            
            # Brief success highlight
            highlight_success(item_widget.product_input, duration_ms=1000)
            
        except Exception as e:
            print(f"Quick add product error: {e}")
            QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")

    def add_item(self):
        # Check if the last item row has a product selected before adding new row
        if self.items_layout.count() > 1:  # There's at least one item row (plus stretch)
            last_item_widget = None
            # Find the last InvoiceItemWidget
            for i in range(self.items_layout.count() - 2, -1, -1):
                widget = self.items_layout.itemAt(i).widget()
                if isinstance(widget, InvoiceItemWidget):
                    last_item_widget = widget
                    break
            
            if last_item_widget:
                # Check if product is selected (not empty)
                product_text = last_item_widget.product_input.text().strip()
                if not product_text:
                    # Highlight the empty product field and show message
                    highlight_error(last_item_widget.product_input, "Please select a product first")
                    last_item_widget.product_input.setFocus()
                    return  # Don't add new row
        
        item_widget = InvoiceItemWidget(products=self.products, parent_dialog=self)
        # Wire row-level ➕ to add another item row
        item_widget.add_requested.connect(self.add_item)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_item(item_widget))
        item_widget.item_changed.connect(self.update_totals)
        item_widget.setStyleSheet(f""" QWidget:hover {{ background: rgba(59, 130, 246, 0.05); border-radius: 8px; }} """)
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        # Assign row numbers after insertion
        self.number_items()
        self.update_totals()
        
        # Auto-scroll to show the new row and set focus
        QTimer.singleShot(50, lambda: self.scroll_to_new_item(item_widget))

    def remove_item(self, item_widget):
        if self.items_layout.count() <= 2:
            QMessageBox.warning(self, "Cannot Remove", "🚫 At least one item is required for the invoice!")
            return
        reply = QMessageBox.question(self, "Remove Item", "❓ Are you sure you want to remove this item?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.items_layout.removeWidget(item_widget)
            item_widget.deleteLater()
            # Re-number items after removal
            self.number_items()
            self.update_totals()

    def scroll_to_new_item(self, item_widget):
        """Auto-scroll to show the newly added item and set focus on its product input"""
        try:
            # Find the scroll area that contains the items
            scroll_area = None
            for i in range(self.items_frame.layout().count()):
                widget = self.items_frame.layout().itemAt(i).widget()
                if isinstance(widget, QScrollArea):
                    scroll_area = widget
                    break
            
            if scroll_area and item_widget:
                # Ensure the widget is visible by scrolling to it
                scroll_area.ensureWidgetVisible(item_widget)
                
                # Set focus on the product input field
                item_widget.product_input.setFocus()
                
        except Exception as e:
            print(f"Error scrolling to new item: {e}")
            # Fallback: just set focus without scrolling
            try:
                item_widget.product_input.setFocus()
            except Exception:
                pass

    def number_items(self):
        """Update the read-only row number textbox in each item row (1-based)."""
        try:
            row = 1
            for i in range(self.items_layout.count() - 1):  # exclude the stretch at the end
                w = self.items_layout.itemAt(i).widget()
                if isinstance(w, InvoiceItemWidget) and hasattr(w, 'set_row_number'):
                    w.set_row_number(row)
                    row += 1
        except Exception as e:
            print(f"Error numbering items: {e}")

    def update_totals(self):
        try:
            subtotal, total_discount, total_tax, item_count = 0, 0, 0, 0
            total_cgst, total_sgst, total_igst = 0, 0, 0
            
            # Get current tax type selection
            tax_type = self.gst_combo.currentText() if hasattr(self, 'gst_combo') else 'GST - Same State'
            
            # Determine state based on tax type selection
            is_interstate = (tax_type == 'GST - Other State')
            is_non_gst = (tax_type == 'Non-GST')
            
            for i in range(self.items_layout.count() - 1):
                item_widget = self.items_layout.itemAt(i).widget()
                if isinstance(item_widget, InvoiceItemWidget):
                    item_data = item_widget.get_item_data()
                    if item_data:
                        quantity = item_data['quantity']
                        rate = item_data['rate']
                        item_subtotal = quantity * rate
                        subtotal += item_subtotal
                        total_discount += item_data['discount_amount']
                        total_tax += item_data['tax_amount']
                        item_count += 1
                        
                        # Calculate GST breakdown for this item
                        tax_amount = item_data['tax_amount']
                        if tax_amount > 0 and not is_non_gst:  # Only calculate GST breakdown if there's tax and not Non-GST
                            if is_interstate:
                                # Inter-state: All tax goes to IGST
                                total_igst += tax_amount
                            else:
                                # Intra-state: Split between CGST and SGST
                                cgst_amount = tax_amount / 2
                                sgst_amount = tax_amount / 2
                                total_cgst += cgst_amount
                                total_sgst += sgst_amount
            
            grand_total = subtotal - total_discount + total_tax
            
            # Update items section subtotal label
            if hasattr(self, 'items_subtotal_label'):
                self.items_subtotal_label.setText(f"₹{subtotal:,.2f}")
            
            # Update all totals labels
            self.subtotal_label.setText(f"₹{subtotal:,.2f}")
            self.discount_label.setText(f"-₹{total_discount:,.2f}")
            self.cgst_label.setText(f"₹{total_cgst:,.2f}")
            self.sgst_label.setText(f"₹{total_sgst:,.2f}")
            self.igst_label.setText(f"₹{total_igst:,.2f}")
            self.tax_label.setText(f"₹{total_tax:,.2f}")
            self.grand_total_label.setText(f"₹{grand_total:,.2f}")
            
            # Update tax breakdown box beside Tax amount
            if hasattr(self, 'tax_breakdown_box'):
                if not is_non_gst and total_tax > 0:
                    if is_interstate:
                        # Show IGST breakdown with HTML formatting (secondary text for label, primary text for price)
                        self.tax_breakdown_box.setText(f"<span style='color: {TEXT_SECONDARY};'>IGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_igst:,.2f}</span>")
                    else:
                        # Show CGST + SGST breakdown with HTML formatting
                        self.tax_breakdown_box.setText(f"<span style='color: {TEXT_SECONDARY};'>CGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_cgst:,.2f}</span> + <span style='color: {TEXT_SECONDARY};'>SGST:</span> <span style='color: {TEXT_PRIMARY};'>₹{total_sgst:,.2f}</span>")
                    self.tax_breakdown_box.setVisible(True)
                else:
                    self.tax_breakdown_box.setVisible(False)
            
            # Update amount in words
            if hasattr(self, 'amount_in_words_label'):
                self.amount_in_words_label.setText(number_to_words_indian(grand_total))
            
            # Check if grand total has decimal (for round-off)
            has_decimal = (grand_total % 1) != 0
            if hasattr(self, 'roundoff_container'):
                self.roundoff_container.setVisible(has_decimal and grand_total > 0)
            
            # Get bill type for Balance Due visibility
            bill_type = self.billtype_combo.currentText() if hasattr(self, 'billtype_combo') else 'CASH'
            is_credit = (bill_type == 'CREDIT')
            
            # ========== VISIBILITY LOGIC ==========
            # 1) CASH, No Tax, No Disc → Grand Total only
            # 2) CREDIT, No Tax, No Disc → Grand Total + Balance Due
            # 3) CREDIT, Tax, No Disc → Tax (with breakdown) + Grand Total + Balance Due
            # 4) CREDIT, Tax, Disc → Disc + Tax (with breakdown) + Grand Total + Balance Due
            
            has_tax = (total_tax > 0 and not is_non_gst)
            has_discount = (total_discount > 0)
            
            # Show/hide Discount row
            if hasattr(self, 'discount_label'):
                # Find and hide discount row in form layout
                for i in range(self.totals_layout.rowCount()):
                    label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                    if label_item and label_item.widget():
                        label_text = label_item.widget().text()
                        if label_text == "Discount:":
                            label_item.widget().setVisible(has_discount)
                            if field_item and field_item.widget():
                                field_item.widget().setVisible(has_discount)
            
            # Show/hide Tax row (with breakdown box)
            if hasattr(self, 'tax_row_label'):
                self.tax_row_label.setVisible(has_tax)
                # Find tax container in form layout
                for i in range(self.totals_layout.rowCount()):
                    label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                    if label_item and label_item.widget() == self.tax_row_label:
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(has_tax)
            
            # Show/hide Balance Due row (only for CREDIT)
            for i in range(self.totals_layout.rowCount()):
                label_item = self.totals_layout.itemAt(i, QFormLayout.LabelRole)
                field_item = self.totals_layout.itemAt(i, QFormLayout.FieldRole)
                if label_item and label_item.widget():
                    label_text = label_item.widget().text()
                    if label_text == "Balance Due:":
                        label_item.widget().setVisible(is_credit)
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(is_credit)
            
            # Update item count badge
            if hasattr(self, 'item_count_badge'):
                self.item_count_badge.setText(str(item_count))
                # Change badge color based on item count
                if item_count == 0:
                    badge_color = TEXT_SECONDARY
                elif item_count >= 5:
                    badge_color = SUCCESS
                else:
                    badge_color = PRIMARY
                self.item_count_badge.setStyleSheet(f"""
                    QLabel {{
                        background: {badge_color};
                        color: {WHITE};
                        border-radius: 12px;
                        font-size: 18px;
                        font-weight: bold;
                        padding: 8px;
                    }}
                """)
            
            self.update_balance_due()
        except Exception as e:
            print(f"Error updating totals: {e}")

    def save_invoice(self):
        # Show confirmation dialog first
        action_text = "update" if self.invoice_data else "save"
        reply = QMessageBox.question(
            self, 
            "Confirm Save", 
            f"Do you want to {action_text} this invoice?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return  # User cancelled
        
        # Validate party selection with visual feedback
        party_text = getattr(self, 'party_search').text().strip()
        party_data = getattr(self, 'party_data_map', {}).get(party_text)
        if not party_data or not party_text:
            show_validation_error(
                self, 
                self.party_search if hasattr(self, 'party_search') else None,
                "Validation Error", 
                "Please select a valid party from the search!"
            )
            return
        
        # Validate items with visual feedback
        items = []
        for i in range(self.items_layout.count() - 1):
            item_widget = self.items_layout.itemAt(i).widget()
            if isinstance(item_widget, InvoiceItemWidget):
                item_data = item_widget.get_item_data()
                if item_data:
                    items.append(item_data)
        
        if not items:
            # Highlight the item count badge to draw attention
            if hasattr(self, 'item_count_badge'):
                highlight_error(self.item_count_badge, "Add at least one item")
            QMessageBox.warning(self, "Validation Error", "⚠️ Please add at least one item with a valid product!")
            return
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        total_discount = sum(item['discount_amount'] for item in items)
        total_tax = sum(item['tax_amount'] for item in items)
        grand_total = subtotal - total_discount + total_tax
        notes_text = ''
        if hasattr(self, 'notes') and self.notes is not None:
            notes_text = self.notes.toPlainText()
        invoice_data = {
            'party_id': party_data['id'],
            'party_name': party_data['name'],
            'invoice_date': self.invoice_date.date().toString('yyyy-MM-dd'),
            'notes': notes_text,
            'subtotal': subtotal,
            'total_discount': total_discount,
            'grand_total': grand_total,
            'paid_amount': self.paid_amount_spin.value(),
            'balance_due': max(0, grand_total - self.paid_amount_spin.value()),
            'status': 'Draft',
            'items': items
        }
        try:
            invoice_no = self.invoice_number.text().strip() if hasattr(self, 'invoice_number') else ''
            if not invoice_no:
                QMessageBox.warning(self, "Error", "Invoice number cannot be empty!")
                return
            # Check for duplicate invoice number only when creating new
            if not self.invoice_data and hasattr(db, 'invoice_no_exists') and db.invoice_no_exists(invoice_no):
                QMessageBox.warning(self, "Error", f"Invoice number '{invoice_no}' already exists. Please use a unique invoice number.")
                return
            invoice_data['invoice_no'] = invoice_no
            if self.invoice_data:
                invoice_data['id'] = self.invoice_data['id']
                db.update_invoice(invoice_data)
                # Update invoice items
                db.delete_invoice_items(self.invoice_data['id'])
                for item in items:
                    db.add_invoice_item(
                        self.invoice_data['id'],
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
                # Update stock for sales items (decrease stock for products with track_stock enabled)
                db.update_stock_for_sales_items(items)
                # Show success with visual feedback
                highlight_success(self.invoice_number)
                QMessageBox.information(self, "Success", "✅ Invoice updated successfully!")
            else:
                # Create new invoice
                invoice_id = db.add_invoice(
                    invoice_no,
                    invoice_data.get('invoice_date', ''),
                    invoice_data.get('party_id', ''),
                    invoice_data.get('status', 'GST'),
                    invoice_data.get('subtotal', 0),
                    0, 0, 0, 0,  # cgst, sgst, igst, round_off (defaults)
                    invoice_data.get('grand_total', 0)
                )
                # Add invoice items
                for item in items:
                    db.add_invoice_item(
                        invoice_id,
                        item.get('product_id'),
                        item['product_name'],
                        item.get('hsn_no', ''),
                        item['quantity'],
                        item.get('unit', 'Piece'),
                        item['rate'],
                        item['discount_percent'],
                        item['discount_amount'],
                        item['tax_percent'],
                        item['tax_amount'],
                        item['amount']
                    )
                # Update stock for sales items (decrease stock for products with track_stock enabled)
                db.update_stock_for_sales_items(items)
                # Show success with visual feedback
                highlight_success(self.invoice_number)
                QMessageBox.information(self, "Success", "✅ Invoice created successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save invoice: {str(e)}")

    def reset_form(self):
        """Reset all form fields to defaults and update date to today"""
        try:
            # Show confirmation dialog first
            reply = QMessageBox.question(
                self, 
                "Confirm Reset", 
                "Are you sure you want to reset all fields? This will clear all entered data.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default to No for safety
            )
            
            if reply != QMessageBox.Yes:
                return  # User cancelled
            
            # Reset date to today
            if hasattr(self, 'invoice_date') and self.invoice_date is not None:
                self.invoice_date.setDate(QDate.currentDate())
            
            # Reset invoice number to next available
            if hasattr(self, 'invoice_number') and self.invoice_number is not None:
                try:
                    if hasattr(db, 'get_next_invoice_number'):
                        next_inv_no = db.get_next_invoice_number()
                    else:
                        # Fallback logic matching create_header_section
                        invoices = db.get_invoices() or []
                        max_no = 0
                        for inv in invoices:
                            inv_no = str(inv.get('invoice_no', ''))
                            if inv_no.startswith('INV-'):
                                try:
                                    num = int(inv_no.replace('INV-', '').split()[0])
                                    max_no = max(max_no, num)
                                except Exception:
                                    pass
                        next_inv_no = f"INV-{max_no+1:03d}"
                    self.invoice_number.setText(next_inv_no)
                except Exception as e:
                    print(f"Error generating next invoice number: {e}")
                    self.invoice_number.setText("INV-001")
            
            # Clear party search
            if hasattr(self, 'party_search') and self.party_search is not None:
                self.party_search.clear()
                # Repopulate party data map from parties list (don't clear it completely)
                if hasattr(self, 'party_data_map'):
                    self.party_data_map = {}
                    # Repopulate from self.parties
                    for party in self.parties:
                        name = party.get('name', '').upper()
                        if name:
                            self.party_data_map[name] = party
            
            # Clear notes if it exists
            if hasattr(self, 'notes') and self.notes is not None:
                self.notes.clear()
            
            # Reset paid amount
            if hasattr(self, 'paid_amount_spin') and self.paid_amount_spin is not None:
                self.paid_amount_spin.setValue(0.0)
            
            # Remove all item widgets except the stretch at the end
            if hasattr(self, 'items_layout') and self.items_layout is not None:
                # Remove all items in reverse order (preserve stretch at end)
                for i in reversed(range(self.items_layout.count() - 1)):
                    item = self.items_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, InvoiceItemWidget):
                            self.items_layout.removeWidget(widget)
                            widget.deleteLater()
                
                # Add one new empty item
                self.add_item()
            
            # Update totals display
            self.update_totals()
            
            # Re-enable save buttons (in case they were disabled after a FINAL save)
            if hasattr(self, 'save_button'):
                self.save_button.setEnabled(True)
                self.save_button.setText("💾 Save Invoice")
            
            if hasattr(self, 'save_print_button'):
                self.save_print_button.setEnabled(True)
                self.save_print_button.setText("� Save Print")
            
            # Clear invoice_data so this is treated as a new invoice
            self.invoice_data = None
            
            # Show success message
            QMessageBox.information(self, "Reset Complete", "Invoice has been reset. You can now create a new invoice.")
            
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Failed to reset invoice: {str(e)}")


