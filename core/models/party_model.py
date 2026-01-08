"""
Party Model
Data structure for party (customer/supplier) entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Party:
    """Party data model (Customer or Supplier)"""
    id: Optional[int] = None
    company_id: Optional[int] = None
    name: str = ""
    mobile: Optional[str] = None
    email: Optional[str] = None
    party_type: str = "Customer"
    gst_number: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    opening_balance: float = 0.0
    balance_type: str = "dr"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Party':
        """Create a Party from a dictionary"""
        return cls(
            id=data.get('id'),
            company_id=data.get('company_id'),
            name=data.get('name', ''),
            mobile=data.get('mobile') or data.get('phone'),
            email=data.get('email'),
            party_type=data.get('party_type') or data.get('type', 'Customer'),
            gst_number=data.get('gst_number') or data.get('gstin'),
            pan=data.get('pan'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode'),
            opening_balance=float(data.get('opening_balance', 0) or 0),
            balance_type=data.get('balance_type', 'dr')
        )
    
    def to_dict(self) -> dict:
        """Convert Party to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'mobile': self.mobile,
            'email': self.email,
            'party_type': self.party_type,
            'gst_number': self.gst_number,
            'pan': self.pan,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'opening_balance': self.opening_balance,
            'balance_type': self.balance_type
        }
    
    @property
    def is_customer(self) -> bool:
        """Check if party is a customer"""
        return self.party_type.lower() in ['customer', 'both']
    
    @property
    def is_supplier(self) -> bool:
        """Check if party is a supplier"""
        return self.party_type.lower() in ['supplier', 'both']
