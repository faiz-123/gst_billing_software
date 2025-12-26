from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QLabel
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
        self.search.textChanged.connect(self.filter)
        # Allow arrow key navigation from the search box
        self.search.installEventFilter(self)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

        # Select first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

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
        self.search.textChanged.connect(self.filter)
        # Allow arrow key navigation from the search box
        self.search.installEventFilter(self)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

        # Select first item by default if available
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

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
                self.selected_name = typed
        super().accept()
