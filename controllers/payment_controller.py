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
from core.logger import get_logger, log_performance, UserActionLogger
from core.error_handler import ErrorHandler, handle_errors
from core.exceptions import PaymentException, InvalidPaymentAmount

logger = get_logger(__name__)


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
        logger.debug("PaymentController initialized")
    
    @log_performance
    def get_all_payments(self) -> List[Dict]:
        """
        Get all payments (PAYMENT type = money OUT to suppliers).
        
        Returns:
            List of payment dictionaries
        """
        try:
            logger.debug("Fetching all payments from service")
            all_payments = self._service.get_payments(payment_type='PAYMENT')
            logger.info(f"🔄 Fetched {len(all_payments) if all_payments else 0} TOTAL payments from database")
            return all_payments or []
        except Exception as e:
            logger.error(f"Error fetching all payments: {e}", exc_info=True)
            return []
    
    def filter_payments(
        self,
        payments: List[Dict],
        search_text: str = "",
        method_filter: str = "All Methods",
        period_filter: str = "All Time",
        status_filter: str = "All Status"
    ) -> List[Dict]:
        """
        Apply filters to a list of payments.
        
        Args:
            payments: List of payment dictionaries to filter
            search_text: Text to search in party name, reference, etc.
            method_filter: Payment method filter
            period_filter: Time period filter
            status_filter: Payment status filter
            
        Returns:
            Filtered list of payments
        """
        filtered = payments
        
        # Apply search filter
        if search_text:
            search_lower = search_text.lower()
            filtered = [
                p for p in filtered
                if self._matches_search(p, search_lower)
            ]
            logger.debug(f"After search filter: {len(filtered)} payments")
        
        # Apply method filter
        if method_filter and method_filter != "All Methods":
            filtered = [
                p for p in filtered
                if (p.get('mode') or '') == method_filter
            ]
            logger.debug(f"After method filter: {len(filtered)} payments")
        
        # Apply status filter
        if status_filter and status_filter != "All Status":
            filtered = [
                p for p in filtered
                if (p.get('status') or 'Completed') == status_filter
            ]
            logger.debug(f"After status filter: {len(filtered)} payments")
        
        # Apply period filter
        if period_filter and period_filter != "All Time":
            filtered = [
                p for p in filtered
                if self._matches_period(p.get('date', ''), period_filter)
            ]
            logger.debug(f"After period filter: {len(filtered)} payments")
        
        return filtered
    
    def calculate_stats(self, payments: List[Dict]) -> PaymentStats:
        """
        Calculate payment statistics (public method for UI).
        
        Args:
            payments: List of all payments
            
        Returns:
            PaymentStats with computed values
        """
        return self._calculate_stats(payments)
    
    @log_performance
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
            logger.debug(f"Fetching filtered payments with filters: {filters}")
            
            # Get all payments (PAYMENT type = money OUT to suppliers)
            all_payments = self._service.get_payments(payment_type='PAYMENT')
            logger.debug(f"Retrieved {len(all_payments) if all_payments else 0} payments")
            
            # Calculate stats on unfiltered data
            stats = self._calculate_stats(all_payments)
            
            # Apply filters if provided
            if filters:
                filtered = self._apply_filters(all_payments, filters)
            else:
                filtered = all_payments
            
            logger.info(f"Filtered payments: {len(filtered) if filtered else 0} out of {len(all_payments) if all_payments else 0}")
            return filtered, stats
            
        except Exception as e:
            logger.error(f"Error fetching payments: {e}", exc_info=True)
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
            logger.debug(f"After search filter: {len(filtered)} payments")
        
        # Apply method filter
        if filters.method and filters.method != "All Methods":
            filtered = [
                p for p in filtered
                if (p.get('mode') or '') == filters.method
            ]
            logger.debug(f"After method filter: {len(filtered)} payments")
        
        # Apply status filter
        if filters.status and filters.status != "All Status":
            filtered = [
                p for p in filtered
                if (p.get('status') or 'Completed') == filters.status
            ]
            logger.debug(f"After status filter: {len(filtered)} payments")
        
        # Apply period filter
        if filters.period and filters.period != "All Time":
            filtered = [
                p for p in filtered
                if self._matches_period(p.get('date', ''), filters.period)
            ]
            logger.debug(f"After period filter: {len(filtered)} payments")
        
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
    
    @log_performance
    @handle_errors("Delete Payment")
    def delete_payment(self, payment_id: int) -> Tuple[bool, str]:
        """
        Delete a payment by ID.
        
        Args:
            payment_id: ID of payment to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Attempting to delete payment ID: {payment_id}")
            
            # Delete the payment
            success = self._service.delete_payment(payment_id)
            
            if success:
                UserActionLogger.log_payment_deleted(payment_id)
                logger.info(f"Successfully deleted payment ID: {payment_id}")
                return True, "Payment deleted successfully"
            
            logger.warning(f"Failed to delete payment ID: {payment_id}")
            return False, "Failed to delete payment"
            
        except PaymentException as e:
            logger.error(f"Payment error while deleting {payment_id}: {e.error_code}", exc_info=True)
            return False, e.to_user_message()
        except Exception as e:
            logger.error(f"Error deleting payment {payment_id}: {e}", exc_info=True)
            return ErrorHandler.handle_exception(e, "Delete Payment", show_dialog=False)
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        """
        Get a single payment by ID.
        
        Args:
            payment_id: Payment ID to fetch
            
        Returns:
            Payment dictionary or None if not found
        """
        try:
            logger.debug(f"Fetching payment ID: {payment_id}")
            return self._service.get_payment_by_id(payment_id)
        except Exception as e:
            logger.error(f"Error fetching payment {payment_id}: {e}", exc_info=True)
            return None


# Singleton instance for app-wide use
payment_controller = PaymentController()
