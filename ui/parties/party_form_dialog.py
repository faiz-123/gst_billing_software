"""
Party dialog module - Add/Edit Party (Customer/Supplier)
Follows the same style as product_form_dialog.py
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox,
    QScrollArea, QWidget, QGridLayout
)
from PySide6.QtCore import Qt

from theme import (
    # Colors
    PRIMARY, TEXT_PRIMARY, BORDER,
    # Fonts
    get_title_font, get_section_title_font, get_link_font,
    # Styles
    get_section_frame_style, get_dialog_footer_style,
    get_cancel_button_style, get_save_button_style,
    get_link_label_style, get_scroll_area_style
)
from widgets import (
    DialogInput, DialogComboBox, DialogTextEdit, DialogFieldGroup, CustomButton
)
from ui.base.base_dialog import BaseDialog
from core.enums import PartyType, BalanceType
from core.services.party_service import party_service
from core import to_upper


class PartyDialog(BaseDialog):
    """Dialog for adding/editing a party (customer/supplier)"""
    
    def __init__(self, parent=None, party_data=None):
        self.party_data = party_data
        self.result_data = None
        super().__init__(
            parent=parent,
            title="Add Party" if not party_data else "Edit Party",
            default_width=1300,
            default_height=1000,
            min_width=800,
            min_height=600
        )
        self.build_ui()
    
    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for the entire content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(get_scroll_area_style())
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(40, 30, 40, 30)
        self.scroll_layout.setSpacing(24)
        
        # Header
        title_text = "Edit Party" if self.party_data else "Add New Party"
        title = QLabel(title_text)
        title.setFont(get_title_font())
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        self.scroll_layout.addWidget(title)
        
        # === SECTION 1: General Details ===
        self.scroll_layout.addWidget(self._create_section("General Details", self._build_general_section()))
        
        # === SECTION 2: Address ===
        self.scroll_layout.addWidget(self._create_section("Address", self._build_address_section()))
        
        # === Bank Details Link ===
        self._build_bank_link()
        
        # === SECTION 3: Bank Details (hidden by default) ===
        self.bank_section = self._create_section("Bank Account Details", self._build_bank_section())
        self.bank_section.setVisible(False)
        self.scroll_layout.addWidget(self.bank_section)
        
        self.scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Footer with buttons
        main_layout.addWidget(self._build_footer())
        
        # Populate form if editing
        if self.party_data:
            self._populate_form()
    
    def _build_bank_link(self):
        """Create a hyperlink to show/hide bank details section"""
        link_container = QWidget()
        link_container.setStyleSheet("background: transparent;")
        link_layout = QHBoxLayout(link_container)
        link_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bank_link = QLabel("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Bank Account Details</a>".format(PRIMARY))
        self.bank_link.setTextFormat(Qt.RichText)
        self.bank_link.setFont(get_link_font())
        self.bank_link.setCursor(Qt.PointingHandCursor)
        self.bank_link.setStyleSheet(get_link_label_style())
        self.bank_link.mousePressEvent = self._toggle_bank_section
        link_layout.addWidget(self.bank_link)
        link_layout.addStretch()
        
        self.scroll_layout.addWidget(link_container)
    
    def _toggle_bank_section(self, event=None):
        """Show/hide bank details section"""
        is_visible = self.bank_section.isVisible()
        self.bank_section.setVisible(not is_visible)
        
        if is_visible:
            self.bank_link.setText("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Bank Account Details</a>".format(PRIMARY))
        else:
            self.bank_link.setText("➖ <a href='#' style='color: {0}; text-decoration: none;'>Hide Bank Account Details</a>".format(PRIMARY))
    
    def _create_section(self, title: str, content_widget: QWidget) -> QFrame:
        """Create a styled section card with title and content"""
        section = QFrame()
        section.setObjectName("sectionFrame")
        section.setStyleSheet(get_section_frame_style())
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Section title
        title_label = QLabel(title)
        title_label.setFont(get_section_title_font())
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; background: transparent;")
        layout.addWidget(title_label)
        
        # Separator line
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background: {BORDER}; border: none;")
        layout.addWidget(separator)
        
        # Content
        layout.addWidget(content_widget)
        
        return section
    
    def _build_general_section(self) -> QWidget:
        """Build the general details section with 3 columns"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Party Name, Mobile, Email
        layout.addWidget(self._create_field_group(
            "Party Name <span style='color:#d32f2f'>*</span>",
            self._create_name_input()
        ), 0, 0)
        
        layout.addWidget(self._create_field_group(
            "Mobile Number",
            self._create_phone_input()
        ), 0, 1)
        
        layout.addWidget(self._create_field_group(
            "Email",
            self._create_email_input()
        ), 0, 2)
        
        # Row 1: GSTIN, PAN, Party Type
        layout.addWidget(self._create_field_group(
            "GSTIN",
            self._create_gstin_input()
        ), 1, 0)
        
        layout.addWidget(self._create_field_group(
            "PAN Number",
            self._create_pan_input()
        ), 1, 1)
        
        layout.addWidget(self._create_field_group(
            "Party Type <span style='color:#d32f2f'>*</span>",
            self._create_type_combo()
        ), 1, 2)
        
        # Row 2: Opening Balance, Balance Type
        layout.addWidget(self._create_field_group(
            "Opening Balance",
            self._create_opening_balance_input()
        ), 2, 0)
        
        layout.addWidget(self._create_field_group(
            "Balance Type",
            self._create_balance_type_combo()
        ), 2, 1)
        
        # Empty placeholder for alignment
        empty_widget = QWidget()
        empty_widget.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(empty_widget, 2, 2)
        
        return widget
    
    def _build_address_section(self) -> QWidget:
        """Build the address section"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Address (spans all 3 columns)
        address_group = self._create_field_group(
            "Address",
            self._create_address_input()
        )
        layout.addWidget(address_group, 0, 0, 1, 3)
        
        # Row 1: City, State, Pin Code
        layout.addWidget(self._create_field_group(
            "City",
            self._create_city_input()
        ), 1, 0)
        
        layout.addWidget(self._create_field_group(
            "State",
            self._create_state_input()
        ), 1, 1)
        
        layout.addWidget(self._create_field_group(
            "Pin Code",
            self._create_pincode_input()
        ), 1, 2)
        
        return widget
    
    def _build_bank_section(self) -> QWidget:
        """Build the bank account details section"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Account Number, Re-enter Account Number, IFSC Code
        layout.addWidget(self._create_field_group(
            "Bank Account Number",
            self._create_account_number_input()
        ), 0, 0)
        
        layout.addWidget(self._create_field_group(
            "Re-Enter Account Number",
            self._create_account_number_confirm_input()
        ), 0, 1)
        
        layout.addWidget(self._create_field_group(
            "IFSC Code",
            self._create_ifsc_input()
        ), 0, 2)
        
        # Row 1: Bank & Branch, Account Holder Name, UPI ID
        layout.addWidget(self._create_field_group(
            "Bank & Branch Name",
            self._create_bank_branch_input()
        ), 1, 0)
        
        layout.addWidget(self._create_field_group(
            "Account Holder's Name",
            self._create_account_holder_input()
        ), 1, 1)
        
        layout.addWidget(self._create_field_group(
            "UPI ID",
            self._create_upi_input()
        ), 1, 2)
        
        return widget
    
    def _create_field_group(self, label_text: str, input_widget: QWidget) -> DialogFieldGroup:
        """Create a field group with label and input using DialogFieldGroup"""
        return DialogFieldGroup(label_text, input_widget)
    
    def _build_footer(self) -> QFrame:
        """Build the footer with action buttons"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(get_dialog_footer_style())
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(40, 0, 40, 0)
        
        layout.addStretch()
        
        cancel_btn = CustomButton("Cancel", "secondary")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(120, 44)
        cancel_btn.setStyleSheet(get_cancel_button_style())
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addSpacing(12)
        
        save_btn = CustomButton("Save Party", "primary")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(140, 44)
        save_btn.setStyleSheet(get_save_button_style())
        save_btn.clicked.connect(self._save_party)
        layout.addWidget(save_btn)
        
        return footer
    
    # === Input Field Creators ===
    
    def _create_name_input(self) -> DialogInput:
        self.name_input = DialogInput("Enter party name")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.textChanged.connect(self._clear_name_error)
        return self.name_input
    
    def _create_phone_input(self) -> DialogInput:
        self.phone_input = DialogInput("Enter mobile number")
        return self.phone_input
    
    def _create_email_input(self) -> DialogInput:
        self.email_input = DialogInput("Enter email address")
        return self.email_input
    
    def _create_gstin_input(self) -> DialogInput:
        self.gst_number_input = DialogInput("Enter GSTIN")
        return self.gst_number_input
    
    def _create_pan_input(self) -> DialogInput:
        self.pan_input = DialogInput("Enter PAN number")
        return self.pan_input
    
    def _create_type_combo(self) -> DialogComboBox:
        party_types = ["", PartyType.CUSTOMER.value, PartyType.SUPPLIER.value, PartyType.BOTH.value]
        self.type_combo = DialogComboBox(items=party_types)
        # Default to Customer on new party
        if not self.party_data:
            idx = self.type_combo.findText(PartyType.CUSTOMER.value)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        # Connect party type change to update default balance type
        self.type_combo.currentTextChanged.connect(self._on_party_type_changed)
        return self.type_combo
    
    def _create_opening_balance_input(self) -> DialogInput:
        self.opening_balance = DialogInput("Enter opening balance")
        self.opening_balance.setText("0.00")
        return self.opening_balance
    
    def _create_balance_type_combo(self) -> DialogComboBox:
        # Balance types: To Receive (dr) for customers, To Pay (cr) for suppliers
        balance_types = [
            ("To Receive (DR)", "dr"),
            ("To Pay (CR)", "cr")
        ]
        self.balance_type_combo = DialogComboBox(items=[bt[0] for bt in balance_types])
        # Store mapping for later use
        self._balance_type_map = {bt[0]: bt[1] for bt in balance_types}
        self._balance_type_reverse_map = {bt[1]: bt[0] for bt in balance_types}
        # Default to "To Receive" for customers
        return self.balance_type_combo
    
    def _on_party_type_changed(self, party_type: str):
        """Update default balance type based on party type"""
        if hasattr(self, 'balance_type_combo'):
            if party_type == PartyType.SUPPLIER.value:
                # Suppliers default to "To Pay" (cr)
                idx = self.balance_type_combo.findText("To Pay (CR)")
            else:
                # Customers default to "To Receive" (dr)
                idx = self.balance_type_combo.findText("To Receive (DR)")
            if idx >= 0:
                self.balance_type_combo.setCurrentIndex(idx)
    
    def _create_address_input(self) -> DialogTextEdit:
        self.address_input = DialogTextEdit("Enter address", 80)
        return self.address_input
    
    def _create_city_input(self) -> DialogInput:
        self.city_input = DialogInput("Enter city")
        return self.city_input
    
    def _create_state_input(self) -> DialogComboBox:
        # List of all Indian states and union territories
        indian_states = [
            "",  # Empty option for no selection
            # "Andaman and Nicobar Islands",
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chandigarh",
            "Chhattisgarh",
            # "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jammu and Kashmir",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Ladakh",
            "Lakshadweep",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Puducherry",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
        ]
        self.state_input = DialogComboBox(indian_states)
        return self.state_input
    
    def _create_pincode_input(self) -> DialogInput:
        self.pincode_input = DialogInput("Enter pin code")
        return self.pincode_input
    
    # Bank Details Inputs
    def _create_account_number_input(self) -> DialogInput:
        self.account_number_input = DialogInput("ex: 123456789")
        return self.account_number_input
    
    def _create_account_number_confirm_input(self) -> DialogInput:
        self.account_number_confirm = DialogInput("ex: 123456789")
        return self.account_number_confirm
    
    def _create_ifsc_input(self) -> DialogInput:
        self.ifsc_input = DialogInput("ex: ICIC0001234")
        return self.ifsc_input
    
    def _create_bank_branch_input(self) -> DialogInput:
        self.bank_branch_input = DialogInput("ex: ICICI Bank, Mumbai")
        return self.bank_branch_input
    
    def _create_account_holder_input(self) -> DialogInput:
        self.account_holder_input = DialogInput("ex: Babu Lal")
        return self.account_holder_input
    
    def _create_upi_input(self) -> DialogInput:
        self.upi_input = DialogInput("ex: babulal@upi")
        return self.upi_input
    
    # === Helper Methods ===
    
    def _on_name_changed(self, text: str):
        """Force uppercase in Party Name input"""
        to_upper(self.name_input, text)
    
    def _clear_name_error(self, *_):
        """Reset Party Name field style when user edits it"""
        try:
            self.name_input.set_error(False)
        except Exception:
            pass
    
    def _populate_form(self):
        """Populate form fields with existing party data"""
        d = self.party_data or {}
        
        self.name_input.setText(d.get('name', ''))
        self.phone_input.setText(d.get('phone') or d.get('mobile', ''))
        self.email_input.setText(d.get('email', ''))
        self.address_input.setPlainText(d.get('address', ''))
        self.gst_number_input.setText(d.get('gst_number') or d.get('gstin', ''))
        self.pan_input.setText(d.get('pan', ''))
        
        party_type = d.get('type') or d.get('party_type', 'Customer')
        type_index = self.type_combo.findText(party_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.opening_balance.setText(str(d.get('opening_balance', 0)))
        
        # Balance type
        balance_type = d.get('balance_type', 'dr').lower()
        if balance_type in self._balance_type_reverse_map:
            display_text = self._balance_type_reverse_map[balance_type]
            bt_index = self.balance_type_combo.findText(display_text)
            if bt_index >= 0:
                self.balance_type_combo.setCurrentIndex(bt_index)
        
        # State (combo box)
        state_value = d.get('state', '')
        state_index = self.state_input.findText(state_value)
        if state_index >= 0:
            self.state_input.setCurrentIndex(state_index)
        
        self.city_input.setText(d.get('city', ''))
        self.pincode_input.setText(d.get('pincode', ''))
        
        # Bank details (if present)
        bank_data = d.get('bank_details', {})
        if bank_data:
            self.account_number_input.setText(bank_data.get('account_number', ''))
            self.account_number_confirm.setText(bank_data.get('account_number', ''))
            self.ifsc_input.setText(bank_data.get('ifsc', ''))
            self.bank_branch_input.setText(bank_data.get('bank_branch', ''))
            self.account_holder_input.setText(bank_data.get('account_holder', ''))
            self.upi_input.setText(bank_data.get('upi', ''))
            # Show bank section if data exists
            if any(bank_data.values()):
                self.bank_section.setVisible(True)
                self.bank_link.setText("➖ <a href='#' style='color: {0}; text-decoration: none;'>Hide Bank Account Details</a>".format(PRIMARY))
    
    def _save_party(self):
        """Validate and save party data"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        gst = self.gst_number_input.text().strip()
        pan = self.pan_input.text().strip()
        address = self.address_input.toPlainText().strip()
        state = self.state_input.currentText().strip()
        city = self.city_input.text().strip()
        pincode = self.pincode_input.text().strip()
        party_type = self.type_combo.currentText().strip()
        
        # Get current party ID for edit mode
        current_party_id = self.party_data.get('id') if self.party_data else None
        
        # Check for duplicate party name
        is_duplicate, error = party_service.check_duplicate_name(name, current_party_id)
        if is_duplicate:
            QMessageBox.warning(self, "Duplicate Name", error)
            self.name_input.setFocus()
            return
        
        # Validate party name
        is_valid, error = party_service.validate_party_name(name)
        if not is_valid:
            self.name_input.set_error(True, error)
            self.name_input.setFocus()
            return
        
        # Validate party type
        is_valid, error = party_service.validate_party_type(party_type)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.type_combo.setFocus()
            return
        
        # Validate phone number
        is_valid, error = party_service.validate_mobile_number(phone)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.phone_input.setFocus()
            return
        
        # Validate email
        is_valid, error = party_service.validate_email_address(email)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.email_input.setFocus()
            return
        
        # Validate GSTIN
        is_valid, error = party_service.validate_gstin_number(gst)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.gst_number_input.setFocus()
            return
        
        # Validate PAN
        is_valid, error = party_service.validate_pan_number(pan)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.pan_input.setFocus()
            return
        
        # Validate pincode
        is_valid, error = party_service.validate_pincode_number(pincode)
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.pincode_input.setFocus()
            return
        
        # Validate opening balance
        is_valid, opening, error = party_service.validate_opening_balance(
            self.opening_balance.text()
        )
        if not is_valid:
            QMessageBox.warning(self, "Validation", error)
            self.opening_balance.setFocus()
            return
        
        # Validate bank details if bank section is visible
        bank_details = None
        if self.bank_section.isVisible():
            acc_num = self.account_number_input.text().strip()
            acc_confirm = self.account_number_confirm.text().strip()
            
            if acc_num or acc_confirm:
                if acc_num != acc_confirm:
                    QMessageBox.warning(self, "Validation", "Account numbers must match")
                    self.account_number_confirm.setFocus()
                    return
                
                bank_details = {
                    'account_number': acc_num,
                    'ifsc': self.ifsc_input.text().strip(),
                    'bank_branch': self.bank_branch_input.text().strip(),
                    'account_holder': self.account_holder_input.text().strip(),
                    'upi': self.upi_input.text().strip(),
                }

        # Get balance type value
        balance_type_display = self.balance_type_combo.currentText()
        balance_type = self._balance_type_map.get(balance_type_display, 'dr')

        party = party_service.prepare_party_data(
            name=name,
            mobile=phone,
            email=email,
            gst_number=gst,
            pan=pan,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            opening_balance=opening,
            balance_type=balance_type,
            party_type=party_type,
            party_id=current_party_id
        )

        # Save to database via service
        try:
            if current_party_id:
                success = party_service.update_party(current_party_id, party)
                if not success:
                    QMessageBox.warning(self, "Error", "Failed to update party.")
                    return
            else:
                party_id = party_service.add_party(party)
                if party_id:
                    party['id'] = party_id
                else:
                    QMessageBox.warning(self, "Error", "Failed to add party.")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving party: {e}")
            return

        # Add bank details to result
        if bank_details:
            party['bank_details'] = bank_details
        
        self.result_data = party
        QMessageBox.information(self, "Success", "Party saved successfully!")
        self.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts: Enter to save, Escape to cancel."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Don't save if focus is in TextEdit
            from PySide6.QtWidgets import QTextEdit
            if not isinstance(self.focusWidget(), QTextEdit):
                self._save_party()
                return
        elif event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

