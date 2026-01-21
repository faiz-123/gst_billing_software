"""
Custom Exception Hierarchy for GST Billing Software

Provides specific exception types for different error scenarios,
making error handling more precise and user-friendly.
"""

from typing import Optional, Dict, Any


class BillingException(Exception):
    """Base exception for all billing-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_user_message(self) -> str:
        """Get user-friendly error message"""
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }


class InvoiceException(BillingException):
    """Exception for invoice-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 invoice_id: Optional[Any] = None, details: Optional[Dict] = None):
        self.invoice_id = invoice_id
        details = details or {}
        if invoice_id:
            details['invoice_id'] = invoice_id
        super().__init__(message, error_code or "INVOICE_ERROR", details)


class InvoiceAlreadyExistsException(InvoiceException):
    """Invoice number already exists"""
    
    def __init__(self, invoice_no: str, invoice_id: Optional[int] = None):
        self.invoice_no = invoice_no
        message = f"Invoice number '{invoice_no}' already exists. Please use a different invoice number."
        super().__init__(message, "INVOICE_DUPLICATE", invoice_id, 
                        {'invoice_no': invoice_no})


class InvoiceNotFound(InvoiceException):
    """Invoice not found in database"""
    
    def __init__(self, invoice_id: int):
        message = f"Invoice with ID {invoice_id} not found."
        super().__init__(message, "INVOICE_NOT_FOUND", invoice_id)


class InvalidInvoiceTotal(InvoiceException):
    """Invoice total calculation is invalid"""
    
    def __init__(self, invoice_id: int, expected: float, actual: float):
        message = (f"Invoice total mismatch. Expected: {expected}, "
                  f"Actual: {actual}. Please verify all items and taxes.")
        super().__init__(message, "INVOICE_TOTAL_MISMATCH", invoice_id,
                        {'expected': expected, 'actual': actual})


class PaymentException(BillingException):
    """Exception for payment-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 payment_id: Optional[Any] = None, details: Optional[Dict] = None):
        self.payment_id = payment_id
        details = details or {}
        if payment_id:
            details['payment_id'] = payment_id
        super().__init__(message, error_code or "PAYMENT_ERROR", details)


class InvalidPaymentAmount(PaymentException):
    """Payment amount is invalid"""
    
    def __init__(self, amount: float, min_amount: float = 0):
        message = (f"Payment amount {amount} is invalid. "
                  f"Amount must be greater than {min_amount}.")
        super().__init__(message, "INVALID_PAYMENT_AMOUNT",
                        details={'amount': amount, 'min_amount': min_amount})


class InsufficientPaymentAmount(PaymentException):
    """Payment amount is less than invoice amount"""
    
    def __init__(self, invoice_amount: float, payment_amount: float):
        message = (f"Payment amount ({payment_amount}) is less than invoice amount ({invoice_amount}). "
                  f"Please pay the full amount or mark as partial payment.")
        super().__init__(message, "INSUFFICIENT_PAYMENT_AMOUNT",
                        details={'invoice_amount': invoice_amount, 'payment_amount': payment_amount})


class PartyException(BillingException):
    """Exception for party (customer/supplier) related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 party_id: Optional[int] = None, details: Optional[Dict] = None):
        self.party_id = party_id
        details = details or {}
        if party_id:
            details['party_id'] = party_id
        super().__init__(message, error_code or "PARTY_ERROR", details)


class PartyAlreadyExists(PartyException):
    """Party with same name/details already exists"""
    
    def __init__(self, party_name: str):
        message = (f"A party with name '{party_name}' already exists. "
                  f"Please use a different name or edit the existing party.")
        super().__init__(message, "PARTY_DUPLICATE", details={'party_name': party_name})


class PartyNotFound(PartyException):
    """Party not found in database"""
    
    def __init__(self, party_id: int):
        message = f"Party with ID {party_id} not found."
        super().__init__(message, "PARTY_NOT_FOUND", party_id)


class CreditLimitExceeded(PartyException):
    """Party credit limit exceeded"""
    
    def __init__(self, party_id: int, party_name: str, current_balance: float, 
                 credit_limit: float, invoice_amount: float):
        message = (f"Credit limit exceeded for {party_name}. "
                  f"Current balance: {current_balance}, Credit limit: {credit_limit}. "
                  f"Cannot create invoice for amount: {invoice_amount}.")
        super().__init__(message, "CREDIT_LIMIT_EXCEEDED", party_id,
                        {'party_name': party_name, 'current_balance': current_balance,
                         'credit_limit': credit_limit, 'invoice_amount': invoice_amount})


class ProductException(BillingException):
    """Exception for product-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 product_id: Optional[int] = None, details: Optional[Dict] = None):
        self.product_id = product_id
        details = details or {}
        if product_id:
            details['product_id'] = product_id
        super().__init__(message, error_code or "PRODUCT_ERROR", details)


class ProductNotFound(ProductException):
    """Product not found in database"""
    
    def __init__(self, product_id: int):
        message = f"Product with ID {product_id} not found."
        super().__init__(message, "PRODUCT_NOT_FOUND", product_id)


class InsufficientStock(ProductException):
    """Insufficient stock for product"""
    
    def __init__(self, product_id: int, product_name: str, required: float, 
                 available: float):
        message = (f"Insufficient stock for '{product_name}'. "
                  f"Required: {required}, Available: {available}. "
                  f"Please adjust quantity or enable backorder.")
        super().__init__(message, "INSUFFICIENT_STOCK", product_id,
                        {'product_name': product_name, 'required': required,
                         'available': available})


class ValidationException(BillingException):
    """Exception for data validation errors"""
    
    def __init__(self, message: str, field_name: Optional[str] = None,
                 details: Optional[Dict] = None):
        self.field_name = field_name
        details = details or {}
        if field_name:
            details['field_name'] = field_name
        error_code = f"VALIDATION_ERROR_{field_name.upper()}" if field_name else "VALIDATION_ERROR"
        super().__init__(message, error_code, details)


class InvalidEmailException(ValidationException):
    """Invalid email format"""
    
    def __init__(self, email: str):
        message = f"Invalid email address: '{email}'. Please enter a valid email."
        super().__init__(message, "email", {'email': email})


class InvalidPhoneException(ValidationException):
    """Invalid phone number format"""
    
    def __init__(self, phone: str):
        message = f"Invalid phone number: '{phone}'. Please enter a valid 10-digit phone number."
        super().__init__(message, "phone", {'phone': phone})


class InvalidGSTIN(ValidationException):
    """Invalid GSTIN format"""
    
    def __init__(self, gstin: str):
        message = (f"Invalid GSTIN: '{gstin}'. "
                  f"GSTIN must be 15 characters in the format: 27AABCT1234H1Z0")
        super().__init__(message, "gstin", {'gstin': gstin})


class InvalidPAN(ValidationException):
    """Invalid PAN format"""
    
    def __init__(self, pan: str):
        message = (f"Invalid PAN: '{pan}'. "
                  f"PAN must be 10 characters in the format: AAAAA1234A")
        super().__init__(message, "pan", {'pan': pan})


class DecimalPrecisionException(ValidationException):
    """Amount has incorrect decimal precision"""
    
    def __init__(self, field_name: str, value: float):
        message = (f"Amount in {field_name} must have exactly 2 decimal places. "
                  f"Current value: {value}")
        super().__init__(message, field_name, {'value': value})


class DatabaseException(BillingException):
    """Exception for database-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 details: Optional[Dict] = None):
        super().__init__(message, error_code or "DATABASE_ERROR", details)


class DatabaseLocked(DatabaseException):
    """Database is locked (concurrent access issue)"""
    
    def __init__(self):
        message = ("Database is currently locked. Another user or process is making changes. "
                  "Please wait a moment and try again.")
        super().__init__(message, "DATABASE_LOCKED")


class DatabaseConnectionError(DatabaseException):
    """Cannot connect to database"""
    
    def __init__(self, reason: Optional[str] = None):
        message = "Failed to connect to database."
        if reason:
            message += f" Reason: {reason}"
        message += " Please check database connection and try again."
        super().__init__(message, "DATABASE_CONNECTION_ERROR", 
                        {'reason': reason} if reason else {})


class TransactionRollbackError(DatabaseException):
    """Transaction rollback failed"""
    
    def __init__(self, operation: str, reason: Optional[str] = None):
        message = (f"Failed to rollback {operation} operation. "
                  f"Data may be in an inconsistent state.")
        if reason:
            message += f" Error: {reason}"
        super().__init__(message, "TRANSACTION_ROLLBACK_ERROR",
                        {'operation': operation, 'reason': reason})


class CompanyException(BillingException):
    """Exception for company-related errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 company_id: Optional[int] = None, details: Optional[Dict] = None):
        self.company_id = company_id
        details = details or {}
        if company_id:
            details['company_id'] = company_id
        super().__init__(message, error_code or "COMPANY_ERROR", details)


class CompanyNotFound(CompanyException):
    """Company not found"""
    
    def __init__(self, company_id: int):
        message = f"Company with ID {company_id} not found."
        super().__init__(message, "COMPANY_NOT_FOUND", company_id)


class NoCompanySelected(CompanyException):
    """No company is currently selected"""
    
    def __init__(self):
        message = "No company selected. Please select or create a company to continue."
        super().__init__(message, "NO_COMPANY_SELECTED")


__all__ = [
    'BillingException',
    'InvoiceException',
    'InvoiceAlreadyExistsException',
    'InvoiceNotFound',
    'InvalidInvoiceTotal',
    'PaymentException',
    'InvalidPaymentAmount',
    'InsufficientPaymentAmount',
    'PartyException',
    'PartyAlreadyExists',
    'PartyNotFound',
    'CreditLimitExceeded',
    'ProductException',
    'ProductNotFound',
    'InsufficientStock',
    'ValidationException',
    'InvalidEmailException',
    'InvalidPhoneException',
    'InvalidGSTIN',
    'InvalidPAN',
    'DecimalPrecisionException',
    'DatabaseException',
    'DatabaseLocked',
    'DatabaseConnectionError',
    'TransactionRollbackError',
    'CompanyException',
    'CompanyNotFound',
    'NoCompanySelected',
]
