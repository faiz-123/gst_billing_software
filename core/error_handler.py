"""
Error Handler - Centralized error handling and user feedback system

Provides:
- Error recovery mechanisms
- Transaction rollback support
- User-friendly error dialogs
- Logging integration
"""

from typing import Optional, Callable, Any, Tuple
from functools import wraps
import traceback

from core.logger import get_logger
from core.exceptions import (
    BillingException, DatabaseException, TransactionRollbackError,
    DatabaseLocked, DatabaseConnectionError
)

logger = get_logger(__name__)


class ErrorHandler:
    """Centralized error handling system"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: Optional[str] = None,
                        show_dialog: bool = True) -> Tuple[bool, str]:
        """
        Handle an exception with logging and user feedback
        
        Args:
            exception: The exception to handle
            context: Context information about where error occurred
            show_dialog: Whether to show error dialog (set False for non-GUI contexts)
            
        Returns:
            Tuple of (success, message)
        """
        error_message = ""
        error_type = exception.__class__.__name__
        
        # Log the exception
        if context:
            logger.error(f"Error in {context}: {error_type}", exc_info=True)
        else:
            logger.error(f"Unhandled error: {error_type}", exc_info=True)
        
        # Get user-friendly message
        if isinstance(exception, BillingException):
            error_message = exception.to_user_message()
            logger.error(f"Business Logic Error [{exception.error_code}]: {error_message}")
        elif isinstance(exception, DatabaseException):
            if isinstance(exception, DatabaseLocked):
                error_message = exception.to_user_message()
                logger.warning(f"Database locked, user should retry")
            elif isinstance(exception, DatabaseConnectionError):
                error_message = exception.to_user_message()
                logger.critical(f"Database connection failed")
            else:
                error_message = exception.to_user_message()
                logger.error(f"Database error: {str(exception)}")
        else:
            # Generic exception
            error_message = f"An unexpected error occurred: {str(exception)}"
            logger.error(f"Unexpected error type {error_type}: {str(exception)}")
        
        # Show user dialog if needed
        if show_dialog:
            try:
                from PySide6.QtWidgets import QMessageBox, QApplication
                app = QApplication.instance()
                if app:
                    ErrorDialog.show_error(
                        title="Error",
                        message=error_message,
                        details=str(exception) if isinstance(exception, BillingException) else traceback.format_exc()
                    )
            except Exception as dialog_error:
                logger.error(f"Failed to show error dialog: {str(dialog_error)}")
        
        return False, error_message
    
    @staticmethod
    def handle_validation_error(field_name: str, error_message: str,
                               show_dialog: bool = True) -> Tuple[bool, str]:
        """
        Handle validation error
        
        Args:
            field_name: Name of field that failed validation
            error_message: User-friendly error message
            show_dialog: Whether to show error dialog
            
        Returns:
            Tuple of (success, message)
        """
        logger.warning(f"Validation error in field '{field_name}': {error_message}")
        
        if show_dialog:
            try:
                from PySide6.QtWidgets import QMessageBox, QApplication
                app = QApplication.instance()
                if app:
                    ErrorDialog.show_warning(
                        title="Validation Error",
                        message=error_message
                    )
            except Exception as e:
                logger.error(f"Failed to show validation dialog: {str(e)}")
        
        return False, error_message
    
    @staticmethod
    def handle_confirmation(title: str, message: str) -> bool:
        """
        Show confirmation dialog and return user choice
        
        Args:
            title: Dialog title
            message: Message to display
            
        Returns:
            True if user clicked OK, False if Cancel
        """
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            app = QApplication.instance()
            if app:
                return ErrorDialog.show_confirmation(title, message)
        except Exception as e:
            logger.error(f"Failed to show confirmation dialog: {str(e)}")
        
        return False


class ErrorDialog:
    """PySide6 error dialog system"""
    
    @staticmethod
    def show_error(title: str, message: str, details: Optional[str] = None):
        """Show error dialog"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            from PySide6.QtCore import Qt
            
            app = QApplication.instance()
            if not app:
                return
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(title)
            msg.setText(message)
            
            if details:
                msg.setDetailedText(details)
            
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except ImportError:
            # GUI not available
            logger.error(f"{title}: {message}")
    
    @staticmethod
    def show_warning(title: str, message: str, details: Optional[str] = None):
        """Show warning dialog"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            app = QApplication.instance()
            if not app:
                return
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(title)
            msg.setText(message)
            
            if details:
                msg.setDetailedText(details)
            
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except ImportError:
            # GUI not available
            logger.warning(f"{title}: {message}")
    
    @staticmethod
    def show_confirmation(title: str, message: str) -> bool:
        """Show confirmation dialog, return True if OK clicked"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            app = QApplication.instance()
            if not app:
                return False
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            
            result = msg.exec()
            from PySide6.QtWidgets import QMessageBox as MB
            return result == MB.Ok
        except ImportError:
            # GUI not available
            logger.warning(f"{title}: {message}")
            return False
    
    @staticmethod
    def show_info(title: str, message: str):
        """Show info dialog"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            app = QApplication.instance()
            if not app:
                return
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except ImportError:
            # GUI not available
            logger.info(f"{title}: {message}")


class TransactionManager:
    """Manage database transactions with rollback support"""
    
    def __init__(self, db):
        self.db = db
        self.is_transaction_active = False
    
    def begin_transaction(self):
        """Begin a database transaction"""
        try:
            self.db.conn.execute("BEGIN TRANSACTION")
            self.is_transaction_active = True
            logger.debug("Transaction started")
        except Exception as e:
            logger.error(f"Failed to start transaction: {e}")
            raise DatabaseConnectionError(str(e))
    
    def commit_transaction(self):
        """Commit the current transaction"""
        try:
            if self.is_transaction_active:
                self.db.conn.commit()
                self.is_transaction_active = False
                logger.debug("Transaction committed")
        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            self.rollback_transaction()
            raise DatabaseException(f"Failed to commit transaction: {e}")
    
    def rollback_transaction(self, operation: Optional[str] = None):
        """Rollback the current transaction"""
        try:
            if self.is_transaction_active:
                self.db.conn.rollback()
                self.is_transaction_active = False
                op_text = f" for {operation}" if operation else ""
                logger.warning(f"Transaction rolled back{op_text}")
        except Exception as e:
            logger.critical(f"Failed to rollback transaction: {e}")
            raise TransactionRollbackError(operation or "unknown", str(e))
    
    def __enter__(self):
        """Context manager entry"""
        self.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is not None:
            self.rollback_transaction()
            return False  # Re-raise the exception
        else:
            self.commit_transaction()
            return True


def handle_errors(operation_name: str = "Operation", show_dialog: bool = True):
    """
    Decorator to handle errors in functions
    
    Usage:
        @handle_errors("Create Invoice")
        def create_invoice(self, data):
            # Function code
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Starting: {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed: {operation_name}")
                return result
            except BillingException as e:
                logger.error(f"Business logic error in {operation_name}: {e.error_code}")
                return ErrorHandler.handle_exception(e, operation_name, show_dialog)
            except DatabaseException as e:
                logger.error(f"Database error in {operation_name}")
                return ErrorHandler.handle_exception(e, operation_name, show_dialog)
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {type(e).__name__}", exc_info=True)
                return ErrorHandler.handle_exception(e, operation_name, show_dialog)
        
        return wrapper
    return decorator


__all__ = [
    'ErrorHandler',
    'ErrorDialog',
    'TransactionManager',
    'handle_errors',
]
