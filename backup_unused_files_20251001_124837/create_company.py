import sys, re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QDateEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QMessageBox, QSizePolicy,
    QGroupBox, QSpacerItem
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDate

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"

APP_STYLESHEET = f"""
QWidget {{
  background: {BACKGROUND};
  color: {TEXT_PRIMARY};
  font-family: "Arial";
  font-size: 13px;
}}

QGroupBox {{
  border: 2px solid {BORDER};
  border-radius: 20px;
  margin-top: 7px;
  font-weight: bold;
  padding: 8px;
}}
QGroupBox::title {{
  subcontrol-origin: margin;
  subcontrol-position: top center;
  padding: 0 6px;
  color: {TEXT_SECONDARY};
}}

QLineEdit, QTextEdit, QDateEdit {{
  border: 1px solid {BORDER};
  border-radius: 6px;
  padding: 6px;
  background: #FFFFFF;
  color: {TEXT_PRIMARY};
  height: 28px;
  font-size: 16px;
}}
QTextEdit {{
  min-height: 20px;
}}

QLabel#lblLogoPreview, QLabel#lblLogoLarge {{
  border: 2px dashed {BORDER};
  background: #FFFFFF;
  color: {TEXT_SECONDARY};
  border-radius: 8px;
  qproperty-alignment: AlignCenter;
}}

QPushButton#btnSave {{
  background-color: {PRIMARY};
  color: white;
  border-radius: 6px;
  font-weight: 600;
  padding: 15px 50px;
  font-size: 18px;       /* Bigger text */
}}
QPushButton#btnSave:hover {{
  background-color: {PRIMARY_HOVER};
}}

QPushButton#btnCancel {{
  background-color: white;
  color: {TEXT_PRIMARY};
  border: 1px solid {BORDER};
  border-radius: 6px;
  padding: 15px 50px;
  font-size: 18px;       /* Bigger text */
}}

QPushButton#btnCancel:hover {{
  background-color: {BACKGROUND};
}}

QPushButton#btnBrowse {{
  background-color: white;
  color: {TEXT_PRIMARY};
  border: 1px solid {BORDER};
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 20px;
}}

QLabel#lblTitle {{
  color: {TEXT_PRIMARY};
  font-weight: bold;
  font-size: 24px;
  margin-bottom: 12px;
}}
QLabel#inputLabel {{
  color: {TEXT_PRIMARY};
  font-weight: 500;
  margin-bottom: 4px;
}}
"""


class CompanyForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Company")
        self.resize(1200, 900)
        self.logo_path = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("New Company")
        title.setObjectName("lblTitle")

        layout.addWidget(title)

        # ---- Top Grid (Company Details + Logo+FY) ----
        top_grid = QHBoxLayout()

        # Company Details
        company_box = QGroupBox("Company Details")
        comp_layout = QVBoxLayout()
        self.leCompanyName = self.add_field("Company Name", comp_layout)

        row_mobile = QHBoxLayout()
        mobile_box = QVBoxLayout()
        email_box = QVBoxLayout()

        self.leMobile = self.add_field("Mobile No", mobile_box, maxlength=10)
        self.leEmail = self.add_field("Email", email_box)

        row_mobile.addLayout(mobile_box, 1)
        row_mobile.addLayout(email_box, 1)
        comp_layout.addLayout(row_mobile)
        
        row_tax = QHBoxLayout()
        tax_box = QVBoxLayout()
        website_box = QVBoxLayout()

        self.leTaxType = self.add_field("Tax Type", tax_box)
        self.leEmail = self.add_field("Website", website_box)

        row_tax.addLayout(tax_box, 1)
        row_tax.addLayout(website_box, 1)
        comp_layout.addLayout(row_tax)
        
        fy_label = QLabel("Financial Year")
        fy_label.setFont(QFont("Arial", 12, QFont.Bold))
        fy_row = QHBoxLayout()
        self.deFYStart = QDateEdit()
        self.deFYStart.setCalendarPopup(True)
        self.deFYStart.setDate(QDate.currentDate())
        self.deFYEnd = QDateEdit()
        self.deFYEnd.setCalendarPopup(True)
        self.deFYEnd.setDate(QDate.currentDate())
        fy_row.addWidget(self.deFYStart)
        fy_row.addWidget(self.deFYEnd)

        comp_layout.addWidget(fy_label)
        comp_layout.addLayout(fy_row)

        self.teAddress = QTextEdit()
        comp_layout.addWidget(QLabel("Address"))
        comp_layout.addWidget(self.teAddress)


        company_box.setLayout(comp_layout)
        
        #  ---- License Information ----
        license_box = QGroupBox("License Information")
        lic_layout = QVBoxLayout()
        self.leGSTNumber = self.add_field("GST Number", lic_layout)
        self.leOtherLicense = self.add_field("Other License Number", lic_layout)

        
        self.ltInfo = QTextEdit()
        lic_layout.addWidget(QLabel("Other Information"))
        lic_layout.addWidget(self.ltInfo)
        license_box.setLayout(lic_layout)

        top_grid.addWidget(company_box, 1)
        top_grid.addWidget(license_box, 1)
        layout.addLayout(top_grid)


        # ---- Bank Details ----
        bank_box = QGroupBox("Bank Details")
        bank_layout = QVBoxLayout()
        self.leBankName = self.add_field("Bank Name", bank_layout)
        self.leAccountName = self.add_field("Account Name", bank_layout)
        self.leAccountNumber = self.add_field("Account Number", bank_layout)
        self.leIFSC = self.add_field("IFSC Code", bank_layout)
        bank_box.setLayout(bank_layout)

        # Logo + FY
        logo_box = QGroupBox("Logo (Upload File)")
        logo_layout_v = QVBoxLayout()
        logo_layout = QHBoxLayout()
        self.lblLogoPreview = QLabel("Drop + Upload")
        self.lblLogoPreview.setObjectName("lblLogoPreview")
        self.lblLogoPreview.setFixedSize(300, 120)
        self.btnBrowse = QPushButton("Browse")
        self.btnBrowse.setObjectName("btnBrowse")
        self.btnBrowse.clicked.connect(self.upload_logo)
        logo_layout.addWidget(self.lblLogoPreview, alignment=Qt.AlignLeft)
        logo_layout.addWidget(self.btnBrowse, alignment=Qt.AlignLeft)
        logo_layout.addSpacing(4)
        logo_layout_v.addLayout(logo_layout)
        
        # ---- Large Logo Preview ----
        self.lblLogoLarge = QLabel("Logo Preview")
        self.lblLogoLarge.setObjectName("lblLogoLarge")
        self.lblLogoLarge.setFixedHeight(150)
        logo_layout_v.addWidget(self.lblLogoLarge)
        logo_box.setLayout(logo_layout_v)
         
        mid_grid = QHBoxLayout()
        mid_grid.addWidget(bank_box, 1)
        mid_grid.addWidget(logo_box, 1)
        layout.addLayout(mid_grid)

        
        # layout.addWidget(logo_large_box)

        # ---- Buttons ----
        btn_row = QHBoxLayout()
        btn_row.setSpacing(40) 
        btn_row.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.close)
        self.btnSave = QPushButton("Save")
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self.save_data)
        btn_row.addWidget(self.btnCancel)
        btn_row.addWidget(self.btnSave)
        layout.addLayout(btn_row)

    def add_field(self, label_text, layout, maxlength=None):
        lbl = QLabel(label_text)
        lbl.setObjectName("inputLabel")
        line = QLineEdit()
        if maxlength:
            line.setMaxLength(maxlength)
        layout.addWidget(lbl)
        layout.addWidget(line)
        return line

    def upload_logo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            pix = QPixmap(fname)
            self.lblLogoPreview.setPixmap(pix.scaled(self.lblLogoPreview.size(), Qt.KeepAspectRatio))
            self.lblLogoLarge.setPixmap(pix.scaled(self.lblLogoLarge.size(), Qt.KeepAspectRatio))
            self.logo_path = fname

    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def validate_ifsc(self, ifsc):
        return re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc)

    def save_data(self):
        data = {
            "company_name": self.leCompanyName.text(),
            "address": self.teAddress.toPlainText(),
            "mobile": self.leMobile.text(),
            "email": self.leEmail.text(),
            "tax_type": self.leTaxType.text(),
            "fy_start": self.deFYStart.date().toString("yyyy-MM-dd"),
            "fy_end": self.deFYEnd.date().toString("yyyy-MM-dd"),
            "gst": self.leGSTNumber.text(),
            "other_license": self.leOtherLicense.text(),
            "bank_name": self.leBankName.text(),
            "account_name": self.leAccountName.text(),
            "account_number": self.leAccountNumber.text(),
            "ifsc": self.leIFSC.text(),
            "logo": self.logo_path
        }

        if not data["company_name"]:
            QMessageBox.warning(self, "Validation", "Company Name is required")
            return
        if data["mobile"] and (not data["mobile"].isdigit() or len(data["mobile"]) != 10):
            QMessageBox.warning(self, "Validation", "Mobile number must be 10 digits")
            return
        if data["email"] and not self.validate_email(data["email"]):
            QMessageBox.warning(self, "Validation", "Invalid Email")
            return
        if data["ifsc"] and not self.validate_ifsc(data["ifsc"]):
            QMessageBox.warning(self, "Validation", "Invalid IFSC Code")
            return

        QMessageBox.information(self, "Saved", "Company data saved successfully!")
        print("Saved:", data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = CompanyForm()
    window.showMaximized()
    sys.exit(app.exec_())
