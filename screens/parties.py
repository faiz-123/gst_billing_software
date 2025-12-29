"""Parties screen - Manage customers and suppliers

This module provides a polished Parties screen (`PartiesScreen`) and a
reusable `PartyDialog` for adding/editing parties. The dialog validates
inputs and will call `db.add_party` if available.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QWidget,
    QFrame, QDialog, QMessageBox, QLineEdit, QComboBox, QTextEdit, QCheckBox,
    QShortcut, QToolButton, QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QKeySequence
import re

from .base_screen import BaseScreen
from theme import PRIMARY, SUCCESS, WARNING, DANGER, WHITE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY
from widgets import CustomTable
from database import db
from .party_dialog import PartyDialog, BankAccountDialog


# NOTE: PartyDialog and BankAccountDialog are now imported from .party_dialog



class PartiesScreen(BaseScreen):
    def __init__(self):
        super().__init__("Parties Management")
        self.setup_parties_screen()
        self.load_parties_data()

    def setup_parties_screen(self):
        self.setup_action_bar()
        # self.setup_header_stats()
        self.setup_filters()
        self.setup_parties_table()

    def setup_header_stats(self):
        stats_layout = QHBoxLayout()
        stats_layout.setObjectName("stats_layout")

        stats_data = [
            ("👥", "Total Parties", "42", PRIMARY),
            ("🏢", "Customers", "28", SUCCESS),
            ("🏭", "Suppliers", "14", WARNING),
            ("📊", "GST Registered", "38", DANGER)
        ]

        for icon, label, value, color in stats_data:
            card = self.create_stat_card(icon, label, value, color)
            stats_layout.addWidget(card)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.add_content(stats_widget)

    def create_stat_card(self, icon, label, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setFixedWidth(250)
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 2px solid {BORDER};
                border-radius: 12px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: #f8f9fa;
            }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: #6B7280; font-size: 14px; border: none;")

        text_layout.addWidget(value_label)
        text_layout.addWidget(label_widget)
        layout.addLayout(text_layout)

        return card

    def setup_action_bar(self):
        action_frame = QFrame()
        action_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)

        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(15)

        search_container = QFrame()
        search_container.setFixedWidth(350)
        search_container.setFixedHeight(55)
        search_container.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {BORDER};
                border-radius: 8px;
                background: {WHITE};
            }}
            QFrame:focus-within {{
                border-color: {PRIMARY};
            }}
        """)

        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 0, 0, 0)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search with name")
        try:
            self.search_input.setClearButtonEnabled(True)
        except Exception:
            pass
        self.search_input.setAlignment(Qt.AlignLeft)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.search_input.textChanged.connect(self.filter_parties)
        
        search_layout.addWidget(self.search_input)
        action_layout.addWidget(search_container)
        action_layout.addStretch()

       

        buttons_data = [
            ("📊 Export", "secondary", self.export_parties),
            ("📄 Import", "secondary", self.import_parties),
            ("➕ Add Party", "primary", self.add_party)
        ]

        for text, style, callback in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setMinimumWidth(120)
            btn.clicked.connect(callback)

            if style == "primary":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {PRIMARY};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background: #2563EB;
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
                        border: 2px solid {BORDER};
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        border-color: {PRIMARY};
                        background: #f8f9fa;
                    }}
                """)

            action_layout.addWidget(btn)

        self.add_content(action_frame)

    def force_upper(self, text):
        if text != text.upper():
            cursor_pos = self.search_input.cursorPosition()
            self.search_input.setText(text.upper())
            self.search_input.setCursorPosition(cursor_pos)

    def setup_filters(self):
        """Setup enhanced filter controls"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(25)

        # Filter title
        filter_title = QLabel("📋 Filters")
        filter_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        filter_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        filter_layout.addWidget(filter_title)

        # Modern filter dropdowns
        filters_data = [
            ("Type:", ["All", "Customer", "Supplier", "Both"]),
            ("GST Status:", ["All", "Registered", "Unregistered"]),
            ("Balance:", ["All", "Receivable", "Payable", "Zero Balance"])
        ]

        self.filter_combos = {}

        for label_text, items in filters_data:
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 500; border: none;")
            filter_layout.addWidget(label)

            # Combo
            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedHeight(35)
            combo.setFixedWidth(140)
            combo.setStyleSheet(f"""
                QComboBox {{
                    border: 2px solid {BORDER};
                    border-radius: 8px;
                    padding: 6px 12px;
                    background: {WHITE};
                    font-size: 14px;
                    color: {TEXT_PRIMARY};
                }}
                QComboBox:hover {{
                    border-color: {PRIMARY};
                }}
                QComboBox:focus {{
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
                    border-top: 6px solid {TEXT_PRIMARY};
                    margin-right: 8px;
                }}
                QComboBox QAbstractItemView {{
                    border: 2px solid {PRIMARY};
                    background: {WHITE};
                    selection-background-color: {PRIMARY};
                    selection-color: white;
                    border-radius: 8px;
                }}
            """)
            combo.currentTextChanged.connect(self.filter_parties)

            # Store reference for filtering
            filter_key = label_text.lower().replace(":", "").replace(" ", "_")
            self.filter_combos[filter_key] = combo

            filter_layout.addWidget(combo)
            filter_layout.addSpacing(10)

        filter_layout.addStretch()

        # Enhanced action buttons
        action_buttons = [
            ("🔄", "Refresh", self.load_parties_data),
            ("🗑️", "Clear Filters", self.clear_filters)
        ]

        for icon, tooltip, callback in action_buttons:
            btn = QPushButton(icon)
            # btn.setFixedSize(50, 35)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {BORDER};
                    border-radius: 17px;
                    background: {WHITE};
                    font-size: 16px;
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background: {PRIMARY};
                    color: white;
                    border-color: {PRIMARY};
                }}
                QPushButton:pressed {{
                    background: #1D4ED8;
                }}
            """)
            btn.clicked.connect(callback)
            filter_layout.addWidget(btn)

        self.add_content(filter_frame)

    def import_parties(self):
        """Import parties from file"""
        QMessageBox.information(self, "Import", "Import functionality coming soon!")

    def clear_filters(self):
        """Clear all filters"""
        for combo in self.filter_combos.values():
            combo.setCurrentIndex(0)
        self.search_input.clear()
        self.filter_parties()

    def setup_parties_table(self):
        """Setup enhanced parties data table"""
        # Modern table container
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 12px;
                margin: 5px;
            }}
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(25, 25, 25, 25)
        table_layout.setSpacing(15)

        # Table header with count
        header_layout = QHBoxLayout()

        table_title = QLabel("📋 Parties List")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none;")
        header_layout.addWidget(table_title)

        self.count_label = QLabel("Total: 0 parties")
        self.count_label.setStyleSheet(f"color: #6B7280; font-size: 14px; border: none;")
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        # View toggle buttons
        view_buttons = QWidget()
        view_layout = QHBoxLayout(view_buttons)
        view_layout.setSpacing(5)
        view_layout.setContentsMargins(0, 0, 0, 0)

        # Optional: view toggle buttons can be added here later
        # header_layout.addWidget(view_buttons)
        # Add header (title + count) above the table
        table_layout.addLayout(header_layout)

        # Enhanced table
        headers = ["#", "Name", "Type", "Contact", "GST Status", "Balance", "Actions"]
        # Create the parties table using CustomTable
        self.parties_table = CustomTable(0, len(headers), headers)

        # Enhanced table styling
        self.parties_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #E5E7EB;
                background-color: {WHITE};
                border: none;
                font-size: 14px;
                selection-background-color: #EEF2FF;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #F3F4F6;
                padding: 12px 8px;
            }}
            QTableWidget::item:selected {{
                background-color: #EEF2FF;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {TEXT_PRIMARY};
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                padding: 12px 8px;
                font-size: 14px;
            }}
            QHeaderView::section:hover {{
                background-color: #F1F5F9;
            }}
        """)

        # Set optimal column widths
        column_widths = [40, 180, 100, 150, 120, 100, 120]
        for i, width in enumerate(column_widths):
            self.parties_table.setColumnWidth(i, width)

        # Set minimum height for better appearance
        self.parties_table.setMinimumHeight(400)
        # Ensure rows are tall enough for action buttons
        try:
            vh = self.parties_table.verticalHeader()
            vh.setDefaultSectionSize(36)
        except Exception:
            pass
        self.parties_table.setColumnWidth(5, 100)  # Balance
        self.parties_table.setColumnWidth(6, 120)  # Actions (compact)

        table_layout.addWidget(self.parties_table)
        self.add_content(table_frame)

        # Store original data for filtering
        self.all_parties_data = []

    def load_parties_data(self):
        """Load parties data into table"""
        try:
            parties = db.get_parties()
            self.all_parties_data = parties
            self.populate_table(parties)
            self.update_header_stats()
            # Ensure count label shows total on initial load
            if hasattr(self, 'count_label'):
                self.count_label.setText(f"📊 Total: {len(self.all_parties_data)} parties")
        except Exception as e:
            # Show error if database not available
            QMessageBox.critical(self, "Database Error", f"Could not load parties from database:\n{e}")
            self.all_parties_data = []
            self.populate_table([])
            if hasattr(self, 'count_label'):
                self.count_label.setText("No parties found.")

    def populate_table(self, parties_data):
        """Populate table with enhanced party data"""
        self.parties_table.setRowCount(len(parties_data))

        for row, party in enumerate(parties_data):
            # Column 0: Row number
            self.parties_table.setItem(row, 0, self.parties_table.create_item(str(row + 1), Qt.AlignCenter))

            # Column 1: Party name
            self.parties_table.setItem(row, 1, self.parties_table.create_item(party['name'], Qt.AlignCenter))

            # Column 2: Type with icon
            party_type = party.get('party_type', '')
            type_icon = "🏢" if party_type == "Customer" else "🏭" if party_type == "Supplier" else "🔄"
            type_display = f"{type_icon} {party_type}"
            self.parties_table.setItem(row, 2, self.parties_table.create_item(type_display, Qt.AlignCenter))

            # Column 3: Contact (phone/email)
            phone = party.get('phone', '')
            email = party.get('email', '')
            contact_display = phone if phone else email if email else "No contact"
            self.parties_table.setItem(row, 3, self.parties_table.create_item(contact_display, Qt.AlignCenter))

            # Column 4: GST Status with icon
            gst_number = party.get('gst_number', '')
            if gst_number:
                gst_display = f"✅ {gst_number[:15]}{'...' if len(gst_number) > 15 else ''}"
            else:
                gst_display = "❌ Not Registered"
            self.parties_table.setItem(row, 4, self.parties_table.create_item(gst_display, Qt.AlignCenter))

            # Format balance
            balance = party.get('opening_balance', 0)
            balance_text = f"₹{abs(balance):,.2f} {'Dr' if balance >= 0 else 'Cr'}"
            self.parties_table.setItem(row, 5, self.parties_table.create_item(balance_text, Qt.AlignCenter))

            # Action buttons
            actions_widget = self.create_action_buttons(party)
            self.parties_table.setCellWidget(row, 6, actions_widget)

    def create_action_buttons(self, party):
        """Create action buttons for each row"""
        widget = QWidget()
        widget.setFixedHeight(25)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setStyleSheet("background: transparent;")
        widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignCenter)

        # Edit tool button (emoji text for consistent rendering)
        edit_btn = QToolButton()
        edit_btn.setText("✎")
        edit_btn.setToolTip("Edit")
        edit_btn.setFixedSize(22, 22)
        edit_btn.setAutoRaise(True)
        edit_btn.setStyleSheet(f"""
            QToolButton {{
                border: 1px solid {PRIMARY};
                border-radius: 11px;
                padding: 0px;
                background: transparent;
            }}
            QToolButton:hover {{
                background: {PRIMARY};
                color: white;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_party(party))
        layout.addWidget(edit_btn)

        # Delete tool button (emoji text)
        delete_btn = QToolButton()
        delete_btn.setText("🗑️")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(22, 22)
        delete_btn.setAutoRaise(True)
        delete_btn.setStyleSheet(f"""
            QToolButton {{
                border: 1px solid {DANGER};
                border-radius: 11px;
                padding: 0px;
                background: transparent;
            }}
            QToolButton:hover {{
                background: {DANGER};
                color: white;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_party(party))
        layout.addWidget(delete_btn)

        return widget

    def filter_parties(self, *_):
        """Enhanced filter parties based on search and multiple filters"""
        self.force_upper(self.search_input.text())
        search_text = self.search_input.text().lower()

        # Get filter values
        type_filter = self.filter_combos.get('type', self.filter_combos.get('type_filter', type('', (), {'currentText': lambda: 'All'})))
        gst_filter = self.filter_combos.get('gst_status', self.filter_combos.get('gst_filter', type('', (), {'currentText': lambda: 'All'})))
        balance_filter = self.filter_combos.get('balance', type('', (), {'currentText': lambda: 'All'}))

        type_text = type_filter.currentText() if hasattr(type_filter, 'currentText') else 'All'
        gst_text = gst_filter.currentText() if hasattr(gst_filter, 'currentText') else 'All'
        balance_text = balance_filter.currentText() if hasattr(balance_filter, 'currentText') else 'All'

        filtered_data = []
        for party in self.all_parties_data:
            # Search filter (name, phone, email)
            if search_text:
                # Safely handle None values in fields
                search_fields = [
                    (party.get('name') or '').lower(),
                    (party.get('phone') or '').lower(),
                    (party.get('email') or '').lower(),
                    (party.get('gst_number') or '').lower(),
                ]
                if not any(search_text in field for field in search_fields):
                    continue

            # Type filter
            if type_text != "All" and party.get('party_type', '') != type_text:
                continue

            # GST filter
            if gst_text == "Registered" and not party.get('gst_number'):
                continue
            elif gst_text == "Unregistered" and party.get('gst_number'):
                continue

            # Balance filter
            balance = float(party.get('opening_balance', 0))
            if balance_text == "Receivable" and balance <= 0:
                continue
            elif balance_text == "Payable" and balance >= 0:
                continue
            elif balance_text == "Zero Balance" and balance != 0:
                continue

            filtered_data.append(party)

        self.populate_table(filtered_data)

        # Enhanced count with additional stats
        if hasattr(self, 'count_label'):
            if len(filtered_data) == len(self.all_parties_data):
                self.count_label.setText(f"📊 Total: {len(self.all_parties_data)} parties")
            else:
                self.count_label.setText(f"🔍 Showing: {len(filtered_data)} of {len(self.all_parties_data)} parties")

        # Update header stats when filters change
        self.update_filtered_stats(filtered_data)

    def update_filtered_stats(self, filtered_data):
        """Update stats based on filtered data for better context"""
        try:
            if not filtered_data:
                return

            total = len(filtered_data)
            customers = len([p for p in filtered_data if p.get('party_type') == 'Customer'])
            suppliers = len([p for p in filtered_data if p.get('party_type') == 'Supplier'])
            both_type = len([p for p in filtered_data if p.get('party_type') == 'Both'])
            gst_registered = len([p for p in filtered_data if p.get('gst_number')])

            # Print filtered stats for debugging
            # print(f"Filtered Stats - Total: {total}, Customers: {customers + both_type}, "
            #       f"Suppliers: {suppliers + both_type}, GST Registered: {gst_registered}")

        except Exception as e:
            print(f"Error updating filtered stats: {e}")

    def add_party(self):
        """Enhanced add party with better UX and validation"""
        try:
            # Create and configure dialog
            dialog = PartyDialog(self)
            dialog.setWindowTitle("➕ Add New Party")

            # Center dialog on parent
            if self.parent():
                parent_geometry = self.parent().geometry()
                x = parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2
                y = parent_geometry.y() + (parent_geometry.height() - dialog.height()) // 2
                dialog.move(x, y)

            # Show dialog and handle result
            result = dialog.exec_()

            if result == QDialog.Accepted:
                # Show success feedback
                self.show_success_message("🎉 Party Added Successfully!",
                                        "New party has been added to your database.")

                # Refresh data and update stats
                self.refresh_parties_data()

                # Auto-clear search to show new party
                if hasattr(self, 'search_input'):
                    self.search_input.clear()

                # Reset filters to 'All' to ensure new party is visible
                self.reset_filters_to_show_all()

                # Scroll to the newly added party (typically at the end)
                if hasattr(self, 'parties_table') and self.parties_table.rowCount() > 0:
                    self.parties_table.scrollToBottom()
                    # Briefly highlight the last row (new party)
                    last_row = self.parties_table.rowCount() - 1
                    self.parties_table.selectRow(last_row)

        except Exception as e:
            # Enhanced error handling
            self.show_error_message("❌ Failed to Add Party",
                                   f"An error occurred while adding the party:\n{str(e)}")
            print(f"Error in add_party: {e}")  # For debugging

    def show_success_message(self, title, message):
        """Show enhanced success message with modern styling"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)

        # Enhanced styling for success message
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE};
                border: 2px solid {SUCCESS};
                border-radius: 12px;
                font-size: 14px;
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
                background-color: #16A34A;
            }}
        """)

        msg_box.exec_()

    def show_error_message(self, title, message):
        """Show enhanced error message with modern styling"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)

        # Enhanced styling for error message
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE};
                border: 2px solid {DANGER};
                border-radius: 12px;
                font-size: 14px;
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

    def reset_filters_to_show_all(self):
        """Reset all filters to 'All' to ensure new party is visible"""
        try:
            for combo in self.filter_combos.values():
                if hasattr(combo, 'setCurrentIndex'):
                    combo.setCurrentIndex(0)  # Set to 'All'
        except Exception as e:
            print(f"Error resetting filters: {e}")

    def refresh_parties_data(self):
        """Enhanced refresh with stats update"""
        try:
            # Reload parties data
            self.load_parties_data()

            # Update statistics dynamically
            self.update_header_stats()

            # Apply current filters after refresh
            self.filter_parties()

        except Exception as e:
            print(f"Error refreshing parties data: {e}")
            # Show sample data as fallback
            self.load_sample_data()

    def update_header_stats(self):
        """Update header statistics with real data"""
        try:
            if not hasattr(self, 'all_parties_data'):
                return

            total_parties = len(self.all_parties_data)
            customers = len([p for p in self.all_parties_data if p.get('party_type') == 'Customer'])
            suppliers = len([p for p in self.all_parties_data if p.get('party_type') == 'Supplier'])
            both_type = len([p for p in self.all_parties_data if p.get('party_type') == 'Both'])
            gst_registered = len([p for p in self.all_parties_data if p.get('gst_number')])

            # Update stats if we have dynamic references (this would need to be implemented)
            stats_updates = {
                'total': str(total_parties),
                'customers': str(customers + both_type),  # Include 'Both' in customers
                'suppliers': str(suppliers + both_type),   # Include 'Both' in suppliers
                'gst_registered': str(gst_registered)
            }

            # For now, we'll print the updated stats
            # print(f"Updated Stats - Total: {total_parties}, Customers: {customers + both_type}, "
            #       f"Suppliers: {suppliers + both_type}, GST Registered: {gst_registered}")

        except Exception as e:
            print(f"Error updating header stats: {e}")

    # Removed load_sample_data: always show actual database data

    def edit_party(self, party):
        """Open edit party dialog"""
        dialog = PartyDialog(self, party)
        if dialog.exec_() == QDialog.Accepted:
            self.load_parties_data()

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
                QMessageBox.information(self, "Success", "Party deleted successfully!")
                self.load_parties_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete party: {str(e)}")

    def export_parties(self):
        """Export parties data"""
        # This would implement CSV/Excel export
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")

    def refresh_data(self):
        """Refresh parties data"""
        self.load_parties_data()
