"""
STUB: Purchase Invoice Dialog
This is a placeholder stub created during refactoring.

DEPRECATED: This file depends on the old monolithic sales_invoice_form_dialog which has been removed.
TODO (PHASE 6): Refactor purchase invoices to use component-based architecture similar to sales invoices.

Status: The purchase_invoice_form_dialog.py file is broken after deleting the old sales dialog.
This stub allows the application to run while we plan the proper refactoring.
"""

from PySide6.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PurchaseInvoiceDialog(QDialog):
    """
    STUB: Purchase Invoice Dialog - Coming in PHASE 6 refactoring
    
    The previous version depended on the old monolithic sales_invoice_form_dialog.py which has been removed.
    This stub displays a message and allows graceful degradation.
    """
    
    def __init__(self, parent=None, invoice_data=None, invoice_number=None, read_only=False):
        super().__init__(parent)
        self.setWindowTitle("🛒 Purchase Invoice (Under Refactoring)")
        self.setModal(True)
        self.setMinimumSize(600, 300)
        
        # Create layout with deprecation message
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ Purchase Invoices - Under Refactoring")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "Purchase Invoice feature is being refactored to use the new component-based architecture.\n\n"
            "Expected in PHASE 6.\n\n"
            "For now, you can:\n"
            "• View existing purchase invoices in the list\n"
            "• Export/Print existing invoices\n\n"
            "Creating new purchase invoices will be available soon."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch()
        
        # OK button
        from widgets import CustomButton
        ok_btn = CustomButton("OK", "primary")
        ok_btn.clicked.connect(self.reject)
        layout.addWidget(ok_btn)
    
    def exec_(self):
        """Execute the dialog"""
        return self.exec()
