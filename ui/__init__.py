"""
UI module - Contains all user interface screens and dialogs
"""

# This module contains all the UI components organized by feature
# Import common components that might be used across the application

from .base.base_screen import BaseScreen
from .base.base_dialog import BaseDialog

__all__ = [
    'BaseScreen',
    'BaseDialog',
]
