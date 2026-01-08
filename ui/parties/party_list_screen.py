"""
Parties screen - Manage customers and suppliers with enhanced UI and functionality
Responsive design with modern card-based layout (similar to invoices.py)
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QAbstractItemView, QSizePolicy, QToolButton, QApplication
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QColor

from ui.base.base_screen import BaseScreen
from widgets import CustomTable
from theme import (
    SUCCESS, DANGER, PRIMARY, WARNING, WHITE, TEXT_PRIMARY,
    BORDER, BACKGROUND, TEXT_SECONDARY, PRIMARY_HOVER
)
from core.db.sqlite_db import db
from ui.parties.party_form_dialog import PartyDialog, BankAccountDialog


class PartiesScreen(BaseScreen):
    """Enhanced Parties screen with modern responsive UI"""

    def __init__(self):
        super().__init__("👥 Parties Management")
        self.all_parties_data = []
        self.current_page = 1
        self._initialized = False
        self.setup_parties_screen()

    def showEvent(self, event):
        """Called when the screen becomes visible - refresh data"""
        super().showEvent(event)
        # Load data when screen becomes visible
        if not self._initialized:
            QTimer.singleShot(0, self.load_parties_data)
            self._initialized = True

    def setup_parties_screen(self):
        """Setup enhanced parties screen content"""
        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header section with search and actions
        self.setup_header_section(content_layout)

        # Stats cards row
        self.setup_stats_section(content_layout)

        # Filters section
        self.setup_filters_section(content_layout)

        # Table section
        self.setup_table_section(content_layout)

        scroll_area.setWidget(content_widget)
        self.add_content(scroll_area)

    def setup_header_section(self, parent_layout):
        """Setup header with search and action buttons"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(16)

        # Search box with icon
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QFrame:focus-within {{
                border-color: {PRIMARY};
            }}
        """)
        search_frame.setMinimumWidth(250)
        search_frame.setMaximumWidth(400)
        search_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 8, 12, 8)
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 16px;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search parties...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {TEXT_PRIMARY};
                padding: 4px 0;
            }}
        """)
        self.search_input.textChanged.connect(self.filter_parties)
        search_layout.addWidget(self.search_input)

        header_layout.addWidget(search_frame)
        header_layout.addStretch()

        # Action buttons
        buttons_data = [
            ("📤 Export", "secondary", self.export_parties),
            ("📥 Import", "secondary", self.import_parties),
            ("➕ Add Party", "primary", self.add_party)
        ]

        for text, style, callback in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            if style == "primary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {PRIMARY};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 600;
                        padding: 8px 20px;
                    }}
                    QPushButton:hover {{
                        background: {PRIMARY_HOVER};
                    }}
                    QPushButton:pressed {{
                        background: #1D4ED8;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {WHITE};
                        color: {TEXT_PRIMARY};
                        border: 1px solid {BORDER};
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: {BACKGROUND};
                        border-color: {PRIMARY};
                        color: {PRIMARY};
                    }}
                """)

            header_layout.addWidget(btn)

        parent_layout.addWidget(header_frame)

    def setup_stats_section(self, parent_layout):
        """Setup statistics cards with responsive grid"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent; border: none;")
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        # Statistics cards data
        stats_data = [
            ("👥", "Total Parties", "0", PRIMARY, "total_parties_label"),
            ("🏢", "Customers", "0", SUCCESS, "customers_label"),
            ("🏭", "Suppliers", "0", WARNING, "suppliers_label"),
            ("📋", "GST Registered", "0", "#10B981", "gst_registered_label")
        ]

        for icon, label_text, value, color, attr_name in stats_data:
            card = self.create_stat_card(icon, label_text, value, color)
            setattr(self, attr_name, card.findChild(QLabel, "value_label"))
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_frame)

    def create_stat_card(self, icon, label_text, value, color):
        """Create modern statistics card"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(80)
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                border-color: {color};
                background: #FAFBFC;
            }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}20;
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px; border: none;")
        icon_layout.addWidget(icon_label)

        layout.addWidget(icon_container)

        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(4)

        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            border: none;
        """)
        text_container.addWidget(label_widget)

        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 22px;
            font-weight: 700;
            border: none;
        """)
        text_container.addWidget(value_label)

        layout.addLayout(text_container)
        layout.addStretch()

        return card

    def setup_filters_section(self, parent_layout):
        """Setup responsive filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        filters_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(16, 12, 16, 12)
        filters_layout.setSpacing(16)

        # Filter label
        filter_label = QLabel("🎯 Filters")
        filter_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 600;
            border: none;
        """)
        filters_layout.addWidget(filter_label)

        # Add separator
        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setFixedHeight(30)
        separator.setStyleSheet(f"background: {BORDER};")
        filters_layout.addWidget(separator)

        # Filter controls
        filter_controls = [
            ("Type", ["All", "Customer", "Supplier", "Both"], "type_filter"),
            ("GST Status", ["All", "Registered", "Unregistered"], "gst_filter"),
            ("Balance", ["All", "Receivable", "Payable", "Zero Balance"], "balance_filter")
        ]

        combo_style = f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                padding-right: 30px;
                background: {BACKGROUND};
                font-size: 13px;
                color: {TEXT_PRIMARY};
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {TEXT_SECONDARY};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {BORDER};
                background: {WHITE};
                selection-background-color: {PRIMARY};
                selection-color: white;
                outline: none;
            }}
        """

        self.filter_combos = {}

        for label_text, items, attr_name in filter_controls:
            # Container for label + combo
            filter_container = QVBoxLayout()
            filter_container.setSpacing(4)

            label = QLabel(label_text)
            label.setStyleSheet(f"""
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 500;
                border: none;
            """)
            filter_container.addWidget(label)

            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedHeight(32)
            combo.setStyleSheet(combo_style)
            combo.currentTextChanged.connect(self.filter_parties)
            setattr(self, attr_name, combo)
            self.filter_combos[attr_name] = combo
            filter_container.addWidget(combo)

            filters_layout.addLayout(filter_container)

        filters_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Refresh Data")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 14px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: white;
                border-color: {PRIMARY};
            }}
        """)
        refresh_btn.clicked.connect(self.load_parties_data)
        filters_layout.addWidget(refresh_btn)

        # Clear filters button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(32)
        clear_btn.setToolTip("Clear All Filters")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 13px;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                color: {DANGER};
            }}
        """)
        clear_btn.clicked.connect(self.clear_filters)
        filters_layout.addWidget(clear_btn)

        parent_layout.addWidget(filters_frame)

    def setup_table_section(self, parent_layout):
        """Setup responsive table with pagination"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_frame.setStyleSheet(f"""
            QFrame#tableFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(24, 20, 24, 20)
        table_layout.setSpacing(16)

        # Table header with title and count
        header_layout = QHBoxLayout()
        
        # Title with icon
        title_container = QHBoxLayout()
        title_container.setSpacing(10)
        
        title_icon = QLabel("👥")
        title_icon.setStyleSheet("border: none; font-size: 20px;")
        title_container.addWidget(title_icon)

        table_title = QLabel("Parties List")
        table_title.setFont(QFont("Arial", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        title_container.addWidget(table_title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)

        # Count badge
        self.count_label = QLabel("0 parties")
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                background: {BACKGROUND};
                padding: 6px 14px;
                border-radius: 16px;
                border: none;
            }}
        """)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()

        # Items per page
        items_label = QLabel("Show:")
        items_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; border: none;")
        header_layout.addWidget(items_label)

        self.items_per_page = QComboBox()
        self.items_per_page.addItems(["25", "50", "100", "200"])
        self.items_per_page.setCurrentText("50")
        self.items_per_page.setFixedWidth(70)
        self.items_per_page.setFixedHeight(28)
        self.items_per_page.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                background: {WHITE};
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.items_per_page.currentTextChanged.connect(self.on_items_per_page_changed)
        header_layout.addWidget(self.items_per_page)

        table_layout.addLayout(header_layout)

        # Create table using CustomTable
        headers = ["#", "Name", "Type", "Contact", "GST Status", "Balance", "Actions"]
        self.parties_table = CustomTable(0, len(headers), headers)
        self.parties_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Enhanced table styling (same as products.py)
        self.parties_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #F3F4F6;
                background-color: {WHITE};
                border: none;
                font-size: 14px;
                selection-background-color: #EEF2FF;
                alternate-background-color: #FAFBFC;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding: 14px 10px;
            }}
            QTableWidget::item:selected {{
                background-color: #EEF2FF;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {TEXT_SECONDARY};
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                padding: 14px 10px;
                font-size: 13px;
                text-transform: uppercase;
            }}
            QHeaderView::section:hover {{
                background-color: #F1F5F9;
            }}
        """)

        # Enable alternating row colors
        self.parties_table.setAlternatingRowColors(True)

        # Column widths using ratios (like products.py)
        # ["#", "Name", "Type", "Contact", "GST Status", "Balance", "Actions"]
        column_ratios = [0.05, 0.22, 0.10, 0.15, 0.18, 0.12, 0.18]
        for i, ratio in enumerate(column_ratios):
            self.parties_table.setColumnWidth(i, int(900 * ratio))

        # Row height
        self.parties_table.verticalHeader().setDefaultSectionSize(56)
        self.parties_table.setMinimumHeight(400)

        # Double-click to edit
        self.parties_table.itemDoubleClicked.connect(self.handle_double_click)

        table_layout.addWidget(self.parties_table)

        # Pagination footer
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {BACKGROUND};
                border: none;
                border-top: 1px solid {BORDER};
                border-radius: 0 0 12px 12px;
            }}
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(16, 10, 16, 10)

        self.pagination_info = QLabel("Showing 0 - 0 of 0 items")
        self.pagination_info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; border: none;")
        pagination_layout.addWidget(self.pagination_info)

        pagination_layout.addStretch()

        # Pagination controls
        btn_style = f"""
            QPushButton {{
                background: {WHITE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {BACKGROUND};
                border-color: {PRIMARY};
            }}
            QPushButton:disabled {{
                color: {BORDER};
                background: {BACKGROUND};
            }}
        """

        self.prev_page_btn = QPushButton("← Previous")
        self.prev_page_btn.setFixedHeight(32)
        self.prev_page_btn.setStyleSheet(btn_style)
        self.prev_page_btn.setCursor(Qt.PointingHandCursor)
        self.prev_page_btn.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_page_btn)

        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 500; padding: 0 12px; border: none;")
        pagination_layout.addWidget(self.page_info)

        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.setFixedHeight(32)
        self.next_page_btn.setStyleSheet(btn_style)
        self.next_page_btn.setCursor(Qt.PointingHandCursor)
        self.next_page_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_page_btn)

        table_layout.addWidget(pagination_frame)

        parent_layout.addWidget(table_frame)

    def load_parties_data(self):
        """Load parties data into table"""
        try:
            parties = db.get_parties()
            self.all_parties_data = parties
            self.current_page = 1
            self.apply_filters_and_display()
        except Exception as e:
            print(f"Error loading parties: {e}")
            self.all_parties_data = []
            self.populate_table([])
            self.update_stats([])
            QMessageBox.information(
                self,
                "Database Info",
                f"Unable to load parties from database.\n\nError: {str(e)}\n\nPlease check your database connection."
            )

    def on_items_per_page_changed(self):
        """Handle items per page change"""
        self.current_page = 1
        self.apply_filters_and_display()

    def apply_filters_and_display(self):
        """Apply current filters and display data"""
        filtered_data = self.get_filtered_data()
        self.populate_table(filtered_data)
        self.update_stats(filtered_data)

    def get_filtered_data(self):
        """Get filtered data based on current filter settings"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        gst_filter = self.gst_filter.currentText()
        balance_filter = self.balance_filter.currentText()

        filtered_data = []
        for party in self.all_parties_data:
            # Search filter
            if search_text:
                searchable = f"{party.get('name', '')} {party.get('phone', '')} {party.get('email', '')} {party.get('gst_number', '')}".lower()
                if search_text not in searchable:
                    continue

            # Type filter
            if type_filter != "All" and party.get('party_type', '') != type_filter:
                continue

            # GST filter
            if gst_filter == "Registered" and not party.get('gst_number'):
                continue
            elif gst_filter == "Unregistered" and party.get('gst_number'):
                continue

            # Balance filter
            balance = float(party.get('opening_balance', 0))
            if balance_filter == "Receivable" and balance <= 0:
                continue
            elif balance_filter == "Payable" and balance >= 0:
                continue
            elif balance_filter == "Zero Balance" and balance != 0:
                continue

            filtered_data.append(party)

        return filtered_data

    def populate_table(self, parties_data):
        """Populate table with parties data"""
        # Apply pagination
        items_per_page = int(self.items_per_page.currentText())
        total_items = len(parties_data)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        # Ensure current page is valid
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        paginated_data = parties_data[start_idx:end_idx]

        self.parties_table.setRowCount(len(paginated_data))

        for row, party in enumerate(paginated_data):
            # Column 0: Row number
            self.parties_table.setItem(row, 0, self.parties_table.create_item(str(start_idx + row + 1), Qt.AlignCenter))

            # Column 1: Party name
            name_item = self.parties_table.create_item(party.get('name', ''))
            name_item.setFont(QFont("Arial", 12, QFont.Bold))
            self.parties_table.setItem(row, 1, name_item)

            # Column 2: Type with color coding
            party_type = party.get('party_type', '')
            type_icon = "🏢" if party_type == "Customer" else "🏭" if party_type == "Supplier" else "🔄"
            type_item = self.parties_table.create_item(f"{type_icon} {party_type}", Qt.AlignCenter)

            type_colors = {
                'Customer': (SUCCESS, "#D1FAE5"),
                'Supplier': (WARNING, "#FEF3C7"),
                'Both': (PRIMARY, "#EBF8FF")
            }

            if party_type in type_colors:
                fg_color, bg_color = type_colors[party_type]
                type_item.setForeground(QColor(fg_color))
                type_item.setBackground(QColor(bg_color))

            self.parties_table.setItem(row, 2, type_item)

            # Column 3: Contact
            phone = party.get('phone', '')
            email = party.get('email', '')
            contact = phone if phone else email if email else "—"
            self.parties_table.setItem(row, 3, self.parties_table.create_item(contact, Qt.AlignCenter))

            # Column 4: GST Status
            gst_number = party.get('gst_number', '')
            if gst_number:
                gst_display = gst_number[:15] + ('...' if len(gst_number) > 15 else '')
                gst_item = self.parties_table.create_item(f"✅ {gst_display}", Qt.AlignCenter)
                gst_item.setForeground(QColor(SUCCESS))
            else:
                gst_item = self.parties_table.create_item("❌ Not Registered", Qt.AlignCenter)
                gst_item.setForeground(QColor(TEXT_SECONDARY))
            self.parties_table.setItem(row, 4, gst_item)

            # Column 5: Balance
            balance = float(party.get('opening_balance', 0))
            balance_text = f"₹{abs(balance):,.2f}"
            if balance > 0:
                balance_text += " Dr"
                balance_item = self.parties_table.create_item(balance_text, Qt.AlignRight | Qt.AlignVCenter)
                balance_item.setForeground(QColor(SUCCESS))
            elif balance < 0:
                balance_text += " Cr"
                balance_item = self.parties_table.create_item(balance_text, Qt.AlignRight | Qt.AlignVCenter)
                balance_item.setForeground(QColor(DANGER))
            else:
                balance_item = self.parties_table.create_item("₹0.00", Qt.AlignRight | Qt.AlignVCenter)
                balance_item.setForeground(QColor(TEXT_SECONDARY))
            balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.parties_table.setItem(row, 5, balance_item)

            # Column 6: Action buttons
            actions_widget = self.create_action_buttons(party)
            self.parties_table.setCellWidget(row, 6, actions_widget)

        self.update_pagination_info(total_items, parties_data)

    def create_action_buttons(self, party):
        """Create enhanced action buttons for each party row"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        widget.setFixedHeight(40)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # Action buttons
        actions = [
            ("Edit", "Edit Party", lambda _, p=party: self.edit_party(p), "#EEF2FF", PRIMARY),
            ("Del", "Delete Party", lambda _, p=party: self.delete_party(p), "#FEE2E2", DANGER)
        ]

        for text, tooltip, callback, bg_color, hover_color in actions:
            btn = QPushButton(text)
            btn.setFixedSize(42, 26)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    background: {bg_color};
                    font-size: 11px;
                    font-weight: 600;
                    color: {TEXT_PRIMARY};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: {hover_color};
                    border-color: {hover_color};
                    color: white;
                }}
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        return widget

    def update_stats(self, parties):
        """Update statistics cards"""
        total_count = len(parties)
        customers = sum(1 for p in parties if p.get('party_type') in ['Customer', 'Both'])
        suppliers = sum(1 for p in parties if p.get('party_type') in ['Supplier', 'Both'])
        gst_registered = sum(1 for p in parties if p.get('gst_number'))

        # Update labels
        if hasattr(self, 'total_parties_label') and self.total_parties_label:
            self.total_parties_label.setText(str(total_count))
        if hasattr(self, 'customers_label') and self.customers_label:
            self.customers_label.setText(str(customers))
        if hasattr(self, 'suppliers_label') and self.suppliers_label:
            self.suppliers_label.setText(str(suppliers))
        if hasattr(self, 'gst_registered_label') and self.gst_registered_label:
            self.gst_registered_label.setText(str(gst_registered))

    def update_pagination_info(self, total_items, filtered_data=None):
        """Update pagination information"""
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        start_item = (self.current_page - 1) * items_per_page + 1 if total_items > 0 else 0
        end_item = min(self.current_page * items_per_page, total_items)

        self.pagination_info.setText(f"Showing {start_item} - {end_item} of {total_items} items")
        self.page_info.setText(f"Page {self.current_page} of {total_pages}")

        # Update button states
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)

        # Update count label
        if filtered_data is not None and len(filtered_data) != len(self.all_parties_data):
            self.count_label.setText(f"Showing: {len(filtered_data)} of {len(self.all_parties_data)} parties")
        else:
            self.count_label.setText(f"Total: {len(self.all_parties_data)} parties")

    def filter_parties(self):
        """Filter parties based on search and filter criteria"""
        self.current_page = 1
        self.apply_filters_and_display()

    def clear_filters(self):
        """Clear all applied filters"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.gst_filter.setCurrentIndex(0)
        self.balance_filter.setCurrentIndex(0)
        self.current_page = 1
        self.apply_filters_and_display()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.apply_filters_and_display()

    def next_page(self):
        """Go to next page"""
        filtered_data = self.get_filtered_data()
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (len(filtered_data) + items_per_page - 1) // items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.apply_filters_and_display()

    def handle_double_click(self, item):
        """Handle double-click on party row - edit party"""
        row = item.row()
        # Get the actual index considering pagination
        items_per_page = int(self.items_per_page.currentText())
        actual_idx = (self.current_page - 1) * items_per_page + row
        filtered_data = self.get_filtered_data()
        if actual_idx < len(filtered_data):
            party = filtered_data[actual_idx]
            self.edit_party(party)

    def add_party(self):
        """Open add party dialog"""
        try:
            dialog = PartyDialog(self)
            dialog.setWindowTitle("➕ Add New Party")

            if dialog.exec_() == QDialog.Accepted:
                self.show_success_message("🎉 Party Added!", "New party has been added successfully.")
                self.load_parties_data()

        except Exception as e:
            self.show_error_message("❌ Error", f"Failed to add party:\n{str(e)}")

    def edit_party(self, party):
        """Open edit party dialog"""
        try:
            dialog = PartyDialog(self, party)
            dialog.setWindowTitle("✏️ Edit Party")

            if dialog.exec_() == QDialog.Accepted:
                self.show_success_message("✅ Party Updated!", "Party details have been updated successfully.")
                self.load_parties_data()

        except Exception as e:
            self.show_error_message("❌ Error", f"Failed to edit party:\n{str(e)}")

    def delete_party(self, party):
        """Delete party with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{party['name']}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db.delete_party(party['id'])
                self.show_success_message("🗑️ Party Deleted!", "Party has been deleted successfully.")
                self.load_parties_data()
            except Exception as e:
                self.show_error_message("❌ Error", f"Failed to delete party:\n{str(e)}")

    def export_parties(self):
        """Export parties data"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")

    def import_parties(self):
        """Import parties data"""
        QMessageBox.information(self, "Import", "Import functionality will be implemented soon!")

    def show_success_message(self, title, message):
        """Show success message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE};
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {SUCCESS};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        msg_box.exec_()

    def show_error_message(self, title, message):
        """Show error message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE};
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {DANGER};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        msg_box.exec_()

    def refresh_data(self):
        """Refresh parties data"""
        self.load_parties_data()
