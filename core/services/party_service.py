"""
Party Service
Business logic for party (customer/supplier) operations
"""

from typing import Dict, List, Optional, Tuple

from core.validators import validate_gstin, validate_pan, validate_mobile, validate_email, validate_pincode
from core.models.party_model import Party
from core.enums import PartyType
from core.logger import get_logger
from core.exceptions import (
    PartyException, PartyAlreadyExists, PartyNotFound,
    CreditLimitExceeded
)

logger = get_logger(__name__)


class PartyService:
    """Service class for party-related business logic"""
    
    def __init__(self, db=None):
        self.db = db
    
    def validate_party_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate that party name is not empty
        
        Args:
            name: Party name
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Party name is required"
        return True, ""
    
    def validate_party_type(self, party_type: str) -> Tuple[bool, str]:
        """
        Validate that party type is selected
        
        Args:
            party_type: Party type (Customer, Supplier, Both)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not party_type or not party_type.strip():
            return False, "Please select a Party Type"
        
        valid_types = [pt.value for pt in PartyType]
        if party_type not in valid_types:
            return False, f"Invalid party type. Must be one of: {', '.join(valid_types)}"
        
        return True, ""
    
    def validate_mobile_number(self, mobile: str) -> Tuple[bool, str]:
        """
        Validate Indian mobile number
        
        Args:
            mobile: Mobile number
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not mobile:
            return True, ""  # Optional field
        
        if not validate_mobile(mobile):
            return False, "Please enter a valid 10-digit mobile number"
        
        return True, ""
    
    def validate_email_address(self, email: str) -> Tuple[bool, str]:
        """
        Validate email address
        
        Args:
            email: Email address
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not email:
            return True, ""  # Optional field
        
        if not validate_email(email):
            return False, "Please enter a valid email address"
        
        return True, ""
    
    def validate_gstin_number(self, gstin: str) -> Tuple[bool, str]:
        """
        Validate GSTIN
        
        Args:
            gstin: GSTIN number
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not gstin:
            return True, ""  # Optional field
        
        if not validate_gstin(gstin):
            return False, "Please enter a valid 15-character GSTIN"
        
        return True, ""
    
    def validate_pan_number(self, pan: str) -> Tuple[bool, str]:
        """
        Validate PAN number
        
        Args:
            pan: PAN number
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not pan:
            return True, ""  # Optional field
        
        if not validate_pan(pan):
            return False, "Please enter a valid 10-character PAN"
        
        return True, ""
    
    def validate_pincode_number(self, pincode: str) -> Tuple[bool, str]:
        """
        Validate PIN code
        
        Args:
            pincode: PIN code
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not pincode:
            return True, ""  # Optional field
        
        if not validate_pincode(pincode):
            return False, "Please enter a valid 6-digit PIN code"
        
        return True, ""
    
    def validate_opening_balance(self, balance: str) -> Tuple[bool, float, str]:
        """
        Validate opening balance is a valid number
        
        Args:
            balance: Opening balance as string
            
        Returns:
            Tuple[bool, float, str]: (is_valid, parsed_value, error_message)
        """
        try:
            value = float(balance or 0)
            return True, value, ""
        except ValueError:
            return False, 0, "Opening balance must be a number"
    
    def check_duplicate_name(self, name: str, current_party_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Check if a party with the same name already exists
        
        Args:
            name: Party name to check
            current_party_id: ID of current party (for edit mode, to exclude self)
            
        Returns:
            Tuple[bool, str]: (is_duplicate, error_message)
        """
        if not self.db:
            logger.warning("Database not available for duplicate check")
            return False, ""
        
        try:
            existing_parties = self.db.get_parties()
            if not existing_parties:
                return False, ""
            
            for party in existing_parties:
                # Skip the current party being edited
                if current_party_id and party.get('id') == current_party_id:
                    continue
                
                party_name = party.get('name', '').strip().upper()
                check_name = name.strip().upper()
                
                # Case-insensitive duplicate check
                if party_name == check_name:
                    return True, f"A party with the name '{name}' already exists"
        except Exception as e:
            logger.error(f"Error checking duplicate party name: {e}")
            pass
        
        return False, ""
    
    def validate_party(self, party_data: Dict, current_party_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate all party fields
        
        Args:
            party_data: Dictionary with party data
            current_party_id: ID of current party (for edit mode)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Name validation
        is_valid, error = self.validate_party_name(party_data.get('name', ''))
        if not is_valid:
            return False, error
        
        # Duplicate check
        is_duplicate, error = self.check_duplicate_name(
            party_data.get('name', ''), 
            current_party_id
        )
        if is_duplicate:
            return False, error
        
        # Party type validation
        is_valid, error = self.validate_party_type(party_data.get('party_type', ''))
        if not is_valid:
            return False, error
        
        # Mobile validation
        is_valid, error = self.validate_mobile_number(party_data.get('mobile', ''))
        if not is_valid:
            return False, error
        
        # Email validation
        is_valid, error = self.validate_email_address(party_data.get('email', ''))
        if not is_valid:
            return False, error
        
        # GSTIN validation
        is_valid, error = self.validate_gstin_number(party_data.get('gst_number', ''))
        if not is_valid:
            return False, error
        
        # PAN validation
        is_valid, error = self.validate_pan_number(party_data.get('pan', ''))
        if not is_valid:
            return False, error
        
        # Pincode validation
        is_valid, error = self.validate_pincode_number(party_data.get('pincode', ''))
        if not is_valid:
            return False, error
        
        # Opening balance validation
        is_valid, _, error = self.validate_opening_balance(
            str(party_data.get('opening_balance', 0))
        )
        if not is_valid:
            return False, error
        
        return True, ""
    
    def prepare_party_data(
        self,
        name: str,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        gst_number: Optional[str] = None,
        pan: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        opening_balance: float = 0.0,
        balance_type: str = "dr",
        party_type: str = "Customer",
        party_id: Optional[int] = None
    ) -> Dict:
        """
        Prepare party data dictionary for database operations
        
        Args:
            All party fields
            
        Returns:
            dict: Prepared party data
        """
        data = {
            'name': name.strip().upper() if name else '',
            'mobile': mobile.strip() if mobile else None,
            'email': email.strip().lower() if email else None,
            'gst_number': gst_number.strip().upper() if gst_number else None,
            'pan': pan.strip().upper() if pan else None,
            'address': address.strip() if address else None,
            'city': city.strip() if city else None,
            'state': state.strip() if state else None,
            'pincode': pincode.strip() if pincode else None,
            'opening_balance': float(opening_balance or 0),
            'balance_type': balance_type.lower() if balance_type else 'dr',
            'party_type': party_type,
            'is_gst_registered': 1 if gst_number else 0
        }
        
        if party_id:
            data['id'] = party_id
        
        return data
    
    def create_party_from_dict(self, data: Dict) -> Party:
        """
        Create a Party model from dictionary
        
        Args:
            data: Dictionary with party data
            
        Returns:
            Party: Party model instance
        """
        return Party.from_dict(data)
    
    def add_party(self, party_data: Dict) -> Optional[int]:
        """
        Add a new party to the database
        
        Args:
            party_data: Dictionary with party data
            
        Returns:
            int: New party ID or None on failure
            
        Raises:
            PartyAlreadyExists: If party with same name already exists
        """
        if not self.db:
            logger.error("Database not available for add_party")
            return None
        
        try:
            return self.db.add_party(party_data)
        except PartyAlreadyExists:
            # Re-raise duplicate exception so caller knows it's a duplicate
            raise
        except Exception as e:
            logger.error(f"Error adding party: {e}")
            raise PartyException(f"Failed to add party: {str(e)}") from e
    
    def update_party(self, party_id: int, party_data: Dict) -> bool:
        """
        Update an existing party
        
        Args:
            party_id: ID of party to update
            party_data: Dictionary with updated party data
            
        Returns:
            bool: True on success, False on failure
        """
        if not self.db:
            return False
        
        try:
            if hasattr(self.db, 'update_party'):
                return self.db.update_party(party_id, party_data)
            return False
        except Exception as e:
            print(f"Error updating party: {e}")
            return False
    
    def delete_party(self, party_id: int) -> bool:
        """
        Delete a party from the database
        
        Args:
            party_id: ID of party to delete
            
        Returns:
            bool: True on success, False on failure
        """
        if not self.db:
            return False
        
        try:
            if hasattr(self.db, 'delete_party'):
                self.db.delete_party(party_id)
            else:
                # Fallback to direct SQL
                self.db.execute("DELETE FROM parties WHERE id = ?", (party_id,))
            return True
        except Exception as e:
            print(f"Error deleting party: {e}")
            return False
    
    def get_parties(self, party_type: Optional[str] = None) -> List[Dict]:
        """
        Get all parties, optionally filtered by type
        
        Args:
            party_type: Optional filter by party type
            
        Returns:
            List[Dict]: List of party dictionaries
        """
        if not self.db:
            return []
        
        try:
            parties = self.db.get_parties()
            if party_type:
                parties = [p for p in parties if p.get('party_type', '').lower() in [party_type.lower(), 'both']]
            return parties
        except Exception:
            return []
    
    def get_party_by_id(self, party_id: int) -> Optional[Dict]:
        """
        Get a party by ID
        
        Args:
            party_id: Party ID
            
        Returns:
            Dict: Party data or None
        """
        if not self.db:
            return None
        
        try:
            if hasattr(self.db, 'get_party_by_id'):
                return self.db.get_party_by_id(party_id)
            # Fallback: search in all parties
            parties = self.db.get_parties()
            for p in parties:
                if p.get('id') == party_id:
                    return p
            return None
        except Exception:
            return None

    def detect_tax_type_for_party(self, party_data: dict, company_data: dict) -> str:
        """
        Detect appropriate tax type based on party and company GSTIN.
        Compares state codes extracted from GSTINs to determine if intra-state or inter-state.
        
        Args:
            party_data: Dictionary with party information (must have 'gstin' key)
            company_data: Dictionary with company information (must have 'gstin' key)
            
        Returns:
            str: Tax type 'GST' or 'Non-GST'
        """
        try:
            party_gstin = party_data.get('gstin', '').strip() if party_data else ''
            company_gstin = company_data.get('gstin', '').strip() if company_data else ''
            
            # If either GSTIN is missing or invalid, return Non-GST
            if not party_gstin or not company_gstin or len(party_gstin) < 2 or len(company_gstin) < 2:
                return 'Non-GST'
            
            # GSTIN format: First 2 characters are state code
            party_state_code = party_gstin[:2]
            company_state_code = company_gstin[:2]
            
            # If state codes match, it's intra-state GST, otherwise inter-state
            if party_state_code == company_state_code:
                return 'GST'
            else:
                return 'GST'  # Both intra-state and inter-state use GST
        except Exception as e:
            print(f"Error detecting tax type: {e}")
            return 'Non-GST'


# Create a singleton instance for convenience
try:
    from core.db.sqlite_db import db
    party_service = PartyService(db)
except ImportError:
    party_service = PartyService()