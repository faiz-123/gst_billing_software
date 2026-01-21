"""
Product Controller
Orchestrates product-related operations between UI and Service layers.

This controller handles:
- Product list loading and filtering
- Product form validation and save orchestration
- GST calculation coordination
- Form data preparation
- Delete operations
- Stock statistics
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.services.product_service import ProductService
from core.db.sqlite_db import db
from core.logger import get_logger, log_performance, UserActionLogger
from core.error_handler import ErrorHandler, handle_errors
from core.exceptions import ProductException, InsufficientStock

logger = get_logger(__name__)


@dataclass
class ProductFormData:
    """Data class for product form input"""
    name: str
    hsn_code: str
    barcode: str
    product_type: str
    category: str
    unit: str
    sales_rate: float
    purchase_rate: float
    mrp: float
    discount_percent: float
    is_gst_registered: bool
    tax_rate: float
    sgst_rate: float
    cgst_rate: float
    track_stock: bool
    opening_stock: int
    low_stock_alert: int
    warranty_months: int
    has_serial_number: bool
    description: str
    product_id: Optional[int] = None


@dataclass
class ProductStats:
    """Data class for product statistics"""
    total: int
    in_stock: int
    low_stock: int
    out_of_stock: int


class ProductController:
    """
    Controller for product form operations.
    
    Responsibilities:
    - Validate product form data
    - Calculate GST splits
    - Orchestrate save operations via service
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller with service reference."""
        self._service = ProductService(db)
    
    def calculate_split_gst(self, gst_rate: float) -> Tuple[float, float]:
        """
        Calculate SGST and CGST from total GST rate.
        
        Args:
            gst_rate: Total GST percentage
            
        Returns:
            Tuple of (sgst_rate, cgst_rate)
        """
        return self._service.calculate_split_gst(gst_rate)
    
    def validate_product_name(self, name: str) -> bool:
        """
        Validate product name is not empty.
        
        Args:
            name: Product name
            
        Returns:
            True if valid
        """
        return self._service.validate_product_name(name)
    
    def validate_selling_price(self, price: float) -> Tuple[bool, str]:
        """
        Validate selling price is greater than zero.
        
        Args:
            price: Selling price value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self._service.validate_selling_price(price)
    
    def save_product(self, form_data: ProductFormData) -> Tuple[bool, str]:
        """
        Save product from form data.
        
        Args:
            form_data: ProductFormData instance with all form values
            
        Returns:
            Tuple of (success, message)
        """
        # Prepare data for service
        product_data = self._service.prepare_product_data(
            name=form_data.name,
            hsn_code=form_data.hsn_code,
            barcode=form_data.barcode,
            unit=form_data.unit,
            sales_rate=form_data.sales_rate,
            purchase_rate=form_data.purchase_rate,
            discount_percent=form_data.discount_percent,
            mrp=form_data.mrp,
            tax_rate=form_data.tax_rate,
            sgst_rate=form_data.sgst_rate,
            cgst_rate=form_data.cgst_rate,
            opening_stock=form_data.opening_stock,
            low_stock=form_data.low_stock_alert,
            product_type=form_data.product_type,
            category=form_data.category,
            description=form_data.description,
            warranty_months=form_data.warranty_months,
            has_serial_number=1 if form_data.has_serial_number else 0,
            is_gst_registered=1 if form_data.is_gst_registered else 0,
            track_stock=1 if form_data.track_stock else 0,
            product_id=form_data.product_id
        )
        
        # Save via service
        is_update = form_data.product_id is not None
        return self._service.save_product(product_data, is_update)
    
    def get_default_gst_values(self) -> Tuple[float, float, float]:
        """
        Get default GST values when GST is enabled.
        
        Returns:
            Tuple of (tax_rate, sgst, cgst)
        """
        default_gst = 18.0
        sgst, cgst = self._service.calculate_split_gst(default_gst)
        return default_gst, sgst, cgst

    # -------------------------------------------------------------------------
    # List Screen Methods
    # -------------------------------------------------------------------------
    
    @log_performance
    def get_all_products(self) -> List[Dict]:
        """
        Fetch all products from database.
        
        Returns:
            List of product dictionaries
        """
        try:
            logger.debug("Fetching all products from database")
            products = db.get_products()
            if products:
                result = [dict(p) if hasattr(p, 'keys') else p for p in products]
                logger.info(f"Successfully fetched {len(result)} products")
                return result
            logger.debug("No products found in database")
            return []
        except Exception as e:
            logger.error(f"Error loading products: {e}", exc_info=True)
            return []
    
    @log_performance
    @handle_errors("Delete Product")
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """
        Delete a product by ID.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Attempting to delete product ID: {product_id}")
            
            # Get product details before deletion for logging
            product = db.get_product_by_id(product_id)
            if not product:
                raise ProductException("Product not found")
            
            product_name = product.get('name', 'Unknown')
            
            # Delete the product
            db.delete_product(product_id)
            
            UserActionLogger.log_product_created(product_id, product_name)  # Using for consistency
            logger.info(f"Successfully deleted product ID: {product_id}, Name: {product_name}")
            return True, "Product deleted successfully!"
            
        except ProductException as e:
            logger.error(f"Product error while deleting {product_id}: {e.error_code}", exc_info=True)
            return False, e.to_user_message()
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}", exc_info=True)
            return ErrorHandler.handle_exception(e, "Delete Product", show_dialog=False)
    
    def get_stock_status(self, product: Dict) -> str:
        """
        Get stock status for a product.
        
        Args:
            product: Product data dictionary
            
        Returns:
            Status string - "Service", "In Stock", "Low Stock", or "Out of Stock"
        """
        return ProductService.get_stock_status(product)
    
    def calculate_stats(self, products: List[Dict]) -> ProductStats:
        """
        Calculate product statistics from a list of products.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            ProductStats with counts for each category
        """
        total = len(products)
        in_stock = sum(1 for p in products if self.get_stock_status(p) == "In Stock")
        low_stock = sum(1 for p in products if self.get_stock_status(p) == "Low Stock")
        out_of_stock = sum(1 for p in products if self.get_stock_status(p) == "Out of Stock")
        
        return ProductStats(
            total=total,
            in_stock=in_stock,
            low_stock=low_stock,
            out_of_stock=out_of_stock
        )
    
    def extract_categories(self, products: List[Dict]) -> List[str]:
        """
        Extract unique categories from products list.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Sorted list of unique category names
        """
        categories = set()
        for product in products:
            category = product.get('category')
            if category:
                categories.add(category)
        return sorted(categories)
    
    def filter_products(
        self,
        products: List[Dict],
        search_text: str = "",
        type_filter: str = "All",
        category_filter: str = "All Categories",
        stock_filter: str = "All"
    ) -> List[Dict]:
        """
        Filter products based on search and dropdown criteria.
        
        Args:
            products: List of all products
            search_text: Text to search in name, sku, category
            type_filter: Product type filter ("All", "Goods", "Service")
            category_filter: Category filter ("All Categories" or specific)
            stock_filter: Stock status filter ("All", "In Stock", etc.)
            
        Returns:
            Filtered list of products
        """
        search_text = search_text.lower()
        filtered = []
        
        for product in products:
            # Search filter
            if search_text:
                search_fields = [
                    (product.get('name') or '').lower(),
                    (product.get('sku') or '').lower(),
                    (product.get('category') or '').lower()
                ]
                if not any(search_text in field for field in search_fields):
                    continue
            
            # Type filter
            product_type = product.get('product_type', product.get('type', ''))
            if type_filter != "All" and product_type != type_filter:
                continue
            
            # Category filter
            if category_filter != "All Categories" and product.get('category', '') != category_filter:
                continue
            
            # Stock status filter
            status = self.get_stock_status(product)
            if stock_filter != "All" and status != stock_filter:
                continue
            
            filtered.append(product)
        
        return filtered


# Singleton instance for convenience
product_controller = ProductController()
