"""
Payment Model
Data structure for payment entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Payment:
    """Payment data model (for supplier payments)"""
    id: Optional[int] = None
    company_id: Optional[int] = None
    payment_id: Optional[str] = None
    party_id: Optional[int] = None
    amount: float = 0.0
    date: Optional[str] = None
    mode: str = "Cash"
    invoice_id: Optional[int] = None
    notes: Optional[str] = None
    type: str = "PAYMENT"  # PAYMENT or RECEIPT
    party_name: Optional[str] = None  # From joined query
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        """Create a Payment from a dictionary"""
        return cls(
            id=data.get('id'),
            company_id=data.get('company_id'),
            payment_id=data.get('payment_id'),
            party_id=data.get('party_id'),
            amount=float(data.get('amount', 0) or 0),
            date=data.get('date'),
            mode=data.get('mode', 'Cash'),
            invoice_id=data.get('invoice_id'),
            notes=data.get('notes'),
            type=data.get('type', 'PAYMENT'),
            party_name=data.get('party_name')
        )
    
    def to_dict(self) -> dict:
        """Convert Payment to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'payment_id': self.payment_id,
            'party_id': self.party_id,
            'amount': self.amount,
            'date': self.date,
            'mode': self.mode,
            'invoice_id': self.invoice_id,
            'notes': self.notes,
            'type': self.type
        }
    
    @property
    def is_payment(self) -> bool:
        """Check if this is a payment (to supplier)"""
        return self.type == 'PAYMENT'
    
    @property
    def is_receipt(self) -> bool:
        """Check if this is a receipt (from customer)"""
        return self.type == 'RECEIPT'
