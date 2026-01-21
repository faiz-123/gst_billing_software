"""
Invoice Service
Business logic for invoice operations
"""

from typing import List, Dict, Optional
from datetime import datetime
from core.logger import get_logger
from core.exceptions import (
    InvoiceException, InvoiceAlreadyExistsException,
    InvalidInvoiceTotal, InvoiceNotFound
)

logger = get_logger(__name__)


class InvoiceService:
    """Service class for invoice-related business logic"""
    
    def __init__(self, db):
        self.db = db
    
    def generate_invoice_number(self, prefix: str = "INV", year_format: bool = True) -> str:
        """
        Generate a unique invoice number
        
        Args:
            prefix: Prefix for the invoice number
            year_format: Whether to include year in the format
            
        Returns:
            str: Generated invoice number
        """
        # Get current financial year
        today = datetime.now()
        if today.month >= 4:
            fy_start = today.year
            fy_end = today.year + 1
        else:
            fy_start = today.year - 1
            fy_end = today.year
        
        # Get last invoice number for this financial year
        invoices = self.db.get_invoices()
        
        # Filter invoices for current financial year
        max_number = 0
        fy_prefix = f"{prefix}-{fy_start % 100:02d}{fy_end % 100:02d}-" if year_format else f"{prefix}-"
        
        for inv in invoices:
            inv_no = inv.get('invoice_no', '')
            if inv_no.startswith(fy_prefix):
                try:
                    num_part = inv_no.replace(fy_prefix, '')
                    num = int(num_part)
                    if num > max_number:
                        max_number = num
                except ValueError:
                    pass
        
        new_number = max_number + 1
        return f"{fy_prefix}{new_number:04d}"
    
    def calculate_invoice_totals(self, items: List[Dict], tax_type: str = "GST") -> Dict:
        """
        Calculate invoice totals from line items
        
        Args:
            items: List of invoice line items
            tax_type: Type of tax (GST or Non-GST)
            
        Returns:
            dict: Calculated totals
        """
        subtotal = 0.0
        total_discount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        
        for item in items:
            quantity = float(item.get('quantity', 0) or 0)
            rate = float(item.get('rate', 0) or 0)
            discount_percent = float(item.get('discount_percent', 0) or 0)
            tax_percent = float(item.get('tax_percent', 0) or 0)
            
            item_total = quantity * rate
            discount_amount = item_total * (discount_percent / 100)
            taxable_amount = item_total - discount_amount
            
            subtotal += taxable_amount
            total_discount += discount_amount
            
            if tax_type.upper() == "GST":
                # Split tax equally between CGST and SGST (assuming intra-state)
                tax_amount = taxable_amount * (tax_percent / 100)
                total_cgst += tax_amount / 2
                total_sgst += tax_amount / 2
        
        # Calculate grand total
        total_tax = total_cgst + total_sgst + total_igst
        grand_total_raw = subtotal + total_tax
        
        # Round off
        grand_total = round(grand_total_raw)
        round_off = grand_total - grand_total_raw
        
        return {
            'subtotal': round(subtotal, 2),
            'discount': round(total_discount, 2),
            'cgst': round(total_cgst, 2),
            'sgst': round(total_sgst, 2),
            'igst': round(total_igst, 2),
            'round_off': round(round_off, 2),
            'grand_total': grand_total,
            'total_tax': round(total_tax, 2)
        }
    
    def get_invoice_status(self, grand_total: float, paid_amount: float) -> str:
        """
        Determine invoice status based on payment
        
        Args:
            grand_total: Total invoice amount
            paid_amount: Amount already paid
            
        Returns:
            str: Invoice status
        """
        if paid_amount <= 0:
            return "Pending"
        elif paid_amount >= grand_total:
            return "Paid"
        else:
            return "Partial"
    
    def get_invoices_summary(self) -> Dict:
        """
        Get summary statistics for invoices
        
        Returns:
            dict: Summary statistics
        """
        invoices = self.db.get_invoices()
        
        total_amount = 0.0
        paid_amount = 0.0
        pending_count = 0
        paid_count = 0
        
        for inv in invoices:
            grand_total = float(inv.get('grand_total', 0) or 0)
            balance_due = float(inv.get('balance_due', 0) or 0)
            status = inv.get('status', 'Unpaid') or 'Unpaid'
            
            total_amount += grand_total
            paid_amount += (grand_total - balance_due)
            
            if status.lower() == 'paid':
                paid_count += 1
            elif status.lower() in ['pending', 'partial', 'unpaid']:
                pending_count += 1
        
        return {
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': total_amount - paid_amount,
            'paid_count': paid_count,
            'pending_count': pending_count
        }

    def get_recent_party_ids(self, limit: int = 5) -> list:
        """
        Get list of recently used party IDs from invoices.
        
        Args:
            limit: Maximum number of recent parties to return
            
        Returns:
            List of unique party IDs ordered by most recent invoice
        """
        try:
            result = self.db._query(
                """
                SELECT DISTINCT party_id 
                FROM invoices 
                ORDER BY date DESC, id DESC 
                LIMIT ?
                """,
                (limit,)
            )
            return [row['party_id'] for row in result if row['party_id']]
        except Exception as e:
            print(f"Error fetching recent party IDs: {e}")
            return []

    def get_recent_product_ids(self, limit: int = 10) -> list:
        """
        Get list of recently used product IDs from invoice items.
        
        Args:
            limit: Maximum number of recent products to return
            
        Returns:
            List of unique product IDs ordered by most recent usage
        """
        try:
            result = self.db._query(
                """
                SELECT DISTINCT ii.product_id 
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.id
                ORDER BY i.date DESC, i.id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [row['product_id'] for row in result if row['product_id']]
        except Exception as e:
            print(f"Error fetching recent product IDs: {e}")
            return []

    def calculate_invoice_totals_detailed(self, items: list, tax_type: str, 
                                         invoice_discount: float = 0.0, 
                                         invoice_discount_type: str = "%",
                                         other_charges: float = 0.0) -> Dict:
        """
        Calculate detailed invoice totals with all components for UI display.
        
        This is the comprehensive calculation method used by the UI for real-time updates.
        Handles:
        - Item-level subtotals and discounts
        - Invoice-level discount (% or flat)
        - GST breakdown (CGST/SGST for Same State, IGST for Other State)
        - Other charges (shipping, packaging, etc.)
        - Grand total and balance due
        
        Args:
            items: List of item dictionaries from invoice items widget
                  Each item must have: quantity, rate, discount_amount, tax_amount
            tax_type: Invoice tax type ('GST - Same State', 'GST - Other State', 'Non-GST')
            invoice_discount: Invoice-level discount value (amount or percentage)
            invoice_discount_type: Type of discount ("%" for percentage, "₹" or other for flat)
            other_charges: Additional charges to add to invoice
            
        Returns:
            Dict with comprehensive breakdown:
            {
                'subtotal': float,
                'item_discount': float,
                'invoice_discount': float,
                'total_discount': float,
                'cgst': float,
                'sgst': float,
                'igst': float,
                'total_tax': float,
                'other_charges': float,
                'roundoff_amount': float,  # For rounding to nearest rupee
                'grand_total': float,
                'is_interstate': bool,
                'is_non_gst': bool,
                'item_count': int,
                'has_decimal': bool  # Whether grand total has decimal portion
            }
        """
        try:
            subtotal = 0.0
            total_item_discount = 0.0
            total_tax = 0.0
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            item_count = 0
            
            # Determine tax classification
            is_interstate = 'Other State' in tax_type
            is_non_gst = 'Non-GST' in tax_type
            
            # Calculate item-level totals
            for item in items:
                if not item:
                    continue
                    
                quantity = float(item.get('quantity', 0) or 0)
                rate = float(item.get('rate', 0) or 0)
                item_subtotal = quantity * rate
                subtotal += item_subtotal
                
                # Item discount
                item_discount = float(item.get('discount_amount', 0) or 0)
                total_item_discount += item_discount
                
                # Item tax
                item_tax = float(item.get('tax_amount', 0) or 0)
                total_tax += item_tax
                item_count += 1
                
                # GST breakdown for this item
                if item_tax > 0 and not is_non_gst:
                    if is_interstate:
                        total_igst += item_tax
                    else:
                        # Split evenly between CGST and SGST (intra-state)
                        cgst_amount = item_tax / 2
                        sgst_amount = item_tax / 2
                        total_cgst += cgst_amount
                        total_sgst += sgst_amount
            
            # Calculate invoice-level discount
            calc_invoice_discount = 0.0
            if invoice_discount > 0:
                if invoice_discount_type == "%":
                    # Percentage discount on (subtotal - item_discount)
                    taxable_amount = subtotal - total_item_discount
                    calc_invoice_discount = (taxable_amount * invoice_discount) / 100
                else:
                    # Flat amount discount
                    calc_invoice_discount = invoice_discount
            
            # Total discount = item-level + invoice-level
            total_discount = total_item_discount + calc_invoice_discount
            
            # Calculate grand total before roundoff
            grand_total_before_roundoff = subtotal - total_discount + total_tax + other_charges
            
            # Calculate roundoff (round to nearest rupee)
            roundoff_amount = round(grand_total_before_roundoff) - grand_total_before_roundoff
            grand_total = round(grand_total_before_roundoff)
            
            # Check if grand total has decimal portion (for roundoff visibility)
            has_decimal = round(grand_total_before_roundoff, 2) % 1 != 0
            
            return {
                'subtotal': round(subtotal, 2),
                'item_discount': round(total_item_discount, 2),
                'invoice_discount': round(calc_invoice_discount, 2),
                'total_discount': round(total_discount, 2),
                'cgst': round(total_cgst, 2),
                'sgst': round(total_sgst, 2),
                'igst': round(total_igst, 2),
                'total_tax': round(total_tax, 2),
                'other_charges': round(other_charges, 2),
                'roundoff_amount': round(roundoff_amount, 2),
                'grand_total': grand_total,
                'is_interstate': is_interstate,
                'is_non_gst': is_non_gst,
                'item_count': item_count,
                'has_decimal': has_decimal
            }
            
        except Exception as e:
            print(f"Error calculating invoice totals: {e}")
            # Return default values on error
            return {
                'subtotal': 0.0,
                'item_discount': 0.0,
                'invoice_discount': 0.0,
                'total_discount': 0.0,
                'cgst': 0.0,
                'sgst': 0.0,
                'igst': 0.0,
                'total_tax': 0.0,
                'other_charges': 0.0,
                'roundoff_amount': 0.0,
                'grand_total': 0,
                'is_interstate': False,
                'is_non_gst': False,
                'item_count': 0,
                'has_decimal': False
            }

