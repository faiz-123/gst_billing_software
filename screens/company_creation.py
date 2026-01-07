"""
Company Creation Screen for GST Billing Software
"""

import sys
import re
from typing import Optional, Dict, Any
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
    WHITE = "#FFFFFF"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    BORDER = "#E5E7EB"
    
    # Form validation constants
    MOBILE_LENGTH = 10
    IFSC_PATTERN = r"^[A-Z]{4}0[A-Z0-9]{6}$"
    EMAIL_PATTERN = r"[^@]+@[^@]+\.[^@]+"
    SUPPORTED_IMAGE_FORMATS = "Images (*.png *.jpg *.jpeg *.bmp *.gif)"

    # UI Constants
    LOGO_PREVIEW_SIZE = (300, 120)
    LOGO_LARGE_SIZE = 150
    DEFAULT_WINDOW_SIZE = (1200, 900)
    MIN_WINDOW_SIZE = (800, 600)

    # Signals
    company_saved = pyqtSignal(dict)  # Emitted when company data is saved successfully

    
    def __init__(self, parent=None, company_data=None):
        super().__init__(parent)
        self.company_data = company_data  # If provided, we're in edit mode
        self.is_edit_mode = company_data is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("Edit Company")
        else:
            self.setWindowTitle("New Company")
            
        self.resize(1200, 900)
        self.logo_path = None
        self._setup_ui()
        self.setup_connections()
        self.apply_styles()
        
        # If editing, populate the form with existing data
        if self.is_edit_mode:
            self._populate_form_for_edit()


    def _setup_ui(self) -> None:
        """Set up the main user interface."""
        self.setWindowTitle("GST Billing Software")
        # self.setMinimumSize(*self.MIN_WINDOW_SIZE)
        # self.resize(*self.DEFAULT_WINDOW_SIZE)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        if self.is_edit_mode:
            title_label = QLabel("Edit Company Details")
        else:
            title_label = QLabel("New Company Registration")
        title_label.setObjectName("lblTitle")
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Create form sections
        self._create_company_details_section(main_layout)
        self._create_bank_and_logo_section(main_layout)
        self._create_action_buttons(main_layout)
    
    def _create_company_details_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the company details and license information section."""
        # Top section with company details and license info
        top_section = QHBoxLayout()
        top_section.setSpacing(10)
        
        # Company Details Group
        company_group = self._create_company_group()
        license_group = self._create_license_group()
        
        top_section.addWidget(company_group, 1)
        top_section.addWidget(license_group, 1)
        parent_layout.addLayout(top_section)
    
    def _create_company_group(self) -> QGroupBox:
        """Create the company details group box."""
        company_box = QGroupBox("Company Details")
        layout = QVBoxLayout(company_box)
        layout.setSpacing(12)
        
        # Company name (required)
        self.le_company_name = self._add_field("Company Name *", layout)
        
        # Contact information row
        contact_row = QHBoxLayout()
        mobile_layout = QVBoxLayout()
        email_layout = QVBoxLayout()
        
        self.le_mobile = self._add_field("Mobile Number", mobile_layout, max_length=self.MOBILE_LENGTH)
        self.le_email = self._add_field("Email Address", email_layout)
        
        contact_row.addLayout(mobile_layout, 1)
        contact_row.addLayout(email_layout, 1)
        layout.addLayout(contact_row)
        
        # Tax type and website row
        tax_row = QHBoxLayout()
        tax_layout = QVBoxLayout()
        website_layout = QVBoxLayout()
        
        self.le_tax_type = self._add_field("Tax Type", tax_layout)
        self.le_website = self._add_field("Website", website_layout)
        
        tax_row.addLayout(tax_layout, 1)
        tax_row.addLayout(website_layout, 1)
        layout.addLayout(tax_row)
        
        # Financial Year section
        self._add_financial_year_section(layout)
        
        
        return company_box
    
    def _create_license_group(self) -> QGroupBox:
        """Create the license information group box."""
        license_box = QGroupBox("License Information")
        layout = QVBoxLayout(license_box)
        layout.setSpacing(12)
        
        self.le_gst_number = self._add_field("GST Number", layout)
        self.le_other_license = self._add_field("Other License Number", layout)
        self.te_address = self._add_text_field("Company Address", layout)
        # self.te_other_info = self._add_text_field("Additional Information", layout)
        
        return license_box
    
    def _create_bank_and_logo_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the bank details and logo upload section."""
        middle_section = QHBoxLayout()
        middle_section.setSpacing(20)
        
        # Bank Details Group
        bank_group = self._create_bank_group()
        logo_group = self._create_logo_group()
        
        middle_section.addWidget(bank_group, 1)
        middle_section.addWidget(logo_group, 1)
        parent_layout.addLayout(middle_section)
    
    def _create_bank_group(self) -> QGroupBox:
        """Create the bank details group box."""
        bank_box = QGroupBox("Bank Details")
        layout = QVBoxLayout(bank_box)
        layout.setSpacing(12)
        
        self.le_bank_name = self._add_field("Bank Name", layout)
        self.le_account_name = self._add_field("Account Holder Name", layout)
        self.le_account_number = self._add_field("Account Number", layout)
        self.le_ifsc = self._add_field("IFSC Code", layout)
        
        return bank_box
    
    def _create_logo_group(self) -> QGroupBox:
        """Create the logo upload group box."""
        logo_box = QGroupBox("Company Logo")
        layout = QVBoxLayout(logo_box)
        layout.setSpacing(12)
        
        # Logo upload section
        upload_layout = QHBoxLayout()
        
        self.lbl_logo_preview = QLabel("Click 'Browse' to upload logo")
        self.lbl_logo_preview.setObjectName("lblLogoPreview")
        self.lbl_logo_preview.setFixedSize(*self.LOGO_PREVIEW_SIZE)
        
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setObjectName("btnBrowse")
        
        upload_layout.addWidget(self.lbl_logo_preview)
        upload_layout.addWidget(self.btn_browse, alignment=Qt.AlignTop)
        layout.addLayout(upload_layout)
        
        # Large logo preview
        self.lbl_logo_large = QLabel("Logo Preview")
        self.lbl_logo_large.setObjectName("lblLogoLarge")
        self.lbl_logo_large.setFixedHeight(self.LOGO_LARGE_SIZE)
        layout.addWidget(self.lbl_logo_large)
        
        return logo_box
    
    def _add_financial_year_section(self, layout: QVBoxLayout) -> None:
        """Add financial year date selection section."""
        fy_label = QLabel("Financial Year")
        fy_label.setObjectName("inputLabel")
        layout.addWidget(fy_label)
        fy_layout = QHBoxLayout()
        
        # Start date
        start_layout = QVBoxLayout()
        start_label = QLabel("Start Date")
        start_label.setObjectName("inputLabel")
        self.de_fy_start = QDateEdit()
        self.de_fy_start.setCalendarPopup(True)
        self.de_fy_start.setDate(QDate.currentDate())
        
        # Apply calendar styling
        from theme import get_calendar_stylesheet
        self.de_fy_start.setStyleSheet(get_calendar_stylesheet())
        
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.de_fy_start)
        
        # End date
        end_layout = QVBoxLayout()
        end_label = QLabel("End Date")
        end_label.setObjectName("inputLabel")
        self.de_fy_end = QDateEdit()
        self.de_fy_end.setCalendarPopup(True)
        # Set end date to one year from start date
        self.de_fy_end.setDate(QDate.currentDate().addYears(1))
        
        # Apply calendar styling
        self.de_fy_end.setStyleSheet(get_calendar_stylesheet())
        
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.de_fy_end)
        
        fy_layout.addLayout(start_layout)
        fy_layout.addLayout(end_layout)
        layout.addLayout(fy_layout)
    
    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Create the action buttons (Cancel/Save)."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Add spacer to push buttons to the right
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("btnCancel")
        
        self.btn_save = QPushButton("Save Company")
        self.btn_save.setObjectName("btnSave")
        
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_save)
        parent_layout.addLayout(button_layout)
    
    def _add_field(self, label_text: str, layout: QVBoxLayout, max_length: Optional[int] = None) -> QLineEdit:
        """
        Add a labeled input field to the layout.
        
        Args:
            label_text: Text for the field label
            layout: Layout to add the field to
            max_length: Maximum character length (optional)
            
        Returns:
            The created QLineEdit widget
        """
        label = QLabel(label_text)
        label.setObjectName("inputLabel")
        
        line_edit = QLineEdit()
        if max_length:
            line_edit.setMaxLength(max_length)
            
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return line_edit
    
    def _add_text_field(self, label_text: str, layout: QVBoxLayout) -> QTextEdit:
        """
        Add a labeled text area to the layout.
        
        Args:
            label_text: Text for the field label
            layout: Layout to add the field to
            
        Returns:
            The created QTextEdit widget
        """
        label = QLabel(label_text)
        label.setObjectName("inputLabel")
        
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(100)
        
        layout.addWidget(label)
        layout.addWidget(text_edit)
        return text_edit

    def setup_connections(self):
        """Set up signal connections"""        
        self.btn_browse.clicked.connect(self.upload_logo)
        self.btn_cancel.clicked.connect(self.handle_cancel)
        self.btn_save.clicked.connect(self.save_company_data)
        
        self.de_fy_start.dateChanged.connect(self.update_fy_end_date)
        
        # Connect all QLineEdit fields to force uppercase
        self.setup_uppercase_connections()
    
    def setup_uppercase_connections(self):
        """Set up connections to force uppercase text in all QLineEdit fields"""
        line_edit_fields = [
            self.le_company_name,
            self.le_mobile,
            self.le_email,
            self.le_tax_type,
            self.le_website,
            self.le_gst_number,
            self.le_other_license,
            self.le_bank_name,
            self.le_account_name,
            self.le_account_number,
            self.le_ifsc
        ]
        
        for field in line_edit_fields:
            field.textChanged.connect(lambda text, f=field: self.force_uppercase(f, text))
    
    def force_uppercase(self, line_edit, text):
        """Force text to uppercase in a QLineEdit field"""
        if text != text.upper():
            cursor_pos = line_edit.cursorPosition()
            line_edit.blockSignals(True)  # Prevent recursive calls
            line_edit.setText(text.upper())
            line_edit.setCursorPosition(cursor_pos)
            line_edit.blockSignals(False)

    def update_fy_end_date(self, start_date: QDate) -> None:
        """
        Automatically update the financial year end date when start date changes.
        
        Args:
            start_date: The selected start date
        """
        # Set end date to one year minus one day from start date
        end_date = start_date.addYears(1).addDays(-1)
        self.de_fy_end.setDate(end_date)

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

    def validate_mobile(self, mobile: str) -> bool:
        """
        Validate mobile number format.
        
        Args:
            mobile: Mobile number to validate
            
        Returns:
            True if mobile is valid, False otherwise
        """
        if not mobile:
            return True  # Empty mobile is allowed
        return mobile.isdigit() and len(mobile) == self.MOBILE_LENGTH

    def handle_cancel(self):
        """Handle cancel button click"""
        self.cancelled.emit()

    def collect_form_data(self) -> Dict[str, Any]:
        """
        Collect all form data into a dictionary.
        
        Returns:
            Dictionary containing all form data
        """
        return {
            "company_name": self.le_company_name.text().strip(),
            "address": self.te_address.toPlainText().strip(),
            "mobile": self.le_mobile.text().strip(),
            "email": self.le_email.text().strip(),
            "website": self.le_website.text().strip(),
            "tax_type": self.le_tax_type.text().strip(),
            "fy_start": self.de_fy_start.date().toString("yyyy-MM-dd"),
            "fy_end": self.de_fy_end.date().toString("yyyy-MM-dd"),
            "gst_number": self.le_gst_number.text().strip(),
            "other_license": self.le_other_license.text().strip(),
            "bank_name": self.le_bank_name.text().strip(),
            "account_name": self.le_account_name.text().strip(),
            "account_number": self.le_account_number.text().strip(),
            "ifsc_code": self.le_ifsc.text().strip().upper(),
            "logo_path": self.logo_path
        }

    def validate_form_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate all form data.
        
        Args:
            data: Form data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields validation
        if not data["company_name"]:
            return False, "Company Name is required."
        
        # Mobile number validation
        if data["mobile"] and not self.validate_mobile(data["mobile"]):
            return False, "Mobile number must be exactly 10 digits."
        
        # Email validation
        if data["email"] and not self.validate_email(data["email"]):
            return False, "Please enter a valid email address."
        
        # IFSC validation
        if data["ifsc_code"] and not self.validate_ifsc(data["ifsc_code"]):
            return False, "Invalid IFSC Code format. Please check and try again."
        
        # Financial year validation
        fy_start = self.de_fy_start.date()
        fy_end = self.de_fy_end.date()
        if fy_start >= fy_end:
            return False, "Financial year end date must be after start date."
        
        return True, ""
    
    def save_company_data(self) -> None:
        """Save the company data after validation."""
        try:
            # Collect form data
            data = self.collect_form_data()
            
            # Validate data
            is_valid, error_message = self.validate_form_data(data)
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error_message)
                return
            
            # Import database here to avoid circular imports
            from database import db
            
            if self.is_edit_mode:
                # Update existing company
                company_id = self.company_data['id']
                db.update_company(
                    company_id,
                    data['company_name'],
                    data.get('gst_number'),
                    data.get('mobile'),
                    data.get('email'),
                    data.get('address'),
                    data.get('website'),
                    data.get('tax_type'),
                    data.get('fy_start'),
                    data.get('fy_end'),
                    data.get('other_license'),
                    data.get('bank_name'),
                    data.get('account_name'),
                    data.get('account_number'),
                    data.get('ifsc_code'),
                    data.get('logo_path')
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Company '{data['company_name']}' has been updated successfully!"
                )
            else:
                # Create new company
                db.add_company(
                    data['company_name'],
                    data.get('gst_number'),
                    data.get('mobile'),
                    data.get('email'),
                    data.get('address'),
                    data.get('website'),
                    data.get('tax_type'),
                    data.get('fy_start'),
                    data.get('fy_end'),
                    data.get('other_license'),
                    data.get('bank_name'),
                    data.get('account_name'),
                    data.get('account_number'),
                    data.get('ifsc_code'),
                    data.get('logo_path')
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Company '{data['company_name']}' has been registered successfully!"
                )
            
            # After user clicks OK on success message, emit signals for navigation
            if self.is_edit_mode:
                self.company_saved.emit(data)  # For edit mode, just emit saved signal
            else:
                self.company_created.emit(data)  # For create mode, emit created signal
            
            # The form will be reset when navigating back to company selection
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving company data:\n{str(e)}"
            )


    def reset_form(self) -> None:
        """Reset all form fields to their default values."""
        # Text fields
        for field in [self.le_company_name, self.le_mobile, self.le_email, self.le_website,
                     self.le_tax_type, self.le_gst_number, self.le_other_license,
                     self.le_bank_name, self.le_account_name, self.le_account_number, self.le_ifsc]:
            field.clear()
        
        # Text areas
        self.te_address.clear()
        # self.te_other_info.clear()
        
        # Date fields
        current_date = QDate.currentDate()
        self.de_fy_start.setDate(current_date)
        self.de_fy_end.setDate(current_date.addYears(1))
        
        # Logo
        self.logo_path = None
        self.lbl_logo_preview.clear()
        self.lbl_logo_preview.setText("Click 'Browse' to upload logo")
        self.lbl_logo_large.clear()
        self.lbl_logo_large.setText("Logo Preview")

    def apply_styles(self):
        """Apply CSS styles to the widget"""
        self.setStyleSheet(f"""
        QWidget {{
            background: {self.BACKGROUND};
            color: {self.TEXT_PRIMARY};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 14px;
        }}

        QGroupBox {{
            border: 2px solid {self.BORDER};
            border-radius: 12px;
            margin-top: 10px;
            font-weight: bold;
            padding: 12px;
            background: {self.WHITE};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            color: {self.TEXT_SECONDARY};
            font-size: 15px;
            font-weight: 600;
        }}

        QLineEdit, QTextEdit, QDateEdit {{
            border: 2px solid {self.BORDER};
            border-radius: 8px;
            padding: 10px;
            background: {self.WHITE};
            color: {self.TEXT_PRIMARY};
            min-height: 20px;
            font-size: 14px;
        }}

        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {{
            border-color: {self.PRIMARY};
            outline: none;
        }}

        QLineEdit:hover, QTextEdit:hover, QDateEdit:hover {{
            border-color: {self.PRIMARY_HOVER};
        }}

        QTextEdit {{
            min-height: 80px;
        }}

        QLabel#lblLogoPreview, QLabel#lblLogoLarge {{
            border: 2px dashed {self.BORDER};
            background: {self.WHITE};
            color: {self.TEXT_SECONDARY};
            border-radius: 8px;
            qproperty-alignment: AlignCenter;
            font-weight: 500;
        }}

        QPushButton#btnSave {{
            background-color: {self.PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 15px 30px;
            font-size: 16px;
            min-width: 120px;
        }}

        QPushButton#btnSave:hover {{
            background-color: {self.PRIMARY_HOVER};
        }}

        QPushButton#btnSave:pressed {{
            background-color: #1D4ED8;
        }}

        QPushButton#btnCancel {{
            background-color: {self.WHITE};
            color: {self.TEXT_PRIMARY};
            border: 2px solid {self.BORDER};
            border-radius: 8px;
            font-weight: 500;
            padding: 15px 30px;
            font-size: 16px;
            min-width: 120px;
        }}

        QPushButton#btnCancel:hover {{
            background-color: {self.BACKGROUND};
            border-color: {self.PRIMARY};
        }}

        QPushButton#btnBrowse {{
            background-color: {self.WHITE};
            color: {self.TEXT_PRIMARY};
            border: 2px solid {self.BORDER};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
        }}

        QPushButton#btnBrowse:hover {{
            background-color: {self.PRIMARY};
            color: white;
            border-color: {self.PRIMARY};
        }}

        QLabel#lblTitle {{
            color: {self.TEXT_PRIMARY};
            font-weight: bold;
            font-size: 28px;
            margin-bottom: 20px;
            background: transparent;
        }}

        QLabel#inputLabel {{
            color: {self.TEXT_PRIMARY};
            font-weight: 600;
            margin-bottom: 4px;
            font-size: 14px;
            background: {self.WHITE};
        }}
        """)

    def _populate_form_for_edit(self):
        """Populate the form with existing company data for editing."""
        if not self.company_data:
            return
            
        # Basic company details
        if 'name' in self.company_data:
            self.le_company_name.setText(self.company_data['name'])
        if 'mobile' in self.company_data and self.company_data['mobile']:
            self.le_mobile.setText(str(self.company_data['mobile']))
        if 'email' in self.company_data and self.company_data['email']:
            self.le_email.setText(self.company_data['email'])
        if 'address' in self.company_data and self.company_data['address']:
            self.te_address.setText(self.company_data['address'])
        if 'gstin' in self.company_data and self.company_data['gstin']:
            self.le_gst_number.setText(self.company_data['gstin'])

