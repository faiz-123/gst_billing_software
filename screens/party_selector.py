from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt

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
        layout.addWidget(self.list)
        btns = QHBoxLayout()
        ok = QPushButton("Select")
        cancel = QPushButton("Cancel")
        btns.addStretch()
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.parties = [p.get('name','') for p in (parties or []) if p.get('name')]
        self.list.addItems(self.parties)
        self.search.textChanged.connect(self.filter)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())

    def filter(self, text):
        text = text.strip().lower()
        self.list.clear()
        for name in self.parties:
            if text in name.lower():
                self.list.addItem(name)

    def accept(self):
        item = self.list.currentItem()
        if item:
            self.selected_name = item.text()
        super().accept()
