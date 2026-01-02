from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QEvent


class PartySelector(QDialog):
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
                    
                    reply = msg_box.exec_()
                    
                    if reply == QMessageBox.Yes:
                        # Import and open PartyDialog
                        try:
                            from .party_dialog import PartyDialog
                            add_party_dialog = PartyDialog(self)
                            add_party_dialog.setWindowTitle(f"➕ Add New Party: {typed}")
                            
                            # Pre-fill the name field with the typed text
                            if hasattr(add_party_dialog, 'name_input'):
                                add_party_dialog.name_input.setText(typed)
                            
                            # Show the add party dialog
                            result = add_party_dialog.exec_()
                            
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
                                success_box.exec_()
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
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Product")
        self.setModal(True)
        self.selected_name = None

        layout = QVBoxLayout(self)
        # layout.addWidget(QLabel("Search"))
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
        self.search.textChanged.connect(self.force_upper_product)
        self.search.textChanged.connect(self.filter)
        # Allow arrow key navigation from the search box
        self.search.installEventFilter(self)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

        # Select first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def force_upper_product(self, text):
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
                    
                    reply = msg_box.exec_()
                    
                    if reply == QMessageBox.Yes:
                        # Import and open ProductDialog
                        try:
                            from .product_dialogue import ProductDialog
                            add_product_dialog = ProductDialog(self)
                            add_product_dialog.setWindowTitle(f"➕ Add New Product: {typed}")
                            
                            # Pre-fill the name field with the typed text
                            if hasattr(add_product_dialog, 'name_input'):
                                add_product_dialog.name_input.setText(typed)
                            
                            # Show the add product dialog
                            result = add_product_dialog.exec_()
                            
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
                                success_box.exec_()
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
