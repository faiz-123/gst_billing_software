import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
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

class AddPartyScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Party")
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        self.setMinimumSize(700,700)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 0, 40, 40)
        main_layout.setSpacing(5)

        # Title
        title = QLabel("Add Party")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 32px; padding: 2px px 2px 0px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)

        # Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)
        form_frame.setMinimumWidth(700)
        form_frame.setMinimumHeight(500)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(16)

        # Party Name
        lbl_party = QLabel("Party Name")
        lbl_party.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_party = QLineEdit()
        txt_party.setPlaceholderText("Enter Party Name")
        txt_party.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        form_layout.addWidget(lbl_party)
        form_layout.addWidget(txt_party)

        # Contact Number
        lbl_contact = QLabel("Contact Number")
        lbl_contact.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_contact = QLineEdit()
        txt_contact.setPlaceholderText("Enter Contact Number")
        txt_contact.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        form_layout.addWidget(lbl_contact)
        form_layout.addWidget(txt_contact)

        # GSTIN and PAN NO (side by side)
        row_gstin_pan = QHBoxLayout()
        row_gstin_pan.setSpacing(16)

        # GSTIN
        lbl_gstin = QLabel("GSTIN")
        lbl_gstin.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_gstin = QLineEdit()
        txt_gstin.setPlaceholderText("Enter GSTIN")
        txt_gstin.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        gstin_col = QVBoxLayout()
        gstin_col.setSpacing(2)
        gstin_col.addWidget(lbl_gstin)
        gstin_col.addWidget(txt_gstin)

        # PAN NO
        lbl_pan = QLabel("PAN NO")
        lbl_pan.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_pan = QLineEdit()
        txt_pan.setPlaceholderText("Enter PAN NO")
        txt_pan.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        pan_col = QVBoxLayout()
        pan_col.setSpacing(2)
        pan_col.addWidget(lbl_pan)
        pan_col.addWidget(txt_pan)

        row_gstin_pan.addLayout(gstin_col)
        row_gstin_pan.addSpacing(16)
        row_gstin_pan.addLayout(pan_col)
        form_layout.addLayout(row_gstin_pan)

        main_layout.addWidget(form_frame)
        
        # ...existing code...

        # Address and State (side by side)
        row_address_state = QHBoxLayout()
        row_address_state.setSpacing(16)

        # Address
        lbl_address = QLabel("Address")
        lbl_address.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_address = QLineEdit()
        txt_address.setPlaceholderText("Enter Address")
        txt_address.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        address_col = QVBoxLayout()
        address_col.setSpacing(2)
        address_col.addWidget(lbl_address)
        address_col.addWidget(txt_address)

        # State
        lbl_state = QLabel("State")
        lbl_state.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_state = QLineEdit()
        txt_state.setPlaceholderText("Enter State")
        txt_state.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        state_col = QVBoxLayout()
        state_col.setSpacing(2)
        state_col.addWidget(lbl_state)
        state_col.addWidget(txt_state)

        row_address_state.addLayout(address_col)
        row_address_state.addSpacing(16)
        row_address_state.addLayout(state_col)
        form_layout.addLayout(row_address_state)


        # Party Type and Credit Limit (side by side)
        row_party_credit = QHBoxLayout()
        row_party_credit.setSpacing(16)

        # Party Type
        lbl_party_type = QLabel("Party Type")
        lbl_party_type.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_party_type = QLineEdit()
        txt_party_type.setPlaceholderText("Enter Party Type")
        txt_party_type.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        party_type_col = QVBoxLayout()
        party_type_col.setSpacing(2)
        party_type_col.addWidget(lbl_party_type)
        party_type_col.addWidget(txt_party_type)

        # Credit Limit Rs.
        lbl_credit = QLabel("Credit Limit Rs.")
        lbl_credit.setStyleSheet(f"color: {TEXT_PRIMARY};  border: none; font-size: 16px; font-weight: bold;")
        txt_credit = QLineEdit()
        txt_credit.setPlaceholderText("Enter Credit Limit")
        txt_credit.setStyleSheet(f"""
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 12px;
            background: white;
            color: {TEXT_PRIMARY};
            font-size: 16px;
            min-height: 16px;
        """)
        credit_col = QVBoxLayout()
        credit_col.setSpacing(2)
        credit_col.addWidget(lbl_credit)
        credit_col.addWidget(txt_credit)

        row_party_credit.addLayout(party_type_col)
        row_party_credit.addSpacing(16)
        row_party_credit.addLayout(credit_col)
        form_layout.addLayout(row_party_credit)

        # Buttons (outside form, at the bottom)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        save_btn = QPushButton("Save")
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

        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        main_layout.addLayout(btn_row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddPartyScreen()
    window.show()
    sys.exit(app.exec_())