"""
Payment Service
Business logic for payment and receipt operations
"""

from typing import List, Dict, Optional
from datetime import datetime

from core.db.sqlite_db import db as default_db


class PaymentService:
    """Service class for payment-related business logic"""
    
    def __init__(self, db=None):
        self.db = db or default_db
    
    # ─────────────────────────────────────────────────────────────────────────
    # CRUD Operations (delegated to DB)
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_payments(self, payment_type: str = None) -> List[Dict]:
        """
        Get all payments, optionally filtered by type.
        
        Args:
            payment_type: Filter by type ('PAYMENT' or 'RECEIPT')
            
        Returns:
            List of payment dictionaries
        """
        return self.db.get_payments(payment_type) or []
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        """
        Get a single payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment dictionary or None
        """
        payments = self.db.get_payments()
        for payment in payments:
            if payment.get('id') == payment_id:
                return payment
        return None
    
    def delete_payment(self, payment_id: int) -> bool:
        """
        Delete a payment by ID.
        
        Args:
            payment_id: Payment ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.db.delete_payment(payment_id)
            return True
        except Exception as e:
            print(f"[PaymentService] Error deleting payment: {e}")
            return False
    
    # ─────────────────────────────────────────────────────────────────────────
    # ID Generation
    # ─────────────────────────────────────────────────────────────────────────
    
    def generate_payment_id(self, payment_type: str = "PAYMENT") -> str:
        """
        Generate a unique payment ID
        
        Args:
            payment_type: Type of payment (PAYMENT or RECEIPT)
            
        Returns:
            str: Generated payment ID
        """
        prefix = "PAY" if payment_type == "PAYMENT" else "RCP"
        
        # Get current date for the ID
        today = datetime.now()
        date_part = today.strftime('%Y%m%d')
        
        # Get last payment number for today
        payments = self.db.get_payments(payment_type)
        
        max_number = 0
        id_prefix = f"{prefix}-{date_part}-"
        
        for payment in payments:
            pay_id = payment.get('payment_id', '')
            if pay_id and pay_id.startswith(id_prefix):
                try:
                    num_part = pay_id.replace(id_prefix, '')
                    num = int(num_part)
                    if num > max_number:
                        max_number = num
                except ValueError:
                    pass
        
        new_number = max_number + 1
        return f"{id_prefix}{new_number:04d}"
    
    def process_payment(self, party_id: int, amount: float, mode: str = "Cash",
                       invoice_id: int = None, notes: str = None) -> int:
        """
        Process a payment to a supplier
        
        Args:
            party_id: Supplier party ID
            amount: Payment amount
            mode: Payment mode
            invoice_id: Optional linked invoice ID
            notes: Optional notes
            
        Returns:
            int: Created payment ID
        """
        payment_id = self.generate_payment_id("PAYMENT")
        date = datetime.now().strftime('%Y-%m-%d')
        
        return self.db.add_payment(
            payment_id=payment_id,
            party_id=party_id,
            amount=amount,
            date=date,
            mode=mode,
            invoice_id=invoice_id,
            notes=notes,
            payment_type="PAYMENT"
        )
    
    def process_receipt(self, party_id: int, amount: float, mode: str = "Cash",
                       invoice_id: int = None, notes: str = None) -> int:
        """
        Process a receipt from a customer
        
        Args:
            party_id: Customer party ID
            amount: Receipt amount
            mode: Payment mode
            invoice_id: Optional linked invoice ID
            notes: Optional notes
            
        Returns:
            int: Created receipt ID
        """
        receipt_id = self.generate_payment_id("RECEIPT")
        date = datetime.now().strftime('%Y-%m-%d')
        
        return self.db.add_payment(
            payment_id=receipt_id,
            party_id=party_id,
            amount=amount,
            date=date,
            mode=mode,
            invoice_id=invoice_id,
            notes=notes,
            payment_type="RECEIPT"
        )
    
    def get_payments_summary(self) -> Dict:
        """
        Get summary statistics for payments
        
        Returns:
            dict: Summary statistics
        """
        payments = self.db.get_payments("PAYMENT")
        receipts = self.db.get_payments("RECEIPT")
        
        total_payments = sum(float(p.get('amount', 0) or 0) for p in payments)
        total_receipts = sum(float(r.get('amount', 0) or 0) for r in receipts)
        
        return {
            'total_payments_count': len(payments),
            'total_payments_amount': round(total_payments, 2),
            'total_receipts_count': len(receipts),
            'total_receipts_amount': round(total_receipts, 2),
            'net_cash_flow': round(total_receipts - total_payments, 2)
        }
    
    def get_payment_modes_breakdown(self, payment_type: str = None) -> Dict:
        """
        Get breakdown of payments by mode
        
        Args:
            payment_type: Optional filter by type (PAYMENT or RECEIPT)
            
        Returns:
            dict: Breakdown by payment mode
        """
        payments = self.db.get_payments(payment_type)
        
        breakdown = {}
        for payment in payments:
            mode = payment.get('mode', 'Cash')
            amount = float(payment.get('amount', 0) or 0)
            
            if mode not in breakdown:
                breakdown[mode] = {'count': 0, 'amount': 0.0}
            
            breakdown[mode]['count'] += 1
            breakdown[mode]['amount'] += amount
        
        # Round amounts
        for mode in breakdown:
            breakdown[mode]['amount'] = round(breakdown[mode]['amount'], 2)
        
        return breakdown


# Singleton instance for app-wide use
payment_service = PaymentService()
