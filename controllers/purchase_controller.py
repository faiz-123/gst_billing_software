"""
Purchase Invoice Controller
Orchestrates purchase invoice operations between UI and Service layers.

Architecture: UI → Controller → Service → DB

This controller handles:
- Purchase invoice list loading and filtering
- Statistics calculation for display
- Delete operations coordination
- Data formatting for UI consumption
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date, timedelta

from core.db.sqlite_db import db
from core.logger import get_logger, log_performance, UserActionLogger
from core.error_handler import ErrorHandler, handle_errors
from core.exceptions import InvoiceException
from theme import (
    PRIMARY, PRIMARY_LIGHT, SUCCESS, SUCCESS_LIGHT, WARNING, WARNING_LIGHT,
    GRAY_500, GRAY_100
)

logger = get_logger(__name__)


@dataclass
class PurchaseStats:
    """Data class for purchase invoice statistics"""
    total: int = 0
    total_amount: float = 0.0
    paid_count: int = 0
    unpaid_count: int = 0


class PurchaseController:
    """
    Controller for purchase invoice list screen operations.
    
    Responsibilities:
    - Fetch and filter purchase invoices
    - Calculate statistics
    - Orchestrate CRUD operations
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller."""
        pass
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Fetching
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_all_purchases(self) -> List[Dict]:
        """
        Fetch all purchase invoices with supplier details.
        
        Returns:
            List of purchase invoice dictionaries with party_name and status
        """
        try:
            company_id = db.get_current_company_id()
            
            if hasattr(db, '_query'):
                # Use JOIN query for better performance
                if company_id:
                    query = """
                        SELECT 
                            pi.*,
                            COALESCE(p.name, 'Unknown Supplier') as party_name
                        FROM purchase_invoices pi
                        LEFT JOIN parties p ON pi.supplier_id = p.id
                        WHERE pi.company_id = ?
                        ORDER BY pi.id DESC
                    """
                    purchases = db._query(query, (company_id,))
                else:
                    query = """
                        SELECT 
                            pi.*,
                            COALESCE(p.name, 'Unknown Supplier') as party_name
                        FROM purchase_invoices pi
                        LEFT JOIN parties p ON pi.supplier_id = p.id
                        ORDER BY pi.id DESC
                    """
                    purchases = db._query(query)
            else:
                # Fallback to basic method
                purchases = db.get_purchase_invoices() or []
                
                # Enrich with party names
                for purchase in purchases:
                    if purchase.get('supplier_id'):
                        try:
                            party = db.get_party_by_id(purchase['supplier_id'])
                            purchase['party_name'] = party.get('name', 'Unknown Supplier') if party else 'Unknown Supplier'
                        except Exception:
                            purchase['party_name'] = 'Unknown Supplier'
                    else:
                        purchase['party_name'] = 'Unknown Supplier'
            
            # Add computed status to each purchase
            for purchase in purchases:
                purchase['status'] = self._compute_purchase_status(purchase)
            
            return list(purchases) if purchases else []
            
        except Exception as e:
            print(f"[PurchaseController] Error fetching purchases: {e}")
            return []
    
    def get_purchase_with_items(self, purchase_id: int) -> Optional[Dict]:
        """
        Get full purchase invoice data including line items.
        
        Args:
            purchase_id: ID of the purchase invoice
            
        Returns:
            Purchase invoice dictionary with items or None
        """
        try:
            return db.get_purchase_invoice_with_items_by_id(purchase_id)
        except Exception as e:
            print(f"[PurchaseController] Error fetching purchase {purchase_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────────────
    # Filtering
    # ─────────────────────────────────────────────────────────────────────────
    
    def filter_purchases(
        self,
        purchases: List[Dict],
        search_text: str = "",
        status_filter: str = "All",
        period_filter: str = "All Time",
        amount_filter: str = "All Amounts",
        supplier_filter: str = "All Suppliers"
    ) -> List[Dict]:
        """
        Filter purchases based on search and dropdown criteria.
        
        Args:
            purchases: List of all purchases
            search_text: Text to search in invoice_no, party_name
            status_filter: Status filter ("All", "Paid", "Unpaid", "Cancelled")
            period_filter: Time period filter
            amount_filter: Amount range filter
            supplier_filter: Supplier name filter
            
        Returns:
            Filtered list of purchases
        """
        search_lower = search_text.lower()
        filtered = []
        
        for purchase in purchases:
            # Search filter
            if search_lower:
                searchable = f"{purchase.get('invoice_no', '')} {purchase.get('party_name', '')}".lower()
                if search_lower not in searchable:
                    continue
            
            # Status filter
            if status_filter != "All":
                purchase_status = purchase.get('status', 'Unpaid')
                if purchase_status != status_filter:
                    continue
            
            # Amount filter
            amount = float(purchase.get('grand_total', 0) or 0)
            if not self._matches_amount_filter(amount, amount_filter):
                continue
            
            # Supplier filter
            if supplier_filter != "All Suppliers":
                if purchase.get('party_name', '') != supplier_filter:
                    continue
            
            # Period filter
            if not self._matches_period_filter(purchase.get('date'), period_filter):
                continue
            
            filtered.append(purchase)
        
        return filtered
    
    def _matches_amount_filter(self, amount: float, amount_filter: str) -> bool:
        """Check if amount matches the filter criteria."""
        if amount_filter == "All Amounts":
            return True
        elif amount_filter == "Under ₹10K":
            return amount < 10000
        elif amount_filter == "₹10K - ₹50K":
            return 10000 <= amount < 50000
        elif amount_filter == "₹50K - ₹1L":
            return 50000 <= amount < 100000
        elif amount_filter == "Above ₹1L":
            return amount >= 100000
        return True
    
    def _matches_period_filter(self, purchase_date: str, period_filter: str) -> bool:
        """Check if purchase date matches period filter."""
        if period_filter == "All Time":
            return True
        
        if not purchase_date:
            return False
        
        try:
            # Parse purchase date
            if isinstance(purchase_date, str):
                pur_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            elif isinstance(purchase_date, (date, datetime)):
                pur_date = purchase_date if isinstance(purchase_date, date) else purchase_date.date()
            else:
                return True
            
            today = date.today()
            
            if period_filter == "Today":
                return pur_date == today
            elif period_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return pur_date >= week_start
            elif period_filter == "This Month":
                return pur_date.year == today.year and pur_date.month == today.month
            elif period_filter == "This Year":
                return pur_date.year == today.year
                
        except (ValueError, TypeError):
            pass
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────
    
    def calculate_stats(self, purchases: List[Dict]) -> PurchaseStats:
        """
        Calculate statistics from purchase list.
        
        Args:
            purchases: List of purchase dictionaries
            
        Returns:
            PurchaseStats with computed values
        """
        total = len(purchases)
        total_amount = sum(float(pur.get('grand_total', 0) or 0) for pur in purchases)
        paid_count = sum(1 for pur in purchases if pur.get('status') == 'Paid')
        unpaid_count = sum(1 for pur in purchases if pur.get('status') in ['Unpaid', 'Partial Paid'])
        
        return PurchaseStats(
            total=total,
            total_amount=total_amount,
            paid_count=paid_count,
            unpaid_count=unpaid_count
        )
    
    def extract_supplier_names(self, purchases: List[Dict]) -> List[str]:
        """
        Extract unique supplier names from purchases.
        
        Args:
            purchases: List of purchase dictionaries
            
        Returns:
            Sorted list of unique supplier names
        """
        suppliers = set()
        for purchase in purchases:
            party_name = purchase.get('party_name')
            if party_name and party_name != 'Unknown Supplier':
                suppliers.add(party_name)
        return sorted(suppliers)
    
    # ─────────────────────────────────────────────────────────────────────────
    # CRUD Operations
    # ─────────────────────────────────────────────────────────────────────────
    
    @handle_errors("Delete Purchase Invoice")
    def delete_purchase(self, purchase_id: int) -> Tuple[bool, str]:
        """
        Delete a purchase invoice by ID.
        
        Args:
            purchase_id: ID of the purchase to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Attempting to delete purchase invoice ID: {purchase_id}")
            
            # Get purchase details for logging
            purchase = db.get_purchase_invoice(purchase_id)
            if not purchase:
                raise InvoiceException("Purchase invoice not found")
            
            purchase_no = purchase.get('invoice_no', 'Unknown')
            
            # Delete the purchase
            db.delete_purchase_invoice(purchase_id)
            
            logger.info(f"Successfully deleted purchase invoice ID: {purchase_id}, Number: {purchase_no}")
            return True, "Purchase invoice deleted successfully!"
            
        except InvoiceException as e:
            logger.error(f"Invoice error while deleting purchase {purchase_id}: {e.error_code}", exc_info=True)
            return False, e.to_user_message()
        except Exception as e:
            logger.error(f"Failed to delete purchase invoice {purchase_id}: {e}", exc_info=True)
            return ErrorHandler.handle_exception(e, "Delete Purchase Invoice", show_dialog=False)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Status Computation
    # ─────────────────────────────────────────────────────────────────────────
    
    def _compute_purchase_status(self, purchase: Dict) -> str:
        """
        Compute purchase status based on business rules.
        
        Args:
            purchase: Purchase dictionary
            
        Returns:
            Status string ('Paid', 'Unpaid', 'Partial Paid', 'Cancelled')
        """
        # Check for explicit status
        explicit_status = purchase.get('status')
        if explicit_status and explicit_status in ('Paid', 'Cancelled'):
            return explicit_status
        
        grand_total = float(purchase.get('grand_total', 0) or 0)
        balance_due = float(purchase.get('balance_due', grand_total) or grand_total)
        
        # Paid if no balance due
        if balance_due <= 0 and grand_total > 0:
            return 'Paid'
        
        # Partial Paid if some balance remains
        if 0 < balance_due < grand_total and grand_total > 0:
            return 'Partial Paid'
        
        # Default to Unpaid
        return 'Unpaid'
    
    def get_purchase_status_color(self, status: str) -> Tuple[str, str]:
        """
        Get color scheme for purchase status.
        
        Args:
            status: Purchase status string
            
        Returns:
            Tuple of (text_color, background_color)
        """
        status_colors = {
            'Unpaid': (PRIMARY, PRIMARY_LIGHT),
            'Partial Paid': (WARNING, WARNING_LIGHT),
            'Paid': (SUCCESS, SUCCESS_LIGHT),
            'Cancelled': (GRAY_500, GRAY_100)
        }
        return status_colors.get(status, (GRAY_500, GRAY_100))


# Singleton instance for convenience
purchase_controller = PurchaseController()
