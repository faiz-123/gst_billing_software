"""
Main entry point and navigation manager for GST Billing Software
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QStackedWidget
from PySide6.QtCore import Qt

# Enable WebEngine sharing BEFORE QApplication is created
# This is required for QWebEngineView to work properly
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

from theme import APP_STYLESHEET
from widgets import Sidebar
from config import config
from core.db.sqlite_db import db

# Import screens from ui module
from ui.dashboard.dashboard_screen import DashboardScreen
from ui.parties.party_list_screen import PartiesScreen
from ui.products.product_list_screen import ProductsScreen
from ui.invoices.sales.sales_invoice_list_screen import InvoicesScreen
from ui.invoices.purchase.purchase_invoice_list_screen import PurchasesScreen
from ui.payments.payment_list_screen import PaymentsScreen
from ui.receipts.receipt_list_screen import ReceiptsScreen

class MainWindow(QMainWindow):
    def __init__(self, company_name="GST Billing"):
        super().__init__()
        self.setWindowTitle("GST Billing Software")
        self.setMinimumSize(1200, 800)
        self.company_name = company_name
        
        # Always start maximized
        self.showMaximized()
        
        self.setup_ui()
        
        # Always start with dashboard as default screen
        self.navigate_to('dashboard')
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(company_name=self.company_name)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area with stacked widget
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Initialize screens
        self.screens = {
            'dashboard': DashboardScreen(),
            'parties': PartiesScreen(),
            'products': ProductsScreen(),
            'invoices': InvoicesScreen(),
            'purchases': PurchasesScreen(),
            'receipts': ReceiptsScreen(),
            'payments': PaymentsScreen()
        }
        
        # Add screens to stack
        for screen in self.screens.values():
            self.content_stack.addWidget(screen)
    
    def setup_sidebar(self):
        """Setup sidebar menu items without sections"""
        # Main navigation items
        dashboard_btn = self.sidebar.add_menu_item("Dashboard", "🏠", lambda: self.navigate_to('dashboard'))
        invoices_btn = self.sidebar.add_menu_item("Sales", "📄", lambda: self.navigate_to('invoices'))
        self.sidebar.add_menu_item("Purchases", "🛒", lambda: self.navigate_to('purchases'))
        self.sidebar.add_menu_item("Products", "📦", lambda: self.navigate_to('products'))
        self.sidebar.add_menu_item("Parties", "👥", lambda: self.navigate_to('parties'))
        self.sidebar.add_menu_item("Receipts", "💰", lambda: self.navigate_to('receipts'))
        self.sidebar.add_menu_item("Payments", "💸", lambda: self.navigate_to('payments'))
        
        self.sidebar.add_stretch()
        
        # Utility items with separator
        self.sidebar.add_separator()
        self.sidebar.add_menu_item("Settings", "🔧", lambda: self.show_coming_soon("Settings"))
        self.sidebar.add_menu_item("Backup", "💾", lambda: self.show_coming_soon("Backup"))
        
        # Set dashboard as default active
        dashboard_btn.set_active(True)
        self.sidebar.active_button = dashboard_btn
    
    def navigate_to(self, screen_name):
        """Navigate to a specific screen"""
        if screen_name in self.screens:
            screen = self.screens[screen_name]
            self.content_stack.setCurrentWidget(screen)
            
            # Save last screen
            config.set('ui.last_screen', screen_name)
            
            # Update active button based on screen
            self.update_active_sidebar_button(screen_name)
            
            # Refresh screen data if it has a refresh method
            if hasattr(screen, 'refresh_data'):
                screen.refresh_data()
                
    def update_active_sidebar_button(self, screen_name):
        """Update active sidebar button based on current screen"""
        # Map screen names to button text for finding the right button
        screen_button_map = {
            'dashboard': 'Dashboard',
            'invoices': 'Sales', 
            'purchases': 'Purchases',
            'products': 'Products',
            'parties': 'Parties',
            'receipts': 'Receipts',
            'payments': 'Payments'
        }
        
        target_text = screen_button_map.get(screen_name)
        if target_text:
            for button in self.sidebar.menu_buttons:
                if button.text == target_text:
                    self.sidebar.set_active_button(button)
                    break
    
    def show_coming_soon(self, feature_name):
        """Show coming soon message for unimplemented features"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, 
            "Coming Soon", 
            f"{feature_name} feature is coming soon!"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window settings
        config.set_window_settings(
            maximized=self.isMaximized(),
            last_screen=config.get('ui.last_screen', 'dashboard')
        )
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    
    # Initialize database
    db.create_tables()
    
    # Restore current company from config if available
    current_company_id = config.get('company.current_company_id')
    if current_company_id:
        db.set_current_company(current_company_id)
        print(f"Restored current company ID: {current_company_id}")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
