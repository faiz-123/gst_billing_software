#!/usr/bin/env python3
"""
Cleanup script to move unused files after screen reorganization
"""

import os
import shutil
from datetime import datetime

# Files that are no longer needed (replaced by screens/ versions)
UNUSED_FILES = [
    # Original screen files (replaced)
    'login_ui.py',
    'select_company.py', 
    'create_company.py',
    'new_company_ai.py',
    
    # Old individual screen files (moved to screens/)
    'dashboard.py',
    'add_party.py',
    'add_product.py',
    'invoice.py',
    'invoice_list.py',
    'parties_list.py',
    'payment_list.py',
    'product_list.py',
    'record_payment.py',
]

def main():
    """Move unused files to backup directory"""
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_unused_files_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    
    moved_files = []
    missing_files = []
    
    for filename in UNUSED_FILES:
        if os.path.exists(filename):
            try:
                shutil.move(filename, os.path.join(backup_dir, filename))
                moved_files.append(filename)
                print(f"✅ Moved: {filename} → {backup_dir}/")
            except Exception as e:
                print(f"❌ Error moving {filename}: {e}")
        else:
            missing_files.append(filename)
            print(f"⚠️  File not found: {filename}")
    
    # Create summary
    summary_content = f"""# Cleanup Summary - {timestamp}

## Files Moved to Backup:
{chr(10).join([f"- {f}" for f in moved_files])}

## Files Not Found (already removed):
{chr(10).join([f"- {f}" for f in missing_files])}

## Reason for Cleanup:
These files were moved to backup because they have been replaced by the new organized screen structure in the `screens/` directory.

## Current Active Structure:
- `screens/login.py` (replaces login_ui.py)
- `screens/company_selection.py` (replaces select_company.py)
- `screens/company_creation.py` (replaces create_company.py, new_company_ai.py)
- `screens/dashboard.py` (replaces dashboard.py)
- `screens/parties.py` (replaces add_party.py, parties_list.py)
- `screens/products.py` (replaces add_product.py, product_list.py)
- `screens/invoices.py` (replaces invoice.py, invoice_list.py)
- `screens/payments.py` (replaces record_payment.py, payment_list.py)

## Safe to Delete:
These backup files can be safely deleted after confirming the new structure works correctly.
"""
    
    with open(os.path.join(backup_dir, "CLEANUP_SUMMARY.md"), "w") as f:
        f.write(summary_content)
    
    print(f"\n📋 Summary:")
    print(f"   Moved: {len(moved_files)} files")
    print(f"   Missing: {len(missing_files)} files")
    print(f"   Backup location: {backup_dir}/")
    print(f"   Summary: {backup_dir}/CLEANUP_SUMMARY.md")

if __name__ == "__main__":
    main()
