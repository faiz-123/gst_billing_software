#!/usr/bin/env python3
"""
GST Billing Software Launcher
Run this file to start the application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Main application entry point"""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("GST Billing Software")
        app.setApplicationVersion("1.0.0")
        
        # Import and create main window
        from main import MainWindow
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please make sure PyQt5 is installed:")
        print("pip install PyQt5")
        sys.exit(1)
        
    except Exception as e:
        print(f"Application Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# if __name__ == "__main__":
#     main()
