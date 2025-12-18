# record_payment.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QFormLayout, QDateEdit, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"


class RecordPaymentScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Record Payment")
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_PRIMARY};")
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        # Title
        title = QLabel("Record Payment")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; padding: 2px 0px 2px 0px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)

        # Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)
        form_frame.setMinimumWidth(500)
        form_frame.setMinimumHeight(600)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(18)

        # Party
        party_col = QVBoxLayout()
        party_col.addWidget(self.label("Party *"))
        self.party_dropdown = QComboBox()
        self.party_dropdown.addItems(["Select party", "XYZ Enterprises", "John Doe", "Acme Corp", "Jane Smith"])
        self.party_dropdown.setStyleSheet(self.input_style())
        self.party_dropdown.setMinimumHeight(40)
        party_col.addWidget(self.party_dropdown)
        form_layout.addLayout(party_col)

        # Invoice
        invoice_col = QVBoxLayout()
        invoice_col.addWidget(self.label("Invoice"))
        self.invoice_dropdown = QComboBox()
        self.invoice_dropdown.addItems(["Select invoice", "Invoice #1001", "Invoice #1002", "Invoice #1003"])
        self.invoice_dropdown.setStyleSheet(self.input_style())
        self.invoice_dropdown.setMinimumHeight(40)
        invoice_col.addWidget(self.invoice_dropdown)
        form_layout.addLayout(invoice_col)

        # Date
        date_col = QVBoxLayout()
        date_col.addWidget(self.label("Date"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setStyleSheet(self.input_style())
        self.date_edit.setMinimumHeight(40)
        date_col.addWidget(self.date_edit)
        form_layout.addLayout(date_col)

        # Amount
        amount_col = QVBoxLayout()
        amount_col.addWidget(self.label("Amount"))
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("₹ 0")
        self.amount_edit.setStyleSheet(self.input_style())
        self.amount_edit.setMinimumHeight(40)
        amount_col.addWidget(self.amount_edit)
        form_layout.addLayout(amount_col)

        # Mode
        mode_col = QVBoxLayout()
        mode_col.addWidget(self.label("Mode"))
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Select mode", "Bank", "Cash", "UPI"])
        self.mode_dropdown.setStyleSheet(self.input_style())
        self.mode_dropdown.setMinimumHeight(40)
        mode_col.addWidget(self.mode_dropdown)
        form_layout.addLayout(mode_col)

        # Notes
        notes_col = QVBoxLayout()
        notes_col.addWidget(self.label("Notes"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add notes...")
        self.notes_edit.setStyleSheet(self.input_style(multiline=True))
        self.notes_edit.setMinimumHeight(60)
        notes_col.addWidget(self.notes_edit)
        form_layout.addLayout(notes_col)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        save_btn = QPushButton("Save Payment")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border-radius: 6px;
                padding: 10px 50px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 2px solid {BORDER};
                border-radius: 6px;
                padding: 10px 50px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {BORDER};
            }}
        """)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

    def label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 16))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold; border: none;")
        return lbl

    def input_style(self, multiline=False):
        if multiline:
            return f"""
                QTextEdit {{
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    padding: 6px;
                    font-size: 14px;
                }}
            """
        else:
            return f"""
                QLineEdit, QComboBox, QDateEdit {{
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    padding: 6px;
                    font-size: 14px;
                    background-color: white;
                }}
            """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecordPaymentScreen()
    window.show()
    sys.exit(app.exec_())
