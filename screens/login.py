"""
Login Screen for GST Billing Software
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class LoginScreen(QtWidgets.QWidget):
    """Login screen for user authentication"""
    
    # Signal emitted when login is successful
    login_successful = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GST Billing Software - Login")
        self.resize(400, 700)
        self.setMinimumSize(QtCore.QSize(400, 700))
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Set up the user interface"""
        self.setStyleSheet(
            "QWidget#LoginScreen{\n"
            "  background-color: #F9FAFB;\n"
            "}\n"
            "\n"
            "QLineEdit#passwordLineEdit {\n"
            "  border: 1px solid #E5E7EB;\n"
            "  border-radius: 8px;\n"
            "  padding: 12px;\n"
            "  font-size: 16px;\n"
            "  color: #111827;\n"
            "}\n"
            "QToolButton#passwordToggleButton{\n"
            "  border: none;\n"
            "  padding: 0 10px;\n"
            "}\n"
        )
        
        # Main horizontal layout for centering the content
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setObjectName("main_layout")

        # Left spacer for centering
        spacer_left = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.main_layout.addItem(spacer_left)

        # Content widget (holds all login UI elements)
        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setMinimumSize(QtCore.QSize(350, 0))
        self.content_widget.setMaximumSize(QtCore.QSize(420, 420))
        
        # Vertical layout for content
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(18)

        # Logo label
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setMinimumSize(QtCore.QSize(300, 80))
        self.logo_label.setStyleSheet(
            "QLabel {\n"
            "    background-color: #E5E7EB;\n"
            "    border-radius: 8px;\n"
            "}\n"
        )
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_label.setText("Logo")
        self.content_layout.addWidget(self.logo_label)

        # Title label
        self.title_label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(32)
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(
            "QLabel {\n"
            "  color: #111827;\n"
            "}\n"
        )
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setText("GST Billing Software")
        self.content_layout.addWidget(self.title_label)

        # Username section
        self.username_label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(14)
        self.username_label.setFont(font)
        self.username_label.setText("Username")
        self.content_layout.addWidget(self.username_label)

        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setMinimumSize(QtCore.QSize(0, 48))
        self.username_input.setStyleSheet(
            "QLineEdit {\n"
            "  border: 1px solid #E5E7EB;\n"
            "  border-radius: 8px;\n"
            "  background-color: #FFFFFF;\n"
            "  padding: 12px;\n"
            "  font-size: 16px;\n"
            "  color: #111827;\n"
            "}\n"
        )
        self.username_input.setPlaceholderText("Enter username")
        self.content_layout.addWidget(self.username_input)

        # Password section
        self.password_label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(14)
        self.password_label.setFont(font)
        self.password_label.setText("Password")
        self.content_layout.addWidget(self.password_label)

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setMinimumSize(QtCore.QSize(0, 48))
        self.password_input.setStyleSheet(
            "QLineEdit {\n"
            "  border: 1px solid #E5E7EB;\n"
            "  border-radius: 8px;\n"
            "  background-color: #FFFFFF;\n"
            "  padding: 12px;\n"
            "  font-size: 16px;\n"
            "  color: #111827;\n"
            "}\n"
        )
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Add the eye toggle action inside QLineEdit
        self.toggle_password_action = QtWidgets.QAction(self.password_input)
        self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye-off.png"))  # Default: hidden
        self.toggle_password_action.setCheckable(True)
        
        self.content_layout.addWidget(self.password_input)

        # Login button
        self.login_button = QtWidgets.QPushButton()
        self.login_button.setMinimumSize(QtCore.QSize(0, 52))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.login_button.setFont(font)
        self.login_button.setStyleSheet(
            "QPushButton {\n"
            "  color: white;\n"
            "  border-radius: 8px;\n"
            "  font-weight: 600;\n"
            "  min-height: 52px;\n"
            "  font-size: 18px;\n"
            "  background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3B82F6, stop:1 #2563EB);\n"
            "}\n"
            "QPushButton:hover {\n"
            "  background: #2563EB;\n"
            "}\n"
        )
        self.login_button.setText("Login")
        self.content_layout.addWidget(self.login_button)

        # Add content widget to main layout
        self.main_layout.addWidget(self.content_widget)

        # Right spacer for centering
        spacer_right = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.main_layout.addItem(spacer_right)

    def setup_connections(self):
        """Set up signal connections"""
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)
        self.toggle_password_action.toggled.connect(self.toggle_password_visibility)
        self.password_input.textChanged.connect(self.on_password_text_changed)

    def on_password_text_changed(self, text):
        """Show eye icon only when there is text in the password box"""
        if text:  # If not empty, add the action if not already present
            if self.toggle_password_action not in self.password_input.actions():
                self.password_input.addAction(
                    self.toggle_password_action, QtWidgets.QLineEdit.TrailingPosition
                )
        else:  # If empty, remove the action
            self.password_input.removeAction(self.toggle_password_action)

    def toggle_password_visibility(self, checked):
        """Toggle password visibility and icon"""
        if checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye.png"))  # Show password
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.toggle_password_action.setIcon(QtGui.QIcon("assets/icons/eye-off.png"))  # Hide password

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
