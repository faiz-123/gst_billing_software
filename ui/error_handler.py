"""
UI Error Dialog Utilities

Provides convenient error handling for PySide6 forms and dialogs.
Integrates with the error handling system for consistent user feedback.
"""

from typing import Optional, Callable
from functools import wraps

from core.error_handler import ErrorDialog, ErrorHandler
from core.exceptions import BillingException
from core.logger import get_logger

logger = get_logger(__name__)


class UIErrorHandler:
    """Error handling utilities for UI components"""
    
    @staticmethod
    def show_error(title: str, message: str, details: Optional[str] = None):
        """
        Show error dialog to user
        
        Args:
            title: Dialog title
            message: Error message
            details: Optional detailed error information
        """
        logger.error(f"UI Error [{title}]: {message}")
        ErrorDialog.show_error(title, message, details)
    
    @staticmethod
    def show_validation_error(field_name: str, message):
        """
        Show validation error for a specific field
        
        Args:
            field_name: Name of field that failed validation
            message: Error message (str or list of str)
        """
        # Handle both string and list inputs
        if isinstance(message, list):
            message_text = "\n".join(message) if message else "Validation error"
        else:
            message_text = str(message)
        
        logger.warning(f"Validation Error [{field_name}]: {message_text}")
        ErrorDialog.show_warning("Validation Error", message_text)
    
    @staticmethod
    def show_success(title: str, message: str):
        """
        Show success message to user
        
        Args:
            title: Dialog title
            message: Success message
        """
        logger.info(f"UI Success [{title}]: {message}")
        ErrorDialog.show_info(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """
        Show warning dialog to user
        
        Args:
            title: Dialog title
            message: Warning message
        """
        logger.warning(f"UI Warning [{title}]: {message}")
        ErrorDialog.show_warning(title, message)
    
    @staticmethod
    def ask_confirmation(title: str, message: str) -> bool:
        """
        Ask user for confirmation
        
        Args:
            title: Dialog title
            message: Confirmation message
            
        Returns:
            True if user clicked OK, False if Cancel
        """
        logger.debug(f"UI Confirmation [{title}]: {message}")
        return ErrorDialog.show_confirmation(title, message)
    
    @staticmethod
    def show_exception(exception: BillingException, context: Optional[str] = None):
        """
        Display exception to user with proper formatting
        
        Args:
            exception: The exception to display
            context: Optional context about where error occurred
        """
        if context:
            logger.error(f"Exception in {context}: {exception.error_code}")
        else:
            logger.error(f"Exception: {exception.error_code}")
        
        UIErrorHandler.show_error(
            title="Error",
            message=exception.to_user_message(),
            details=f"Error Code: {exception.error_code}"
        )
    
    @staticmethod
    def handle_form_error(exception: Exception, form_name: str = "Form"):
        """
        Handle exception from form submission
        
        Args:
            exception: The exception that occurred
            form_name: Name of the form (for logging)
        """
        if isinstance(exception, BillingException):
            UIErrorHandler.show_exception(exception, form_name)
        else:
            logger.error(f"Error in {form_name}: {str(exception)}", exc_info=True)
            UIErrorHandler.show_error(
                title="Error",
                message=f"An error occurred in {form_name}. Please try again.",
                details=str(exception)
            )


def handle_ui_errors(operation_name: str = "Operation"):
    """
    Decorator for handling errors in UI operations
    
    Usage:
        @handle_ui_errors("Create Invoice")
        def on_create_button_clicked(self):
            # Form code
            pass
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"UI Operation Start: {operation_name}")
                result = func(*args, **kwargs)
                logger.debug(f"UI Operation Complete: {operation_name}")
                return result
            except BillingException as e:
                logger.error(f"Business Logic Error in {operation_name}: {e.error_code}")
                UIErrorHandler.show_exception(e, operation_name)
                return None
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
                UIErrorHandler.handle_form_error(e, operation_name)
                return None
        
        return wrapper
    return decorator


class FormValidator:
    """Helper for form field validation with error display"""
    
    def __init__(self, form_name: str = "Form"):
        self.form_name = form_name
        self.has_errors = False
        self.errors = {}
    
    def add_error(self, field_name: str, error_message: str):
        """Add a validation error for a field"""
        self.errors[field_name] = error_message
        self.has_errors = True
        logger.warning(f"Validation Error in {self.form_name}.{field_name}: {error_message}")
    
    def clear_errors(self):
        """Clear all validation errors"""
        self.errors = {}
        self.has_errors = False
    
    def show_errors(self):
        """Display all validation errors to user"""
        if self.has_errors:
            error_message = "Please fix the following errors:\n\n"
            error_message += "\n".join(f"• {field}: {msg}" for field, msg in self.errors.items())
            UIErrorHandler.show_validation_error(self.form_name, error_message)
    
    def validate_required(self, field_name: str, value: str, display_name: str = None) -> bool:
        """
        Validate required field
        
        Args:
            field_name: Internal field name
            value: Field value to validate
            display_name: User-friendly field name
            
        Returns:
            True if valid
        """
        display_name = display_name or field_name
        if not value or not value.strip():
            self.add_error(field_name, f"{display_name} is required")
            return False
        return True
    
    def validate_email(self, field_name: str, email: str, display_name: str = None) -> bool:
        """
        Validate email field
        
        Args:
            field_name: Internal field name
            email: Email to validate
            display_name: User-friendly field name
            
        Returns:
            True if valid
        """
        display_name = display_name or field_name
        if email and not self._is_valid_email(email):
            self.add_error(field_name, f"{display_name} is not a valid email address")
            return False
        return True
    
    def validate_numeric(self, field_name: str, value: str, display_name: str = None, min_value: float = None) -> bool:
        """
        Validate numeric field
        
        Args:
            field_name: Internal field name
            value: Value to validate
            display_name: User-friendly field name
            min_value: Minimum allowed value
            
        Returns:
            True if valid
        """
        display_name = display_name or field_name
        try:
            num_value = float(value)
            if min_value is not None and num_value < min_value:
                self.add_error(field_name, f"{display_name} must be at least {min_value}")
                return False
            return True
        except ValueError:
            self.add_error(field_name, f"{display_name} must be a valid number")
            return False
    
    def validate_length(self, field_name: str, value: str, min_len: int = None, max_len: int = None, display_name: str = None) -> bool:
        """
        Validate string length
        
        Args:
            field_name: Internal field name
            value: Value to validate
            min_len: Minimum length
            max_len: Maximum length
            display_name: User-friendly field name
            
        Returns:
            True if valid
        """
        display_name = display_name or field_name
        length = len(value)
        
        if min_len is not None and length < min_len:
            self.add_error(field_name, f"{display_name} must be at least {min_len} characters")
            return False
        
        if max_len is not None and length > max_len:
            self.add_error(field_name, f"{display_name} must not exceed {max_len} characters")
            return False
        
        return True
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Simple email validation"""
        return "@" in email and "." in email.split("@")[1] if "@" in email else False


__all__ = [
    'UIErrorHandler',
    'handle_ui_errors',
    'FormValidator',
]
