"""
Party dialog module - Add/Edit Party (Customer/Supplier)
Uses common methods from BaseDialog
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QGridLayout
)
from PySide6.QtCore import Qt

from theme import (
    PRIMARY, TEXT_PRIMARY,
    get_title_font,
    DIALOG_FORM_DEFAULT_WIDTH, DIALOG_FORM_DEFAULT_HEIGHT,
    DIALOG_FORM_MIN_WIDTH, DIALOG_FORM_MIN_HEIGHT
)
from widgets import (
    DialogInput, DialogComboBox, DialogEditableComboBox, DialogTextEdit, DialogScrollArea   
)
from ui.base.base_dialog import BaseDialog
from ui.error_handler import UIErrorHandler
from core.enums import PartyType, BalanceType, get_state_list
from core.services.party_service import party_service
from core.core_utils import to_upper
from core.logger import get_logger

logger = get_logger(__name__)


class PartyDialog(BaseDialog):
    def __init__(self, parent=None, party_data=None):
        self.party_data = party_data
        self.result_data = None
        super().__init__(
            parent=parent,
            title="Add Party" if not party_data else "Edit Party",
            default_width=DIALOG_FORM_DEFAULT_WIDTH,
            default_height=DIALOG_FORM_DEFAULT_HEIGHT,
            min_width=DIALOG_FORM_MIN_WIDTH,
            min_height=DIALOG_FORM_MIN_HEIGHT
        )
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Always create credit fields for dialog lifetime
        self._create_credit_limit_input()
        self._create_credit_days_input()

        # Create scroll area widget
        scroll_widget = DialogScrollArea()
        self.scroll_layout = scroll_widget.get_layout()

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

        main_layout.addWidget(scroll_widget)

        # Set tab order for keyboard navigation
        self._set_tab_order()

        # Footer with buttons
        main_layout.addWidget(self._build_footer(
            save_text="Save Party",
            save_callback=self._on_save
        ))

        # Populate form if editing
        if self.party_data:
            self._populate_form()

    def _build_bank_link(self):
        """Create a hyperlink to show/hide bank details section"""
        self.bank_link = self._create_collapsible_link(
            add_text="Add Bank Account Details",
            hide_text="Hide Bank Account Details",
            scroll_layout=self.scroll_layout
        )
        self.bank_link.mousePressEvent = self._toggle_bank_section

    def _toggle_bank_section(self, event=None):
        """Show/hide bank details section"""
        self._toggle_collapsible_section(self.bank_section, self.bank_link)

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

        # Row 3: Credit Limit, Credit Days
        layout.addWidget(self._create_field_group(
            "Credit Limit",
            self._create_credit_limit_input()
        ), 3, 0)
        layout.addWidget(self._create_field_group(
            "Credit Days",
            self._create_credit_days_input()
        ), 3, 1)
        layout.addWidget(self._create_field_group(
            "Status",
            self._create_status_combo()
        ), 3, 2)
        return widget

    def _validate_credit_fields(self):
        # Credit limit: must be a valid decimal >= 0
        # Credit days: must be integer >= 0
        errors = []
        try:
            credit_limit = float(self.credit_limit_input.text() or 0)
            if credit_limit < 0:
                errors.append("Credit limit cannot be negative.")
                self.credit_limit_input.set_error(True)
        except Exception:
            errors.append("Credit limit must be a valid number.")
            self.credit_limit_input.set_error(True)
        try:
            credit_days = int(self.credit_days_input.text() or 0)
            if credit_days < 0:
                errors.append("Credit days cannot be negative.")
                self.credit_days_input.set_error(True)
        except Exception:
            errors.append("Credit days must be a valid integer.")
            self.credit_days_input.set_error(True)
        return errors

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

    def _create_status_combo(self) -> DialogComboBox:
        self.status_combo = DialogComboBox(items=["Active", "Inactive"])
        self.status_combo.setAccessibleName("Party Status")
        self.status_combo.setToolTip("Active parties appear in invoices. Inactive parties are hidden.")
        self.status_combo.setCurrentIndex(0)
        return self.status_combo

    def _create_credit_limit_input(self) -> DialogInput:
        self.credit_limit_input = DialogInput("Credit Limit (₹)")
        self.credit_limit_input.setPlaceholderText("0.00")
        self.credit_limit_input.setAccessibleName("Credit Limit")
        self.credit_limit_input.setToolTip("Maximum credit amount allowed for this party (0 = unlimited)")
        self.credit_limit_input.setMaxLength(12)
        self.credit_limit_input.setValidator(self._get_decimal_validator())
        self.credit_limit_input.textChanged.connect(self._clear_credit_limit_error)
        return self.credit_limit_input

    def _clear_credit_limit_error(self, *_):
        try:
            self.credit_limit_input.set_error(False)
        except Exception:
            pass

    def _create_credit_days_input(self) -> DialogInput:
        self.credit_days_input = DialogInput("Credit Days")
        self.credit_days_input.setPlaceholderText("0")
        self.credit_days_input.setAccessibleName("Credit Days")
        self.credit_days_input.setToolTip("Payment due period in days (0 = immediate payment)")
        self.credit_days_input.setMaxLength(3)
        self.credit_days_input.setValidator(self._get_int_validator())
        self.credit_days_input.textChanged.connect(self._clear_credit_days_error)
        return self.credit_days_input

    def _clear_credit_days_error(self, *_):
        try:
            self.credit_days_input.set_error(False)
        except Exception:
            pass

    def _get_decimal_validator(self):
        from PySide6.QtGui import QDoubleValidator
        v = QDoubleValidator(0.00, 99999999.99, 2)
        v.setNotation(QDoubleValidator.StandardNotation)
        return v

    def _get_int_validator(self):
        from PySide6.QtGui import QIntValidator
        return QIntValidator(0, 365)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QToolTip
        if event.type() == QEvent.FocusIn:
            if obj is getattr(self, 'gst_number_input', None):
                QToolTip.showText(obj.mapToGlobal(obj.rect().bottomLeft()), obj.toolTip(), obj)
            elif obj is getattr(self, 'pan_input', None):
                QToolTip.showText(obj.mapToGlobal(obj.rect().bottomLeft()), obj.toolTip(), obj)
        return super().eventFilter(obj, event)

    def _set_tab_order(self):
        # Set tab order for keyboard navigation (main fields only)
        """Dialog for adding/editing a party (customer/supplier)"""
        widgets = [
            self.name_input,
            self.phone_input,
            self.email_input,
            self.gst_number_input,
            self.pan_input,
            self.type_combo,
            self.opening_balance,
            self.balance_type_combo,
            self.address_input,
            self.city_input,
            self.state_input,
            self.pincode_input
        ]
        for i in range(len(widgets) - 1):
            self.setTabOrder(widgets[i], widgets[i + 1])

    # === Input Field Creators ===
    
    def _create_name_input(self) -> DialogInput:
        self.name_input = DialogInput("Enter party name")
        self.name_input.setToolTip("Required. Party name (will be stored in uppercase)")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.textChanged.connect(self._clear_name_error)
        self.name_input.textChanged.connect(self._mark_form_modified)
        return self.name_input
    
    def _create_phone_input(self) -> DialogInput:
        self.phone_input = DialogInput("Enter mobile number")
        self.phone_input.setToolTip("10-digit Indian mobile number (optional)")
        self.phone_input.textChanged.connect(self._clear_phone_error)
        self.phone_input.textChanged.connect(self._mark_form_modified)
        return self.phone_input
    
    def _clear_phone_error(self, *_):
        """Reset phone field style when user edits it"""
        try:
            self.phone_input.set_error(False)
        except Exception:
            pass
    
    def _create_email_input(self) -> DialogInput:
        self.email_input = DialogInput("Enter email address")
        self.email_input.setToolTip("Valid email address (optional)")
        self.email_input.textChanged.connect(self._clear_email_error)
        self.email_input.textChanged.connect(self._mark_form_modified)
        return self.email_input
    
    def _clear_email_error(self, *_):
        """Reset email field style when user edits it"""
        try:
            self.email_input.set_error(False)
        except Exception:
            pass
    
    def _create_gstin_input(self) -> DialogInput:
        self.gst_number_input = DialogInput("Ex: 22AAAAA0000A1Z5")
        self.gst_number_input.setAccessibleName("GSTIN")
        self.gst_number_input.setToolTip("15-character GST Identification Number (format: 22AAAAA0000A1Z5)")
        self.gst_number_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.gst_number_input.customContextMenuRequested.connect(self._show_gstin_context_menu)
        self.gst_number_input.textChanged.connect(lambda text: to_upper(self.gst_number_input, text))
        self.gst_number_input.textChanged.connect(self._clear_gstin_error)
        self.gst_number_input.textChanged.connect(self._mark_form_modified)
        self.gst_number_input.installEventFilter(self)
        return self.gst_number_input

    def _show_gstin_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu, QApplication
        menu = QMenu()
        copy_action = menu.addAction("Copy GSTIN")
        action = menu.exec_(self.gst_number_input.mapToGlobal(pos))
        if action == copy_action:
            QApplication.clipboard().setText(self.gst_number_input.text())
    
    def _clear_gstin_error(self, *_):
        """Reset GSTIN field style when user edits it"""
        try:
            self.gst_number_input.set_error(False)
        except Exception:
            pass
    
    def _create_pan_input(self) -> DialogInput:
        self.pan_input = DialogInput("Ex: ABCDE1234F")
        self.pan_input.setToolTip("10-character Permanent Account Number (format: ABCDE1234F)")
        self.pan_input.textChanged.connect(lambda text: to_upper(self.pan_input, text))
        self.pan_input.textChanged.connect(self._clear_pan_error)
        self.pan_input.installEventFilter(self)
        return self.pan_input
    
    def _clear_pan_error(self, *_):
        """Reset PAN field style when user edits it"""
        try:
            self.pan_input.set_error(False)
        except Exception:
            pass
    
    def _create_type_combo(self) -> DialogComboBox:
        party_types = ["", PartyType.CUSTOMER.value, PartyType.SUPPLIER.value, PartyType.BOTH.value]
        self.type_combo = DialogComboBox(items=party_types)
        self.type_combo.setToolTip("Required. Select party type (Customer/Supplier/Both)")
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
        self.opening_balance.setToolTip("Opening balance amount from previous accounting period")
        self.opening_balance.textChanged.connect(self._clear_opening_balance_error)
        return self.opening_balance
    
    def _clear_opening_balance_error(self, *_):
        """Reset opening balance field style when user edits it"""
        try:
            self.opening_balance.set_error(False)
        except Exception:
            pass
    
    def _create_balance_type_combo(self) -> DialogComboBox:
        # Balance types: To Receive (dr) for customers, To Pay (cr) for suppliers
        balance_types = [
            ("To Receive (DR)", "dr"),
            ("To Pay (CR)", "cr")
        ]
        self.balance_type_combo = DialogComboBox(items=[bt[0] for bt in balance_types])
        self.balance_type_combo.setToolTip("To Receive (DR) = Party owes you | To Pay (CR) = You owe party")
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
        self.address_input.setToolTip("Full address including street, building, landmark etc.")
        self.address_input.textChanged.connect(self._clear_address_error)
        return self.address_input
    
    def _clear_address_error(self, *_):
        """Reset address field style when user edits it"""
        try:
            if hasattr(self.address_input, 'set_error'):
                self.address_input.set_error(False)
        except Exception:
            pass
    
    def _create_city_input(self) -> DialogInput:
        self.city_input = DialogInput("Enter city")
        self.city_input.setToolTip("City or town name")
        self.city_input.textChanged.connect(lambda text: to_upper(self.city_input, text))
        self.city_input.textChanged.connect(self._clear_city_error)
        return self.city_input
    
    def _clear_city_error(self, *_):
        """Reset city field style when user edits it"""
        try:
            self.city_input.set_error(False)
        except Exception:
            pass
    
    def _create_state_input(self) -> DialogEditableComboBox:
        # Use centralized state list from core.enums
        states = get_state_list()
        self.state_input = DialogEditableComboBox(
            items=states,
            placeholder="Select or type state",
            auto_upper=False  # State names have proper casing
        )
        self.state_input.setToolTip("Type to search or select from dropdown")
        # Set default state to first item if no existing data
        if not self.party_data and len(states) > 0:
            self.state_input.setCurrentIndex(0)
        return self.state_input
    
    def _create_pincode_input(self) -> DialogInput:
        self.pincode_input = DialogInput("Enter pin code")
        self.pincode_input.setToolTip("6-digit postal code for the party's address")
        self.pincode_input.textChanged.connect(self._clear_pincode_error)
        return self.pincode_input
    
    def _clear_pincode_error(self, *_):
        """Reset pincode field style when user edits it"""
        try:
            self.pincode_input.set_error(False)
        except Exception:
            pass
    
    # Bank Details Inputs
    def _create_account_number_input(self) -> DialogInput:
        self.account_number_input = DialogInput("ex: 123456789")
        self.account_number_input.setToolTip("Bank account number for payment transactions")
        return self.account_number_input
    
    def _create_account_number_confirm_input(self) -> DialogInput:
        self.account_number_confirm = DialogInput("ex: 123456789")
        self.account_number_confirm.setToolTip("Re-enter account number for verification")
        return self.account_number_confirm
    
    def _create_ifsc_input(self) -> DialogInput:
        self.ifsc_input = DialogInput("ex: ICIC0001234")
        self.ifsc_input.setToolTip("11-character IFSC code (e.g., ICIC0001234)")
        return self.ifsc_input
    
    def _create_bank_branch_input(self) -> DialogInput:
        self.bank_branch_input = DialogInput("ex: ICICI Bank, Mumbai")
        self.bank_branch_input.setToolTip("Bank name and branch location")
        return self.bank_branch_input
    
    def _create_account_holder_input(self) -> DialogInput:
        self.account_holder_input = DialogInput("ex: Babu Lal")
        self.account_holder_input.setToolTip("Name of the account holder as per bank records")
        return self.account_holder_input
    
    def _create_upi_input(self) -> DialogInput:
        self.upi_input = DialogInput("ex: babulal@upi")
        self.upi_input.setToolTip("UPI ID for quick digital payments (e.g., name@bank)")
        self.upi_input.textChanged.connect(self._clear_upi_error)
        return self.upi_input
    
    def _clear_upi_error(self, *_):
        """Reset UPI field style when user edits it"""
        try:
            self.upi_input.set_error(False)
        except Exception:
            pass
    
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
        
        # State (editable combo box - use setText for better compatibility)
        state_value = d.get('state', '')
        if state_value:
            self.state_input.setText(state_value)
        
        self.city_input.setText(d.get('city', ''))
        self.pincode_input.setText(d.get('pincode', ''))
        
        # Credit settings
        status = d.get('status', 'Active')
        status_index = self.status_combo.findText(status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        self.credit_limit_input.setText(str(d.get('credit_limit', 0)))
        self.credit_days_input.setText(str(d.get('credit_days', 0)))
        
        # Bank details - handle both nested dict and flat columns from database
        bank_data = d.get('bank_details', {})
        # Also check for flat bank columns (direct from database)
        account_number = bank_data.get('account_number') or d.get('account_number', '')
        ifsc = bank_data.get('ifsc') or d.get('ifsc', '')
        bank_branch = bank_data.get('bank_branch') or d.get('bank_branch', '')
        account_holder = bank_data.get('account_holder') or d.get('account_holder', '')
        upi = bank_data.get('upi') or d.get('upi', '')
        
        if account_number or ifsc or bank_branch or account_holder or upi:
            self.account_number_input.setText(account_number or '')
            self.account_number_confirm.setText(account_number or '')
            self.ifsc_input.setText(ifsc or '')
            self.bank_branch_input.setText(bank_branch or '')
            self.account_holder_input.setText(account_holder or '')
            self.upi_input.setText(upi or '')
            # Show bank section if data exists
            self.bank_section.setVisible(True)
            self.bank_link.setText("➖ <a href='#' style='color: {0}; text-decoration: none;'>Hide Bank Account Details</a>".format(PRIMARY))
        
        # Reset form modified flag after population
        self._form_modified = False
    
    def _on_save(self):
        """Validate and save party data"""
        self._show_loading(True)
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

        # Required fields check
        required_fields = [
            (self.name_input, name, "Party name is required."),
            (self.type_combo, party_type, "Party type is required."),
        ]
        missing = []
        for widget, value, msg in required_fields:
            if not value:
                if hasattr(widget, 'set_error'):
                    widget.set_error(True, msg)
                missing.append(msg)
        if missing:
            UIErrorHandler.show_validation_error("Missing Required Fields", missing)
            self._show_loading(False)
            return

        # Duplicate party name
        is_duplicate, error = party_service.check_duplicate_name(name, current_party_id)
        if is_duplicate:
            self.name_input.set_error(True, error)
            self.name_input.setFocus()
            UIErrorHandler.show_validation_error("Duplicate Name", [error])
            self._show_loading(False)
            return

        # Duplicate GSTIN (if provided)
        if gst:
            is_dup_gstin, gstin_error = party_service.check_duplicate_gstin(gst, current_party_id)
            if is_dup_gstin:
                self.gst_number_input.set_error(True, gstin_error)
                self.gst_number_input.setFocus()
                UIErrorHandler.show_validation_error("Duplicate GSTIN", [gstin_error])
                self._show_loading(False)
                return

        # Validate party name
        is_valid, error = party_service.validate_party_name(name)
        if not is_valid:
            self.name_input.set_error(True, error)
            self.name_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate party type
        is_valid, error = party_service.validate_party_type(party_type)
        if not is_valid:
            self.type_combo.set_error(True, error) if hasattr(self.type_combo, 'set_error') else None
            self.type_combo.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate phone number
        is_valid, error = party_service.validate_mobile_number(phone)
        if not is_valid:
            self.phone_input.set_error(True, error)
            self.phone_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate email
        is_valid, error = party_service.validate_email_address(email)
        if not is_valid:
            self.email_input.set_error(True, error)
            self.email_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate GSTIN
        is_valid, error = party_service.validate_gstin_number(gst)
        if not is_valid:
            self.gst_number_input.set_error(True, error)
            self.gst_number_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate PAN
        is_valid, error = party_service.validate_pan_number(pan)
        if not is_valid:
            self.pan_input.set_error(True, error)
            self.pan_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate pincode
        is_valid, error = party_service.validate_pincode_number(pincode)
        if not is_valid:
            self.pincode_input.set_error(True, error)
            self.pincode_input.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return

        # Validate opening balance
        is_valid, opening, error = party_service.validate_opening_balance(
            self.opening_balance.text()
        )
        if not is_valid:
            self.opening_balance.set_error(True, error)
            self.opening_balance.setFocus()
            UIErrorHandler.show_validation_error("Validation Error", [error])
            self._show_loading(False)
            return


        # Validate credit fields
        credit_errors = self._validate_credit_fields()
        if credit_errors:
            UIErrorHandler.show_validation_error("Validation Error", credit_errors)
            self._show_loading(False)
            return

        # Validate bank details if bank section is visible (early validation)
        bank_details = None
        if self.bank_section.isVisible():
            acc_num = self.account_number_input.text().strip()
            acc_confirm = self.account_number_confirm.text().strip()

            if acc_num or acc_confirm:
                # Validate account numbers match early
                if acc_num != acc_confirm:
                    self.account_number_confirm.set_error(True, "Account numbers must match")
                    self.account_number_confirm.setFocus()
                    UIErrorHandler.show_validation_error("Validation Error", ["Account numbers must match"])
                    self._show_loading(False)
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
            credit_limit=float(self.credit_limit_input.text() or 0),
            credit_days=int(self.credit_days_input.text() or 0),
            status=self.status_combo.currentText(),
            party_id=current_party_id,
            bank_details=bank_details
        )

        # Save to database via service
        is_update = current_party_id is not None
        action = "update" if is_update else "create"
        logger.info(f"Attempting to {action} party: {name}")
        
        try:
            if current_party_id:
                success = party_service.update_party(current_party_id, party)
                if not success:
                    logger.error(f"Failed to update party: {name}")
                    UIErrorHandler.show_error("Error", "Failed to update party.")
                    self._show_loading(False)
                    return
            else:
                party_id = party_service.add_party(party)
                if party_id:
                    party['id'] = party_id
                else:
                    logger.error(f"Failed to add party: {name}")
                    UIErrorHandler.show_error("Error", "Failed to add party.")
                    self._show_loading(False)
                    return
        except Exception as e:
            # Show specific error message for duplicate party
            error_msg = str(e)
            logger.error(f"Error saving party {name}: {error_msg}")
            if "already exists" in error_msg.lower():
                UIErrorHandler.show_validation_error("Duplicate Party", [error_msg])
            else:
                UIErrorHandler.show_error("Error", f"Error saving party: {error_msg}")
            self._show_loading(False)
            return

        # Add bank details to result
        if bank_details:
            party['bank_details'] = bank_details

        self.result_data = party
        logger.info(f"Party {action}d successfully: {name}")
        UIErrorHandler.show_success("Success", "Party saved successfully!")
        self._show_loading(False)
        self.accept()
    
    def closeEvent(self, event):
        """Clean up resources when dialog is closed"""
        self._cleanup_resources()
        super().closeEvent(event)
    
    def _cleanup_resources(self):
        """Disconnect signals and cleanup resources"""
        try:
            # Disconnect all signal connections
            if hasattr(self, 'name_input') and self.name_input:
                try:
                    self.name_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'phone_input') and self.phone_input:
                try:
                    self.phone_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'email_input') and self.email_input:
                try:
                    self.email_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'gst_number_input') and self.gst_number_input:
                try:
                    self.gst_number_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'pan_input') and self.pan_input:
                try:
                    self.pan_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'city_input') and self.city_input:
                try:
                    self.city_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'pincode_input') and self.pincode_input:
                try:
                    self.pincode_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'opening_balance') and self.opening_balance:
                try:
                    self.opening_balance.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'type_combo') and self.type_combo:
                try:
                    self.type_combo.currentTextChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'address_input') and self.address_input:
                try:
                    self.address_input.textChanged.disconnect()
                except Exception:
                    pass
            
            if hasattr(self, 'upi_input') and self.upi_input:
                try:
                    self.upi_input.textChanged.disconnect()
                except Exception:
                    pass
        except Exception as e:
            # Log but don't raise during cleanup
            import logging
            logging.debug(f"Error during resource cleanup: {e}")

