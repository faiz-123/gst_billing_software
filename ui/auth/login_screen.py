"""
Login Screen for GST Billing Software
Modern, responsive design with gradient background and card-based layout
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class LoginScreen(QtWidgets.QWidget):
    """Login screen for user authentication"""
    
    # Signal emitted when login is successful
    login_successful = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GST Billing Software - Login")
        self.setMinimumSize(QtCore.QSize(500, 600))
        self.setup_ui()
        self.setup_connections()
        self.setup_animations()

    def setup_ui(self):
        """Set up the user interface"""
        # Main gradient background
        self.setStyleSheet("""
            QWidget#LoginScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:0.5 #764ba2,
                    stop:1 #f093fb
                );
            }
        """)
        self.setObjectName("LoginScreen")
        
        # Main layout with responsive margins
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Top spacer for vertical centering
        self.main_layout.addStretch(1)
        
        # Horizontal layout for card centering
        card_h_layout = QtWidgets.QHBoxLayout()
        card_h_layout.addStretch(1)
        
        # Card container with shadow effect
        self.card_widget = QtWidgets.QFrame()
        self.card_widget.setObjectName("loginCard")
        self.card_widget.setMinimumSize(QtCore.QSize(420, 520))
        self.card_widget.setMaximumSize(QtCore.QSize(550, 600))
        self.card_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )
        self.card_widget.setStyleSheet("""
            QFrame#loginCard {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: none;
            }
        """)
        
        # Add shadow effect to card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.card_widget.setGraphicsEffect(shadow)
        
        # Card content layout
        self.card_layout = QtWidgets.QVBoxLayout(self.card_widget)
        self.card_layout.setContentsMargins(40, 50, 40, 40)
        self.card_layout.setSpacing(0)
        
        # Logo/Icon container
        self.logo_container = QtWidgets.QWidget()
        self.logo_container.setFixedSize(80, 80)
        self.logo_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                border-radius: 40px;
            }
        """)
        logo_layout = QtWidgets.QVBoxLayout(self.logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo icon/text
        self.logo_icon = QtWidgets.QLabel("💼")
        self.logo_icon.setStyleSheet("""
            QLabel {
                font-size: 36px;
                background: transparent;
            }
        """)
        self.logo_icon.setAlignment(QtCore.Qt.AlignCenter)
        logo_layout.addWidget(self.logo_icon)
        
        # Center logo
        logo_h_layout = QtWidgets.QHBoxLayout()
        logo_h_layout.addStretch()
        logo_h_layout.addWidget(self.logo_container)
        logo_h_layout.addStretch()
        self.card_layout.addLayout(logo_h_layout)
        
        self.card_layout.addSpacing(25)
        
        # Welcome text
        self.welcome_label = QtWidgets.QLabel("Welcome Back")
        self.welcome_label.setStyleSheet("""
            QLabel {
                color: #1a1a2e;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.card_layout.addWidget(self.welcome_label)
        
        self.card_layout.addSpacing(8)
        
        # Subtitle
        self.subtitle_label = QtWidgets.QLabel("Sign in to GST Billing Software")
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        self.card_layout.addWidget(self.subtitle_label)
        
        self.card_layout.addSpacing(35)
        
        # Username section
        self.username_label = QtWidgets.QLabel("Username")
        self.username_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                margin-bottom: 6px;
            }
        """)
        self.card_layout.addWidget(self.username_label)
        
        self.card_layout.addSpacing(6)
        
        # Username input with icon
        self.username_container = QtWidgets.QFrame()
        self.username_container.setObjectName("inputContainer")
        self.username_container.setStyleSheet("""
            QFrame#inputContainer {
                background-color: #f3f4f6;
                border: 2px solid transparent;
                border-radius: 12px;
            }
            QFrame#inputContainer:hover {
                border: 2px solid #667eea;
            }
        """)
        username_layout = QtWidgets.QHBoxLayout(self.username_container)
        username_layout.setContentsMargins(16, 0, 16, 0)
        username_layout.setSpacing(12)
        
        self.username_icon = QtWidgets.QLabel("👤")
        self.username_icon.setStyleSheet("font-size: 18px; background: transparent;")
        username_layout.addWidget(self.username_icon)
        
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                font-size: 15px;
                color: #1f2937;
                padding: 0;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(self.username_input)
        
        self.card_layout.addWidget(self.username_container)
        
        self.card_layout.addSpacing(20)
        
        # Password section
        self.password_label = QtWidgets.QLabel("Password")
        self.password_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                margin-bottom: 6px;
            }
        """)
        self.card_layout.addWidget(self.password_label)
        
        self.card_layout.addSpacing(6)
        
        # Password input with icon
        self.password_container = QtWidgets.QFrame()
        self.password_container.setObjectName("inputContainer")
        self.password_container.setStyleSheet("""
            QFrame#inputContainer {
                background-color: #f3f4f6;
                border: 2px solid transparent;
                border-radius: 12px;
            }
            QFrame#inputContainer:hover {
                border: 2px solid #667eea;
            }
        """)
        password_layout = QtWidgets.QHBoxLayout(self.password_container)
        password_layout.setContentsMargins(16, 0, 16, 0)
        password_layout.setSpacing(12)
        
        self.password_icon = QtWidgets.QLabel("🔒")
        self.password_icon.setStyleSheet("font-size: 18px; background: transparent;")
        password_layout.addWidget(self.password_icon)
        
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                font-size: 15px;
                color: #1f2937;
                padding: 0;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        
        # Toggle password visibility button
        self.toggle_password_btn = QtWidgets.QPushButton("👁")
        self.toggle_password_btn.setFixedSize(36, 36)
        self.toggle_password_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(102, 126, 234, 0.1);
            }
        """)
        self.toggle_password_btn.setCheckable(True)
        password_layout.addWidget(self.toggle_password_btn)
        
        # Keep the action for compatibility
        self.toggle_password_action = QtWidgets.QAction(self.password_input)
        self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye-off.png"))
        self.toggle_password_action.setCheckable(True)
        
        self.card_layout.addWidget(self.password_container)
        
        self.card_layout.addSpacing(30)
        
        # Login button with gradient
        self.login_button = QtWidgets.QPushButton("Sign In")
        self.login_button.setMinimumHeight(54)
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.5px;
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
        self.card_layout.addWidget(self.login_button)
        
        self.card_layout.addSpacing(20)
        
        # Footer text
        self.footer_label = QtWidgets.QLabel("Default: admin / admin")
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.footer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.card_layout.addWidget(self.footer_label)
        
        self.card_layout.addStretch()
        
        # Add card to horizontal layout
        card_h_layout.addWidget(self.card_widget)
        card_h_layout.addStretch(1)
        
        self.main_layout.addLayout(card_h_layout)
        
        # Bottom spacer
        self.main_layout.addStretch(1)
        
        # Copyright footer
        self.copyright_label = QtWidgets.QLabel("© 2026 GST Billing Software")
        self.copyright_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                background: transparent;
            }
        """)
        self.copyright_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.copyright_label)
    
    def setup_animations(self):
        """Setup entrance animations"""
        # Fade in effect for card
        self.card_widget.setWindowOpacity(0)
        QTimer.singleShot(100, self.animate_card_entrance)
    
    def animate_card_entrance(self):
        """Animate card entrance"""
        # Simple visual effect - the card is already visible
        pass

    def setup_connections(self):
        """Set up signal connections"""
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.focus_password)
        self.toggle_password_btn.toggled.connect(self.toggle_password_visibility)
        
        # Focus styling for inputs
        self.username_input.focusInEvent = lambda e: self.on_input_focus(self.username_container, True, e)
        self.username_input.focusOutEvent = lambda e: self.on_input_focus(self.username_container, False, e)
        self.password_input.focusInEvent = lambda e: self.on_input_focus(self.password_container, True, e)
        self.password_input.focusOutEvent = lambda e: self.on_input_focus(self.password_container, False, e)
    
    def focus_password(self):
        """Move focus to password field"""
        self.password_input.setFocus()
    
    def on_input_focus(self, container, focused, event):
        """Handle input focus styling"""
        QtWidgets.QLineEdit.focusInEvent(self.username_input, event) if focused else QtWidgets.QLineEdit.focusOutEvent(self.username_input, event)
        if focused:
            container.setStyleSheet("""
                QFrame#inputContainer {
                    background-color: #f3f4f6;
                    border: 2px solid #667eea;
                    border-radius: 12px;
                }
            """)
        else:
            container.setStyleSheet("""
                QFrame#inputContainer {
                    background-color: #f3f4f6;
                    border: 2px solid transparent;
                    border-radius: 12px;
                }
                QFrame#inputContainer:hover {
                    border: 2px solid #667eea;
                }
            """)

    def toggle_password_visibility(self, checked):
        """Toggle password visibility and icon"""
        if checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.toggle_password_btn.setText("🙈")
            self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye.png"))
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.toggle_password_btn.setText("👁")
            self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye-off.png"))

    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        print(f"Login attempt: username='{username}', password='{password}'")  # Debug
        
        if not username or not password:
            QtWidgets.QMessageBox.warning(
                self, 
                "Login Error", 
                "Please enter both username and password."
            )
            return
        
        # TODO: Add actual authentication logic here
        # For now, accept any non-empty credentials
        if self.authenticate(username, password):
            print("Authentication successful, emitting signal...")  # Debug
            self.login_successful.emit()
        else:
            QtWidgets.QMessageBox.warning(
                self, 
                "Login Failed", 
                "Invalid username or password."
            )
            self.password_input.clear()
            self.username_input.setFocus()

    def authenticate(self, username, password):
        """
        Authenticate user credentials
        Override this method to implement actual authentication
        """
        # Temporary: Accept admin/admin for demo
        return username == "admin" and password == "admin"

    def reset_form(self):
        """Reset the login form"""
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()
