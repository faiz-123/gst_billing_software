"""
GST Service
Business logic for GST calculations and reporting
"""

from typing import List, Dict, Optional
from datetime import datetime


class GSTService:
    """Service class for GST-related business logic"""
    
    # Standard GST rates in India
    GST_RATES = [0, 5, 12, 18, 28]
    
    def __init__(self, db):
        self.db = db
    
    def calculate_gst(self, amount: float, rate: float, is_interstate: bool = False) -> Dict:
        """
        Calculate GST breakdown
        
        Args:
            amount: Taxable amount
            rate: GST rate percentage
            is_interstate: Whether it's an interstate transaction
            
        Returns:
            dict: GST breakdown
        """
        total_gst = amount * (rate / 100)
        
        if is_interstate:
            return {
                'cgst_rate': 0,
                'cgst_amount': 0,
                'sgst_rate': 0,
                'sgst_amount': 0,
                'igst_rate': rate,
                'igst_amount': round(total_gst, 2),
                'total_gst': round(total_gst, 2)
            }
        else:
            half_rate = rate / 2
            half_amount = total_gst / 2
            return {
                'cgst_rate': half_rate,
                'cgst_amount': round(half_amount, 2),
                'sgst_rate': half_rate,
                'sgst_amount': round(half_amount, 2),
                'igst_rate': 0,
                'igst_amount': 0,
                'total_gst': round(total_gst, 2)
            }
    
    def get_hsn_summary(self, invoice_id: int) -> List[Dict]:
        """
        Get HSN-wise summary for an invoice
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            List[Dict]: HSN-wise breakdown
        """
        items = self.db.get_invoice_items(invoice_id)
        
        hsn_summary = {}
        for item in items:
            hsn = item.get('hsn_code', 'N/A') or 'N/A'
            tax_percent = float(item.get('tax_percent', 0) or 0)
            amount = float(item.get('amount', 0) or 0)
            tax_amount = float(item.get('tax_amount', 0) or 0)
            
            key = f"{hsn}_{tax_percent}"
            
            if key not in hsn_summary:
                hsn_summary[key] = {
                    'hsn_code': hsn,
                    'tax_rate': tax_percent,
                    'taxable_value': 0,
                    'cgst_amount': 0,
                    'sgst_amount': 0,
                    'igst_amount': 0,
                    'total_tax': 0
                }
            
            taxable = amount - tax_amount
            hsn_summary[key]['taxable_value'] += taxable
            hsn_summary[key]['total_tax'] += tax_amount
            hsn_summary[key]['cgst_amount'] += tax_amount / 2
            hsn_summary[key]['sgst_amount'] += tax_amount / 2
        
        # Round values and convert to list
        result = []
        for data in hsn_summary.values():
            result.append({
                'hsn_code': data['hsn_code'],
                'tax_rate': data['tax_rate'],
                'taxable_value': round(data['taxable_value'], 2),
                'cgst_amount': round(data['cgst_amount'], 2),
                'sgst_amount': round(data['sgst_amount'], 2),
                'igst_amount': round(data['igst_amount'], 2),
                'total_tax': round(data['total_tax'], 2)
            })
        
        return result
    
    def get_gst_report(self, start_date: str, end_date: str) -> Dict:
        """
        Generate GST report for a period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            dict: GST report
        """
        # Get sales invoices
        sales_query = """
            SELECT * FROM invoices 
            WHERE date BETWEEN ? AND ? AND tax_type = 'GST'
        """
        if self.db._current_company_id:
            sales_query += " AND company_id = ?"
            sales = self.db._query(sales_query, (start_date, end_date, self.db._current_company_id))
        else:
            sales = self.db._query(sales_query, (start_date, end_date))
        
        # Get purchase invoices
        purchases_query = """
            SELECT * FROM purchase_invoices 
            WHERE date BETWEEN ? AND ? AND type = 'GST'
        """
        if self.db._current_company_id:
            purchases_query += " AND company_id = ?"
            purchases = self.db._query(purchases_query, (start_date, end_date, self.db._current_company_id))
        else:
            purchases = self.db._query(purchases_query, (start_date, end_date))
        
        # Calculate output GST (from sales)
        output_cgst = sum(float(inv.get('cgst', 0) or 0) for inv in sales)
        output_sgst = sum(float(inv.get('sgst', 0) or 0) for inv in sales)
        output_igst = sum(float(inv.get('igst', 0) or 0) for inv in sales)
        
        # For input GST, we would need to track GST on purchases
        # This is a simplified version
        input_cgst = 0
        input_sgst = 0
        input_igst = 0
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'output_gst': {
                'cgst': round(output_cgst, 2),
                'sgst': round(output_sgst, 2),
                'igst': round(output_igst, 2),
                'total': round(output_cgst + output_sgst + output_igst, 2)
            },
            'input_gst': {
                'cgst': round(input_cgst, 2),
                'sgst': round(input_sgst, 2),
                'igst': round(input_igst, 2),
                'total': round(input_cgst + input_sgst + input_igst, 2)
            },
            'net_payable': {
                'cgst': round(output_cgst - input_cgst, 2),
                'sgst': round(output_sgst - input_sgst, 2),
                'igst': round(output_igst - input_igst, 2),
                'total': round((output_cgst + output_sgst + output_igst) - 
                              (input_cgst + input_sgst + input_igst), 2)
            },
            'sales_count': len(sales),
            'purchases_count': len(purchases)
        }
    
    def validate_gstin(self, gstin: str) -> Dict:
        """
        Validate GSTIN format
        
        Args:
            gstin: GSTIN to validate
            
        Returns:
            dict: Validation result
        """
        import re
        
        if not gstin:
            return {'valid': True, 'message': 'GSTIN is optional'}
        
        gstin = gstin.upper().strip()
        
        # Length check
        if len(gstin) != 15:
            return {'valid': False, 'message': 'GSTIN must be 15 characters'}
        
        # Pattern check
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, gstin):
            return {'valid': False, 'message': 'Invalid GSTIN format'}
        
        # State code check
        state_code = int(gstin[:2])
        if state_code < 1 or state_code > 37:
            return {'valid': False, 'message': 'Invalid state code in GSTIN'}
        
        return {'valid': True, 'message': 'Valid GSTIN', 'gstin': gstin}
    
    def get_state_from_gstin(self, gstin: str) -> Optional[str]:
        """
        Extract state from GSTIN
        
        Args:
            gstin: GSTIN
            
        Returns:
            str: State name or None
        """
        if not gstin or len(gstin) < 2:
            return None
        
        state_codes = {
            '01': 'Jammu and Kashmir',
            '02': 'Himachal Pradesh',
            '03': 'Punjab',
            '04': 'Chandigarh',
            '05': 'Uttarakhand',
            '06': 'Haryana',
            '07': 'Delhi',
            '08': 'Rajasthan',
            '09': 'Uttar Pradesh',
            '10': 'Bihar',
            '11': 'Sikkim',
            '12': 'Arunachal Pradesh',
            '13': 'Nagaland',
            '14': 'Manipur',
            '15': 'Mizoram',
            '16': 'Tripura',
            '17': 'Meghalaya',
            '18': 'Assam',
            '19': 'West Bengal',
            '20': 'Jharkhand',
            '21': 'Odisha',
            '22': 'Chhattisgarh',
            '23': 'Madhya Pradesh',
            '24': 'Gujarat',
            '26': 'Dadra and Nagar Haveli and Daman and Diu',
            '27': 'Maharashtra',
            '29': 'Karnataka',
            '30': 'Goa',
            '31': 'Lakshadweep',
            '32': 'Kerala',
            '33': 'Tamil Nadu',
            '34': 'Puducherry',
            '35': 'Andaman and Nicobar Islands',
            '36': 'Telangana',
            '37': 'Andhra Pradesh',
            '38': 'Ladakh'
        }
        
        code = gstin[:2]
        return state_codes.get(code)
