"""
Receipt Model
Data structure for receipt entities (alias for Payment with type='RECEIPT')
"""

from .payment_model import Payment


# Receipt is just a Payment with type='RECEIPT'
# This is a convenience alias for clarity
Receipt = Payment
