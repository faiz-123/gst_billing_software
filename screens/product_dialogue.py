"""
Product dialog module (moved from products.py to avoid circular imports)
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QDialog, QMessageBox,
    QFormLayout, QLineEdit, QComboBox, QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
    QScrollArea, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER
)
from database import db


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Add Product" if not product_data else "Edit Product")
        self.setModal(True)
        # Dynamic sizing based on screen
        if parent:
            screen_rect = parent.geometry()
            width = min(1300, int(screen_rect.width() * 0.85))
            height = min(1000, int(screen_rect.height() * 0.9))
            self.resize(width, height)
        else:
            self.resize(1300, 1000)
        self.setMinimumSize(800, 600)
        self.build_ui()
    
    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for the entire content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {BACKGROUND}; border: none;")
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(40, 30, 40, 30)
        self.scroll_layout.setSpacing(24)
        
        # Header
        title_text = "Edit Product" if self.product_data else "Add New Product"
        title = QLabel(title_text)
        title.setFont(QFont("Arial", 24, QFont.Bold))
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
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
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
        self.stock_link.setFont(QFont("Arial", 13))
        self.stock_link.setCursor(Qt.PointingHandCursor)
        self.stock_link.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                background: transparent;
                padding: 8px 0;
            }}
            QLabel:hover {{
                color: {PRIMARY_HOVER};
            }}
        """)
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
        self.additional_link.setFont(QFont("Arial", 13))
        self.additional_link.setCursor(Qt.PointingHandCursor)
        self.additional_link.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY};
                background: transparent;
                padding: 8px 0;
            }}
            QLabel:hover {{
                color: {PRIMARY_HOVER};
            }}
        """)
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
        section.setStyleSheet(f"""
            QFrame#sectionFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Section title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
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
        
        self.track_stock_checkbox = QCheckBox("Track Stock")
        self.track_stock_checkbox.setChecked(False)
        self.track_stock_checkbox.setFont(QFont("Arial", 12))
        self.track_stock_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRIMARY};
                font-weight: 600;
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {BORDER};
                border-radius: 4px;
                background: {WHITE};
            }}
            QCheckBox::indicator:checked {{
                background: {PRIMARY};
                border-color: {PRIMARY};
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
            }}
            QCheckBox::indicator:hover {{
                border-color: {PRIMARY};
            }}
        """)
        self.track_stock_checkbox.stateChanged.connect(self._on_track_stock_changed)
        layout.addWidget(self.track_stock_checkbox)
        layout.addStretch()
        
        return container
    
    def _on_track_stock_changed(self, state: int):
        """Handle Track Stock checkbox state change"""
        is_checked = state == Qt.Checked
        self._update_stock_fields_state(is_checked)
    
    def _update_stock_fields_state(self, enabled: bool):
        """Update Opening Stock and Low Stock Alert fields read-only state"""
        # Set read-only state
        self.opening_stock.setReadOnly(not enabled)
        self.low_stock_alert.setReadOnly(not enabled)
        
        # Update styling based on state
        if enabled:
            # Editable style
            self.opening_stock.setStyleSheet(self._input_style())
            self.low_stock_alert.setStyleSheet(self._input_style())
        else:
            # Read-only style
            readonly_style = self._readonly_input_style()
            self.opening_stock.setStyleSheet(readonly_style)
            self.low_stock_alert.setStyleSheet(readonly_style)
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
    
    def _create_field_group(self, label_text: str, input_widget: QWidget) -> QWidget:
        """Create a field group with label and input"""
        group = QWidget()
        group.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setTextFormat(Qt.RichText)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; border: none; background: transparent;")
        layout.addWidget(label)
        
        layout.addWidget(input_widget)
        
        return group
    
    def _build_footer(self) -> QFrame:
        """Build the footer with action buttons"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-top: 1px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(40, 0, 40, 0)
        
        layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(120, 44)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: 2px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
                border-color: {TEXT_SECONDARY};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addSpacing(12)
        
        save_btn = QPushButton("Save Product")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(140, 44)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {PRIMARY_HOVER};
            }}
        """)
        save_btn.clicked.connect(self.save_product)
        layout.addWidget(save_btn)
        
        return footer
    
    # === Input Field Creators ===
    
    def _create_name_input(self) -> QLineEdit:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name")
        self.name_input.setStyleSheet(self._input_style())
        self.name_input.setFixedHeight(44)
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.textChanged.connect(lambda text: self._to_upper(self.name_input, text))
        return self.name_input
    
    def _create_hsn_input(self) -> QLineEdit:
        self.hsn_code = QLineEdit()
        self.hsn_code.setPlaceholderText("Enter HSN code")
        self.hsn_code.setStyleSheet(self._input_style())
        self.hsn_code.setFixedHeight(44)
        return self.hsn_code
    
    def _create_barcode_input(self) -> QLineEdit:
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Enter barcode or SKU")
        self.barcode_input.setStyleSheet(self._input_style())
        self.barcode_input.setFixedHeight(44)
        return self.barcode_input
    
    def _create_type_combo(self) -> QComboBox:
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Goods", "Service"])
        self.type_combo.setStyleSheet(self._input_style())
        self.type_combo.setFixedHeight(44)
        return self.type_combo
    
    def _create_category_input(self) -> QLineEdit:
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., Electronics, Clothing")
        self.category_input.setStyleSheet(self._input_style())
        self.category_input.setFixedHeight(44)
        self.category_input.textChanged.connect(lambda text: self._to_upper(self.category_input, text))
        return self.category_input
    
    def _create_unit_combo(self) -> QComboBox:
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["PCS", "KG", "LTR", "BOX", "MTR", "SET"])
        self.unit_combo.setStyleSheet(self._input_style())
        self.unit_combo.setFixedHeight(44)
        return self.unit_combo
    
    def _create_selling_price_input(self) -> QDoubleSpinBox:
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 9999999.99)
        self.selling_price.setDecimals(2)
        self.selling_price.setPrefix("₹ ")
        self.selling_price.setStyleSheet(self._input_style())
        self.selling_price.setFixedHeight(44)
        self.selling_price.valueChanged.connect(self._on_selling_price_changed)
        return self.selling_price
    
    def _create_purchase_price_input(self) -> QDoubleSpinBox:
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 9999999.99)
        self.purchase_price.setDecimals(2)
        self.purchase_price.setPrefix("₹ ")
        self.purchase_price.setStyleSheet(self._input_style())
        self.purchase_price.setFixedHeight(44)
        return self.purchase_price
    
    def _create_mrp_input(self) -> QDoubleSpinBox:
        self.mrp = QDoubleSpinBox()
        self.mrp.setRange(0, 9999999.99)
        self.mrp.setDecimals(2)
        self.mrp.setPrefix("₹ ")
        self.mrp.setStyleSheet(self._input_style())
        self.mrp.setFixedHeight(44)
        return self.mrp
    
    def _create_gst_registered_checkbox(self) -> QWidget:
        """Create GST Registered checkbox"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        self.gst_registered_checkbox = QCheckBox("GST Registered")
        self.gst_registered_checkbox.setChecked(False)
        self.gst_registered_checkbox.setFont(QFont("Arial", 12))
        self.gst_registered_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRIMARY};
                font-weight: 600;
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {BORDER};
                border-radius: 4px;
                background: {WHITE};
            }}
            QCheckBox::indicator:checked {{
                background: {PRIMARY};
                border-color: {PRIMARY};
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
            }}
            QCheckBox::indicator:hover {{
                border-color: {PRIMARY};
            }}
        """)
        self.gst_registered_checkbox.stateChanged.connect(self._on_gst_registered_changed)
        layout.addWidget(self.gst_registered_checkbox)
        layout.addStretch()
        
        return container
    
    def _on_gst_registered_changed(self, state: int):
        """Handle GST Registered checkbox state change"""
        is_checked = state == Qt.Checked
        self._update_gst_fields_state(is_checked)
    
    def _update_gst_fields_state(self, enabled: bool):
        """Update GST, SGST, CGST fields read-only state"""
        # Set read-only state
        self.tax_rate.setReadOnly(not enabled)
        self.sgst_input.setReadOnly(not enabled)
        self.cgst_input.setReadOnly(not enabled)
        
        # Update styling based on state
        if enabled:
            # Editable style
            self.tax_rate.setStyleSheet(self._input_style())
            self.sgst_input.setStyleSheet(self._input_style())
            self.cgst_input.setStyleSheet(self._input_style())
            # Set default GST values when enabled (if currently 0)
            if self.tax_rate.value() == 0:
                self.tax_rate.setValue(18.0)
                self.sgst_input.setValue(9.0)
                self.cgst_input.setValue(9.0)
        else:
            # Read-only style
            readonly_style = self._readonly_input_style()
            self.tax_rate.setStyleSheet(readonly_style)
            self.sgst_input.setStyleSheet(readonly_style)
            self.cgst_input.setStyleSheet(readonly_style)
            # Reset values to 0 when disabled
            self.tax_rate.setValue(0)
            self.sgst_input.setValue(0)
            self.cgst_input.setValue(0)
    
    def _readonly_input_style(self) -> str:
        """Return style for read-only input fields"""
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                color: {TEXT_SECONDARY};
                background: {BACKGROUND};
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {TEXT_SECONDARY};
                margin-right: 10px;
            }}
        """

    def _create_tax_rate_input(self) -> QDoubleSpinBox:
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setDecimals(2)
        self.tax_rate.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.tax_rate.setSuffix(" %")
        self.tax_rate.setStyleSheet(self._input_style())
        self.tax_rate.setFixedHeight(44)
        self.tax_rate.valueChanged.connect(self._on_gst_changed)
        return self.tax_rate
    
    def _create_sgst_input(self) -> QDoubleSpinBox:
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setRange(0, 100)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.sgst_input.setSuffix(" %")
        self.sgst_input.setStyleSheet(self._input_style())
        self.sgst_input.setFixedHeight(44)
        return self.sgst_input
    
    def _create_cgst_input(self) -> QDoubleSpinBox:
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setRange(0, 100)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0)  # Default to 0, will be set when GST Registered is checked
        self.cgst_input.setSuffix(" %")
        self.cgst_input.setStyleSheet(self._input_style())
        self.cgst_input.setFixedHeight(44)
        return self.cgst_input
    
    def _create_discount_input(self) -> QDoubleSpinBox:
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix(" %")
        self.discount_input.setStyleSheet(self._input_style())
        self.discount_input.setFixedHeight(44)
        return self.discount_input
    
    def _create_opening_stock_input(self) -> QSpinBox:
        self.opening_stock = QSpinBox()
        self.opening_stock.setRange(0, 9999999)
        self.opening_stock.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        self.opening_stock.setStyleSheet(self._input_style())
        self.opening_stock.setFixedHeight(44)
        return self.opening_stock
    
    def _create_low_stock_input(self) -> QSpinBox:
        self.low_stock_alert = QSpinBox()
        self.low_stock_alert.setRange(0, 9999999)
        self.low_stock_alert.setValue(0)  # Default to 0, will be editable when Track Stock is checked
        self.low_stock_alert.setStyleSheet(self._input_style())
        self.low_stock_alert.setFixedHeight(44)
        return self.low_stock_alert
    
    def _create_warranty_input(self) -> QSpinBox:
        self.warranty_input = QSpinBox()
        self.warranty_input.setRange(0, 120)
        self.warranty_input.setValue(0)
        self.warranty_input.setStyleSheet(self._input_style())
        self.warranty_input.setFixedHeight(44)
        self.warranty_input.setSpecialValueText("No Warranty")
        self.warranty_input.setSuffix(" months")
        return self.warranty_input
    
    def _create_serial_number_combo(self) -> QComboBox:
        self.has_serial_number = QComboBox()
        self.has_serial_number.addItems(["No", "Yes"])
        self.has_serial_number.setStyleSheet(self._input_style())
        self.has_serial_number.setFixedHeight(44)
        self.has_serial_number.setToolTip("If Yes, serial numbers will be required when creating purchase invoices")
        return self.has_serial_number
    
    def _create_description_input(self) -> QTextEdit:
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description (optional)")
        self.description_input.setFixedHeight(80)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 10px 12px;
                color: {TEXT_PRIMARY};
                background: {WHITE};
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY};
            }}
        """)
        return self.description_input
    
    # === Helper Methods ===
    
    def _input_style(self) -> str:
        return f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                color: {TEXT_PRIMARY};
                background: {WHITE};
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {TEXT_SECONDARY};
                margin-right: 10px;
            }}
        """
    
    @staticmethod
    def _to_upper(edit: QLineEdit, text: str):
        upper = text.upper()
        if text != upper:
            cursor_pos = edit.cursorPosition()
            edit.blockSignals(True)
            edit.setText(upper)
            edit.setCursorPosition(cursor_pos)
            edit.blockSignals(False)
    
    def _on_gst_changed(self, value: float):
        half = round(value / 2, 2)
        self.sgst_input.blockSignals(True)
        self.cgst_input.blockSignals(True)
        self.sgst_input.setValue(half)
        self.cgst_input.setValue(half)
        self.sgst_input.blockSignals(False)
        self.cgst_input.blockSignals(False)
    
    def _on_name_changed(self, text: str):
        if text and text.strip():
            self._set_name_error_state(False)
    
    def _set_name_error_state(self, is_error: bool):
        if is_error:
            self.name_input.setStyleSheet(f"""
                QLineEdit {{
                    border: 2px solid {DANGER};
                    border-radius: 8px;
                    padding: 0 12px;
                    background: #fff5f5;
                    color: {TEXT_PRIMARY};
                    font-size: 14px;
                }}
            """)
            self.name_input.setToolTip("Item Name is required")
        else:
            self.name_input.setStyleSheet(self._input_style())
            self.name_input.setToolTip("")
    
    def _on_selling_price_changed(self, value: float):
        if value > 0:
            self._set_selling_price_error_state(False)
    
    def _set_selling_price_error_state(self, is_error: bool):
        if is_error:
            self.selling_price.setStyleSheet(f"""
                QDoubleSpinBox {{
                    border: 2px solid {DANGER};
                    border-radius: 8px;
                    padding: 0 12px;
                    background: #fff5f5;
                    color: {TEXT_PRIMARY};
                    font-size: 14px;
                }}
            """)
            self.selling_price.setToolTip("Selling price must be greater than 0")
        else:
            self.selling_price.setStyleSheet(self._input_style())
            self.selling_price.setToolTip("")
    
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
        """Save product data"""
        name = self.name_input.text().strip()
        if not name:
            self._set_name_error_state(True)
            self.name_input.setFocus()
            return
        
        selling_price = self.selling_price.value()
        if selling_price <= 0:
            self._set_selling_price_error_state(True)
            self.selling_price.setFocus()
            return
        
        hsn = self.hsn_code.text().strip() or None
        stock_qty = float(self.opening_stock.value())
        
        # Get checkbox states
        is_gst_registered = 1 if self.gst_registered_checkbox.isChecked() else 0
        track_stock = 1 if self.track_stock_checkbox.isChecked() else 0
        
        try:
            if self.product_data:  # Editing
                update_payload = {
                    'id': self.product_data['id'],
                    'name': name,
                    'hsn_code': hsn,
                    'barcode': self.barcode_input.text().strip() or None,
                    'unit': self.unit_combo.currentText(),
                    'sales_rate': float(selling_price),
                    'purchase_rate': float(self.purchase_price.value()),
                    'discount_percent': float(self.discount_input.value()),
                    'mrp': float(self.mrp.value()),
                    'tax_rate': self.tax_rate.value(),
                    'sgst_rate': self.sgst_input.value(),
                    'cgst_rate': self.cgst_input.value(),
                    'opening_stock': stock_qty,
                    'low_stock': float(self.low_stock_alert.value()),
                    'product_type': self.type_combo.currentText(),
                    'category': self.category_input.text().strip() or None,
                    'description': self.description_input.toPlainText().strip() or None,
                    'warranty_months': self.warranty_input.value(),
                    'has_serial_number': 1 if self.has_serial_number.currentText() == "Yes" else 0,
                    'is_gst_registered': is_gst_registered,
                    'track_stock': track_stock,
                }
                db.update_product(update_payload)
                QMessageBox.information(self, "Success", "Product updated successfully!")
            else:  # Adding new
                db.add_product(
                    name=name,
                    hsn_code=hsn,
                    barcode=self.barcode_input.text().strip() or None,
                    unit=self.unit_combo.currentText(),
                    sales_rate=float(selling_price),
                    purchase_rate=float(self.purchase_price.value()),
                    discount_percent=float(self.discount_input.value()),
                    mrp=float(self.mrp.value()),
                    tax_rate=self.tax_rate.value(),
                    sgst_rate=self.sgst_input.value(),
                    cgst_rate=self.cgst_input.value(),
                    opening_stock=stock_qty,
                    low_stock=float(self.low_stock_alert.value()),
                    product_type=self.type_combo.currentText(),
                    category=self.category_input.text().strip() or None,
                    description=self.description_input.toPlainText().strip() or None,
                    warranty_months=self.warranty_input.value(),
                    has_serial_number=1 if self.has_serial_number.currentText() == "Yes" else 0,
                    is_gst_registered=is_gst_registered,
                    track_stock=track_stock,
                )
                QMessageBox.information(self, "Success", "Product added successfully!")
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
    
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