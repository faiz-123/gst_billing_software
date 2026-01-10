"""
Product Service
Business logic for product operations
"""

from typing import Dict, Optional, Tuple


class ProductService:
    """Service class for product-related business logic"""
    
    def __init__(self, db=None):
        self.db = db
    
    def calculate_split_gst(self, gst_rate: float) -> Tuple[float, float]:
        """
        Calculate SGST and CGST from total GST rate
        
        Args:
            gst_rate: Total GST percentage (e.g., 18.0)
            
        Returns:
            Tuple[float, float]: (SGST rate, CGST rate)
        """
        half = round(gst_rate / 2, 2)
        return half, half
    
    def validate_selling_price(self, price: float) -> bool:
        """
        Validate that selling price is greater than 0
        
        Args:
            price: Selling price value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if price <= 0:
            return False, "Selling price must be greater than zero"
        return True, ""
    
    def validate_product_name(self, name: str) -> bool:
        """
        Validate that product name is not empty
        
        Args:
            name: Product name
            
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(name and name.strip())
    
    def prepare_product_data(
        self,
        name: str,
        hsn_code: Optional[str],
        barcode: Optional[str],
        unit: str,
        sales_rate: float,
        purchase_rate: float,
        discount_percent: float,
        mrp: float,
        tax_rate: float,
        sgst_rate: float,
        cgst_rate: float,
        opening_stock: float,
        low_stock: float,
        product_type: str,
        category: Optional[str],
        description: Optional[str],
        warranty_months: int,
        has_serial_number: int,
        is_gst_registered: int,
        track_stock: int,
        product_id: Optional[int] = None
    ) -> Dict:
        """
        Prepare product data dictionary for database operations
        
        Args:
            All product fields
            
        Returns:
            dict: Prepared product data
        """
        data = {
            'name': name,
            'hsn_code': hsn_code or None,
            'barcode': barcode or None,
            'unit': unit,
            'sales_rate': float(sales_rate),
            'purchase_rate': float(purchase_rate),
            'discount_percent': float(discount_percent),
            'mrp': float(mrp),
            'tax_rate': tax_rate,
            'sgst_rate': sgst_rate,
            'cgst_rate': cgst_rate,
            'opening_stock': float(opening_stock),
            'low_stock': float(low_stock),
            'product_type': product_type,
            'category': category or None,
            'description': description or None,
            'warranty_months': warranty_months,
            'has_serial_number': has_serial_number,
            'is_gst_registered': is_gst_registered,
            'track_stock': track_stock,
        }
        
        if product_id is not None:
            data['id'] = product_id
        
        return data
    
    def save_product(self, product_data: Dict, is_update: bool = False) -> Tuple[bool, str]:
        """
        Save product to database (add or update)
        
        Args:
            product_data: Product data dictionary
            is_update: True if updating existing product, False for new product
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.db:
            return False, "Database connection not available"
        
        try:
            if is_update:
                self.db.update_product(product_data)
                return True, "Product updated successfully!"
            else:
                # Remove 'id' if present for new product
                product_data.pop('id', None)
                self.db.add_product(**product_data)
                return True, "Product added successfully!"
        except Exception as e:
            return False, f"Failed to save product: {str(e)}"

    @staticmethod
    def get_stock_status(product: Dict) -> str:
        """
        Get stock status for a product
        
        Args:
            product: Product data dictionary
            
        Returns:
            str: Status string - "Service", "In Stock", "Low Stock", or "Out of Stock"
        """
        product_type = product.get('product_type', product.get('type', '')) or ''
        if product_type.lower() == 'service':
            return "Service"
        
        # Use current_stock if available, fallback to opening_stock
        stock = product.get('current_stock', 
                           product.get('opening_stock', 
                                      product.get('stock_quantity', 0))) or 0
        low_stock_alert = product.get('low_stock', 
                                      product.get('low_stock_alert', 5)) or 5
        
        if stock <= 0:
            return "Out of Stock"
        elif stock <= low_stock_alert:
            return "Low Stock"
        else:
            return "In Stock"

    @staticmethod
    def calculate_gst(data: dict):
        pass

# Singleton instance (can be initialized with db later)
product_service = ProductService()
