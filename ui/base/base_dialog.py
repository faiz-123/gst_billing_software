"""
Base dialog class with common functionality
All dialogs should inherit from this class
"""

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt


class BaseDialog(QDialog):
    """
    Base dialog class with dynamic sizing based on parent window.
    
    Usage:
        class MyDialog(BaseDialog):
            def __init__(self, parent=None, data=None):
                super().__init__(
                    parent=parent,
                    title="Add Item" if not data else "Edit Item",
                    default_width=1300,
                    default_height=1000,
                    min_width=800,
                    min_height=600,
                    width_ratio=0.85,
                    height_ratio=0.9
                )
                self.data = data
                self.build_ui()
    """
    
    def __init__(
        self,
        parent=None,
        title: str = "Dialog",
        default_width: int = 1300,
        default_height: int = 1000,
        min_width: int = 800,
        min_height: int = 600,
        width_ratio: float = 0.85,
        height_ratio: float = 0.9
    ):
        """
        Initialize the base dialog with dynamic sizing.
        
        Args:
            parent: Parent widget
            title: Dialog window title
            default_width: Default width when no parent
            default_height: Default height when no parent
            min_width: Minimum dialog width
            min_height: Minimum dialog height
            width_ratio: Ratio of parent width (0.0 to 1.0)
            height_ratio: Ratio of parent height (0.0 to 1.0)
        """
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Dynamic sizing based on parent screen
        if parent:
            screen_rect = parent.geometry()
            width = min(default_width, int(screen_rect.width() * width_ratio))
            height = min(default_height, int(screen_rect.height() * height_ratio))
            self.resize(width, height)
        else:
            self.resize(default_width, default_height)
        
        self.setMinimumSize(min_width, min_height)
    
    def build_ui(self):
        """
        Build the dialog UI. Override this method in subclasses.
        """
        pass
