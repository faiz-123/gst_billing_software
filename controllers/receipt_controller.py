"""
Receipt Controller
Orchestrates receipt-related operations between UI and Service layers.

This controller handles:
- Filtering and searching receipts
- Computing statistics for display
- Coordinating CRUD operations
- Formatting data for UI consumption
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.services.payment_service import payment_service


@dataclass
class ReceiptStats:
    """Data class for receipt statistics"""
    total_received: float = 0.0
    total_count: int = 0
    month_total: float = 0.0
    customers_count: int = 0


@dataclass
class ReceiptFilters:
    """Data class for receipt filter criteria"""
    search_text: str = ""
    method: str = "All Methods"
    period: str = "All Time"
    status: str = "All Status"


class ReceiptController:
    """
    Controller for receipt list screen operations.
    
    Responsibilities:
    - Fetch and filter receipts
    - Calculate statistics
    - Orchestrate CRUD operations via service
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller with service reference"""
        self._service = payment_service
    
    def get_filtered_receipts(
        self, 
        filters: Optional[ReceiptFilters] = None
    ) -> Tuple[List[Dict], ReceiptStats]:
        """
        Get receipts with applied filters and computed statistics.
        
        Args:
            filters: ReceiptFilters object with filter criteria
            
        Returns:
            Tuple containing:
            - List of filtered receipt dictionaries
            - ReceiptStats with computed statistics
        """
        try:
            # Get all receipts (RECEIPT type = money IN from customers)
            all_receipts = self._service.get_payments(payment_type='RECEIPT')
            
            # Calculate stats on unfiltered data
            stats = self._calculate_stats(all_receipts)
            
            # Apply filters if provided
            if filters:
                filtered = self._apply_filters(all_receipts, filters)
            else:
                filtered = all_receipts
            
            return filtered, stats
            
        except Exception as e:
            print(f"[ReceiptController] Error fetching receipts: {e}")
            return [], ReceiptStats()
    
    def _apply_filters(
        self, 
        receipts: List[Dict], 
        filters: ReceiptFilters
    ) -> List[Dict]:
        """
        Apply all filters to receipts list.
        
        Args:
            receipts: List of receipt dictionaries
            filters: ReceiptFilters with filter criteria
            
        Returns:
            Filtered list of receipts
        """
        filtered = receipts
        
        # Apply search filter
        if filters.search_text:
            search_lower = filters.search_text.lower()
            filtered = [
                r for r in filtered
                if self._matches_search(r, search_lower)
            ]
        
        # Apply method filter
        if filters.method and filters.method != "All Methods":
            filtered = [
                r for r in filtered
                if (r.get('mode') or '') == filters.method
            ]
        
        # Apply status filter
        if filters.status and filters.status != "All Status":
            filtered = [
                r for r in filtered
                if (r.get('status') or 'Completed') == filters.status
            ]
        
        # Apply period filter
        if filters.period and filters.period != "All Time":
            filtered = [
                r for r in filtered
                if self._matches_period(r.get('date', ''), filters.period)
            ]
        
        return filtered
    
    def _matches_search(self, receipt: Dict, search_lower: str) -> bool:
        """
        Check if receipt matches search criteria.
        
        Args:
            receipt: Receipt dictionary
            search_lower: Lowercase search string
            
        Returns:
            True if receipt matches search
        """
        searchable_fields = [
            receipt.get('party_name') or '',
            receipt.get('reference') or '',
            receipt.get('mode') or '',
            receipt.get('notes') or ''
        ]
        searchable = ' '.join(searchable_fields).lower()
        return search_lower in searchable
    
    def _matches_period(self, receipt_date: str, period_filter: str) -> bool:
        """
        Check if receipt date matches the period filter.
        
        Args:
            receipt_date: Receipt date string (YYYY-MM-DD)
            period_filter: Period filter value
            
        Returns:
            True if date matches period
        """
        if period_filter == "All Time":
            return True
        
        try:
            receipt_dt = datetime.strptime(str(receipt_date), '%Y-%m-%d')
            today = datetime.now()
            
            if period_filter == "Today":
                return receipt_dt.date() == today.date()
            elif period_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return receipt_dt >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period_filter == "This Month":
                return receipt_dt.year == today.year and receipt_dt.month == today.month
            elif period_filter == "This Year":
                return receipt_dt.year == today.year
        except ValueError:
            return True
        
        return True
    
    def _calculate_stats(self, receipts: List[Dict]) -> ReceiptStats:
        """
        Calculate receipt statistics.
        
        Args:
            receipts: List of all receipts
            
        Returns:
            ReceiptStats with computed values
        """
        total_received = sum(float(r.get('amount') or 0) for r in receipts)
        total_count = len(receipts)
        
        # Count unique customers
        customers = set(r.get('party_id') for r in receipts if r.get('party_id'))
        customers_count = len(customers)
        
        # Calculate this month's total
        current_month = datetime.now().strftime('%Y-%m')
        month_total = sum(
            float(r.get('amount') or 0) for r in receipts 
            if str(r.get('date', '')).startswith(current_month)
        )
        
        return ReceiptStats(
            total_received=total_received,
            total_count=total_count,
            month_total=month_total,
            customers_count=customers_count
        )
    
    def delete_receipt(self, receipt_id: int) -> Tuple[bool, str]:
        """
        Delete a receipt by ID.
        
        Args:
            receipt_id: ID of receipt to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success = self._service.delete_payment(receipt_id)
            if success:
                return True, "Receipt deleted successfully"
            return False, "Failed to delete receipt"
        except Exception as e:
            return False, f"Error deleting receipt: {str(e)}"
    
    def get_receipt_by_id(self, receipt_id: int) -> Optional[Dict]:
        """
        Get a single receipt by ID.
        
        Args:
            receipt_id: Receipt ID to fetch
            
        Returns:
            Receipt dictionary or None if not found
        """
        try:
            return self._service.get_payment_by_id(receipt_id)
        except Exception as e:
            print(f"[ReceiptController] Error fetching receipt: {e}")
            return None


# Singleton instance for app-wide use
receipt_controller = ReceiptController()
