"""
Widgets module - Reusable UI components
"""

from .common_widgets import (
    # General widgets
    CustomButton, CustomInput, CustomLabel, CustomComboBox,
    CustomTable, StatCard, TableActionButton, ListTable, TableFrame,
    SearchInputContainer, RefreshButton, ListHeader, StatsContainer,
    SearchBox, FormField, SidebarButton, Sidebar,
    # Dialog-specific widgets
    DialogInput, DialogComboBox, DialogEditableComboBox, DialogSpinBox, DialogDoubleSpinBox,
    DialogCheckBox, DialogTextEdit, DialogFieldGroup, DialogScrollArea,
    # Selector dialogs
    PartySelector, ProductSelector,
    # Invoice item widget and helpers
    InvoiceItemWidget, highlight_error, highlight_success, show_validation_error
)
from .filter_widget import FilterWidget

__all__ = [
    # General widgets
    'CustomButton', 'CustomInput', 'CustomLabel', 'CustomComboBox',
    'CustomTable', 'StatCard', 'TableActionButton', 'ListTable', 'TableFrame',
    'SearchInputContainer', 'RefreshButton', 'ListHeader', 'StatsContainer',
    'SearchBox', 'FormField', 'SidebarButton', 'Sidebar',
    # Dialog-specific widgets
    'DialogInput', 'DialogComboBox', 'DialogEditableComboBox', 'DialogSpinBox', 'DialogDoubleSpinBox',
    'DialogCheckBox', 'DialogTextEdit', 'DialogFieldGroup', 'DialogScrollArea',
    # Selector dialogs
    'PartySelector', 'ProductSelector',
    # Invoice item widget and helpers
    'InvoiceItemWidget', 'highlight_error', 'highlight_success', 'show_validation_error',
    # Filter widget
    'FilterWidget'
]
