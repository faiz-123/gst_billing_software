#!/usr/bin/env python3
"""
Demo: Show full invoice of INV-002 (now possible!)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db

def show_full_invoice_demo():
    """Demonstrate getting full invoice details"""
    print("🎉 DEMO: Show Full Invoice of INV-002")
    print("=" * 50)
    
    # Get complete invoice with items
    invoice_data = db.get_invoice_with_items("INV-002")
    
    if not invoice_data:
        print("❌ Invoice INV-002 not found!")
        return
    
    invoice = invoice_data['invoice']
    party = invoice_data['party']
    items = invoice_data['items']
    
    print("📄 INVOICE DETAILS:")
    print(f"   Invoice Number: {invoice['invoice_no']}")
    print(f"   Date: {invoice['date']}")
    
    customer_name = party['name'] if party else f"Party ID: {invoice['party_id']}"
    print(f"   Customer: {customer_name}")
    print(f"   Status: {invoice.get('status', 'Unknown')}")
    print(f"   Grand Total: ₹{invoice['grand_total']:,.2f}")
    
    if items:
        print(f"\n🛍️ LINE ITEMS ({len(items)} items):")
        print("   No | Product Name           | HSN   | Qty  | Rate    | Disc% | Tax%  | Amount")
        print("   " + "-" * 80)
        
        for i, item in enumerate(items, 1):
            print(f"   {i:2d} | {item['product_name']:<20} | {item['hsn_code'] or 'N/A':<5} | "
                  f"{item['quantity']:4.1f} | ₹{item['rate']:6.2f} | {item['discount_percent']:4.1f}% | "
                  f"{item['tax_percent']:4.1f}% | ₹{item['amount']:8.2f}")
        
        # Calculate summary
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        total_discount = sum(item['discount_amount'] for item in items)
        total_tax = sum(item['tax_amount'] for item in items)
        
        print("\n💰 SUMMARY:")
        print(f"   Subtotal:      ₹{subtotal:8.2f}")
        print(f"   Total Discount: -₹{total_discount:7.2f}")
        print(f"   Total Tax:      ₹{total_tax:8.2f}")
        print(f"   Grand Total:    ₹{invoice['grand_total']:8.2f}")
        
    else:
        print("\n⚠️  No line items found.")
        print("   This invoice was created before line items were implemented.")
        print("   Only header information is available.")
    
    print(f"\n✅ PROBLEM SOLVED!")
    print("   You can now access complete invoice details including:")
    print("   • Product-level breakdown")
    print("   • Quantities and rates")
    print("   • Discount and tax details")
    print("   • Customer information")

if __name__ == "__main__":
    show_full_invoice_demo()
