"""
Ledger Service
Business logic for ledger/accounting operations
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta


class LedgerService:
    """Service class for ledger-related business logic"""
    
    def __init__(self, db):
        self.db = db
    
    def get_party_balance(self, party_id: int) -> Dict:
        """
        Calculate current balance for a party
        
        Args:
            party_id: Party ID
            
        Returns:
            dict: Balance information
        """
        # Get party opening balance
        parties = self.db._query("SELECT * FROM parties WHERE id = ?", (party_id,))
        if not parties:
            return {'balance': 0}
        
        party = parties[0]
        opening_balance = float(party.get('opening_balance', 0) or 0)
        party_type = (party.get('party_type', 'Customer') or 'Customer').lower()
        
        # Calculate from invoices (amount owed by customer)
        invoices = self.db._query(
            "SELECT SUM(grand_total) as total FROM invoices WHERE party_id = ?",
            (party_id,)
        )
        invoice_total = float(invoices[0]['total'] or 0) if invoices else 0
        
        # Calculate from receipts (amount received from customer)
        # Include payments with type='RECEIPT' OR type IS NULL (for backward compatibility)
        receipts = self.db._query(
            "SELECT SUM(amount) as total FROM payments WHERE party_id = ? AND (type = 'RECEIPT' OR type IS NULL)",
            (party_id,)
        )
        receipt_total = float(receipts[0]['total'] or 0) if receipts else 0
        
        # Calculate from purchases (amount owed to supplier)
        purchases = self.db._query(
            "SELECT SUM(grand_total) as total FROM purchase_invoices WHERE supplier_id = ?",
            (party_id,)
        )
        purchase_total = float(purchases[0]['total'] or 0) if purchases else 0
        
        # Calculate from payments (amount paid to supplier)
        # Include payments with type='PAYMENT' (supplier payments typically have explicit type)
        payments = self.db._query(
            "SELECT SUM(amount) as total FROM payments WHERE party_id = ? AND type = 'PAYMENT'",
            (party_id,)
        )
        payment_total = float(payments[0]['total'] or 0) if payments else 0
        
        # Net balance calculation
        # For customers: invoice_total - receipt_total (positive means customer owes)
        # For suppliers: purchase_total - payment_total (positive means we owe)
        customer_balance = invoice_total - receipt_total
        supplier_balance = purchase_total - payment_total
        
        # Add opening balance based on party type
        # Suppliers: opening balance is credit (we owe them)
        # Customers: opening balance is debit (they owe us)
        if party_type == 'supplier':
            supplier_balance += opening_balance
        else:
            customer_balance += opening_balance
        
        return {
            'party_id': party_id,
            'party_name': party.get('name', ''),
            'party_type': party_type,
            'opening_balance': opening_balance,
            'invoice_total': invoice_total,
            'receipt_total': receipt_total,
            'purchase_total': purchase_total,
            'payment_total': payment_total,
            'customer_balance': round(customer_balance, 2),
            'supplier_balance': round(supplier_balance, 2)
        }
    
    def get_outstanding_receivables(self) -> List[Dict]:
        """
        Get list of outstanding receivables (customer dues)
        
        Returns:
            List[Dict]: Customers with outstanding balances
        """
        parties = self.db.get_parties()
        receivables = []
        
        for party in parties:
            party_type = party.get('party_type', 'Customer')
            if (party_type or '').lower() not in ['customer', 'both']:
                continue
            
            balance_info = self.get_party_balance(party['id'])
            customer_balance = balance_info['customer_balance']
            
            if customer_balance > 0:
                receivables.append({
                    'party_id': party['id'],
                    'party_name': party.get('name', ''),
                    'amount': customer_balance
                })
        
        return sorted(receivables, key=lambda x: x['amount'], reverse=True)
    
    def get_outstanding_payables(self) -> List[Dict]:
        """
        Get list of outstanding payables (supplier dues)
        
        Returns:
            List[Dict]: Suppliers with outstanding balances
        """
        parties = self.db.get_parties()
        payables = []
        
        for party in parties:
            party_type = party.get('party_type', 'Customer')
            if (party_type or '').lower() not in ['supplier', 'both']:
                continue
            
            balance_info = self.get_party_balance(party['id'])
            supplier_balance = balance_info['supplier_balance']
            
            if supplier_balance > 0:
                payables.append({
                    'party_id': party['id'],
                    'party_name': party.get('name', ''),
                    'amount': supplier_balance
                })
        
        return sorted(payables, key=lambda x: x['amount'], reverse=True)
    
    def get_financial_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get financial summary for a period
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            dict: Financial summary
        """
        # Default to current month if dates not provided
        if not start_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get sales total
        sales_query = """
            SELECT COALESCE(SUM(grand_total), 0) as total 
            FROM invoices 
            WHERE date BETWEEN ? AND ?
        """
        if self.db._current_company_id:
            sales_query += " AND company_id = ?"
            sales = self.db._query(sales_query, (start_date, end_date, self.db._current_company_id))
        else:
            sales = self.db._query(sales_query, (start_date, end_date))
        sales_total = float(sales[0]['total'] or 0) if sales else 0
        
        # Get purchases total
        purchases_query = """
            SELECT COALESCE(SUM(grand_total), 0) as total 
            FROM purchase_invoices 
            WHERE date BETWEEN ? AND ?
        """
        if self.db._current_company_id:
            purchases_query += " AND company_id = ?"
            purchases = self.db._query(purchases_query, (start_date, end_date, self.db._current_company_id))
        else:
            purchases = self.db._query(purchases_query, (start_date, end_date))
        purchases_total = float(purchases[0]['total'] or 0) if purchases else 0
        
        # Get receipts total
        receipts_query = """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM payments 
            WHERE type = 'RECEIPT' AND date BETWEEN ? AND ?
        """
        if self.db._current_company_id:
            receipts_query += " AND company_id = ?"
            receipts = self.db._query(receipts_query, (start_date, end_date, self.db._current_company_id))
        else:
            receipts = self.db._query(receipts_query, (start_date, end_date))
        receipts_total = float(receipts[0]['total'] or 0) if receipts else 0
        
        # Get payments total
        payments_query = """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM payments 
            WHERE type = 'PAYMENT' AND date BETWEEN ? AND ?
        """
        if self.db._current_company_id:
            payments_query += " AND company_id = ?"
            payments = self.db._query(payments_query, (start_date, end_date, self.db._current_company_id))
        else:
            payments = self.db._query(payments_query, (start_date, end_date))
        payments_total = float(payments[0]['total'] or 0) if payments else 0
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'sales_total': round(sales_total, 2),
            'purchases_total': round(purchases_total, 2),
            'receipts_total': round(receipts_total, 2),
            'payments_total': round(payments_total, 2),
            'gross_profit': round(sales_total - purchases_total, 2),
            'net_cash_flow': round(receipts_total - payments_total, 2)
        }
