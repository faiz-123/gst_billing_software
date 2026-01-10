"""
Payment Controller
Orchestrates payment-related operations between UI and Service layers.

This controller handles:
- Filtering and searching payments
- Computing statistics for display
- Coordinating CRUD operations
- Formatting data for UI consumption
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.services.payment_service import payment_service


@dataclass
class PaymentStats:
    """Data class for payment statistics"""
    total_paid: float = 0.0
    total_count: int = 0
    month_total: float = 0.0
    suppliers_count: int = 0


@dataclass
class PaymentFilters:
    """Data class for payment filter criteria"""
    search_text: str = ""
    method: str = "All Methods"
    period: str = "All Time"
    status: str = "All Status"


class PaymentController:
    """
    Controller for payment list screen operations.
    
    Responsibilities:
    - Fetch and filter payments
    - Calculate statistics
    - Orchestrate CRUD operations via service
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller with service reference"""
        self._service = payment_service
    
    def get_filtered_payments(
        self, 
        filters: Optional[PaymentFilters] = None
    ) -> Tuple[List[Dict], PaymentStats]:
        """
        Get payments with applied filters and computed statistics.
        
        Args:
            filters: PaymentFilters object with filter criteria
            
        Returns:
            Tuple containing:
            - List of filtered payment dictionaries
            - PaymentStats with computed statistics
        """
        try:
            # Get all payments (PAYMENT type = money OUT to suppliers)
            all_payments = self._service.get_payments(payment_type='PAYMENT')
            
            # Calculate stats on unfiltered data
            stats = self._calculate_stats(all_payments)
            
            # Apply filters if provided
            if filters:
                filtered = self._apply_filters(all_payments, filters)
            else:
                filtered = all_payments
            
            return filtered, stats
            
        except Exception as e:
            print(f"[PaymentController] Error fetching payments: {e}")
            return [], PaymentStats()
    
    def _apply_filters(
        self, 
        payments: List[Dict], 
        filters: PaymentFilters
    ) -> List[Dict]:
        """
        Apply all filters to payments list.
        
        Args:
            payments: List of payment dictionaries
            filters: PaymentFilters with filter criteria
            
        Returns:
            Filtered list of payments
        """
        filtered = payments
        
        # Apply search filter
        if filters.search_text:
            search_lower = filters.search_text.lower()
            filtered = [
                p for p in filtered
                if self._matches_search(p, search_lower)
            ]
        
        # Apply method filter
        if filters.method and filters.method != "All Methods":
            filtered = [
                p for p in filtered
                if (p.get('mode') or '') == filters.method
            ]
        
        # Apply status filter
        if filters.status and filters.status != "All Status":
            filtered = [
                p for p in filtered
                if (p.get('status') or 'Completed') == filters.status
            ]
        
        # Apply period filter
        if filters.period and filters.period != "All Time":
            filtered = [
                p for p in filtered
                if self._matches_period(p.get('date', ''), filters.period)
            ]
        
        return filtered
    
    def _matches_search(self, payment: Dict, search_lower: str) -> bool:
        """
        Check if payment matches search criteria.
        
        Args:
            payment: Payment dictionary
            search_lower: Lowercase search string
            
        Returns:
            True if payment matches search
        """
        searchable_fields = [
            payment.get('party_name') or '',
            payment.get('reference') or '',
            payment.get('mode') or '',
            payment.get('notes') or ''
        ]
        searchable = ' '.join(searchable_fields).lower()
        return search_lower in searchable
    
    def _matches_period(self, payment_date: str, period_filter: str) -> bool:
        """
        Check if payment date matches the period filter.
        
        Args:
            payment_date: Payment date string (YYYY-MM-DD)
            period_filter: Period filter value
            
        Returns:
            True if date matches period
        """
        if period_filter == "All Time":
            return True
        
        try:
            payment_dt = datetime.strptime(str(payment_date), '%Y-%m-%d')
            today = datetime.now()
            
            if period_filter == "Today":
                return payment_dt.date() == today.date()
            elif period_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return payment_dt >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period_filter == "This Month":
                return payment_dt.year == today.year and payment_dt.month == today.month
            elif period_filter == "This Year":
                return payment_dt.year == today.year
        except ValueError:
            return True
        
        return True
    
    def _calculate_stats(self, payments: List[Dict]) -> PaymentStats:
        """
        Calculate payment statistics.
        
        Args:
            payments: List of all payments
            
        Returns:
            PaymentStats with computed values
        """
        total_paid = sum(float(p.get('amount') or 0) for p in payments)
        total_count = len(payments)
        
        # Count unique suppliers
        suppliers = set(p.get('party_id') for p in payments if p.get('party_id'))
        suppliers_count = len(suppliers)
        
        # Calculate this month's total
        current_month = datetime.now().strftime('%Y-%m')
        month_total = sum(
            float(p.get('amount') or 0) for p in payments 
            if str(p.get('date', '')).startswith(current_month)
        )
        
        return PaymentStats(
            total_paid=total_paid,
            total_count=total_count,
            month_total=month_total,
            suppliers_count=suppliers_count
        )
    
    def delete_payment(self, payment_id: int) -> Tuple[bool, str]:
        """
        Delete a payment by ID.
        
        Args:
            payment_id: ID of payment to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success = self._service.delete_payment(payment_id)
            if success:
                return True, "Payment deleted successfully"
            return False, "Failed to delete payment"
        except Exception as e:
            return False, f"Error deleting payment: {str(e)}"
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        """
        Get a single payment by ID.
        
        Args:
            payment_id: Payment ID to fetch
            
        Returns:
            Payment dictionary or None if not found
        """
        try:
            return self._service.get_payment_by_id(payment_id)
        except Exception as e:
            print(f"[PaymentController] Error fetching payment: {e}")
            return None


# Singleton instance for app-wide use
payment_controller = PaymentController()
