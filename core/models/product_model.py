"""
Product Model
Data structure for product entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """Product data model"""
    id: Optional[int] = None
    company_id: Optional[int] = None
    name: str = ""
    hsn_code: Optional[str] = None
    barcode: Optional[str] = None
    unit: str = "PCS"
    sales_rate: float = 0.0
    purchase_rate: float = 0.0
    discount_percent: float = 0.0
    mrp: float = 0.0
    tax_rate: float = 18.0
    sgst_rate: float = 9.0
    cgst_rate: float = 9.0
    opening_stock: float = 0.0
    current_stock: float = 0.0
    low_stock: float = 0.0
    product_type: str = "Goods"
    category: Optional[str] = None
    description: Optional[str] = None
    warranty_months: int = 0
    has_serial_number: int = 0
    track_stock: int = 0
    is_gst_registered: int = 0
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Create a Product from a dictionary"""
        return cls(
            id=data.get('id'),
            company_id=data.get('company_id'),
            name=data.get('name', ''),
            hsn_code=data.get('hsn_code'),
            barcode=data.get('barcode'),
            unit=data.get('unit', 'PCS'),
            sales_rate=float(data.get('sales_rate', 0) or 0),
            purchase_rate=float(data.get('purchase_rate', 0) or 0),
            discount_percent=float(data.get('discount_percent', 0) or 0),
            mrp=float(data.get('mrp', 0) or 0),
            tax_rate=float(data.get('tax_rate', 18) or 18),
            sgst_rate=float(data.get('sgst_rate', 9) or 9),
            cgst_rate=float(data.get('cgst_rate', 9) or 9),
            opening_stock=float(data.get('opening_stock', 0) or 0),
            current_stock=float(data.get('current_stock', 0) or 0),
            low_stock=float(data.get('low_stock', 0) or 0),
            product_type=data.get('product_type', 'Goods'),
            category=data.get('category'),
            description=data.get('description'),
            warranty_months=int(data.get('warranty_months', 0) or 0),
            has_serial_number=int(data.get('has_serial_number', 0) or 0),
            track_stock=int(data.get('track_stock', 0) or 0),
            is_gst_registered=int(data.get('is_gst_registered', 0) or 0),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        """Convert Product to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'hsn_code': self.hsn_code,
            'barcode': self.barcode,
            'unit': self.unit,
            'sales_rate': self.sales_rate,
            'purchase_rate': self.purchase_rate,
            'discount_percent': self.discount_percent,
            'mrp': self.mrp,
            'tax_rate': self.tax_rate,
            'sgst_rate': self.sgst_rate,
            'cgst_rate': self.cgst_rate,
            'opening_stock': self.opening_stock,
            'current_stock': self.current_stock,
            'low_stock': self.low_stock,
            'product_type': self.product_type,
            'category': self.category,
            'description': self.description,
            'warranty_months': self.warranty_months,
            'has_serial_number': self.has_serial_number,
            'track_stock': self.track_stock,
            'is_gst_registered': self.is_gst_registered,
            'created_at': self.created_at
        }
