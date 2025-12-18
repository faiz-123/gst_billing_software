#!/usr/bin/env python3
"""
Test script for the new authentication screens
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import pyqtSlot

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from screens import LoginScreen, CompanySelectionScreen, CompanyCreationScreen


class AuthFlow(QMainWindow):
    """Test application for authentication flow"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software - Authentication Flow Test")
        self.setMinimumSize(1200, 800)
        
        # Create stacked widget to manage screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.login_screen = LoginScreen()
        self.company_selection_screen = CompanySelectionScreen()
        self.company_creation_screen = CompanyCreationScreen()
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.company_selection_screen)
        self.stacked_widget.addWidget(self.company_creation_screen)
        
        # Set up connections
        self.setup_connections()
        
        # Start with login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def setup_connections(self):
        """Connect screen signals"""
        # Login successful -> Company Selection
        self.login_screen.login_successful.connect(self.show_company_selection)
        
        # Company Selection -> New Company Creation
        self.company_selection_screen.new_company_requested.connect(self.show_company_creation)
        
        # Company Selection -> Company Selected (would go to main app)
        self.company_selection_screen.company_selected.connect(self.company_selected)
        
        # Company Creation -> Back to Selection or Main App
        self.company_creation_screen.company_created.connect(self.company_created)
        self.company_creation_screen.cancelled.connect(self.show_company_selection)

    @pyqtSlot()
    def show_company_selection(self):
        """Show company selection screen"""
        print("Signal received: Showing company selection screen")  # Debug
        self.stacked_widget.setCurrentWidget(self.company_selection_screen)
        # Refresh companies list in case new company was added
        self.company_selection_screen.refresh_companies()

    @pyqtSlot()
    def show_company_creation(self):
        """Show company creation screen"""
        self.stacked_widget.setCurrentWidget(self.company_creation_screen)
        # Reset form for new company
        self.company_creation_screen.reset_form()

    @pyqtSlot(str)
    def company_selected(self, company_name):
        """Handle company selection"""
        print(f"Company selected: {company_name}")
        # In real app, this would load the main application with selected company
        # For now, just show a message
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self, 
            "Company Selected", 
            f"Selected company: {company_name}\\n\\nIn the real application, this would load the main dashboard."
        )

    @pyqtSlot(dict)
    def company_created(self, company_data):
        """Handle company creation"""
        print(f"Company created: {company_data['company_name']}")
        # Add the new company to the company selection screen
        self.company_selection_screen.add_company(company_data)
        # Go back to company selection to show the new company
        self.show_company_selection()


def main():
    """Main function to run the authentication flow test"""
    app = QApplication(sys.argv)
    app.setApplicationName("GST Billing Software - Auth Flow Test")
    
    # Create and show auth flow window
    auth_flow = AuthFlow()
    auth_flow.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
