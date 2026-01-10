"""
Invoice Service
Business logic for invoice operations
"""

from typing import List, Dict, Optional
from datetime import datetime


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
            status = inv.get('status', 'Draft') or 'Draft'
            
            total_amount += grand_total
            paid_amount += (grand_total - balance_due)
            
            if status.lower() == 'paid':
                paid_count += 1
            elif status.lower() in ['pending', 'partial']:
                pending_count += 1
        
        return {
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': total_amount - paid_amount,
            'paid_count': paid_count,
            'pending_count': pending_count
        }
