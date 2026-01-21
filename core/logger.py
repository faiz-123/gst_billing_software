"""
Centralized logging system for GST Billing Software
Handles all logging with rotation, different levels, and performance metrics
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import time
from functools import wraps
from typing import Any


class BillingLogger:
    """Centralized logger for the application"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BillingLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize the logger with file rotation and console handlers"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger('BillingSoftware')
        self._logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self._logger.handlers = []
        
        # Create log file path
        log_file = os.path.join(log_dir, 'app.log')
        
        # File handler with rotation (10MB per file, keep 30 files = 300MB)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=30  # Keep 30 backup files (30 days worth)
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter with timestamp, level, module name
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)-8s] [%(name)s] [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '[%(levelname)-8s] [%(funcName)s] - %(message)s'
        )
        
        # Add handlers
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(console_formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self._logger
    
    @staticmethod
    def debug(message: str, **kwargs):
        """Log debug message"""
        logger = BillingLogger()._logger
        logger.debug(message, extra=kwargs)
    
    @staticmethod
    def info(message: str, **kwargs):
        """Log info message"""
        logger = BillingLogger()._logger
        logger.info(message, extra=kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        """Log warning message"""
        logger = BillingLogger()._logger
        logger.warning(message, extra=kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        """Log error message"""
        logger = BillingLogger()._logger
        logger.error(message, extra=kwargs)
    
    @staticmethod
    def critical(message: str, **kwargs):
        """Log critical message"""
        logger = BillingLogger()._logger
        logger.critical(message, extra=kwargs)


# Convenience function to get logger
def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    Usage: logger = get_logger(__name__)
    """
    logger = BillingLogger().get_logger()
    return logging.getLogger(f'BillingSoftware.{module_name}')


# Performance tracking decorator
def log_performance(func):
    """
    Decorator to log function execution time
    Usage:
        @log_performance
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            logger.debug(f"Starting execution of {func.__name__}")
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log warning if function takes more than 1 second
            if execution_time > 1.0:
                logger.warning(
                    f"{func.__name__} took {execution_time:.2f}s (slow operation)",
                    extra={'execution_time': execution_time}
                )
            else:
                logger.debug(
                    f"{func.__name__} completed in {execution_time:.4f}s",
                    extra={'execution_time': execution_time}
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.4f}s: {str(e)}",
                extra={'execution_time': execution_time, 'error': str(e)},
                exc_info=True
            )
            raise
    
    return wrapper


# User action tracking
class UserActionLogger:
    """Track all user actions like invoice creation, payment, deletion"""
    
    @staticmethod
    def log_action(action_type: str, entity_type: str, entity_id: Any, details: str = "", user: str = "system"):
        """
        Log a user action
        
        Args:
            action_type: CREATE, UPDATE, DELETE, VIEW, EXPORT, PRINT
            entity_type: Invoice, Payment, Party, Product, etc.
            entity_id: ID of the entity
            details: Additional details about the action
            user: User who performed the action
        """
        logger = get_logger('UserActions')
        message = f"[{action_type}] {entity_type}(id={entity_id}) by user={user}"
        if details:
            message += f" - {details}"
        
        logger.info(message)
    
    @staticmethod
    def log_invoice_created(invoice_id: str, invoice_no: str, party_id: int, amount: float, user: str = "system"):
        """Log invoice creation"""
        UserActionLogger.log_action(
            "CREATE",
            "Invoice",
            invoice_id,
            f"Number={invoice_no}, Party={party_id}, Amount={amount}",
            user
        )
    
    @staticmethod
    def log_invoice_updated(invoice_id: str, changes: dict, user: str = "system"):
        """Log invoice update"""
        UserActionLogger.log_action(
            "UPDATE",
            "Invoice",
            invoice_id,
            f"Changes={changes}",
            user
        )
    
    @staticmethod
    def log_invoice_deleted(invoice_id: str, invoice_no: str, user: str = "system"):
        """Log invoice deletion"""
        UserActionLogger.log_action(
            "DELETE",
            "Invoice",
            invoice_id,
            f"Number={invoice_no}",
            user
        )
    
    @staticmethod
    def log_payment_recorded(payment_id: str, party_id: int, amount: float, user: str = "system"):
        """Log payment recording"""
        UserActionLogger.log_action(
            "CREATE",
            "Payment",
            payment_id,
            f"Party={party_id}, Amount={amount}",
            user
        )
    
    @staticmethod
    def log_payment_deleted(payment_id: str, user: str = "system"):
        """Log payment deletion"""
        UserActionLogger.log_action(
            "DELETE",
            "Payment",
            payment_id,
            user=user
        )
    
    @staticmethod
    def log_party_created(party_id: int, party_name: str, user: str = "system"):
        """Log party creation"""
        UserActionLogger.log_action(
            "CREATE",
            "Party",
            party_id,
            f"Name={party_name}",
            user
        )
    
    @staticmethod
    def log_party_updated(party_id: int, party_name: str, user: str = "system"):
        """Log party update"""
        UserActionLogger.log_action(
            "UPDATE",
            "Party",
            party_id,
            f"Name={party_name}",
            user
        )
    
    @staticmethod
    def log_product_created(product_id: int, product_name: str, user: str = "system"):
        """Log product creation"""
        UserActionLogger.log_action(
            "CREATE",
            "Product",
            product_id,
            f"Name={product_name}",
            user
        )
    
    @staticmethod
    def log_export_action(export_type: str, format_type: str, record_count: int, user: str = "system"):
        """Log export actions"""
        UserActionLogger.log_action(
            "EXPORT",
            export_type,
            "batch",
            f"Format={format_type}, RecordCount={record_count}",
            user
        )
    
    @staticmethod
    def log_report_generated(report_type: str, filters: dict, user: str = "system"):
        """Log report generation"""
        UserActionLogger.log_action(
            "GENERATE",
            "Report",
            report_type,
            f"Filters={filters}",
            user
        )


# SQL Query logging
class SQLLogger:
    """Log SQL queries with execution time"""
    
    @staticmethod
    def log_query(query: str, params: tuple = (), execution_time: float = 0.0, row_count: int = 0):
        """
        Log a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            execution_time: Time taken to execute (in seconds)
            row_count: Number of rows returned/affected
        """
        logger = get_logger('DatabaseQueries')
        
        # Hide sensitive parameters in logs
        safe_query = query
        if params:
            # Don't log actual parameter values for security
            param_count = len(params)
            safe_query = f"{query} [with {param_count} params]"
        
        # Log performance warning for slow queries
        if execution_time > 0.5:  # More than 500ms
            logger.warning(
                f"SLOW QUERY ({execution_time:.3f}s, rows={row_count}): {safe_query}"
            )
        else:
            logger.debug(
                f"Query ({execution_time:.4f}s, rows={row_count}): {safe_query}"
            )


# Singleton instance
_logger_instance = BillingLogger()

# Export main functions
__all__ = [
    'get_logger',
    'log_performance',
    'UserActionLogger',
    'SQLLogger',
    'BillingLogger'
]
