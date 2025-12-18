"""
Base screen class with common functionality
All screens should inherit from this class
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import get_header_font, get_card_style, BACKGROUND, TEXT_PRIMARY, WHITE, BORDER, PRIMARY

class BaseScreen(QWidget):
    def __init__(self, title="Screen", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        """Setup basic UI structure"""
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setFont(get_header_font())
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        self.main_layout.addWidget(self.title_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        
        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet(get_card_style())
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(40, 20, 40, 20)
        self.content_layout.setSpacing(10)
        
        self.main_layout.addWidget(self.content_frame)
        
    def add_content(self, widget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)
        
    def add_content_layout(self, layout):
        """Add layout to content area"""
        self.content_layout.addLayout(layout)
        
    def set_title(self, title):
        """Update screen title"""
        self.title = title
        self.title_label.setText(title)
