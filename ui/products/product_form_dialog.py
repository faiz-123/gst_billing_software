"""
Product dialog module (moved from products.py to avoid circular imports)
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt

from theme import (
    PRIMARY, TEXT_PRIMARY,
    get_title_font, get_quick_chip_style,
    DIALOG_FORM_DEFAULT_WIDTH, DIALOG_FORM_DEFAULT_HEIGHT,
    DIALOG_FORM_MIN_WIDTH, DIALOG_FORM_MIN_HEIGHT
)
from widgets import (
    DialogInput, DialogComboBox, DialogEditableComboBox, DialogSpinBox, DialogDoubleSpinBox,
    DialogCheckBox, DialogTextEdit, DialogScrollArea
)
from ui.base.base_dialog import BaseDialog
from ui.error_handler import UIErrorHandler
from core.services.product_service import ProductService
from core.validators import (
    set_name_error_state, set_price_error_state, set_field_error_state,
    validate_hsn_code
)
from core.core_utils import to_upper
from core.db.sqlite_db import db
from core.logger import get_logger
from core.enums import QUICK_GST_RATES

logger = get_logger(__name__)


class ProductDialog(BaseDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_data=None):
        self.product_data = product_data
        self.product_service = ProductService(db)
        super().__init__(
            parent=parent,
            title="Add Product" if not product_data else "Edit Product",
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
        
        # Create scroll area widget
        scroll_widget = DialogScrollArea()
        self.scroll_layout = scroll_widget.get_layout()
        
        # Header
        title_text = "Edit Product" if self.product_data else "Add New Product"
        title = QLabel(title_text)
        title.setFont(get_title_font())
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        self.scroll_layout.addWidget(title)
        
        
        # === SECTION 1: Basic Information ===
        self.scroll_layout.addWidget(self._create_section("Basic Information", self._build_basic_info_section()))
        
        # === SECTION 2: Pricing & Tax ===
        self.scroll_layout.addWidget(self._create_section("Pricing & Tax", self._build_pricing_section()))
        
        # === Stock & Inventory Link ===
        self._build_stock_link()
        
        # === SECTION 3: Stock & Inventory (hidden by default) ===
        self.stock_section = self._create_section("Stock & Inventory", self._build_stock_section())
        self.stock_section.setVisible(False)
        self.scroll_layout.addWidget(self.stock_section)
        
        # === Additional Details Link ===
        self._build_additional_link()
        
        # === SECTION 4: Additional Details (hidden by default) ===
        self.additional_section = self._create_section("Additional Details", self._build_additional_section())
        self.additional_section.setVisible(False)
        self.scroll_layout.addWidget(self.additional_section)
        
        self.scroll_layout.addStretch()
        
        main_layout.addWidget(scroll_widget)
        
        # Footer with buttons
        main_layout.addWidget(self._build_footer(
            save_text="Save Product",
            save_callback=self._on_save
        ))
        
        # Populate form if editing
        if self.product_data:
            self.populate_form()
    
    def _build_stock_link(self):
        """Create a hyperlink to show/hide stock & inventory section"""
        self.stock_link = self._create_collapsible_link(
            add_text="Add Stock & Inventory",
            hide_text="Hide Stock & Inventory",
            scroll_layout=self.scroll_layout
        )
        self.stock_link.mousePressEvent = self._toggle_stock_section
    
    def _toggle_stock_section(self, event=None):
        """Show/hide stock & inventory section"""
        self._toggle_collapsible_section(self.stock_section, self.stock_link)
    
    def _build_additional_link(self):
        """Create a hyperlink to show/hide additional details"""
        self.additional_link = self._create_collapsible_link(
            add_text="Add Additional Information",
            hide_text="Hide Additional Information",
            scroll_layout=self.scroll_layout
        )
        self.additional_link.mousePressEvent = self._toggle_additional_section
    
    def _toggle_additional_section(self, event=None):
        """Show/hide additional details section"""
        self._toggle_collapsible_section(self.additional_section, self.additional_link)
    
    def _build_basic_info_section(self) -> QWidget:
        """Build the basic information section with 3 columns"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Item Name, HSN Code, Barcode/SKU
        layout.addWidget(self._create_field_group(
            "Item Name <span style='color:#d32f2f'>*</span>",
            self._create_name_input()
        ), 0, 0)
        
        layout.addWidget(self._create_field_group(
            "HSN Code",
            self._create_hsn_input()
        ), 0, 1)
        
        layout.addWidget(self._create_field_group(
            "Barcode / SKU",
            self._create_barcode_input()
        ), 0, 2)
        
        # Row 1: Product Type, Category, Unit of Measure
        layout.addWidget(self._create_field_group(
            "Product Type",
            self._create_type_combo()
        ), 1, 0)
        
        layout.addWidget(self._create_field_group(
            "Category",
            self._create_category_input()
        ), 1, 1)
        
        layout.addWidget(self._create_field_group(
            "Unit of Measure",
            self._create_unit_combo()
        ), 1, 2)
        
        return widget
    
    def _build_pricing_section(self) -> QWidget:
        """Build the pricing & tax section with 3 columns"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Sales Rate, Purchase Rate, MRP
        layout.addWidget(self._create_field_group(
            "Sales Rate <span style='color:#d32f2f'>*</span>",
            self._create_selling_price_input()
        ), 0, 0)
        
        layout.addWidget(self._create_field_group(
            "Purchase Rate",
            self._create_purchase_price_input()
        ), 0, 1)
        
        layout.addWidget(self._create_field_group(
            "MRP",
            self._create_mrp_input()
        ), 0, 2)
        
        # Row 1: Discount, GST Registered checkbox
        layout.addWidget(self._create_field_group(
            "Discount %",
            self._create_discount_input()
        ), 1, 0)
        
        layout.addWidget(self._create_gst_registered_checkbox(), 1, 1, 1, 2)
        
        # Row 2: GST Rate with Quick Select Buttons, SGST, CGST
        layout.addWidget(self._create_gst_rate_with_quick_buttons(), 2, 0, Qt.AlignTop)
        
        layout.addWidget(self._create_field_group(
            "SGST %",
            self._create_sgst_input()
        ), 2, 1, Qt.AlignTop)
        
        layout.addWidget(self._create_field_group(
            "CGST %",
            self._create_cgst_input()
        ), 2, 2, Qt.AlignTop)
        
        # Set initial read-only state for GST fields (checkbox is unchecked by default)
        self._update_gst_fields_state(False)
        
        return widget
    
    def _create_gst_rate_with_quick_buttons(self) -> QWidget:
        """Create GST Rate field with quick-select buttons for common rates"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel("Tax Rate (GST) %")
        label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none; background: transparent;")
        layout.addWidget(label)
        
        # GST Rate Input
        self._create_tax_rate_input()
        layout.addWidget(self.tax_rate)
        
        # Quick Select Buttons Container
        self.quick_gst_container = QWidget()
        self.quick_gst_container.setStyleSheet("background: transparent; border: none;")
        quick_layout = QHBoxLayout(self.quick_gst_container)
        quick_layout.setContentsMargins(0, 4, 0, 0)
        quick_layout.setSpacing(8)
        
        # Quick Rate Label
        quick_label = QLabel("Quick:")
        quick_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; border: none; background: transparent;")
        quick_layout.addWidget(quick_label)
        
        # Common GST Rates from centralized config
        self.gst_rate_buttons = {}
        for rate in QUICK_GST_RATES:
            btn = QPushButton(f"{rate}%")
            btn.setFixedSize(50, 28)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(get_quick_chip_style(False))
            btn.clicked.connect(lambda checked, r=rate: self._on_quick_gst_selected(r))
            btn.setToolTip(f"Set GST rate to {rate}%")
            self.gst_rate_buttons[rate] = btn
            quick_layout.addWidget(btn)
        
        quick_layout.addStretch()
        layout.addWidget(self.quick_gst_container)
        
        return container

    def _on_quick_gst_selected(self, rate: float):
        """Handle quick GST rate button click"""
        # Enable GST registered if selecting a non-zero rate
        if rate > 0 and not self.gst_registered_checkbox.isChecked():
            self.gst_registered_checkbox.setChecked(True)
        
        # Set the tax rate
        self.tax_rate.setValue(rate)
        self._form_modified = True
        
        # Update button styles to show active selection
        self._update_gst_rate_button_styles(rate)
    
    def _update_gst_rate_button_styles(self, active_rate: float = None):
        """Update quick GST rate button styles to highlight active selection"""
        for rate, btn in self.gst_rate_buttons.items():
            is_active = (rate == active_rate)
            btn.setStyleSheet(get_quick_chip_style(is_active))

    def _build_stock_section(self) -> QWidget:
        """Build the stock & inventory section with 3 columns"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Track Stock checkbox (spans all 3 columns)
        layout.addWidget(self._create_track_stock_checkbox(), 0, 0, 1, 3)
        
        # Row 1: Opening Stock, Low Stock Alert
        layout.addWidget(self._create_field_group(
            "Opening Stock",
            self._create_opening_stock_input()
        ), 1, 0)
        
        layout.addWidget(self._create_field_group(
            "Low Stock Alert",
            self._create_low_stock_input()
        ), 1, 1)
        
        # Empty placeholder for alignment
        empty_widget = QWidget()
        empty_widget.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(empty_widget, 1, 2)
        
        # Set initial read-only state for stock fields (checkbox is unchecked by default)
        self._update_stock_fields_state(False)
        
        return widget
    
    def _create_track_stock_checkbox(self) -> QWidget:
        """Create Track Stock checkbox"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        self.track_stock_checkbox = DialogCheckBox("Track Stock")
        self.track_stock_checkbox.setChecked(False)
        self.track_stock_checkbox.setToolTip("Enable inventory tracking. Stock will be updated automatically on sales/purchases.")
        self.track_stock_checkbox.stateChanged.connect(self._on_track_stock_changed)
        layout.addWidget(self.track_stock_checkbox)
        layout.addStretch()
        
        return container
    
    def _on_track_stock_changed(self, state: int):
        """Handle Track Stock checkbox state change"""
        is_checked = state == Qt.Checked.value
        self._update_stock_fields_state(is_checked)
    
    def _update_stock_fields_state(self, enabled: bool):
        """Update Opening Stock and Low Stock Alert fields read-only state"""
        # Use the widget's set_readonly method
        self.opening_stock.set_readonly(not enabled)
        self.low_stock_alert.set_readonly(not enabled)
        
        if not enabled:
            # Reset values to 0 when disabled
            self.opening_stock.setValue(0)
            self.low_stock_alert.setValue(0)
    
    def _build_additional_section(self) -> QWidget:
        """Build the additional details section with 3 columns"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        # Row 0: Warranty, Serial Number Tracking, (empty)
        layout.addWidget(self._create_field_group(
            "Warranty (Months)",
            self._create_warranty_input()
        ), 0, 0)
        
        layout.addWidget(self._create_field_group(
            "Track Serial Numbers",
            self._create_serial_number_combo()
        ), 0, 1)
        
        # Empty placeholder for alignment
        empty_widget = QWidget()
        empty_widget.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(empty_widget, 0, 2)
        
        # Row 1: Description (spans all 3 columns)
        desc_group = self._create_field_group(
            "Description",
            self._create_description_input()
        )
        layout.addWidget(desc_group, 1, 0, 1, 3)
        
        return widget
    
    # === Input Field Creators ===
    
    def _create_name_input(self) -> DialogInput:
        self.name_input = DialogInput("Enter item name")
        self.name_input.setToolTip("Enter the product/service name (will be converted to uppercase)")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.textChanged.connect(lambda text: to_upper(self.name_input, text))
        return self.name_input
    
    def _create_hsn_input(self) -> DialogInput:
        self.hsn_code = DialogInput("Enter HSN code")
        self.hsn_code.setToolTip("HSN (Harmonized System of Nomenclature) code: 4, 6, or 8 digits for goods classification")
        return self.hsn_code
    
    def _create_barcode_input(self) -> DialogInput:
        self.barcode_input = DialogInput("Enter barcode or SKU")
        self.barcode_input.setToolTip("Product barcode or Stock Keeping Unit (SKU) for inventory tracking")
        return self.barcode_input
    
    def _create_type_combo(self) -> DialogComboBox:
        self.type_combo = DialogComboBox(["Goods", "Service"])
        self.type_combo.setToolTip("Select 'Goods' for physical products or 'Service' for services")
        return self.type_combo
    
    def _create_category_input(self) -> DialogEditableComboBox:
        # Get existing categories from database
        existing_categories = db.get_product_categories()
        self.category_input = DialogEditableComboBox(
            items=existing_categories,
            placeholder="Select or type new category",
            auto_upper=True
        )
        self.category_input.setToolTip("Product category for grouping and filtering (type to create new)")
        return self.category_input
    
    def _create_unit_combo(self) -> DialogComboBox:
        self.unit_combo = DialogComboBox(["PCS", "KG", "LTR", "BOX", "MTR", "SET"])
        return self.unit_combo
    
    def _create_selling_price_input(self) -> DialogDoubleSpinBox:
        self.selling_price = DialogDoubleSpinBox(0, 9999999.99, 2)
        self.selling_price.setPrefix("₹ ")
        self.selling_price.valueChanged.connect(self._on_selling_price_changed)
        return self.selling_price
    
    def _create_purchase_price_input(self) -> DialogDoubleSpinBox:
        self.purchase_price = DialogDoubleSpinBox(0, 9999999.99, 2)
        self.purchase_price.setPrefix("₹ ")
        return self.purchase_price
    
    def _create_mrp_input(self) -> DialogDoubleSpinBox:
        self.mrp = DialogDoubleSpinBox(0, 9999999.99, 2)
        self.mrp.setPrefix("₹ ")
        self.mrp.setToolTip("Maximum Retail Price - the maximum price at which the product can be sold")
        return self.mrp
    
    def _create_gst_registered_checkbox(self) -> QWidget:
        """Create GST Registered checkbox"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        self.gst_registered_checkbox = DialogCheckBox("GST Registered")
        self.gst_registered_checkbox.setChecked(False)
        self.gst_registered_checkbox.setToolTip("Check this if GST applies to this product. Enables GST rate fields.")
        self.gst_registered_checkbox.stateChanged.connect(self._on_gst_registered_changed)
        layout.addWidget(self.gst_registered_checkbox)
        layout.addStretch()
        
        return container
    
    def _on_gst_registered_changed(self, state: int):
        """Handle GST Registered checkbox state change"""
        is_checked = state == Qt.Checked.value
        self._update_gst_fields_state(is_checked)
    
    def _update_gst_fields_state(self, enabled: bool):
        """Update GST, SGST, CGST fields read-only state"""
        # Use the widget's set_readonly method
        self.tax_rate.set_readonly(not enabled)
        self.sgst_input.set_readonly(not enabled)
        self.cgst_input.set_readonly(not enabled)
        
        # Enable/disable quick GST rate buttons
        if hasattr(self, 'quick_gst_container'):
            self.quick_gst_container.setEnabled(enabled)
            # Update opacity to show disabled state
            self.quick_gst_container.setStyleSheet(
                f"background: transparent; border: none; opacity: {'1' if enabled else '0.5'};"
            )
            for btn in self.gst_rate_buttons.values():
                btn.setEnabled(enabled)
        
        if enabled:
            # Set default GST values when enabled (if currently 0)
            if self.tax_rate.value() == 0:
                self.tax_rate.setValue(18.0)
                self.sgst_input.setValue(9.0)
                self.cgst_input.setValue(9.0)
                # Highlight the 18% button
                self._update_gst_rate_button_styles(18)
        else:
            # Reset values to 0 when disabled
            self.tax_rate.setValue(0)
            self.sgst_input.setValue(0)
            self.cgst_input.setValue(0)
            # Clear button highlights
            if hasattr(self, 'gst_rate_buttons'):
                self._update_gst_rate_button_styles(None)

    def _create_tax_rate_input(self) -> DialogDoubleSpinBox:
        self.tax_rate = DialogDoubleSpinBox(0, 100, 2)
        self.tax_rate.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.tax_rate.setSuffix(" %")
        self.tax_rate.setToolTip("Total GST rate (will auto-split into SGST and CGST). Common rates: 5%, 12%, 18%, 28%")
        self.tax_rate.valueChanged.connect(self._on_gst_changed)
        return self.tax_rate
    
    def _create_sgst_input(self) -> DialogDoubleSpinBox:
        self.sgst_input = DialogDoubleSpinBox(0, 100, 2)
        self.sgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.sgst_input.setSuffix(" %")
        self.sgst_input.setToolTip("State GST - automatically calculated as half of total GST rate")
        return self.sgst_input
    
    def _create_cgst_input(self) -> DialogDoubleSpinBox:
        self.cgst_input = DialogDoubleSpinBox(0, 100, 2)
        self.cgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.cgst_input.setSuffix(" %")
        self.cgst_input.setToolTip("Central GST - automatically calculated as half of total GST rate")
        return self.cgst_input
    
    def _create_discount_input(self) -> DialogDoubleSpinBox:
        self.discount_input = DialogDoubleSpinBox(0, 100, 2)
        self.discount_input.setSuffix(" %")
        self.discount_input.setToolTip("Default discount percentage to apply when adding this product to invoices")
        return self.discount_input
    
    def _create_opening_stock_input(self) -> DialogSpinBox:
        self.opening_stock = DialogSpinBox(0, 9999999)
        self.opening_stock.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        self.opening_stock.setToolTip("Initial stock quantity when adding product. This becomes current stock.")
        return self.opening_stock
    
    def _create_low_stock_input(self) -> DialogSpinBox:
        self.low_stock_alert = DialogSpinBox(0, 9999999)
        self.low_stock_alert.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        self.low_stock_alert.setToolTip("Alert threshold - shows 'Low Stock' warning when stock falls below this level")
        return self.low_stock_alert
    
    def _create_warranty_input(self) -> DialogSpinBox:
        self.warranty_input = DialogSpinBox(0, 120)
        self.warranty_input.setValue(0)
        self.warranty_input.setSpecialValueText("No Warranty")
        self.warranty_input.setSuffix(" months")
        self.warranty_input.setToolTip("Warranty period in months (0 = No Warranty)")
        return self.warranty_input
    
    def _create_serial_number_combo(self) -> DialogComboBox:
        self.has_serial_number = DialogComboBox(["No", "Yes"])
        self.has_serial_number.setToolTip("If Yes, serial numbers will be required when creating purchase invoices")
        return self.has_serial_number
    
    def _create_description_input(self) -> DialogTextEdit:
        self.description_input = DialogTextEdit("Enter product description (optional)", 80)
        self.description_input.setToolTip("Additional details about the product (specifications, notes, etc.)")
        return self.description_input
    
    # === Helper Methods ===
    
    def _on_gst_changed(self, value: float):
        sgst, cgst = self.product_service.calculate_split_gst(value)
        self.sgst_input.blockSignals(True)
        self.cgst_input.blockSignals(True)
        self.sgst_input.setValue(sgst)
        self.cgst_input.setValue(cgst)
        self.sgst_input.blockSignals(False)
        self.cgst_input.blockSignals(False)
        
        # Update quick GST rate button styles
        # Highlight the button if value matches a preset rate
        if value in QUICK_GST_RATES:
            self._update_gst_rate_button_styles(value)
        else:
            self._update_gst_rate_button_styles(None)  # Clear all highlights
    
    def _on_name_changed(self, text: str):
        self._form_modified = True
        if text and text.strip():
            set_name_error_state(self.name_input, False)
    
    def _on_selling_price_changed(self, value: float):
        self._form_modified = True
        valid, error = self.product_service.validate_selling_price(value)
        if not valid:
            set_price_error_state(self.selling_price, True)
    
    def populate_form(self):
        """Populate form with existing product data"""
        data = self.product_data
        
        # Basic info
        self.name_input.setText(data.get('name', ''))
        self.hsn_code.setText(data.get('hsn_code', ''))
        self.barcode_input.setText(data.get('barcode', ''))
        
        type_index = self.type_combo.findText(data.get('product_type', 'Goods'))
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.category_input.setText(data.get('category', ''))
        
        unit_index = self.unit_combo.findText(data.get('unit', 'PCS'))
        if unit_index >= 0:
            self.unit_combo.setCurrentIndex(unit_index)
        
        # Pricing
        self.selling_price.setValue(data.get('sales_rate', 0) or data.get('selling_price', 0))
        self.purchase_price.setValue(data.get('purchase_rate', 0) or data.get('purchase_price', 0))
        self.mrp.setValue(data.get('mrp', 0))
        self.discount_input.setValue(data.get('discount_percent', 0) or data.get('discount', 0))
        
        # GST fields - use stored is_gst_registered flag, fallback to checking values
        is_gst_registered = data.get('is_gst_registered', 0)
        if not is_gst_registered:
            # Fallback: check if product has tax rate > 0
            tax_rate_value = data.get('tax_rate', 0)
            sgst_value = data.get('sgst_rate', 0) or data.get('sgst', 0)
            cgst_value = data.get('cgst_rate', 0) or data.get('cgst', 0)
            is_gst_registered = tax_rate_value > 0 or sgst_value > 0 or cgst_value > 0
        
        # Set checkbox state first (this will enable/disable the fields)
        self.gst_registered_checkbox.setChecked(bool(is_gst_registered))
        
        # Then set the values
        tax_rate_value = data.get('tax_rate', 0)
        self.tax_rate.setValue(tax_rate_value)
        self.sgst_input.setValue(data.get('sgst_rate', 0) or data.get('sgst', 0))
        self.cgst_input.setValue(data.get('cgst_rate', 0) or data.get('cgst', 0))
        
        # Update quick GST rate button highlights
        if tax_rate_value in QUICK_GST_RATES:
            self._update_gst_rate_button_styles(tax_rate_value)
        
        # Stock fields - use stored track_stock flag, fallback to checking values
        is_track_stock = data.get('track_stock', 0)
        opening_stock_value = int(data.get('opening_stock', 0) or data.get('stock_quantity', 0))
        low_stock_value = int(data.get('low_stock', 0) or data.get('low_stock_alert', 0))
        if not is_track_stock:
            # Fallback: check if product has stock values > 0
            is_track_stock = opening_stock_value > 0 or low_stock_value > 0
        
        # Set checkbox state first (this will enable/disable the fields)
        self.track_stock_checkbox.setChecked(bool(is_track_stock))
        
        # Then set the values
        self.opening_stock.setValue(opening_stock_value)
        self.low_stock_alert.setValue(low_stock_value)
        
        # Additional
        self.warranty_input.setValue(data.get('warranty_months', 0))
        has_serial = data.get('has_serial_number', 0)
        self.has_serial_number.setCurrentIndex(1 if has_serial else 0)
        self.description_input.setPlainText(data.get('description', ''))
        
        # Reset form modified flag after population
        self._form_modified = False
    
    def _on_save(self):
        """Save product data using ProductService with UIErrorHandler"""
        validation_errors = []
        
        # Validate product name
        name = self.name_input.text().strip()
        if not self.product_service.validate_product_name(name):
            set_name_error_state(self.name_input, True)
            validation_errors.append("Product name is required")
        else:
            set_name_error_state(self.name_input, False)
        
        # Validate selling price
        selling_price = self.selling_price.value()
        valid, error = self.product_service.validate_selling_price(selling_price)
        if not valid:
            set_price_error_state(self.selling_price, True)
            validation_errors.append(error)
        else:
            set_price_error_state(self.selling_price, False)
        
        # Validate HSN code if provided
        hsn_code = self.hsn_code.text().strip()
        if hsn_code and not validate_hsn_code(hsn_code):
            set_field_error_state(self.hsn_code, True, "HSN code must be 4, 6, or 8 digits")
            validation_errors.append("HSN code must be 4, 6, or 8 digits")
        else:
            set_field_error_state(self.hsn_code, False)
        
        # Validate MRP >= Sales Rate if MRP is provided
        mrp = self.mrp.value()
        if mrp > 0 and mrp < selling_price:
            set_field_error_state(self.mrp, True, "MRP should be >= Sales Rate")
            validation_errors.append("MRP should be greater than or equal to Sales Rate")
        else:
            if hasattr(self.mrp, 'set_error'):
                self.mrp.set_error(False)
        
        # Validate Purchase Rate <= Sales Rate (margin check)
        purchase_price = self.purchase_price.value()
        if purchase_price > 0 and purchase_price > selling_price:
            UIErrorHandler.show_warning(
                "Margin Warning",
                "Purchase rate is higher than sales rate. This will result in a loss."
            )
        
        # Show all validation errors at once
        if validation_errors:
            self.name_input.setFocus() if not name else self.selling_price.setFocus()
            UIErrorHandler.show_validation_error(
                "Validation Error",
                validation_errors
            )
            return
        
        # Check for duplicate product (same name in same company)
        product_id = self.product_data['id'] if self.product_data else None
        if self.product_service.check_duplicate_product(name, product_id):
            set_name_error_state(self.name_input, True)
            UIErrorHandler.show_validation_error(
                "Duplicate Product",
                [f"A product with name '{name}' already exists"]
            )
            return
        
        # Check for duplicate barcode if provided
        barcode = self.barcode_input.text().strip()
        if barcode and self.product_service.check_duplicate_barcode(barcode, product_id):
            set_field_error_state(self.barcode_input, True, "Barcode already exists")
            UIErrorHandler.show_validation_error(
                "Duplicate Barcode",
                [f"A product with barcode '{barcode}' already exists"]
            )
            return
        
        # Get checkbox states
        is_gst_registered = 1 if self.gst_registered_checkbox.isChecked() else 0
        track_stock = 1 if self.track_stock_checkbox.isChecked() else 0
        
        # Prepare product data using service
        product_data = self.product_service.prepare_product_data(
            name=name,
            hsn_code=self.hsn_code.text().strip(),
            barcode=self.barcode_input.text().strip(),
            unit=self.unit_combo.currentText(),
            sales_rate=selling_price,
            purchase_rate=self.purchase_price.value(),
            discount_percent=self.discount_input.value(),
            mrp=self.mrp.value(),
            tax_rate=self.tax_rate.value(),
            sgst_rate=self.sgst_input.value(),
            cgst_rate=self.cgst_input.value(),
            opening_stock=self.opening_stock.value(),
            low_stock=self.low_stock_alert.value(),
            product_type=self.type_combo.currentText(),
            category=self.category_input.text().strip(),
            description=self.description_input.toPlainText().strip(),
            warranty_months=self.warranty_input.value(),
            has_serial_number=1 if self.has_serial_number.currentText() == "Yes" else 0,
            is_gst_registered=is_gst_registered,
            track_stock=track_stock,
            product_id=self.product_data['id'] if self.product_data else None
        )
        
        # Save using service
        is_update = self.product_data is not None
        action = "update" if is_update else "create"
        logger.info(f"Attempting to {action} product: {name}")
        
        # Disable buttons during save
        self._set_saving_state(True)
        
        try:
            success, message = self.product_service.save_product(product_data, is_update)
            
            if success:
                logger.info(f"Product {action}d successfully: {name}")
                UIErrorHandler.show_success("Success", message)
                self.accept()
            else:
                logger.error(f"Failed to {action} product: {name} - {message}")
                UIErrorHandler.show_error("Error", message)
        finally:
            # Re-enable buttons
            self._set_saving_state(False)

