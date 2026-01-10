"""
Validators for GST Billing Software
Contains validation functions for various data types
"""

import re


def validate_gstin(gstin: str) -> bool:
    """
    Validate GSTIN (Goods and Services Tax Identification Number)
    
    Format: 15 characters
    - First 2 digits: State code (01-37)
    - Next 10 characters: PAN
    - 13th character: Entity number (1-9 or A-Z)
    - 14th character: 'Z' by default
    - 15th character: Checksum digit
    
    Args:
        gstin: The GSTIN to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not gstin:
        return True  # Empty is valid (optional field)
    
    gstin = gstin.upper().strip()
    
    # Length check
    if len(gstin) != 15:
        return False
    
    # Pattern check
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gstin):
        return False
    
    # State code check (01-37)
    state_code = int(gstin[:2])
    if state_code < 1 or state_code > 37:
        return False
    
    return True


def validate_pan(pan: str) -> bool:
    """
    Validate PAN (Permanent Account Number)
    
    Format: 10 characters
    - First 5 characters: Uppercase letters
    - Next 4 characters: Numbers
    - Last character: Uppercase letter
    
    Args:
        pan: The PAN to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not pan:
        return True  # Empty is valid (optional field)
    
    pan = pan.upper().strip()
    
    # Length check
    if len(pan) != 10:
        return False
    
    # Pattern check
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan))


def validate_mobile(mobile: str) -> bool:
    """
    Validate Indian mobile number
    
    Format: 10 digits starting with 6, 7, 8, or 9
    Can have optional +91 or 0 prefix
    
    Args:
        mobile: The mobile number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not mobile:
        return True  # Empty is valid (optional field)
    
    # Remove spaces, dashes, and common prefixes
    mobile = mobile.strip().replace(' ', '').replace('-', '')
    mobile = mobile.lstrip('+91').lstrip('91').lstrip('0')
    
    # Length check
    if len(mobile) != 10:
        return False
    
    # Pattern check (starts with 6, 7, 8, or 9)
    pattern = r'^[6-9][0-9]{9}$'
    return bool(re.match(pattern, mobile))


def validate_email(email: str) -> bool:
    """
    Validate email address
    
    Args:
        email: The email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return True  # Empty is valid (optional field)
    
    email = email.strip().lower()
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_pincode(pincode: str) -> bool:
    """
    Validate Indian PIN code
    
    Format: 6 digits, first digit cannot be 0
    
    Args:
        pincode: The PIN code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not pincode:
        return True  # Empty is valid (optional field)
    
    pincode = pincode.strip()
    
    # Length check
    if len(pincode) != 6:
        return False
    
    # Pattern check
    pattern = r'^[1-9][0-9]{5}$'
    return bool(re.match(pattern, pincode))


def validate_hsn_code(hsn: str) -> bool:
    """
    Validate HSN (Harmonized System of Nomenclature) code
    
    Format: 4, 6, or 8 digits
    
    Args:
        hsn: The HSN code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not hsn:
        return True  # Empty is valid (optional field)
    
    hsn = hsn.strip()
    
    # Length check (4, 6, or 8 digits)
    if len(hsn) not in [4, 6, 8]:
        return False
    
    # Must be all digits
    return hsn.isdigit()


def validate_ifsc_code(ifsc: str) -> bool:
    """
    Validate IFSC (Indian Financial System Code)
    
    Format: 11 characters
    - First 4 characters: Bank code (letters)
    - 5th character: 0 (reserved for future use)
    - Last 6 characters: Branch code (alphanumeric)
    
    Args:
        ifsc: The IFSC code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not ifsc:
        return True  # Empty is valid (optional field)
    
    ifsc = ifsc.upper().strip()
    
    # Length check
    if len(ifsc) != 11:
        return False
    
    # Pattern check
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc))


def validate_positive_number(value, allow_zero: bool = True) -> bool:
    """
    Validate that a value is a positive number
    
    Args:
        value: The value to validate
        allow_zero: Whether zero is allowed
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num = float(value)
        if allow_zero:
            return num >= 0
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_required(value) -> bool:
    """
    Validate that a value is not empty
    
    Args:
        value: The value to validate
        
    Returns:
        bool: True if not empty, False otherwise
    """
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


# === UI Field Error State Helpers ===

def set_field_error_state(widget, is_error: bool, error_message: str = ""):
    """
    Set error state on a widget that has set_error() method
    
    Args:
        widget: Widget with set_error(is_error, message) method
        is_error: True to show error state, False to clear
        error_message: Error message to display when is_error is True
    """
    if hasattr(widget, 'set_error'):
        widget.set_error(is_error, error_message if is_error else "")


def set_name_error_state(name_widget, is_error: bool):
    """
    Set error state for a name/required text field
    
    Args:
        name_widget: Widget with set_error() method
        is_error: True to show error, False to clear
    """
    set_field_error_state(name_widget, is_error, "Item Name is required")


def set_price_error_state(price_widget, is_error: bool):
    """
    Set error state for a price field
    
    Args:
        price_widget: Widget with set_error() method
        is_error: True to show error, False to clear
    """
    set_field_error_state(price_widget, is_error, "Selling price must be greater than 0")
