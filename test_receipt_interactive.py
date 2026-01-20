#!/usr/bin/env python3
"""Interactive test for down arrow key in receipt dialog."""

import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent

def test_interactive():
    """Test with visual feedback."""
    
    app = QApplication(sys.argv)
    
    from ui.receipts.receipt_form_dialog import ReceiptDialog
    
    # Create dialog
    dialog = ReceiptDialog()
    
    # Create a simple test window
    window = QWidget()
    window.setWindowTitle("Receipt Dialog - Down Arrow Key Test Instructions")
    layout = QVBoxLayout()
    
    instructions = QLabel(
        "<h3>Receipt Dialog Down Arrow Key Test</h3>"
        "<p><b>Instructions:</b></p>"
        "<ol>"
        "<li>Click in the 'Customer' search field</li>"
        "<li>Press the <b>Down Arrow</b> key (↓)</li>"
        "<li>Expected: A dropdown list should appear below the field</li>"
        "<li>You should see all available customers in the list</li>"
        "</ol>"
        "<p><b>Additional Features:</b></p>"
        "<ul>"
        "<li>Type to filter the customer list</li>"
        "<li>Press Up/Down arrows to navigate the list</li>"
        "<li>Press Enter to select a customer</li>"
        "<li>Press Escape to close the list</li>"
        "</ul>"
        "<p style='color: green; font-weight: bold;'>✓ Ready for testing!</p>"
    )
    instructions.setStyleSheet("padding: 20px; font-size: 14px;")
    layout.addWidget(instructions)
    
    window.setLayout(layout)
    window.resize(600, 500)
    window.show()
    
    # Show the receipt dialog
    dialog.show()
    
    # Auto-test after 2 seconds
    def auto_test():
        # Get line edit
        line_edit = dialog.party_search.lineEdit()
        line_edit.setFocus()
        app.processEvents()
        
        # Simulate down arrow key
        key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
        dialog.eventFilter(line_edit, key_event)
        
        app.processEvents()
        
        # Check if popup is visible
        popup = dialog.party_completer.popup()
        if popup and popup.isVisible():
            print("\n✓ SUCCESS: Down arrow key opened the completer popup!")
            print(f"✓ Popup shows {dialog.party_completer.completionModel().rowCount()} customers")
        else:
            print("\n✗ Popup not visible - checking alternative methods...")
    
    QTimer.singleShot(2000, auto_test)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_interactive()
