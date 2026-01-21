"""
Product dialog module (moved from products.py to avoid circular imports)
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QWidget, QGridLayout, QTextEdit
)
from PySide6.QtCore import Qt

from theme import (
    # Colors (only those still needed for remaining inline styles)
    PRIMARY, TEXT_PRIMARY, BORDER,
    # Fonts
    get_title_font, get_section_title_font, get_link_font,
    # Styles
    get_section_frame_style, get_dialog_footer_style,
    get_cancel_button_style, get_save_button_style,
    get_link_label_style
)
from widgets import (
    DialogInput, DialogComboBox, DialogEditableComboBox, DialogSpinBox, DialogDoubleSpinBox,
    DialogCheckBox, DialogTextEdit, DialogFieldGroup, CustomButton, DialogScrollArea
)
from ui.base.base_dialog import BaseDialog
from ui.error_handler import UIErrorHandler
from core.services.product_service import ProductService
from core.validators import set_name_error_state, set_price_error_state
from core.core_utils import to_upper
from core.db.sqlite_db import db


class ProductDialog(BaseDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_data=None):
        self.product_data = product_data
        self.product_service = ProductService(db)
        super().__init__(
            parent=parent,
            title="Add Product" if not product_data else "Edit Product",
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
        main_layout.addWidget(self._build_footer())
        
        # Populate form if editing
        if self.product_data:
            self.populate_form()
    
    def _build_stock_link(self):
        """Create a hyperlink to show/hide stock & inventory section"""
        link_container = QWidget()
        link_container.setStyleSheet("background: transparent;")
        link_layout = QHBoxLayout(link_container)
        link_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stock_link = QLabel("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Stock & Inventory</a>".format(PRIMARY))
        self.stock_link.setTextFormat(Qt.RichText)
        self.stock_link.setFont(get_link_font())
        self.stock_link.setCursor(Qt.PointingHandCursor)
        self.stock_link.setStyleSheet(get_link_label_style())
        self.stock_link.mousePressEvent = self._toggle_stock_section
        link_layout.addWidget(self.stock_link)
        link_layout.addStretch()
        
        self.scroll_layout.addWidget(link_container)
    
    def _toggle_stock_section(self, event=None):
        """Show/hide stock & inventory section"""
        is_visible = self.stock_section.isVisible()
        self.stock_section.setVisible(not is_visible)
        
        if is_visible:
            self.stock_link.setText("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Stock & Inventory</a>".format(PRIMARY))
        else:
            self.stock_link.setText("➖ <a href='#' style='color: {0}; text-decoration: none;'>Hide Stock & Inventory</a>".format(PRIMARY))
    
    def _build_additional_link(self):
        """Create a hyperlink to show/hide additional details"""
        link_container = QWidget()
        link_container.setStyleSheet("background: transparent;")
        link_layout = QHBoxLayout(link_container)
        link_layout.setContentsMargins(0, 0, 0, 0)
        
        self.additional_link = QLabel("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Additional Information</a>".format(PRIMARY))
        self.additional_link.setTextFormat(Qt.RichText)
        self.additional_link.setFont(get_link_font())
        self.additional_link.setCursor(Qt.PointingHandCursor)
        self.additional_link.setStyleSheet(get_link_label_style())
        self.additional_link.mousePressEvent = self._toggle_additional_section
        link_layout.addWidget(self.additional_link)
        link_layout.addStretch()
        
        self.scroll_layout.addWidget(link_container)
    
    def _toggle_additional_section(self, event=None):
        """Show/hide additional details section"""
        is_visible = self.additional_section.isVisible()
        self.additional_section.setVisible(not is_visible)
        
        if is_visible:
            self.additional_link.setText("➕ <a href='#' style='color: {0}; text-decoration: none;'>Add Additional Information</a>".format(PRIMARY))
        else:
            self.additional_link.setText("➖ <a href='#' style='color: {0}; text-decoration: none;'>Hide Additional Information</a>".format(PRIMARY))
    
    def _create_section(self, title: str, content_widget: QWidget) -> QFrame:
        """Create a styled section card with title and content - matches products.py main frame style"""
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
        
        # Row 2: GST Rate, SGST, CGST
        layout.addWidget(self._create_field_group(
            "Tax Rate (GST) %",
            self._create_tax_rate_input()
        ), 2, 0)
        
        layout.addWidget(self._create_field_group(
            "SGST %",
            self._create_sgst_input()
        ), 2, 1)
        
        layout.addWidget(self._create_field_group(
            "CGST %",
            self._create_cgst_input()
        ), 2, 2)
        
        # Set initial read-only state for GST fields (checkbox is unchecked by default)
        self._update_gst_fields_state(False)
        
        return widget
    
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
        
        save_btn = CustomButton("Save Product", "primary")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(140, 44)
        save_btn.setStyleSheet(get_save_button_style())
        save_btn.clicked.connect(self.save_product)
        layout.addWidget(save_btn)
        
        return footer
    
    # === Input Field Creators ===
    
    def _create_name_input(self) -> DialogInput:
        self.name_input = DialogInput("Enter item name")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.textChanged.connect(lambda text: to_upper(self.name_input, text))
        return self.name_input
    
    def _create_hsn_input(self) -> DialogInput:
        self.hsn_code = DialogInput("Enter HSN code")
        return self.hsn_code
    
    def _create_barcode_input(self) -> DialogInput:
        self.barcode_input = DialogInput("Enter barcode or SKU")
        return self.barcode_input
    
    def _create_type_combo(self) -> DialogComboBox:
        self.type_combo = DialogComboBox(["Goods", "Service"])
        return self.type_combo
    
    def _create_category_input(self) -> DialogEditableComboBox:
        # Get existing categories from database
        existing_categories = db.get_product_categories()
        self.category_input = DialogEditableComboBox(
            items=existing_categories,
            placeholder="Select or type new category",
            auto_upper=True
        )
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
        
        if enabled:
            # Set default GST values when enabled (if currently 0)
            if self.tax_rate.value() == 0:
                self.tax_rate.setValue(18.0)
                self.sgst_input.setValue(9.0)
                self.cgst_input.setValue(9.0)
        else:
            # Reset values to 0 when disabled
            self.tax_rate.setValue(0)
            self.sgst_input.setValue(0)
            self.cgst_input.setValue(0)

    def _create_tax_rate_input(self) -> DialogDoubleSpinBox:
        self.tax_rate = DialogDoubleSpinBox(0, 100, 2)
        self.tax_rate.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.tax_rate.setSuffix(" %")
        self.tax_rate.valueChanged.connect(self._on_gst_changed)
        return self.tax_rate
    
    def _create_sgst_input(self) -> DialogDoubleSpinBox:
        self.sgst_input = DialogDoubleSpinBox(0, 100, 2)
        self.sgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.sgst_input.setSuffix(" %")
        return self.sgst_input
    
    def _create_cgst_input(self) -> DialogDoubleSpinBox:
        self.cgst_input = DialogDoubleSpinBox(0, 100, 2)
        self.cgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.cgst_input.setSuffix(" %")
        return self.cgst_input
    
    def _create_discount_input(self) -> DialogDoubleSpinBox:
        self.discount_input = DialogDoubleSpinBox(0, 100, 2)
        self.discount_input.setSuffix(" %")
        return self.discount_input
    
    def _create_opening_stock_input(self) -> DialogSpinBox:
        self.opening_stock = DialogSpinBox(0, 9999999)
        self.opening_stock.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        return self.opening_stock
    
    def _create_low_stock_input(self) -> DialogSpinBox:
        self.low_stock_alert = DialogSpinBox(0, 9999999)
        self.low_stock_alert.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        return self.low_stock_alert
    
    def _create_warranty_input(self) -> DialogSpinBox:
        self.warranty_input = DialogSpinBox(0, 120)
        self.warranty_input.setValue(0)
        self.warranty_input.setSpecialValueText("No Warranty")
        self.warranty_input.setSuffix(" months")
        return self.warranty_input
    
    def _create_serial_number_combo(self) -> DialogComboBox:
        self.has_serial_number = DialogComboBox(["No", "Yes"])
        self.has_serial_number.setToolTip("If Yes, serial numbers will be required when creating purchase invoices")
        return self.has_serial_number
    
    def _create_description_input(self) -> DialogTextEdit:
        self.description_input = DialogTextEdit("Enter product description (optional)", 80)
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
    
    def _on_name_changed(self, text: str):
        if text and text.strip():
            set_name_error_state(self.name_input, False)
    
    def _on_selling_price_changed(self, value: float):
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
        self.tax_rate.setValue(data.get('tax_rate', 0))
        self.sgst_input.setValue(data.get('sgst_rate', 0) or data.get('sgst', 0))
        self.cgst_input.setValue(data.get('cgst_rate', 0) or data.get('cgst', 0))
        
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
    
    def save_product(self):
        """Save product data using ProductService with UIErrorHandler"""
        name = self.name_input.text().strip()
        if not self.product_service.validate_product_name(name):
            set_name_error_state(self.name_input, True)
            self.name_input.setFocus()
            UIErrorHandler.show_validation_error(
                "Validation Error",
                ["Product name is required"]
            )
            return
        
        selling_price = self.selling_price.value()
        valid, error = self.product_service.validate_selling_price(selling_price)
        if not valid:
            set_price_error_state(self.selling_price, True)
            self.selling_price.setFocus()
            UIErrorHandler.show_validation_error(
                "Validation Error",
                [error]
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
        success, message = self.product_service.save_product(product_data, is_update)
        
        if success:
            UIErrorHandler.show_success("Success", message)
            self.accept()
        else:
            UIErrorHandler.show_error("Error", message)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts: Enter to save, Escape to cancel."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not isinstance(self.focusWidget(), QTextEdit):
                self.save_product()
                return
        elif event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

