"""
Invoice Controller
Orchestrates sales invoice operations between UI and Service layers.

Architecture: UI → Controller → Service → DB

This controller handles:
- Invoice list loading and filtering
- Statistics calculation for display
- Delete operations coordination
- Data formatting for UI consumption
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date

from core.services.invoice_service import InvoiceService
from core.db.sqlite_db import db


@dataclass
class InvoiceStats:
    """Data class for invoice statistics"""
    total: int = 0
    total_amount: float = 0.0
    paid_count: int = 0
    overdue_count: int = 0


class InvoiceController:
    """
    Controller for sales invoice list screen operations.
    
    Responsibilities:
    - Fetch and filter invoices
    - Calculate statistics
    - Orchestrate CRUD operations via service
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller with service reference."""
        self._service = InvoiceService(db)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Fetching
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_all_invoices(self) -> List[Dict]:
        """
        Fetch all sales invoices with party details.
        
        Returns:
            List of invoice dictionaries with party_name and status
        """
        try:
            company_id = db.get_current_company_id()
            
            if hasattr(db, '_query'):
                # Use JOIN query for better performance
                if company_id:
                    query = """
                        SELECT 
                            i.*,
                            COALESCE(p.name, 'Unknown Party') as party_name
                        FROM invoices i
                        LEFT JOIN parties p ON i.party_id = p.id
                        WHERE i.company_id = ?
                        ORDER BY i.id DESC
                    """
                    invoices = db._query(query, (company_id,))
                else:
                    query = """
                        SELECT 
                            i.*,
                            COALESCE(p.name, 'Unknown Party') as party_name
                        FROM invoices i
                        LEFT JOIN parties p ON i.party_id = p.id
                        ORDER BY i.id DESC
                    """
                    invoices = db._query(query)
            else:
                # Fallback to basic method
                invoices = db.get_invoices() or []
                
                # Enrich with party names
                for invoice in invoices:
                    if invoice.get('party_id'):
                        try:
                            party = db.get_party_by_id(invoice['party_id'])
                            invoice['party_name'] = party.get('name', 'Unknown Party') if party else 'Unknown Party'
                        except Exception:
                            invoice['party_name'] = 'Unknown Party'
                    else:
                        invoice['party_name'] = 'Unknown Party'
            
            # Add computed status to each invoice
            for invoice in invoices:
                invoice['status'] = self._compute_invoice_status(invoice)
            
            return list(invoices) if invoices else []
            
        except Exception as e:
            print(f"[InvoiceController] Error fetching invoices: {e}")
            return []
    
    def get_invoice_with_items(self, invoice_id: int) -> Optional[Dict]:
        """
        Get full invoice data including line items.
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            Invoice dictionary with items or None
        """
        try:
            return db.get_invoice_with_items_by_id(invoice_id)
        except Exception as e:
            print(f"[InvoiceController] Error fetching invoice {invoice_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────────────
    # Filtering
    # ─────────────────────────────────────────────────────────────────────────
    
    def filter_invoices(
        self,
        invoices: List[Dict],
        search_text: str = "",
        status_filter: str = "All",
        period_filter: str = "All Time",
        amount_filter: str = "All Amounts",
        party_filter: str = "All Parties"
    ) -> List[Dict]:
        """
        Filter invoices based on search and dropdown criteria.
        
        Args:
            invoices: List of all invoices
            search_text: Text to search in invoice_no, party_name
            status_filter: Status filter ("All", "Paid", "Overdue", "Cancelled")
            period_filter: Time period filter
            amount_filter: Amount range filter
            party_filter: Party name filter
            
        Returns:
            Filtered list of invoices
        """
        search_lower = search_text.lower()
        filtered = []
        
        for invoice in invoices:
            # Search filter
            if search_lower:
                searchable = f"{invoice.get('invoice_no', '')} {invoice.get('party_name', '')}".lower()
                if search_lower not in searchable:
                    continue
            
            # Status filter
            if status_filter != "All":
                invoice_status = invoice.get('status', 'Unpaid')
                if invoice_status != status_filter:
                    continue
            
            # Amount filter
            amount = float(invoice.get('grand_total', 0) or 0)
            if not self._matches_amount_filter(amount, amount_filter):
                continue
            
            # Party filter
            if party_filter != "All Parties":
                if invoice.get('party_name', '') != party_filter:
                    continue
            
            # Period filter
            if not self._matches_period_filter(invoice.get('date'), period_filter):
                continue
            
            filtered.append(invoice)
        
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
    
    def _matches_period_filter(self, invoice_date: str, period_filter: str) -> bool:
        """Check if invoice date matches period filter."""
        if period_filter == "All Time":
            return True
        
        if not invoice_date:
            return False
        
        try:
            # Parse invoice date
            if isinstance(invoice_date, str):
                inv_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
            elif isinstance(invoice_date, (date, datetime)):
                inv_date = invoice_date if isinstance(invoice_date, date) else invoice_date.date()
            else:
                return True
            
            today = date.today()
            
            if period_filter == "Today":
                return inv_date == today
            elif period_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                return inv_date >= week_start
            elif period_filter == "This Month":
                return inv_date.year == today.year and inv_date.month == today.month
            elif period_filter == "This Year":
                return inv_date.year == today.year
                
        except (ValueError, TypeError):
            pass
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────
    
    def calculate_stats(self, invoices: List[Dict]) -> InvoiceStats:
        """
        Calculate statistics from invoice list.
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            InvoiceStats with computed values
        """
        total = len(invoices)
        total_amount = sum(float(inv.get('grand_total', 0) or 0) for inv in invoices)
        paid_count = sum(1 for inv in invoices if inv.get('status') == 'Paid')
        overdue_count = sum(1 for inv in invoices if inv.get('status') == 'Overdue')
        
        return InvoiceStats(
            total=total,
            total_amount=total_amount,
            paid_count=paid_count,
            overdue_count=overdue_count
        )
    
    def extract_party_names(self, invoices: List[Dict]) -> List[str]:
        """
        Extract unique party names from invoices.
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Sorted list of unique party names
        """
        parties = set()
        for invoice in invoices:
            party_name = invoice.get('party_name')
            if party_name and party_name != 'Unknown Party':
                parties.add(party_name)
        return sorted(parties)
    
    # ─────────────────────────────────────────────────────────────────────────
    # CRUD Operations
    # ─────────────────────────────────────────────────────────────────────────
    
    def delete_invoice(self, invoice_id: int) -> Tuple[bool, str]:
        """
        Delete an invoice by ID.
        
        Args:
            invoice_id: ID of the invoice to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            db.delete_invoice(invoice_id)
            return True, "Invoice deleted successfully!"
        except Exception as e:
            return False, f"Failed to delete invoice: {str(e)}"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Status Computation
    # ─────────────────────────────────────────────────────────────────────────
    
    def _compute_invoice_status(self, invoice: Dict) -> str:
        """
        Compute invoice status based on business rules.
        
        Args:
            invoice: Invoice dictionary
            
        Returns:
            Status string ('Paid', 'Partially Paid', 'Unpaid', 'Overdue', 'Cancelled')
        """
        # Check for explicit status
        explicit_status = invoice.get('status')
        if explicit_status and explicit_status in ('Paid', 'Cancelled'):
            return explicit_status
        
        grand_total = float(invoice.get('grand_total', 0) or 0)
        balance_due = float(invoice.get('balance_due', grand_total) or grand_total)
        
        # Paid if no balance due
        if balance_due <= 0 and grand_total > 0:
            return 'Paid'
        
        # Partially Paid if some payment received but balance remains
        if 0 < balance_due < grand_total and grand_total > 0:
            return 'Partially Paid'
        
        # Check for overdue (older than 30 days with balance)
        invoice_date = invoice.get('date')
        if invoice_date and balance_due > 0:
            try:
                if isinstance(invoice_date, str):
                    inv_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                elif isinstance(invoice_date, (date, datetime)):
                    inv_date = invoice_date if isinstance(invoice_date, date) else invoice_date.date()
                else:
                    inv_date = None
                
                if inv_date:
                    days_old = (date.today() - inv_date).days
                    if days_old > 30:
                        return 'Overdue'
            except (ValueError, TypeError):
                pass
        
        # Default to Unpaid if has value
        if grand_total > 0:
            return 'Unpaid'
        return 'Unpaid'
    
    def get_invoice_status_color(self, status: str) -> Tuple[str, str]:
        """
        Get color scheme for invoice status.
        
        Args:
            status: Invoice status string
            
        Returns:
            Tuple of (text_color, background_color)
        """
        status_colors = {
            'Unpaid': ("#3B82F6", "#DBEAFE"),
            'Partially Paid': ("#F59E0B", "#FEF3C7"),
            'Paid': ("#10B981", "#D1FAE5"),
            'Overdue': ("#EF4444", "#FEE2E2"),
            'Cancelled': ("#8B5CF6", "#EDE9FE")
        }
        return status_colors.get(status, ("#3B82F6", "#DBEAFE"))


# Import required for period filtering
from datetime import timedelta


# Singleton instance for convenience
invoice_controller = InvoiceController()


# ============================================================================
# Invoice Form Controller - For form dialog operations
# ============================================================================

class InvoiceFormController:
    """
    Controller for invoice form (create/edit) operations.
    
    Responsibilities:
    - Generate invoice numbers
    - Validate invoice data
    - Save invoices with items
    - Get related data (products, parties)
    - Helper methods for display
    """
    
    def __init__(self):
        """Initialize controller with service reference."""
        self._service = InvoiceService(db)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Invoice Number Generation
    # ─────────────────────────────────────────────────────────────────────────
    
    def generate_next_invoice_number(self) -> str:
        """
        Generate the next sequential invoice number.
        
        Returns:
            Next invoice number string (e.g., "INV-00001")
        """
        try:
            company_id = db.get_current_company_id()
            
            # Get all invoices and find the highest number
            if hasattr(db, '_query') and company_id:
                invoices = db._query(
                    "SELECT invoice_no FROM invoices WHERE company_id = ? ORDER BY id DESC LIMIT 100",
                    (company_id,)
                )
            else:
                invoices = db.get_invoices() or []
            
            max_num = 0
            for inv in invoices:
                inv_no = inv.get('invoice_no', '')
                # Extract number from patterns like "INV-00001" or "00001"
                if inv_no:
                    # Try to extract numeric part
                    parts = inv_no.split('-')
                    try:
                        num = int(parts[-1]) if parts else int(inv_no)
                        max_num = max(max_num, num)
                    except ValueError:
                        continue
            
            next_num = max_num + 1
            return f"INV-{next_num:05d}"
            
        except Exception as e:
            print(f"Error generating invoice number: {e}")
            import random
            return f"INV-{random.randint(10000, 99999)}"
    
    def invoice_number_exists(self, invoice_no: str) -> bool:
        """
        Check if an invoice number already exists.
        
        Args:
            invoice_no: Invoice number to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            company_id = db.get_current_company_id()
            
            if hasattr(db, '_query') and company_id:
                result = db._query(
                    "SELECT 1 FROM invoices WHERE invoice_no = ? AND company_id = ? LIMIT 1",
                    (invoice_no, company_id)
                )
                return len(result) > 0
            else:
                invoices = db.get_invoices() or []
                return any(inv.get('invoice_no') == invoice_no for inv in invoices)
                
        except Exception as e:
            print(f"Error checking invoice number: {e}")
            return False
    
    def ensure_unique_invoice_number(self, invoice_no: str) -> str:
        """
        Ensure invoice number is unique, appending suffix if needed.
        
        Args:
            invoice_no: Desired invoice number
            
        Returns:
            Unique invoice number
        """
        if not self.invoice_number_exists(invoice_no):
            return invoice_no
        
        # Append suffix to make unique
        base = invoice_no
        suffix = 1
        while self.invoice_number_exists(f"{base}-{suffix}"):
            suffix += 1
            if suffix > 100:  # Safety limit
                return self.generate_next_invoice_number()
        
        return f"{base}-{suffix}"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Retrieval
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_invoice_by_number(self, invoice_no: str) -> Optional[Dict]:
        """
        Get invoice data by invoice number.
        
        Args:
            invoice_no: Invoice number
            
        Returns:
            Invoice dictionary with items or None
        """
        try:
            company_id = db.get_current_company_id()
            
            if hasattr(db, '_query') and company_id:
                invoices = db._query(
                    "SELECT * FROM invoices WHERE invoice_no = ? AND company_id = ?",
                    (invoice_no, company_id)
                )
                if invoices:
                    invoice = invoices[0]
                    # Get items
                    items = db._query(
                        "SELECT * FROM invoice_items WHERE invoice_id = ?",
                        (invoice['id'],)
                    )
                    return {'invoice': invoice, 'items': items}
            
            return None
            
        except Exception as e:
            print(f"Error getting invoice by number: {e}")
            return None
    
    def get_products(self) -> List[Dict]:
        """
        Get all products for dropdown/selection.
        
        Returns:
            List of product dictionaries
        """
        try:
            company_id = db.get_current_company_id()
            if company_id and hasattr(db, 'get_products_by_company'):
                return db.get_products_by_company(company_id) or []
            return db.get_products() or []
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_parties(self) -> List[Dict]:
        """
        Get all parties for dropdown/selection.
        
        Returns:
            List of party dictionaries
        """
        try:
            company_id = db.get_current_company_id()
            if company_id and hasattr(db, 'get_parties_by_company'):
                return db.get_parties_by_company(company_id) or []
            return db.get_parties() or []
        except Exception as e:
            print(f"Error getting parties: {e}")
            return []
    
    # ─────────────────────────────────────────────────────────────────────────
    # Type Mapping
    # ─────────────────────────────────────────────────────────────────────────
    
    def map_invoice_type_to_internal(self, display_type: str) -> str:
        """
        Map display invoice type to internal type.
        
        Args:
            display_type: Display text (e.g., "GST - Same State")
            
        Returns:
            Internal type (e.g., "GST_SAME_STATE")
        """
        type_map = {
            "GST - Same State": "GST_SAME_STATE",
            "GST - Other State": "GST_OTHER_STATE",
            "Non-GST": "NON_GST"
        }
        return type_map.get(display_type, "GST_SAME_STATE")
    
    def map_internal_to_display_type(self, internal_type: str) -> str:
        """
        Map internal invoice type to display type.
        
        Args:
            internal_type: Internal type (e.g., "GST_SAME_STATE")
            
        Returns:
            Display text (e.g., "GST - Same State")
        """
        type_map = {
            "GST_SAME_STATE": "GST - Same State",
            "GST_OTHER_STATE": "GST - Other State",
            "NON_GST": "Non-GST"
        }
        return type_map.get(internal_type, "GST - Same State")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────────────────
    
    def validate_invoice_data(
        self, 
        invoice_no: str, 
        party_id: int, 
        items: List[Dict],
        is_new: bool = True,
        skip_duplicate_check: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Validate invoice data before saving.
        
        Args:
            invoice_no: Invoice number
            party_id: Party ID
            items: List of item dictionaries
            is_new: Whether this is a new invoice
            skip_duplicate_check: Skip duplicate check (if already ensured unique)
            
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        # Validate invoice number
        if not invoice_no or not invoice_no.strip():
            return False, "Invoice number is required", "invoice_no"
        
        # Check for duplicate invoice number (only for new invoices, if not skipped)
        if is_new and not skip_duplicate_check and self.invoice_number_exists(invoice_no):
            return False, f"Invoice number '{invoice_no}' already exists", "invoice_no"
        
        # Validate party
        if not party_id:
            return False, "Please select a party", "party"
        
        # Validate items
        if not items:
            return False, "Please add at least one item", "items"
        
        for i, item in enumerate(items):
            if not item.get('product_name'):
                return False, f"Item {i+1}: Product name is required", "items"
            if item.get('quantity', 0) <= 0:
                return False, f"Item {i+1}: Quantity must be greater than 0", "items"
            if item.get('rate', 0) < 0:
                return False, f"Item {i+1}: Rate cannot be negative", "items"
        
        return True, "", ""
    
    # ─────────────────────────────────────────────────────────────────────────
    # Save Operations
    # ─────────────────────────────────────────────────────────────────────────
    
    def save_invoice(
        self, 
        invoice_data: Dict, 
        items: List[Dict],
        is_final: bool = False
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Save invoice with items.
        
        Args:
            invoice_data: Invoice header data
            items: List of item dictionaries
            is_final: Whether to mark as final
            
        Returns:
            Tuple of (success, message, invoice_id)
        """
        try:
            # Add company_id if not present
            if 'company_id' not in invoice_data:
                invoice_data['company_id'] = db.get_current_company_id()
            
            # Calculate totals
            subtotal = sum(item.get('quantity', 0) * item.get('rate', 0) for item in items)
            total_discount = sum(item.get('discount_amount', 0) for item in items)
            total_tax = sum(item.get('tax_amount', 0) for item in items)
            grand_total = subtotal - total_discount + total_tax + invoice_data.get('round_off', 0)
            
            # Calculate CGST, SGST, IGST based on tax_type
            tax_type = invoice_data.get('invoice_type', 'GST - Same State')
            is_interstate = 'Other State' in tax_type
            is_non_gst = 'Non-GST' in tax_type
            
            if is_non_gst:
                # Non-GST invoice: no CGST, SGST, IGST
                cgst_total = 0.0
                sgst_total = 0.0
                igst_total = 0.0
            elif is_interstate:
                # Interstate (IGST): all tax goes to IGST
                cgst_total = 0.0
                sgst_total = 0.0
                igst_total = total_tax
            else:
                # Intrastate (CGST + SGST): split tax equally
                cgst_total = total_tax / 2
                sgst_total = total_tax / 2
                igst_total = 0.0
            
            # Update invoice_data with calculated tax breakdown
            invoice_data['subtotal'] = subtotal
            invoice_data['total_discount'] = total_discount
            invoice_data['total_tax'] = total_tax
            invoice_data['cgst'] = cgst_total
            invoice_data['sgst'] = sgst_total
            invoice_data['igst'] = igst_total
            invoice_data['grand_total'] = grand_total
            
            # Calculate balance_due based on bill type
            # CASH invoices: balance_due = 0 (fully paid immediately)
            # CREDIT invoices: balance_due = grand_total (payment tracking needed)
            bill_type = invoice_data.get('bill_type', 'CASH')
            if bill_type == 'CASH':
                invoice_data['balance_due'] = 0.0  # CASH: No balance due (fully paid)
            else:
                invoice_data['balance_due'] = grand_total  # CREDIT: Full amount is due
            
            # Compute status based on balance_due
            # For CASH: balance_due = 0, so status should be 'Paid'
            # For CREDIT: balance_due = grand_total, so status should be 'Unpaid'
            balance_due = invoice_data.get('balance_due', 0)
            if balance_due <= 0 and grand_total > 0:
                computed_status = 'Paid'
            elif 0 < balance_due < grand_total and grand_total > 0:
                computed_status = 'Partially Paid'
            else:
                computed_status = 'Unpaid'
            invoice_data['status'] = computed_status
            
            invoice_id = invoice_data.get('id')
            
            if invoice_id:
                # Update existing invoice
                db.update_invoice(invoice_data)
                # Delete old items and add new ones
                if hasattr(db, 'delete_invoice_items'):
                    db.delete_invoice_items(invoice_id)
            else:
                # Create new invoice
                invoice_id = db.add_invoice(
                    invoice_no=invoice_data.get('invoice_no'),
                    date=invoice_data.get('date'),
                    party_id=invoice_data.get('party_id'),
                    tax_type=invoice_data.get('invoice_type', 'GST - Same State'),
                    subtotal=invoice_data.get('subtotal', 0),
                    cgst=invoice_data.get('cgst', 0),
                    sgst=invoice_data.get('sgst', 0),
                    igst=invoice_data.get('igst', 0),
                    round_off=invoice_data.get('round_off', 0),
                    grand_total=invoice_data.get('grand_total', 0),
                    status=invoice_data.get('status', 'Unpaid'),
                    bill_type=invoice_data.get('bill_type', 'CASH'),
                    discount=invoice_data.get('total_discount', 0),
                    balance_due=invoice_data.get('balance_due', 0),
                    notes=invoice_data.get('notes')
                )
            
            # Save items
            if invoice_id:
                for item in items:
                    db.add_invoice_item(
                        invoice_id=invoice_id,
                        product_id=item.get('product_id', 0),
                        product_name=item.get('product_name', ''),
                        hsn_code=item.get('hsn_code'),
                        quantity=item.get('quantity', 0),
                        unit=item.get('unit', 'Piece'),
                        rate=item.get('rate', 0),
                        discount_percent=item.get('discount_percent', 0),
                        discount_amount=item.get('discount_amount', 0),
                        tax_percent=item.get('tax_percent', 0),
                        tax_amount=item.get('tax_amount', 0),
                        amount=item.get('amount', 0)
                    )
            
            return True, "Invoice saved successfully!", invoice_id
            
        except Exception as e:
            print(f"Error saving invoice: {e}")
            return False, f"Error saving invoice: {str(e)}", None
    
    # ─────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def number_to_words_indian(self, amount: float) -> str:
        """
        Convert number to words in Indian format.
        
        Args:
            amount: Amount to convert
            
        Returns:
            Words representation (e.g., "One Lakh Twenty Thousand Rupees Only")
        """
        try:
            if amount <= 0:
                return "Zero Rupees Only"
            
            # Round to nearest integer
            amount = int(round(amount))
            
            ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 
                    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 
                    'Seventeen', 'Eighteen', 'Nineteen']
            tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
            
            def two_digit(n):
                if n < 20:
                    return ones[n]
                return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')
            
            def three_digit(n):
                if n < 100:
                    return two_digit(n)
                return ones[n // 100] + ' Hundred' + (' ' + two_digit(n % 100) if n % 100 else '')
            
            if amount < 1000:
                words = three_digit(amount)
            elif amount < 100000:
                words = two_digit(amount // 1000) + ' Thousand'
                if amount % 1000:
                    words += ' ' + three_digit(amount % 1000)
            elif amount < 10000000:
                words = two_digit(amount // 100000) + ' Lakh'
                if amount % 100000:
                    words += ' ' + self.number_to_words_indian(amount % 100000).replace(' Rupees Only', '')
            else:
                words = two_digit(amount // 10000000) + ' Crore'
                if amount % 10000000:
                    words += ' ' + self.number_to_words_indian(amount % 10000000).replace(' Rupees Only', '')
            
            return words.strip() + ' Rupees Only'
            
        except Exception as e:
            print(f"Error converting number to words: {e}")
            return f"{amount:,.2f} Rupees"


# Singleton instance for form operations
invoice_form_controller = InvoiceFormController()
