"""
Invoice Model
Data structure for invoice entities
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class InvoiceItem:
    """Invoice line item data model"""
    id: Optional[int] = None
    invoice_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: str = ""
    hsn_code: Optional[str] = None
    quantity: float = 0.0
    unit: str = "Piece"
    rate: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    tax_percent: float = 0.0
    tax_amount: float = 0.0
    amount: float = 0.0
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InvoiceItem':
        """Create an InvoiceItem from a dictionary"""
        return cls(
            id=data.get('id'),
            invoice_id=data.get('invoice_id'),
            product_id=data.get('product_id'),
            product_name=data.get('product_name', ''),
            hsn_code=data.get('hsn_code'),
            quantity=float(data.get('quantity', 0) or 0),
            unit=data.get('unit', 'Piece'),
            rate=float(data.get('rate', 0) or 0),
            discount_percent=float(data.get('discount_percent', 0) or 0),
            discount_amount=float(data.get('discount_amount', 0) or 0),
            tax_percent=float(data.get('tax_percent', 0) or 0),
            tax_amount=float(data.get('tax_amount', 0) or 0),
            amount=float(data.get('amount', 0) or 0)
        )
    
    def to_dict(self) -> dict:
        """Convert InvoiceItem to dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'hsn_code': self.hsn_code,
            'quantity': self.quantity,
            'unit': self.unit,
            'rate': self.rate,
            'discount_percent': self.discount_percent,
            'discount_amount': self.discount_amount,
            'tax_percent': self.tax_percent,
            'tax_amount': self.tax_amount,
            'amount': self.amount
        }


@dataclass
class Invoice:
    """Invoice data model"""
    id: Optional[int] = None
    company_id: Optional[int] = None
    invoice_no: str = ""
    date: str = ""
    party_id: Optional[int] = None
    tax_type: str = "GST - Same State"
    bill_type: str = "CASH"
    subtotal: float = 0.0
    discount: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    round_off: float = 0.0
    grand_total: float = 0.0
    balance_due: float = 0.0
    status: str = "Unpaid"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    items: List[InvoiceItem] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict, items: List[dict] = None) -> 'Invoice':
        """Create an Invoice from a dictionary"""
        invoice = cls(
            id=data.get('id'),
            company_id=data.get('company_id'),
            invoice_no=data.get('invoice_no', ''),
            date=data.get('date', ''),
            party_id=data.get('party_id'),
            tax_type=data.get('tax_type', 'GST - Same State'),
            bill_type=data.get('bill_type', 'CASH'),
            subtotal=float(data.get('subtotal', 0) or 0),
            discount=float(data.get('discount', 0) or 0),
            cgst=float(data.get('cgst', 0) or 0),
            sgst=float(data.get('sgst', 0) or 0),
            igst=float(data.get('igst', 0) or 0),
            round_off=float(data.get('round_off', 0) or 0),
            grand_total=float(data.get('grand_total', 0) or 0),
            balance_due=float(data.get('balance_due', 0) or 0),
            status=data.get('status', 'Unpaid'),
            notes=data.get('notes'),
            created_at=data.get('created_at')
        )
        
        if items:
            invoice.items = [InvoiceItem.from_dict(item) for item in items]
        
        return invoice
    
    def to_dict(self) -> dict:
        """Convert Invoice to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'invoice_no': self.invoice_no,
            'date': self.date,
            'party_id': self.party_id,
            'tax_type': self.tax_type,
            'bill_type': self.bill_type,
            'subtotal': self.subtotal,
            'discount': self.discount,
            'cgst': self.cgst,
            'sgst': self.sgst,
            'igst': self.igst,
            'round_off': self.round_off,
            'grand_total': self.grand_total,
            'balance_due': self.balance_due,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at
        }
    
    @property
    def is_gst(self) -> bool:
        """Check if invoice is GST type"""
        return self.tax_type.upper() == 'GST'
    
    @property
    def total_tax(self) -> float:
        """Get total tax amount"""
        return self.cgst + self.sgst + self.igst
