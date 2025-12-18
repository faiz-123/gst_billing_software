"""
Custom widgets and reusable UI components
"""

from PyQt5.QtWidgets import (
    QPushButton, QLineEdit, QLabel, QComboBox, QTableWidget, 
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QAbstractItemView
)
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from theme import (
    get_button_style, BORDER, WHITE, TEXT_PRIMARY, FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE, BACKGROUND, TEXT_SECONDARY
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

class SidebarButton(QPushButton):
    """Enhanced sidebar button with active state"""
    def __init__(self, text, icon="", parent=None):
        super().__init__(parent)
        self.text = text
        self.icon = icon
        self.is_active = False
        self.is_collapsed = False
        self.update_text()
        self.setObjectName("sidebarButton")
        
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
        self.expanded_width = 300  # Increased from 280
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
        """Create header with company name and toggle button"""
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 15, 15)
        
        # Company name section
        self.company_section = QHBoxLayout()
        
        # Company name title
        self.title_label = QLabel(self.company_name)
        self.title_label.setObjectName("sidebarTitle")
        self.title_label.setWordWrap(True)  # Allow text wrapping for long company names
        
        self.company_section.addWidget(self.title_label, 1)
        
        # Toggle button
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setObjectName("toggleButton")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        header_layout.addLayout(self.company_section, 1)
        header_layout.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(header_frame)
        
    def create_menu_section(self):
        """Create scrollable menu section"""
        # Menu container
        self.menu_frame = QFrame()
        self.menu_frame.setObjectName("menuFrame")
        
        self.menu_layout = QVBoxLayout(self.menu_frame)
        self.menu_layout.setContentsMargins(15, 20, 15, 10)
        self.menu_layout.setSpacing(8)
        
        self.main_layout.addWidget(self.menu_frame, 1)
        
    def create_footer(self):
        """Create footer section (now empty/minimal)"""
        footer_frame = QFrame()
        footer_frame.setObjectName("sidebarFooter")
        footer_frame.setFixedHeight(20)  # Reduced height since no content
        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 5, 20, 5)
        
        # Empty footer or just spacing
        footer_layout.addStretch()
        
        self.main_layout.addWidget(footer_frame)
        
    def add_menu_section(self, title):
        """Add a section header"""
        if not self.is_collapsed:
            section_label = QLabel(title)
            section_label.setObjectName("sectionHeader")
            self.menu_layout.addWidget(section_label)
            
        # Add some spacing
        self.menu_layout.addSpacing(5)
        
    def add_menu_item(self, text, icon="", callback=None):
        """Add a menu item to sidebar"""
        btn = SidebarButton(text, icon)
        btn.setMinimumHeight(50)  # Increased from 45
        
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
        
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.setFixedWidth(self.collapsed_width)
            self.title_label.hide()
            # Update all buttons to collapsed mode
            for button in self.menu_buttons:
                button.set_collapsed(True)
            # Hide section headers
            for i in range(self.menu_layout.count()):
                item = self.menu_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'objectName') and widget.objectName() == "sectionHeader":
                        widget.hide()
        else:
            self.setFixedWidth(self.expanded_width)
            self.title_label.show()
            # Update all buttons to expanded mode
            for button in self.menu_buttons:
                button.set_collapsed(False)
            # Show section headers
            for i in range(self.menu_layout.count()):
                item = self.menu_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'objectName') and widget.objectName() == "sectionHeader":
                        widget.show()
                        
    def apply_styles(self):
        """Apply professional styling to sidebar with official colors"""
        self.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: none;
            }
            
            QFrame#sidebarHeader {
                background-color: rgba(30, 41, 59, 0.95);
                border-bottom: 1px solid #334155;
                border-radius: 0px;
            }
            
            QFrame#menuFrame {
                background: transparent;
            }
            
            QFrame#sidebarFooter {
                background-color: rgba(20, 25, 35, 0.8);
                border-top: 1px solid #334155;
                border-radius: 0px;
            }
            
            QLabel#sidebarTitle {
                color: #E2E8F0;
                font-weight: bold;
                font-size: 18px;
                padding: 8px 0px;
                margin: 0px;
            }
            
            QLabel#userInfo, QLabel#companyInfo {
                color: #E2E8F0;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 4px;
                border-radius: 4px;
                background-color: rgba(51, 65, 85, 0.6);
                margin: 2px 0px;
            }
            
            QPushButton#toggleButton {
                background-color: #3B82F6;
                border: 1px solid #0EA5E9;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#toggleButton:hover {
                background-color: #0EA5E9;
                border: 1px solid #3B82F6;
            }
            
            QPushButton#toggleButton:pressed {
                background-color: #1D4ED8;
            }
            
            QPushButton#sidebarButton {
                text-align: left;
                padding: 15px 18px;
                border: none;
                color: #F8FAFC;
                background: transparent;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                margin: 3px 6px;
                border-left: 3px solid transparent;
            }
            
            /* Collapsed sidebar buttons - center the icons */
            QPushButton#sidebarButton[collapsed="true"] {
                text-align: center;
                padding: 15px 5px;
                font-size: 18px;
            }
            
            QPushButton#sidebarButton:hover {
                background-color: #334155;
                color: #FFFFFF;
                border-left: 3px solid #0EA5E9;
            }
            
            QPushButton#sidebarButton[active="true"] {
                background-color: #3B82F6;
                color: #FFFFFF;
                font-weight: 600;
                border-left: 3px solid #0EA5E9;
            }
            
            QPushButton#sidebarButton:pressed {
                background-color: #1E40AF;
                color: white;
            }
        """)
