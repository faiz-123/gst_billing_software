"""
Company Creation Screen for GST Billing Software
"""

import sys
import re
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QDateEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QMessageBox, QSizePolicy,
    QGroupBox, QSpacerItem
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from .base_screen import BaseScreen


class CompanyCreationScreen(QWidget):
    """Screen for creating a new company"""
    
    company_created = pyqtSignal(dict)  # Emits company data when saved
    cancelled = pyqtSignal()
    
    # Color constants
    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#3B82F6"
    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    BACKGROUND = "#F9FAFB"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    BORDER = "#E5E7EB"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Company")
        self.resize(1200, 900)
        self.logo_path = None
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("New Company Registration")
        title.setObjectName("lblTitle")
        layout.addWidget(title)

        # Top Grid (Company Details + License Information)
        top_grid = QHBoxLayout()

        # Company Details
        company_box = QGroupBox("Company Details")
        comp_layout = QVBoxLayout()
        self.company_name_input = self.add_field("Company Name", comp_layout)

        # Mobile and Email row
        row_mobile = QHBoxLayout()
        mobile_box = QVBoxLayout()
        email_box = QVBoxLayout()

        self.mobile_input = self.add_field("Mobile No", mobile_box, maxlength=10)
        self.email_input = self.add_field("Email", email_box)

        row_mobile.addLayout(mobile_box, 1)
        row_mobile.addLayout(email_box, 1)
        comp_layout.addLayout(row_mobile)
        
        # Tax Type and Website row
        row_tax = QHBoxLayout()
        tax_box = QVBoxLayout()
        website_box = QVBoxLayout()

        self.tax_type_input = self.add_field("Tax Type", tax_box)
        self.website_input = self.add_field("Website", website_box)

        row_tax.addLayout(tax_box, 1)
        row_tax.addLayout(website_box, 1)
        comp_layout.addLayout(row_tax)
        
        # Financial Year
        fy_label = QLabel("Financial Year")
        fy_label.setFont(QFont("Arial", 12, QFont.Bold))
        fy_row = QHBoxLayout()
        self.fy_start_input = QDateEdit()
        self.fy_start_input.setCalendarPopup(True)
        self.fy_start_input.setDate(QDate.currentDate())
        self.fy_end_input = QDateEdit()
        self.fy_end_input.setCalendarPopup(True)
        self.fy_end_input.setDate(QDate.currentDate())
        fy_row.addWidget(self.fy_start_input)
        fy_row.addWidget(self.fy_end_input)

        comp_layout.addWidget(fy_label)
        comp_layout.addLayout(fy_row)

        # Address
        self.address_input = QTextEdit()
        comp_layout.addWidget(QLabel("Address"))
        comp_layout.addWidget(self.address_input)

        company_box.setLayout(comp_layout)
        
        # License Information
        license_box = QGroupBox("License Information")
        lic_layout = QVBoxLayout()
        self.gst_number_input = self.add_field("GST Number", lic_layout)
        self.other_license_input = self.add_field("Other License Number", lic_layout)

        self.other_info_input = QTextEdit()
        lic_layout.addWidget(QLabel("Other Information"))
        lic_layout.addWidget(self.other_info_input)
        license_box.setLayout(lic_layout)

        top_grid.addWidget(company_box, 1)
        top_grid.addWidget(license_box, 1)
        layout.addLayout(top_grid)

        # Bank Details and Logo
        mid_grid = QHBoxLayout()

        # Bank Details
        bank_box = QGroupBox("Bank Details")
        bank_layout = QVBoxLayout()
        self.bank_name_input = self.add_field("Bank Name", bank_layout)
        self.account_name_input = self.add_field("Account Name", bank_layout)
        self.account_number_input = self.add_field("Account Number", bank_layout)
        self.ifsc_input = self.add_field("IFSC Code", bank_layout)
        bank_box.setLayout(bank_layout)

        # Logo Upload
        logo_box = QGroupBox("Logo (Upload File)")
        logo_layout_v = QVBoxLayout()
        logo_layout = QHBoxLayout()
        self.logo_preview = QLabel("Drop + Upload")
        self.logo_preview.setObjectName("lblLogoPreview")
        self.logo_preview.setFixedSize(300, 120)
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("btnBrowse")
        logo_layout.addWidget(self.logo_preview, alignment=Qt.AlignLeft)
        logo_layout.addWidget(self.browse_button, alignment=Qt.AlignLeft)
        logo_layout.addSpacing(4)
        logo_layout_v.addLayout(logo_layout)
        
        # Large Logo Preview
        self.logo_large = QLabel("Logo Preview")
        self.logo_large.setObjectName("lblLogoLarge")
        self.logo_large.setFixedHeight(150)
        logo_layout_v.addWidget(self.logo_large)
        logo_box.setLayout(logo_layout_v)
         
        mid_grid.addWidget(bank_box, 1)
        mid_grid.addWidget(logo_box, 1)
        layout.addLayout(mid_grid)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(40) 
        btn_row.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("btnCancel")
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("btnSave")
        btn_row.addWidget(self.cancel_button)
        btn_row.addWidget(self.save_button)
        layout.addLayout(btn_row)

    def setup_connections(self):
        """Set up signal connections"""
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.save_button.clicked.connect(self.handle_save)
        self.browse_button.clicked.connect(self.upload_logo)

    def add_field(self, label_text, layout, maxlength=None):
        """Add a labeled input field to a layout"""
        lbl = QLabel(label_text)
        lbl.setObjectName("inputLabel")
        line = QLineEdit()
        if maxlength:
            line.setMaxLength(maxlength)
        layout.addWidget(lbl)
        layout.addWidget(line)
        return line

    def upload_logo(self):
        """Handle logo upload"""
        fname, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if fname:
            pix = QPixmap(fname)
            self.logo_preview.setPixmap(pix.scaled(self.logo_preview.size(), Qt.KeepAspectRatio))
            self.logo_large.setPixmap(pix.scaled(self.logo_large.size(), Qt.KeepAspectRatio))
            self.logo_path = fname

    def validate_email(self, email):
        """Validate email format"""
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def validate_ifsc(self, ifsc):
        """Validate IFSC code format"""
        return re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc)

    def handle_cancel(self):
        """Handle cancel button click"""
        self.cancelled.emit()

    def handle_save(self):
        """Handle save button click"""
        data = {
            "company_name": self.company_name_input.text(),
            "address": self.address_input.toPlainText(),
            "mobile": self.mobile_input.text(),
            "email": self.email_input.text(),
            "website": self.website_input.text(),
            "tax_type": self.tax_type_input.text(),
            "fy_start": self.fy_start_input.date().toString("yyyy-MM-dd"),
            "fy_end": self.fy_end_input.date().toString("yyyy-MM-dd"),
            "gst": self.gst_number_input.text(),
            "other_license": self.other_license_input.text(),
            "other_info": self.other_info_input.toPlainText(),
            "bank_name": self.bank_name_input.text(),
            "account_name": self.account_name_input.text(),
            "account_number": self.account_number_input.text(),
            "ifsc": self.ifsc_input.text(),
            "logo": self.logo_path
        }

        # Validation
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

        # Emit the data
        self.company_created.emit(data)
        QMessageBox.information(self, "Success", "Company created successfully!")

    def reset_form(self):
        """Reset all form fields"""
        self.company_name_input.clear()
        self.address_input.clear()
        self.mobile_input.clear()
        self.email_input.clear()
        self.website_input.clear()
        self.tax_type_input.clear()
        self.fy_start_input.setDate(QDate.currentDate())
        self.fy_end_input.setDate(QDate.currentDate())
        self.gst_number_input.clear()
        self.other_license_input.clear()
        self.other_info_input.clear()
        self.bank_name_input.clear()
        self.account_name_input.clear()
        self.account_number_input.clear()
        self.ifsc_input.clear()
        self.logo_path = None
        self.logo_preview.clear()
        self.logo_preview.setText("Drop + Upload")
        self.logo_large.clear()
        self.logo_large.setText("Logo Preview")

    def apply_styles(self):
        """Apply CSS styles to the widget"""
        self.setStyleSheet(f"""
        QWidget {{
          background: {self.BACKGROUND};
          color: {self.TEXT_PRIMARY};
          font-family: "Arial";
          font-size: 13px;
        }}

        QGroupBox {{
          border: 2px solid {self.BORDER};
          border-radius: 20px;
          margin-top: 7px;
          font-weight: bold;
          padding: 8px;
        }}

        QGroupBox::title {{
          subcontrol-origin: margin;
          subcontrol-position: top center;
          padding: 0 6px;
          color: {self.TEXT_SECONDARY};
        }}

        QLineEdit, QTextEdit, QDateEdit {{
          border: 1px solid {self.BORDER};
          border-radius: 6px;
          padding: 6px;
          background: #FFFFFF;
          color: {self.TEXT_PRIMARY};
          height: 28px;
          font-size: 16px;
        }}
        QTextEdit {{
          min-height: 20px;
        }}

        QLabel#lblLogoPreview, QLabel#lblLogoLarge {{
          border: 2px dashed {self.BORDER};
          background: #FFFFFF;
          color: {self.TEXT_SECONDARY};
          border-radius: 8px;
          qproperty-alignment: AlignCenter;
        }}

        QPushButton#btnSave {{
          background-color: {self.PRIMARY};
          color: white;
          border-radius: 6px;
          font-weight: 600;
          padding: 15px 50px;
          font-size: 18px;
        }}
        QPushButton#btnSave:hover {{
          background-color: {self.PRIMARY_HOVER};
        }}

        QPushButton#btnCancel {{
          background-color: white;
          color: {self.TEXT_PRIMARY};
          border: 1px solid {self.BORDER};
          border-radius: 6px;
          padding: 15px 50px;
          font-size: 18px;
        }}

        QPushButton#btnCancel:hover {{
          background-color: {self.BACKGROUND};
        }}

        QPushButton#btnBrowse {{
          background-color: white;
          color: {self.TEXT_PRIMARY};
          border: 1px solid {self.BORDER};
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 20px;
        }}

        QLabel#lblTitle {{
          color: {self.TEXT_PRIMARY};
          font-weight: bold;
          font-size: 28px;
          margin-bottom: px;
        }}
        QLabel#inputLabel {{
          color: {self.TEXT_PRIMARY};
          font-weight: 500;
          margin-bottom: 4px;
        }}
        """)
