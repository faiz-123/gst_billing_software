"""
Stock Service
Business logic for stock/inventory operations
"""

from typing import List, Dict, Optional


class StockService:
    """Service class for stock-related business logic"""
    
    def __init__(self, db):
        self.db = db
    
    def update_stock_for_sale(self, items: List[Dict]) -> bool:
        """
        Update stock for items sold (decrease stock)
        
        Args:
            items: List of items with product_id and quantity
            
        Returns:
            bool: True if successful
        """
        for item in items:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity', 0))
            if product_id and quantity > 0:
                self.db.update_product_stock(product_id, quantity, 'subtract')
        return True
    
    def update_stock_for_purchase(self, items: List[Dict]) -> bool:
        """
        Update stock for items purchased (increase stock)
        
        Args:
            items: List of items with product_id and quantity
            
        Returns:
            bool: True if successful
        """
        for item in items:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity', 0))
            if product_id and quantity > 0:
                self.db.update_product_stock(product_id, quantity, 'add')
        return True
    
    def check_stock_availability(self, product_id: int, required_quantity: float) -> Dict:
        """
        Check if sufficient stock is available
        
        Args:
            product_id: Product ID to check
            required_quantity: Quantity required
            
        Returns:
            dict: Stock availability info
        """
        product = self.db.get_product_by_id(product_id)
        if not product:
            return {
                'available': False,
                'message': 'Product not found',
                'current_stock': 0,
                'required': required_quantity
            }
        
        current_stock = float(product.get('current_stock', 0) or 0)
        track_stock = bool(product.get('track_stock', 0))
        
        if not track_stock:
            # If stock tracking is disabled, always allow
            return {
                'available': True,
                'message': 'Stock tracking disabled',
                'current_stock': current_stock,
                'required': required_quantity
            }
        
        available = current_stock >= required_quantity
        return {
            'available': available,
            'message': 'Sufficient stock' if available else 'Insufficient stock',
            'current_stock': current_stock,
            'required': required_quantity,
            'shortage': max(0, required_quantity - current_stock)
        }
    
    def get_low_stock_products(self) -> List[Dict]:
        """
        Get list of products below low stock threshold
        
        Returns:
            List[Dict]: Products with low stock
        """
        products = self.db.get_products()
        low_stock_products = []
        
        for product in products:
            track_stock = bool(product.get('track_stock', 0))
            if not track_stock:
                continue
            
            current_stock = float(product.get('current_stock', 0) or 0)
            low_stock = float(product.get('low_stock', 0) or 0)
            
            if current_stock <= low_stock:
                low_stock_products.append({
                    'id': product['id'],
                    'name': product['name'],
                    'current_stock': current_stock,
                    'low_stock_threshold': low_stock,
                    'shortage': max(0, low_stock - current_stock)
                })
        
        return low_stock_products
    
    def get_stock_summary(self) -> Dict:
        """
        Get stock summary statistics
        
        Returns:
            dict: Stock summary
        """
        products = self.db.get_products()
        
        total_products = len(products)
        tracked_products = 0
        low_stock_count = 0
        out_of_stock_count = 0
        total_stock_value = 0.0
        
        for product in products:
            track_stock = bool(product.get('track_stock', 0))
            if track_stock:
                tracked_products += 1
                current_stock = float(product.get('current_stock', 0) or 0)
                low_stock = float(product.get('low_stock', 0) or 0)
                purchase_rate = float(product.get('purchase_rate', 0) or 0)
                
                if current_stock <= 0:
                    out_of_stock_count += 1
                elif current_stock <= low_stock:
                    low_stock_count += 1
                
                total_stock_value += current_stock * purchase_rate
        
        return {
            'total_products': total_products,
            'tracked_products': tracked_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_stock_value': round(total_stock_value, 2)
        }
