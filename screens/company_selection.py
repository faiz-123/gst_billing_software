"""
Company Selection Screen for GST Billing Software
Modern, responsive design with gradient background and card-based layout
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFrame, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QCursor

# Import database
try:
    from database import db
except ImportError:
    db = None


class CompanyCard(QFrame):
    """Individual company card widget with modern styling"""
    
    company_selected = pyqtSignal(str)  # Emits company name when selected
    company_edit_requested = pyqtSignal(dict)  # Emits company data when edit is requested
    company_delete_requested = pyqtSignal(dict)  # Emits company data when delete is requested
    
    # Avatar colors for variety
    AVATAR_COLORS = ["#667eea", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]
    
    def __init__(self, company_data, letter, fy, index=0, parent=None):
        super().__init__(parent)
        self.company_data = company_data  # Store the full company data dict
        self.company_name = company_data.get('name', '')
        self.avatar_color = self.AVATAR_COLORS[index % len(self.AVATAR_COLORS)]
        self.setObjectName("companyCard")
        self.setMinimumHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setup_ui(self.company_name, company_data.get('gstin', ''), letter, fy)
        self.setup_shadow()

    def setup_shadow(self):
        """Add subtle shadow effect"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def setup_ui(self, name, gstin, letter, fy):
        """Set up the company card UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Avatar with gradient background
        avatar = QLabel(letter)
        avatar.setObjectName("avatar")
        avatar.setFixedSize(58, 58)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel#avatar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.avatar_color},
                    stop:1 {self._darken_color(self.avatar_color)}
                );
                color: white;
                border-radius: 29px;
                font-weight: 700;
                font-size: 22px;
            }}
        """)

        # Text container
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        name_label = QLabel(name)
        name_label.setObjectName("companyName")
        
        gst_label = QLabel(f"GSTIN: {gstin}")
        gst_label.setObjectName("companyGST")
        
        fy_label = QLabel(f"📅 {fy}")
        fy_label.setObjectName("financialYear")
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(gst_label)
        text_layout.addWidget(fy_label)

        # Buttons container
        buttons_container = QWidget()
        buttons_container.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(6)

        # Delete button
        delete_button = QPushButton("×")
        delete_button.setObjectName("deleteBtn")
        delete_button.setFixedSize(32, 32)
        delete_button.setCursor(QCursor(Qt.PointingHandCursor))
        delete_button.setToolTip("Delete Company")
        delete_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EF4444,
                    stop:1 #DC2626
                );
                color: white;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC2626,
                    stop:1 #B91C1C
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #B91C1C,
                    stop:1 #991B1B
                );
            }
        """)
        delete_button.clicked.connect(self.on_delete_clicked)

        # Edit button
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("editBtn")
        edit_button.setFixedSize(50, 32)
        edit_button.setCursor(QCursor(Qt.PointingHandCursor))
        edit_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6B7280,
                    stop:1 #4B5563
                );
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4B5563,
                    stop:1 #374151
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #374151,
                    stop:1 #1F2937
                );
            }
        """)
        edit_button.clicked.connect(self.on_edit_clicked)

        # Open button with modern styling
        open_button = QPushButton("Open →")
        open_button.setObjectName("openBtn")
        open_button.setFixedSize(70, 32)
        open_button.setCursor(QCursor(Qt.PointingHandCursor))
        # Add inline styling to ensure visibility
        open_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8,
                    stop:1 #6b46c1
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf,
                    stop:1 #553c9a
                );
            }
        """)
        open_button.clicked.connect(self.on_open_clicked)

        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(open_button)

        layout.addWidget(avatar)
        layout.addWidget(text_container, 1)
        layout.addWidget(buttons_container, 0, Qt.AlignRight | Qt.AlignVCenter)

    def _darken_color(self, hex_color):
        """Darken a hex color for gradient"""
        # Simple darkening
        colors = {
            "#667eea": "#5a67d8",
            "#10B981": "#059669",
            "#F59E0B": "#D97706",
            "#EF4444": "#DC2626",
            "#8B5CF6": "#7C3AED",
            "#EC4899": "#DB2777"
        }
        return colors.get(hex_color, hex_color)

    def on_open_clicked(self):
        """Handle open button click"""
        self.company_selected.emit(self.company_name)
    
    def on_edit_clicked(self):
        """Handle edit button click"""
        self.company_edit_requested.emit(self.company_data)
    
    def on_delete_clicked(self):
        """Handle delete button click"""
        self.company_delete_requested.emit(self.company_data)
    
    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == Qt.LeftButton:
            self.company_selected.emit(self.company_name)
        super().mousePressEvent(event)


class CompanySelectionScreen(QWidget):
    """Screen for selecting a company with modern design"""
    
    company_selected = pyqtSignal(str)
    new_company_requested = pyqtSignal()
    edit_company_requested = pyqtSignal(dict)  # New signal for edit requests
    delete_company_requested = pyqtSignal(dict)  # New signal for delete requests
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GST Billing Software - Select Company")
        self.setObjectName("CompanySelectionScreen")
        
        # Store companies list for dynamic updates
        self.companies_data = []
        
        self.setup_ui()
        self.setup_connections()
        self.load_companies_from_db()

    def setup_ui(self):
        """Set up the user interface"""
        # Main gradient background
        self.setStyleSheet("""
            QWidget#CompanySelectionScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:0.5 #764ba2,
                    stop:1 #f093fb
                );
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)
        
        # Main card container - full window size
        self.main_card = QFrame()
        self.main_card.setObjectName("mainCard")
        self.main_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_card.setStyleSheet("""
            QFrame#mainCard {
                background-color: rgba(255, 255, 255, 0.97);
                border-radius: 24px;
                border: none;
            }
        """)
        
        # Card shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.main_card.setGraphicsEffect(shadow)
        
        # Card content layout
        card_layout = QVBoxLayout(self.main_card)
        card_layout.setContentsMargins(40, 40, 40, 35)
        card_layout.setSpacing(0)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # Logo container
        logo_container = QWidget()
        logo_container.setFixedSize(64, 64)
        logo_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                border-radius: 32px;
            }
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_icon = QLabel("🏢")
        logo_icon.setStyleSheet("font-size: 28px; background: transparent;")
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_icon)
        
        # Title section
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title_label = QLabel("Select Company")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #1a1a2e;
                background: transparent;
            }
        """)
        
        subtitle_label = QLabel("Choose a company to continue")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6b7280;
                background: transparent;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # New company button
        self.new_company_button = QPushButton("+ New Company")
        self.new_company_button.setObjectName("btnNewCompany")
        self.new_company_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.new_company_button.setFixedHeight(44)
        self.new_company_button.setStyleSheet("""
            QPushButton#btnNewCompany {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton#btnNewCompany:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8,
                    stop:1 #6b46c1
                );
            }
            QPushButton#btnNewCompany:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf,
                    stop:1 #553c9a
                );
            }
        """)
        
        header_layout.addWidget(logo_container)
        header_layout.addWidget(title_container, 1)
        header_layout.addWidget(self.new_company_button, 0, Qt.AlignTop)
        
        card_layout.addLayout(header_layout)
        card_layout.addSpacing(25)
        
        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e5e7eb;")
        card_layout.addWidget(divider)
        
        card_layout.addSpacing(20)
        
        # Companies list label
        companies_header = QHBoxLayout()
        companies_label = QLabel("Your Companies")
        companies_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                background: transparent;
            }
        """)
        
        count_label = QLabel("0 companies")
        count_label.setObjectName("countLabel")
        count_label.setStyleSheet("""
            QLabel#countLabel {
                font-size: 13px;
                color: #9ca3af;
                background: transparent;
            }
        """)
        
        companies_header.addWidget(companies_label)
        companies_header.addStretch()
        companies_header.addWidget(count_label)
        
        card_layout.addLayout(companies_header)
        card_layout.addSpacing(16)
        
        # Scroll area for companies
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea#scrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#scrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f3f4f6;
                width: 8px;
                border-radius: 4px;
                margin: 4px 2px;
            }
            QScrollBar::handle:vertical {
                background: #d1d5db;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.companies_layout = QVBoxLayout(scroll_content)
        self.companies_layout.setSpacing(12)
        self.companies_layout.setContentsMargins(4, 4, 4, 4)
        self.companies_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        card_layout.addWidget(scroll_area, 1)
        
        # Store count label reference for updates
        self.count_label = count_label
        
        # Add main card directly to main layout
        main_layout.addWidget(self.main_card, 1)
        
        # Footer
        footer_label = QLabel("© 2026 GST Billing Software")
        footer_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                background: transparent;
            }
        """)
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)
        
        # Apply company card styles
        self.apply_card_styles()

    def apply_card_styles(self):
        """Apply styles to company cards"""
        card_style = """
            QFrame#companyCard {
                background: #ffffff;
                border: 2px solid #f3f4f6;
                border-radius: 14px;
            }
            QFrame#companyCard:hover {
                border-color: #667eea;
                background: #fafaff;
            }
            QLabel#companyName {
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
                background: transparent;
            }
            QLabel#companyGST {
                font-size: 13px;
                color: #6b7280;
                background: transparent;
            }
            QLabel#financialYear {
                font-size: 12px;
                color: #9ca3af;
                background: transparent;
            }
            QPushButton#openBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2
                ) !important;
                color: white !important;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton#openBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8,
                    stop:1 #6b46c1
                ) !important;
                color: white !important;
            }
            QPushButton#openBtn:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf,
                    stop:1 #553c9a
                ) !important;
                color: white !important;
            }
        """
        # Apply to scroll area content
        self.setStyleSheet(self.styleSheet() + card_style)

    def setup_connections(self):
        """Set up signal connections"""
        self.new_company_button.clicked.connect(self.on_new_company_clicked)

    def load_companies_from_db(self):
        """Load companies from database and populate the UI"""
        if db is None:
            print("Database not available")
            return
            
        try:
            # Get companies from database
            companies = db.get_companies()
            self.companies_data = []
            
            # Process each company from database
            for company in companies:
                name = company.get('name', 'Unknown Company')
                gstin = company.get('gstin', 'No GSTIN')
                letter = name[0].upper() if name else 'C'
                
                # Since database doesn't have FY info, use current year
                fy = "FY: 2023-24"  # You can modify this based on your requirements
                
                # Store complete company data
                self.companies_data.append((company, letter, fy))
            
            # Update UI
            self.load_companies()
            self.count_label.setText(f"{len(self.companies_data)} companies")
            
            print(f"Loaded {len(self.companies_data)} companies from database")
            
        except Exception as e:
            print(f"Error loading companies from database: {e}")
            # Fallback to empty list
            self.companies_data = []
            self.load_companies()
            self.count_label.setText("0 companies")

    def load_companies(self):
        """Load companies from stored data and display them"""
        # Clear existing companies first
        for i in reversed(range(self.companies_layout.count())):
            child = self.companies_layout.itemAt(i).widget()
            if child and isinstance(child, CompanyCard):
                child.setParent(None)
        
        # Add companies from data
        for index, (company_data, letter, fy) in enumerate(self.companies_data):
            card = CompanyCard(company_data, letter, fy, index)
            card.company_selected.connect(self.company_selected.emit)
            card.company_edit_requested.connect(self.on_company_edit_requested)
            card.company_delete_requested.connect(self.on_company_delete_requested)
            self.companies_layout.addWidget(card)

    def on_new_company_clicked(self):
        """Handle new company button click"""
        self.new_company_requested.emit()
    
    def on_company_edit_requested(self, company_data):
        """Handle edit company request"""
        self.edit_company_requested.emit(company_data)
    
    def on_company_delete_requested(self, company_data):
        """Handle delete company request"""
        self.delete_company_requested.emit(company_data)

    def add_company(self, company_data):
        """Add a new company to the database and refresh the list"""
        if db is None:
            print("Database not available")
            return
            
        try:
            name = company_data.get('company_name', 'Unknown Company')
            gstin = company_data.get('gst', None)
            mobile = company_data.get('mobile', None)
            email = company_data.get('email', None)
            address = company_data.get('address', None)
            
            # Add to database
            company_id = db.add_company(name, gstin, mobile, email, address)
            
            if company_id:
                print(f"Added company '{name}' to database with ID: {company_id}")
                # Refresh the companies list from database
                self.load_companies_from_db()
            else:
                print(f"Failed to add company '{name}' to database")
                
        except Exception as e:
            print(f"Error adding company to database: {e}")

    def refresh_companies(self):
        """Refresh the companies list from database"""
        self.load_companies_from_db()
