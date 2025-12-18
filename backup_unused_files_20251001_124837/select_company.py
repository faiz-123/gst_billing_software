# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QLabel, QPushButton,
#     QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
# )
# from PySide6.QtCore import Qt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
import sys

# ---------------- Colors ----------------
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BACKGROUND = "#F9FAFB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
WHITE = "#FFFFFF"

# ---------------- Company Card ----------------
class CompanyCard(QFrame):
    def __init__(self, name, gstin, letter, fy, parent=None):
        super().__init__(parent)
        self.setObjectName("companyCard")
        self.setMinimumHeight(80)

        # Layout
        h = QHBoxLayout(self)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(10)

        # Avatar
        avatar = QLabel(letter)
        avatar.setObjectName("avatar")
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignCenter)

        # Texts
        vbox = QVBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setObjectName("companyName")
        gst_lbl = QLabel(f"GSTIN: {gstin}")
        gst_lbl.setObjectName("companyGST")
        fy_lbl = QLabel(fy)
        fy_lbl.setObjectName("financialYear")
        vbox.addWidget(name_lbl)
        vbox.addWidget(gst_lbl)
        vbox.addWidget(fy_lbl)

        # Open button
        btn_open = QPushButton("Open")
        btn_open.setObjectName("openBtn")
        btn_open.setFixedSize(90, 44)
        btn_open.clicked.connect(lambda: print(f"Opening {name}"))

        h.addWidget(avatar)
        h.addLayout(vbox, 1)
        h.addWidget(btn_open, 0, Qt.AlignRight)


# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software - Select Company")
        self.resize(1200, 800)

        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(80, 80, 80, 80)

        # ---------------- Top row ----------------
        top_row = QHBoxLayout()
        lbl_title = QLabel("GST Billing Software")
        lbl_title.setObjectName("lblTitle")
        btn_new = QPushButton("+ New Company")
        btn_new.setObjectName("btnNewCompany")
        btn_new.setFixedHeight(44)
        top_row.addWidget(lbl_title)
        top_row.addStretch(1)
        top_row.addWidget(btn_new)
        main_layout.addLayout(top_row)

        # ---------------- Select Company Card ----------------
        frame_select = QFrame()
        frame_select.setObjectName("frameSelectCompany")
        frame_layout = QHBoxLayout(frame_select)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)

        logo_lbl = QLabel("LOGO")
        logo_lbl.setObjectName("lblLogoPlaceholder")
        logo_lbl.setFixedSize(84, 84)
        logo_lbl.setAlignment(Qt.AlignCenter)

        select_lbl = QLabel("Select Company")
        select_lbl.setObjectName("lblSelectCompany")

        frame_layout.addWidget(logo_lbl)
        frame_layout.addWidget(select_lbl)
        frame_layout.addStretch(1)

        main_layout.addWidget(frame_select)

        # ---------------- Your Companies Label ----------------
        lbl_your = QLabel("List Of Companies")
        lbl_your.setObjectName("lblCompaniesList")
        main_layout.addWidget(lbl_your)

        # ---------------- Scroll Area ----------------
        scroll = QScrollArea()
        scroll.setObjectName("scrollArea")
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        vbox_cards = QVBoxLayout(scroll_content)
        vbox_cards.setSpacing(16)

        # Add sample companies
        companies = [
            ("ABC Traders", "24ABCDE234F75", "A", "FY: 2023-24"),
            ("XYZ Supermarket", "27XY2123425", "X", "FY: 2023-24"),
            ("Ravi Stores", "24ABC4567015", "R", "FY: 2023-24"),
        ]
        for name, gst, letter, fy in companies:
            vbox_cards.addWidget(CompanyCard(name, gst, letter, fy))

        vbox_cards.addStretch(1)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setCentralWidget(central)

        # ---------------- Apply Styles ----------------
        self.setStyleSheet(self.app_styles())

    def app_styles(self):
        return f"""
        QWidget {{
            background: {BACKGROUND};
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', sans-serif;
        }}
        QLabel#lblTitle {{
            font-size: 28px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        }}
        QPushButton#btnNewCompany {{
            background-color: {PRIMARY};
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton#btnNewCompany:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        QFrame#frameSelectCompany {{
            background: white;
            border: 2px solid {BORDER};
            border-radius: 10px;
        }}
        QLabel#lblLogoPlaceholder {{
            background: white;
            c
            border-radius: 8px;
            color: {TEXT_SECONDARY};
            font-weight: 600;
        }}
        QLabel#lblSelectCompany {{
            font-size: 28px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
            background-color: {WHITE};
        }}
        QLabel#lblCompaniesList {{
            font-size: 20px;
            font-weight: bold;
            margin-top: 8px;
        }}
         QScrollArea#scrollArea {{
            background: white;
            border: 2px solid {BORDER};
            border-radius: 10px;
        }}
        QFrame#companyCard {{
            background: white;
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}
        QLabel#avatar {{
            background: {SUCCESS};
            color: white;
            border-radius: 28px;
            font-weight: 700;
            font-size: 22px;
        }}
        QPushButton#openBtn {{
            background: white;
            border: 1px solid {BORDER};
            border-radius: 8px;
            font-weight: 600;
        }}
        QPushButton#openBtn:hover {{
            background: #F3F4F6;
        }}
        QLabel#companyName {{
            font-size: 16px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            background-color: {WHITE};
        }}
        QLabel#financialYear {{
            font-size: 12px;
            color: {TEXT_SECONDARY};
            background-color: {WHITE};
        }}
        QLabel#companyGST {{
            font-size: 13px;
            color: {TEXT_SECONDARY};
            background-color: {WHITE};
        }}
        """


# ---------------- Run App ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
