"""
Utility functions for GST Billing Software
Contains helper functions for number conversion, formatting, etc.
"""

def number_to_words_indian(n):
    """Convert number to Indian English words format
    
    Args:
        n (float): Number to convert
        
    Returns:
        str: Number in words (e.g., "Three Thousand Nine Hundred Only")
    """
    if n == 0:
        return "Zero Only"
    
    if n < 0:
        return "Minus " + number_to_words_indian(-n)
    
    # Handle decimal part
    rupees = int(n)
    paise = int((n - rupees) * 100)
    
    result = ""
    
    # Convert rupees part
    if rupees > 0:
        result = _convert_number_to_words(rupees)
        if rupees == 1:
            result += " Rupee"
        else:
            result += " Rupees"
    
    # Convert paise part
    if paise > 0:
        if result:
            result += " and "
        result += _convert_number_to_words(paise)
        if paise == 1:
            result += " Paisa"
        else:
            result += " Paise"
    
    return result + " Only"

def _convert_number_to_words(num):
    """Convert integer to words (Indian numbering system)"""
    if num == 0:
        return ""
    
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_hundreds(n):
        result = ""
        if n >= 100:
            result += ones[n // 100] + " Hundred"
            n %= 100
            if n > 0:
                result += " "
        
        if n >= 20:
            result += tens[n // 10]
            n %= 10
            if n > 0:
                result += " " + ones[n]
        elif n > 0:
            result += ones[n]
            
        return result
    
    # Handle crores
    crores = num // 10000000
    num %= 10000000
    
    # Handle lakhs
    lakhs = num // 100000
    num %= 100000
    
    # Handle thousands
    thousands = num // 1000
    num %= 1000
    
    # Handle hundreds, tens, ones
    hundreds = num
    
    result = ""
    
    if crores > 0:
        result += convert_hundreds(crores) + " Crore"
        if lakhs > 0 or thousands > 0 or hundreds > 0:
            result += " "
    
    if lakhs > 0:
        result += convert_hundreds(lakhs) + " Lakh"
        if thousands > 0 or hundreds > 0:
            result += " "
    
    if thousands > 0:
        result += convert_hundreds(thousands) + " Thousand"
        if hundreds > 0:
            result += " "
    
    if hundreds > 0:
        result += convert_hundreds(hundreds)
    
    return result.strip()

def format_currency(amount):
    """Format amount in Indian currency format with ₹ symbol"""
    return f"₹{amount:,.2f}"

def format_indian_number(num):
    """Format number in Indian numbering system (with commas)"""
    s = f"{num:,.2f}"
    return s

def get_gst_rate_from_tax_percent(tax_percent):
    """Get GST rate breakdown from total tax percentage"""
    if tax_percent <= 0:
        return {"cgst": 0, "sgst": 0, "igst": 0}
    
    # For intra-state (default), split equally between CGST and SGST
    cgst_rate = tax_percent / 2
    sgst_rate = tax_percent / 2
    igst_rate = 0  # For interstate, this would be equal to tax_percent
    
    return {
        "cgst": cgst_rate,
        "sgst": sgst_rate, 
        "igst": igst_rate
    }

def calculate_gst_amounts(taxable_amount, tax_percent, is_interstate=False):
    """Calculate GST amounts based on taxable amount and tax rate"""
    total_tax = taxable_amount * (tax_percent / 100)
    
    if is_interstate:
        return {
            "cgst_amount": 0,
            "sgst_amount": 0,
            "igst_amount": total_tax,
            "total_tax": total_tax
        }
    else:
        cgst_amount = total_tax / 2
        sgst_amount = total_tax / 2
        return {
            "cgst_amount": cgst_amount,
            "sgst_amount": sgst_amount,
            "igst_amount": 0,
            "total_tax": total_tax
        }


def to_upper(edit, text: str):
    """
    Convert text to uppercase and update the input field while preserving cursor position.
    
    Args:
        edit: Input widget with setText, cursorPosition, setCursorPosition, and blockSignals methods
        text: Current text value
    """
    upper = text.upper()
    if text != upper:
        cursor_pos = edit.cursorPosition()
        edit.blockSignals(True)
        edit.setText(upper)
        edit.setCursorPosition(cursor_pos)
        edit.blockSignals(False)
