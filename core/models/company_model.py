"""
Company Model
Data structure for company entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    """Company data model"""
    id: Optional[int] = None
    name: str = ""
    gstin: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    tax_type: Optional[str] = None
    fy_start: Optional[str] = None
    fy_end: Optional[str] = None
    other_license: Optional[str] = None
    bank_name: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    logo_path: Optional[str] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Company':
        """Create a Company from a dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            gstin=data.get('gstin'),
            mobile=data.get('mobile'),
            email=data.get('email'),
            address=data.get('address'),
            website=data.get('website'),
            tax_type=data.get('tax_type'),
            fy_start=data.get('fy_start'),
            fy_end=data.get('fy_end'),
            other_license=data.get('other_license'),
            bank_name=data.get('bank_name'),
            account_name=data.get('account_name'),
            account_number=data.get('account_number'),
            ifsc_code=data.get('ifsc_code'),
            logo_path=data.get('logo_path'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        """Convert Company to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'gstin': self.gstin,
            'mobile': self.mobile,
            'email': self.email,
            'address': self.address,
            'website': self.website,
            'tax_type': self.tax_type,
            'fy_start': self.fy_start,
            'fy_end': self.fy_end,
            'other_license': self.other_license,
            'bank_name': self.bank_name,
            'account_name': self.account_name,
            'account_number': self.account_number,
            'ifsc_code': self.ifsc_code,
            'logo_path': self.logo_path,
            'created_at': self.created_at
        }
