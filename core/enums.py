"""
Enumerations for GST Billing Software
Contains all enum types used across the application
"""

from enum import Enum

 
class PartyType(str, Enum):
    """Types of parties"""
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    BOTH = "Both"


class TaxType(str, Enum):
    """Types of tax invoices"""
    GST = "GST"
    NON_GST = "Non-GST"


class BillType(str, Enum):
    """Types of bills"""
    CASH = "CASH"
    CREDIT = "CREDIT"


class InvoiceStatus(str, Enum):
    """Invoice statuses"""
    DRAFT = "Draft"
    PENDING = "Pending"
    PAID = "Paid"
    PARTIAL = "Partial"
    CANCELLED = "Cancelled"
    OVERDUE = "Overdue"


class PaymentMode(str, Enum):
    """Payment modes"""
    CASH = "Cash"
    CHEQUE = "Cheque"
    BANK_TRANSFER = "Bank Transfer"
    UPI = "UPI"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    NEFT = "NEFT"
    RTGS = "RTGS"
    IMPS = "IMPS"
    OTHER = "Other"


class PaymentType(str, Enum):
    """Types of payment transactions"""
    PAYMENT = "PAYMENT"  # Payment made to supplier
    RECEIPT = "RECEIPT"  # Receipt from customer


class ProductType(str, Enum):
    """Types of products"""
    GOODS = "Goods"
    SERVICES = "Services"


class BalanceType(str, Enum):
    """Types of balance for opening balance"""
    DEBIT = "To Receive"
    CREDIT = "To Pay"


class Unit(str, Enum):
    """Units of measurement"""
    PIECE = "PCS"
    KILOGRAM = "KG"
    GRAM = "GM"
    LITRE = "LTR"
    MILLILITRE = "ML"
    METER = "MTR"
    CENTIMETER = "CM"
    SQUARE_METER = "SQM"
    SQUARE_FEET = "SQF"
    BOX = "BOX"
    DOZEN = "DZN"
    PACK = "PACK"
    SET = "SET"
    PAIR = "PAIR"
    UNIT = "UNIT"
    NUMBER = "NOS"


class GSTRate(float, Enum):
    """Standard GST rates"""
    ZERO = 0.0
    FIVE = 5.0
    TWELVE = 12.0
    EIGHTEEN = 18.0
    TWENTY_EIGHT = 28.0


class State(str, Enum):
    """Indian states with codes"""
    ANDHRA_PRADESH = "37 - Andhra Pradesh"
    ARUNACHAL_PRADESH = "12 - Arunachal Pradesh"
    ASSAM = "18 - Assam"
    BIHAR = "10 - Bihar"
    CHHATTISGARH = "22 - Chhattisgarh"
    GOA = "30 - Goa"
    GUJARAT = "24 - Gujarat"
    HARYANA = "06 - Haryana"
    HIMACHAL_PRADESH = "02 - Himachal Pradesh"
    JHARKHAND = "20 - Jharkhand"
    KARNATAKA = "29 - Karnataka"
    KERALA = "32 - Kerala"
    MADHYA_PRADESH = "23 - Madhya Pradesh"
    MAHARASHTRA = "27 - Maharashtra"
    MANIPUR = "14 - Manipur"
    MEGHALAYA = "17 - Meghalaya"
    MIZORAM = "15 - Mizoram"
    NAGALAND = "13 - Nagaland"
    ODISHA = "21 - Odisha"
    PUNJAB = "03 - Punjab"
    RAJASTHAN = "08 - Rajasthan"
    SIKKIM = "11 - Sikkim"
    TAMIL_NADU = "33 - Tamil Nadu"
    TELANGANA = "36 - Telangana"
    TRIPURA = "16 - Tripura"
    UTTAR_PRADESH = "09 - Uttar Pradesh"
    UTTARAKHAND = "05 - Uttarakhand"
    WEST_BENGAL = "19 - West Bengal"
    # Union Territories
    ANDAMAN_NICOBAR = "35 - Andaman and Nicobar Islands"
    CHANDIGARH = "04 - Chandigarh"
    DADRA_NAGAR_HAVELI = "26 - Dadra and Nagar Haveli and Daman and Diu"
    DELHI = "07 - Delhi"
    JAMMU_KASHMIR = "01 - Jammu and Kashmir"
    LADAKH = "38 - Ladakh"
    LAKSHADWEEP = "31 - Lakshadweep"
    PUDUCHERRY = "34 - Puducherry"


def get_state_list():
    """Get list of state names for dropdowns"""
    return [state.value for state in State]


def get_unit_list():
    """Get list of units for dropdowns"""
    return [unit.value for unit in Unit]


def get_gst_rate_list():
    """Get list of GST rates for dropdowns"""
    return [rate.value for rate in GSTRate]


# Quick GST rates for chip buttons (common rates without 0%)
QUICK_GST_RATES = [5, 12, 18, 28]

# All valid GST rates including 0%
ALL_GST_RATES = [0, 5, 12, 18, 28]


def get_payment_mode_list():
    """Get list of payment modes for dropdowns"""
    return [mode.value for mode in PaymentMode]


def get_party_type_list():
    """Get list of party types for dropdowns"""
    return [ptype.value for ptype in PartyType]


def get_product_type_list():
    """Get list of product types for dropdowns"""
    return [ptype.value for ptype in ProductType]


def get_invoice_status_list():
    """Get list of invoice statuses for dropdowns"""
    return [status.value for status in InvoiceStatus]
