"""
Base dialog class with common functionality
All dialogs should inherit from this class
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QWidget, QTextEdit
)
from PySide6.QtCore import Qt

from theme import (
    PRIMARY, TEXT_PRIMARY, BORDER,
    get_section_title_font, get_link_font,
    get_section_frame_style, get_dialog_footer_style,
    get_cancel_button_style, get_save_button_style,
    get_link_label_style
)
from widgets import DialogFieldGroup, CustomButton
from ui.error_handler import UIErrorHandler
from core.logger import get_logger

logger = get_logger(__name__)


class BaseDialog(QDialog):
    """
    Base dialog class with dynamic sizing based on parent window.
    
    Features:
        - Dynamic sizing based on parent window
        - Common section creation methods
        - Collapsible section support
        - Form modification tracking
        - Save/Cancel button management
        - Keyboard shortcuts (Enter to save, Escape to cancel)
    
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
        
        # Form state tracking
        self._form_modified = False
        self._confirm_on_cancel = True  # Set to False to disable cancel confirmation
        
        # Button references (set by _build_footer)
        self.save_btn = None
        self.cancel_btn = None
        
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
    
    # === Common Section Creation Methods ===
    
    def _create_section(self, title: str, content_widget: QWidget) -> QFrame:
        """
        Create a styled section card with title and content.
        
        Args:
            title: Section title text
            content_widget: Widget containing section content
            
        Returns:
            QFrame: Styled section frame
        """
        section = QFrame()
        section.setObjectName("sectionFrame")
        section.setStyleSheet(get_section_frame_style())
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Section title
        title_label = QLabel(title)
        title_label.setFont(get_section_title_font())
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; background: transparent;")
        layout.addWidget(title_label)
        
        # Separator line
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background: {BORDER}; border: none;")
        layout.addWidget(separator)
        
        # Content
        layout.addWidget(content_widget)
        
        return section
    
    def _create_field_group(self, label_text: str, input_widget: QWidget) -> DialogFieldGroup:
        """
        Create a field group with label and input using DialogFieldGroup.
        
        Args:
            label_text: Label text (supports HTML for required asterisks)
            input_widget: Input widget
            
        Returns:
            DialogFieldGroup: Field group widget
        """
        return DialogFieldGroup(label_text, input_widget)
    
    def _create_collapsible_link(
        self,
        add_text: str,
        hide_text: str,
        scroll_layout: QVBoxLayout
    ) -> tuple:
        """
        Create a collapsible section link with show/hide functionality.
        
        Args:
            add_text: Text to show when section is collapsed (e.g., "Add Bank Details")
            hide_text: Text to show when section is expanded (e.g., "Hide Bank Details")
            scroll_layout: Layout to add the link to
            
        Returns:
            tuple: (link_label, toggle_function)
        """
        link_container = QWidget()
        link_container.setStyleSheet("background: transparent;")
        link_layout = QHBoxLayout(link_container)
        link_layout.setContentsMargins(0, 0, 0, 0)
        
        link_label = QLabel(f"➕ <a href='#' style='color: {PRIMARY}; text-decoration: none;'>{add_text}</a>")
        link_label.setTextFormat(Qt.RichText)
        link_label.setFont(get_link_font())
        link_label.setCursor(Qt.PointingHandCursor)
        link_label.setStyleSheet(get_link_label_style())
        link_layout.addWidget(link_label)
        link_layout.addStretch()
        
        scroll_layout.addWidget(link_container)
        
        # Store texts for toggle
        link_label._add_text = add_text
        link_label._hide_text = hide_text
        
        return link_label
    
    def _toggle_collapsible_section(self, section: QFrame, link_label: QLabel):
        """
        Toggle visibility of a collapsible section.
        
        Args:
            section: The section frame to show/hide
            link_label: The link label to update text
        """
        is_visible = section.isVisible()
        section.setVisible(not is_visible)
        
        add_text = getattr(link_label, '_add_text', 'Add Section')
        hide_text = getattr(link_label, '_hide_text', 'Hide Section')
        
        if is_visible:
            link_label.setText(f"➕ <a href='#' style='color: {PRIMARY}; text-decoration: none;'>{add_text}</a>")
        else:
            link_label.setText(f"➖ <a href='#' style='color: {PRIMARY}; text-decoration: none;'>{hide_text}</a>")
    
    # === Footer and Button Methods ===
    
    def _build_footer(
        self,
        save_text: str = "Save",
        cancel_text: str = "Cancel",
        save_callback=None,
        cancel_callback=None
    ) -> QFrame:
        """
        Build the footer with action buttons.
        
        Args:
            save_text: Text for save button
            cancel_text: Text for cancel button
            save_callback: Callback for save button (default: None, must be set)
            cancel_callback: Callback for cancel button (default: self.reject)
            
        Returns:
            QFrame: Footer frame with buttons
        """
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(get_dialog_footer_style())
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(40, 0, 40, 0)
        
        layout.addStretch()
        
        self.cancel_btn = CustomButton(cancel_text, "secondary")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedSize(120, 44)
        self.cancel_btn.setStyleSheet(get_cancel_button_style())
        self.cancel_btn.clicked.connect(cancel_callback or self.reject)
        layout.addWidget(self.cancel_btn)
        
        layout.addSpacing(12)
        
        self.save_btn = CustomButton(save_text, "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedSize(140, 44)
        self.save_btn.setStyleSheet(get_save_button_style())
        if save_callback:
            self.save_btn.clicked.connect(save_callback)
        layout.addWidget(self.save_btn)
        
        # Store original save text for restoration
        self._save_btn_text = save_text
        
        return footer
    
    def _set_saving_state(self, is_saving: bool):
        """
        Enable/disable buttons during save operation.
        
        Args:
            is_saving: True to show saving state, False to restore
        """
        if self.save_btn:
            self.save_btn.setEnabled(not is_saving)
            if is_saving:
                self.save_btn.setText("Saving...")
            else:
                self.save_btn.setText(getattr(self, '_save_btn_text', 'Save'))
        
        if self.cancel_btn:
            self.cancel_btn.setEnabled(not is_saving)
    
    def _mark_form_modified(self):
        """Mark the form as having unsaved changes."""
        self._form_modified = True
    
    def _show_loading(self, show: bool = True):
        """
        Show/hide loading cursor during operations.
        
        Args:
            show: True to show wait cursor, False to restore arrow cursor
        """
        from PySide6.QtWidgets import QApplication
        if show:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()
    
    # === Keyboard and Dialog Event Handlers ===
    
    def keyPressEvent(self, event):
        """
        Handle keyboard shortcuts: Enter to save, Escape to cancel.
        Override _on_save() in subclass to define save behavior.
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Don't save if focus is in TextEdit (allow newlines)
            if not isinstance(self.focusWidget(), QTextEdit):
                if hasattr(self, '_on_save'):
                    self._on_save()
                return
        elif event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)
    
    def reject(self):
        """
        Override reject to confirm if there are unsaved changes.
        Set self._confirm_on_cancel = False to disable this behavior.
        """
        if self._confirm_on_cancel and self._form_modified:
            if UIErrorHandler.ask_confirmation(
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to cancel?"
            ):
                super().reject()
        else:
            super().reject()
