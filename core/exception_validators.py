"""
Enhanced Validators with Exception Integration

Wraps core validators to raise custom exceptions for form validation
and business logic validation with user-friendly error messages.
"""

from typing import Any, Union, Tuple
from decimal import Decimal

from core.logger import get_logger
from core.exceptions import (
    ValidationException, InvalidEmailException, InvalidPhoneException,
    InvalidGSTIN, InvalidPAN, DecimalPrecisionException,
    InvalidInvoiceTotal, InsufficientStock
)
from core.validators import (
    validate_gstin as core_validate_gstin,
    validate_pan as core_validate_pan,
    validate_mobile as core_validate_mobile,
    validate_email as core_validate_email
)

logger = get_logger(__name__)


class ValidatorWithException:
    """Enhanced validators that raise custom exceptions"""
    
    @staticmethod
    def validate_gstin(gstin: str, raise_exception: bool = True) -> bool:
        """
        Validate GSTIN and optionally raise exception
        
        Args:
            gstin: The GSTIN to validate
            raise_exception: If True, raises InvalidGSTIN on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            InvalidGSTIN: If invalid and raise_exception=True
        """
        if not core_validate_gstin(gstin):
            if raise_exception:
                logger.warning(f"Invalid GSTIN: {gstin}")
                raise InvalidGSTIN(gstin)
            return False
        return True
    
    @staticmethod
    def validate_pan(pan: str, raise_exception: bool = True) -> bool:
        """
        Validate PAN and optionally raise exception
        
        Args:
            pan: The PAN to validate
            raise_exception: If True, raises InvalidPAN on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            InvalidPAN: If invalid and raise_exception=True
        """
        if not core_validate_pan(pan):
            if raise_exception:
                logger.warning(f"Invalid PAN: {pan}")
                raise InvalidPAN(pan)
            return False
        return True
    
    @staticmethod
    def validate_mobile(mobile: str, raise_exception: bool = True) -> bool:
        """
        Validate mobile number and optionally raise exception
        
        Args:
            mobile: The mobile number to validate
            raise_exception: If True, raises InvalidPhoneException on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            InvalidPhoneException: If invalid and raise_exception=True
        """
        if not core_validate_mobile(mobile):
            if raise_exception:
                logger.warning(f"Invalid mobile: {mobile}")
                raise InvalidPhoneException(mobile)
            return False
        return True
    
    @staticmethod
    def validate_email(email: str, raise_exception: bool = True) -> bool:
        """
        Validate email and optionally raise exception
        
        Args:
            email: The email to validate
            raise_exception: If True, raises InvalidEmailException on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            InvalidEmailException: If invalid and raise_exception=True
        """
        if not core_validate_email(email):
            if raise_exception:
                logger.warning(f"Invalid email: {email}")
                raise InvalidEmailException(email)
            return False
        return True
    
    @staticmethod
    def validate_decimal_precision(value: Union[float, Decimal, str],
                                   max_decimals: int = 2,
                                   raise_exception: bool = True) -> bool:
        """
        Validate decimal precision (used for currency/GST values)
        
        Args:
            value: The decimal value to validate
            max_decimals: Maximum number of decimal places allowed
            raise_exception: If True, raises DecimalPrecisionException on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            DecimalPrecisionException: If precision exceeds max_decimals
        """
        try:
            decimal_value = Decimal(str(value))
            # Get decimal places
            if decimal_value % 1 != 0:
                # Count decimal places
                decimal_str = str(decimal_value).split('.')[-1]
                actual_decimals = len(decimal_str.rstrip('0'))
                
                if actual_decimals > max_decimals:
                    if raise_exception:
                        logger.warning(f"Decimal precision exceeded: {value} (max {max_decimals} decimals)")
                        raise DecimalPrecisionException("amount", float(value))
                    return False
            return True
        except DecimalPrecisionException:
            raise
        except Exception as e:
            if raise_exception:
                logger.error(f"Error validating decimal precision: {e}")
                raise DecimalPrecisionException("amount", float(value))
            return False
    
    @staticmethod
    def validate_invoice_total(invoice_items: list,
                              total_amount: float,
                              tolerance: float = 0.01,
                              raise_exception: bool = True) -> bool:
        """
        Validate invoice total matches sum of items
        
        Args:
            invoice_items: List of invoice line items with amounts
            total_amount: The claimed total amount
            tolerance: Allowed difference (for rounding errors)
            raise_exception: If True, raises InvalidInvoiceTotal on failure
            
        Returns:
            bool: True if valid
            
        Raises:
            InvalidInvoiceTotal: If total doesn't match calculated sum
        """
        calculated_total = sum(item.get('amount', 0) for item in invoice_items)
        difference = abs(calculated_total - total_amount)
        
        if difference > tolerance:
            if raise_exception:
                logger.warning(f"Invoice total mismatch: declared={total_amount}, calculated={calculated_total}")
                raise InvalidInvoiceTotal(
                    invoice_id=0,  # 0 for validation before creation
                    expected=calculated_total,
                    actual=total_amount
                )
            return False
        return True
    
    @staticmethod
    def validate_stock_availability(current_stock: int,
                                   requested_quantity: int,
                                   product_id: int,
                                   product_name: str = "Product",
                                   raise_exception: bool = True) -> bool:
        """
        Validate sufficient stock availability
        
        Args:
            current_stock: Current quantity in stock
            requested_quantity: Quantity being requested
            product_id: Product ID (for error details)
            product_name: Product name (for user message)
            raise_exception: If True, raises InsufficientStock on failure
            
        Returns:
            bool: True if sufficient stock
            
        Raises:
            InsufficientStock: If insufficient stock available
        """
        if current_stock < requested_quantity:
            if raise_exception:
                logger.warning(f"Insufficient stock for {product_name}: available={current_stock}, requested={requested_quantity}")
                raise InsufficientStock(
                    product_id=product_id,
                    product_name=product_name,
                    required=requested_quantity,
                    available=current_stock
                )
            return False
        return True
    
    @staticmethod
    def validate_required_field(value: Any, field_name: str,
                               raise_exception: bool = True) -> bool:
        """
        Validate required field is not empty
        
        Args:
            value: The field value
            field_name: Name of the field (for error message)
            raise_exception: If True, raises ValidationException on failure
            
        Returns:
            bool: True if not empty
            
        Raises:
            ValidationException: If field is empty
        """
        if value is None or value == "" or (isinstance(value, str) and not value.strip()):
            if raise_exception:
                logger.warning(f"Required field empty: {field_name}")
                raise ValidationException(
                    message=f"'{field_name}' is required and cannot be empty",
                    field_name=field_name,
                    details={"field": field_name}
                )
            return False
        return True


# Convenience functions for use in forms/dialogs
def validate_gstin_field(gstin: str) -> Tuple[bool, str]:
    """Validate GSTIN field, returns (is_valid, error_message)"""
    try:
        ValidatorWithException.validate_gstin(gstin, raise_exception=True)
        return True, ""
    except InvalidGSTIN as e:
        return False, e.to_user_message()
    except Exception as e:
        logger.error(f"Unexpected error validating GSTIN: {e}")
        return False, "Invalid GSTIN format"


def validate_pan_field(pan: str) -> Tuple[bool, str]:
    """Validate PAN field, returns (is_valid, error_message)"""
    try:
        ValidatorWithException.validate_pan(pan, raise_exception=True)
        return True, ""
    except InvalidPAN as e:
        return False, e.to_user_message()
    except Exception as e:
        logger.error(f"Unexpected error validating PAN: {e}")
        return False, "Invalid PAN format"


def validate_mobile_field(mobile: str) -> Tuple[bool, str]:
    """Validate mobile field, returns (is_valid, error_message)"""
    try:
        ValidatorWithException.validate_mobile(mobile, raise_exception=True)
        return True, ""
    except InvalidPhoneException as e:
        return False, e.to_user_message()
    except Exception as e:
        logger.error(f"Unexpected error validating mobile: {e}")
        return False, "Invalid mobile number"


def validate_email_field(email: str) -> Tuple[bool, str]:
    """Validate email field, returns (is_valid, error_message)"""
    try:
        ValidatorWithException.validate_email(email, raise_exception=True)
        return True, ""
    except InvalidEmailException as e:
        return False, e.to_user_message()
    except Exception as e:
        logger.error(f"Unexpected error validating email: {e}")
        return False, "Invalid email format"


__all__ = [
    'ValidatorWithException',
    'validate_gstin_field',
    'validate_pan_field',
    'validate_mobile_field',
    'validate_email_field',
]
