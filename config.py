"""
Configuration and file handling
"""

import json
import os
from datetime import datetime

class Config:
    def __init__(self, config_file="data/config.json"):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
            else:
                # Create default config
                self.config_data = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config_data = self.get_default_config()
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            "app": {
                "name": "GST Billing Software",
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat()
            },
            "company": {
                "current_company_id": None,
                "name": "",
                "gstin": "",
                "address": "",
                "mobile": "",
                "email": ""
            },
            "invoice": {
                "auto_generate_number": True,
                "number_prefix": "INV",
                "starting_number": 1001,
                "default_tax_rate": 18.0
            },
            "ui": {
                "theme": "default",
                "window_maximized": True,
                "last_screen": "dashboard"
            },
            "database": {
                "path": "data/gst_billing.db",
                "backup_enabled": True,
                "backup_interval_days": 7
            }
        }
    
    def get(self, key, default=None):
        """Get configuration value using dot notation (e.g., 'app.name')"""
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        data = self.config_data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save_config()
    
    def get_company_info(self):
        """Get current company information"""
        return self.get('company', {})
    
    def set_company_info(self, company_data):
        """Set current company information"""
        for key, value in company_data.items():
            self.set(f'company.{key}', value)
    
    def get_current_company_id(self):
        """Get the current company ID"""
        return self.get('company.current_company_id')
    
    def set_current_company_id(self, company_id):
        """Set the current company ID"""
        self.set('company.current_company_id', company_id)
    
    def get_next_invoice_number(self):
        """Get the next invoice number"""
        prefix = self.get('invoice.number_prefix', 'INV')
        starting_number = self.get('invoice.starting_number', 1001)
        
        # Here you would typically check the database for the last used number
        # For now, we'll use the starting number
        return f"{prefix}{starting_number}"
    
    def get_window_settings(self):
        """Get window settings"""
        return {
            'maximized': self.get('ui.window_maximized', True),
            'last_screen': self.get('ui.last_screen', 'dashboard')
        }
    
    def set_window_settings(self, maximized=None, last_screen=None):
        """Set window settings"""
        if maximized is not None:
            self.set('ui.window_maximized', maximized)
        if last_screen is not None:
            self.set('ui.last_screen', last_screen)

# Global config instance
config = Config()
