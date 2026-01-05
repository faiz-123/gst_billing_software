#!/usr/bin/env python3
"""
Complete GST Billing Software with Authentication Flow
This integrates the login/company selection with the main application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import pyqtSlot

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from screens import LoginScreen, CompanySelectionScreen, CompanyCreationScreen
from main import MainWindow


class AuthenticatedApp(QMainWindow):
    """Main application with authentication flow"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GST Billing Software")
        # Start with login screen size, will maximize later for other screens
        self.resize(500, 700)
        self.setMinimumSize(500, 700)
        
        # Store the selected company info
        self.selected_company = None
        
        # Create stacked widget to manage different application states
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create authentication screens
        self.login_screen = LoginScreen()
        self.company_selection_screen = CompanySelectionScreen()
        self.company_creation_screen = CompanyCreationScreen()
        
        # Create main application (will be shown after company selection)
        self.main_app = None
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.company_selection_screen)
        self.stacked_widget.addWidget(self.company_creation_screen)
        
        # Set up connections
        self.setup_connections()
        
        # Start with login screen (normal size)
        self.stacked_widget.setCurrentWidget(self.login_screen)
        # Don't maximize for login screen - keep normal size

    def setup_connections(self):
        """Connect screen signals"""
        # Login successful -> Company Selection
        self.login_screen.login_successful.connect(self.show_company_selection)
        
        # Company Selection -> New Company Creation
        self.company_selection_screen.new_company_requested.connect(self.show_company_creation)
        
        # Company Selection -> Edit Company
        self.company_selection_screen.edit_company_requested.connect(self.show_company_edit)
        
        # Company Selection -> Delete Company
        self.company_selection_screen.delete_company_requested.connect(self.delete_company)
        
        # Company Selection -> Company Selected (go to main app)
        self.company_selection_screen.company_selected.connect(self.company_selected)
        
        # Company Creation -> Back to Selection
        self.company_creation_screen.company_created.connect(self.company_created)
        self.company_creation_screen.company_saved.connect(lambda data: print(f"Company saved: {data['company_name']}"))
        self.company_creation_screen.cancelled.connect(self.show_company_selection)

    @pyqtSlot()
    def show_company_selection(self):
        """Show company selection screen"""
        print("Signal received: Showing company selection screen")
        self.stacked_widget.setCurrentWidget(self.company_selection_screen)
        # Maximize window for company selection
        self.showMaximized()
        # Refresh companies list in case new company was added
        self.company_selection_screen.refresh_companies()

    @pyqtSlot()
    def show_company_creation(self):
        """Show company creation screen"""
        print("Showing company creation screen")
        self.stacked_widget.setCurrentWidget(self.company_creation_screen)
        # Maximize window for company creation
        self.showMaximized()
        # Reset form for new company
        self.company_creation_screen.reset_form()

    @pyqtSlot(dict)
    def show_company_edit(self, company_data):
        """Show company edit screen"""
        print(f"Showing company edit screen for: {company_data.get('name', 'Unknown')}")
        
        # Create or reuse company creation screen for editing
        # Create new instance for editing with company data
        edit_screen = CompanyCreationScreen(parent=self, company_data=company_data)
        
        # Connect edit screen signals
        edit_screen.company_saved.connect(self.company_updated)  # Edit mode emits company_saved
        edit_screen.company_created.connect(self.company_updated)  # Just in case, handle both
        edit_screen.cancelled.connect(self.show_company_selection)
        
        # Add to stack and show
        self.stacked_widget.addWidget(edit_screen)
        self.stacked_widget.setCurrentWidget(edit_screen)
        self.showMaximized()

    @pyqtSlot(str)
    def company_selected(self, company_name):
        """Handle company selection - Navigate to main application"""
        print(f"Company selected: {company_name}")
        self.selected_company = company_name
        
        # Update window title to show selected company
        self.setWindowTitle(f"GST Billing Software - {company_name}")
        
        # Create and show main application
        self.show_main_application()

    @pyqtSlot(dict)
    def company_created(self, company_data):
        """Handle company creation - just navigate back and refresh"""
        print(f"Company created: {company_data['company_name']}")
        # Don't add to database here - it's already added in save_company_data()
        # Just go back to company selection and refresh
        self.show_company_selection()

    @pyqtSlot(dict)
    def company_updated(self, company_data):
        """Handle company update"""
        print(f"Company updated: {company_data['company_name']}")
        # Refresh the company selection screen to show updated data
        self.show_company_selection()

    @pyqtSlot(dict)
    def delete_company(self, company_data):
        """Handle company deletion with confirmation"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Show confirmation dialog
        company_name = company_data.get('name', 'Unknown Company')
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{company_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Import database here to avoid circular imports
                from database import db
                
                # Delete company from database
                db.delete_company(company_data['id'])
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Company '{company_name}' has been deleted successfully."
                )
                
                # Refresh company selection screen
                self.show_company_selection()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete company:\n{str(e)}"
                )

    def show_main_application(self):
        """Show the main GST billing application"""
        try:
            # Import the main application
            from main import MainWindow
            
            # Create main application with full interface (sidebar, etc.)
            # Pass the selected company name to the main window
            main_app = MainWindow(company_name=self.selected_company)
            
            # Add main application to stacked widget
            self.stacked_widget.addWidget(main_app)
            
            # Show main application
            self.stacked_widget.setCurrentWidget(main_app)
            
            # Maximize window for main application
            self.showMaximized()
            
            # Update window title
            if self.selected_company:
                self.setWindowTitle(f"GST Billing Software - {self.selected_company}")
            
            print(f"Main application with sidebar opened for company: {self.selected_company}")
            
        except Exception as e:
            print(f"Error opening main application: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Application Error",
                f"Could not open main application:\\n{str(e)}"
            )

    def show_company_selector(self):
        """Method to return to company selection (for logout functionality)"""
        self.show_company_selection()

    def show_login(self):
        """Method to return to login screen (for logout functionality)"""
        self.stacked_widget.setCurrentWidget(self.login_screen)
        # Restore normal window size for login
        self.showNormal()
        self.resize(400, 700)
        # Reset login form
        self.login_screen.reset_form()


def main():
    """Main function to run the complete application"""
    app = QApplication(sys.argv)
    app.setApplicationName("GST Billing Software")
    
    # Create and show authenticated app
    auth_app = AuthenticatedApp()
    auth_app.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
