"""
Party Controller
Orchestrates party (customer/supplier) operations between UI and Service layers.

Architecture: UI → Controller → Service → DB

This controller handles:
- Party list loading and filtering
- Party form validation and save orchestration
- Party search and selection
- Statistics calculation
- Delete operations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.services.party_service import PartyService
from core.db.sqlite_db import db


@dataclass
class PartyStats:
    """Data class for party statistics"""
    total: int = 0
    customers: int = 0
    suppliers: int = 0
    receivable_amount: float = 0.0
    payable_amount: float = 0.0


class PartyController:
    """
    Controller for party list and form operations.
    
    Responsibilities:
    - Fetch and filter parties
    - Validate party form data
    - Orchestrate CRUD operations via service
    - Format data for UI display
    """
    
    def __init__(self):
        """Initialize controller with service reference."""
        self._service = PartyService(db)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Fetching
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_all_parties(self) -> List[Dict]:
        """
        Fetch all parties for the current company.
        
        Returns:
            List of party dictionaries
        """
        try:
            company_id = db.get_current_company_id()
            if company_id:
                return db.get_parties_by_company(company_id) or []
            return db.get_parties() or []
        except Exception as e:
            print(f"Error fetching parties: {e}")
            return []
    
    def get_party_by_id(self, party_id: int) -> Optional[Dict]:
        """
        Fetch a single party by ID.
        
        Args:
            party_id: Party ID
            
        Returns:
            Party dictionary or None
        """
        try:
            return db.get_party_by_id(party_id)
        except Exception as e:
            print(f"Error fetching party: {e}")
            return None
    
    def search_parties(self, query: str, party_type: Optional[str] = None) -> List[Dict]:
        """
        Search parties by name or other criteria.
        
        Args:
            query: Search query
            party_type: Optional filter by party type
            
        Returns:
            List of matching party dictionaries
        """
        try:
            parties = self.get_all_parties()
            
            if not query:
                if party_type:
                    return [p for p in parties if p.get('party_type') == party_type]
                return parties
            
            query_lower = query.lower()
            results = []
            
            for party in parties:
                # Match by name, mobile, or GSTIN
                if (query_lower in party.get('name', '').lower() or
                    query_lower in party.get('mobile', '').lower() or
                    query_lower in party.get('gstin', '').lower()):
                    
                    if party_type is None or party.get('party_type') == party_type:
                        results.append(party)
            
            return results
        except Exception as e:
            print(f"Error searching parties: {e}")
            return []
    
    def get_customers(self) -> List[Dict]:
        """
        Fetch all customers.
        
        Returns:
            List of customer party dictionaries
        """
        return self.search_parties("", party_type="Customer")
    
    def get_suppliers(self) -> List[Dict]:
        """
        Fetch all suppliers.
        
        Returns:
            List of supplier party dictionaries
        """
        return self.search_parties("", party_type="Supplier")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_party_stats(self) -> PartyStats:
        """
        Calculate party statistics.
        
        Returns:
            PartyStats dataclass with totals
        """
        try:
            parties = self.get_all_parties()
            
            stats = PartyStats(
                total=len(parties),
                customers=sum(1 for p in parties if p.get('party_type') in ['Customer', 'Both']),
                suppliers=sum(1 for p in parties if p.get('party_type') in ['Supplier', 'Both']),
                receivable_amount=sum(float(p.get('balance', 0) or 0) for p in parties 
                                     if float(p.get('balance', 0) or 0) > 0),
                payable_amount=abs(sum(float(p.get('balance', 0) or 0) for p in parties 
                                      if float(p.get('balance', 0) or 0) < 0))
            )
            return stats
        except Exception as e:
            print(f"Error calculating party stats: {e}")
            return PartyStats()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────────────────
    
    def validate_party_data(self, name: str, party_type: str, mobile: str = "", 
                           email: str = "", gstin: str = "") -> Tuple[bool, str, str]:
        """
        Validate party form data.
        
        Args:
            name: Party name
            party_type: Party type (Customer, Supplier, Both)
            mobile: Mobile number (optional)
            email: Email address (optional)
            gstin: GSTIN (optional)
            
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        # Validate name
        is_valid, error = self._service.validate_party_name(name)
        if not is_valid:
            return False, error, "name"
        
        # Validate party type
        is_valid, error = self._service.validate_party_type(party_type)
        if not is_valid:
            return False, error, "party_type"
        
        # Validate mobile if provided
        if mobile:
            is_valid, error = self._service.validate_mobile_number(mobile)
            if not is_valid:
                return False, error, "mobile"
        
        # Validate email if provided
        if email:
            is_valid, error = self._service.validate_email_address(email)
            if not is_valid:
                return False, error, "email"
        
        # Validate GSTIN if provided
        if gstin:
            is_valid, error = self._service.validate_gstin_number(gstin)
            if not is_valid:
                return False, error, "gstin"
        
        return True, "", ""
    
    # ─────────────────────────────────────────────────────────────────────────
    # CRUD Operations
    # ─────────────────────────────────────────────────────────────────────────
    
    def save_party(self, party_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """
        Save a party (create or update).
        
        Args:
            party_data: Dictionary containing party data
            
        Returns:
            Tuple of (success, message, party_id)
        """
        try:
            # Validate first
            is_valid, error, field = self.validate_party_data(
                party_data.get('name', ''),
                party_data.get('party_type', ''),
                party_data.get('mobile', ''),
                party_data.get('email', ''),
                party_data.get('gstin', '')
            )
            
            if not is_valid:
                return False, error, None
            
            # Add company_id if not present
            if 'company_id' not in party_data:
                party_data['company_id'] = db.get_current_company_id()
            
            party_id = party_data.get('id')
            
            if party_id:
                # Update existing party
                success = db.update_party(party_id, party_data)
                if success:
                    return True, "Party updated successfully!", party_id
                return False, "Failed to update party", None
            else:
                # Create new party
                new_id = db.add_party(party_data)
                if new_id:
                    return True, "Party created successfully!", new_id
                return False, "Failed to create party", None
                
        except Exception as e:
            print(f"Error saving party: {e}")
            return False, f"Error saving party: {str(e)}", None
    
    def delete_party(self, party_id: int) -> Tuple[bool, str]:
        """
        Delete a party.
        
        Args:
            party_id: Party ID to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if party has related transactions
            # (This check could be in the service layer)
            
            success = db.delete_party(party_id)
            if success:
                return True, "Party deleted successfully!"
            return False, "Failed to delete party"
        except Exception as e:
            print(f"Error deleting party: {e}")
            return False, f"Error deleting party: {str(e)}"


# Singleton instance for easy import
party_controller = PartyController()
