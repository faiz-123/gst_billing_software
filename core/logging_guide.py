"""
Logging Configuration and Usage Guide

This module provides examples and utilities for using the logging system throughout the GST Billing application.
"""

from core.logger import get_logger, log_performance, UserActionLogger, SQLLogger

# ═══════════════════════════════════════════════════════════════════════════════
# BASIC USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

# 1. SIMPLE LOGGING IN ANY MODULE
# ───────────────────────────────────────────────────────────────────────────────
"""
In any module, at the top of the file:

    from core.logger import get_logger
    
    logger = get_logger(__name__)
    
    # Then use anywhere in the module:
    logger.debug("Debug message for detailed troubleshooting")
    logger.info("Information message about normal operations")
    logger.warning("Warning about potential issues")
    logger.error("Error occurred but app continues")
    logger.critical("Critical error, app may not continue")
"""

# 2. PERFORMANCE TRACKING WITH DECORATOR
# ───────────────────────────────────────────────────────────────────────────────
"""
Use @log_performance decorator to automatically track execution time:

    from core.logger import log_performance
    
    @log_performance
    def slow_database_query():
        # This function's execution time will be logged
        # If takes > 1 second, it will be logged as WARNING
        # If takes < 1 second, it will be logged as DEBUG
        results = db.get_invoices()
        return results

Example output in logs:
    [2026-01-21 11:19:00] [DEBUG   ] [MyModule] - slow_database_query completed in 0.2450s
    [2026-01-21 11:19:05] [WARNING ] [MyModule] - slow_database_query took 1.25s (slow operation)
"""

# 3. USER ACTION TRACKING
# ───────────────────────────────────────────────────────────────────────────────
"""
Track important user actions for audit trail:

    from core.logger import UserActionLogger
    
    # Invoice actions
    UserActionLogger.log_invoice_created("INV-001", "INV-2026-0001", party_id=5, amount=50000.00)
    UserActionLogger.log_invoice_updated("INV-001", {"status": "Paid", "amount": 50000.00})
    UserActionLogger.log_invoice_deleted("INV-001", "INV-2026-0001")
    
    # Payment actions
    UserActionLogger.log_payment_recorded("PAY-001", party_id=5, amount=10000.00)
    UserActionLogger.log_payment_deleted("PAY-001")
    
    # Party actions
    UserActionLogger.log_party_created(party_id=5, party_name="ABC Enterprises")
    UserActionLogger.log_party_updated(party_id=5, party_name="ABC Enterprises Pvt Ltd")
    
    # Product actions
    UserActionLogger.log_product_created(product_id=12, product_name="Product A")
    
    # Export/Report actions
    UserActionLogger.log_export_action("Invoices", "CSV", record_count=150)
    UserActionLogger.log_report_generated("Sales Report", {"start_date": "2026-01-01", "end_date": "2026-01-31"})

Example output in logs:
    [2026-01-21 11:19:00] [INFO    ] [BillingSoftware.UserActions] - [CREATE] Invoice(id=INV-001) by user=system - Number=INV-2026-0001, Party=5, Amount=50000.0
    [2026-01-21 11:19:05] [INFO    ] [BillingSoftware.UserActions] - [DELETE] Invoice(id=INV-001) by user=system - Number=INV-2026-0001
"""

# 4. SQL QUERY LOGGING
# ───────────────────────────────────────────────────────────────────────────────
"""
SQL queries are automatically logged in the database module.
You don't need to manually log them, but understanding the logs:

Example output:
    [2026-01-21 11:19:00] [DEBUG   ] [BillingSoftware.DatabaseQueries] - Query (0.0034s, rows=42): 
        SELECT * FROM invoices WHERE company_id = ? [with 1 params]
    
    [2026-01-21 11:19:02] [WARNING ] [BillingSoftware.DatabaseQueries] - SLOW QUERY (1.234s, rows=150): 
        SELECT * FROM invoices WHERE party_id = ? [with 1 params]

The WARNING is shown for queries taking > 500ms (0.5s)
"""

# 5. EXCEPTION LOGGING
# ───────────────────────────────────────────────────────────────────────────────
"""
Exceptions are automatically logged when you use logger.error() with exc_info=True:

    from core.logger import get_logger
    
    logger = get_logger(__name__)
    
    try:
        result = risky_operation()
    except Exception as e:
        # This logs the error WITH the full traceback
        logger.error(f"Operation failed: {e}", exc_info=True)
        # or simply:
        logger.error(f"Operation failed: {e}", exc_info=True)

Example output in logs (with full traceback):
    [2026-01-21 11:19:00] [ERROR   ] [MyModule] - Operation failed: Division by zero
    Traceback (most recent call last):
      File "/path/to/module.py", line 42, in some_function
        result = 100 / 0
    ZeroDivisionError: division by zero
"""

# ═══════════════════════════════════════════════════════════════════════════════
# LOG FILE LOCATIONS & ROTATION
# ═══════════════════════════════════════════════════════════════════════════════

"""
Log files are stored in: data/logs/app.log

Rotation Policy:
- Max file size: 10 MB per file
- Keep 30 backup files: app.log, app.log.1, app.log.2, ... app.log.30
- Total storage: ~300 MB (30 files × 10 MB)
- When app.log reaches 10 MB, it's renamed to app.log.1
- Old app.log.30 is deleted
- This keeps ~30 days of logs (depends on log volume)

To view logs:
    # Last 100 lines
    tail -100 data/logs/app.log
    
    # Search for specific error
    grep "ERROR" data/logs/app.log
    
    # Search for specific invoice
    grep "INV-2026-0001" data/logs/app.log
    
    # Search for slow queries
    grep "SLOW QUERY" data/logs/app.log
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PRACTICAL EXAMPLES IN CONTROLLERS
# ═══════════════════════════════════════════════════════════════════════════════

"""
Example 1: Invoice Deletion with Logging

    from core.logger import get_logger, log_performance, UserActionLogger
    
    logger = get_logger(__name__)
    
    @log_performance
    def delete_invoice(self, invoice_id: int) -> Tuple[bool, str]:
        try:
            logger.info(f"Attempting to delete invoice ID: {invoice_id}")
            
            # Get invoice details before deletion for logging
            invoice = db.get_invoice_by_id(invoice_id)
            invoice_no = invoice.get('invoice_no', 'Unknown') if invoice else 'Unknown'
            
            db.delete_invoice(invoice_id)
            
            # Log the user action (creates audit trail)
            UserActionLogger.log_invoice_deleted(invoice_id, invoice_no)
            
            logger.info(f"Successfully deleted invoice ID: {invoice_id}, Number: {invoice_no}")
            return True, "Invoice deleted successfully!"
        except Exception as e:
            logger.error(f"Failed to delete invoice {invoice_id}: {str(e)}", exc_info=True)
            return False, f"Failed to delete invoice: {str(e)}"

Log output would be:
    [2026-01-21 11:19:00] [DEBUG   ] [controllers.invoice_controller] - Starting execution of delete_invoice
    [2026-01-21 11:19:00] [INFO    ] [controllers.invoice_controller] - Attempting to delete invoice ID: 42
    [2026-01-21 11:19:00] [DEBUG   ] [BillingSoftware.DatabaseQueries] - Query (0.0045s, rows=1): SELECT * FROM invoices WHERE id = ? [with 1 params]
    [2026-01-21 11:19:00] [INFO    ] [BillingSoftware.UserActions] - [DELETE] Invoice(id=42) by user=system - Number=INV-2026-0001
    [2026-01-21 11:19:00] [INFO    ] [controllers.invoice_controller] - Successfully deleted invoice ID: 42, Number: INV-2026-0001
    [2026-01-21 11:19:00] [DEBUG   ] [controllers.invoice_controller] - delete_invoice completed in 0.0102s
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TROUBLESHOOTING GUIDE
# ═══════════════════════════════════════════════════════════════════════════════

"""
Problem: App crashes without error message
Solution: Check logs for the full traceback
    grep "ERROR" data/logs/app.log | head -20

Problem: Slow performance, don't know where
Solution: Search for slow operations
    grep "SLOW QUERY\|took.*s (slow operation)" data/logs/app.log

Problem: Track specific user action (e.g., which invoices were deleted)
Solution: Search user action logs
    grep "\\[DELETE\\].*Invoice" data/logs/app.log

Problem: Find when a specific party was modified
Solution: Search party operations with date
    grep "\\[UPDATE\\].*Party.*ABC" data/logs/app.log

Problem: Understand what happened during specific time window
Solution: Search by timestamp
    grep "2026-01-21 11:1[0-5]:" data/logs/app.log
"""

# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH ERROR HANDLING (FUTURE)
# ═══════════════════════════════════════════════════════════════════════════════

"""
Once custom exceptions are implemented (Phase 2), logging will work with them:

    from core.exceptions import InvoiceException
    from core.logger import get_logger
    
    logger = get_logger(__name__)
    
    try:
        if invoice_no_exists:
            raise InvoiceException(f"Invoice {invoice_no} already exists!")
    except InvoiceException as e:
        logger.warning(f"Validation error: {e}")  # Business logic error
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)  # Unexpected error
        return False, "An unexpected error occurred"
"""

# ═══════════════════════════════════════════════════════════════════════════════
# BEST PRACTICES
# ═══════════════════════════════════════════════════════════════════════════════

"""
DO:
✓ Log at module initialization: logger = get_logger(__name__)
✓ Use appropriate log levels:
  - DEBUG: Detailed info for developers (normal flow, variable values)
  - INFO: Important business events (invoice created, payment recorded)
  - WARNING: Potential issues (slow queries, validation failures)
  - ERROR: Errors that don't stop the app (delete failed, but app continues)
  - CRITICAL: Errors that stop the app (database connection failed)
✓ Use exc_info=True when logging exceptions
✓ Use @log_performance decorator on potentially slow functions
✓ Use UserActionLogger for audit trail
✓ Include relevant context in logs (IDs, amounts, names)
✓ Search logs to troubleshoot issues

DON'T:
✗ Use print() - it goes to console, not to file
✗ Log sensitive data (passwords, full credit card numbers)
✗ Forget to include context in log messages
✗ Log without module name (always use get_logger(__name__))
✗ Use generic messages like "Error occurred" without details
"""

__all__ = ['get_logger', 'log_performance', 'UserActionLogger', 'SQLLogger']
