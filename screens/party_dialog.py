"""Add/Edit Party Dialogs

Contains `PartyDialog` and `BankAccountDialog` used by Parties screen.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame,
    QDialog, QMessageBox, QLineEdit, QComboBox, QTextEdit, QCheckBox, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
import re

from theme import PRIMARY, WHITE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY
from database import db


class PartyDialog(QDialog):
    def __init__(self, parent=None, party_data=None):
        super().__init__(parent)
        self.party_data = party_data or {}
        self.result_data = None
        self.setWindowTitle("Add Party" if not party_data else "Edit Party")
        self.setModal(True)
        self.setMinimumSize(1200, 800)

        # try to size/center relative to parent
        try:
            if parent is not None:
                container = getattr(parent, 'content_frame', parent)
                pw = container.width() or container.size().width()
                ph = container.height() or container.size().height()
                target_w = max(600, int(pw * 0.9))
                target_h = max(480, int(ph * 0.9))
                self.resize(target_w, target_h)
                try:
                    top = parent.window() if hasattr(parent, 'window') else parent
                    px = top.x(); py = top.y(); pw_total = top.width(); ph_total = top.height()
                    dx = px + max(0, (pw_total - self.width()) // 2)
                    dy = py + max(0, (ph_total - self.height()) // 2)
                    self.move(dx, dy)
                except Exception:
                    pass
        except Exception:
            pass

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        # title = QLabel("Add Party" if not self.party_data else "Edit Party")
        # title.setFont(QFont("Arial", 24, QFont.Bold))
        # title.setStyleSheet(f"color: {TEXT_PRIMARY}; padding-bottom: 6px;")
        # main_layout.addWidget(title, alignment=Qt.AlignLeft)

        form_frame = QFrame()
        form_frame.setStyleSheet(f"background: {WHITE}; border: 1px solid {BORDER}; border-radius: 12px;")
        form_layout = QGridLayout(form_frame)

        def create_label(text):
            lbl = QLabel(text)
            # Normal weight, grey color for field labels
            lbl.setFont(QFont("Arial", 14, QFont.Normal))
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none;")
            # Add red * for mandatory Party Name
            if text.strip().lower() == "party name":
                lbl.setText("Party Name <span style='color:#DC2626'>*</span>")
                lbl.setTextFormat(Qt.RichText)
            # Add red * for mandatory Party Type
            if text.strip().lower() == "party type":
                lbl.setText("Party Type <span style='color:#DC2626'>*</span>")
                lbl.setTextFormat(Qt.RichText)
            return lbl

        # Base style reused to reset inputs after error state
        default_input_style = f"border: 1px solid {BORDER}; border-radius: 6px; padding: 10px; color: {TEXT_PRIMARY}; background: {WHITE}; font-size: 14px;"

        def create_input(value="", placeholder=""):
            e = QLineEdit(value)
            e.setStyleSheet(default_input_style)
            e.setMinimumHeight(40)
            if placeholder:
                e.setPlaceholderText(placeholder)
            return e

        # Store for use in validation reset
        self._input_base_style = default_input_style

        # General Details (rows 0, 2, 4 combined)
        general_frame = QFrame()
        general_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        general_layout = QVBoxLayout(general_frame)
        general_layout.setContentsMargins(12, 12, 12, 12)
        general_layout.setSpacing(10)
        general_title = QLabel("General Details")
        general_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none;")
        general_layout.addWidget(general_title)

        # Grid for fields inside General Details
        general_grid = QGridLayout()
        general_grid.setHorizontalSpacing(12)
        general_grid.setVerticalSpacing(15)

        # Name, Mobile, Email
        self.name_input = create_input(self.party_data.get('name', ''), "Enter party name")
        # Force uppercase in Party Name QLineEdit
        def force_upper(text):
            if text != text.upper():
                cursor_pos = self.name_input.cursorPosition()
                self.name_input.setText(text.upper())
                self.name_input.setCursorPosition(cursor_pos)
        self.name_input.textChanged.connect(force_upper)
        # Clear error highlight as soon as user types
        try:
            self.name_input.textChanged.connect(self._clear_name_error)
        except Exception:
            pass
        self.phone_input = create_input(self.party_data.get('phone', ''), "Enter mobile number")
        self.email_input = create_input(self.party_data.get('email', ''), "Enter email address")
        general_grid.addWidget(create_label("Party Name"), 0, 0)
        general_grid.addWidget(create_label("Mobile Number"), 0, 1)
        general_grid.addWidget(create_label("Email"), 0, 2)
        general_grid.addWidget(self.name_input, 1, 0)
        general_grid.addWidget(self.phone_input, 1, 1)
        general_grid.addWidget(self.email_input, 1, 2)

        # GSTIN, PAN, Party Type
        self.gst_number_input = create_input(self.party_data.get('gstin', self.party_data.get('gst_number', '')), "Enter GSTIN")
        self.pan_input = create_input(self.party_data.get('pan', ''), "Enter PAN number")
        self.type_combo = QComboBox(); self.type_combo.addItems(["", "Customer", "Supplier", "Both"])
        # Default to Customer on new party
        try:
            idx = self.type_combo.findText("Customer")
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        except Exception:
            pass
        general_grid.addWidget(create_label("GSTIN"), 2, 0)
        general_grid.addWidget(create_label("PAN Number"), 2, 1)
        general_grid.addWidget(create_label("Party Type"), 2, 2)
        general_grid.addWidget(self.gst_number_input, 3, 0)
        general_grid.addWidget(self.pan_input, 3, 1)
        general_grid.addWidget(self.type_combo, 3, 2)

        # Opening Balance, Balance Type
        self.opening_balance = create_input(str(self.party_data.get('opening_balance', '0.00')), "Enter opening balance")
        self.balance_type = QComboBox(); self.balance_type.addItems(["Receivable (Dr)", "Payable (Cr)"])
        general_grid.addWidget(create_label("Opening Balance"), 4, 0)
        general_grid.addWidget(create_label("Balance Type"), 4, 1)
        general_grid.addWidget(self.opening_balance, 5, 0)
        general_grid.addWidget(self.balance_type, 5, 1)

        general_layout.addLayout(general_grid)
        form_layout.addWidget(general_frame, 0, 0, 1, 3)


        # Address + State/Pin (combined framed section)
        address_frame = QFrame()
        address_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        address_container = QVBoxLayout(address_frame)
        address_container.setContentsMargins(12, 12, 12, 12)
        address_container.setSpacing(10)
        address_title = QLabel("Address")
        address_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none;")
        address_container.addWidget(address_title)
        self.address_input = QTextEdit(self.party_data.get('address', ''))
        self.address_input.setMinimumHeight(40)
        self.address_input.setStyleSheet(f"QTextEdit {{ border: 1px solid {BORDER}; border-radius: 6px; padding: 8px; color: {TEXT_PRIMARY}; background: {WHITE}; }}")
        address_container.addWidget(self.address_input)
        # Inline grid for State/City/Pin under Address
        location_grid = QGridLayout()
        location_grid.setHorizontalSpacing(12)
        location_grid.setVerticalSpacing(8)
        self.city_input = create_input(self.party_data.get('city', ''), "Enter city")
        self.state_input = create_input(self.party_data.get('state', ''), "Enter state")
        self.pincode_input = create_input(self.party_data.get('pincode', ''), "Enter pin code")
        location_grid.addWidget(create_label("City"), 0, 0)
        location_grid.addWidget(create_label("State"), 0, 1)
        location_grid.addWidget(create_label("Pin Code"), 0, 2)
        location_grid.addWidget(self.city_input, 1, 0)
        location_grid.addWidget(self.state_input, 1, 1)
        location_grid.addWidget(self.pincode_input, 1, 2)
        address_container.addLayout(location_grid)
        form_layout.addWidget(address_frame, 1, 0, 1, 3)

        # (Removed separate State/Pin frame; combined above with Address)

        # Bank panel (framed)
        bank_panel = QFrame()
        bank_panel.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        bank_panel.setMinimumHeight(180)
        bank_layout = QVBoxLayout(bank_panel)
        bank_layout.setContentsMargins(12, 12, 12, 12)
        bank_layout.setSpacing(6)
        bank_title = QLabel("Party Bank Account")
        bank_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none;")
        bank_layout.addWidget(bank_title)
        bank_hint = QLabel("Add party bank information to manage transactions")
        bank_hint.setAlignment(Qt.AlignCenter)
        bank_hint.setStyleSheet(f"color: {TEXT_SECONDARY}; border: none; padding: 8px 0;")
        bank_layout.addWidget(bank_hint)
        bank_link_inline = QLabel("<a href='bank'>+ Add Bank Account</a>")
        bank_link_inline.setAlignment(Qt.AlignCenter)
        bank_link_inline.setTextInteractionFlags(Qt.TextBrowserInteraction)
        bank_link_inline.setOpenExternalLinks(False)
        bank_link_inline.linkActivated.connect(self.open_bank_details)
        bank_link_inline.setStyleSheet(f"color: {PRIMARY}; font-weight: 600; border: none;")
        bank_layout.addWidget(bank_link_inline)
        form_layout.addWidget(bank_panel, 2, 0, 1, 3)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setMinimumWidth(140)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save_party)
        save_btn.setStyleSheet(f"background: {PRIMARY}; color: white; padding: 10px 24px; border-radius: 8px;")
        cancel_btn.setStyleSheet(f"background: {WHITE}; color: {TEXT_PRIMARY}; padding: 10px 22px; border: 1px solid {BORDER}; border-radius: 8px;")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        form_layout.addLayout(btn_row, 3, 0, 1, 3)

        main_layout.addWidget(form_frame)
        try:
            QShortcut(QKeySequence('Return'), self, activated=self.save_party)
            QShortcut(QKeySequence('Enter'), self, activated=self.save_party)
            QShortcut(QKeySequence('Escape'), self, activated=self.reject)
        except Exception:
            pass
        if self.party_data:
            self.populate_form()

    def populate_form(self):
        d = self.party_data or {}
        self.name_input.setText(d.get('name', ''))
        self.phone_input.setText(d.get('phone', ''))
        self.email_input.setText(d.get('email', ''))
        self.address_input.setPlainText(d.get('address', ''))
        self.gst_number_input.setText(d.get('gst_number', d.get('gstin', d.get('gstin_number', ''))))
        self.pan_input.setText(d.get('pan', ''))
        type_index = self.type_combo.findText(d.get('type', 'Customer'))
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        self.opening_balance.setText(str(d.get('opening_balance', 0)))
        bal = 'Receivable (Dr)' if d.get('balance_type', 'dr') == 'dr' else 'Payable (Cr)'
        bi = self.balance_type.findText(bal)
        if bi >= 0:
            self.balance_type.setCurrentIndex(bi)
        self.state_input.setText(d.get('state', ''))
        self.city_input.setText(d.get('city', ''))

    def save_party(self):
        name = self.name_input.text().strip()
        # Check for duplicate party name (case-insensitive)
        if hasattr(db, 'get_parties'):
            existing_parties = db.get_parties()
            for p in existing_parties:
                if p.get('name', '').strip().upper() == name.upper():
                    QMessageBox.warning(self, "Duplicate Name", f"A party with the name '{name}' already exists.")
                    self.name_input.setFocus()
                    return
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        gst = self.gst_number_input.text().strip()
        pan = self.pan_input.text().strip()
        address = self.address_input.toPlainText().strip()
        state = self.state_input.text().strip()
        city = self.city_input.text().strip()

        if not name:
            # Highlight name input instead of showing a message box
            self.name_input.setStyleSheet(
                f"border: 1px solid #DC2626; border-radius: 6px; padding: 10px; "
                f"color: {TEXT_PRIMARY}; background: #FEE2E2; font-size: 14px;"
            )
            self.name_input.setFocus()
            return
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            QMessageBox.warning(self, "Validation", "Please enter a valid email address"); return
        try:
            opening = float(self.opening_balance.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Validation", "Opening balance must be a number"); return

        party = {
            'name': name,
            'phone': phone,
            'email': email,
            'gst_number': gst,
            'pan': pan,
            'address': address,
            'state': state,
            'city': city,
            'opening_balance': opening,
            'balance_type': 'dr' if 'Receivable' in self.balance_type.currentText() else 'cr',
            'is_gst_registered': 1 if gst else 0,
            'type': self.type_combo.currentText()
        }

        try:
            if hasattr(db, 'add_party'):
                try:
                    db.add_party(party)
                except TypeError:
                    try:
                        db.add_party(party['name'], party['phone'], party['email'], party['gst_number'], party['pan'], party['address'], None, party['type'])
                    except Exception:
                        print('Warning: db.add_party failed to persist party')
        except Exception as e:
            print(f"Warning: error while saving to db: {e}")

        self.result_data = party; self.accept()

    def _clear_name_error(self, *_):
        """Reset Party Name field style when user edits it."""
        try:
            self.name_input.setStyleSheet(self._input_base_style)
        except Exception:
            pass

    def open_bank_details(self):
        dlg = BankAccountDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            if self.result_data is None:
                self.result_data = {}
            self.result_data['bank_details'] = dlg.result_data


class BankAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bank Account")
        self.setModal(True)
        self.setMinimumSize(600, 420)
        self.result_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Add Bank Account"); title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(title)

        form = QGridLayout(); form.setHorizontalSpacing(16); form.setVerticalSpacing(12)

        def lbl(text):
            l = QLabel(text); l.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none;"); return l
        def inp(ph):
            e = QLineEdit(); e.setMinimumHeight(40); e.setPlaceholderText(ph)
            e.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 8px; padding: 10px; font-size: 14px;"); return e

        form.addWidget(lbl("Bank Account Number *"), 0, 0); self.acc_no = inp("ex: 123456789"); form.addWidget(self.acc_no, 1, 0)
        form.addWidget(lbl("Re-Enter Bank Account Number *"), 0, 1); self.acc_no_re = inp("ex: 123456789"); form.addWidget(self.acc_no_re, 1, 1)
        form.addWidget(lbl("IFSC Code"), 2, 0); self.ifsc = inp("ex: ICIC0001234"); form.addWidget(self.ifsc, 3, 0)
        form.addWidget(lbl("Bank & Branch Name"), 2, 1); self.bank_branch = inp("ex: ICICI Bank, Mumbai"); form.addWidget(self.bank_branch, 3, 1)
        form.addWidget(lbl("Account Holder’s Name"), 4, 0); self.holder = inp("ex: Babu Lal"); form.addWidget(self.holder, 5, 0)
        form.addWidget(lbl("UPI ID"), 4, 1); self.upi = inp("ex: babulal@upi"); form.addWidget(self.upi, 5, 1)

        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch(1)
        cancel = QPushButton("Cancel"); submit = QPushButton("Submit")
        cancel.clicked.connect(self.reject); submit.clicked.connect(self.submit)
        cancel.setStyleSheet(f"background: {WHITE}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER}; border-radius: 6px; padding: 8px 18px;")
        submit.setStyleSheet(f"background: {PRIMARY}; color: white; border-radius: 6px; padding: 8px 22px;")
        btns.addWidget(cancel); btns.addWidget(submit)
        layout.addLayout(btns)

    def submit(self):
        a1 = self.acc_no.text().strip(); a2 = self.acc_no_re.text().strip()
        if not a1 or a1 != a2:
            QMessageBox.warning(self, "Validation", "Account numbers must match and not be empty"); return
        self.result_data = {
            'account_number': a1,
            'ifsc': self.ifsc.text().strip(),
            'bank_branch': self.bank_branch.text().strip(),
            'account_holder': self.holder.text().strip(),
            'upi': self.upi.text().strip(),
        }
        self.accept()
