#!/usr/bin/env python3
"""
Generate 500 dummy parties for testing GST Billing Software
Includes varied data: customers, suppliers, full details, partial details, different balances
"""

import random
import sys
from typing import Dict, List

# Core imports
from core.db.sqlite_db import Database
from core.logger import get_logger

logger = get_logger(__name__)

# Sample data for generation
FIRST_NAMES = [
    "Raj", "Priya", "Amit", "Sneha", "Arjun", "Divya", "Vikram", "Ananya",
    "Rohan", "Neha", "Arun", "Pooja", "Sanjay", "Riya", "Kunal", "Anjali",
    "Nikhil", "Shreya", "Abhishek", "Isha", "Rahul", "Diya", "Akshay", "Nisha",
    "Dev", "Simran", "Ashish", "Avni", "Bhavin", "Anita"
]

LAST_NAMES = [
    "Singh", "Patel", "Kumar", "Sharma", "Gupta", "Verma", "Reddy", "Nair",
    "Desai", "Iyer", "Menon", "Bhat", "Chopra", "Kapoor", "Malhotra", "Saxena",
    "Agarwal", "Joshi", "Pandey", "Rao", "Bhattacharya", "Sen", "Das", "Dutta",
    "Mukherjee", "Roy", "Banerjee", "Ganguly", "Chatterjee", "Bose"
]

COMPANY_SUFFIXES = [
    "Pvt Ltd", "Ltd", "Industries", "Trading", "Export", "Import", "Enterprises",
    "Solutions", "Services", "Manufacturing", "Distributors", "Wholesale", "Retail",
    "Group", "Corporation", "Global", "International", "Digital", "Tech", "Logistics"
]

CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Indore", "Surat", "Vadodara",
    "Nashik", "Nagpur", "Aurangabad", "Visakhapatnam", "Kochi", "Gurgaon"
]

STATES = {
    "Delhi": "DL", "Mumbai": "MH", "Bangalore": "KA", "Hyderabad": "TS",
    "Chennai": "TN", "Kolkata": "WB", "Pune": "MH", "Ahmedabad": "GJ",
    "Jaipur": "RJ", "Lucknow": "UP", "Chandigarh": "CH", "Indore": "MP",
    "Surat": "GJ", "Vadodara": "GJ", "Nashik": "MH", "Nagpur": "MH",
    "Aurangabad": "MH", "Visakhapatnam": "AP", "Kochi": "KL", "Gurgaon": "HR"
}


def generate_gstin() -> str:
    """Generate a realistic GSTIN (15 characters)"""
    state_code = random.randint(1, 37)  # State codes 1-37
    state_code_str = f"{state_code:02d}"
    
    pan = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5)])
    pan += "".join([str(random.randint(0, 9)) for _ in range(4)])
    pan += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    entity_code = f"{random.randint(1, 99):02d}"
    check_digit = str(random.randint(0, 9))
    
    return f"{state_code_str}{pan}{entity_code}{check_digit}"


def generate_pan() -> str:
    """Generate a realistic PAN (10 characters)"""
    pan = ""
    # First 5 are letters
    pan += "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5)])
    # Next 4 are digits
    pan += "".join([str(random.randint(0, 9)) for _ in range(4)])
    # Last 1 is letter
    pan += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return pan


def generate_mobile() -> str:
    """Generate an Indian mobile number"""
    return f"9{random.randint(1, 9)}{random.randint(0, 9)}{random.randint(10, 99)}{random.randint(10000, 99999)}"


def generate_pincode() -> str:
    """Generate a 6-digit pincode"""
    return f"{random.randint(100000, 999999)}"


def generate_address() -> str:
    """Generate a realistic address"""
    street_numbers = random.randint(1, 500)
    street_types = ["Street", "Lane", "Road", "Avenue", "Marg", "Path", "Boulevard", "Circle"]
    
    return f"{street_numbers} {random.choice(street_types)}, {random.choice(CITIES)}"


def generate_party_name() -> str:
    """Generate a company name"""
    if random.random() < 0.6:
        # Person name company
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    else:
        # Formal company name
        words = random.sample(FIRST_NAMES + LAST_NAMES, random.randint(1, 3))
        name = " ".join(words)
    
    if random.random() < 0.7:
        name += f" {random.choice(COMPANY_SUFFIXES)}"
    
    return name


def generate_opening_balance() -> tuple:
    """Generate opening balance and balance type
    
    Returns:
        Tuple of (balance_amount, balance_type)
        balance_type: 'dr' for receivable, 'cr' for payable
    """
    if random.random() < 0.3:
        # No opening balance
        return 0.0, 'dr'
    
    # Generate balance between 1000 to 500000
    amount = random.randint(10, 500) * 1000 + random.randint(0, 999)
    balance_type = random.choice(['dr', 'cr'])  # 50-50 receivable vs payable
    
    return float(amount), balance_type


def create_dummy_party(detail_level: str, party_type: str) -> Dict:
    """Create a dummy party with varying detail levels
    
    Args:
        detail_level: 'full' (100%), 'partial' (50%), 'minimal' (25%)
        party_type: 'Customer' or 'Supplier'
    
    Returns:
        Dictionary with party data
    """
    party = {
        'name': generate_party_name(),
        'party_type': party_type,
    }
    
    # All parties get mobile (70% chance) and email (60% chance)
    if random.random() < 0.7:
        party['mobile'] = generate_mobile()
    
    if random.random() < 0.6:
        party['email'] = f"contact@{party['name'].lower().replace(' ', '')}.com"
    
    if detail_level == 'full':
        # 100% details - all fields
        party['gstin'] = generate_gstin()
        party['pan'] = generate_pan()
        party['address'] = generate_address()
        city = random.choice(CITIES)
        party['city'] = city
        party['state'] = STATES.get(city, 'UT')
        party['pincode'] = generate_pincode()
        opening_balance, balance_type = generate_opening_balance()
        party['opening_balance'] = opening_balance
        party['balance_type'] = balance_type
        
    elif detail_level == 'partial':
        # 50% details - some fields
        if random.random() < 0.5:
            party['gstin'] = generate_gstin()
        if random.random() < 0.5:
            party['pan'] = generate_pan()
        if random.random() < 0.5:
            party['address'] = generate_address()
            city = random.choice(CITIES)
            party['city'] = city
            party['state'] = STATES.get(city, 'UT')
        if random.random() < 0.5:
            party['pincode'] = generate_pincode()
        
        opening_balance, balance_type = generate_opening_balance()
        party['opening_balance'] = opening_balance
        party['balance_type'] = balance_type
        
    else:  # minimal
        # 25% details - just name and type
        opening_balance, balance_type = generate_opening_balance()
        party['opening_balance'] = opening_balance
        party['balance_type'] = balance_type
    
    return party


def generate_500_parties(db: Database) -> None:
    """Generate 500 dummy parties with varied data
    
    Distribution:
    - 250 Customers, 250 Suppliers
    - 50% with full details
    - 30% with partial details
    - 20% with minimal details
    - 50% with opening balance (Dr - Receivable, Cr - Payable)
    """
    
    logger.info("Starting generation of 500 dummy parties...")
    
    parties: List[Dict] = []
    party_names_set = set()
    
    # Customer parties
    logger.info("Generating 250 Customer parties...")
    for i in range(250):
        detail_level_rand = random.random()
        if detail_level_rand < 0.5:
            detail_level = 'full'
        elif detail_level_rand < 0.8:
            detail_level = 'partial'
        else:
            detail_level = 'minimal'
        
        # Ensure unique party names
        while True:
            party = create_dummy_party(detail_level, 'Customer')
            if party['name'] not in party_names_set:
                party_names_set.add(party['name'])
                break
        
        parties.append(party)
        
        if (i + 1) % 50 == 0:
            logger.debug(f"Generated {i + 1} customer parties")
    
    # Supplier parties
    logger.info("Generating 250 Supplier parties...")
    for i in range(250):
        detail_level_rand = random.random()
        if detail_level_rand < 0.5:
            detail_level = 'full'
        elif detail_level_rand < 0.8:
            detail_level = 'partial'
        else:
            detail_level = 'minimal'
        
        # Ensure unique party names
        while True:
            party = create_dummy_party(detail_level, 'Supplier')
            if party['name'] not in party_names_set:
                party_names_set.add(party['name'])
                break
        
        parties.append(party)
        
        if (i + 1) % 50 == 0:
            logger.debug(f"Generated {i + 1} supplier parties (total {250 + i + 1})")
    
    # Insert into database
    logger.info(f"Inserting {len(parties)} parties into database...")
    successful = 0
    failed = 0
    
    for idx, party in enumerate(parties):
        try:
            party_id = db.add_party(party)
            successful += 1
            
            if (idx + 1) % 50 == 0:
                logger.debug(f"Inserted {idx + 1} parties (Success: {successful}, Failed: {failed})")
        
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to insert party {party['name']}: {str(e)}")
            
            if failed > 10:  # Stop if too many failures
                logger.error("Too many failures, stopping insertion")
                break
    
    logger.info(f"✅ Party generation completed!")
    logger.info(f"   Total parties created: {successful}")
    logger.info(f"   Failed inserts: {failed}")
    logger.info(f"   Success rate: {successful / len(parties) * 100:.1f}%")
    
    # Log summary statistics
    dr_count = len([p for p in parties if p.get('balance_type') == 'dr' and p.get('opening_balance', 0) > 0])
    cr_count = len([p for p in parties if p.get('balance_type') == 'cr' and p.get('opening_balance', 0) > 0])
    customer_count = len([p for p in parties if p.get('party_type') == 'Customer'])
    supplier_count = len([p for p in parties if p.get('party_type') == 'Supplier'])
    
    logger.info(f"\n📊 Party Distribution:")
    logger.info(f"   Customers: {customer_count}")
    logger.info(f"   Suppliers: {supplier_count}")
    logger.info(f"   Receivable (Dr): {dr_count}")
    logger.info(f"   Payable (Cr): {cr_count}")


def main():
    """Main entry point"""
    try:
        # Initialize database
        db = Database()
        
        # Set a default company (usually company_id = 1)
        # This assumes at least one company exists
        db._current_company_id = 1
        
        logger.info(f"Using database: {db.path}")
        logger.info(f"Company ID: {db._current_company_id}")
        
        # Check if parties already exist
        existing = db.get_parties()
        if existing and len(existing) > 0:
            logger.warning(f"⚠️  Database already contains {len(existing)} parties")
            response = input("Do you want to continue and add more parties? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Cancelled by user")
                return
        
        # Generate parties
        generate_500_parties(db)
        
        logger.info("✅ Script completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during party generation: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
