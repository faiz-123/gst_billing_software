"""
Company Selection Screen for GST Billing Software
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from .base_screen import BaseScreen


class CompanyCard(QFrame):
    """Individual company card widget"""
    
    company_selected = pyqtSignal(str)  # Emits company name when selected
    
    def __init__(self, name, gstin, letter, fy, parent=None):
        super().__init__(parent)
        self.company_name = name
        self.setObjectName("companyCard")
        self.setMinimumHeight(80)
        self.setup_ui(name, gstin, letter, fy)

    def setup_ui(self, name, gstin, letter, fy):
        """Set up the company card UI"""
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        # Avatar
        avatar = QLabel(letter)
        avatar.setObjectName("avatar")
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignCenter)

        # Texts
        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setObjectName("companyName")
        gst_label = QLabel(f"GSTIN: {gstin}")
        gst_label.setObjectName("companyGST")
        fy_label = QLabel(fy)
        fy_label.setObjectName("financialYear")
        text_layout.addWidget(name_label)
        text_layout.addWidget(gst_label)
        text_layout.addWidget(fy_label)

        # Open button
        open_button = QPushButton("Open")
        open_button.setObjectName("openBtn")
        open_button.setFixedSize(90, 44)
        open_button.clicked.connect(self.on_open_clicked)

        layout.addWidget(avatar)
        layout.addLayout(text_layout, 1)
        layout.addWidget(open_button, 0, Qt.AlignRight)

    def on_open_clicked(self):
        """Handle open button click"""
        self.company_selected.emit(self.company_name)


class CompanySelectionScreen(QWidget):
    """Screen for selecting a company"""
    
    company_selected = pyqtSignal(str)
    new_company_requested = pyqtSignal()
    
    # Color constants
    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#3B82F6"
    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    BACKGROUND = "#F9FAFB"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    BORDER = "#E5E7EB"
    WHITE = "#FFFFFF"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GST Billing Software - Select Company")
        self.resize(1200, 800)
        
        # Store companies list for dynamic updates
        self.companies_data = [
            ("ABC Traders", "24ABCDE234F75", "A", "FY: 2023-24"),
            ("XYZ Supermarket", "27XY2123425", "X", "FY: 2023-24"),
            ("Ravi Stores", "24ABC4567015", "R", "FY: 2023-24"),
        ]
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface"""
        # Central widget layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(80, 80, 80, 80)

        # Top row with title and new company button
        top_row = QHBoxLayout()
        title_label = QLabel("GST Billing Software")
        title_label.setObjectName("lblTitle")
        
        new_company_button = QPushButton("+ New Company")
        new_company_button.setObjectName("btnNewCompany")
        # new_company_button.setFixedHeight(44)
        
        top_row.addWidget(title_label)
        top_row.addStretch(1)
        top_row.addWidget(new_company_button)
        main_layout.addLayout(top_row)

        # Select Company Card
        select_frame = QFrame()
        select_frame.setObjectName("frameSelectCompany")
        frame_layout = QHBoxLayout(select_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)

        logo_label = QLabel("LOGO")
        logo_label.setObjectName("lblLogoPlaceholder")
        logo_label.setFixedSize(84, 84)
        logo_label.setAlignment(Qt.AlignCenter)

        select_label = QLabel("Select Company")
        select_label.setObjectName("lblSelectCompany")

        frame_layout.addWidget(logo_label)
        frame_layout.addWidget(select_label)
        frame_layout.addStretch(1)

        main_layout.addWidget(select_frame)

        # Companies list label
        companies_label = QLabel("List Of Companies")
        companies_label.setObjectName("lblCompaniesList")
        main_layout.addWidget(companies_label)

        # Scroll area for companies
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignTop)
        scroll_content = QWidget()
        self.companies_layout = QVBoxLayout(scroll_content)
        self.companies_layout.setSpacing(16)
        # self.companies_layout.setContentsMargins(16, 0, 16, 8)  # Top aligned with no top margin
        self.companies_layout.setAlignment(Qt.AlignTop)

        # Add sample companies (this would normally come from database)
        self.load_companies()

        # self.companies_layout.addStretch(1)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Store reference to new company button for connections
        self.new_company_button = new_company_button

    def setup_connections(self):
        """Set up signal connections"""
        self.new_company_button.clicked.connect(self.on_new_company_clicked)

    def load_companies(self):
        """Load companies from database and display them"""
        # Use stored companies data
        for name, gst, letter, fy in self.companies_data:
            card = CompanyCard(name, gst, letter, fy)
            card.company_selected.connect(self.company_selected.emit)
            self.companies_layout.addWidget(card)

    def on_new_company_clicked(self):
        """Handle new company button click"""
        self.new_company_requested.emit()

    def add_company(self, company_data):
        """Add a new company to the list"""
        # Extract data from company_data dict
        name = company_data.get('company_name', 'Unknown Company')
        gst = company_data.get('gst', 'No GST')
        # Get first letter of company name for avatar
        letter = name[0].upper() if name else 'C'
        # Format financial year from the dates
        fy_start = company_data.get('fy_start', '2023-04-01')
        fy_end = company_data.get('fy_end', '2024-03-31')
        fy = f"FY: {fy_start[:4]}-{fy_end[2:4]}"
        
        # Add to companies data
        new_company = (name, gst, letter, fy)
        self.companies_data.append(new_company)
        
        # Add to UI
        card = CompanyCard(name, gst, letter, fy)
        card.company_selected.connect(self.company_selected.emit)
        # Insert before the stretch at the end
        self.companies_layout.insertWidget(self.companies_layout.count() - 1, card)
        
        print(f"Added company: {name} to the list")  # Debug

    def apply_styles(self):
        """Apply CSS styles to the widget"""
        self.setStyleSheet(f"""
        QWidget {{
            background: {self.BACKGROUND};
            color: {self.TEXT_PRIMARY};
        }}
        QLabel#lblTitle {{
            font-size: 28px;
            font-weight: bold;
            color: {self.TEXT_PRIMARY};
            background-color: transparent;
        }}
        QPushButton#btnNewCompany {{
            background-color: {self.PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 15px 30px;
            font-size: 16px;
            min-width: 120px;
        }}
        QPushButton#btnNewCompany:hover {{
            background-color: {self.PRIMARY_HOVER};
        }}
        QPushButton#btnNewCompany:pressed {{
            background-color: #1E40AF;
        }}
        QFrame#frameSelectCompany {{
            background: {self.WHITE};
            border: 2px solid {self.BORDER};
            border-radius: 10px;
        }}
        QLabel#lblLogoPlaceholder {{
            background: {self.WHITE};
            border: 2px dashed {self.BORDER};
            border-radius: 8px;
            color: {self.TEXT_SECONDARY};
            font-weight: 600;
        }}
        QLabel#lblSelectCompany {{
            font-size: 28px;
            font-weight: bold;
            color: {self.TEXT_PRIMARY};
            background-color: {self.WHITE};
        }}
        QLabel#lblCompaniesList {{
            font-size: 20px;
            font-weight: bold;
            margin-top: 8px;
            background-color: transparent;
            color: {self.TEXT_PRIMARY};
        }}
        QScrollArea#scrollArea {{
            background: white;
            border: 2px solid {self.BORDER};
            border-radius: 10px;
        }}
        
        QFrame#companyCard {{
            background: white;
            border: 1px solid {self.BORDER};
            border-radius: 10px;
        }}
        QFrame#companyCard:hover {{
            border-color: {self.PRIMARY};
        }}
        QLabel#avatar {{
            background: {self.SUCCESS};
            color: white;
            border-radius: 28px;
            font-weight: 700;
            font-size: 22px;
        }}
        QPushButton#openBtn {{
            background: white;
            border: 1px solid {self.BORDER};
            border-radius: 8px;
            font-weight: 600;
        }}
        QPushButton#openBtn:hover {{
            background: #F3F4F6;
            border-color: {self.PRIMARY};
        }}
        QLabel#companyName {{
            font-size: 16px;
            font-weight: 600;
            color: {self.TEXT_PRIMARY};
            background-color: transparent;
        }}
        QLabel#companyGST {{
            font-size: 14px;
            color: {self.TEXT_SECONDARY};
            background-color: transparent;
        }}
        QLabel#financialYear {{
            font-size: 13px;
            color: {self.TEXT_SECONDARY};
            background-color: transparent;
        }}
        """)

    def refresh_companies(self):
        """Refresh the companies list"""
        # Clear existing companies
        for i in reversed(range(self.companies_layout.count())):
            child = self.companies_layout.itemAt(i).widget()
            if child and isinstance(child, CompanyCard):
                child.setParent(None)
        
        # Reload companies
        self.load_companies()
